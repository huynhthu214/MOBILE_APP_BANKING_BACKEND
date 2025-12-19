def otp_email_template(otp_code, purpose="transaction"):
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
            ">
                {otp_code}
            </div>

            <p>Mã OTP này sẽ hết hạn sau <b>50 giây</b>.</p>
            <p>Nếu bạn không yêu cầu điều này, vui lòng bỏ qua email này.</p>

            <hr>
            <small>Hệ thốngZY Banking</small>
        </body>
    </html>
    """
