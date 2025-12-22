from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["crud_database"]
products = db["products"]

try:
    if products.count_documents({}) == 0:
        produk = [
            {"name": "Laptop ASUS", "price": 8000000, "jumlah": 10, "gambar": "laptop.jpg"},
            {"name": "Mouse Wireless", "price": 150000, "jumlah": 25, "gambar": "mouse.jpg"},
            {"name": "Keyboard Mechanical", "price": 500000, "jumlah": 15, "gambar": "keyboard.jpg"},
            {"name": "Monitor 24 inch", "price": 2500000, "jumlah": 8, "gambar": "monitor.jpg"},
            {"name": "Webcam HD", "price": 300000, "jumlah": 20, "gambar": "webcam.jpg"},
            {"name": "Headset Gaming", "price": 750000, "jumlah": 12, "gambar": "headset.jpg"}
        ]
        products.insert_many(produk)
except:
    db.drop_collection("products")
    products = db["products"]
    produk = [
        {"name": "Laptop ASUS", "price": 8000000, "jumlah": 10, "gambar": "laptop.jpg"},
        {"name": "Mouse Wireless", "price": 150000, "jumlah": 25, "gambar": "mouse.jpg"},
        {"name": "Keyboard Mechanical", "price": 500000, "jumlah": 15, "gambar": "keyboard.jpg"},
        {"name": "Monitor 24 inch", "price": 2500000, "jumlah": 8, "gambar": "monitor.jpg"},
        {"name": "Webcam HD", "price": 300000, "jumlah": 20, "gambar": "webcam.jpg"},
        {"name": "Headset Gaming", "price": 750000, "jumlah": 12, "gambar": "headset.jpg"}
    ]
    products.insert_many(produk)

@app.route("/")
def index():
    data = list(products.find())
    return render_template("index.html", products=data)

@app.route("/product/<id>")
def detail(id):
    product = products.find_one({"_id": ObjectId(id)})
    return render_template("detail.html", product=product)

@app.route("/cart")
def cart():
    return render_template("cart.html")

if __name__ == "__main__":
    app.run(debug=True)

