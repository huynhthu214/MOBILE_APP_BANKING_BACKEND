# services/noti_service.py
from models.noti_model import get_notifications_by_user_id_model, mark_all_as_read_model, mark_single_as_read_model

def get_user_notifications(user_id):
    notifications = get_notifications_by_user_id_model(user_id)
    return notifications

def mark_read_service(user_id):
    return mark_all_as_read_model(user_id)

def mark_single_read_service(noti_id):
    # Logic nghiệp vụ để đánh dấu một thông báo cụ thể là đã đọc
    return mark_single_as_read_model(noti_id)