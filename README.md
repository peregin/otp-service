One time password generator service
==

Testing
--
```shell
# register
curl -X POST http://127.0.0.1:5000/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser"}'
     
{
  "message": "User registered",
  "otp_auth_url": "otpauth://totp/MyApp:testuser?secret=TDU6LBK5UAHPRUU65ZAWO7CZAECTBARY&issuer=MyApp",
  "secret": "TDU6LBK5UAHPRUU65ZAWO7CZAECTBARY"
}

# register with QR code
curl -X POST http://127.0.0.1:5000/register/qr \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser"}' \
     --output qr.png

# verify
curl -X POST http://127.0.0.1:5000/verify \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "otp": "123456"}'
```
