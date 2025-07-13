#!/usr/bin/env python3
"""
Test logic scheduling thông minh:
- Không kiểm tra due cards liên tục
- calculate_next_test_interval() tính toán chính xác
- Cooldown thông minh dựa trên interval
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from database_manager import DatabaseManager, FlashCard

def test_smart_scheduling():
    """Test the smart scheduling logic"""
    print("🧠 Testing Smart Scheduling Logic")
    print("=" * 50)
    
    # Create test database
    db = DatabaseManager("test_scheduling.db")
    
    print("📊 Test 1: calculate_next_test_interval() với database trống")
    interval_empty = db.calculate_next_test_interval()
    print(f"  Interval với database trống: {interval_empty} phút")
    print(f"  Expected: 30 phút (default)")
    print(f"  Result: {'✅' if interval_empty == 30 else '❌'}")
    
    # Create test flashcards với different due times
    print(f"\n📝 Tạo test flashcards...")
    
    # Card 1: Due now
    flashcard_data1 = {'word': 'now', 'meaning': 'hiện tại', 'example': 'now example', 'tag': 'time'}
    card1_id = db.create_flashcard(flashcard_data1)
    
    # Card 2: Due in 20 minutes  
    flashcard_data2 = {'word': 'later', 'meaning': 'muộn hơn', 'example': 'later example', 'tag': 'time'}
    card2_id = db.create_flashcard(flashcard_data2)
    
    # Card 3: Due in 45 minutes
    flashcard_data3 = {'word': 'future', 'meaning': 'tương lai', 'example': 'future example', 'tag': 'time'}
    card3_id = db.create_flashcard(flashcard_data3)
    
    # Set different due times
    with sqlite3.connect(db.db_path) as conn:
        now = datetime.now()
        future_20min = now + timedelta(minutes=20)
        future_45min = now + timedelta(minutes=45)
        
        # Card 1: due now (Stage 2)
        conn.execute("""
            UPDATE flashcards 
            SET stage_id = 2, next_review_time = ?
            WHERE id = ?
        """, (now, card1_id))
        
        # Card 2: due in 20 minutes (Stage 3)
        conn.execute("""
            UPDATE flashcards 
            SET stage_id = 3, next_review_time = ?
            WHERE id = ?
        """, (future_20min, card2_id))
        
        # Card 3: due in 45 minutes (Stage 4)
        conn.execute("""
            UPDATE flashcards 
            SET stage_id = 4, next_review_time = ?
            WHERE id = ?
        """, (future_45min, card3_id))
        
        conn.commit()
    
    print(f"✅ Created 3 test cards:")
    print(f"  Card {card1_id}: Due now (Stage 2)")
    print(f"  Card {card2_id}: Due in 20 min (Stage 3)")
    print(f"  Card {card3_id}: Due in 45 min (Stage 4)")
    
    print(f"\n📊 Test 2: calculate_next_test_interval() với due cards")
    interval_with_due = db.calculate_next_test_interval()
    print(f"  Interval với 1 due card: {interval_with_due} phút")
    print(f"  Expected: 15 phút (1 <= due_count <= 5)")
    print(f"  Result: {'✅' if interval_with_due == 15 else '❌'}")
    
    print(f"\n⏰ Test 3: TIMEOUT card với smart cooldown")
    print(f"  Applying TIMEOUT to card {card1_id}...")
    
    # Apply TIMEOUT
    db.update_flashcard_after_review(card1_id, "TIMEOUT")
    
    # Check new due time
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review_time FROM flashcards WHERE id = ?", (card1_id,))
        new_due_time = cursor.fetchone()[0]
    
    new_due_dt = datetime.fromisoformat(new_due_time.replace('Z', '+00:00')) if isinstance(new_due_time, str) else new_due_time
    cooldown_minutes = (new_due_dt - datetime.now()).total_seconds() / 60
    
    print(f"  New due time: {new_due_time}")
    print(f"  Cooldown applied: {cooldown_minutes:.1f} phút")
    print(f"  Expected: >= 10 phút (smart cooldown)")
    print(f"  Result: {'✅' if cooldown_minutes >= 10 else '❌'}")
    
    print(f"\n📊 Test 4: calculate_next_test_interval() sau TIMEOUT")
    interval_after_timeout = db.calculate_next_test_interval()
    print(f"  Interval sau TIMEOUT: {interval_after_timeout} phút")
    print(f"  Expected: 20 phút (thời gian đến card sắp due)")
    print(f"  Result: {'✅' if 15 <= interval_after_timeout <= 25 else '❌'}")
    
    print(f"\n📊 Test 5: calculate_next_test_interval() khi không có due cards")
    
    # Move all cards to future
    with sqlite3.connect(db.db_path) as conn:
        future_time = datetime.now() + timedelta(minutes=35)
        conn.execute("""
            UPDATE flashcards 
            SET next_review_time = ?
        """, (future_time,))
        conn.commit()
    
    interval_no_due = db.calculate_next_test_interval()
    print(f"  Interval khi không có due cards: {interval_no_due} phút")
    print(f"  Expected: ~35 phút (thời gian đến card sắp due)")
    print(f"  Result: {'✅' if 30 <= interval_no_due <= 40 else '❌'}")
    
    print(f"\n🚪 Test 6: ESCAPE logic")
    
    # Make a card due now for ESCAPE test
    with sqlite3.connect(db.db_path) as conn:
        now = datetime.now()
        conn.execute("""
            UPDATE flashcards 
            SET next_review_time = ?
            WHERE id = ?
        """, (now, card2_id))
        conn.commit()
    
    # Apply ESCAPE
    db.update_flashcard_after_review(card2_id, "ESCAPE")
    
    # Check result
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review_time FROM flashcards WHERE id = ?", (card2_id,))
        escape_due_time = cursor.fetchone()[0]
    
    escape_due_dt = datetime.fromisoformat(escape_due_time.replace('Z', '+00:00')) if isinstance(escape_due_time, str) else escape_due_time
    escape_cooldown = (escape_due_dt - datetime.now()).total_seconds() / 60
    
    print(f"  ESCAPE cooldown: {escape_cooldown:.1f} phút")
    print(f"  Result: {'✅' if escape_cooldown >= 10 else '❌'}")
    
    # Final check: no immediate due cards
    due_cards_final = db.get_due_flashcards(limit=10)
    print(f"\n📋 Final check:")
    print(f"  Due cards count: {len(due_cards_final)}")
    print(f"  Expected: 0 (all cards have cooldown)")
    print(f"  Result: {'✅' if len(due_cards_final) == 0 else '❌'}")
    
    # Cleanup
    import os
    os.remove("test_scheduling.db")
    print(f"\n🧹 Cleanup completed")
    print("\n🎉 Smart scheduling test completed!")

if __name__ == "__main__":
    test_smart_scheduling()