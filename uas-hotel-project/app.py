from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database", "hotel.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "kamar")
BANNER_UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "img")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BANNER_UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["BANNER_UPLOAD_FOLDER"] = BANNER_UPLOAD_FOLDER


@app.template_filter("rupiah")
def rupiah_filter(value):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return value
    return ("Rp " + format(int(round(amount)), ",")).replace(",", ".")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kamar (
            id_kamar INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_kamar TEXT NOT NULL,
            tipe_kamar TEXT NOT NULL,
            harga_per_malam INTEGER NOT NULL,
            status TEXT NOT NULL,
            deskripsi TEXT,
            filename TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS booking (
            id_booking INTEGER PRIMARY KEY AUTOINCREMENT,
            id_kamar INTEGER NOT NULL,
            nama TEXT NOT NULL,
            email TEXT,
            telepon TEXT,
            tanggal_checkin TEXT,
            tanggal_checkout TEXT,
            catatan TEXT,
            status_pembayaran TEXT DEFAULT 'Belum Bayar',
            tanggal_booking TEXT,
            FOREIGN KEY (id_kamar) REFERENCES kamar (id_kamar)
        )
        """
    )
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(booking)")
        columns = [row[1] for row in cur.fetchall()]
        if 'status_pembayaran' not in columns:
            cur.execute("ALTER TABLE booking ADD COLUMN status_pembayaran TEXT DEFAULT 'Belum Bayar'")
            conn.commit()
        if 'tanggal_booking' not in columns:
            cur.execute("ALTER TABLE booking ADD COLUMN tanggal_booking TEXT")
            conn.commit()
    except Exception as e:
        print(f"Error adding columns: {e}")
        pass
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS banner (
            id_banner INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT,
            subjudul TEXT,
            filename TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tipe_kamar_detail (
            tipe_kamar TEXT PRIMARY KEY,
            judul TEXT NOT NULL,
            deskripsi TEXT,
            luas TEXT,
            fasilitas TEXT,
            keuntungan TEXT,
            filename TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kontak (
            id_kontak INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            email TEXT,
            pesan TEXT,
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS admin (
            id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM admin")
        if cur.fetchone()[0] == 0:
            default_password = generate_password_hash("admin123")
            cur.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", default_password))
            conn.commit()
    except:
        pass
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def user_index():
    search_query = request.args.get("search", "")
    conn = get_db()
    cur = conn.cursor()
    if search_query:
        like = "%" + search_query + "%"
        cur.execute(
            """
            WITH first_per_type AS (
                SELECT tipe_kamar, MIN(id_kamar) AS min_id
                FROM kamar
                WHERE status = 'Tersedia'
                  AND (nomor_kamar LIKE ? OR tipe_kamar LIKE ?)
                GROUP BY tipe_kamar
            )
            SELECT k.*, t.deskripsi as deskripsi_tipe
            FROM kamar k
            JOIN first_per_type f ON k.id_kamar = f.min_id
            LEFT JOIN tipe_kamar_detail t ON k.tipe_kamar = t.tipe_kamar
            ORDER BY CASE k.tipe_kamar
                WHEN 'Standard' THEN 1
                WHEN 'Deluxe' THEN 2
                WHEN 'Suite' THEN 3
                WHEN 'VIP' THEN 4
                ELSE 5
            END
            """,
            (like, like),
        )
    else:
        cur.execute(
            """
            WITH first_per_type AS (
                SELECT tipe_kamar, MIN(id_kamar) AS min_id
                FROM kamar
                WHERE status = 'Tersedia'
                GROUP BY tipe_kamar
            )
            SELECT k.*, t.deskripsi as deskripsi_tipe
            FROM kamar k
            JOIN first_per_type f ON k.id_kamar = f.min_id
            LEFT JOIN tipe_kamar_detail t ON k.tipe_kamar = t.tipe_kamar
            ORDER BY CASE k.tipe_kamar
                WHEN 'Standard' THEN 1
                WHEN 'Deluxe' THEN 2
                WHEN 'Suite' THEN 3
                WHEN 'VIP' THEN 4
                ELSE 5
            END
            """
        )
    kamars = cur.fetchall()
    cur.execute("SELECT * FROM banner ORDER BY id_banner ASC")
    banners = cur.fetchall()
    conn.close()
    return render_template("user/index.html", kamars=kamars, banners=banners, search_query=search_query)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nama = request.form["nama"]
        email = request.form.get("email")
        pesan = request.form.get("pesan")
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO kontak (nama, email, pesan, created_at)
            VALUES (?, ?, ?, datetime('now','localtime'))
            """,
            (nama, email, pesan),
        )
        conn.commit()
        conn.close()
        return render_template("user/contact.html", success=True)
    return render_template("user/contact.html", success=False)


