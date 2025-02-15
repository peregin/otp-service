One time password generator service
==

Docs
--
http://localhost:5000/docs

Project
--
```shell
poetry show --outdated
```

Building
--
```shell
docker build -t otp-service .
docker run --rm -it -p 5000:8000 otp-service
```

Testing
--
```shell
# register
curl -X 'POST' \
  'http://localhost:5000/register?username=testuser' \
  -H 'accept: application/json' \
  -d ''

# register with QR code
curl -X 'POST' \
  'http://localhost:5000/register/qr?username=testuser' \
  -H 'accept: application/json' \
  -d '' \
  --output qr.png
     
# verify
curl -X 'POST' \
  'http://localhost:5000/verify?username=testuser&otp=123456' \
  -H 'accept: application/json' \
  -d ''
```
