#!/usr/bin/env python3
"""
Test file for testing two consecutive review sessions to verify
that modal summary from first session doesn't appear during second session.

Session 1: 5 flashcards
Session 2: 3 flashcards

This test helps identify the issue where modal summary UI from previous
session appears during the new session.
"""

import sys
import logging
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from database_manager import DatabaseManager, FlashCard
from reviewer_schedule_maker import ReviewerScheduleMaker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DoubleSessionTester(QWidget):
    """GUI test controller for double session testing"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.reviewer_schedule_maker = ReviewerScheduleMaker(self.db_manager)
        
        # Test data
        self.session1_flashcards = []  # 5 flashcards
        self.session2_flashcards = []  # 3 flashcards
        
        # Setup UI
        self.setup_ui()
        self.setup_test_data()
        
    def setup_ui(self):
        """Setup the test controller UI"""
        self.setWindowTitle("Double Session Test Controller")
        self.setFixedSize(500, 600)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🧪 Double Session Test Controller")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Test consecutive review sessions:\n• Session 1: 5 flashcards\n• Session 2: 3 flashcards")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #34495e; font-size: 12px; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # Test buttons
        self.test_session1_btn = QPushButton("🎯 Start Session 1 (5 flashcards)")
        self.test_session1_btn.setStyleSheet(self.get_button_style("#3498db"))
        self.test_session1_btn.clicked.connect(self.start_session1)
        layout.addWidget(self.test_session1_btn)
        
        self.test_session2_btn = QPushButton("🎯 Start Session 2 (3 flashcards)")
        self.test_session2_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        self.test_session2_btn.clicked.connect(self.start_session2)
        self.test_session2_btn.setEnabled(False)  # Disabled until session 1 completes
        layout.addWidget(self.test_session2_btn)
        
        # Auto sequence button
        self.auto_test_btn = QPushButton("🔄 Auto Test Both Sessions (5s delay)")
        self.auto_test_btn.setStyleSheet(self.get_button_style("#9b59b6"))
        self.auto_test_btn.clicked.connect(self.start_auto_test)
        layout.addWidget(self.auto_test_btn)
        
        # Reset button
        self.reset_btn = QPushButton("🔄 Reset Test Data")
        self.reset_btn.setStyleSheet(self.get_button_style("#95a5a6"))
        self.reset_btn.clicked.connect(self.reset_test_data)
        layout.addWidget(self.reset_btn)
        
        # Results area
        results_label = QLabel("📊 Test Results:")
        results_label.setStyleSheet("color: #2c3e50; font-weight: bold; margin-top: 15px;")
        layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-family: monospace;
                font-size: 10px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.results_text)
        
        # Status label
        self.status_label = QLabel("Status: Ready for testing")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Window styling
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        
    def get_button_style(self, color):
        """Get button style with specified color"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #7f8c8d;
            }}
        """
    
    def darken_color(self, hex_color, factor=0.9):
        """Darken a hex color by a factor"""
        # Simple darkening - multiply RGB values by factor
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        
    def setup_test_data(self):
        """Setup test flashcards data"""
        try:
            # Session 1: 5 flashcards with different stages
            self.session1_flashcards = [
                FlashCard(
                    id=1001, word="hello", meaning="greeting", example="Hello, how are you?", 
                    tag="greetings", stage_id=1, review_count=0, correct_count=0,
                    created_at="2024-01-01 10:00:00", next_review_time="2024-01-01 10:30:00"
                ),
                FlashCard(
                    id=1002, word="computer", meaning="electronic machine", example="I use a computer for work", 
                    tag="technology", stage_id=2, review_count=1, correct_count=0,
                    created_at="2024-01-01 11:00:00", next_review_time="2024-01-01 11:30:00"
                ),
                FlashCard(
                    id=1003, word="beautiful", meaning="attractive or pleasing", example="The sunset is beautiful", 
                    tag="adjectives", stage_id=3, review_count=2, correct_count=1,
                    created_at="2024-01-01 12:00:00", next_review_time="2024-01-01 12:30:00"
                ),
                FlashCard(
                    id=1004, word="programming", meaning="process of creating software", example="I enjoy programming", 
                    tag="technology", stage_id=4, review_count=3, correct_count=2,
                    created_at="2024-01-01 13:00:00", next_review_time="2024-01-01 13:30:00"
                ),
                FlashCard(
                    id=1005, word="learning", meaning="acquiring knowledge", example="Learning is fun", 
                    tag="education", stage_id=1, review_count=0, correct_count=0,
                    created_at="2024-01-01 14:00:00", next_review_time="2024-01-01 14:30:00"
                )
            ]
            
            # Session 2: 3 flashcards with different stages
            self.session2_flashcards = [
                FlashCard(
                    id=2001, word="testing", meaning="checking for errors", example="Testing is important", 
                    tag="development", stage_id=2, review_count=1, correct_count=0,
                    created_at="2024-01-01 15:00:00", next_review_time="2024-01-01 15:30:00"
                ),
                FlashCard(
                    id=2002, word="success", meaning="achievement of goals", example="Success requires effort", 
                    tag="motivation", stage_id=3, review_count=2, correct_count=1,
                    created_at="2024-01-01 16:00:00", next_review_time="2024-01-01 16:30:00"
                ),
                FlashCard(
                    id=2003, word="practice", meaning="repeated exercise", example="Practice makes perfect", 
                    tag="improvement", stage_id=4, review_count=3, correct_count=2,
                    created_at="2024-01-01 17:00:00", next_review_time="2024-01-01 17:30:00"
                )
            ]
            
            self.log_message("✅ Test data setup completed")
            self.log_message(f"Session 1: {len(self.session1_flashcards)} flashcards")
            self.log_message(f"Session 2: {len(self.session2_flashcards)} flashcards")
            
        except Exception as e:
            self.log_message(f"❌ Error setting up test data: {e}")
    
    def start_session1(self):
        """Start Session 1 with 5 flashcards"""
        try:
            self.status_label.setText("Status: Running Session 1...")
            self.status_label.setStyleSheet("color: #3498db; font-weight: bold; padding: 5px;")
            self.test_session1_btn.setEnabled(False)
            
            self.log_message("🎯 Starting Session 1 (5 flashcards)")
            
            # Prepare contextual data
            contextual_words = ["example", "test", "word", "sample", "demo"]
            contextual_meanings = ["a test meaning", "sample definition", "example phrase"]
            
            # Execute session using reviewer_schedule_maker
            results = self.reviewer_schedule_maker.execute_review_session(
                self.session1_flashcards, contextual_words, contextual_meanings
            )
            
            self.log_message(f"📊 Session 1 completed with {len(results) if results else 0} results")
            if results:
                for flashcard_id, result in results.items():
                    self.log_message(f"  Flashcard {flashcard_id}: {result}")
            
            # Enable session 2 button
            self.test_session2_btn.setEnabled(True)
            self.status_label.setText("Status: Session 1 completed, ready for Session 2")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
            
        except Exception as e:
            self.log_message(f"❌ Error in Session 1: {e}")
            self.test_session1_btn.setEnabled(True)
            self.status_label.setText("Status: Session 1 failed")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 5px;")
    
    def start_session2(self):
        """Start Session 2 with 3 flashcards"""
        try:
            self.status_label.setText("Status: Running Session 2...")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 5px;")
            self.test_session2_btn.setEnabled(False)
            
            self.log_message("🎯 Starting Session 2 (3 flashcards)")
            
            # Prepare contextual data
            contextual_words = ["debug", "fix", "code", "build", "run"]
            contextual_meanings = ["finding bugs", "fixing issues", "writing code"]
            
            # Execute session using reviewer_schedule_maker
            results = self.reviewer_schedule_maker.execute_review_session(
                self.session2_flashcards, contextual_words, contextual_meanings
            )
            
            self.log_message(f"📊 Session 2 completed with {len(results) if results else 0} results")
            if results:
                for flashcard_id, result in results.items():
                    self.log_message(f"  Flashcard {flashcard_id}: {result}")
            
            self.status_label.setText("Status: Both sessions completed successfully!")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
            
            # Re-enable session 1 for repeated testing
            self.test_session1_btn.setEnabled(True)
            
        except Exception as e:
            self.log_message(f"❌ Error in Session 2: {e}")
            self.test_session2_btn.setEnabled(True)
            self.status_label.setText("Status: Session 2 failed")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 5px;")
    
    def start_auto_test(self):
        """Start automatic testing of both sessions with delay"""
        try:
            self.status_label.setText("Status: Auto test starting...")
            self.status_label.setStyleSheet("color: #9b59b6; font-weight: bold; padding: 5px;")
            self.auto_test_btn.setEnabled(False)
            
            self.log_message("🔄 Starting automatic double session test")
            
            # Start session 1
            self.start_session1()
            
            # Schedule session 2 after 5 seconds
            QTimer.singleShot(5000, self.auto_start_session2)
            
        except Exception as e:
            self.log_message(f"❌ Error in auto test: {e}")
            self.auto_test_btn.setEnabled(True)
    
    def auto_start_session2(self):
        """Auto start session 2 (called by timer)"""
        self.log_message("⏰ Auto-starting Session 2 after 5-second delay")
        self.start_session2()
        self.auto_test_btn.setEnabled(True)
    
    def reset_test_data(self):
        """Reset test data and UI state"""
        try:
            self.log_message("🔄 Resetting test data...")
            
            # Reset UI state
            self.test_session1_btn.setEnabled(True)
            self.test_session2_btn.setEnabled(False)
            self.auto_test_btn.setEnabled(True)
            
            # Clear results
            self.results_text.clear()
            
            # Cleanup reviewer
            if self.reviewer_schedule_maker.reviewer_module:
                self.reviewer_schedule_maker.reviewer_module.close()
                self.reviewer_schedule_maker.reviewer_module = None
            
            self.status_label.setText("Status: Reset completed, ready for testing")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
            
            self.log_message("✅ Reset completed successfully")
            
        except Exception as e:
            self.log_message(f"❌ Error during reset: {e}")
    
    def log_message(self, message):
        """Log message to results area"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.results_text.append(formatted_message)
        
        # Also log to console
        logger.info(message)
        
        # Auto-scroll to bottom
        scrollbar = self.results_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Cleanup reviewer
        if self.reviewer_schedule_maker.reviewer_module:
            self.reviewer_schedule_maker.reviewer_module.close()
        
        event.accept()

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Double Session Tester")
    app.setApplicationVersion("1.0")
    
    # Create and show test window
    tester = DoubleSessionTester()
    tester.show()
    
    # Center window on screen
    screen_geometry = app.desktop().screenGeometry()
    x = (screen_geometry.width() - tester.width()) // 2
    y = (screen_geometry.height() - tester.height()) // 2
    tester.move(x, y)
    
    logger.info("Double Session Tester started")
    logger.info("Instructions:")
    logger.info("1. Click 'Start Session 1' to test 5 flashcards")
    logger.info("2. After Session 1 completes, click 'Start Session 2' to test 3 flashcards")
    logger.info("3. Or use 'Auto Test Both Sessions' for automatic testing")
    logger.info("4. Watch for any UI overlap issues between sessions")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())