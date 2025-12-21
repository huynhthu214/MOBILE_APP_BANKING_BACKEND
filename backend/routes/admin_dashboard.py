from flask import Blueprint, jsonify, request
from services.admin_dashboard_service import AdminDashboardService

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

@admin_dashboard_bp.route("/admin/dashboard/stats", methods=["GET"])
def dashboard_stats():
    data = AdminDashboardService.get_dashboard_stats()
    return jsonify(data), 200

@admin_dashboard_bp.route("/admin/users", methods=["GET"])
def get_users_list():
    search = request.args.get('search', '')
    data = AdminDashboardService.get_customers_list(search)
    return jsonify({"status": "success", "data": data}), 200

@admin_dashboard_bp.route("/admin/transactions", methods=["GET"])
def get_transactions_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '') #
    
    data = AdminDashboardService.get_transactions_list(search, status)
    return jsonify({"status": "success", "data": data}), 200