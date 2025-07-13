from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QTextEdit, QPushButton, QLabel, QFrame, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import logging

logger = logging.getLogger(__name__)

class CreateNewFlashcard(QWidget):
    closed = pyqtSignal()
    
    def __init__(self, database_manager):
        super().__init__()
        self.database_manager = database_manager
        self.setup_ui()
        self.setup_window_properties()
        self.setup_shortcuts()
        
    def setup_ui(self):
        """Setup the user interface with semi-transparent container"""
        self.setWindowTitle("📚 Vocabulary Flashcard Creator")
        self.setFixedSize(400, 450)
        
        # Variables for dragging window
        self.drag_start_position = None
        
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
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        self.container.setLayout(main_layout)
        
        # Title (draggable area) - modal_style.html color scheme
        title_label = QLabel("📚 Vocabulary Flashcard Creator")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #FFFFFF; margin-bottom: 10px; background-color: transparent; border: none;")
        # Make title draggable
        title_label.mousePressEvent = self.mousePressEvent
        title_label.mouseMoveEvent = self.mouseMoveEvent
        main_layout.addWidget(title_label)
        
        # Word label and input (modal_style.html color scheme)
        word_label = QLabel("Word:")
        word_label.setFont(QFont("Arial", 10, QFont.Bold))
        word_label.setStyleSheet("color: #B0B0B0; background-color: transparent; border: none;")
        main_layout.addWidget(word_label)
        
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter the word...")
        self.word_input.setStyleSheet("""
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
        main_layout.addWidget(self.word_input)
        
        # Meaning label and input
        meaning_label = QLabel("Meaning:")
        meaning_label.setFont(QFont("Arial", 10, QFont.Bold))
        meaning_label.setStyleSheet("color: #B0B0B0; background-color: transparent; border: none;")
        main_layout.addWidget(meaning_label)
        
        self.meaning_input = QTextEdit()
        self.meaning_input.setMaximumHeight(60)
        self.meaning_input.setPlaceholderText("Enter the meaning...")
        self.meaning_input.setStyleSheet("""
            QTextEdit {
                background-color: rgba(18, 18, 18, 0.5);
                color: #E0E0E0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 1px solid #888888;
                background-color: rgba(18, 18, 18, 0.7);
            }
        """)
        main_layout.addWidget(self.meaning_input)
        
        # Example label and input
        example_label = QLabel("Example (optional):")
        example_label.setFont(QFont("Arial", 10, QFont.Bold))
        example_label.setStyleSheet("color: #B0B0B0; background-color: transparent; border: none;")
        main_layout.addWidget(example_label)
        
        self.example_input = QTextEdit()
        self.example_input.setMaximumHeight(45)
        self.example_input.setPlaceholderText("Enter an example sentence...")
        self.example_input.setStyleSheet("""
            QTextEdit {
                background-color: rgba(18, 18, 18, 0.5);
                color: #E0E0E0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 1px solid #888888;
                background-color: rgba(18, 18, 18, 0.7);
            }
        """)
        main_layout.addWidget(self.example_input)
        
        # Tags label and input
        tags_label = QLabel("Tags (comma separated):")
        tags_label.setFont(QFont("Arial", 10, QFont.Bold))
        tags_label.setStyleSheet("color: #B0B0B0; background-color: transparent; border: none;")
        main_layout.addWidget(tags_label)
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("e.g., noun, business, advanced")
        self.tag_input.setStyleSheet("""
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
        main_layout.addWidget(self.tag_input)
        
        # Buttons layout (following Create_flashcard.py style)
        button_layout = QHBoxLayout()
        
        # Save button (modal_style.html color scheme)
        self.save_button = QPushButton("✓ Save")
        self.save_button.setStyleSheet("""
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
        
        # Clear button (modal_style.html color scheme)
        clear_button = QPushButton("⟳ Clear")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #121212;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """)
        
        # Close button (modal_style.html color scheme)
        self.cancel_button = QPushButton("✖ Close")
        self.cancel_button.setStyleSheet("""
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
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Status label (modal_style.html color scheme)
        self.status_label = QLabel("📖 Ready to create flashcard")
        self.status_label.setStyleSheet("color: #B0B0B0; font-size: 10px; background-color: transparent; border: none;")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Additional styling for clean labels
        self.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                outline: none;
            }
        """)
        
        # Connect signals
        self.save_button.clicked.connect(self.save_flashcard)
        clear_button.clicked.connect(self.clear_inputs)
        self.cancel_button.clicked.connect(self.close)
        
    def setup_window_properties(self):
        """Setup window properties with semi-transparent background"""
        # Frameless window with transparency support
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window background color to match modal_style.html
        self.setStyleSheet("background-color: #676767;")
        
        # Make window draggable
        self.mouse_pressed = False
        self.mouse_position = None
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Auto-focus on word field when opened
        self.word_input.setFocus()
        
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.mouse_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.mouse_pressed and self.mouse_position:
            self.move(event.globalPos() - self.mouse_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.mouse_pressed = False
        self.mouse_position = None
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.save_flashcard()
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Space:
            self.close()
        else:
            super().keyPressEvent(event)
    
    def validate_form(self):
        """Validate form fields"""
        word = self.word_input.text().strip()
        meaning = self.meaning_input.text().strip()
        
        if not word:
            QMessageBox.warning(self, "Validation Error", "Word field is required!")
            self.word_input.setFocus()
            return False
        
        if not meaning:
            QMessageBox.warning(self, "Validation Error", "Meaning field is required!")
            self.meaning_input.setFocus()
            return False
        
        return True
    
    def clear_inputs(self):
        """Clear all input fields (following Create_flashcard.py style)"""
        self.word_input.clear()
        self.meaning_input.clear()
        self.example_input.clear()
        self.tag_input.clear()
        self.word_input.setFocus()
    
    def save_flashcard(self):
        """Save flashcard to database (following Create_flashcard.py style)"""
        try:
            word = self.word_input.text().strip()
            meaning = self.meaning_input.toPlainText().strip()
            example = self.example_input.toPlainText().strip()
            tags = self.tag_input.text().strip()
            
            if not word or not meaning:
                QMessageBox.warning(self, "Warning", "Please fill in both Word and Meaning fields!")
                return
            
            # Process tags
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
            
            # Create flashcard data
            flashcard_data = {
                'word': word,
                'meaning': meaning,
                'example': example,
                'tag': ', '.join(tag_list) if tag_list else ''
            }
            
            # Save to database
            flashcard_id = self.database_manager.create_flashcard(flashcard_data)
            
            if flashcard_id:
                logger.info(f"Flashcard created successfully with ID: {flashcard_id}")
                
                # Clear inputs
                self.clear_inputs()
                
                # Update status with success message
                from datetime import datetime
                self.status_label.setText(f"📖 Flashcard saved! (Last: {datetime.now().strftime('%H:%M:%S')})")
                
                # Focus back to word input
                self.word_input.setFocus()
                
            else:
                QMessageBox.critical(self, "Error", "Failed to create flashcard!")
                
        except Exception as e:
            logger.error(f"Error saving flashcard: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save flashcard: {str(e)}")
    
    def show(self):
        """Show the flashcard window (following Create_flashcard.py style)"""
        super().show()
        self.raise_()
        self.activateWindow()
        
        # Center window on screen (like Create_flashcard.py)
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
        
        # Focus on word input
        self.word_input.setFocus()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.closed.emit()
        event.accept()