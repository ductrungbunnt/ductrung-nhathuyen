from datetime import datetime

import bcrypt
from database import db

class UserModel:
    @staticmethod
    def find_by_username(username):
        user = db.users.find_one({'username': username})
        if user:
            user['_id'] = str(user['_id'])
            print("Found user:", user)  # Debug print
            # Chỉ trả về các trường cần thiết
            return {
                '_id': user['_id'],
                'username': user['username'],
                'email': user['email'],
                'level': user['level'],
                'fullname': user.get('fullname', user['username']),
                'pass': user.get('pass')  # Chỉ lấy trường pass
            }
        return None

    # @staticmethod
    # def check_password(password, hashed_password):
    #     print("Checking password:", password)  # Debug print
    #     print("Stored password:", hashed_password)  # Debug print
    #     # So sánh mật khẩu trực tiếp
    #     return password == hashed_password

    @staticmethod
    def create_user(fullname, username, password, email, level='user'):
        # Create user document
        user = {
            'fullname': fullname,
            'username': username,
            'password':  UserModel.hash_password(password),  # Lưu mật khẩu trực tiếp
            'email': email,
            'level': level,
            'avatar': f'https://ui-avatars.com/api/?name={fullname.replace(" ", "+")}&background=random',
            'joinday': datetime.utcnow(),
            'lastlogin': datetime.utcnow()
        }
        
        # Check if username or email already exists
        if db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
            return None, 'Username hoặc email đã tồn tại'
        
        # Insert user
        result = db.users.insert_one(user)
        user['_id'] = str(result.inserted_id)
        user['joinday'] = user['joinday'].isoformat()
        user['lastlogin'] = user['lastlogin'].isoformat()
        
        # Remove password from response
        del user['password']
        
        return user, None
    
    @staticmethod
    def get_user_by_username(username):
        try:
            print(f"Searching for user with username: {username}")  # Debug log
            user = db.users.find_one({'username': username})
            print(f"Found user in database: {user}")  # Debug log
            return user
        except Exception as e:
            print('Lỗi khi lấy thông tin user:', str(e))
            return None
    
    @staticmethod
    def get_user_by_email(email):
        user = db.users.find_one({'email': email})
        if user:
            user['_id'] = str(user['_id'])
            user['joinday'] = user['joinday'].isoformat()
            user['lastlogin'] = user['lastlogin'].isoformat()
            return user
        return None
    
    @staticmethod
    def update_last_login(username):
        try:
            db.users.update_one(
                {'username': username},
                {'$set': {'lastlogin': datetime.utcnow()}}
            )
        except Exception as e:
            print('Lỗi khi cập nhật thời gian đăng nhập:', str(e))
    
    @staticmethod
    def get_all_users():
        users = list(db.users.find())
        for user in users:
            user['_id'] = str(user['_id'])
            user['joinday'] = user['joinday'].isoformat()
            user['lastlogin'] = user['lastlogin'].isoformat()
            del user['password']
        return users
    
    @staticmethod
    def update_user(user_id, update_data):
        if "password" in update_data:
            update_data["password"] = UserModel.hash_password(update_data["password"])
        # Không mã hóa mật khẩu nữa
        result = db.users.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete_user(user_id):
        result = db.users.delete_one({'_id': user_id})
        return result.deleted_count > 0 
    @staticmethod
    def get_all_users():
        return list(db.users.find({}, {"username": 1, "email": 1, "level": 1, "_id": 0}))
    
    @staticmethod
    def hash_password(password):
        # Hàm mã hóa mật khẩu
        
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def check_password(password, hashed_password):
        # print("So sánh: ", password, hashed_password)  # Debug print
        # Hàm kiểm tra mật khẩu
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
