from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "scendy1904"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="scendy1904",
    database="crud_kamar_hotel"
)
cursor = db.cursor(dictionary=True)

@app.template_filter('rupiah')
def rupiah_format(value):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return value
    return 'Rp ' + format(int(round(amount)), ',d').replace(',', '.')

@app.route("/")
def index():
    search_query = request.args.get('search', '')
    if search_query:
        cursor.execute("""
            SELECT k1.* FROM kamar k1
            INNER JOIN (
                SELECT tipe_kamar, MIN(id_kamar) as min_id
                FROM kamar
                WHERE status='Tersedia' AND (nomor_kamar LIKE %s OR tipe_kamar LIKE %s)
                GROUP BY tipe_kamar
            ) k2 ON k1.tipe_kamar = k2.tipe_kamar AND k1.id_kamar = k2.min_id
            WHERE k1.status='Tersedia'
            ORDER BY FIELD(k1.tipe_kamar, 'Standard', 'Deluxe', 'Suite', 'VIP')
        """, ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("""
            SELECT k1.* FROM kamar k1
            INNER JOIN (
                SELECT tipe_kamar, MIN(id_kamar) as min_id
                FROM kamar
                WHERE status='Tersedia'
                GROUP BY tipe_kamar
            ) k2 ON k1.tipe_kamar = k2.tipe_kamar AND k1.id_kamar = k2.min_id
            WHERE k1.status='Tersedia'
            ORDER BY FIELD(k1.tipe_kamar, 'Standard', 'Deluxe', 'Suite', 'VIP')
        """)
    kamars = cursor.fetchall()
    return render_template("index.html", kamars=kamars, search_query=search_query)

@app.route("/kamar/<int:id>")
def kamar_detail(id):
    cursor.execute("SELECT * FROM kamar WHERE id_kamar=%s", (id,))
    kamar = cursor.fetchone()
    return render_template("product_detail.html", kamar=kamar)

@app.route("/cart/add/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(id)
    return redirect("/cart")

@app.route("/cart")
def cart():
    if "cart" not in session:
        session["cart"] = []
    cart_items = []
    for kid in session["cart"]:
        cursor.execute("SELECT * FROM kamar WHERE id_kamar=%s", (kid,))
        cart_items.append(cursor.fetchone())
    total = sum(item["harga_per_malam"] for item in cart_items if item)
    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "cart" not in session or not session["cart"]:
        return redirect("/cart")

    cart_items = []
    for kid in session["cart"]:
        cursor.execute("SELECT * FROM kamar WHERE id_kamar=%s", (kid,))
        cart_items.append(cursor.fetchone())
    total = sum(item["harga_per_malam"] for item in cart_items if item)

    if request.method == "POST":
        session["cart"] = []
        return render_template("checkout.html", cart_items=cart_items, total=total, success=True)

    return render_template("checkout.html", cart_items=cart_items, total=total, success=False)

@app.route("/kategori/<kategori>")
def kategori_detail(kategori):
    cursor.execute("SELECT * FROM kamar WHERE tipe_kamar=%s AND status='Tersedia'", (kategori,))
    kamars = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as stok FROM kamar WHERE tipe_kamar=%s AND status='Tersedia'", (kategori,))
    stok_result = cursor.fetchone()
    stok = stok_result['stok'] if stok_result else 0
    
    info_data = {
        'Standard': {
            'title': 'Standard Room',
            'description': 'Kamar standar seluas 20 m² ini dilengkapi dengan fasilitas lengkap untuk kenyamanan Anda selama menginap.',
            'luas': '20 m²',
            'fasilitas': [
                'Kamar tidur dengan tempat tidur double',
                'AC dengan remote control',
                'TV LED 32 inch',
                'Kamar mandi dengan shower',
                'WiFi gratis',
                'Lemari pakaian',
                'Meja kerja',
                'Air mineral gratis'
            ],
            'keuntungan': [
                'Akses ke kolam renang hotel',
                'Akses ke pusat kebugaran',
                'Layanan kamar 24 jam'
            ],
            'foto': 'kamar1.jpg'
        },
        'Deluxe': {
            'title': 'Deluxe Room',
            'description': 'Kamar deluxe seluas 30 m² ini layaknya sebuah oasis dalam hunian mewah dengan fasilitas premium untuk kenyamanan maksimal.',
            'luas': '30 m²',
            'fasilitas': [
                'Kamar tidur dengan tempat tidur king size',
                'AC dengan remote control',
                'TV LED 43 inch dengan Smart TV',
                'Kamar mandi dengan shower dan bathtub',
                'WiFi gratis high speed',
                'Lemari pakaian besar',
                'Meja kerja ergonomis',
                'Minibar',
                'Air mineral dan snack gratis',
                'Balkon dengan pemandangan'
            ],
            'keuntungan': [
                'Akses ke kolam renang ukuran olimpiade',
                'Akses ke pusat kebugaran dan fasilitas olahraga lainnya',
                'Layanan kamar 24 jam',
                'Surat kabar harian lokal dan internasional'
            ],
            'foto': 'kamar3.jpg'
        },
        'Suite': {
            'title': 'Suite Room',
            'description': 'Kamar suite seluas 50 m² ini layaknya sebuah oasis dalam hunian mewah dengan ruang tamu terpisah dari ruang tidur utama.',
            'luas': '50 m²',
            'fasilitas': [
                'Kamar tidur master dengan tempat tidur king size',
                'Ruang tamu terpisah',
                'AC dengan remote control',
                'TV LED 55 inch Smart TV di kamar dan ruang tamu',
                'Kamar mandi mewah dengan shower dan bathtub jacuzzi',
                'WiFi gratis high speed',
                'Walk-in closet',
                'Meja kerja premium',
                'Minibar lengkap',
                'Snack dan minuman premium gratis',
                'Balkon luas dengan pemandangan',
                'Coffee maker',
                'Safe deposit box'
            ],
            'keuntungan': [
                'Akses ke kolam renang ukuran olimpiade, pusat kebugaran dan fasilitas olahraga lainnya',
                'Layanan butler 24 jam',
                'Jamuan teh sore pukul 15.00 WIB - 17.00 WIB di Executive Lounge',
                'Jamuan koktail beserta kudapan ringan dari pukul 18.00 WIB - 20.00 WIB'
            ],
            'foto': 'kamar5.jpg'
        },
        'VIP': {
            'title': 'VIP Room',
            'description': 'Kamar VIP seluas 80 m² ini layaknya sebuah oasis dalam hunian mewah dengan ruang tamu dan ruang makan terpisah dari ruang tidur utama.',
            'luas': '80 m²',
            'fasilitas': [
                'Kamar tidur master mewah dengan tempat tidur king size premium',
                'Ruang tamu dan ruang makan terpisah',
                'AC dengan remote control dan sistem kontrol suhu canggih',
                'TV LED 65 inch Smart TV di kamar, ruang tamu, dan kamar mandi',
                'Kamar mandi mewah dengan shower rain, bathtub jacuzzi, dan sauna',
                'WiFi gratis ultra high speed',
                'Walk-in closet premium',
                'Meja kerja executive',
                'Minibar premium lengkap',
                'Snack, minuman, dan buah premium gratis',
                'Balkon pribadi luas dengan pemandangan eksklusif',
                'Coffee maker premium',
                'Safe deposit box digital'
            ],
            'keuntungan': [
                'Layanan butler 24 jam',
                'Jamuan teh sore pukul 15.00 WIB - 17.00 WIB dan jamuan koktail beserta kudapan ringan dari pukul 18.00 WIB - 20.00 WIB di VIP Lounge',
                'Jasa binatu bebas biaya untuk 2 potong baju per hari',
                'Penggunaan ruang rapat tanpa biaya selama 2 jam',
                'Bebas akses dan penggunaan kolam renang ukuran olimpiade, pusat kebugaran dan fasilitas olahraga lainnya'
            ],
            'foto': 'kamar7.jpg'
        }
    }
    
    info = info_data.get(kategori, {
        'title': kategori,
        'description': 'Informasi tentang kelas kamar ' + kategori,
        'luas': '-',
        'fasilitas': [],
        'keuntungan': [],
        'foto': 'default.jpg'
    })
    
    return render_template("kategori_detail.html", kamars=kamars, kategori=kategori, info=info, stok=stok)

if __name__ == "__main__":
    app.run(debug=True)

