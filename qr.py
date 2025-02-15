from io import BytesIO

import qrcode

def generate_qr(data: str) -> BytesIO:
    """
    Generate QR code

    Args:
        data: The QR code data
    Returns:
        BytesIO object with the QR code PNG image
    """
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return buf
