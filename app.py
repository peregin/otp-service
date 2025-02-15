import os
from functools import lru_cache
from http import HTTPStatus

from flask import Flask, jsonify, send_file
import pyotp
from database import init_db, register_user, get_user_secret
from decorators import RequestValidators
from qr import generate_qr

app = Flask(__name__)

APP_ISSUER = os.getenv("ISSUER", "peregin.com")

@lru_cache(maxsize=100)
def generate_totp_uri(secret: str, username: str, issuer: str = APP_ISSUER) -> str:
    """Cache TOTP URI generation for frequently accessed combinations"""
    return pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name=issuer)

@app.route("/register", methods=["POST"])
@RequestValidators.validate_username
def register(username: str):
    secret = pyotp.random_base32()
    error = register_user(username, secret)
    if error:
        return jsonify({"error": error}), HTTPStatus.CONFLICT
    otp_auth_url = generate_totp_uri(secret, username)
    return jsonify({"message": "User registered", "secret": secret, "otp_auth_url": otp_auth_url})

@app.route("/register/qr", methods=["POST"])
@RequestValidators.validate_username
def register_qr(username: str):
    secret = pyotp.random_base32()
    error = register_user(username, secret)
    if error:
        return jsonify({"error": error}), HTTPStatus.CONFLICT
    otp_auth_url = generate_totp_uri(secret, username)

    qr = generate_qr(otp_auth_url)
    return send_file(qr, mimetype='image/png')

@app.route("/verify", methods=["POST"])
@RequestValidators.validate_username
@RequestValidators.validate_otp
def verify(username: str, otp: str):
    secret, error = get_user_secret(username)
    if error:
        return jsonify({"error": error}), HTTPStatus.NOT_FOUND

    totp = pyotp.TOTP(secret)
    if totp.verify(otp):
        return jsonify({"message": "OTP is valid"})
    else:
        return jsonify({"error": "Invalid OTP"}), HTTPStatus.UNAUTHORIZED

if __name__ == "__main__":
    init_db()
    app.run(debug=True)


