from database import db
from bson import ObjectId

class LibraryModel:
    collection = db.library  # Sử dụng collection "library"

    @staticmethod
    def add_document(title, content, category, grade, author):
        # Thêm tài liệu mới vào collection
        new_doc = {
            "title": title,
            "content": content,
            "category": category,
            "grade": grade,
            "author": author
        }
        return LibraryModel.collection.insert_one(new_doc)
    @staticmethod
    def get_document_by_id(doc_id):
        try:
            return db.library.find_one({"_id": ObjectId(doc_id)})
        except Exception as e:
            print(f"Lỗi khi tìm tài liệu theo ID: {e}")
            return None

    @staticmethod
    def get_documents():
        # Lấy tất cả tài liệu trong collection
        return list(LibraryModel.collection.find({}))

    @staticmethod
    def delete_document(doc_id):
        # Xóa tài liệu theo _id
        result = LibraryModel.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0  # Trả về True nếu xóa thành công

    @staticmethod
    def update_document(doc_id, updated_data):
        # Cập nhật tài liệu theo _id
        result = LibraryModel.collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": updated_data}  # Cập nhật các trường với dữ liệu mới
        )
        if result.modified_count > 0:
            return LibraryModel.collection.find_one({"_id": ObjectId(doc_id)})  # Trả về tài liệu đã được cập nhật
        return None  # Trả về None nếu không tìm thấy tài liệu hoặc không có thay đổi

    @staticmethod
    def search_documents(query, category=None):
        # Tìm kiếm tài liệu theo tên (title) và loại (category)
        search_query = {}
        
        if query:
            search_query["title"] = {"$regex": query, "$options": "i"}  # Tìm kiếm không phân biệt chữ hoa/thường
        if category:
            search_query["category"] = {"$regex": category, "$options": "i"}  # Tìm kiếm theo category
        
        return list(LibraryModel.collection.find(search_query))  # Trả về danh sách tài liệu tìm được
