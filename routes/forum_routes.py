from flask import Blueprint, request, jsonify
from models.forum import ForumModel
from models.users import UserModel
from bson import ObjectId
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import db

# Khai báo Blueprint (KHÔNG CẦN lặp lại "/forum" trong các route)
forum_bp = Blueprint('forum', __name__)
collection = db["posts"]

def serialize_objectid(obj):
    return str(obj) if isinstance(obj, ObjectId) else obj

# 🟢 Tạo bài viết
@forum_bp.route("/posts", methods=["POST"])
def create_post():

    print('create post in router forum')
    data = request.json
    title = data.get("title")
    content = data.get("content")
    author = data.get("author")
    category = data.get("category")
    
    if not title or not content or not author:
        return jsonify({"message": "Title, content, and author are required"}), 400

    author_id = author if ObjectId.is_valid(author) else None
    if not author_id:
        user = UserModel.get_user_by_name(author)
        if not user:
            return jsonify({"message": "Author not found"}), 404
        author_id = str(user["_id"])

    ForumModel.create_post(title, content, author_id, category)
    return jsonify({"message": "Post created successfully"}), 201

@forum_bp.route("/posts", methods=["GET"])
def get_posts():
    if "posts" not in db.list_collection_names():
        return jsonify({"message": "Collection 'posts' không tồn tại!"}), 500

    posts = list(db["posts"].find())
    
    if not posts:
        return jsonify([]), 200

    for post in posts:
        post["_id"] = str(post["_id"])

    return jsonify(posts), 200



# 🟢 Lấy một bài viết cụ thể
@forum_bp.route("/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    if not ObjectId.is_valid(post_id):
        return jsonify({"message": "Invalid post ID"}), 400
    
    post = db["posts"].find_one({"_id": ObjectId(post_id)})
    if post:
        post["_id"] = serialize_objectid(post["_id"])
        return jsonify(post), 200
    return jsonify({"message": "Post not found"}), 404

# 🔴 Xóa bài viết
@forum_bp.route("/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    if not ObjectId.is_valid(post_id):
        return jsonify({"message": "Invalid post ID"}), 400
    
    result = ForumModel.collection.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        return jsonify({"message": "Post not found"}), 404
    
    return jsonify({"message": "Post deleted successfully"}), 200

# ❤️ Thích bài viết
@forum_bp.route("/posts/<post_id>/like", methods=["POST"])
def like_post(post_id):
    if not ObjectId.is_valid(post_id):
        return jsonify({"message": "Invalid post ID"}), 400
    
    post = ForumModel.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404
    
    new_likes = post.get("likes", 0)
    if not isinstance(new_likes, int):
        new_likes = 0
    new_likes += 1
    
    ForumModel.collection.update_one({"_id": ObjectId(post_id)}, {"$set": {"likes": new_likes}})
    return jsonify({"message": "Post liked", "likes": new_likes}), 200

# 🚩 Báo cáo bài viết
@forum_bp.route("/posts/<post_id>/report", methods=["POST"])
def report_post(post_id):
    if not ObjectId.is_valid(post_id):
        return jsonify({"message": "ID bài viết không hợp lệ"}), 400
    
    post = ForumModel.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Bài viết không tồn tại"}), 404
    
    ForumModel.report_post(post_id)
    return jsonify({"message": "Bài viết đã được báo cáo", "isReported": True}), 200

# 📊 Lấy danh sách bài viết đã báo cáo
@forum_bp.route("/posts/reported", methods=["GET"])
def get_reported_posts():
    reported_posts = list(ForumModel.collection.find({"isReported": True}))
    
    for post in reported_posts:
        post["_id"] = str(post["_id"])
    
    return jsonify(reported_posts), 200

# 💬 Thêm bình luận
@forum_bp.route("/posts/<post_id>/comments", methods=["POST"])
def add_comment(post_id):
    if not ObjectId.is_valid(post_id):
        return jsonify({"message": "Invalid post ID"}), 400
    
    data = request.json
    comment_content = data.get("content")
    commenter = data.get("author")
    
    if not comment_content or not commenter:
        return jsonify({"message": "Content and author are required"}), 400
    
    post = ForumModel.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404
    
    commenter_id = commenter if ObjectId.is_valid(commenter) else None
    if not commenter_id:
        user = UserModel.get_user_by_name(commenter)
        if not user:
            return jsonify({"message": "Author not found"}), 404
        commenter_id = str(user["_id"])
    
    comment = {"author": commenter_id, "content": comment_content}
    
    ForumModel.collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}, "$setOnInsert": {"comments": []}}
    )
    
    comment["author"] = serialize_objectid(comment["author"])
    return jsonify({"message": "Comment added", "comment": comment}), 201
