from database import db
from bson import ObjectId

class UserModel:
    collection = db.users

    @staticmethod
    def create_user(username, email, password_hash, role="student"):
        new_user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role
        }
        return UserModel.collection.insert_one(new_user)

    @staticmethod
    def find_by_email(email):
        return UserModel.collection.find_one({"email": email})

    @staticmethod
    def find_by_id(user_id):
        return UserModel.collection.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def get_user_by_name(username):
        return UserModel.collection.find_one({"username": username})
    
    @staticmethod
    def get_all_users():
        return list(UserModel.collection.find({}, {"_id": 0, "username": 1, "email": 1, "role": 1}))

    @staticmethod
    def update_role(email, new_role):
        db.users.update_one({"email": email}, {"$set": {"role": new_role}})