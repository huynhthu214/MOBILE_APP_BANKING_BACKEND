from models.admin_dashboard_model import DashboardModel

class AdminDashboardService:
    @staticmethod
    def get_dashboard_stats():
        # Lấy dữ liệu từ Model
        total_users = DashboardModel.get_total_users()
        total_transactions = DashboardModel.get_total_transactions()
        total_amount = DashboardModel.get_total_transaction_amount()
        
        recent_tx = DashboardModel.get_recent_transactions(5)
        
        if total_amount is None:
            total_amount = 0.0

        return {
            "status": "success",
            "total_users": total_users,
            "total_transactions": total_transactions,
            "total_amount": float(total_amount),
            "recent_transactions": recent_tx
        }
    @staticmethod
    def get_customers_list(search_query):
        return DashboardModel.get_all_customers(search_query)

    @staticmethod
    def get_transactions_list(search_query, status_filter):
        return DashboardModel.get_all_transactions(search_query, status_filter)