from configs import config

from pymongo import MongoClient

# Kết nối MongoDB
client = MongoClient(config.MONGO_URI)

# Chọn database
db = client["social_app"]  # Database mặc định

print(f"✅ Đã kết nối đến MongoDB: {config.MONGO_URI}")
print(f"📌 Đang sử dụng cơ sở dữ liệu: {db.name}")

