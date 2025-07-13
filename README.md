# Drip - Micro Vocabulary Learning System

🧠 **Drip** is a non-intrusive vocabulary learning system that seamlessly integrates into your work environment. It displays periodic flashcard reviews as notifications using a spaced repetition system (SRS), running in the background with a system tray icon and global hotkeys for quick access.

## ✨ Features

- **🎯 Non-Intrusive Design**: Ultra-compact notifications that minimize workflow disruption
- **🧠 Spaced Repetition System**: Advanced SRS algorithms for optimal learning intervals
- **⌨️ Global Hotkeys**: `Ctrl+Space` for flashcard creation, `Ctrl+Shift+R` for manual reviews
- **📊 4 Learning Stages**: Progressive difficulty from info display to active recall
- **🔔 Smart Notifications**: Pre-review notifications with user choice and sound alerts
- **⚙️ Customizable Settings**: Sound notifications, timeouts, and user preferences
- **🔄 Intelligent Scheduling**: Contextual word selection and priority scoring

## 🚀 Quick Start

### Environment Setup
```bash
# Activate virtual environment
source DripEnv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import PyQt5, pystray, pynput; print('All dependencies OK')"
```

### Running the Application
```bash
# Main entry point (recommended)
python launch_drip.py

# Debug mode with detailed logging
python launch_drip.py --debug

# Alternative direct launch (not recommended)
python main.py
```

### Getting Started
- **Ctrl+Space**: Create new flashcard
- **Ctrl+Shift+R**: Start manual review session
- **System Tray**: Right-click the water droplet icon for menu

## 🎮 Learning System

### 4-Stage Learning Process
1. **New** (Stage 1): Info display with "Got It!" button - shows word, meaning, example
2. **Learning** (Stage 2): Multiple choice meaning selection with contextual options
3. **Reviewing** (Stage 3): Multiple choice word selection with contextual options  
4. **Mastered** (Stage 4): Type the word when shown meaning

### Smart Features
- **Pre-Review Notifications**: Ultra-compact modal (260x100px) with user choice
- **Sound Notifications**: Custom notification sounds with user toggle
- **Contextual Learning**: Related words from similar time periods for better retention
- **Timeout Handling**: Smart timeout logic that preserves learning progress
- **Priority Scoring**: Advanced algorithms for optimal review scheduling

## 🧪 Testing & Development

### Component Testing
```bash
# Test all 4 reviewer stages independently (GUI-based)
python test_reviewer_stages.py

# Test pre-review notification system
python test_pre_review_notification.py

# Test sound notification system
python -c "from sound_manager import get_sound_manager; sm = get_sound_manager(); print(f'Sound enabled: {sm.is_sound_enabled()}'); sm.play_notification()"

# Test individual components
python -c "from create_new_flashcard import CreateNewFlashcard; print('Flashcard creator OK')"
python -c "from reviewer_module import ReviewerModule; print('Reviewer module OK')"
python -c "from database_manager import DatabaseManager; print('Database manager OK')"
python -c "from reviewer_schedule_maker import ReviewerScheduleMaker; print('Schedule maker OK')"
```

### Test Features
- **Individual Stage Testing**: Test each stage (1-4) independently
- **Multi-Flashcard Testing**: Test with 5 flashcards in sequence
- **Timeout Scenario Testing**: Test early exit on timeout with short timeouts
- **ESC Scenario Testing**: Test early exit on ESC key press
- **Interactive GUI**: Visual test controller with buttons for each scenario

## 🏗️ Architecture

### Core Components
```
main.py                           # System manager and entry point
├── create_new_flashcard.py       # Flashcard creation UI
├── pre_review_notification.py    # Pre-review notification modal
├── reviewer_module.py            # Review session UI (4 test types)
├── reviewer_schedule_maker.py    # Business logic controller
├── database_manager.py           # Data access layer with SRS algorithms
├── sound_manager.py              # Audio notification system
└── settings_window.py            # Application settings UI
```

### Data Flow
```
User Input → main.py → CreateNewFlashcard → DatabaseManager
                   ↓
ReviewerScheduleMaker ← DatabaseManager
                   ↓
        PreReviewNotification → User Choice
                   ↓                ↓
           (Let's Go)        (Not Now/Timeout)
                   ↓                ↓  
ReviewerModule → Results    Mark as TIMEOUT
                   ↓                ↓
ReviewerScheduleMaker ← ← ← ← ← ← ← ← ←
```

## ⚙️ Configuration

### Dependencies
- PyQt5==5.15.9 (GUI framework)
- pystray==0.19.4 (system tray icon)
- pynput==1.7.6 (global hotkeys)
- Pillow==9.5.0 (image processing)

### Settings
- **Sound Alerts**: Configurable via Settings window
- **Stage Timeouts**: Stage 1: 5s, Stage 2: 15s, Stage 3: 10s, Stage 4: 15s
- **Auto-scheduling**: Uses SRS intervals with priority scoring
- **Audio Files**: Located in `static/sound/` directory

## 🔧 Troubleshooting

### Application Monitoring
```bash
# Check application logs
tail -f drip.log

# Run with debug logging
python launch_drip.py --debug

# Kill running instance if needed  
pkill -f "python.*launch_drip.py"
```

### Database Operations
```bash
# Database inspection
sqlite3 drip.db "SELECT * FROM flashcards LIMIT 10;"

# Monitor due flashcards
sqlite3 drip.db "SELECT word, stage_id, next_review_time, priority_score FROM flashcards WHERE next_review_time <= datetime('now') ORDER BY priority_score DESC;"
```

### Common Issues
1. **System tray icon not appearing**: Install `python3-dev libdbus-1-dev` and restart
2. **Hotkeys not working**: Check virtual environment activation and permissions
3. **PyQt5 issues**: Try `pip uninstall PyQt5 && pip install PyQt5==5.15.9`
4. **Database reset**: `rm drip.db` (caution: deletes all data)

## 🛠️ Development

### Key Features
- **Event-driven design** with PyQt signals for thread safety
- **Layered architecture** with clear separation of concerns
- **Dark theme UI** with consistent styling across components
- **Cross-platform audio** support (Windows/Linux/macOS)
- **Comprehensive testing** suite for all components

### Recent Enhancements
- Ultra-compact pre-review notification system
- Configurable sound notification system
- Settings management with JSON persistence
- Enhanced database operations with local timezone support
- Improved contextual learning with related word selection

For detailed development guidelines, see `CLAUDE.md`.

---

**Happy Learning! 🎓**

*Drip learns with you - transforming vocabulary acquisition from active effort to passive absorption.*
