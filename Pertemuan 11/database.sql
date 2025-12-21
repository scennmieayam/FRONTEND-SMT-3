CREATE DATABASE IF NOT EXISTS crud_kamar_hotel;
USE crud_kamar_hotel;

CREATE TABLE IF NOT EXISTS kamar (
    id_kamar INT AUTO_INCREMENT PRIMARY KEY,
    nomor_kamar VARCHAR(50) NOT NULL,
    tipe_kamar VARCHAR(100) NOT NULL,
    harga_per_malam DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    filename VARCHAR(255)
);

INSERT INTO kamar (nomor_kamar, tipe_kamar, harga_per_malam, status, filename) VALUES
('101', 'Standard', 500000, 'Tersedia', 'kamar1.jpg'),
('102', 'Standard', 500000, 'Tersedia', 'kamar2.jpg'),
('103', 'Standard', 500000, 'Tersedia', 'kamar1.jpg'),
('104', 'Standard', 500000, 'Tersedia', 'kamar2.jpg'),
('201', 'Deluxe', 800000, 'Tersedia', 'kamar3.jpg'),
('202', 'Deluxe', 800000, 'Tersedia', 'kamar4.jpg'),
('203', 'Deluxe', 800000, 'Tersedia', 'kamar3.jpg'),
('204', 'Deluxe', 800000, 'Tersedia', 'kamar4.jpg'),
('301', 'Suite', 1500000, 'Tersedia', 'kamar5.jpg'),
('302', 'Suite', 1500000, 'Tersedia', 'kamar6.jpg'),
('303', 'Suite', 1500000, 'Tersedia', 'kamar5.jpg'),
('304', 'Suite', 1500000, 'Tersedia', 'kamar6.jpg'),
('401', 'VIP', 2500000, 'Tersedia', 'kamar7.jpg'),
('402', 'VIP', 2500000, 'Tersedia', 'kamar8.jpg'),
('403', 'VIP', 2500000, 'Tersedia', 'kamar7.jpg'),
('404', 'VIP', 2500000, 'Tersedia', 'kamar8.jpg');

