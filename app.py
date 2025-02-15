import os
from functools import lru_cache

import pyotp
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse

from database import init_db, register_user, get_user_secret
from qr import generate_qr

app = FastAPI()

APP_ISSUER = os.getenv("ISSUER", "peregin.com")

@lru_cache(maxsize=100)
def generate_totp_uri(secret: str, username: str, issuer: str = APP_ISSUER) -> str:
    """Cache TOTP URI generation for frequently accessed combinations"""
    return pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name=issuer)

@app.post("/register")
def register(username: str):
    secret = pyotp.random_base32()
    error = register_user(username, secret)
    if error:
        raise HTTPException(status_code=409, detail=error)
    otp_auth_url = generate_totp_uri(secret, username)
    return {
        "message": "User registered",
        "secret": secret,
        "otp_auth_url": otp_auth_url
    }

@app.post("/register/qr")
def register_qr(username: str):
    secret = pyotp.random_base32()
    error = register_user(username, secret)
    if error:
        raise HTTPException(status_code=409, detail=error)

    otp_auth_url = generate_totp_uri(secret, username)
    qr = generate_qr(otp_auth_url)

    return StreamingResponse(qr, media_type="image/png")

@app.post("/verify")
def verify(username: str, otp: str):
    secret, error = get_user_secret(username)
    if error:
        raise HTTPException(status_code=404, detail=error)

    totp = pyotp.TOTP(secret)
    if totp.verify(otp):
        return {"message": "OTP is valid"}
    else:
        raise HTTPException(status_code=401, detail="Invalid OTP")

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)


