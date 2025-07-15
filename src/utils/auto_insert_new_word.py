import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class AutoInsertNewWord:
    def __init__(self, db_path: str = "data/drip.db", json_path: str = "insert_new_words.json"):
        self.db_path = db_path
        self.json_path = json_path
        
    def load_words_from_json(self) -> List[Dict]:
        """Đọc từ vựng từ file JSON"""
        try:
            if not os.path.exists(self.json_path):
                print(f"Warning: JSON file {self.json_path} not found")
                return []
                
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Kiểm tra format của data
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'words' in data:
                return data['words']
            else:
                print(f"Warning: Invalid JSON format in {self.json_path}")
                return []
                
        except Exception as e:
            print(f"Error loading words from JSON: {e}")
            return []
    
    def check_word_exists(self, word: str) -> bool:
        """Kiểm tra xem từ vựng đã tồn tại trong database chưa"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM flashcards WHERE LOWER(word) = LOWER(?)", (word,))
            count = cursor.fetchone()[0]
            return count > 0
    
    def get_today_inserted_count(self, target_time: datetime) -> int:
        """Đếm số từ vựng đã được thêm vào hôm nay tại thời điểm target_time"""
        # Tạo khoảng thời gian từ target_time - 1 tiếng đến target_time + 1 tiếng
        start_time = target_time - timedelta(hours=1)
        end_time = target_time + timedelta(hours=1)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM flashcards 
                WHERE created_at >= ? AND created_at <= ?
            """, (start_time, end_time))
            count = cursor.fetchone()[0]
            return count
    
    def insert_word_to_database(self, word_data: Dict) -> bool:
        """Thêm một từ vựng vào database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Sử dụng thời gian hiện tại cho created_at
                current_time = datetime.now()
                first_review_time = current_time + timedelta(hours=0.5)
                
                cursor.execute("""
                    INSERT INTO flashcards (word, meaning, example, tag, stage_id, 
                                          created_at, next_review_time, priority_score, interval_hours)
                    VALUES (?, ?, ?, ?, 1, ?, ?, 100, 0.5)
                """, (
                    word_data['word'],
                    word_data['meaning'],
                    word_data.get('example', ''),
                    word_data.get('tag', 'auto-inserted'),
                    current_time,
                    first_review_time
                ))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error inserting word '{word_data.get('word', 'unknown')}': {e}")
            return False
    
    def auto_insert_daily_words(self, target_count: int, target_hour: int = 7, target_minute: int = 0) -> Dict:
        """
        Tự động thêm từ vựng hàng ngày
        
        Args:
            target_count: Số lượng từ vựng cần thêm hàng ngày
            target_hour: Giờ thêm từ vựng (24h format)
            target_minute: Phút thêm từ vựng
            
        Returns:
            Dict với thông tin kết quả
        """
        result = {
            'success': False,
            'message': '',
            'inserted_count': 0,
            'skipped_count': 0,
            'already_exists_count': 0,
            'target_count': target_count
        }
        
        try:
            # Tạo thời điểm target cho hôm nay
            today = datetime.now().date()
            target_datetime = datetime.combine(today, datetime.min.time().replace(hour=target_hour, minute=target_minute))
            
            # Kiểm tra xem đã đến thời gian insert chưa
            current_time = datetime.now()
            if current_time < target_datetime:
                result['message'] = f"Chưa đến thời gian insert ({target_hour:02d}:{target_minute:02d})"
                return result
            
            # Kiểm tra xem hôm nay đã insert đủ số lượng chưa
            today_count = self.get_today_inserted_count(target_datetime)
            if today_count >= target_count:
                result['message'] = f"Hôm nay đã insert đủ {target_count} từ vựng"
                result['success'] = True
                return result
            
            # Tính số từ còn cần insert
            remaining_count = target_count - today_count
            
            # Đọc danh sách từ vựng từ JSON
            words_data = self.load_words_from_json()
            if not words_data:
                result['message'] = "Không thể đọc file JSON hoặc file trống"
                return result
            
            # Lọc các từ chưa tồn tại trong database
            new_words = []
            for word_data in words_data:
                if len(new_words) >= remaining_count:
                    break
                    
                if not isinstance(word_data, dict) or 'word' not in word_data or 'meaning' not in word_data:
                    result['skipped_count'] += 1
                    continue
                    
                if self.check_word_exists(word_data['word']):
                    result['already_exists_count'] += 1
                    continue
                    
                new_words.append(word_data)
            
            # Insert các từ mới vào database
            successful_inserts = 0
            for word_data in new_words:
                if self.insert_word_to_database(word_data):
                    successful_inserts += 1
                else:
                    result['skipped_count'] += 1
            
            result['inserted_count'] = successful_inserts
            result['success'] = True
            
            if successful_inserts > 0:
                result['message'] = f"Đã thêm {successful_inserts} từ vựng mới vào database"
            else:
                result['message'] = "Không có từ vựng mới nào được thêm"
                
        except Exception as e:
            result['message'] = f"Lỗi trong quá trình auto-insert: {e}"
            
        return result
    
    def get_auto_insert_status(self, target_count: int, target_hour: int = 7, target_minute: int = 0) -> Dict:
        """
        Lấy trạng thái auto-insert cho hôm nay
        
        Returns:
            Dict với thông tin trạng thái
        """
        today = datetime.now().date()
        target_datetime = datetime.combine(today, datetime.min.time().replace(hour=target_hour, minute=target_minute))
        
        today_count = self.get_today_inserted_count(target_datetime)
        
        return {
            'target_count': target_count,
            'today_count': today_count,
            'remaining_count': max(0, target_count - today_count),
            'target_time': target_datetime,
            'is_completed': today_count >= target_count,
            'is_time_reached': datetime.now() >= target_datetime
        }