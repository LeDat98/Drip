#!/usr/bin/env python3
"""
Test script for the new pre-review notification system
Tests both the standalone notification and integrated workflow
"""

import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer

from pre_review_notification import PreReviewNotification
from database_manager import DatabaseManager
from reviewer_schedule_maker import ReviewerScheduleMaker

class PreReviewTestController(QWidget):
    """Test controller for pre-review notification functionality"""
    
    def __init__(self):
        super().__init__()
        self.notification = None
        self.db_manager = None
        self.schedule_maker = None
        self.setup_ui()
        self.setup_test_data()
        
    def setup_ui(self):
        """Setup test controller UI"""
        self.setWindowTitle("Pre-Review Notification Test Controller")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Pre-Review Notification Test Controller")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Test buttons
        test1_btn = QPushButton("Test 1: Standalone Notification (3 flashcards)")
        test1_btn.clicked.connect(lambda: self.test_standalone_notification(3))
        layout.addWidget(test1_btn)
        
        test2_btn = QPushButton("Test 2: Standalone Notification (1 flashcard)")
        test2_btn.clicked.connect(lambda: self.test_standalone_notification(1))
        layout.addWidget(test2_btn)
        
        test3_btn = QPushButton("Test 3: Integrated Workflow (Accept)")
        test3_btn.clicked.connect(self.test_integrated_workflow)
        layout.addWidget(test3_btn)
        
        test4_btn = QPushButton("Test 4: Empty Database (No flashcards)")
        test4_btn.clicked.connect(self.test_empty_database)
        layout.addWidget(test4_btn)
        
        # Status label
        self.status_label = QLabel("Ready to test...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: green; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Instructions
        instructions = QLabel("""
Instructions:
• Test 1-2: Tests standalone notification only (260x100px, ultra-compact 3-field design)
• Test 3: Tests full workflow with database integration  
• Test 4: Tests behavior with no due flashcards
• Each notification auto-closes after 5 seconds with smooth slide-down animation
• Press ESC to decline, Enter to accept
• Notification slides down from top-right corner with 300ms animation
        """)
        instructions.setStyleSheet("font-size: 10px; color: gray; margin: 10px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        self.setLayout(layout)
        
    def setup_test_data(self):
        """Setup test database and components"""
        try:
            # Initialize database with test data
            self.db_manager = DatabaseManager("test_drip.db")
            self.schedule_maker = ReviewerScheduleMaker(self.db_manager)
            
            # Create test flashcards if database is empty
            self.create_test_flashcards()
            
            self.update_status("Test environment initialized successfully", "green")
            
        except Exception as e:
            self.update_status(f"Setup error: {e}", "red")
    
    def create_test_flashcards(self):
        """Create test flashcards for testing"""
        try:
            # Check if we already have flashcards
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM flashcards")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # Create test flashcards
                    test_cards = [
                        {"word": "hello", "meaning": "a greeting", "example": "Hello, how are you?", "tag": "greetings"},
                        {"word": "computer", "meaning": "electronic device for processing data", "example": "I work on my computer daily", "tag": "technology"},
                        {"word": "beautiful", "meaning": "pleasing to look at", "example": "The sunset is beautiful", "tag": "adjectives"},
                        {"word": "programming", "meaning": "process of creating software", "example": "Programming requires logical thinking", "tag": "technology"},
                        {"word": "learning", "meaning": "acquiring knowledge or skills", "example": "Learning new languages is fun", "tag": "education"}
                    ]
                    
                    for card_data in test_cards:
                        self.db_manager.create_flashcard(card_data)
                    
                    # Make all flashcards due for testing
                    cursor.execute("""
                        UPDATE flashcards 
                        SET next_review_time = ? 
                        WHERE next_review_time > ?
                    """, (datetime.now(), datetime.now()))
                    conn.commit()
                    
                    self.update_status(f"Created {len(test_cards)} test flashcards", "blue")
                else:
                    self.update_status(f"Found {count} existing flashcards", "blue")
                    
        except Exception as e:
            self.update_status(f"Error creating test data: {e}", "red")
    
    def test_standalone_notification(self, flashcard_count: int):
        """Test standalone notification modal"""
        try:
            self.update_status(f"Testing standalone notification with {flashcard_count} flashcard(s)...", "blue")
            
            # Clean up any existing notification
            if self.notification:
                self.notification.close()
                self.notification = None
            
            # Create and show notification
            self.notification = PreReviewNotification(flashcard_count)
            self.notification.review_accepted.connect(
                lambda: self.update_status("✅ User ACCEPTED review!", "green")
            )
            self.notification.review_declined.connect(
                lambda: self.update_status("❌ User DECLINED review or timed out", "orange")
            )
            
            self.notification.show_notification()
            
        except Exception as e:
            self.update_status(f"Test error: {e}", "red")
    
    def test_integrated_workflow(self):
        """Test full integrated workflow"""
        try:
            self.update_status("Testing integrated workflow...", "blue")
            
            # Start review session (which will show notification first)
            success, next_interval = self.schedule_maker.start_review_session()
            
            if success:
                self.update_status(f"✅ Review completed! Next session in {next_interval} minutes", "green")
            else:
                self.update_status(f"❌ Review was declined or failed. Next session in {next_interval} minutes", "orange")
                
        except Exception as e:
            self.update_status(f"Integrated test error: {e}", "red")
    
    def test_empty_database(self):
        """Test behavior with no due flashcards"""
        try:
            self.update_status("Testing empty database scenario...", "blue")
            
            # Temporarily set all flashcards to future review time
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                future_time = datetime.now().replace(hour=23, minute=59)
                cursor.execute("UPDATE flashcards SET next_review_time = ?", (future_time,))
                conn.commit()
            
            # Try to start review session
            success, next_interval = self.schedule_maker.start_review_session()
            
            if not success:
                self.update_status(f"✅ Correctly handled empty database. Next session in {next_interval} minutes", "green")
            else:
                self.update_status("❓ Unexpected: session started with no due flashcards", "orange")
            
            # Reset flashcards to be due again
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE flashcards SET next_review_time = ?", (datetime.now(),))
                conn.commit()
                
        except Exception as e:
            self.update_status(f"Empty database test error: {e}", "red")
    
    def update_status(self, message: str, color: str = "black"):
        """Update status label with message and color"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; margin: 10px; font-weight: bold;")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def closeEvent(self, event):
        """Clean up when closing"""
        try:
            if self.notification:
                self.notification.close()
            if self.schedule_maker:
                self.schedule_maker.cleanup()
        except:
            pass
        event.accept()

def main():
    """Main test function"""
    app = QApplication(sys.argv)
    
    # Create and show test controller
    controller = PreReviewTestController()
    controller.show()
    
    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()