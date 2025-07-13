from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QLabel, QPushButton, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
from typing import List, Dict
import logging
import random

from database_manager import FlashCard

logger = logging.getLogger(__name__)

class ReviewerModule(QWidget):
    review_completed = pyqtSignal(dict)  # {flashcard_id: result}
    
    def __init__(self):
        super().__init__()
        self.current_flashcards = []
        self.current_index = 0
        self.results = {}
        self.timeout_seconds = 10
        self.contextual_words = []
        self.contextual_meanings = []
        
        self.setup_ui()
        self.setup_window_properties()
        
        # Auto-close timer
        self.auto_close_timer = QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.handle_timeout)
        
        # Countdown timer for display update
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown_display)
        self.remaining_seconds = 0
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Vocabulary Review")
        self.setFixedSize(380, 320)
        
        # Create main container widget with modal_style.html color scheme
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(68, 68, 68, 0.75);
                border: 1px solid #444444;
                border-radius: 8px;
            }
        """)
        
        # Main layout for the window
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.container)
        self.setLayout(window_layout)
        
        # Content layout inside container
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.container.setLayout(self.main_layout)
        
        # Progress indicator
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #B0B0B0; font-size: 12px; font-weight: bold; background-color: transparent; border: none;")
        
        # Content area (will be populated dynamically)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Timer indicator
        self.timer_label = QLabel("")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: #E0E0E0; font-size: 12px; font-weight: bold; background-color: transparent; border: none;")
        
        # Add to main layout
        self.main_layout.addWidget(self.progress_label)
        self.main_layout.addWidget(self.content_widget)
        self.main_layout.addWidget(self.timer_label)
        
    def setup_window_properties(self):
        """Setup window properties according to specifications"""
        # Frameless window, always on top, no focus grab
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window background color to match modal_style.html
        self.setStyleSheet("background-color: #676767;")
        
        # Enable key press events
        self.setFocusPolicy(Qt.StrongFocus)
        
    def start_review(self, flashcards: List[FlashCard], stage_timeouts: Dict[int, int] = None, 
                     contextual_words: List[str] = None, contextual_meanings: List[str] = None) -> Dict[int, str]:
        """Start review session with given flashcards"""
        try:
            if not flashcards:
                logger.info("No flashcards provided for review")
                return {}
            
            # Stop any existing timer
            self.auto_close_timer.stop()
            
            # Reset state
            self.current_flashcards = flashcards
            self.current_index = 0
            self.results = {}
            self.stage_timeouts = stage_timeouts or {1: 7, 2: 15, 3: 12, 4: 15}
            self.contextual_words = contextual_words or []
            self.contextual_meanings = contextual_meanings or []
            
            # Clear any existing input references
            if hasattr(self, 'answer_input'):
                delattr(self, 'answer_input')
            
            # Position at top-right corner
            self.move(self.get_screen_width() - 420, 50)
            
            # Start with first flashcard
            self.show_current_flashcard()
            self.show()
            
            logger.info(f"Started review session with {len(flashcards)} flashcards")
            
        except Exception as e:
            logger.error(f"Error starting review: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_screen_width(self):
        """Get screen width for positioning"""
        try:
            from PyQt5.QtWidgets import QApplication
            return QApplication.desktop().screenGeometry().width()
        except:
            return 1920  # Default fallback
    
    def adjust_modal_size(self, flashcard: FlashCard):
        """Adjust modal size based on content"""
        base_height = 320
        
        # Calculate additional height needed
        extra_height = 0
        
        # Add height for example text if present
        if flashcard.example and flashcard.stage_id in [2, 4]:
            # Estimate height based on example length
            example_lines = len(flashcard.example) // 50 + 1  # ~50 chars per line
            extra_height += example_lines * 20  # 20px per line
        
        # Add height for multiple choice stages (need more space for buttons)
        if flashcard.stage_id in [2, 3]:
            extra_height += 20  # Extra space for multiple choice buttons
        
        # Set new size
        new_height = base_height + extra_height
        self.setFixedSize(380, new_height)
    
    def show_current_flashcard(self):
        """Display current flashcard based on its stage"""
        if self.current_index >= len(self.current_flashcards):
            self.show_summary()
            return
        
        flashcard = self.current_flashcards[self.current_index]
        
        # Update progress
        self.progress_label.setText(f"Review {self.current_index + 1}/{len(self.current_flashcards)}")
        
        # Clear previous content
        self.clear_content()
        
        # Get timeout for current stage
        self.timeout_seconds = self.stage_timeouts.get(flashcard.stage_id, 10)
        
        # Adjust modal size based on content
        self.adjust_modal_size(flashcard)
        
        # Show appropriate test based on stage
        if flashcard.stage_id == 1:
            self.show_info_display(flashcard)
        elif flashcard.stage_id == 2:
            self.show_multiple_choice_meaning(flashcard)
        elif flashcard.stage_id == 3:
            self.show_multiple_choice(flashcard)
        elif flashcard.stage_id == 4:
            self.show_input_word(flashcard)
        
        # Start auto-close timer
        self.start_timer()
    
    def clear_content(self):
        """Clear content area safely"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
    
    def clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
    
    def show_info_display(self, flashcard: FlashCard):
        """Stage 1: Info display only"""
        # Word
        word_label = QLabel(flashcard.word)
        word_label.setAlignment(Qt.AlignCenter)
        word_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF; margin: 5px; background-color: transparent; border: none;")
        
        # Meaning
        meaning_label = QLabel(flashcard.meaning)
        meaning_label.setAlignment(Qt.AlignCenter)
        meaning_label.setStyleSheet("font-size: 16px; color: #E0E0E0; margin: 5px; background-color: transparent; border: none;")
        meaning_label.setWordWrap(True)
        
        # Example (if available)
        if flashcard.example:
            example_label = QLabel(f"Example: {flashcard.example}")
            example_label.setAlignment(Qt.AlignCenter)
            example_label.setStyleSheet("font-size: 12px; color: #B0B0B0; margin: 5px; font-style: italic; background-color: transparent; border: none;")
            example_label.setWordWrap(True)
            self.content_layout.addWidget(example_label)
        
        # Tag (if available)
        if flashcard.tag:
            tag_label = QLabel(f"#{flashcard.tag}")
            tag_label.setAlignment(Qt.AlignCenter)
            tag_label.setStyleSheet("font-size: 10px; color: #B0B0B0; margin: 5px; background-color: transparent; border: none;")
            self.content_layout.addWidget(tag_label)
        
        # Got It button for Stage 1
        got_it_button = QPushButton("Got It!")
        got_it_button.setStyleSheet("""
            QPushButton {
                background-color: #888888;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #999999;
            }
            QPushButton:pressed {
                background-color: #777777;
            }
        """)
        got_it_button.clicked.connect(lambda _: self.record_result("True"))
        
        self.content_layout.addWidget(word_label)
        self.content_layout.addWidget(meaning_label)
        self.content_layout.addWidget(got_it_button)
        
        # Timeout is already set in show_current_flashcard() based on stage
    
    def show_multiple_choice_meaning(self, flashcard: FlashCard):
        """Stage 2: Multiple choice meaning given word"""
        # Word
        word_label = QLabel(flashcard.word)
        word_label.setAlignment(Qt.AlignCenter)
        word_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF; margin: 10px; background-color: transparent; border: none;")
        
        # Example (if available)
        if flashcard.example:
            example_label = QLabel(f"Example: {flashcard.example}")
            example_label.setAlignment(Qt.AlignCenter)
            example_label.setStyleSheet("font-size: 12px; color: #B0B0B0; margin: 5px; font-style: italic; background-color: transparent; border: none;")
            example_label.setWordWrap(True)
            self.content_layout.addWidget(example_label)
        
        # Get contextual meanings for options
        options = self.get_multiple_choice_meanings_for_stage2(flashcard)
        
        # Create buttons for options
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)  # Tăng spacing từ 3 lên 8
        
        for i, option in enumerate(options):
            button = QPushButton(f"{chr(65+i)}. {option}")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    color: #121212;
                    border: none;
                    padding: 6px 8px;
                    border-radius: 4px;
                    font-weight: normal;
                    font-size: 12px;
                    text-align: left;
                    margin: 0px;
                    min-height: 25px;
                    max-height: 35px;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;
                }
                QPushButton:pressed {
                    background-color: #D0D0D0;
                }
            """)
            
            # Set minimum size to ensure text fits
            button.setMinimumHeight(30)
            button.setMaximumHeight(40)
            
            button.clicked.connect(lambda checked=False, opt=option: self.check_multiple_choice_answer(opt, flashcard.meaning))
            button_layout.addWidget(button)
        
        self.content_layout.addWidget(word_label)
        self.content_layout.addLayout(button_layout)
    
    def show_multiple_choice(self, flashcard: FlashCard):
        """Stage 3: Multiple choice word from meaning"""
        # Meaning
        meaning_label = QLabel(flashcard.meaning)
        meaning_label.setAlignment(Qt.AlignCenter)
        meaning_label.setStyleSheet("font-size: 16px; color: #FFFFFF; margin: 10px; background-color: transparent; border: none;")
        meaning_label.setWordWrap(True)
        
        # Get random words for options
        options = self.get_multiple_choice_options(flashcard)
        
        # Create buttons for options
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)  # Tăng spacing từ 3 lên 8
        
        for i, option in enumerate(options):
            button = QPushButton(f"{chr(65+i)}. {option}")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    color: #121212;
                    border: none;
                    padding: 6px 8px;
                    border-radius: 4px;
                    font-weight: normal;
                    font-size: 12px;
                    text-align: left;
                    margin: 0px;
                    min-height: 25px;
                    max-height: 35px;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;
                }
                QPushButton:pressed {
                    background-color: #D0D0D0;
                }
            """)
            
            # Set minimum size to ensure text fits
            button.setMinimumHeight(30)
            button.setMaximumHeight(40)
            
            button.clicked.connect(lambda checked=False, opt=option: self.check_multiple_choice_answer(opt, flashcard.word))
            button_layout.addWidget(button)
        
        self.content_layout.addWidget(meaning_label)
        self.content_layout.addLayout(button_layout)
    
    def show_input_word(self, flashcard: FlashCard):
        """Stage 4: Input word given meaning"""
        # Meaning
        meaning_label = QLabel(flashcard.meaning)
        meaning_label.setAlignment(Qt.AlignCenter)
        meaning_label.setStyleSheet("font-size: 16px; color: #FFFFFF; margin: 10px; background-color: transparent; border: none;")
        meaning_label.setWordWrap(True)
        
        # Example (if available)
        if flashcard.example:
            example_label = QLabel(f"Example: {flashcard.example}")
            example_label.setAlignment(Qt.AlignCenter)
            example_label.setStyleSheet("font-size: 12px; color: #B0B0B0; margin: 5px; font-style: italic; background-color: transparent; border: none;")
            example_label.setWordWrap(True)
            self.content_layout.addWidget(example_label)
        
        # Input field
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Enter the word...")
        self.answer_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(18, 18, 18, 0.5);
                color: #E0E0E0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #888888;
                background-color: rgba(18, 18, 18, 0.7);
            }
            QLineEdit::placeholder {
                color: #B0B0B0;
            }
        """)
        
        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #888888;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #999999;
            }
            QPushButton:pressed {
                background-color: #777777;
            }
        """)
        
        self.content_layout.addWidget(meaning_label)
        self.content_layout.addWidget(self.answer_input)
        self.content_layout.addWidget(submit_button)
        
        # Connect signals
        submit_button.clicked.connect(lambda: self.check_input_answer(flashcard.word))
        self.answer_input.returnPressed.connect(lambda: self.check_input_answer(flashcard.word))
        
        # Focus on input
        self.answer_input.setFocus()
    
    def get_multiple_choice_meanings_for_stage2(self, flashcard: FlashCard):
        """Get 4 meaning options for Stage 2 multiple choice (1 correct + 3 contextual)"""
        options = [flashcard.meaning]
        
        # Add contextual meanings
        available_meanings = [m for m in self.contextual_meanings if m != flashcard.meaning]
        random.shuffle(available_meanings)
        
        # Add up to 3 contextual meanings
        for meaning in available_meanings[:3]:
            options.append(meaning)
        
        # If not enough meanings, add defaults
        default_meanings = [
            "a common example word",
            "a test meaning for practice",
            "a sample definition",
            "a demonstration phrase",
            "a placeholder meaning"
        ]
        for meaning in default_meanings:
            if len(options) < 4 and meaning not in options:
                options.append(meaning)
        
        # Shuffle options
        random.shuffle(options)
        
        return options[:4]
    
    def get_multiple_choice_options(self, flashcard: FlashCard):
        """Get 4 options for Stage 3 multiple choice (1 correct + 3 contextual)"""
        options = [flashcard.word]
        
        # Add contextual words
        available_words = [w for w in self.contextual_words if w != flashcard.word]
        random.shuffle(available_words)
        
        # Add up to 3 contextual words
        for word in available_words[:3]:
            options.append(word)
        
        # If not enough words, add defaults
        default_words = ["example", "test", "word", "sample", "demo"]
        for word in default_words:
            if len(options) < 4 and word not in options:
                options.append(word)
        
        # Shuffle options
        random.shuffle(options)
        
        return options[:4]
    
    def check_input_answer(self, correct_answer: str):
        """Check input answer (case-insensitive, trimmed)"""
        if hasattr(self, 'answer_input') and self.answer_input:
            user_answer = self.answer_input.text().strip().lower()
            correct_answer = correct_answer.strip().lower()
            
            result = "True" if user_answer == correct_answer else "False"
            self.record_result(result)
        else:
            # If no input available, treat as timeout
            self.record_result("TIMEOUT")
    
    def check_multiple_choice_answer(self, selected_option: str, correct_answer: str):
        """Check multiple choice answer"""
        result = "True" if selected_option == correct_answer else "False"
        self.record_result(result)
    
    def record_result(self, result: str):
        """Record result and move to next flashcard"""
        try:
            if self.current_index < len(self.current_flashcards):
                current_flashcard = self.current_flashcards[self.current_index]
                self.results[current_flashcard.id] = result
                
                # Stop timers
                self.auto_close_timer.stop()
                self.countdown_timer.stop()
                
                # Show feedback for stages 2-4 if user answered (not just Stage 1)
                if current_flashcard.stage_id > 1 and result in ["True", "False"]:
                    self.show_feedback(current_flashcard, result)
                    return
                
                # Move to next flashcard
                self.current_index += 1
                self.show_current_flashcard()
        except Exception as e:
            logger.error(f"Error recording result: {e}")
            # Try to finish the review gracefully
            self.finish_review()
    
    def update_countdown_display(self):
        """Update countdown display every second"""
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.countdown_timer.stop()
            self.timer_label.setText("Auto-close in 0s")
        else:
            self.timer_label.setText(f"Auto-close in {self.remaining_seconds}s")
    
    def handle_timeout(self):
        """Handle auto-close timeout"""
        # Stop countdown timer
        self.countdown_timer.stop()
        
        if self.current_index < len(self.current_flashcards):
            current_flashcard = self.current_flashcards[self.current_index]
            self.results[current_flashcard.id] = "TIMEOUT"
            
            # Early exit: Mark all remaining flashcards as TIMEOUT and show summary
            self.mark_remaining_as_timeout()
            self.show_summary_with_timeout_message()
    
    def start_timer(self):
        """Start auto-close timer and countdown display"""
        self.remaining_seconds = self.timeout_seconds
        self.auto_close_timer.start(self.timeout_seconds * 1000)
        
        # Start countdown display timer (update every second)
        self.countdown_timer.start(1000)
        
        # Update timer display
        self.timer_label.setText(f"Auto-close in {self.remaining_seconds}s")
    
    def mark_remaining_as_timeout(self):
        """Mark all remaining flashcards as TIMEOUT"""
        for i in range(self.current_index + 1, len(self.current_flashcards)):
            remaining_flashcard = self.current_flashcards[i]
            self.results[remaining_flashcard.id] = "TIMEOUT"
            logger.info(f"Marking flashcard {remaining_flashcard.id} ({remaining_flashcard.word}) as TIMEOUT due to early exit")
    
    def show_feedback(self, flashcard: FlashCard, result: str):
        """Show feedback for 1 second after user answers"""
        # Clear content
        self.clear_content()
        
        # Create feedback display
        if result == "True":
            feedback_icon = "✅"
            feedback_text = "Correct!"
            feedback_color = "#00CC00"
        else:
            feedback_icon = "❌"
            feedback_text = "Incorrect!"
            feedback_color = "#CC0000"
            
        # Main feedback
        icon_label = QLabel(feedback_icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 40px; color: {feedback_color}; margin: 10px; background-color: transparent; border: none;")
        
        text_label = QLabel(feedback_text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {feedback_color}; margin: 5px; background-color: transparent; border: none;")
        
        self.content_layout.addWidget(icon_label)
        self.content_layout.addWidget(text_label)
        
        # Show correct answer if wrong
        if result == "False":
            if flashcard.stage_id == 2:
                # Stage 2: Show correct meaning
                correct_label = QLabel(f"Correct answer: {flashcard.meaning}")
            elif flashcard.stage_id == 3:
                # Stage 3: Show correct word
                correct_label = QLabel(f"Correct answer: {flashcard.word}")
            elif flashcard.stage_id == 4:
                # Stage 4: Show correct word
                correct_label = QLabel(f"Correct answer: {flashcard.word}")
            
            correct_label.setAlignment(Qt.AlignCenter)
            correct_label.setStyleSheet("font-size: 12px; color: #E0E0E0; margin: 5px; background-color: transparent; border: none;")
            correct_label.setWordWrap(True)
            self.content_layout.addWidget(correct_label)
        
        # Hide timer during feedback
        self.timer_label.setText("")
        
        # Start 1-second timer for feedback
        self.feedback_timer = QTimer()
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(self.hide_feedback)
        self.feedback_timer.start(1000)  # 1 second
    
    def hide_feedback(self):
        """Hide feedback and move to next flashcard"""
        self.current_index += 1
        self.show_current_flashcard()
    
    def show_summary(self):
        """Show final summary with accuracy and emoji"""
        # Reset modal size for summary
        self.setFixedSize(380, 320)
        
        # Calculate accuracy
        total_reviews = len(self.results)
        correct_answers = sum(1 for result in self.results.values() if result == "True")
        accuracy = (correct_answers / total_reviews * 100) if total_reviews > 0 else 0
        
        # Determine emoji and message based on accuracy
        if accuracy >= 90:
            emoji = "🏆"
            message = "Excellent!"
            color = "#FFD700"
        elif accuracy >= 70:
            emoji = "🎉"
            message = "Great job!"
            color = "#00CC00"
        elif accuracy >= 50:
            emoji = "👍"
            message = "Good work!"
            color = "#FFA500"
        else:
            emoji = "💪"
            message = "Keep practicing!"
            color = "#FF6600"
        
        # Clear content
        self.clear_content()
        
        # Create summary display
        emoji_label = QLabel(emoji)
        emoji_label.setAlignment(Qt.AlignCenter)
        emoji_label.setStyleSheet(f"font-size: 50px; margin: 10px; background-color: transparent; border: none;")
        
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; margin: 5px; background-color: transparent; border: none;")
        
        accuracy_label = QLabel(f"Accuracy: {accuracy:.1f}%")
        accuracy_label.setAlignment(Qt.AlignCenter)
        accuracy_label.setStyleSheet("font-size: 14px; color: #E0E0E0; margin: 5px; background-color: transparent; border: none;")
        
        stats_label = QLabel(f"{correct_answers}/{total_reviews} correct")
        stats_label.setAlignment(Qt.AlignCenter)
        stats_label.setStyleSheet("font-size: 12px; color: #B0B0B0; margin: 5px; background-color: transparent; border: none;")
        
        self.content_layout.addWidget(emoji_label)
        self.content_layout.addWidget(message_label)
        self.content_layout.addWidget(accuracy_label)
        self.content_layout.addWidget(stats_label)
        
        # Update progress
        self.progress_label.setText("Review Complete!")
        self.timer_label.setText("")
        
        # Start 3-second timer for summary
        self.summary_timer = QTimer()
        self.summary_timer.setSingleShot(True)
        self.summary_timer.timeout.connect(self.finish_review)
        self.summary_timer.start(3000)  # 3 seconds
    
    def show_summary_with_timeout_message(self):
        """Show summary with timeout/escape message"""
        # Reset modal size for summary
        self.setFixedSize(380, 320)
        
        # Clear content
        self.clear_content()
        
        # Create timeout message display
        emoji_label = QLabel("⏰")
        emoji_label.setAlignment(Qt.AlignCenter)
        emoji_label.setStyleSheet("font-size: 50px; margin: 10px; background-color: transparent; border: none;")
        
        message_label = QLabel("No worries!")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFA500; margin: 5px; background-color: transparent; border: none;")
        
        info_label = QLabel("Come back when you're ready")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #E0E0E0; margin: 5px; background-color: transparent; border: none;")
        
        self.content_layout.addWidget(emoji_label)
        self.content_layout.addWidget(message_label)
        self.content_layout.addWidget(info_label)
        
        # Update progress
        self.progress_label.setText("Session Paused")
        self.timer_label.setText("")
        
        # Start 3-second timer for summary
        self.summary_timer = QTimer()
        self.summary_timer.setSingleShot(True)
        self.summary_timer.timeout.connect(self.finish_review)
        self.summary_timer.start(3000)  # 3 seconds
    
    def finish_review(self):
        """Finish review session with comprehensive cleanup"""
        logger.info(f"Review session completed with {len(self.results)} results")
        
        # Comprehensive timer cleanup
        self.cleanup_all_timers()
        
        # Clear content to prevent any lingering UI elements
        self.clear_content()
        
        # Reset internal state
        self.current_index = 0
        self.remaining_seconds = 0
        
        # Hide window
        self.hide()
        
        # Emit results
        self.review_completed.emit(self.results)
        
        logger.info("Review session cleanup completed successfully")
    
    def cleanup_all_timers(self):
        """Comprehensive cleanup of all timers"""
        try:
            # Stop main timers
            if hasattr(self, 'auto_close_timer') and self.auto_close_timer:
                self.auto_close_timer.stop()
                
            if hasattr(self, 'countdown_timer') and self.countdown_timer:
                self.countdown_timer.stop()
                
            # Stop feedback timer
            if hasattr(self, 'feedback_timer') and self.feedback_timer:
                self.feedback_timer.stop()
                
            # Stop summary timer
            if hasattr(self, 'summary_timer') and self.summary_timer:
                self.summary_timer.stop()
                
            logger.debug("All timers stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping timers: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            # ESC key pressed - close modal immediately
            self.handle_escape_key()
        else:
            super().keyPressEvent(event)
    
    def handle_escape_key(self):
        """Handle ESC key press - close modal immediately"""
        if self.current_index < len(self.current_flashcards):
            current_flashcard = self.current_flashcards[self.current_index]
            self.results[current_flashcard.id] = "ESCAPE"
            
            # Stop timers
            self.auto_close_timer.stop()
            self.countdown_timer.stop()
            
            # Early exit: Mark all remaining flashcards as TIMEOUT and show summary
            self.mark_remaining_as_timeout()
            self.show_summary_with_timeout_message()
    
    def closeEvent(self, event):
        """Handle window close event with comprehensive cleanup"""
        logger.info("ReviewerModule close event triggered")
        
        # Comprehensive timer cleanup
        self.cleanup_all_timers()
        
        # Clear content to prevent any lingering UI elements
        self.clear_content()
        
        # If review was incomplete, mark remaining as timeout
        if self.current_index < len(self.current_flashcards):
            # Mark current flashcard as TIMEOUT if not already recorded
            if self.current_index < len(self.current_flashcards):
                current_flashcard = self.current_flashcards[self.current_index]
                if current_flashcard.id not in self.results:
                    self.results[current_flashcard.id] = "TIMEOUT"
            
            # Mark all remaining flashcards as TIMEOUT
            self.mark_remaining_as_timeout()
        
        # Emit results if any
        if self.results:
            self.review_completed.emit(self.results)
        
        # Reset state for next session
        self.current_index = 0
        self.remaining_seconds = 0
        
        logger.info("ReviewerModule close event cleanup completed")
        event.accept()