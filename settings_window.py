"""
Settings Window for Drip vocabulary learning system
Handles application settings including sound alerts
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QCheckBox, QGroupBox, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import logging
from sound_manager import get_sound_manager

logger = logging.getLogger(__name__)

class SettingsWindow(QWidget):
    """
    Settings window for configuring application preferences
    """
    
    # Signal emitted when settings are updated
    settings_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.sound_manager = get_sound_manager()
        self.setup_ui()
        self.setup_window_properties()
        self.load_current_settings()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Drip Settings")
        self.setFixedSize(400, 300)
        
        # Create main container widget with dark theme
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(68, 68, 68, 0.95);
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
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.container.setLayout(main_layout)
        
        # Title
        title_label = QLabel("Settings")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #FFFFFF; 
            margin: 0px 0px 10px 0px; 
            background-color: transparent; 
            border: none;
        """)
        main_layout.addWidget(title_label)
        
        # Alert Settings Group
        alert_group = QGroupBox("Alert Settings")
        alert_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #E0E0E0;
                border: 2px solid #444444;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #FFFFFF;
                background-color: rgba(68, 68, 68, 0.95);
            }
        """)
        
        alert_layout = QVBoxLayout()
        alert_layout.setSpacing(10)
        alert_layout.setContentsMargins(15, 15, 15, 15)
        
        # Sound notification checkbox
        self.sound_checkbox = QCheckBox("Enable notification sound for vocabulary reviews")
        self.sound_checkbox.setStyleSheet("""
            QCheckBox {
                color: #E0E0E0;
                font-size: 12px;
                background-color: transparent;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #888888;
                border-radius: 3px;
                background-color: rgba(18, 18, 18, 0.5);
            }
            QCheckBox::indicator:checked {
                background-color: #888888;
                border: 2px solid #AAAAAA;
            }
            QCheckBox::indicator:checked::after {
                content: "✓";
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.sound_checkbox.toggled.connect(self.on_sound_toggled)
        
        alert_layout.addWidget(self.sound_checkbox)
        alert_group.setLayout(alert_layout)
        
        main_layout.addWidget(alert_group)
        
        # Add stretch to push buttons to bottom
        main_layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Reset button
        reset_button = QPushButton("Reset to Default")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #121212;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """)
        reset_button.clicked.connect(self.reset_to_default)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #888888;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #999999;
            }
            QPushButton:pressed {
                background-color: #777777;
            }
        """)
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
    def setup_window_properties(self):
        """Setup window properties"""
        # Frameless window, always on top during settings
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window background color
        self.setStyleSheet("background-color: #676767;")
        
        # Enable key press events
        self.setFocusPolicy(Qt.StrongFocus)
    
    def load_current_settings(self):
        """Load current settings into UI"""
        try:
            # Load sound setting
            self.sound_checkbox.setChecked(self.sound_manager.is_sound_enabled())
            
        except Exception as e:
            logger.error(f"Error loading current settings: {e}")
    
    def on_sound_toggled(self, checked: bool):
        """Handle sound checkbox toggle"""
        try:
            self.sound_manager.set_sound_enabled(checked)
            
            status = "enabled" if checked else "disabled"
            logger.info(f"Sound notifications {status}")
            
            # Emit settings updated signal
            self.settings_updated.emit()
            
        except Exception as e:
            logger.error(f"Error toggling sound setting: {e}")
    
    
    def reset_to_default(self):
        """Reset all settings to default values"""
        try:
            # Ask for confirmation
            reply = QMessageBox.question(
                self, 
                "Reset Settings", 
                "Are you sure you want to reset all settings to default values?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Reset sound setting to default (enabled)
                self.sound_manager.set_sound_enabled(True)
                self.sound_checkbox.setChecked(True)
                
                # Emit settings updated signal
                self.settings_updated.emit()
                
                logger.info("Settings reset to default values")
                
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            QMessageBox.warning(self, "Reset Error", f"Error resetting settings: {e}")
    
    def show_settings(self):
        """Show the settings window"""
        try:
            # Reload current settings
            self.load_current_settings()
            
            # Position at center of screen
            screen = self.screen().availableGeometry()
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2
            )
            
            # Show modal
            self.show()
            self.raise_()
            self.activateWindow()
            
            logger.info("Settings window shown")
            
        except Exception as e:
            logger.error(f"Error showing settings window: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            # ESC key pressed - close settings
            self.close()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Settings window closed")
        event.accept()