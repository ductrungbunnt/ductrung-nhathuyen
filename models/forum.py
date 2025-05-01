from database import db
from bson import ObjectId

class ForumModel:
    collection = db.forum

    @staticmethod
    def create_post(title, content, author, category):
        new_post = {
            "title": title,
            "content": content,
            "author": ObjectId(author),
            "category": category,
            "likes": 0,
            "comments": [],
            "isReported": False
        }
        return ForumModel.collection.insert_one(new_post)

    @staticmethod
    def get_posts():
        return list(ForumModel.collection.find({}))

    @staticmethod
    def get_post_by_id(post_id):
        # Tìm bài viết theo ID
        if not ObjectId.is_valid(post_id):
            post_id = ObjectId(post_id)
        post = ForumModel.collection.find_one({"_id": post_id})
        print(post)
        if post:
            post = ForumModel.serialize_post(post)  # Chuyển đổi toàn bộ post
        return post

    @staticmethod
    def serialize_post(post):
        """
        Chuyển đổi mọi ObjectId trong bài viết thành chuỗi để có thể trả về dạng JSON.
        """
        if isinstance(post, dict):
            return {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in post.items()}
        return post

    @staticmethod
    def report_post(post_id):
        """
        Đánh dấu bài viết là đã bị báo cáo
        """
        if not ObjectId.is_valid(post_id):
            post_id = ObjectId(post_id)
        return ForumModel.collection.update_one(
            {"_id": post_id},
            {"$set": {"isReported": True}}
        )

#main
if __name__ == "__main__":
    # Test các phương thức của ForumModel
    post_id = ForumModel.create_post("Test Title", "Test Content", "author_id", "category_id")
    print(f"Post created with ID: {post_id}")
    
    posts = ForumModel.get_posts()
    print(f"All posts: {posts}")
    
    post = ForumModel.get_post_by_id(post_id)
    print(f"Post by ID: {post}")