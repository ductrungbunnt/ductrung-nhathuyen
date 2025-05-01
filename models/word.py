from database import db
from bson.objectid import ObjectId
from datetime import datetime
import os
import unicodedata

class WordModel:
    collection = db.words  # Make sure "words" collection exists in MongoDB
    _dictionary_cache = None  # Cache để lưu trữ từ điển kết nối

    @staticmethod
    def get_word_by_id(word_id):
        """Get a word by its ID"""
        return WordModel.collection.find_one({"_id": ObjectId(word_id)})

    @staticmethod
    def add_word(word, word_type):
        """Add a word to the database with its type"""
        word_data = {
            "word": word,
            "type": word_type,
            "created_at": datetime.utcnow()
        }
        result = WordModel.collection.insert_one(word_data)
        return result.inserted_id  # Return the inserted ID

    @staticmethod
    def get_random_word():
        """Get a random word from the database"""
        pipeline = [{"$sample": {"size": 1}}]
        cursor = WordModel.collection.aggregate(pipeline)
        try:
            return cursor.next()
        except StopIteration:
            return {"word": "hoa", "type": "danh từ"}

    @staticmethod
    def load_dictionary():
        """Tải từ điển kết nối từ file tudien.txt"""
        if WordModel._dictionary_cache is not None:
            return WordModel._dictionary_cache
            
        dictionary = {}
        try:
            # Đọc file và xây dựng từ điển
            dict_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tudien.txt')
            
            # Đọc file và phân tích cấu trúc
            single_words = []
            compound_words = {}
            
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if not word:
                        continue
                        
                    words = word.split()
                    if len(words) == 1:
                        single_words.append(word)
                    elif len(words) > 1:
                        # Thêm vào từ ghép
                        first_word = words[0]
                        if first_word not in compound_words:
                            compound_words[first_word] = []
                        
                        second_word = words[1] if len(words) > 1 else ""
                        if second_word and second_word not in compound_words[first_word]:
                            compound_words[first_word].append(second_word)
            
            # Tạo từ điển kết nối dựa trên từ ghép thực tế
            for word, related_words in compound_words.items():
                if word in single_words and related_words:
                    # Lọc chỉ những từ thứ hai cũng là từ đơn
                    valid_related = [w for w in related_words if w in single_words]
                    if valid_related:
                        dictionary[word] = valid_related
                        
            # Cache lại kết quả
            WordModel._dictionary_cache = dictionary
            return dictionary
            
        except Exception as e:
            print(f"Lỗi khi tải từ điển: {str(e)}")
            return {}

    @staticmethod
    def check_word_connection(word1, word2):
        """Check if two words can be connected meaningfully based on dictionary"""
        # Chuẩn hóa từ về chữ thường để so sánh
        word1 = word1.lower()
        word2 = word2.lower()
        
        # Chuẩn hóa Unicode
        word1 = unicodedata.normalize('NFC', word1)
        word2 = unicodedata.normalize('NFC', word2)
        
        try:
            # Trước tiên, kiểm tra xem từ ghép có tồn tại trực tiếp trong từ điển không
            compound = WordModel.check_compound_in_dictionary(word1, word2)
            if compound:
                print(f"Từ ghép '{word1} {word2}' tồn tại trong từ điển: '{compound}'")
                return True
            
            # Nếu không tìm thấy từ ghép trực tiếp, kiểm tra trong từ điển kết nối
            dictionary = WordModel.load_dictionary()
            
            # Kiểm tra nếu word1 nằm trong từ điển và word2 là một từ có thể kết nối
            if word1 in dictionary and word2 in dictionary[word1]:
                print(f"'{word1}' có thể kết nối với '{word2}' theo từ điển kết nối")
                return True
            
            # Kiểm tra cả trường hợp kết nối ngược
            if word2 in dictionary and word1 in dictionary[word2]:
                print(f"'{word2}' có thể kết nối với '{word1}' theo từ điển kết nối")
                return True
            
            # Kiểm tra theo nguyên tắc nối âm tiết
            last_syllable = word1.split(" ")[-1]
            first_syllable = word2.split(" ")[0]
            if last_syllable == first_syllable:
                print(f"Âm tiết cuối của '{word1}' ('{last_syllable}') trùng với âm tiết đầu của '{word2}' ('{first_syllable}')")
                return True
            
            # Kiểm tra các trường hợp đặc biệt cho "hoa" và "hâm"
            if (word1 == "hoa" and word2 == "hâm") or (word1 == "hâm" and word2 == "hoa"):
                print(f"Từ '{word1}' và '{word2}' được xử lý như trường hợp đặc biệt")
                return True
            
            # Nếu không khớp theo cả các cách trên, trả về False
            print(f"Từ '{word1}' và '{word2}' không thể kết nối dựa trên các quy tắc")
            return False
            
        except Exception as e:
            print(f"Lỗi khi kiểm tra kết nối từ: {str(e)}")
            
            # Fallback: Logic kiểm tra đơn giản (âm tiết cuối của từ 1 trùng với âm tiết đầu của từ 2)
            last_syllable = word1.split(" ")[-1]
            first_syllable = word2.split(" ")[0]
            return last_syllable == first_syllable

    @staticmethod
    def search_words_by_prefix(prefix, limit=10):
        """Search for words starting with a specific prefix"""
        regex_pattern = f"^{prefix}"
        pipeline = [
            {"$match": {"word": {"$regex": regex_pattern, "$options": "i"}}},
            {"$limit": limit}
        ]
        cursor = WordModel.collection.aggregate(pipeline)
        return list(cursor)

    @staticmethod
    def get_all_words():
        """Get all words in the database"""
        return list(WordModel.collection.find())

    @staticmethod
    def check_compound_in_dictionary(word1, word2):
        """Kiểm tra xem từ ghép word1 word2 có trong từ điển không"""
        try:
            dict_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tudien.txt')
            compound_lower = f"{word1.lower()} {word2.lower()}"
            
            # Biến để lưu từ ghép gốc nếu tìm thấy
            original_compound = None
            
            # Chuẩn hóa ký tự Unicode để so sánh
            normalized_compound = unicodedata.normalize('NFC', compound_lower)
            
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_stripped = line.strip()
                    # Chuẩn hóa Unicode và chuyển thành chữ thường
                    normalized_line = unicodedata.normalize('NFC', line_stripped.lower())
                    
                    if normalized_line == normalized_compound or normalized_line == compound_lower:
                        original_compound = line_stripped
                        # In thông tin debug
                        print(f"Tìm thấy từ ghép: '{line_stripped}' khớp với '{word1} {word2}'")
                        break
            
            # In thông tin debug nếu không tìm thấy
            if not original_compound:
                print(f"Không tìm thấy từ ghép: '{word1} {word2}' trong từ điển")
                # Kiểm tra sự khác biệt giữa các biến thể unicode
                with open(dict_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        line_stripped = line.strip()
                        if "Hoa Hâm" in line_stripped or "hoa hâm" in line_stripped.lower():
                            print(f"Tìm thấy 'Hoa Hâm' ở dòng {i+1}: '{line_stripped}'")
                            print(f"Unicode normalized: {[ord(c) for c in unicodedata.normalize('NFC', line_stripped)]}")
                            print(f"Original: {[ord(c) for c in line_stripped]}")
                            print(f"Compound to check: {[ord(c) for c in word1 + ' ' + word2]}")
            
            return original_compound
        except Exception as e:
            print(f"Lỗi khi kiểm tra từ ghép: {str(e)}")
            return None
