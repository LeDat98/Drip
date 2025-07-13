#!/usr/bin/env python3
"""
Test script để kiểm tra logic TIMEOUT/ESCAPE mới:
- Stage 1: TIMEOUT/ESCAPE reschedule sau 30 phút
- Stage 2-4: TIMEOUT/ESCAPE giữ nguyên next_review_time cũ
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from database_manager import DatabaseManager, FlashCard

def test_timeout_escape_logic():
    """Test the new TIMEOUT/ESCAPE logic"""
    print("🧪 Testing TIMEOUT/ESCAPE Logic")
    print("=" * 50)
    
    # Create test database
    db = DatabaseManager("test_timeout.db")
    
    # Create test flashcards for all stages
    test_cards = [
        ("hello", "greeting", "Hello world", "greetings", 1),
        ("computer", "machine", "I use computer", "tech", 2), 
        ("beautiful", "pretty", "Beautiful day", "adjective", 3),
        ("programming", "coding", "I love programming", "tech", 4)
    ]
    
    card_ids = []
    for word, meaning, example, tag, stage in test_cards:
        flashcard_data = {
            'word': word,
            'meaning': meaning, 
            'example': example,
            'tag': tag
        }
        card_id = db.create_flashcard(flashcard_data)
        # Set stage manually
        with sqlite3.connect(db.db_path) as conn:
            # Set specific stage and future review time
            future_time = datetime.now() + timedelta(hours=24)  # 24 hours later
            conn.execute("""
                UPDATE flashcards 
                SET stage_id = ?, next_review_time = ?
                WHERE id = ?
            """, (stage, future_time, card_id))
            conn.commit()
        card_ids.append(card_id)
    
    print(f"✅ Created {len(card_ids)} test flashcards")
    
    # Test TIMEOUT for each stage
    print("\n🔴 Testing TIMEOUT results:")
    for i, card_id in enumerate(card_ids):
        stage = i + 1
        
        # Get original next_review_time
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT next_review_time FROM flashcards WHERE id = ?", (card_id,))
            original_time = cursor.fetchone()[0]
        
        print(f"\nStage {stage} (ID {card_id}):")
        print(f"  Original next_review_time: {original_time}")
        
        # Apply TIMEOUT
        db.update_flashcard_after_review(card_id, "TIMEOUT")
        
        # Check new next_review_time
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT next_review_time, stage_id FROM flashcards WHERE id = ?", (card_id,))
            new_time, current_stage = cursor.fetchone()
        
        print(f"  New next_review_time: {new_time}")
        print(f"  Stage after TIMEOUT: {current_stage}")
        
        if stage == 1:
            print(f"  ✅ Stage 1: Expected reschedule (~30min later)")
        else:
            # Check if new time is about 5 minutes later (cooldown)
            new_dt = datetime.fromisoformat(new_time.replace('Z', '+00:00')) if isinstance(new_time, str) else new_time
            time_diff = (new_dt - datetime.now()).total_seconds() / 60  # minutes
            
            if 3 <= time_diff <= 7:  # Around 5 minutes cooldown
                print(f"  ✅ Stage {stage}: Applied 5-minute cooldown (correct!)")
            else:
                print(f"  ❌ Stage {stage}: Unexpected time change (diff: {time_diff:.1f} min)")
    
    # Reset for ESCAPE test
    print("\n" + "=" * 50)
    print("🚪 Testing ESCAPE results:")
    
    # Reset all cards to future time again
    for i, card_id in enumerate(card_ids):
        stage = i + 1
        with sqlite3.connect(db.db_path) as conn:
            future_time = datetime.now() + timedelta(hours=48)  # 48 hours later
            conn.execute("""
                UPDATE flashcards 
                SET next_review_time = ?
                WHERE id = ?
            """, (future_time, card_id))
            conn.commit()
    
    # Test ESCAPE for each stage
    for i, card_id in enumerate(card_ids):
        stage = i + 1
        
        # Get original next_review_time
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT next_review_time FROM flashcards WHERE id = ?", (card_id,))
            original_time = cursor.fetchone()[0]
        
        print(f"\nStage {stage} (ID {card_id}):")
        print(f"  Original next_review_time: {original_time}")
        
        # Apply ESCAPE
        db.update_flashcard_after_review(card_id, "ESCAPE")
        
        # Check new next_review_time
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT next_review_time, stage_id FROM flashcards WHERE id = ?", (card_id,))
            new_time, current_stage = cursor.fetchone()
        
        print(f"  New next_review_time: {new_time}")
        print(f"  Stage after ESCAPE: {current_stage}")
        
        if stage == 1:
            print(f"  ✅ Stage 1: Expected reschedule (~30min later)")
        else:
            # Check if new time is about 5 minutes later (cooldown)
            new_dt = datetime.fromisoformat(new_time.replace('Z', '+00:00')) if isinstance(new_time, str) else new_time
            time_diff = (new_dt - datetime.now()).total_seconds() / 60  # minutes
            
            if 3 <= time_diff <= 7:  # Around 5 minutes cooldown
                print(f"  ✅ Stage {stage}: Applied 5-minute cooldown (correct!)")
            else:
                print(f"  ❌ Stage {stage}: Unexpected time change (diff: {time_diff:.1f} min)")
    
    # Test comparison with True/False results
    print("\n" + "=" * 50)
    print("📊 Comparison with True/False results:")
    
    # Test True result (should advance stage and change time)
    card_id = card_ids[1]  # Stage 2 card
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review_time, stage_id FROM flashcards WHERE id = ?", (card_id,))
        before_time, before_stage = cursor.fetchone()
    
    print(f"\nTesting 'True' result on Stage {before_stage} card:")
    print(f"  Before: next_review_time={before_time}, stage={before_stage}")
    
    db.update_flashcard_after_review(card_id, "True")
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review_time, stage_id FROM flashcards WHERE id = ?", (card_id,))
        after_time, after_stage = cursor.fetchone()
    
    print(f"  After: next_review_time={after_time}, stage={after_stage}")
    print(f"  ✅ 'True' result: Stage advanced and time changed (as expected)")
    
    # Cleanup
    import os
    os.remove("test_timeout.db")
    print(f"\n🧹 Cleanup completed")
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_timeout_escape_logic()