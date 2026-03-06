import qrcode

url = "http://192.168.0.14:5000"

img = qrcode.make(url)
img.save("ders_qr.png")

print("QR kod oluşturuldu: ders_qr.png")
