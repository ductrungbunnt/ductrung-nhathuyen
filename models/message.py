from database import db
from datetime import datetime, timezone, timedelta
from bson import ObjectId
import os

# Thiết lập múi giờ Việt Nam
def get_current_time():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    vietnam_tz = timezone(timedelta(hours=7))
    vietnam_now = utc_now.astimezone(vietnam_tz)
    return vietnam_now

UPLOAD_FOLDER = "uploads/"
BASE_URL = "http://localhost:8000"  # Đổi thành URL thật nếu deploy
# Tạo thư mục nếu chưa có
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class MessageModel:
    collection = db.messages  # Kết nối MongoDB

    @staticmethod
    def save_message(user, message=None, room="general", image_url=None, file_url=None):
        """ Lưu tin nhắn vào MongoDB """
        msg = {
            "user": user,
            "message": message,
            "room": room,
            "timestamp": get_current_time().isoformat(timespec="milliseconds"),
            "image_url": image_url,
            "file_url": file_url
        }
        result = MessageModel.collection.insert_one(msg)
        msg["_id"] = str(result.inserted_id)  # ✅ Chuyển ObjectId thành chuỗi
        return msg

    @staticmethod
    def get_messages(room):
        """ Lấy danh sách tin nhắn từ MongoDB theo phòng chat """
        messages = MessageModel.collection.find({"room": room}).sort("timestamp", 1)
        return [
            {
                "message_id": str(msg["_id"]),
                "user": msg["user"],
                "message": msg.get("message"),
                "timestamp": msg["timestamp"],
                "image_url": f"{BASE_URL}{msg['image_url']}" if msg.get("image_url") else None,
                "file_url": f"{BASE_URL}{msg['file_url']}" if msg.get("file_url") else None,
            }
            for msg in messages
        ]

    @staticmethod
    def delete_message(message_id):
        """ Xóa tin nhắn bằng ID """
        result = MessageModel.collection.delete_one({"_id": ObjectId(message_id)})
        return result.deleted_count > 0  # True nếu xóa thành công
