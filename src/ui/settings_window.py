"""
Settings Window for Drip vocabulary learning system
Handles application settings including sound alerts
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QCheckBox, QGroupBox, QFrame, QMessageBox,
                             QSpinBox, QTimeEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTime
import logging
import json
import os
from src.utils.sound_manager import get_sound_manager

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
        self.setFixedSize(450, 450)
        
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
        
        # Auto-Insert Settings Group
        auto_insert_group = QGroupBox("Auto-Insert Settings")
        auto_insert_group.setStyleSheet("""
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
        
        auto_insert_layout = QVBoxLayout()
        auto_insert_layout.setSpacing(10)
        auto_insert_layout.setContentsMargins(15, 15, 15, 15)
        
        # Enable auto-insert checkbox
        self.auto_insert_checkbox = QCheckBox("Enable daily auto-insert new vocabulary")
        self.auto_insert_checkbox.setStyleSheet("""
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
        self.auto_insert_checkbox.toggled.connect(self.on_auto_insert_toggled)
        
        auto_insert_layout.addWidget(self.auto_insert_checkbox)
        
        # Daily count setting
        count_layout = QHBoxLayout()
        count_label = QLabel("Daily count:")
        count_label.setStyleSheet("""
            color: #E0E0E0;
            font-size: 12px;
            background-color: transparent;
        """)
        
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 50)
        self.count_spinbox.setValue(10)
        self.count_spinbox.setStyleSheet("""
            QSpinBox {
                color: #E0E0E0;
                background-color: rgba(18, 18, 18, 0.5);
                border: 2px solid #888888;
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #888888;
            }
        """)
        self.count_spinbox.valueChanged.connect(self.on_count_changed)
        
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_spinbox)
        count_layout.addStretch()
        
        auto_insert_layout.addLayout(count_layout)
        
        # Dataset completion info
        self.completion_label = QLabel("Dataset completion: Calculating...")
        self.completion_label.setStyleSheet("""
            color: #B0B0B0;
            font-size: 11px;
            font-style: italic;
            background-color: transparent;
            margin-left: 20px;
        """)
        auto_insert_layout.addWidget(self.completion_label)
        
        # Time setting
        time_layout = QHBoxLayout()
        time_label = QLabel("Daily time:")
        time_label.setStyleSheet("""
            color: #E0E0E0;
            font-size: 12px;
            background-color: transparent;
        """)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(7, 0))  # Default 7:00 AM
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                color: #E0E0E0;
                background-color: rgba(18, 18, 18, 0.5);
                border: 2px solid #888888;
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
                min-width: 80px;
            }
            QTimeEdit:focus {
                border: 2px solid #888888;
            }
        """)
        self.time_edit.timeChanged.connect(self.on_time_changed)
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        
        auto_insert_layout.addLayout(time_layout)
        
        auto_insert_group.setLayout(auto_insert_layout)
        main_layout.addWidget(auto_insert_group)
        
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
            
            # Load auto-insert settings
            auto_insert_settings = self.load_auto_insert_settings()
            self.auto_insert_checkbox.setChecked(auto_insert_settings.get('enabled', False))
            self.count_spinbox.setValue(auto_insert_settings.get('daily_count', 10))
            
            # Load time setting
            hour = auto_insert_settings.get('hour', 7)
            minute = auto_insert_settings.get('minute', 0)
            self.time_edit.setTime(QTime(hour, minute))
            
            # Update completion label
            self.update_completion_label()
            
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
    
    def load_auto_insert_settings(self):
        """Load auto-insert settings from file"""
        try:
            if os.path.exists(self.sound_manager.settings_file):
                with open(self.sound_manager.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('auto_insert', {
                        'enabled': False,
                        'daily_count': 10,
                        'hour': 7,
                        'minute': 0
                    })
            else:
                return {
                    'enabled': False,
                    'daily_count': 10,
                    'hour': 7,
                    'minute': 0
                }
        except Exception as e:
            logger.error(f"Error loading auto-insert settings: {e}")
            return {
                'enabled': False,
                'daily_count': 10,
                'hour': 7,
                'minute': 0
            }
    
    def save_auto_insert_settings(self, settings):
        """Save auto-insert settings to file"""
        try:
            # Load existing settings
            existing_settings = {}
            if os.path.exists(self.sound_manager.settings_file):
                with open(self.sound_manager.settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            
            # Update auto-insert settings
            existing_settings['auto_insert'] = settings
            
            # Save back to file
            with open(self.sound_manager.settings_file, 'w', encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved auto-insert settings: {settings}")
            
        except Exception as e:
            logger.error(f"Error saving auto-insert settings: {e}")
    
    def on_auto_insert_toggled(self, checked: bool):
        """Handle auto-insert checkbox toggle"""
        try:
            # Get current settings
            current_settings = self.load_auto_insert_settings()
            current_settings['enabled'] = checked
            
            # Save settings
            self.save_auto_insert_settings(current_settings)
            
            status = "enabled" if checked else "disabled"
            logger.info(f"Auto-insert {status}")
            
            # Emit settings updated signal
            self.settings_updated.emit()
            
        except Exception as e:
            logger.error(f"Error toggling auto-insert setting: {e}")
    
    def on_count_changed(self, value: int):
        """Handle daily count change"""
        try:
            # Get current settings
            current_settings = self.load_auto_insert_settings()
            current_settings['daily_count'] = value
            
            # Save settings
            self.save_auto_insert_settings(current_settings)
            
            logger.info(f"Auto-insert daily count set to {value}")
            
            # Update completion label
            self.update_completion_label()
            
            # Emit settings updated signal
            self.settings_updated.emit()
            
        except Exception as e:
            logger.error(f"Error changing daily count: {e}")
    
    def on_time_changed(self, time):
        """Handle time change"""
        try:
            # Get current settings
            current_settings = self.load_auto_insert_settings()
            current_settings['hour'] = time.hour()
            current_settings['minute'] = time.minute()
            
            # Save settings
            self.save_auto_insert_settings(current_settings)
            
            logger.info(f"Auto-insert time set to {time.hour():02d}:{time.minute():02d}")
            
            # Emit settings updated signal
            self.settings_updated.emit()
            
        except Exception as e:
            logger.error(f"Error changing time: {e}")
    
    def calculate_dataset_completion(self, daily_count: int) -> str:
        """Calculate dataset completion info"""
        try:
            from src.utils.auto_insert_new_word import AutoInsertNewWord
            
            if daily_count <= 0:
                return "Dataset completion: Please set daily count"
            
            # Initialize auto-insert manager
            auto_insert = AutoInsertNewWord()
            
            # Load words from JSON
            words_data = auto_insert.load_words_from_json()
            if not words_data:
                return "Dataset completion: Cannot load vocabulary file"
            
            total_words = len(words_data)
            
            # Count existing words in database
            existing_count = 0
            for word_data in words_data:
                if auto_insert.check_word_exists(word_data.get('word', '')):
                    existing_count += 1
            
            # Calculate remaining words
            remaining_words = total_words - existing_count
            
            if remaining_words <= 0:
                return "Dataset completion: All words learned!"
            
            # Calculate days needed
            import math
            days_remaining = math.ceil(remaining_words / daily_count)
            
            return f"Dataset completion: {days_remaining} days remaining ({remaining_words}/{total_words} words left)"
            
        except Exception as e:
            logger.error(f"Error calculating dataset completion: {e}")
            return "Dataset completion: Calculation error"
    
    def update_completion_label(self):
        """Update the completion label with current settings"""
        try:
            daily_count = self.count_spinbox.value()
            completion_text = self.calculate_dataset_completion(daily_count)
            self.completion_label.setText(completion_text)
            
        except Exception as e:
            logger.error(f"Error updating completion label: {e}")
            self.completion_label.setText("Dataset completion: Update error")
    
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
                
                # Reset auto-insert settings to default
                default_auto_insert = {
                    'enabled': False,
                    'daily_count': 10,
                    'hour': 7,
                    'minute': 0
                }
                self.save_auto_insert_settings(default_auto_insert)
                self.auto_insert_checkbox.setChecked(False)
                self.count_spinbox.setValue(10)
                self.time_edit.setTime(QTime(7, 0))
                
                # Update completion label
                self.update_completion_label()
                
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