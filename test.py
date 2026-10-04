import jwt
import qrcode
import datetime

payload = {
    "ticket_id": "TCK123",
    "visits_remaining": 3,
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
}

token = jwt.encode(payload, "mysecretkey", algorithm="HS256")
print("JWT:", token)

img = qrcode.make(token)
img.save("test_qr.png")
print("QR code saved as test_qr.png")