# pagination kamar hanya 6 card per page
@app.route("/rooms")
def user_rooms():
    kategori = request.args.get("kategori")
    page = request.args.get("page", 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page
    
    conn = get_db()
    cur = conn.cursor()
    
    if kategori:
        cur.execute("SELECT COUNT(*) FROM kamar WHERE status = ? AND tipe_kamar = ?", ("Tersedia", kategori))
    else:
        cur.execute("SELECT COUNT(*) FROM kamar WHERE status = ?", ("Tersedia",))
    total_rooms = cur.fetchone()[0]
    
    if kategori:
        cur.execute(
            "SELECT * FROM kamar WHERE status = ? AND tipe_kamar = ? ORDER BY id_kamar ASC LIMIT ? OFFSET ?",
            ("Tersedia", kategori, per_page, offset),
        )
    else:
        cur.execute(
            "SELECT * FROM kamar WHERE status = ? ORDER BY id_kamar ASC LIMIT ? OFFSET ?",
            ("Tersedia", per_page, offset),
        )
        
    kamars = cur.fetchall()
    conn.close()
    
    total_pages = (total_rooms + per_page - 1) // per_page
    
    return render_template(
        "user/rooms.html", 
        kamars=kamars, 
        kategori=kategori, 
        page=page, 
        total_pages=total_pages
    )


@app.route("/kamar/<tipe>")
def kamar_detail(tipe):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tipe_kamar_detail WHERE tipe_kamar = ?", (tipe,))
    detail = cur.fetchone()
    cur.execute("SELECT * FROM kamar WHERE status = ? AND tipe_kamar = ? ORDER BY id_kamar ASC", ("Tersedia", tipe))
    kamars = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM kamar WHERE status = ? AND tipe_kamar = ?", ("Tersedia", tipe))
    stok = cur.fetchone()[0]
    conn.close()
    if not detail:
        return redirect(url_for("user_index"))
    return render_template("user/kamar_detail.html", detail=detail, kamars=kamars, stok=stok)


@app.route("/booking")
def booking_redirect():
    return redirect(url_for("user_rooms"))


@app.route("/booking/<int:id_kamar>", methods=["GET", "POST"])
def user_booking(id_kamar):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM kamar WHERE id_kamar = ?", (id_kamar,))
    kamar = cur.fetchone()
    if not kamar:
        conn.close()
        return redirect(url_for("user_index"))
    if request.method == "POST":
        from datetime import datetime
        nama = request.form["nama"]
        email = request.form.get("email")
        telepon = request.form.get("telepon")
        tanggal_checkin = request.form.get("tanggal_checkin")
        tanggal_checkout = request.form.get("tanggal_checkout")
        catatan = request.form.get("catatan")
        tanggal_booking = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            """
            INSERT INTO booking (id_kamar, nama, email, telepon, tanggal_checkin, tanggal_checkout, catatan, tanggal_booking, status_pembayaran)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Belum Bayar')
            """,
            (id_kamar, nama, email, telepon, tanggal_checkin, tanggal_checkout, catatan, tanggal_booking),
        )
        conn.commit()
        id_booking = cur.lastrowid
        conn.close()
        return render_template("user/booking.html", kamar=kamar, id_booking=id_booking, show_payment_modal=True)
    conn.close()
    return render_template("user/booking.html", kamar=kamar, show_payment_modal=False)


