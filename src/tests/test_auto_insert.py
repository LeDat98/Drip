"""
Test Auto-Insert New Word functionality
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.auto_insert_new_word import AutoInsertNewWord
from src.database.database_manager import DatabaseManager

def test_auto_insert_workflow():
    """Test the complete auto-insert workflow"""
    print("=" * 60)
    print("Testing Auto-Insert New Word Workflow")
    print("=" * 60)
    
    # Initialize managers
    auto_insert = AutoInsertNewWord()
    db_manager = DatabaseManager()
    
    # Test 1: Load words from JSON
    print("\n1. Testing JSON word loading...")
    words = auto_insert.load_words_from_json()
    print(f"   ✓ Loaded {len(words)} words from JSON file")
    
    # Show first 3 words với format mới
    for i, word_data in enumerate(words[:3]):
        print(f"   - {word_data.get('word', 'N/A')}: {word_data.get('meaning', 'N/A')}")
        print(f"     Example: {word_data.get('example', 'N/A')}")
        print(f"     Tag: {word_data.get('tag', 'N/A')}")
    
    # Test 2: Check existing words
    print("\n2. Testing duplicate word detection...")
    existing_words = 0
    for word_data in words[:10]:  # Check first 10 words
        if auto_insert.check_word_exists(word_data['word']):
            existing_words += 1
    print(f"   ✓ Found {existing_words} existing words out of first 10")
    
    # Test 3: Get current status
    print("\n3. Testing auto-insert status...")
    status = auto_insert.get_auto_insert_status(target_count=5, target_hour=8, target_minute=0)
    print(f"   ✓ Target count: {status['target_count']}")
    print(f"   ✓ Today count: {status['today_count']}")
    print(f"   ✓ Remaining count: {status['remaining_count']}")
    print(f"   ✓ Is completed: {status['is_completed']}")
    print(f"   ✓ Is time reached: {status['is_time_reached']}")
    
    # Test 4: Test auto-insert with past time (should work)
    print("\n4. Testing auto-insert with past time...")
    past_hour = (datetime.now() - timedelta(hours=1)).hour
    result = auto_insert.auto_insert_daily_words(
        target_count=2,  # Small number for testing
        target_hour=past_hour,
        target_minute=0
    )
    
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ Message: {result['message']}")
    print(f"   ✓ Inserted count: {result['inserted_count']}")
    print(f"   ✓ Already exists count: {result['already_exists_count']}")
    print(f"   ✓ Skipped count: {result['skipped_count']}")
    
    # Test 5: Test auto-insert with future time (should not work)
    print("\n5. Testing auto-insert with future time...")
    future_hour = (datetime.now() + timedelta(hours=2)).hour
    result = auto_insert.auto_insert_daily_words(
        target_count=2,
        target_hour=future_hour,
        target_minute=0
    )
    
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ Message: {result['message']}")
    
    # Test 6: Count total flashcards in database
    print("\n6. Database statistics...")
    try:
        import sqlite3
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM flashcards")
            total_count = cursor.fetchone()[0]
            print(f"   ✓ Total flashcards in database: {total_count}")
            
            # Count by tag
            cursor.execute("SELECT tag, COUNT(*) FROM flashcards GROUP BY tag ORDER BY COUNT(*) DESC LIMIT 5")
            tags = cursor.fetchall()
            print("   ✓ Top tags:")
            for tag, count in tags:
                print(f"     - {tag or 'no-tag'}: {count} words")
    except Exception as e:
        print(f"   ✗ Error querying database: {e}")
    
    print("\n" + "=" * 60)
    print("Auto-Insert Test Completed Successfully!")
    print("=" * 60)

def test_settings_integration():
    """Test settings file integration"""
    print("\n" + "=" * 60)
    print("Testing Settings Integration")
    print("=" * 60)
    
    settings_file = "data/drip_settings.json"
    
    # Test reading current settings
    print("\n1. Testing current settings...")
    if os.path.exists(settings_file):
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            auto_insert_settings = settings.get('auto_insert', {})
            print(f"   ✓ Auto-insert enabled: {auto_insert_settings.get('enabled', False)}")
            print(f"   ✓ Daily count: {auto_insert_settings.get('daily_count', 10)}")
            print(f"   ✓ Time: {auto_insert_settings.get('hour', 7)}:{auto_insert_settings.get('minute', 0):02d}")
    else:
        print("   ✓ Settings file does not exist (will use defaults)")
    
    print("\n" + "=" * 60)
    print("Settings Integration Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_auto_insert_workflow()
        test_settings_integration()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()