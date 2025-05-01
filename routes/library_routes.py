from flask import Blueprint, request, jsonify
from models.library import LibraryModel
from bson import ObjectId

from flask import render_template
from models.library import LibraryModel

library_bp = Blueprint('library', __name__)
@library_bp.route("/library/<doc_id>")
def view_document(doc_id):
    doc = LibraryModel.get_document_by_id(doc_id)
    if not doc:
        return "Không tìm thấy tài liệu", 404
    return render_template("library_detail.html", doc=doc)



# Hàm chuyển ObjectId thành chuỗi
def objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

@library_bp.route("/library", methods=["POST"])
def add_document():
    data = request.json
    LibraryModel.add_document(data["title"], data["content"], data["category"], data["grade"], data["author"])
    return jsonify({"message": "Document added successfully"}), 201

@library_bp.route("/library", methods=["GET"])
def get_documents():
    docs = LibraryModel.get_documents()
    # Sử dụng hàm objectid_to_str để chuyển đổi ObjectId thành chuỗi
    docs = [{key: objectid_to_str(value) for key, value in doc.items()} for doc in docs]
    return jsonify(docs), 200

@library_bp.route("/library/<string:id>", methods=["DELETE"])
def delete_document(id):
    result = LibraryModel.delete_document(id)
    if result:
        return jsonify({"message": "Document xóa thành công"}), 200
    else:
        return jsonify({"message": "Không tồn tại document"}), 404

@library_bp.route("/library/<string:id>", methods=["PUT"])
def update_document(id):
    data = request.json
    updated_document = LibraryModel.update_document(id, data)
    if updated_document:
        # Convert ObjectId fields to strings before returning
        updated_document = {key: objectid_to_str(value) for key, value in updated_document.items()}
        return jsonify(updated_document), 200
    else:
        return jsonify({"message": "Document not found"}), 404


@library_bp.route("/library/search", methods=["GET"])
def search_documents():
    query = request.args.get('query')  # Lấy từ query string: ?query=search_term
    category = request.args.get('category')  # Lấy từ query string: ?category=category_name
    
    # Tìm kiếm theo tên và loại
    docs = LibraryModel.search_documents(query, category)
    
    if docs:
        # Chuyển đổi ObjectId trước khi trả về
        docs = [{key: objectid_to_str(value) for key, value in doc.items()} for doc in docs]
        return jsonify(docs), 200
    else:
        return jsonify({"message": "No documents found"}), 404
