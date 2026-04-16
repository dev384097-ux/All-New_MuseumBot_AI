import qrcode
import io
import base64

def generate_upi_qr(upi_id, name, amount, transaction_id):
    # UPI URL format: upi://pay?pa=<upi_id>&pn=<name>&am=<amount>&tr=<transaction_id>&cu=INR
    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&tr={transaction_id}&cu=INR"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Example usage
upi_id = "your-upi-id@bank"
name = "MuseumBot"
amount = "100.00"
transaction_id = "ORDER12345"
qr_base64 = generate_upi_qr(upi_id, name, amount, transaction_id)
print(f"Generated QR Base64 (first 100 chars): {qr_base64[:100]}...")
