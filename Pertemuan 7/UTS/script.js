//data harga barang
const hargaBarang = {
    'PC': {
        'PC IBM Core i7': 5600000,
        'Laptop Asus Core i5': 4500000,
        'Laptop Lenovo AMD Ryzen 5': 9500000
    },
    'AKSESORIS': {
        'Flasdisk 32gb': 50000,
        'Hardisk 256 gb': 1250000,
        'Speaker Aktif': 255000
    }
};

let selectedItems = [];

//popup kategori
function showKategori() {
    document.getElementById('popupKategori').style.display = 'block';
    closeOtherPopups('popupKategori');
}

//select kategori
function selectKategori(kategori) {
    document.getElementById('kategori').value = kategori;
    document.getElementById('popupKategori').style.display = 'none';
}

//popup items
function showItems() {
    const kategori = document.getElementById('kategori').value;
    
    if (kategori === 'PC / LAPTOP') {
        document.getElementById('popupPC').style.display = 'block';
        closeOtherPopups('popupPC');
    } else if (kategori === 'AKSESORIS') {
        document.getElementById('popupAksesoris').style.display = 'block';
        closeOtherPopups('popupAksesoris');
    } else {
        alert('Pilih kategori terlebih dahulu!');
    }
}

//popup jenis penjualan
function showJenisPenjualan() {
    document.getElementById('popupJenis').style.display = 'block';
    closeOtherPopups('popupJenis');
}

//close popup
function closePopup(popupId) {
    document.getElementById(popupId).style.display = 'none';
}

//close popup lainnya
function closeOtherPopups(currentPopup) {
    const popups = ['popupPC', 'popupAksesoris', 'popupJenis'];
    popups.forEach(popup => {
        if (popup !== currentPopup) {
            document.getElementById(popup).style.display = 'none';
        }
    });
}

//save item (PC/Laptop atau Aksesoris)
function saveItem(type) {
    selectedItems = [];
    let namaBarang = '';
    
    if (type === 'pc') {
        const radios = document.querySelectorAll('input[name="radioPC"]:checked');
        if (radios.length === 0) {
            alert('Pilih salah satu item!');
            return;
        }
        const selectedRadio = radios[0];
        namaBarang = selectedRadio.value;
        selectedItems.push({
            nama: namaBarang,
            harga: hargaBarang['PC'][namaBarang],
            type: 'PC'
        });
        closePopup('popupPC');
    } else if (type === 'aksesoris') {
        const checkboxes = document.querySelectorAll('input[name="checkboxAks"]:checked');
        if (checkboxes.length === 0) {
            alert('Pilih minimal satu item!');
            return;
        }
        checkboxes.forEach(cb => {
            const namaAks = cb.value;
            selectedItems.push({
                nama: namaAks,
                harga: hargaBarang['AKSESORIS'][namaAks],
                type: 'AKSESORIS'
            });
        });
        namaBarang = selectedItems.map(item => item.nama).join(', ');
        closePopup('popupAksesoris');
    }
    
    // Update nama barang
    document.getElementById('namaBarang').value = namaBarang;
    
    // Update harga satuan (total harga semua item)
    let totalHargaSatuan = 0;
    selectedItems.forEach(item => {
        totalHargaSatuan += item.harga;
    });
    document.getElementById('hargaSatuan').value = 'Rp. ' + formatRupiah(totalHargaSatuan);
    
    // Reset jumlah dan recalculate
    document.getElementById('jumlah').value = 1;
    calculatePrice();
}

//save jenis penjualan
function saveJenis() {
    const radios = document.querySelectorAll('input[name="radioJenis"]:checked');
    if (radios.length === 0) {
        alert('Pilih jenis penjualan!');
        return;
    }
    
    const selectedRadio = radios[0];
    document.getElementById('jenisPenjualan').value = selectedRadio.value;
    closePopup('popupJenis');
    calculatePrice();
}

//menghitung total harga
function calculatePrice() {
    //get harga satuan dan jumlah
    let jumlah = parseInt(document.getElementById('jumlah').value) || 0;
    let totalHargaSatuan = 0;
    
    selectedItems.forEach(item => {
        totalHargaSatuan += item.harga;
    });
    
    //hitung total penjualan
    let totalPenjualan = totalHargaSatuan * jumlah;
    
    //hitung diskon (10% jika tunai)
    let jenisPenjualan = document.getElementById('jenisPenjualan').value;
    let diskon = 0;
    if (jenisPenjualan.includes('Tunai')) {
        diskon = totalPenjualan * 0.1;
    }
    
    //hitung pajak
    let pajak = 0;
    selectedItems.forEach(item => {
        let persenPajak = item.type === 'PC' ? 0.15 : 0.10;
        pajak += item.harga * persenPajak * jumlah;
    });
    
    //hitung harga total
    let hargaTotal = totalPenjualan - diskon + pajak;
    
    //display
    document.getElementById('totalPenjualan').textContent = 'Rp. ' + formatRupiah(totalPenjualan);
    document.getElementById('diskon').textContent = 'Rp. ' + formatRupiah(diskon);
    document.getElementById('pajak').textContent = 'Rp. ' + formatRupiah(pajak);
    document.getElementById('hargaTotal').textContent = 'Rp. ' + formatRupiah(hargaTotal);
}

//format duit
function formatRupiah(angka) {
    return angka.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

