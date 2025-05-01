from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from database import db
from models.forum import ForumModel
from models.comment import CommentModel
from models.users import UserModel

comment_bp = Blueprint('comment', __name__)

@comment_bp.route("/forum/comments", methods=["POST"])
def create_comment():
    data = request.json
    print(data)

    post_id = data.get("post_id")
    content = data.get("content")
    author = data.get("author")

    # Kiểm tra nếu thiếu dữ liệu
    if not post_id or not content or not author:
        return jsonify({"message": "Missing required fields"}), 400

    # Kiểm tra nếu bài viết có tồn tại
    post = ForumModel.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    # Kiểm tra nếu người dùng có tồn tại
    user = UserModel.get_user_by_name(author)
    if not user:
        return jsonify({"message": "Author not found"}), 404

    # Debug thông tin bài viết và user
   

    # Tạo bình luận
    try:
        CommentModel.create_comment(post_id, content, author)
        return jsonify({"message": "Comment created successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

@comment_bp.route("/forum/comments/<comment_id>", methods=["GET"])
def get_comments(comment_id):
    # Lấy danh sách bình luận của bài viết
    comment = CommentModel.get_comment_by_id(comment_id)

    # Chuyển ObjectId thành chuỗi để có thể trả về JSON
    if not comment:
        return jsonify({"message": "No comments found"}), 404
    # Chuyển đổi ObjectId thành chuỗi
    # fix TypeError: Object of type ObjectId is not JSON serializable
    comment = {
            "content": comment["content"],
            "author": comment["author"],
            "post_id": str(comment["post_id"]),
            "created_at": comment["created_at"],
            "_id": str(comment["_id"]),
        }
    
    return jsonify({'success': 1, 'comment': comment}), 200

@comment_bp.route("/forum/comments/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    # Xoá bình luận
    result = CommentModel.delete_comment(comment_id)

    if result.deleted_count == 0:
        return jsonify({"message": "Comment not found"}), 404

    return jsonify({"message": "Comment deleted successfully"}), 200

@comment_bp.route("/comments/recent", methods=["GET"])
@jwt_required()
def get_recent_comments():
    # Lấy user ID từ token
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})

    if not user or user.get("level") != "admin":
        return jsonify({"message": "Không có quyền truy cập"}), 403
    # Lấy danh sách bình luận mới nhất
    try:
        recent_comments = CommentModel.get_recent_comments(limit=10)
        # Chuyển ObjectId thành chuỗi để có thể trả về JSON
        print(recent_comments)
        #  recent_comments = [{'_id': ObjectId('67f26ec55bcef40d30b62eb3'), 'post_id': ObjectId('67f2454c5c605d83c2edb7b8'), 'content': '1235545', 'author': 'Người dùng', 'created_at': datetime.datetime(2025, 4, 6, 12, 8, 37, 2000)}]
        
        comments = [
            {
                "content": comment["content"],
                "author": comment["author"],
                "post_title": db.posts.find_one({'_id': comment["post_id"]})["content"],
                "post_id": str(comment["post_id"]),
                "created_at": comment["created_at"],
                "_id": str(comment["_id"]),
            }
            for comment in recent_comments
        ]
        return jsonify({"comments": comments}), 200
    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500