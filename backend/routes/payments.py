from flask import Blueprint, request, jsonify, render_template_string
from services.payment_service import create_payment
from services.payment_callback_service import handle_payment_callback
from db import get_conn # Import để lấy thông tin hiển thị

bp = Blueprint("payments", __name__, url_prefix="/api/v1/payments")

@bp.route('/create', methods=['POST'])
def create_payment_api():
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        amount = data.get('amount')
        provider = data.get('provider')
        payment_type = data.get('type')

        if not all([account_id, amount, provider, payment_type]):
             return jsonify({"error": "Missing required fields"}), 400

        result = create_payment(account_id, amount, provider, payment_type)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error create_payment: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# GIAO DIỆN MOCK ĐÃ ĐƯỢC RENDER LẠI ĐẸP HƠN
# ==========================================
@bp.route('/mock-view/<payment_id>', methods=['GET'])
def mock_payment_view(payment_id):
    # 1. Lấy thông tin từ DB để hiển thị lên giao diện
    conn = get_conn()
    payment_info = None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT AMOUNT, PROVIDER FROM PAYMENT WHERE PAYMENT_ID = %s", (payment_id,))
            payment_info = cur.fetchone()
    finally:
        conn.close()

    if not payment_info:
        return "<h1>Giao dịch không tồn tại</h1>", 404

    # Xử lý dữ liệu hiển thị (tùy thuộc cursor trả về dict hay tuple)
    if isinstance(payment_info, dict):
        amount = payment_info['AMOUNT']
        provider = payment_info['PROVIDER'].upper()
    else:
        amount = payment_info[0]
        provider = payment_info[1].upper()

    # 2. Template HTML mới
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mock Payment</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 90%; max-width: 400px; text-align: center; }
            .provider-tag { background: #e7f3ff; color: #1877f2; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; display: inline-block; margin-bottom: 1rem; }
            .amount { font-size: 2rem; font-weight: bold; color: #1c1e21; margin: 1rem 0; }
            .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; margin-bottom: 0.8rem; transition: 0.3s; }
            .btn-success { background-color: #28a745; color: white; }
            .btn-success:hover { background-color: #218838; }
            .btn-fail { background-color: #f8f9fa; color: #606770; border: 1px solid #ddd; }
            .btn-fail:hover { background-color: #e4e6eb; }
            .footer { font-size: 0.8rem; color: #8a8d91; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="provider-tag">{{ provider }} SANDBOX</div>
            <h2 style="margin:0; color:#333;">Xác nhận nạp tiền</h2>
            <p style="color:#65676b; font-size:0.9rem;">Vui lòng kiểm tra kỹ số tiền trước khi bấm</p>
            
            <div class="amount">{{ "{:,.0f}".format(amount) }} VND</div>

            <form action="/api/v1/payments/process" method="POST">
                <input type="hidden" name="payment_id" value="{{ pid }}">
                <input type="hidden" name="result" value="success">
                <button type="submit" class="btn btn-success">Xác nhận thanh toán</button>
            </form>

            <form action="/api/v1/payments/process" method="POST">
                <input type="hidden" name="payment_id" value="{{ pid }}">
                <input type="hidden" name="result" value="fail">
                <button type="submit" class="btn btn-fail">Hủy bỏ</button>
            </form>

            <div class="footer">ID: {{ pid }}</div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, pid=payment_id, amount=amount, provider=provider)

@bp.route('/process', methods=['POST'])
def process_payment_api():
    try:
        payment_id = request.form.get('payment_id')
        result_status = request.form.get('result')
        response = handle_payment_callback(payment_id, result_status)
        
        if response.get("status") == "success":
            return """<div style='text-align:center; margin-top:50px;'>
                        <h1 style='color:green;'>Thanh toán thành công!</h1>
                        <p>Tiền đã được cộng vào tài khoản của bạn.</p>
                      </div>"""
        else:
            return f"""<div style='text-align:center; margin-top:50px;'>
                        <h1 style='color:red;'>Giao dịch thất bại</h1>
                        <p>{response.get('message', 'Đã có lỗi xảy ra')}</p>
                      </div>"""
    except Exception as e:
        return f"Error: {str(e)}", 500