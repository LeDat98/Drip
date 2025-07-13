import sys
import threading
from typing import Optional
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from pynput import keyboard
import logging

from database_manager import DatabaseManager
from create_new_flashcard import CreateNewFlashcard
from reviewer_schedule_maker import ReviewerScheduleMaker
from settings_window import SettingsWindow
from sound_manager import get_sound_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DripApp(QObject):
    # Signals for thread-safe operations
    show_create_signal = pyqtSignal()
    start_review_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", "System tray is not available on this system.")
            sys.exit(1)
            
        self.app.setQuitOnLastWindowClosed(False)
        
        # Initialize modules
        self.database_manager = DatabaseManager()
        self.reviewer_schedule_maker = ReviewerScheduleMaker(self.database_manager)
        self.create_flashcard_window = None
        self.settings_window = None
        self.sound_manager = get_sound_manager()
        
        # System tray
        self.tray_icon = None
        
        # Timer for automatic reviews
        self.review_timer = QTimer()
        self.review_timer.timeout.connect(self.start_automatic_review)
        
        # Initialize system tray
        self.setup_system_tray()
        
        # Initialize hotkeys
        self.setup_hotkeys()
        
        # Connect signals
        self.show_create_signal.connect(self.show_create_flashcard)
        self.start_review_signal.connect(self.start_manual_review)
        
        # Check for overdue flashcards on startup
        self.check_startup_reviews()
        
        # Show initial notification
        self.tray_icon.showMessage(
            "Drip Vocabulary Learning Started",
            "Press Ctrl+Space to create flashcard, Ctrl+Shift+R for review",
            QSystemTrayIcon.Information,
            3000
        )
        
        logger.info("Drip application initialized successfully")
    
    def setup_system_tray(self):
        """Setup system tray icon and menu using Qt (like flashcard_app.py)"""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Create a simple water drop icon (similar to flashcard_app.py)
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        painter = QPainter(pixmap)
        
        # Draw water drop
        painter.setBrush(QColor(52, 152, 219))  # Blue color
        painter.setPen(QColor(52, 152, 219))
        
        # Main drop (circle)
        painter.drawEllipse(6, 10, 20, 20)
        
        # Drop tail (triangle points)
        from PyQt5.QtGui import QPolygon
        from PyQt5.QtCore import QPoint
        triangle = QPolygon([
            QPoint(16, 2),   # Top point
            QPoint(11, 12),  # Bottom left
            QPoint(21, 12)   # Bottom right
        ])
        painter.drawPolygon(triangle)
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("Drip - Vocabulary Learning\nCtrl+Space: Create flashcard\nCtrl+Shift+R: Review")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Create flashcard action
        create_action = QAction("💧 Create Flashcard", self.app)
        create_action.triggered.connect(self.show_create_flashcard)
        tray_menu.addAction(create_action)
        
        # Start review action
        review_action = QAction("📚 Start Review", self.app)
        review_action.triggered.connect(self.start_manual_review)
        tray_menu.addAction(review_action)
        
        # Separator
        tray_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self.app)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        # Statistics action
        stats_action = QAction("📊 Statistics", self.app)
        stats_action.triggered.connect(self.show_statistics)
        tray_menu.addAction(stats_action)
        
        # Separator
        tray_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("❌ Quit", self.app)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
        logger.info("System tray icon created successfully")
    
    def setup_hotkeys(self):
        """Setup global hotkey using pynput with key state tracking (like Create_flashcard.py)"""
        self.pressed_keys = set()
        
        def on_press(key):
            try:
                # Add key to pressed set
                self.pressed_keys.add(key)
                
                # Check for Ctrl+Space combination
                ctrl_pressed = any(k in self.pressed_keys for k in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r])
                space_pressed = keyboard.Key.space in self.pressed_keys
                
                if ctrl_pressed and space_pressed:
                    logger.info("Ctrl+Space detected - Opening create flashcard")
                    # Emit signal to show window (thread-safe)
                    self.show_create_signal.emit()
                    # Clear pressed keys to prevent repeated triggers
                    self.pressed_keys.clear()
                    return
                
                # Check for Ctrl+Shift+R combination
                shift_pressed = any(k in self.pressed_keys for k in [keyboard.Key.shift_l, keyboard.Key.shift_r])
                r_pressed = any(hasattr(k, 'char') and k.char and k.char.lower() == 'r' for k in self.pressed_keys)
                
                if ctrl_pressed and shift_pressed and r_pressed:
                    logger.info("Ctrl+Shift+R detected - Starting manual review")
                    # Emit signal to start review (thread-safe)
                    self.start_review_signal.emit()
                    # Clear pressed keys to prevent repeated triggers
                    self.pressed_keys.clear()
                    return
                    
            except AttributeError:
                # Handle special keys that don't have char
                pass
        
        def on_release(key):
            try:
                # Remove key from pressed set
                self.pressed_keys.discard(key)
            except AttributeError:
                pass
        
        # Start keyboard listener in separate thread
        def start_listener():
            with keyboard.Listener(
                on_press=on_press,
                on_release=on_release,
                suppress=False
            ) as listener:
                listener.join()
        
        # Start listener thread
        listener_thread = threading.Thread(target=start_listener, daemon=True)
        listener_thread.start()
        
        logger.info("Hotkeys initialized successfully!")
        logger.info("Available hotkeys:")
        logger.info("  Ctrl+Space: Create new flashcard")
        logger.info("  Ctrl+Shift+R: Start manual review")
    
    def show_create_flashcard(self):
        """Show the flashcard creator window (like flashcard_app.py)"""
        try:
            logger.info("Opening create flashcard window...")
            
            if self.create_flashcard_window is None:
                self.create_flashcard_window = CreateNewFlashcard(self.database_manager)
                self.create_flashcard_window.closed.connect(self.on_create_flashcard_closed)
            
            self.create_flashcard_window.show()
            self.create_flashcard_window.raise_()
            self.create_flashcard_window.activateWindow()
            
            logger.info("Create flashcard window opened successfully")
            
        except Exception as e:
            logger.error(f"Failed to show create flashcard window: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def on_create_flashcard_closed(self):
        """Handle CreateNewFlashcard window closed"""
        self.create_flashcard_window = None
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_create_flashcard()
    
    def start_manual_review(self):
        """Start manual review session"""
        try:
            success, next_interval = self.reviewer_schedule_maker.start_review_session()
            
            if success:
                logger.info("Manual review session completed successfully")
                # Reschedule next automatic review
                self.schedule_next_review()
            else:
                logger.info("No flashcards due for review")
                
        except Exception as e:
            logger.error(f"Failed to start manual review: {e}")
    
    def start_automatic_review(self):
        """Start automatic review session (called by timer)"""
        try:
            # Check if review is already in progress
            if self.reviewer_schedule_maker.is_review_in_progress():
                logger.info("Review already in progress, skipping automatic review")
                # Retry after 30 seconds
                self.review_timer.singleShot(30000, self.start_automatic_review)
                return
            
            success, next_interval = self.reviewer_schedule_maker.start_review_session()
            
            if success:
                logger.info("Automatic review session completed")
            
            # Schedule next review regardless of success
            self.schedule_next_review()
            
        except Exception as e:
            logger.error(f"Failed to start automatic review: {e}")
            # Still schedule next review on error
            self.schedule_next_review()
    
    def check_startup_reviews(self):
        """Check for overdue flashcards on startup"""
        try:
            due_flashcards = self.database_manager.get_due_flashcards(limit=1)
            
            if due_flashcards:
                logger.info(f"Found {len(due_flashcards)} overdue flashcards on startup, triggering review")
                # Trigger review after 3 seconds to let UI settle
                self.review_timer.singleShot(3000, self.start_automatic_review)
            else:
                logger.info("No overdue flashcards on startup")
                # Start normal scheduling
                self.schedule_next_review()
                
        except Exception as e:
            logger.error(f"Error checking startup reviews: {e}")
            # Fallback to normal scheduling
            self.schedule_next_review()
    
    def schedule_next_review(self):
        """Schedule next automatic review based on calculated interval"""
        try:
            # Don't check for overdue flashcards here - let the timer run its natural cycle
            # This prevents continuous checking and respects TIMEOUT/ESCAPE cooldowns
            
            # Get next review interval from database manager
            next_interval_minutes = self.database_manager.calculate_next_test_interval()
            
            # Convert to milliseconds for QTimer
            next_interval_ms = next_interval_minutes * 60 * 1000
            
            # Stop current timer and start new one
            self.review_timer.stop()
            self.review_timer.start(next_interval_ms)
            
            logger.info(f"Next review scheduled in {next_interval_minutes} minutes")
            
        except Exception as e:
            logger.error(f"Failed to schedule next review: {e}")
            # Fallback to 30 minutes
            self.review_timer.start(30 * 60 * 1000)
    
    def show_settings(self):
        """Show settings window"""
        try:
            if not self.settings_window:
                self.settings_window = SettingsWindow()
                # Connect settings updated signal
                self.settings_window.settings_updated.connect(self.on_settings_updated)
            
            self.settings_window.show_settings()
            
        except Exception as e:
            logger.error(f"Failed to show settings window: {e}")
    
    def on_settings_updated(self):
        """Handle settings update"""
        logger.info("Settings have been updated")
    
    def show_statistics(self):
        """Show statistics window (placeholder)"""
        logger.info("Statistics window not implemented yet")
    
    def quit_application(self):
        """Quit the entire application"""
        logger.info("Shutting down Drip application")
        
        # Stop timers
        self.review_timer.stop()
        
        # Close any open windows
        if self.create_flashcard_window:
            self.create_flashcard_window.close()
        
        if self.settings_window:
            self.settings_window.close()
        
        # Hide system tray
        self.tray_icon.hide()
        
        # Quit application
        self.app.quit()
        sys.exit(0)
    
    def run(self):
        """Start the application"""
        try:
            logger.info("Starting Drip application")
            return self.app.exec_()
        except Exception as e:
            logger.error(f"Application crashed: {e}")
            return 1

def main():
    """Main entry point"""
    try:
        app = DripApp()
        return app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())