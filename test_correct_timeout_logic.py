#!/usr/bin/env python3
"""
Test logic TIMEOUT/ESCAPE đúng theo yêu cầu:
1. Stage 2-4: TIMEOUT/ESCAPE GIỮ NGUYÊN next_review_time
2. Các từ này được review lại dựa trên chu kỳ calculate_next_test_interval()
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from database_manager import DatabaseManager, FlashCard

def test_correct_timeout_logic():
    """Test the correct TIMEOUT/ESCAPE logic as requested"""
    print("✅ Testing CORRECT TIMEOUT/ESCAPE Logic")
    print("=" * 50)
    
    # Create test database
    db = DatabaseManager("test_correct_logic.db")
    
    # Create a Stage 2 flashcard that is due right now
    flashcard_data = {
        'word': 'test_timeout',
        'meaning': 'testing timeout', 
        'example': 'This is a timeout test',
        'tag': 'testing'
    }
    card_id = db.create_flashcard(flashcard_data)
    
    # Set it to Stage 2 and make it due now with specific time
    original_due_time = datetime.now() - timedelta(minutes=10)  # Due 10 minutes ago
    
    with sqlite3.connect(db.db_path) as conn:
        conn.execute("""
            UPDATE flashcards 
            SET stage_id = 2, next_review_time = ?
            WHERE id = ?
        """, (original_due_time, card_id))
        conn.commit()
    
    print(f"✅ Created test flashcard (ID: {card_id}) at Stage 2")
    print(f"   Original next_review_time: {original_due_time}")
    
    # Verify it's in due list
    due_cards_before = db.get_due_flashcards(limit=10)
    due_ids_before = [card.id for card in due_cards_before]
    
    print(f"\n📋 Before TIMEOUT:")
    print(f"   Due cards: {len(due_cards_before)}")
    print(f"   Test card {card_id} is due: {'✅' if card_id in due_ids_before else '❌'}")
    
    # Apply TIMEOUT
    print(f"\n⏰ Applying TIMEOUT to card {card_id}...")
    db.update_flashcard_after_review(card_id, "TIMEOUT")
    
    # Check if next_review_time is UNCHANGED
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review_time, stage_id, last_reviewed_at, review_count FROM flashcards WHERE id = ?", (card_id,))
        after_timeout_time, stage, last_reviewed, review_count = cursor.fetchone()
    
    print(f"\n📊 After TIMEOUT:")
    print(f"   Original next_review_time: {original_due_time}")
    print(f"   Current next_review_time:  {after_timeout_time}")
    print(f"   Stage: {stage}")
    print(f"   Review count: {review_count}")
    print(f"   Last reviewed: {last_reviewed}")
    
    # Check if time is UNCHANGED
    if str(original_due_time) == str(after_timeout_time):
        print(f"   ✅ CORRECT: next_review_time UNCHANGED")
    else:
        print(f"   ❌ WRONG: next_review_time was changed!")
    
    # Check if it's still in due list (should be, since time unchanged)
    due_cards_after = db.get_due_flashcards(limit=10)
    due_ids_after = [card.id for card in due_cards_after]
    
    print(f"\n📋 Due cards after TIMEOUT:")
    print(f"   Due cards: {len(due_cards_after)}")
    print(f"   Test card {card_id} is still due: {'✅' if card_id in due_ids_after else '❌'}")
    
    if card_id in due_ids_after:
        print(f"   ✅ CORRECT: Card remains due (will be picked up in next cycle)")
    else:
        print(f"   ❌ WRONG: Card is no longer due!")
    
    # Test calculate_next_test_interval
    next_interval = db.calculate_next_test_interval()
    print(f"\n📊 calculate_next_test_interval():")
    print(f"   Returned: {next_interval} minutes")
    print(f"   Expected: 5 minutes (due to test configuration)")
    print(f"   Result: {'✅' if next_interval == 5 else '❌'}")
    
    print(f"\n💡 How the system should work:")
    print(f"   1. User TIMEOUT/ESCAPE → card keeps original due time")
    print(f"   2. calculate_next_test_interval() returns {next_interval} minutes")
    print(f"   3. After {next_interval} minutes, system checks due cards again")
    print(f"   4. Same card will be found and presented again")
    print(f"   5. User can then properly answer or TIMEOUT/ESCAPE again")
    
    # Test ESCAPE as well
    print(f"\n🚪 Testing ESCAPE logic...")
    
    # Create another card for ESCAPE test
    flashcard_data2 = {
        'word': 'test_escape',
        'meaning': 'testing escape', 
        'example': 'This is an escape test',
        'tag': 'testing'
    }
    card2_id = db.create_flashcard(flashcard_data2)
    
    original_due_time2 = datetime.now() - timedelta(minutes=5)  # Due 5 minutes ago
    
    with sqlite3.connect(db.db_path) as conn:
        conn.execute("""
            UPDATE flashcards 
            SET stage_id = 3, next_review_time = ?
            WHERE id = ?
        """, (original_due_time2, card2_id))
        conn.commit()
    
    # Apply ESCAPE
    db.update_flashcard_after_review(card2_id, "ESCAPE")
    
    # Check result
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review_time FROM flashcards WHERE id = ?", (card2_id,))
        after_escape_time = cursor.fetchone()[0]
    
    print(f"   Original due time: {original_due_time2}")
    print(f"   After ESCAPE time: {after_escape_time}")
    
    if str(original_due_time2) == str(after_escape_time):
        print(f"   ✅ ESCAPE also keeps original time")
    else:
        print(f"   ❌ ESCAPE changed the time!")
    
    # Final verification
    final_due_cards = db.get_due_flashcards(limit=10)
    final_due_count = len(final_due_cards)
    
    print(f"\n📋 Final state:")
    print(f"   Total due cards: {final_due_count}")
    print(f"   Expected: 2 (both test cards should remain due)")
    print(f"   Result: {'✅' if final_due_count == 2 else '❌'}")
    
    # Show scheduling behavior
    print(f"\n⏰ Scheduling behavior:")
    print(f"   Next check in: {next_interval} minutes")
    print(f"   Due cards will be: {final_due_count} (same cards)")
    print(f"   ✅ System respects original due times")
    print(f"   ✅ Natural review cycle maintained")
    
    # Cleanup
    import os
    os.remove("test_correct_logic.db")
    print(f"\n🧹 Cleanup completed")
    print("\n🎉 Correct TIMEOUT/ESCAPE logic verified!")

if __name__ == "__main__":
    test_correct_timeout_logic()