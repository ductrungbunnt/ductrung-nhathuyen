from pymongo import MongoClient
from datetime import datetime
import bcrypt

from models.user import UserModel

from configs import config

# Kết nối MongoDB
client = MongoClient(config.MONGO_URI)
db = client.social_app

password = 'Ductrung19@'  # Mật khẩu cho tài khoản admin
# Tạo user admin
admin_user = {
    'username': 'admin',
    'fullname': 'admin cao duc trung',
    'password':  UserModel.hash_password(password),  # Lưu mật khẩu trực tiếp không mã hóa
    'email': 'caoductrung1932010@gmail.com',
    'level': 'admin',
    'joinday': datetime.utcnow(),
    'lastlogin': datetime.utcnow()
}

# Xóa tài khoản admin cũ nếu có
db.users.delete_many({'username': 'admin'})

# Thêm vào database
result = db.users.insert_one(admin_user)
print("Tạo tài khoản admin thành công!")
print("Username: admin")
print("Password: Ductrung19@") 