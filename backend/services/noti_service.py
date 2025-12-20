# services/noti_service.py
from models.noti_model import get_notifications_by_user_id_model, mark_all_as_read_model

def get_user_notifications(user_id):
    # Tại đây có thể thêm logic kiểm tra user_id có tồn tại không nếu cần
    
    # Gọi Model để lấy dữ liệu
    notifications = get_notifications_by_user_id_model(user_id)
    
    # Nếu cần xử lý dữ liệu (ví dụ format ngày tháng), làm ở đây
    # Ví dụ: for noti in notifications: noti['CREATED_AT'] = str(noti['CREATED_AT'])
    
    return notifications

def mark_read_service(user_id):
    return mark_all_as_read_model(user_id)