from database import db
from datetime import datetime
from bson import ObjectId

class MinigameModel:
    collection = db.minigame  

    @staticmethod
    def get_config():
        """Get minigame configuration or create default if not exists"""
        config = MinigameModel.collection.find_one({"type": "config"})
        if config is None:
            config = {
                "type": "config",
                "open_days": [0, 1, 2, 3, 4, 5, 6],  # All days by default
                "time_limit": 60,  # 60 seconds
                "score_multiplier": 10,  # 10 points per correct word
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            MinigameModel.collection.insert_one(config)
        return config

    @staticmethod
    def update_config(open_days=None, time_limit=None, score_multiplier=None):
        """Update minigame configuration"""
        update_data = {"updated_at": datetime.utcnow()}
        
        if open_days is not None:
            update_data["open_days"] = open_days
        
        if time_limit is not None:
            update_data["time_limit"] = time_limit
            
        if score_multiplier is not None:
            update_data["score_multiplier"] = score_multiplier
            
        result = MinigameModel.collection.update_one(
            {"type": "config"},
            {"$set": update_data},
            upsert=True
        )
        return result.modified_count

    @staticmethod
    def save_game_result(user_id, score, words_count):
        """Save a game result"""
        result_data = {
            "user_id": user_id,
            "score": score,
            "words_count": words_count,
            "created_at": datetime.utcnow()
        }
        result = MinigameModel.collection.insert_one(result_data)
        return result.inserted_id

    @staticmethod
    def get_leaderboard(limit=10):
        """Get leaderboard of top scores"""
        pipeline = [
            {"$match": {"score": {"$exists": True}}},
            {"$sort": {"score": -1}},
            {"$limit": limit}
        ]
        return list(MinigameModel.collection.aggregate(pipeline))

    @staticmethod
    def save_score(username, game_type, score):
        """
        Lưu điểm số của người chơi
        :param username: Tên người chơi
        :param game_type: Loại game (ví dụ: 'word_search', 'quiz', etc.)
        :param score: Điểm số
        """
        score_data = {
            "username": username,
            "game_type": game_type,
            "score": score,
            "created_at": datetime.utcnow()
        }
        return MinigameModel.collection.insert_one(score_data)

    @staticmethod
    def get_top_scores(game_type, limit=20):
        """
        Lấy danh sách điểm cao nhất cho một loại game
        :param game_type: Loại game
        :param limit: Số lượng kết quả trả về
        :return: Danh sách điểm số
        """
        scores = list(MinigameModel.collection.find(
            {"game_type": game_type}
        ).sort("score", -1).limit(limit))
        
        # Chuyển đổi ObjectId thành string
        for score in scores:
            score["_id"] = str(score["_id"])
            score["created_at"] = score["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            
        return scores

    @staticmethod
    def get_user_best_score(username, game_type):
        """
        Lấy điểm cao nhất của một người chơi cho một loại game
        :param username: Tên người chơi
        :param game_type: Loại game
        :return: Điểm số cao nhất
        """
        score = MinigameModel.collection.find_one(
            {"username": username, "game_type": game_type},
            sort=[("score", -1)]
        )
        
        if score:
            score["_id"] = str(score["_id"])
            score["created_at"] = score["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            
        return score

    @staticmethod
    def get_user_rank(username, game_type):
        """
        Lấy thứ hạng của người chơi trong một loại game
        :param username: Tên người chơi
        :param game_type: Loại game
        :return: Thứ hạng
        """
        rank = MinigameModel.collection.count_documents({
            "game_type": game_type,
            "score": {"$gt": MinigameModel.get_user_best_score(username, game_type)["score"]}
        }) + 1
        return rank


