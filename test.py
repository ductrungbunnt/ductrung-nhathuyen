from docx import Document
from fpdf import FPDF
import os

# from database import db

# # Truy cập collection exams (giống ExamModel đang dùng)
# collection = db.exams

# # Lấy tất cả đề thi
# exams = collection.find()

# # In ra tiêu đề và đáp án mẫu
# for exam in exams:
#     print("📝 Tiêu đề:", exam.get("title", "Không có tiêu đề"))
#     print("📌 Đáp án mẫu (answer):", exam.get("answer", "Không có đáp án"))
#     print("-" * 60)

# def convert_docx_to_pdf(docx_path, pdf_path=None):
#     """
#     Convert a DOCX file to PDF format.
    
#     Parameters:
#         docx_path (str): Path to the input DOCX file
#         pdf_path (str, optional): Path where the PDF will be saved. 
#                                   If not provided, it will use the same name as 
#                                   the docx file but with .pdf extension.
    
#     Returns:
#         str: Path to the output PDF file
#     """
#     from docx2pdf import convert
    
#     if pdf_path is None:
#         # If no output path is specified, use the same filename but with .pdf extension
#         pdf_path = docx_path.rsplit('.', 1)[0] + '.pdf'
    
#     # Convert the file
#     convert(docx_path, pdf_path)
    
#     return pdf_path
# # Test the function with a file in the uploads directory
# uploads_dir = "uploads"
# docx_file = os.path.join(uploads_dir, "So_yeu_ly_lich1.docx")
# pdf_file = os.path.join(uploads_dir, "example.pdf")

# if os.path.exists(docx_file):
#     convert_docx_to_pdf(docx_file, pdf_file)
#     print(f"Converted {docx_file} to {pdf_file}")
# else:
#     print(f"{docx_file} does not exist.")


import bcrypt

def hash_password(password):
    # Hàm mã hóa mật khẩu
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password, hashed_password):
    # Hàm kiểm tra mật khẩu
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# When creating a user account
user_password = "my_secure_password"
hashed_pw = hash_password(user_password)
# Store hashed_pw in your database

# Later, when verifying login
entered_password = "my_secure_password"  # This would come from a login form
stored_hash = hashed_pw  # This would come from your database

if verify_password(entered_password, stored_hash):
    print("Password is correct!")
else:
    print("Password is incorrect!")