import datetime
from bson import ObjectId
from database import db

class CommentModel:
    collection = db.comments

    @staticmethod
    def create_comment(post_id, content, author):
        new_comment = {
            "post_id": ObjectId(post_id),
            "content": content,
            "author": author,
            "created_at": datetime.datetime.utcnow()
        }
        return CommentModel.collection.insert_one(new_comment)

    @staticmethod
    def get_comments_by_post(post_id):
        return list(CommentModel.collection.find({"post_id": ObjectId(post_id)}))
    
    @staticmethod
    def get_comment_by_id(comment_id):
        return CommentModel.collection.find_one({"_id": ObjectId(comment_id)})

    @staticmethod
    def delete_comment(comment_id):
        return CommentModel.collection.delete_one({"_id": ObjectId(comment_id)})

    @staticmethod
    def get_recent_comments(limit=10):
        return list(CommentModel.collection.find().sort("created_at", -1).limit(limit))