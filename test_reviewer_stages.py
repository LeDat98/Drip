#!/usr/bin/env python3
"""
Test file to demo all 4 reviewer stages with sample data
This file creates sample flashcards and allows testing each stage independently
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reviewer_module import ReviewerModule
from database_manager import FlashCard

class StageTestController(QWidget):
    def __init__(self):
        super().__init__()
        self.reviewer = ReviewerModule()
        self.reviewer.review_completed.connect(self.on_review_completed)
        self.setup_ui()
        
        # Sample flashcards for testing
        self.sample_flashcards = {
            1: FlashCard(
                id=1, word="hello", meaning="a greeting", 
                example="Hello, how are you?", tag="basic",
                stage_id=1
            ),
            2: FlashCard(
                id=2, word="computer", meaning="an electronic device for processing data",
                example="I use my computer for work.", tag="technology",
                stage_id=2
            ),
            3: FlashCard(
                id=3, word="beautiful", meaning="having beauty; pleasing to the senses",
                example="The sunset is beautiful tonight.", tag="adjective",
                stage_id=3
            ),
            4: FlashCard(
                id=4, word="programming", meaning="the process of creating computer software",
                example="I enjoy programming in Python.", tag="technology",
                stage_id=4
            )
        }
        
        # Contextual words for Stage 3 multiple choice
        self.contextual_words = [
            "wonderful", "terrible", "amazing", "awful", "gorgeous", 
            "hideous", "stunning", "ugly", "lovely", "horrible"
        ]
        
        # Contextual meanings for Stage 2 multiple choice
        self.contextual_meanings = [
            "a programming language for web development",
            "a method of organizing data in computer systems",
            "an algorithm for solving complex problems",
            "a tool for creating user interfaces",
            "a framework for building applications",
            "a protocol for network communication",
            "a device for storing digital information",
            "a technique for optimizing performance",
            "a system for managing databases",
            "a platform for cloud computing"
        ]
        
        # Multiple flashcards for testing early exit scenarios
        self.multi_flashcards = [
            FlashCard(id=10, word="test1", meaning="first test word", stage_id=1),
            FlashCard(id=11, word="test2", meaning="second test word", stage_id=2),
            FlashCard(id=12, word="test3", meaning="third test word", stage_id=3),
            FlashCard(id=13, word="test4", meaning="fourth test word", stage_id=1),
            FlashCard(id=14, word="test5", meaning="fifth test word", stage_id=2),
        ]
    
    def setup_ui(self):
        """Setup the test controller UI"""
        self.setWindowTitle("Reviewer Stage Tester")
        self.setFixedSize(450, 600)
        
        # Apply same styling as modal
        self.setStyleSheet("background-color: #676767;")
        
        # Main container
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(68, 68, 68, 0.75);
                border: 1px solid #444444;
                border-radius: 8px;
            }
        """)
        
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)
        self.setLayout(window_layout)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        container.setLayout(main_layout)
        
        # Title
        title = QLabel("📚 Reviewer Stage Tester")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; margin-bottom: 10px; background-color: transparent; border: none;")
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("Test each stage of the vocabulary review system:")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #B0B0B0; margin-bottom: 10px; background-color: transparent; border: none;")
        main_layout.addWidget(desc)
        
        # Stage buttons
        stages_layout = QVBoxLayout()
        
        # Stage 1 button
        stage1_btn = QPushButton("Stage 1: Info Display\n(Word: 'hello')")
        stage1_btn.setStyleSheet(self.get_button_style())
        stage1_btn.clicked.connect(lambda: self.test_stage(1))
        stages_layout.addWidget(stage1_btn)
        
        # Stage 2 button
        stage2_btn = QPushButton("Stage 2: Multiple Choice Meaning\n(Word: 'computer')")
        stage2_btn.setStyleSheet(self.get_button_style())
        stage2_btn.clicked.connect(lambda: self.test_stage(2))
        stages_layout.addWidget(stage2_btn)
        
        # Stage 3 button
        stage3_btn = QPushButton("Stage 3: Multiple Choice\n(Meaning: 'having beauty...')")
        stage3_btn.setStyleSheet(self.get_button_style())
        stage3_btn.clicked.connect(lambda: self.test_stage(3))
        stages_layout.addWidget(stage3_btn)
        
        # Stage 4 button
        stage4_btn = QPushButton("Stage 4: Type Word\n(Meaning: 'process of creating software')")
        stage4_btn.setStyleSheet(self.get_button_style())
        stage4_btn.clicked.connect(lambda: self.test_stage(4))
        stages_layout.addWidget(stage4_btn)
        
        main_layout.addLayout(stages_layout)
        
        # Early exit test buttons
        early_exit_layout = QVBoxLayout()
        
        # Add separator
        separator = QLabel("─── Early Exit Tests ───")
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #888888; font-size: 10px; background-color: transparent; border: none;")
        early_exit_layout.addWidget(separator)
        
        # Test multiple flashcards (normal flow)
        multi_button = QPushButton("Test 5 Flashcards\n(Normal Flow)")
        multi_button.setStyleSheet("""
            QPushButton {
                background-color: #006600;
                color: #FFFFFF;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #007700;
            }
            QPushButton:pressed {
                background-color: #005500;
            }
        """)
        multi_button.clicked.connect(lambda: self.test_multiple_flashcards())
        early_exit_layout.addWidget(multi_button)
        
        # Test timeout scenario
        timeout_button = QPushButton("Test Timeout Exit\n(Auto-close on first timeout)")
        timeout_button.setStyleSheet("""
            QPushButton {
                background-color: #CC6600;
                color: #FFFFFF;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #DD7700;
            }
            QPushButton:pressed {
                background-color: #BB5500;
            }
        """)
        timeout_button.clicked.connect(lambda: self.test_timeout_scenario())
        early_exit_layout.addWidget(timeout_button)
        
        # Test ESC scenario  
        esc_button = QPushButton("Test ESC Exit\n(Press ESC to exit early)")
        esc_button.setStyleSheet("""
            QPushButton {
                background-color: #CC0000;
                color: #FFFFFF;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #DD0000;
            }
            QPushButton:pressed {
                background-color: #BB0000;
            }
        """)
        esc_button.clicked.connect(lambda: self.test_esc_scenario())
        early_exit_layout.addWidget(esc_button)
        
        main_layout.addLayout(early_exit_layout)
        
        # Results area
        self.results_label = QLabel("Click a stage button to test...")
        self.results_label.setAlignment(Qt.AlignCenter)
        self.results_label.setStyleSheet("color: #B0B0B0; font-size: 10px; background-color: transparent; border: none;")
        main_layout.addWidget(self.results_label)
        
        # Close button
        close_btn = QPushButton("Close Tester")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #B0B0B0;
                color: #121212;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #C0C0C0;
            }
            QPushButton:pressed {
                background-color: #A0A0A0;
            }
        """)
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)
    
    def get_button_style(self):
        """Get consistent button styling"""
        return """
            QPushButton {
                background-color: #888888;
                color: #ffffff;
                border: none;
                padding: 12px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #999999;
            }
            QPushButton:pressed {
                background-color: #777777;
            }
        """
    
    def test_stage(self, stage_number):
        """Test a specific stage"""
        flashcard = self.sample_flashcards[stage_number]
        
        self.results_label.setText(f"Testing Stage {stage_number}...")
        
        # Start reviewer with single flashcard
        # Use longer timeouts for testing
        test_timeouts = {
            1: 7,  # Stage 1: Info display
            2: 15,  # Stage 2: Input meaning  
            3: 10,  # Stage 3: Multiple choice
            4: 15, # Stage 4: Input word
        }
        
        self.reviewer.start_review(
            flashcards=[flashcard],
            stage_timeouts=test_timeouts,
            contextual_words=self.contextual_words,
            contextual_meanings=self.contextual_meanings
        )
    
    def test_multiple_flashcards(self):
        """Test multiple flashcards with normal flow"""
        self.results_label.setText("Testing 5 flashcards (normal flow)...\nTry answering normally or test timeout/ESC at any point")
        
        # Use reasonable timeouts for testing
        test_timeouts = {
            1: 10,  # 10 seconds for Stage 1
            2: 20,  # 20 seconds for Stage 2
            3: 15,  # 15 seconds for Stage 3
            4: 20   # 20 seconds for Stage 4
        }
        
        self.reviewer.start_review(
            flashcards=self.multi_flashcards,
            stage_timeouts=test_timeouts,
            contextual_words=self.contextual_words,
            contextual_meanings=self.contextual_meanings
        )
    
    def test_timeout_scenario(self):
        """Test timeout scenario with multiple flashcards"""
        self.results_label.setText("Testing timeout scenario...\nDON'T interact - wait for first timeout\nModal should close immediately")
        
        # Use very short timeouts for testing
        test_timeouts = {
            1: 3,   # 3 seconds for quick timeout
            2: 5,   # 5 seconds
            3: 4,   # 4 seconds
            4: 6    # 6 seconds
        }
        
        self.reviewer.start_review(
            flashcards=self.multi_flashcards,
            stage_timeouts=test_timeouts,
            contextual_words=self.contextual_words,
            contextual_meanings=self.contextual_meanings
        )
    
    def test_esc_scenario(self):
        """Test ESC key scenario with multiple flashcards"""
        self.results_label.setText("Testing ESC scenario...\nPress ESC key on any flashcard\nModal should close immediately")
        
        # Use normal timeouts but user will press ESC
        test_timeouts = {
            1: 15,  # 15 seconds 
            2: 20,  # 20 seconds
            3: 15,  # 15 seconds
            4: 20   # 20 seconds
        }
        
        self.reviewer.start_review(
            flashcards=self.multi_flashcards,
            stage_timeouts=test_timeouts,
            contextual_words=self.contextual_words,
            contextual_meanings=self.contextual_meanings
        )
    
    def on_review_completed(self, results):
        """Handle review completion"""
        if results:
            result_summary = []
            result_counts = {"True": 0, "False": 0, "TIMEOUT": 0, "ESCAPE": 0}
            
            for flashcard_id, result in results.items():
                # Find the flashcard to get its details
                flashcard = None
                # Check both sample flashcards and multi flashcards
                all_flashcards = list(self.sample_flashcards.values()) + self.multi_flashcards
                for fc in all_flashcards:
                    if fc.id == flashcard_id:
                        flashcard = fc
                        break
                
                if flashcard:
                    result_summary.append(f"• {flashcard.word} (Stage {flashcard.stage_id}): {result}")
                else:
                    result_summary.append(f"• ID {flashcard_id}: {result}")
                
                # Count results
                if result in result_counts:
                    result_counts[result] += 1
            
            # Create summary
            summary_parts = []
            for result_type, count in result_counts.items():
                if count > 0:
                    summary_parts.append(f"{result_type}: {count}")
            
            summary = f"Review completed! {len(results)} results\n({', '.join(summary_parts)})"
            detailed_results = "\n".join(result_summary)
            self.results_label.setText(f"{summary}\n\n{detailed_results}")
        else:
            self.results_label.setText("Review completed with no results")

def main():
    """Main function to run the stage tester"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setQuitOnLastWindowClosed(True)
    
    # Create and show the test controller
    tester = StageTestController()
    tester.show()
    
    # Center window on screen
    screen = app.desktop().screenGeometry()
    window = tester.geometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    tester.move(x, y)
    
    print("Reviewer Stage Tester started!")
    print("Instructions:")
    print("1. Click any stage button to test that specific review type")
    print("2. The review modal will appear in the top-right corner")
    print("3. For Stage 1: Click 'Got It!' or wait for auto-close")
    print("4. For Stage 2: Click one of the multiple choice meaning options")
    print("5. For Stage 3: Click one of the multiple choice word options")
    print("6. For Stage 4: Type the word and press Enter or click Submit")
    print("7. Results will appear in the tester window")
    print("")
    print("Early Exit Tests:")
    print("• Test 5 Flashcards: Normal flow with multiple flashcards")
    print("• Test Timeout Exit: Don't interact - modal closes on first timeout")
    print("• Test ESC Exit: Press ESC on any flashcard to exit early")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()