@app.route("/payment/<int:id_booking>")
def payment(id_booking):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.*, k.nomor_kamar, k.tipe_kamar, k.harga_per_malam
        FROM booking b
        JOIN kamar k ON b.id_kamar = k.id_kamar
        WHERE b.id_booking = ?
    """, (id_booking,))
    booking = cur.fetchone()
    conn.close()
    if not booking:
        return redirect(url_for("user_index"))
    
    tanggal_checkin = booking['tanggal_checkin'] or ''
    tanggal_checkout = booking['tanggal_checkout'] or ''
    jumlah_malam = 1
    if tanggal_checkin and tanggal_checkout:
        try:
            from datetime import datetime
            checkin = datetime.strptime(tanggal_checkin, '%Y-%m-%d')
            checkout = datetime.strptime(tanggal_checkout, '%Y-%m-%d')
            jumlah_malam = max(1, (checkout - checkin).days)
        except:
            jumlah_malam = 1
    
    total_harga = booking['harga_per_malam'] * jumlah_malam
    return render_template("user/payment.html", booking=booking, jumlah_malam=jumlah_malam, total_harga=total_harga)


@app.route("/payment/<int:id_booking>/confirm", methods=["POST"])
def confirm_payment(id_booking):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id_kamar FROM booking WHERE id_booking = ?", (id_booking,))
    booking = cur.fetchone()
    if booking:
        cur.execute("UPDATE booking SET status_pembayaran = 'Sudah Bayar' WHERE id_booking = ?", (id_booking,))
        cur.execute("UPDATE kamar SET status = 'Tidak Tersedia' WHERE id_kamar = ?", (booking['id_kamar'],))
        conn.commit()
    conn.close()
    return redirect(url_for("struk", id_booking=id_booking))


@app.route("/struk/<int:id_booking>")
def struk(id_booking):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.*, k.nomor_kamar, k.tipe_kamar, k.harga_per_malam
        FROM booking b
        JOIN kamar k ON b.id_kamar = k.id_kamar
        WHERE b.id_booking = ?
    """, (id_booking,))
    booking = cur.fetchone()
    conn.close()
    if not booking:
        return redirect(url_for("user_index"))
    
    tanggal_checkin = booking['tanggal_checkin'] or ''
    tanggal_checkout = booking['tanggal_checkout'] or ''
    jumlah_malam = 1
    if tanggal_checkin and tanggal_checkout:
        try:
            from datetime import datetime
            checkin = datetime.strptime(tanggal_checkin, '%Y-%m-%d')
            checkout = datetime.strptime(tanggal_checkout, '%Y-%m-%d')
            jumlah_malam = max(1, (checkout - checkin).days)
        except:
            jumlah_malam = 1
    
    total_harga = booking['harga_per_malam'] * jumlah_malam
    return render_template("user/struk.html", booking=booking, jumlah_malam=jumlah_malam, total_harga=total_harga)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM admin WHERE username = ?", (username,))
        admin = cur.fetchone()
        conn.close()
        if admin and check_password_hash(admin['password'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_rooms'))
        else:
            return render_template("admin/login.html", error="Username atau password salah!")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))


