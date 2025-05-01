from database import db
import datetime
from bson import ObjectId

class ExamModel:
    # Collection trong MongoDB
    collection = db.exams

    @staticmethod
    def create_exam(title, question, answer):
        # Tạo một đề thi mới
        new_exam = {
            "title": title,
            "question": question,
            "answer": answer,
            "created_at": datetime.datetime.now()
        }
        # Insert vào MongoDB
        return ExamModel.collection.insert_one(new_exam)

    @staticmethod
    def get_exam_by_id(exam_id):
        # Lấy đề thi theo id
        exam = ExamModel.collection.find_one({"_id": ObjectId(exam_id)})
        if exam:
            exam["_id"] = str(exam["_id"])  # Convert ObjectId thành chuỗi
            return exam
        return None

    @staticmethod
    def get_all_exams():
        # Lấy tất cả các đề thi
        exams = list(ExamModel.collection.find({}))
        # Convert ObjectId thành chuỗi
        for exam in exams:
            exam["_id"] = str(exam["_id"])
        return exams
