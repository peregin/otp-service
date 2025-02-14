from functools import wraps

from flask import Flask, request, jsonify, send_file
import pyotp
import psycopg2
import qrcode
import os
from io import BytesIO

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
    
    try:
        with psycopg2.connect(DB_PARAMS) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, secret) VALUES (%s, %s)", (username, secret))
            conn.commit()
    except psycopg2.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    
    otp_auth_url = pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name="MyApp")
    
    return jsonify({"message": "User registered", "secret": secret, "otp_auth_url": otp_auth_url})

@app.route("/register/qr", methods=["POST"])
@validate_username
def register_qr(username: str):
    secret = pyotp.random_base32()
    
    try:
        with psycopg2.connect(DB_PARAMS) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, secret) VALUES (%s, %s)", (username, secret))
            conn.commit()
    except psycopg2.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

    otp_auth_url = pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name="MyApp")
    
    img = qrcode.make(otp_auth_url)
    buf = BytesIO()
    img.save(buf)
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


