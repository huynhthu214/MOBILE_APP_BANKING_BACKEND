# Sửa lại hàm template để nhận thêm tham số expires_in
def otp_email_template(otp_code, purpose="transaction", expires_in="5 phút"):
    print(f"DEBUG OTP: {otp_code}")
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif">
            <h2>ZY Banking - Xác thực OTP</h2>
            <p>Mã OTP cho <b> {purpose} </b> là:</p>

            <div style="
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 4px;
                margin: 16px 0;
                color: #007bff; 
            ">
                {otp_code}
            </div>

            <p>Mã OTP này sẽ hết hạn sau <b>{expires_in}</b>.</p>
            <p>Nếu bạn không yêu cầu điều này, vui lòng bỏ qua email này.</p>

            <hr>
            <small>Hệ thống ZY Banking</small>
        </body>
    </html>
    """