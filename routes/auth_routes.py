from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token
from bson import ObjectId
from models.user import UserModel
import sys
import os
import datetime
from pymongo import MongoClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import db

# Tạo Blueprint cho auth
auth_bp = Blueprint('auth', __name__)

# Chọn collection `users`
collection_name = "users"
collection = db[collection_name]


def json_converter(data):
    if isinstance(data, ObjectId):
        return str(data)
    raise TypeError(f"Object of type {type(data).__name__} is not JSON serializable")


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        # Kiểm tra nếu thông tin không đầy đủ
        if not data or "username" not in data or "email" not in data:
            return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400

        # Tạo user, mặc định level là 'user'
        user, error = UserModel.create_user(
            fullname=data.get("fullname", data["username"]),
            username=data["username"],
            password=data.get("password", "123456"),
            email=data["email"],
            level=data.get("level", "user")  # Đảm bảo level mặc định là 'user'
        )

        # Nếu có lỗi trong quá trình tạo user, trả về thông báo lỗi
        if error:
            return jsonify({"success": False, "message": error}), 400

        # Trả về thông báo thành công và thông tin user (trừ password)
        return jsonify({"success": True, "message": "Đăng ký thành công", "user": user}), 201

    except Exception as e:
        # Bắt lỗi và trả về thông báo lỗi
        return jsonify({"success": False, "message": f"Lỗi đăng ký: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or "username" not in data or "password" not in data:
            return jsonify({"success": False, "message": "Vui lòng nhập tên đăng nhập và mật khẩu"}), 400

        user = db.users.find_one({"username": {"$regex": f"^{data['username']}$", "$options": "i"}})
        if not user:
            return jsonify({"success": False, "message": "Tên đăng nhập không tồn tại"}), 401

        hashed_db_password = user.get("password", "")
        input_password = data["password"]

        if UserModel.check_password(input_password, hashed_db_password):
            # Cập nhật last login
            UserModel.update_last_login(user["username"])

            token = create_access_token(
                identity=str(user["_id"]),
                additional_claims={
                    "username": user["username"],
                    "level": user.get("level", "user")
                },
                expires_delta=datetime.timedelta(hours=3)
            )

            response_data = {
                "success": True,
                "message": "Đăng nhập thành công",
                "token": token,
                "user": {
                    "id": str(user["_id"]),
                    "username": user.get("username", ""),
                    "email": user.get("email", ""),
                    "level": user.get("level", "user"),
                    "fullname": user.get("fullname", user.get("username", ""))
                }
            }
            return jsonify(response_data)

        return jsonify({"success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng"}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi đăng nhập: {str(e)}"}), 500

@auth_bp.route('/get-key', methods=['POST'])
def get_key():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["apikey_dbs"]  # Tên database
        api_collection = db["apikey"]  # Tên collection

        data = request.get_json()
        print(data)

        return jsonify({"success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng"}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi đăng nhập: {str(e)}"}), 500


