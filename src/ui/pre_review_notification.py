from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QFont
import logging
from src.utils.sound_manager import get_sound_manager

logger = logging.getLogger(__name__)

class PreReviewNotification(QWidget):
    """
    Pre-review notification modal that appears before main review session.
    Gives users choice to start review now or postpone it.
    """
    
    # Signals
    review_accepted = pyqtSignal()  # User clicked "Let's Go!"
    review_declined = pyqtSignal()  # User clicked "Not Now" or timeout/ESC
    
    def __init__(self, flashcard_count: int = 0):
        super().__init__()
        self.flashcard_count = flashcard_count
        self.setup_ui()
        self.setup_window_properties()
        
        # Auto-close timer (5 seconds)
        self.auto_close_timer = QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.handle_timeout)
        
        # Countdown timer for display update
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown_display)
        self.remaining_seconds = 5
        
        # Animation for slide-down effect
        self.slide_animation = None
        
        # Sound manager for notification sound
        self.sound_manager = get_sound_manager()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Review Ready")
        self.setFixedSize(260, 100)
        
        # Create main container widget with modal_style.html color scheme
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(68, 68, 68, 0.92);
                border: 1px solid #444444;
                border-radius: 5px;
            }
        """)
        
        # Main layout for the window
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.container)
        self.setLayout(window_layout)
        
        # Content layout inside container - ultra-compact 3-field design
        main_layout = QVBoxLayout()
        main_layout.setSpacing(4)  # Reduced from 8 to 4
        main_layout.setContentsMargins(10, 8, 10, 8)  # Reduced margins
        self.container.setLayout(main_layout)
        
        # Field 1: Message with icon - more compact
        message_layout = QHBoxLayout()
        message_layout.setSpacing(4)  # Reduced from 6 to 4
        
        icon_label = QLabel("📚")
        icon_label.setStyleSheet("font-size: 14px; background-color: transparent; border: none;")
        
        message_text = "Time for vocabulary review!"
        message_label = QLabel(message_text)
        message_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #FFFFFF; background-color: transparent; border: none;")
        
        message_layout.addWidget(icon_label)
        message_layout.addWidget(message_label)
        message_layout.addStretch()
        
        # Field 2: Flashcard count with countdown - tighter
        count_layout = QHBoxLayout()
        count_layout.setSpacing(6)  # Reduced from 8 to 6
        
        if self.flashcard_count > 0:
            count_text = f"{self.flashcard_count} flashcard{'s' if self.flashcard_count > 1 else ''} ready"
        else:
            count_text = "Ready to practice"
            
        self.count_label = QLabel(count_text)
        self.count_label.setStyleSheet("font-size: 9px; color: #B0B0B0; background-color: transparent; border: none;")
        
        # Countdown timer label
        self.timer_label = QLabel("")
        self.timer_label.setStyleSheet("font-size: 8px; color: #888888; background-color: transparent; border: none;")
        
        count_layout.addWidget(self.count_label)
        count_layout.addStretch()
        count_layout.addWidget(self.timer_label)
        
        # Field 3: Buttons - much smaller
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)  # Reduced from 8 to 6
        
        # Not Now button - much smaller
        self.not_now_button = QPushButton("Not Now")
        self.not_now_button.setStyleSheet("""
            QPushButton {
                background-color: #B0B0B0;
                color: #121212;
                border: none;
                padding: 2px 8px;
                border-radius: 2px;
                font-weight: bold;
                font-size: 9px;
                min-width: 40px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #C0C0C0;
            }
            QPushButton:pressed {
                background-color: #A0A0A0;
            }
        """)
        self.not_now_button.clicked.connect(self.decline_review)
        
        # Let's Go button - much smaller
        self.lets_go_button = QPushButton("Let's Go!")
        self.lets_go_button.setStyleSheet("""
            QPushButton {
                background-color: #888888;
                color: #ffffff;
                border: none;
                padding: 2px 8px;
                border-radius: 2px;
                font-weight: bold;
                font-size: 9px;
                min-width: 40px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #999999;
            }
            QPushButton:pressed {
                background-color: #777777;
            }
        """)
        self.lets_go_button.clicked.connect(self.accept_review)
        
        # Add buttons to layout
        button_layout.addWidget(self.not_now_button)
        button_layout.addWidget(self.lets_go_button)
        
        # Add all fields to main layout
        main_layout.addLayout(message_layout)   # Field 1
        main_layout.addLayout(count_layout)     # Field 2  
        main_layout.addLayout(button_layout)    # Field 3
        
        # Make Let's Go button default focus
        self.lets_go_button.setDefault(True)
        self.lets_go_button.setFocus()
        
    def setup_window_properties(self):
        """Setup window properties according to specifications"""
        # Frameless window, always on top, no focus grab
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window background color to match modal_style.html
        self.setStyleSheet("background-color: #676767;")
        
        # Enable key press events
        self.setFocusPolicy(Qt.StrongFocus)
        
    def show_notification(self):
        """Show the notification modal with slide-down animation"""
        try:
            # Calculate final position (close to top-right corner)
            final_x = self.get_screen_width() - 280  # Adjusted for new width
            final_y = 20
            
            # Set initial position (above screen)
            initial_y = -self.height() - 20
            self.move(final_x, initial_y)
            
            # Show modal (initially hidden above screen)
            self.show()
            self.raise_()
            
            # Create slide-down animation
            self.slide_animation = QPropertyAnimation(self, b"geometry")
            self.slide_animation.setDuration(300)  # 300ms for smooth but not slow animation
            self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)  # Smooth deceleration
            
            # Set start and end geometry
            start_rect = QRect(final_x, initial_y, self.width(), self.height())
            end_rect = QRect(final_x, final_y, self.width(), self.height())
            
            self.slide_animation.setStartValue(start_rect)
            self.slide_animation.setEndValue(end_rect)
            
            # Start animation and then activate/focus
            self.slide_animation.finished.connect(self.on_animation_finished)
            self.slide_animation.start()
            
            # Play notification sound when modal appears
            self.sound_manager.play_notification()
            
            # Start countdown after a brief delay to let animation start
            QTimer.singleShot(100, self.start_countdown)
            
            logger.info(f"Pre-review notification shown with slide animation for {self.flashcard_count} flashcards")
            
        except Exception as e:
            logger.error(f"Error showing pre-review notification: {e}")
            # Fallback to simple show if animation fails
            self.move(self.get_screen_width() - 280, 20)
            self.show()
            self.start_countdown()
    
    def on_animation_finished(self):
        """Called when slide-down animation finishes"""
        try:
            self.activateWindow()
            self.lets_go_button.setFocus()
        except Exception as e:
            logger.error(f"Error in animation finished handler: {e}")
    
    def get_screen_width(self):
        """Get screen width for positioning"""
        try:
            from PyQt5.QtWidgets import QApplication
            return QApplication.desktop().screenGeometry().width()
        except:
            return 1920  # Default fallback
    
    def start_countdown(self):
        """Start countdown timer"""
        self.remaining_seconds = 5
        self.auto_close_timer.start(5000)  # 5 seconds
        
        # Start countdown display timer (update every second)
        self.countdown_timer.start(1000)
        
        # Update timer display
        self.update_countdown_display()
    
    def update_countdown_display(self):
        """Update countdown display every second"""
        if self.remaining_seconds > 0:
            self.timer_label.setText(f"Auto-close in {self.remaining_seconds}s")
            self.remaining_seconds -= 1
        else:
            self.countdown_timer.stop()
            self.timer_label.setText("Auto-closing...")
    
    def handle_timeout(self):
        """Handle auto-close timeout - treat as decline"""
        logger.info("Pre-review notification timed out")
        self.decline_review()
    
    def accept_review(self):
        """User clicked Let's Go! - start review"""
        logger.info("User accepted review session")
        self.cleanup_and_close()
        self.review_accepted.emit()
    
    def decline_review(self):
        """User clicked Not Now or timeout/ESC - postpone review"""
        logger.info("User declined review session")
        self.cleanup_and_close()
        self.review_declined.emit()
    
    def cleanup_and_close(self):
        """Clean up timers, animation and close modal"""
        try:
            # Stop timers
            if hasattr(self, 'auto_close_timer') and self.auto_close_timer:
                self.auto_close_timer.stop()
                
            if hasattr(self, 'countdown_timer') and self.countdown_timer:
                self.countdown_timer.stop()
            
            # Stop animation if running
            if hasattr(self, 'slide_animation') and self.slide_animation:
                self.slide_animation.stop()
                try:
                    self.slide_animation.finished.disconnect()
                except:
                    pass
                self.slide_animation = None
            
            # Hide modal
            self.hide()
            
            logger.debug("Pre-review notification cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during pre-review notification cleanup: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            # ESC key pressed - decline review
            self.decline_review()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Enter key pressed - accept review
            self.accept_review()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Pre-review notification close event triggered")
        self.cleanup_and_close()
        # Treat close as decline
        self.review_declined.emit()
        event.accept()