@app.route("/admin/rooms")
@login_required
def admin_rooms():
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10
    
    conn = get_db()
    cur = conn.cursor()
    
    if search:
        cur.execute("""
            SELECT * FROM kamar 
            WHERE nomor_kamar LIKE ? OR tipe_kamar LIKE ? OR deskripsi LIKE ?
            ORDER BY id_kamar ASC
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT * FROM kamar ORDER BY id_kamar ASC")
    
    all_kamar = cur.fetchall()
    total = len(all_kamar)
    start = (page - 1) * per_page
    end = start + per_page
    kamar_list = all_kamar[start:end]
    
    total_pages = (total + per_page - 1) // per_page
    
    conn.close()
    return render_template("admin/rooms.html", kamar_list=kamar_list, edit_kamar=None, search=search, page=page, total_pages=total_pages, total=total)


@app.route("/admin/rooms/add", methods=["POST"])
@login_required
def admin_add_room():
    nomor_kamar = request.form["nomor_kamar"]
    tipe_kamar = request.form["tipe_kamar"]
    harga_per_malam = request.form["harga_per_malam"]
    status = request.form["status"]
    deskripsi = request.form["deskripsi"]
    file = request.files.get("file")
    filename = None
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO kamar (nomor_kamar, tipe_kamar, harga_per_malam, status, deskripsi, filename)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (nomor_kamar, tipe_kamar, harga_per_malam, status, deskripsi, filename),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_rooms"))


@app.route("/admin/rooms/edit/<int:id_kamar>", methods=["GET", "POST"])
@login_required
def admin_edit_room(id_kamar):
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        nomor_kamar = request.form["nomor_kamar"]
        tipe_kamar = request.form["tipe_kamar"]
        harga_per_malam = request.form["harga_per_malam"]
        status = request.form["status"]
        deskripsi = request.form["deskripsi"]
        file = request.files.get("file")
        cur.execute("SELECT filename FROM kamar WHERE id_kamar = ?", (id_kamar,))
        row = cur.fetchone()
        old_filename = row["filename"] if row else None
        filename = old_filename
        if file and file.filename and allowed_file(file.filename):
            if old_filename:
                old_path = os.path.join(app.config["UPLOAD_FOLDER"], old_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        cur.execute(
            """
            UPDATE kamar
            SET nomor_kamar = ?, tipe_kamar = ?, harga_per_malam = ?, status = ?, deskripsi = ?, filename = ?
            WHERE id_kamar = ?
            """,
            (nomor_kamar, tipe_kamar, harga_per_malam, status, deskripsi, filename, id_kamar),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("admin_rooms"))
    cur.execute("SELECT * FROM kamar WHERE id_kamar = ?", (id_kamar,))
    edit_kamar = cur.fetchone()
    cur.execute("SELECT * FROM kamar ORDER BY id_kamar ASC")
    kamar_list = cur.fetchall()
    conn.close()
    return render_template("admin/rooms.html", kamar_list=kamar_list, edit_kamar=edit_kamar)


@app.route("/admin/rooms/delete/<int:id_kamar>")
@login_required
def admin_delete_room(id_kamar):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT filename FROM kamar WHERE id_kamar = ?", (id_kamar,))
    row = cur.fetchone()
    if row and row["filename"]:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], row["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
    cur.execute("DELETE FROM kamar WHERE id_kamar = ?", (id_kamar,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_rooms"))


@app.route("/admin/banners")
@login_required
def admin_banners():
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10
    
    conn = get_db()
    cur = conn.cursor()
    
    if search:
        cur.execute("""
            SELECT * FROM banner 
            WHERE judul LIKE ? OR subjudul LIKE ?
            ORDER BY id_banner ASC
        """, (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT * FROM banner ORDER BY id_banner ASC")
    
    all_banners = cur.fetchall()
    total = len(all_banners)
    start = (page - 1) * per_page
    end = start + per_page
    banners = all_banners[start:end]
    
    total_pages = (total + per_page - 1) // per_page
    
    conn.close()
    return render_template("admin/banners.html", banners=banners, edit_banner=None, search=search, page=page, total_pages=total_pages, total=total)


@app.route("/admin/banners/add", methods=["POST"])
@login_required
def admin_add_banner():
    judul = request.form["judul"]
    subjudul = request.form.get("subjudul")
    file = request.files.get("file")
    filename = None
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["BANNER_UPLOAD_FOLDER"], filename))
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO banner (judul, subjudul, filename) VALUES (?, ?, ?)",
        (judul, subjudul, filename),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_banners"))


@app.route("/admin/banners/edit/<int:id_banner>", methods=["GET", "POST"])
@login_required
def admin_edit_banner(id_banner):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM banner WHERE id_banner = ?", (id_banner,))
    banner_row = cur.fetchone()
    if not banner_row:
        conn.close()
        return redirect(url_for("admin_banners"))
    if request.method == "POST":
        judul = request.form["judul"]
        subjudul = request.form.get("subjudul")
        file = request.files.get("file")
        filename = banner_row["filename"]
        if file and file.filename and allowed_file(file.filename):
            if filename:
                old_path = os.path.join(app.config["BANNER_UPLOAD_FOLDER"], filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["BANNER_UPLOAD_FOLDER"], filename))
        cur.execute(
            "UPDATE banner SET judul = ?, subjudul = ?, filename = ? WHERE id_banner = ?",
            (judul, subjudul, filename, id_banner),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("admin_banners"))
    cur.execute("SELECT * FROM banner ORDER BY id_banner ASC")
    banners = cur.fetchall()
    conn.close()
    return render_template("admin/banners.html", banners=banners, edit_banner=banner_row)


@app.route("/admin/banners/delete/<int:id_banner>")
@login_required
def admin_delete_banner(id_banner):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT filename FROM banner WHERE id_banner = ?", (id_banner,))
    row = cur.fetchone()
    if row and row["filename"]:
        file_path = os.path.join(app.config["BANNER_UPLOAD_FOLDER"], row["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
    cur.execute("DELETE FROM banner WHERE id_banner = ?", (id_banner,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_banners"))


@app.route("/admin/tipe-kamar")
@login_required
def admin_tipe_kamar():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tipe_kamar_detail ORDER BY tipe_kamar ASC")
    details = cur.fetchall()
    conn.close()
    return render_template("admin/tipe_kamar.html", details=details)


@app.route("/admin/tipe-kamar/edit/<tipe>", methods=["GET", "POST"])
@login_required
def admin_edit_tipe_kamar(tipe):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tipe_kamar_detail WHERE tipe_kamar = ?", (tipe,))
    detail = cur.fetchone()
    if request.method == "POST":
        judul = request.form["judul"]
        deskripsi = request.form.get("deskripsi")
        luas = request.form.get("luas")
        fasilitas = request.form.get("fasilitas")
        keuntungan = request.form.get("keuntungan")
        file = request.files.get("file")
        filename = detail["filename"] if detail else None
        if file and file.filename and allowed_file(file.filename):
            if filename:
                old_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        if detail:
            cur.execute(
                """
                UPDATE tipe_kamar_detail
                SET judul = ?, deskripsi = ?, luas = ?, fasilitas = ?, keuntungan = ?, filename = ?
                WHERE tipe_kamar = ?
                """,
                (judul, deskripsi, luas, fasilitas, keuntungan, filename, tipe),
            )
        else:
            cur.execute(
                """
                INSERT INTO tipe_kamar_detail (tipe_kamar, judul, deskripsi, luas, fasilitas, keuntungan, filename)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (tipe, judul, deskripsi, luas, fasilitas, keuntungan, filename),
            )
        conn.commit()
        conn.close()
        return redirect(url_for("admin_tipe_kamar"))
    conn.close()
    return render_template("admin/tipe_kamar_edit.html", detail=detail, tipe=tipe)


