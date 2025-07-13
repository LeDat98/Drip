#!/usr/bin/env python3
"""
Test để kiểm tra việc TIMEOUT/ESCAPE không bị gọi lại liên tục
do có cooldown 5 phút.
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from database_manager import DatabaseManager, FlashCard

def test_cooldown_prevention():
    """Test that TIMEOUT/ESCAPE cards don't get called again immediately"""
    print("🧪 Testing Cooldown Prevention Logic")
    print("=" * 50)
    
    # Create test database
    db = DatabaseManager("test_cooldown.db")
    
    # Create a Stage 2 flashcard that should be due right now
    flashcard_data = {
        'word': 'test',
        'meaning': 'a trial', 
        'example': 'This is a test',
        'tag': 'testing'
    }
    card_id = db.create_flashcard(flashcard_data)
    
    # Set it to Stage 2 and make it due right now
    with sqlite3.connect(db.db_path) as conn:
        now = datetime.now()
        conn.execute("""
            UPDATE flashcards 
            SET stage_id = 2, next_review_time = ?
            WHERE id = ?
        """, (now, card_id))
        conn.commit()
    
    print(f"✅ Created test flashcard (ID: {card_id}) at Stage 2, due now")
    
    # Check 1: Should be in due flashcards list
    due_cards_before = db.get_due_flashcards(limit=10)
    due_ids_before = [card.id for card in due_cards_before]
    
    print(f"\n📋 Due flashcards BEFORE TIMEOUT:")
    print(f"  Count: {len(due_cards_before)}")
    print(f"  IDs: {due_ids_before}")
    print(f"  Test card {card_id} is due: {'✅' if card_id in due_ids_before else '❌'}")
    
    # Apply TIMEOUT to the card
    print(f"\n⏰ Applying TIMEOUT to card {card_id}...")
    db.update_flashcard_after_review(card_id, "TIMEOUT")
    
    # Check 2: Should NOT be in due flashcards list (due to 5-min cooldown)
    due_cards_after = db.get_due_flashcards(limit=10)
    due_ids_after = [card.id for card in due_cards_after]
    
    print(f"\n📋 Due flashcards AFTER TIMEOUT:")
    print(f"  Count: {len(due_cards_after)}")
    print(f"  IDs: {due_ids_after}")
    print(f"  Test card {card_id} is due: {'❌' if card_id not in due_ids_after else '⚠️'}")
    
    # Check 3: Verify the next_review_time is about 5 minutes in future
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review_time, stage_id FROM flashcards WHERE id = ?", (card_id,))
        next_time, stage = cursor.fetchone()
    
    next_dt = datetime.fromisoformat(next_time.replace('Z', '+00:00')) if isinstance(next_time, str) else next_time
    time_diff = (next_dt - datetime.now()).total_seconds() / 60  # minutes
    
    print(f"\n⏱️ Cooldown Analysis:")
    print(f"  Next review time: {next_time}")
    print(f"  Time until next review: {time_diff:.1f} minutes")
    print(f"  Stage unchanged: {stage == 2}")
    
    if 3 <= time_diff <= 7:
        print(f"  ✅ Cooldown applied correctly (~5 minutes)")
    else:
        print(f"  ❌ Cooldown incorrect (expected ~5 min, got {time_diff:.1f} min)")
    
    # Check 4: Test calculate_next_test_interval
    next_interval = db.calculate_next_test_interval()
    print(f"\n📊 calculate_next_test_interval():")
    print(f"  Returned interval: {next_interval} minutes")
    print(f"  Expected: 5-30 minutes (since no immediate due cards)")
    
    if 5 <= next_interval <= 30:
        print(f"  ✅ Interval reasonable (no immediate review needed)")
    else:
        print(f"  ⚠️ Interval might be too short (could cause rapid calls)")
    
    # Test ESCAPE as well
    print(f"\n🚪 Testing ESCAPE logic...")
    
    # Reset card to be due now
    with sqlite3.connect(db.db_path) as conn:
        now = datetime.now()
        conn.execute("""
            UPDATE flashcards 
            SET next_review_time = ?
            WHERE id = ?
        """, (now, card_id))
        conn.commit()
    
    # Apply ESCAPE
    db.update_flashcard_after_review(card_id, "ESCAPE")
    
    # Check result
    due_cards_escape = db.get_due_flashcards(limit=10)
    due_ids_escape = [card.id for card in due_cards_escape]
    
    print(f"  Due cards after ESCAPE: {len(due_cards_escape)}")
    print(f"  Test card {card_id} is due: {'❌' if card_id not in due_ids_escape else '⚠️'}")
    
    if card_id not in due_ids_escape:
        print(f"  ✅ ESCAPE also applies cooldown correctly")
    else:
        print(f"  ❌ ESCAPE cooldown failed")
    
    # Cleanup
    import os
    os.remove("test_cooldown.db")
    print(f"\n🧹 Cleanup completed")
    print("\n🎉 Cooldown prevention test completed!")

if __name__ == "__main__":
    test_cooldown_prevention()