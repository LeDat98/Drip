"""
Notification Modal for Drip vocabulary learning system
General-purpose notification modal that can be reused for various notifications
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve, QPoint
from PyQt5.QtGui import QFont
import logging
from src.utils.sound_manager import get_sound_manager

logger = logging.getLogger(__name__)

class NotificationModal(QWidget):
    """
    General-purpose notification modal for various system notifications.
    Features auto-close timer, slide-down animation, and sound notification.
    """
    
    # Signals
    notification_closed = pyqtSignal()  # Emitted when notification closes
    
    def __init__(self, title: str = "Notification", message: str = "", 
                 icon: str = "ℹ️", auto_close_seconds: int = 3):
        super().__init__()
        self.title = title
        self.message = message
        self.icon = icon
        self.auto_close_seconds = auto_close_seconds
        self.setup_ui()
        self.setup_window_properties()
        
        # Auto-close timer
        self.auto_close_timer = QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.handle_timeout)
        
        # Countdown timer for display update
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown_display)
        self.remaining_seconds = auto_close_seconds
        
        # Animation for slide-down effect
        self.slide_animation = None
        
        # Sound manager for notification sound
        self.sound_manager = get_sound_manager()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(self.title)
        self.setFixedSize(280, 85)  # More compact size for single message
        
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
        
        # Content layout inside container - more compact
        main_layout = QVBoxLayout()
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(10, 8, 10, 6)
        self.container.setLayout(main_layout)
        
        # Title row with icon - more compact
        title_layout = QHBoxLayout()
        title_layout.setSpacing(4)
        
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 14px; background-color: transparent; border: none;")
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 11px; 
            font-weight: bold; 
            color: #FFFFFF; 
            background-color: transparent; 
            border: none;
        """)
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Message row - combined with title for compactness
        self.message_label = QLabel(self.message)
        self.message_label.setStyleSheet("""
            font-size: 9px; 
            color: #E0E0E0; 
            background-color: transparent; 
            border: none;
            margin-left: 18px;
        """)
        self.message_label.setWordWrap(True)
        
        # Countdown timer row - more compact
        countdown_layout = QHBoxLayout()
        countdown_layout.setSpacing(4)
        
        self.timer_label = QLabel("")
        self.timer_label.setStyleSheet("""
            font-size: 7px; 
            color: #888888; 
            background-color: transparent; 
            border: none;
        """)
        
        # Close button (optional, small)
        self.close_button = QPushButton("✕")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: none;
                padding: 1px;
                font-size: 9px;
                font-weight: bold;
                max-width: 14px;
                max-height: 14px;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
        """)
        self.close_button.clicked.connect(self.close_notification)
        
        countdown_layout.addWidget(self.timer_label)
        countdown_layout.addStretch()
        countdown_layout.addWidget(self.close_button)
        
        # Add all layouts to main layout - more compact
        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.message_label)
        main_layout.addLayout(countdown_layout)
        
    def setup_window_properties(self):
        """Setup window properties"""
        # Frameless window, always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window background color
        self.setStyleSheet("background-color: transparent;")
        
        # Enable key press events
        self.setFocusPolicy(Qt.StrongFocus)
    
    def show_notification(self):
        """Show the notification with slide-down animation and sound"""
        try:
            # Play notification sound
            self.sound_manager.play_notification()
            
            # Position at top-right corner of screen
            screen = self.screen().availableGeometry()
            start_x = screen.width() - self.width() - 20
            start_y = 20
            
            # Set initial position (slightly above final position for slide effect)
            self.move(start_x, start_y - 50)
            
            # Show window
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Setup slide-down animation
            self.slide_animation = QPropertyAnimation(self, b"pos")
            self.slide_animation.setDuration(300)  # 300ms animation
            self.slide_animation.setStartValue(self.pos())
            self.slide_animation.setEndValue(QPoint(start_x, start_y))
            self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # Start animation
            self.slide_animation.start()
            
            # Start countdown timers
            self.remaining_seconds = self.auto_close_seconds
            self.update_countdown_display()
            self.countdown_timer.start(1000)  # Update every second
            self.auto_close_timer.start(self.auto_close_seconds * 1000)
            
            logger.info(f"Notification shown: {self.title}")
            
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
    
    def update_countdown_display(self):
        """Update countdown display"""
        if self.remaining_seconds > 0:
            self.timer_label.setText(f"Auto-close in {self.remaining_seconds}s")
            self.remaining_seconds -= 1
        else:
            self.timer_label.setText("Closing...")
    
    def handle_timeout(self):
        """Handle auto-close timeout"""
        self.close_notification()
    
    def close_notification(self):
        """Close the notification"""
        try:
            # Stop timers
            self.countdown_timer.stop()
            self.auto_close_timer.stop()
            
            # Stop animation if running
            if self.slide_animation and self.slide_animation.state() == QPropertyAnimation.Running:
                self.slide_animation.stop()
            
            # Close window
            self.close()
            
            # Emit signal
            self.notification_closed.emit()
            
            logger.info("Notification closed")
            
        except Exception as e:
            logger.error(f"Error closing notification: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            # ESC key pressed - close notification
            self.close_notification()
        else:
            super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            # Click to close
            self.close_notification()
        else:
            super().mousePressEvent(event)

# Convenience functions for common notification types
def show_info_notification(title: str, message: str, auto_close_seconds: int = 3):
    """Show an info notification"""
    notification = NotificationModal(
        title=title,
        message=message,
        icon="ℹ️",
        auto_close_seconds=auto_close_seconds
    )
    notification.show_notification()
    return notification

def show_success_notification(title: str, message: str, auto_close_seconds: int = 3):
    """Show a success notification"""
    notification = NotificationModal(
        title=title,
        message=message,
        icon="✅",
        auto_close_seconds=auto_close_seconds
    )
    notification.show_notification()
    return notification

def show_vocabulary_added_notification(count: int, auto_close_seconds: int = 4):
    """Show notification for vocabulary added"""
    title = "Vocabulary Added"
    message = f"Added {count} new word{'s' if count > 1 else ''} to your vocabulary list"
    notification = NotificationModal(
        title=title,
        message=message,
        icon="📚",
        auto_close_seconds=auto_close_seconds
    )
    notification.show_notification()
    return notification