@app.route("/admin/contacts")
@login_required
def admin_contacts():
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10
    
    conn = get_db()
    cur = conn.cursor()
    
    if search:
        cur.execute("""
            SELECT * FROM kontak 
            WHERE nama LIKE ? OR email LIKE ? OR pesan LIKE ?
            ORDER BY id_kontak ASC
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT * FROM kontak ORDER BY id_kontak ASC")
    
    all_kontak = cur.fetchall()
    total = len(all_kontak)
    start = (page - 1) * per_page
    end = start + per_page
    kontak_list = all_kontak[start:end]
    
    total_pages = (total + per_page - 1) // per_page
    
    conn.close()
    return render_template("admin/contacts.html", kontak_list=kontak_list, search=search, page=page, total_pages=total_pages, total=total)


@app.route("/admin/bookings")
@login_required
def admin_bookings():
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10
    
    conn = get_db()
    cur = conn.cursor()
    
    if search:
        cur.execute("""
            SELECT b.*, k.nomor_kamar, k.tipe_kamar, k.harga_per_malam
            FROM booking b
            JOIN kamar k ON b.id_kamar = k.id_kamar
            WHERE b.nama LIKE ? OR b.email LIKE ? OR b.telepon LIKE ? OR k.nomor_kamar LIKE ? OR k.tipe_kamar LIKE ?
            ORDER BY b.id_booking ASC
        """, (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        cur.execute("""
            SELECT b.*, k.nomor_kamar, k.tipe_kamar, k.harga_per_malam
            FROM booking b
            JOIN kamar k ON b.id_kamar = k.id_kamar
            ORDER BY b.id_booking ASC
        """)
    
    all_bookings = cur.fetchall()
    total = len(all_bookings)
    start = (page - 1) * per_page
    end = start + per_page
    bookings = all_bookings[start:end]
    
    total_pages = (total + per_page - 1) // per_page
    
    conn.close()
    return render_template("admin/bookings.html", bookings=bookings, search=search, page=page, total_pages=total_pages, total=total)


@app.route("/admin/bookings/delete/<int:id_booking>")
@login_required
def admin_delete_booking(id_booking):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id_kamar, status_pembayaran FROM booking WHERE id_booking = ?", (id_booking,))
    booking = cur.fetchone()
    if booking:
        if booking['status_pembayaran'] == 'Sudah Bayar':
            cur.execute("UPDATE kamar SET status = 'Tersedia' WHERE id_kamar = ?", (booking['id_kamar'],))
        cur.execute("DELETE FROM booking WHERE id_booking = ?", (id_booking,))
        conn.commit()
        
        cur.execute("SELECT * FROM booking ORDER BY id_booking ASC")
        remaining_bookings = cur.fetchall()
        
        if remaining_bookings:
            cur.execute("DROP TABLE IF EXISTS booking_temp")
            cur.execute("""
                CREATE TABLE booking_temp (
                    id_booking INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_kamar INTEGER NOT NULL,
                    nama TEXT NOT NULL,
                    email TEXT,
                    telepon TEXT,
                    tanggal_checkin TEXT,
                    tanggal_checkout TEXT,
                    catatan TEXT,
                    status_pembayaran TEXT DEFAULT 'Belum Bayar',
                    tanggal_booking TEXT,
                    FOREIGN KEY (id_kamar) REFERENCES kamar (id_kamar)
                )
            """)
            
            for booking_data in remaining_bookings:
                cur.execute("""
                    INSERT INTO booking_temp (id_kamar, nama, email, telepon, tanggal_checkin, tanggal_checkout, catatan, status_pembayaran, tanggal_booking)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    booking_data['id_kamar'],
                    booking_data['nama'],
                    booking_data['email'],
                    booking_data['telepon'],
                    booking_data['tanggal_checkin'],
                    booking_data['tanggal_checkout'],
                    booking_data['catatan'],
                    booking_data['status_pembayaran'],
                    booking_data['tanggal_booking']
                ))
            
            cur.execute("DROP TABLE booking")
            cur.execute("ALTER TABLE booking_temp RENAME TO booking")
            conn.commit()
    conn.close()
    return redirect(url_for("admin_bookings"))


if __name__ == "__main__":
    app.run(debug=True)
