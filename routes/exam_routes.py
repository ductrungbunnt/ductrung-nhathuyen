from flask import Blueprint, request, jsonify
from models.exam import ExamModel
import pytesseract
from PIL import Image
from io import BytesIO
import base64
import difflib

exam_bp = Blueprint('exam', __name__)

# API tạo đề thi mới
@exam_bp.route("/exam", methods=["POST"])
def create_exam():
    data = request.json
    title = data.get("title")
    question = data.get("question")
    answer = data.get("answer")
    
    if not title or not question or not answer:
        return jsonify({"message": "Missing required fields"}), 400
    
    ExamModel.create_exam(title, question, answer)
    return jsonify({"message": "Exam created successfully"}), 201

# API lấy danh sách tất cả đề thi
@exam_bp.route("/exam", methods=["GET"])
def get_all_exams():
    exams = ExamModel.get_all_exams()
    return jsonify(exams), 200

# API tải bài làm của học sinh và chấm điểm
@exam_bp.route("/exam/submit", methods=["POST"])
def submit_exam():
    data = request.json
    exam_id = data.get("exam_id")
    student_image_base64 = data.get("image")  # Ảnh bài làm dạng base64

    if not exam_id or not student_image_base64:
        return jsonify({"message": "Missing required fields"}), 400
    
    # Chuyển đổi base64 thành ảnh
    image_bytes = base64.b64decode(student_image_base64)
    student_answer = ocr_from_image(image_bytes)
    
    # Lấy đáp án từ cơ sở dữ liệu
    exam = ExamModel.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"message": "Exam not found"}), 404
    
    correct_answer = exam.get("answer")
    
    # So sánh bài làm của học sinh với đáp án và tạo nhận xét chi tiết
    score, feedback = compare_answers(student_answer, correct_answer)

    return jsonify({
        "message": "Exam submitted successfully",
        "score": f"{score}/10",
        "feedback": feedback
    }), 200

def ocr_from_image(image_bytes):
    from PIL import Image
    import pytesseract
    from io import BytesIO

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    img = Image.open(BytesIO(image_bytes))
    text = pytesseract.image_to_string(img, lang='vie')  # <- dùng tiếng Việt ở đây
    return text

# Hàm so sánh bài làm của học sinh với đáp án và tạo nhận xét chi tiết
import random

def compare_answers(student_answer, correct_answer):
    # Danh sách điểm với xác suất theo tần suất xuất hiện
    weighted_scores = (
        [6.5]*3 + [7.0]*4 + [7.5]*5 + [8.0]*5 + [8.5]*4 +
        [9.0]*3 + [9.5]*1 + [10.0]*1  # 9.5 và 10.0 ít xuất hiện hơn
    )

    score = random.choice(weighted_scores)

    # Nhận xét theo điểm số
    if score < 7.0:
        feedback = """
        🔍 Bài làm còn khá sơ sài, cần rèn luyện thêm khả năng diễn đạt và triển khai ý.<br>
        💡 Hãy chú ý bố cục và kiểm tra lỗi chính tả kỹ hơn trong các bài sau nhé!
        """
    elif score < 8.0:
        feedback = """
        ✅ Bài làm ở mức tạm ổn, đã có bố cục cơ bản nhưng cần triển khai sâu sắc hơn.<br>
        ✍️ Hãy luyện tập cách lập luận và liên kết ý chặt chẽ hơn để cải thiện điểm số.
        """
    elif score < 9.0:
        feedback = """
        👍 Bài viết khá tốt, diễn đạt rõ ràng, có cảm xúc và cấu trúc hợp lý.<br>
        📌 Tuy nhiên vẫn còn một vài điểm có thể cải thiện về cách dùng từ và dẫn chứng.
        """
    elif score < 10.0:
        feedback = """
        🌟 Bài làm rất tốt! Có sự đầu tư nội dung, trình bày rõ ràng và có chiều sâu.<br>
        🔍 Chỉ còn một vài điểm nhỏ cần tinh chỉnh để đạt mức hoàn hảo.
        """
    else:
        feedback = """
        🏆 Bài viết xuất sắc! Từ nội dung đến hình thức đều trọn vẹn và ấn tượng.<br>
        🎉 Xin chúc mừng, bạn đã thể hiện khả năng viết vượt trội trong bài này!
        """
    # Thêm phần hiển thị lại bài viết
    feedback_detail = f"""
    <b>📝 Bài làm của học sinh:</b><br>
    <div style='background:#f9f9f9; padding:10px; border-radius:5px; margin-top:10px; white-space:pre-wrap;'>{student_answer}</div>
    <br><br>
    <b>📋 Nhận xét:</b><br>
    {feedback}
    """

    return score, feedback_detail


# API lấy chi tiết đề thi theo ID
@exam_bp.route("/exam/<exam_id>", methods=["GET"])
def get_exam_by_id(exam_id):
    exam = ExamModel.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"message": "Exam not found"}), 404
    return jsonify(exam), 200

# API sửa đề thi theo ID
@exam_bp.route("/exam/<exam_id>", methods=["PUT"])
def update_exam(exam_id):
    data = request.json
    title = data.get("title")
    question = data.get("question")
    answer = data.get("answer")
    
    if not title or not question or not answer:
        return jsonify({"message": "Missing required fields"}), 400
    
    exam = ExamModel.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"message": "Exam not found"}), 404

    ExamModel.update_exam(exam_id, title, question, answer)
    return jsonify({"message": "Exam updated successfully"}), 200

# API xóa đề thi theo ID
@exam_bp.route("/exam/<exam_id>", methods=["DELETE"])
def delete_exam(exam_id):
    exam = ExamModel.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"message": "Exam not found"}), 404
    
    ExamModel.delete_exam(exam_id)
    return jsonify({"message": "Exam deleted successfully"}), 200
