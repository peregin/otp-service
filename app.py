from functools import wraps, lru_cache
from typing import Optional

from flask import Flask, request, jsonify, send_file
import pyotp
import psycopg2
import qrcode
import os
from io import BytesIO

from qrcode.image.pure import PyPNGImage

app = Flask(__name__)

DB_NAME = os.getenv("DB_NAME", "otp")
DB_USER = os.getenv("DB_USER", "otp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "otp")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5490")
DB_PARAMS = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

def init_db():
    with psycopg2.connect(DB_PARAMS) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username TEXT UNIQUE,
                            secret TEXT)''')
        conn.commit()

@lru_cache(maxsize=100)
def generate_totp_uri(secret: str, username: str, issuer: str = "MyApp") -> str:
    """Cache TOTP URI generation for frequently accessed combinations"""
    return pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name=issuer)

def register_user(username: str, secret: str) -> Optional[str]:
    """Handle user registration database operations"""
    try:
        with psycopg2.connect(DB_PARAMS) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, secret) VALUES (%s, %s)",
                    (username, secret)
                )
                conn.commit()
        return None
    except psycopg2.IntegrityError:
        return "Username already exists"

def validate_username(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.json.get("username")
        if not username:
            return jsonify({"error": "Username is required"}), 400
        return f(username, *args, **kwargs)
    return decorated_function

@app.route("/register", methods=["POST"])
@validate_username
def register(username: str):
    secret = pyotp.random_base32()
    error = register_user(username, secret)
    if error:
        return jsonify({"error": error}), 400
    otp_auth_url = generate_totp_uri(secret, username)
    return jsonify({"message": "User registered", "secret": secret, "otp_auth_url": otp_auth_url})

@app.route("/register/qr", methods=["POST"])
@validate_username
def register_qr(username: str):
    secret = pyotp.random_base32()
    error = register_user(username, secret)
    if error:
        return jsonify({"error": error}), 400
    otp_auth_url = generate_totp_uri(secret, username)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(otp_auth_url)
    qr.make(fit=True, image_factory=PyPNGImage)
    img = qr.make_image(fill="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    username = data.get("username")
    otp = data.get("otp")
    if not username or not otp:
        return jsonify({"error": "Username and OTP are required"}), 400
    
    with psycopg2.connect(DB_PARAMS) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT secret FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
    if not row:
        return jsonify({"error": "User not found"}), 404
    
    secret = row[0]
    totp = pyotp.TOTP(secret)
    
    if totp.verify(otp):
        return jsonify({"message": "OTP is valid"})
    else:
        return jsonify({"error": "Invalid OTP"}), 400

if __name__ == "__main__":
    init_db()
    app.run(debug=True)


