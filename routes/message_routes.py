from flask import Blueprint, request, jsonify
from models.message import MessageModel
import os
from werkzeug.utils import secure_filename

mess_bp = Blueprint("message", __name__)

UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "docx"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """ Kiểm tra định dạng tệp hợp lệ """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@mess_bp.route("/messages", methods=["POST"])
def send_message():
    """ Xử lý gửi tin nhắn, ảnh và file Word """
    user = request.form.get("user")
    message = request.form.get("message")
    room = request.form.get("room", "general")

    image_url = None
    file_url = None

    # Lưu ảnh
    if "image" in request.files:
        image = request.files["image"]
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = f"/uploads/{filename}"

    # Lưu file Word
    if "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            file_url = f"/uploads/{filename}"

    if not user and not (image_url or file_url):
        return jsonify({"message": "Thiếu thông tin người gửi hoặc nội dung"}), 400

    saved_msg = MessageModel.save_message(user, message, room, image_url, file_url)
    return jsonify(saved_msg), 201

@mess_bp.route("/messages", methods=["GET"])
def get_messages():
    """ Lấy danh sách tin nhắn """
    room = request.args.get("room", "general")
    messages = MessageModel.get_messages(room)
    return jsonify(messages)

@mess_bp.route("/messages/<message_id>", methods=["DELETE"])
def delete_message(message_id):
    """ Xóa tin nhắn theo ID """
    success = MessageModel.delete_message(message_id)
    if success:
        return jsonify({"message": "Message deleted successfully"})
    else:
        return jsonify({"message": "Message not found"}), 404
