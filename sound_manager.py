"""
Sound Manager for Drip vocabulary learning system
Handles notification sounds with settings integration
"""

import logging
import json
import os
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import QStandardPaths

logger = logging.getLogger(__name__)

class SoundManager:
    """
    Manages notification sounds for the application
    """
    
    def __init__(self):
        self.settings_file = "drip_settings.json"
        self.sound_enabled = True
        self.notification_sound = None
        
        # Load settings
        self.load_settings()
        
        # Initialize notification sound
        self.init_notification_sound()
    
    def init_notification_sound(self):
        """Initialize the notification sound"""
        try:
            # CUSTOM SOUND PATHS - Bạn có thể thay đổi đường dẫn tại đây
            custom_sound_paths = [
                # Drip custom notification sounds (WAV format)
                "static/sound/DripSoud3.wav",       # File âm thanh chính của Drip
                "static/sound/DripSoud1.wav",       # File âm thanh dự phòng 1
                "static/sound/DripSoud2.wav",       # File âm thanh dự phòng 2
                
                # Backup custom sounds
                "sounds/notification.wav",           # Đường dẫn tương đối
                "sounds/bell.wav",                   # File chuông
                
                # System sounds (fallback)
                "/usr/share/sounds/alsa/Side_Left.wav",
                "/usr/share/sounds/ubuntu/stereo/message-new-instant.ogg",
                "/System/Library/Sounds/Glass.aiff",  # macOS
            ]
            
            # Try custom sound files first
            for sound_path in custom_sound_paths:
                if os.path.exists(sound_path):
                    try:
                        # Use QSound for WAV and other audio formats
                        self.notification_sound = QSound(sound_path)
                        logger.info(f"Using notification sound: {sound_path}")
                        return
                    except Exception as e:
                        logger.warning(f"Failed to load sound {sound_path}: {e}")
                        continue
            
            # Fallback to system sounds
            if os.name == 'nt':  # Windows
                self.notification_sound = QSound("SystemAsterisk")
                logger.info("Using Windows system sound")
            else:  # Linux/macOS fallback
                self.notification_sound = None
                logger.info("Using system beep as notification sound")
            
        except Exception as e:
            logger.error(f"Error initializing notification sound: {e}")
            self.notification_sound = None
    
    def load_settings(self):
        """Load sound settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.sound_enabled = settings.get('alert_sound_enabled', True)
                    logger.info(f"Loaded sound settings: enabled={self.sound_enabled}")
            else:
                # Create default settings file
                self.save_settings()
                logger.info("Created default sound settings")
                
        except Exception as e:
            logger.error(f"Error loading sound settings: {e}")
            self.sound_enabled = True
    
    def save_settings(self):
        """Save sound settings to file"""
        try:
            settings = {
                'alert_sound_enabled': self.sound_enabled,
                'app_version': '1.0.0',
                'created_at': str(os.path.getmtime(__file__) if os.path.exists(__file__) else 'unknown')
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved sound settings: enabled={self.sound_enabled}")
            
        except Exception as e:
            logger.error(f"Error saving sound settings: {e}")
    
    def play_notification(self):
        """Play notification sound if enabled"""
        try:
            if not self.sound_enabled:
                logger.debug("Sound disabled, skipping notification")
                return
            
            if self.notification_sound:
                # Use QSound for WAV and other formats
                self.notification_sound.play()
                logger.debug("Played notification sound via QSound")
            else:
                # Fallback to system beep
                self.play_system_beep()
                
        except Exception as e:
            logger.error(f"Error playing notification sound: {e}")
            # Last resort: try system beep
            self.play_system_beep()
    
    def play_system_beep(self):
        """Play system beep as fallback"""
        try:
            if os.name == 'nt':  # Windows
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:  # Linux/macOS
                # Use system bell
                os.system('echo -e "\a"')
            
            logger.debug("Played system beep notification")
            
        except Exception as e:
            logger.error(f"Error playing system beep: {e}")
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        self.save_settings()
        
        status = "enabled" if self.sound_enabled else "disabled"
        logger.info(f"Sound notification {status}")
        
        return self.sound_enabled
    
    def set_sound_enabled(self, enabled: bool):
        """Set sound enabled state"""
        if self.sound_enabled != enabled:
            self.sound_enabled = enabled
            self.save_settings()
            
            status = "enabled" if enabled else "disabled"
            logger.info(f"Sound notification {status}")
    
    def is_sound_enabled(self) -> bool:
        """Check if sound is enabled"""
        return self.sound_enabled
    
    def test_notification(self):
        """Test notification sound (for settings)"""
        # Temporarily enable sound for testing
        original_state = self.sound_enabled
        self.sound_enabled = True
        
        try:
            self.play_notification()
            logger.info("Test notification sound played")
        except Exception as e:
            logger.error(f"Error testing notification sound: {e}")
        
        # Restore original state
        self.sound_enabled = original_state

# Global sound manager instance
_sound_manager_instance = None

def get_sound_manager():
    """Get global sound manager instance"""
    global _sound_manager_instance
    if _sound_manager_instance is None:
        _sound_manager_instance = SoundManager()
    return _sound_manager_instance