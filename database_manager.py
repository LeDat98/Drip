import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

class FlashCard:
    def __init__(self, id=None, word="", meaning="", example="", tag="", 
                 stage_id=1, correct=None, created_at=None, last_reviewed_at=None,
                 next_review_time=None, review_count=0, correct_count=0, wrong_count=0,
                 priority_score=0, interval_hours=0.5):
        self.id = id
        self.word = word
        self.meaning = meaning
        self.example = example
        self.tag = tag
        self.stage_id = stage_id
        self.correct = correct
        self.created_at = created_at
        self.last_reviewed_at = last_reviewed_at
        self.next_review_time = next_review_time
        self.review_count = review_count
        self.correct_count = correct_count
        self.wrong_count = wrong_count
        self.priority_score = priority_score
        self.interval_hours = interval_hours

class DatabaseManager:
    def __init__(self, db_path: str = "drip.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database cơ bản"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    meaning TEXT NOT NULL, 
                    example TEXT,
                    tag TEXT,
                    stage_id INTEGER NOT NULL DEFAULT 1,
                    correct BOOLEAN DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT NULL,
                    last_reviewed_at TIMESTAMP DEFAULT NULL,
                    next_review_time TIMESTAMP DEFAULT NULL,
                    review_count INTEGER DEFAULT 0,
                    correct_count INTEGER DEFAULT 0,
                    wrong_count INTEGER DEFAULT 0,
                    priority_score REAL DEFAULT 0,
                    interval_hours REAL DEFAULT 0.5,
                    CHECK (stage_id IN (1, 2, 3, 4))
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stage_review ON flashcards(stage_id, next_review_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON flashcards(priority_score DESC)")
            conn.commit()
    
    def create_flashcard(self, flashcard_data: Dict) -> int:
        """Tạo flashcard mới từ modal CreateNewFlashcard"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Sử dụng local time cho cả created_at và next_review_time
            current_time = datetime.now()
            first_review_time = current_time + timedelta(hours=0.5)
            
            cursor.execute("""
                INSERT INTO flashcards (word, meaning, example, tag, stage_id, 
                                      created_at, next_review_time, priority_score, interval_hours)
                VALUES (?, ?, ?, ?, 1, ?, ?, 100, 0.5)
            """, (
                flashcard_data['word'],
                flashcard_data['meaning'], 
                flashcard_data.get('example', ''),
                flashcard_data.get('tag', ''),
                current_time,
                first_review_time
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_due_flashcards(self, limit: int = 5) -> List[FlashCard]:
        """Lấy danh sách flashcard cần ôn tập theo độ ưu tiên (Thuật toán 1)"""
        # Trước tiên cập nhật priority_score cho tất cả flashcard
        self._update_all_priority_scores()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Sắp xếp theo priority_score DESC (cao trước)
            cursor.execute("""
                SELECT * FROM flashcards 
                WHERE next_review_time <= ? 
                ORDER BY priority_score DESC, stage_id ASC, next_review_time ASC
                LIMIT ?
            """, (datetime.now(), limit))
            
            results = cursor.fetchall()
            return [self._row_to_flashcard(row) for row in results]
    
    def update_flashcard_after_review(self, flashcard_id: int, result: str):
        """Cập nhật flashcard sau khi review (Thuật toán 2 - Interval)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Lấy flashcard hiện tại để check stage
            cursor.execute("SELECT * FROM flashcards WHERE id = ?", (flashcard_id,))
            row = cursor.fetchone()
            if not row:
                return
            
            flashcard = self._row_to_flashcard(row)
            
            # Xử lý TIMEOUT dựa trên stage
            if result == "TIMEOUT":
                # Tất cả stages: TIMEOUT từ pre-review notification không nên thay đổi next_review_time
                # Giữ nguyên thời gian review để flashcard vẫn due cho đợt review tiếp theo
                cursor.execute("""
                    UPDATE flashcards 
                    SET last_reviewed_at = ?, review_count = ?
                    WHERE id = ?
                """, (datetime.now(), flashcard.review_count + 1, flashcard_id))
                conn.commit()
                self._update_priority_score(flashcard_id)
                return
            
            # Xử lý ESCAPE key - tương tự như TIMEOUT
            if result == "ESCAPE":
                # Tất cả stages: ESCAPE từ pre-review notification không nên thay đổi next_review_time
                # Giữ nguyên thời gian review để flashcard vẫn due cho đợt review tiếp theo
                cursor.execute("""
                    UPDATE flashcards 
                    SET last_reviewed_at = ?, review_count = ?
                    WHERE id = ?
                """, (datetime.now(), flashcard.review_count + 1, flashcard_id))
                conn.commit()
                self._update_priority_score(flashcard_id)
                return
            
            # Tiếp tục xử lý logic chính cho tất cả results khác (chỉ "True" và "False")
            
            # Tính interval mới theo thuật toán
            new_interval = self._calculate_next_interval(flashcard, result)
            next_review = datetime.now() + timedelta(hours=new_interval)
            now = datetime.now()
            
            if result == "True":  # Đúng
                new_stage = min(flashcard.stage_id + 1, 4)
                cursor.execute("""
                    UPDATE flashcards 
                    SET stage_id = ?, correct = ?, last_reviewed_at = ?, 
                        next_review_time = ?, review_count = ?, 
                        correct_count = ?, interval_hours = ?
                    WHERE id = ?
                """, (new_stage, True, now, next_review, 
                      flashcard.review_count + 1, flashcard.correct_count + 1, 
                      new_interval, flashcard_id))
                
            elif result == "False":  # Sai
                cursor.execute("""
                    UPDATE flashcards 
                    SET correct = ?, last_reviewed_at = ?, 
                        next_review_time = ?, review_count = ?, 
                        wrong_count = ?, interval_hours = ?
                    WHERE id = ?
                """, (False, now, next_review, flashcard.review_count + 1,
                      flashcard.wrong_count + 1, new_interval, flashcard_id))
            
            conn.commit()
            
            # Cập nhật priority_score sau khi review
            self._update_priority_score(flashcard_id)
    
    def get_random_words_for_options(self, exclude_id: int, count: int = 3) -> List[str]:
        """Lấy từ ngẫu nhiên cho bài test multiple choice (stage 3) - DEPRECATED
        
        Sử dụng get_contextual_words_for_stage3() thay thế
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT word FROM flashcards 
                WHERE id != ? 
                ORDER BY RANDOM() 
                LIMIT ?
            """, (exclude_id, count))
            
            results = cursor.fetchall()
            words = [row[0] for row in results]
            
            # Nếu không đủ từ trong database, thêm từ mặc định
            default_words = ["apple", "book", "cat", "dog", "elephant", "flower", "guitar", "house"]
            while len(words) < count:
                for word in default_words:
                    if word not in words and len(words) < count:
                        words.append(word)
                break
                        
            return words[:count]
    
    def get_contextual_words_for_stage3(self, exclude_id: int, count: int = 3) -> List[str]:
        """Lấy từ (words) contextual cho Stage 3 multiple choice
        
        Logic: Lấy từ 10 ID trước và 10 ID sau (tổng 20 từ) để gợi nhớ các từ đã học cùng thời điểm
        Nếu không đủ thì bổ sung từ danh sách mặc định
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Lấy words từ 10 ID trước và 10 ID sau
            cursor.execute("""
                SELECT word FROM flashcards 
                WHERE id != ? AND (
                    (id >= ? AND id <= ?) OR  -- 10 ID trước
                    (id >= ? AND id <= ?)     -- 10 ID sau
                )
                ORDER BY id
            """, (exclude_id, max(1, exclude_id - 10), exclude_id - 1, 
                  exclude_id + 1, exclude_id + 10))
            
            results = cursor.fetchall()
            words = [row[0] for row in results]
            
            # Nếu không đủ từ, lấy thêm từ database (ngẫu nhiên)
            if len(words) < count:
                cursor.execute("""
                    SELECT word FROM flashcards 
                    WHERE id != ? AND word NOT IN ({})
                    ORDER BY RANDOM() 
                    LIMIT ?
                """.format(','.join(['?'] * len(words))), 
                [exclude_id] + words + [count - len(words)])
                
                additional_results = cursor.fetchall()
                words.extend([row[0] for row in additional_results])
            
            # Nếu vẫn không đủ, thêm words mặc định
            default_words = [
                "apple", "book", "cat", "dog", "elephant", 
                "flower", "guitar", "house", "computer", "phone",
                "chair", "table", "water", "coffee", "music",
                "movie", "garden", "window", "door", "street"
            ]
            
            # Bổ sung words mặc định nếu cần
            for word in default_words:
                if len(words) >= count:
                    break
                if word not in words:
                    words.append(word)
            
            # Trộn ngẫu nhiên và lấy đúng số lượng cần
            random.shuffle(words)
            return words[:count]
    
    def get_contextual_meanings_for_stage2(self, exclude_id: int, count: int = 3) -> List[str]:
        """Lấy nghĩa (meanings) contextual cho Stage 2 multiple choice
        
        Logic: Lấy từ 10 ID trước và 10 ID sau (tổng 20 từ) để gợi nhớ các từ đã học cùng thời điểm
        Nếu không đủ thì bổ sung từ danh sách mặc định
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Lấy meanings từ 10 ID trước và 10 ID sau
            cursor.execute("""
                SELECT meaning FROM flashcards 
                WHERE id != ? AND (
                    (id >= ? AND id <= ?) OR  -- 10 ID trước
                    (id >= ? AND id <= ?)     -- 10 ID sau
                )
                ORDER BY id
            """, (exclude_id, max(1, exclude_id - 10), exclude_id - 1, 
                  exclude_id + 1, exclude_id + 10))
            
            results = cursor.fetchall()
            meanings = [row[0] for row in results]
            
            # Nếu không đủ từ, lấy thêm từ database (ngẫu nhiên)
            if len(meanings) < count:
                cursor.execute("""
                    SELECT meaning FROM flashcards 
                    WHERE id != ? AND meaning NOT IN ({})
                    ORDER BY RANDOM() 
                    LIMIT ?
                """.format(','.join(['?'] * len(meanings))), 
                [exclude_id] + meanings + [count - len(meanings)])
                
                additional_results = cursor.fetchall()
                meanings.extend([row[0] for row in additional_results])
            
            # Nếu vẫn không đủ, thêm meanings mặc định
            default_meanings = [
                "a red fruit that grows on trees",
                "an object with pages for reading", 
                "a small animal that says meow",
                "a loyal pet animal",
                "a large gray animal with a trunk",
                "a colorful plant that blooms",
                "a musical instrument with strings",
                "a building where people live",
                "a yellow fruit that monkeys like",
                "a vehicle with four wheels",
                "a device for communication",
                "a piece of furniture for sitting",
                "a liquid that falls from the sky",
                "a bright object in the sky",
                "a green plant that grows in lawns",
                "a tool for writing",
                "a container for drinking",
                "a place where people work",
                "a time when the sun sets",
                "a feeling of happiness"
            ]
            
            # Bổ sung meanings mặc định nếu cần
            for meaning in default_meanings:
                if len(meanings) >= count:
                    break
                if meaning not in meanings:
                    meanings.append(meaning)
            
            # Trộn ngẫu nhiên và lấy đúng số lượng cần
            random.shuffle(meanings)
            return meanings[:count]
    
    def _calculate_next_interval(self, flashcard: FlashCard, result: str) -> float:
        """Thuật toán 2: Tính interval cho lần ôn tập tiếp theo"""
        base_intervals = {1: 0.5, 2: 2, 3: 24, 4: 168}
        base_interval = base_intervals.get(flashcard.stage_id, 0.5)
        
        if result == "True":
            # Tăng interval khi đúng
            multiplier = 2.0 if flashcard.stage_id <= 2 else 1.5
            return base_interval * multiplier
        elif result == "False":
            # Giảm interval khi sai
            return base_interval * 0.5
        elif result == "TIMEOUT":
            # NOTE: Function này chỉ được gọi cho Stage 1
            # Stage 2-4 TIMEOUT giữ nguyên next_review_time cũ
            return base_interval
        elif result == "ESCAPE":
            # NOTE: Function này chỉ được gọi cho Stage 1  
            # Stage 2-4 ESCAPE giữ nguyên next_review_time cũ
            return base_interval
        else:
            # Fallback cho các result khác
            return base_interval
    
    def _calculate_priority_score(self, flashcard: FlashCard) -> float:
        """Thuật toán 1: Tính điểm ưu tiên"""
        current_time = datetime.now()
        
        # Điểm cơ bản theo stage
        stage_priority = {1: 100, 2: 80, 3: 60, 4: 40}
        base_score = stage_priority[flashcard.stage_id]
        
        # Điểm thưởng cho từ vựng quá hạn
        overdue_bonus = 0
        if flashcard.next_review_time:
            if isinstance(flashcard.next_review_time, str):
                try:
                    next_review = datetime.fromisoformat(flashcard.next_review_time.replace('Z', '+00:00'))
                except ValueError:
                    next_review = datetime.strptime(flashcard.next_review_time, '%Y-%m-%d %H:%M:%S')
            else:
                next_review = flashcard.next_review_time
            
            if next_review <= current_time:
                overdue_hours = (current_time - next_review).total_seconds() / 3600
                overdue_bonus = min(overdue_hours * 5, 50)
        
        # Điểm thưởng cho từ vựng sai gần đây
        wrong_penalty = 30 if flashcard.correct == False else 0
        
        # Điểm thưởng cho từ vựng mới
        creation_bonus = 20 if flashcard.stage_id == 1 else 0
        
        return base_score + overdue_bonus + wrong_penalty + creation_bonus
    
    def _update_priority_score(self, flashcard_id: int):
        """Cập nhật priority_score cho một flashcard"""
        flashcard = self.get_flashcard_by_id(flashcard_id)
        if flashcard:
            new_score = self._calculate_priority_score(flashcard)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE flashcards SET priority_score = ? WHERE id = ?", 
                             (new_score, flashcard_id))
                conn.commit()
    
    def _update_all_priority_scores(self):
        """Cập nhật priority_score cho tất cả flashcard"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM flashcards")
            rows = cursor.fetchall()
            
            for row in rows:
                flashcard = self._row_to_flashcard(row)
                new_score = self._calculate_priority_score(flashcard)
                cursor.execute("UPDATE flashcards SET priority_score = ? WHERE id = ?", 
                             (new_score, flashcard.id))
            conn.commit()
    
    def _row_to_flashcard(self, row) -> FlashCard:
        """Chuyển row database thành FlashCard object"""
        return FlashCard(
            id=row[0],
            word=row[1], 
            meaning=row[2],
            example=row[3],
            tag=row[4],
            stage_id=row[5],
            correct=row[6],
            created_at=row[7],
            last_reviewed_at=row[8],
            next_review_time=row[9],
            review_count=row[10],
            correct_count=row[11],
            wrong_count=row[12],
            priority_score=row[13],
            interval_hours=row[14]
        )
    
    # Thuật toán 1: Tính độ ưu tiên (đơn giản)
    def calculate_priority_flashcards(self, limit: int = 5) -> List[FlashCard]:
        """Thuật toán ưu tiên: stage thấp + thời gian sớm = ưu tiên cao"""
        return self.get_due_flashcards(limit)
    
    # Thuật toán 2: Tính interval test tiếp theo (đơn giản)  
    def calculate_next_test_interval(self) -> int:
        """Tính khoảng cách phiên test tiếp theo (phút)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Đếm số từ due hiện tại
            cursor.execute("""
                SELECT COUNT(*) FROM flashcards 
                WHERE next_review_time <= ?
            """, (datetime.now(),))
            due_count = cursor.fetchone()[0]
            
            if due_count == 0:
                # Không có từ due - tìm từ sắp due sớm nhất
                cursor.execute("""
                    SELECT MIN(next_review_time) FROM flashcards 
                    WHERE next_review_time > ?
                """, (datetime.now(),))
                next_due_time = cursor.fetchone()[0]
                
                if next_due_time:
                    # Tính thời gian đến từ sắp due sớm nhất
                    next_due = datetime.fromisoformat(next_due_time.replace('Z', '+00:00')) if isinstance(next_due_time, str) else next_due_time
                    minutes_until_next = max(5, int((next_due - datetime.now()).total_seconds() / 60))
                    return min(minutes_until_next, 60)  # Tối đa 1 giờ
                else:
                    return 5  # Default 30 phút nếu không có từ nào
            elif due_count <= 5:
                return 5  # 15 phút nếu ít từ due
            else:
                return 3  # 10 phút nếu nhiều từ due
    
    def get_flashcard_by_id(self, flashcard_id: int) -> Optional[FlashCard]:
        """Lấy flashcard theo ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM flashcards WHERE id = ?", (flashcard_id,))
            row = cursor.fetchone()
            return self._row_to_flashcard(row) if row else None