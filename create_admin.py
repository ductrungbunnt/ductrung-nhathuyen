from pymongo import MongoClient
from datetime import datetime

# Kết nối MongoDB
client = MongoClient("mongodb+srv://tranxuancong2023:qUJomTP0jDdHmuNV@cluster0.sfcxjee.mongodb.net/ml?retryWrites=true&w=majority")
db = client.social_app

# Tạo tài khoản admin
admin_user = {
    'username': 'admin',
    'fullname': 'admin cao duc trung',
    'password': 'Ductrung19@',
    'email': 'caoductrung1932010@gmail.com',
    'level': 'admin',
    'joinday': datetime.utcnow(),
    'lastlogin': datetime.utcnow()
}

# Kiểm tra xem tài khoản admin đã tồn tại chưa
existing_admin = db.users.find_one({'username': 'admin'})
if existing_admin:
    print("Tài khoản admin đã tồn tại")
else:
    # Thêm tài khoản admin vào database
    result = db.users.insert_one(admin_user)
    print("Đã tạo tài khoản admin thành công") 