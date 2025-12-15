from flask import Blueprint, request, jsonify
from services.transaction_service import *

bp = Blueprint("transactions", __name__)

def success_response(data=None, message="Success"):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), 200

def error_response(message, status_code=400):
    return jsonify({
        "status": "error",
        "message": message
    }), status_code

@bp.post("/transactions/deposit")
def deposit():
    data = request.json
    tx_id = create_deposit(
        request.user["id"],
        data["account_id"],
        data["amount"]
    )
    return success_response({"transaction_id": tx_id})


@bp.post("/transactions/withdraw")
def withdraw():
    data = request.json
    tx_id = create_withdraw(
        request.user["id"],
        data["account_id"],
        data["amount"]
    )
    return success_response({"transaction_id": tx_id})


@bp.post("/transactions/transfer")
def transfer():
    data = request.json
    tx_id = create_transfer(
        request.user["id"],
        data["source_account_id"],
        data["destination_account_id"],
        data["amount"]
    )
    return success_response({"transaction_id": tx_id})


@bp.post("/transactions/<tx_id>/confirm")
def confirm(tx_id):
    data = request.json
    confirm_transaction(
        request.user["id"],
        tx_id,
        data["otp"]
    )
    return success_response()


@bp.post("/transactions/<tx_id>/cancel")
def cancel(tx_id):
    cancel_pending_transaction(request.user["id"], tx_id)
    return success_response()


@bp.post("/transactions/<tx_id>/retry")
def retry(tx_id):
    retry_transaction(request.user["id"], tx_id)
    return success_response()


@bp.post("/admin/transactions/<tx_id>/rollback")
def rollback(tx_id):
    rollback_transaction(request.user["id"], tx_id)
    return success_response()
