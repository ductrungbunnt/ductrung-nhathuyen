from database import db
from bson import ObjectId

# Xóa dữ liệu cũ
db["users"].delete_many({})

# Hash mật khẩu
password = "Ductrung19@"

# Thêm user admin mẫu
admin_user = {
    "username": "admin",
    "fullname": "admin cao duc trung",
    "email": "caoductrung@gmail.com",
    "password": "Ductrung19@",
    "level": "admin"
}

db["users"].insert_one(admin_user)

print("✅ Đã tạo user admin mẫu thành công!")
