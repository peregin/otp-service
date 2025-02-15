import os
from functools import wraps, lru_cache
from flask import Flask, request, jsonify, send_file
import pyotp
from database import init_db, register_user, get_user_secret
from qr import generate_qr

app = Flask(__name__)

APP_ISSUER = os.getenv("ISSUER", "peregin.com")

@lru_cache(maxsize=100)
def generate_totp_uri(secret: str, username: str, issuer: str = APP_ISSUER) -> str:
    """Cache TOTP URI generation for frequently accessed combinations"""
    return pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name=issuer)

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

    qr = generate_qr(otp_auth_url)
    return send_file(qr, mimetype='image/png')

@app.route("/verify", methods=["POST"])
@validate_username
def verify(username: str):
    data = request.json
    otp = data.get("otp")
    if not otp:
        return jsonify({"error": "Username and OTP are required"}), 400
    secret, error = get_user_secret(username)
    if error:
        return jsonify({"error": error}), 404

    totp = pyotp.TOTP(secret)
    if totp.verify(otp):
        return jsonify({"message": "OTP is valid"})
    else:
        return jsonify({"error": "Invalid OTP"}), 400

if __name__ == "__main__":
    init_db()
    app.run(debug=True)


