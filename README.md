# Drip - Micro Vocabulary Learning System

🧠 **Drip** is a non-intrusive vocabulary learning system that seamlessly integrates into your work environment. It displays periodic flashcard reviews as notifications using a spaced repetition system (SRS), running in the background with a system tray icon and global hotkeys for quick access.

## ✨ Features

- **🎯 Non-Intrusive Design**: Ultra-compact notifications that minimize workflow disruption
- **🧠 Spaced Repetition System**: Advanced SRS algorithms for optimal learning intervals
- **⌨️ Global Hotkeys**: `Ctrl+Space` for flashcard creation, `Ctrl+Shift+R` for manual reviews
- **📊 5 Learning Stages**: Progressive difficulty from interactive learning to mastery verification
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

### 5-Stage Learning Process
1. **New** (Stage 1): Interactive learning - "📚 What does this word mean?" → "Got It!" → meaning reveal (2s auto-advance)
2. **Learning** (Stage 2): Multiple choice meaning selection with contextual options
3. **Reviewing** (Stage 3): Multiple choice word selection with contextual options
4. **Spelling** (Stage 4): Type the word with spelling hints (30% characters shown: e.g., "A L _ _ R _ T H M")
5. **Mastered** (Stage 5): Type the word without hints - pure mastery verification with extended intervals

### Smart Features
- **Pre-Review Notifications**: Ultra-compact modal (260x100px) with user choice
- **Sound Notifications**: Custom notification sounds with user toggle
- **Contextual Learning**: Related words from similar time periods for better retention
- **Timeout Handling**: Smart timeout logic that preserves learning progress
- **Priority Scoring**: Advanced algorithms for optimal review scheduling

## 🧪 Testing & Development

### Component Testing
```bash
# Test all 5 reviewer stages independently (GUI-based)
python src/tests/test_reviewer_stages.py

# Test pre-review notification system
python src/tests/test_pre_review_notification.py

# Test sound notification system
python -c "from src.utils.sound_manager import get_sound_manager; sm = get_sound_manager(); print(f'Sound enabled: {sm.is_sound_enabled()}'); sm.play_notification()"

# Test individual components
python -c "from src.ui.create_new_flashcard import CreateNewFlashcard; print('Flashcard creator OK')"
python -c "from src.ui.reviewer_module import ReviewerModule; print('Reviewer module OK')"
python -c "from src.database.database_manager import DatabaseManager; print('Database manager OK')"
python -c "from src.core.reviewer_schedule_maker import ReviewerScheduleMaker; print('Schedule maker OK')"
```

### Test Features
- **Individual Stage Testing**: Test each stage (1-5) independently
- **Multi-Flashcard Testing**: Test with 5 flashcards in sequence
- **Timeout Scenario Testing**: Test early exit on timeout with short timeouts
- **ESC Scenario Testing**: Test early exit on ESC key press
- **Interactive GUI**: Visual test controller with buttons for each scenario
- **Stage 4 Testing**: Spelling hints with sample word "algorithm"
- **Stage 5 Testing**: No-hints typing with sample word "development"

## 🏗️ Architecture

### Core Components
```
src/
├── core/                         # Business logic layer
│   └── reviewer_schedule_maker.py
├── database/                     # Data access layer  
│   └── database_manager.py
├── ui/                           # User interface layer
│   ├── create_new_flashcard.py  # Flashcard creation UI
│   ├── pre_review_notification.py # Pre-review notification modal
│   ├── reviewer_module.py        # Review session UI (5 test types)
│   └── settings_window.py        # Application settings UI
├── utils/                        # Utility/service layer
│   └── sound_manager.py          # Audio notification system
└── tests/                        # Test modules
    ├── test_pre_review_notification.py
    └── test_reviewer_stages.py

main.py                           # System manager and entry point
launch_drip.py                    # Application launcher with environment setup
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
- **Stage Timeouts**: Stage 1: 20s, Stage 2: 30s, Stage 3: 20s, Stage 4: 30s, Stage 5: 30s
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
sqlite3 data/drip.db "SELECT * FROM flashcards LIMIT 10;"

# Monitor due flashcards
sqlite3 data/drip.db "SELECT word, stage_id, next_review_time, priority_score FROM flashcards WHERE next_review_time <= datetime('now') ORDER BY priority_score DESC;"

# Count flashcards by stage
sqlite3 data/drip.db "SELECT stage_id, COUNT(*) as count FROM flashcards GROUP BY stage_id;"
```

### Common Issues
1. **System tray icon not appearing**: Install `python3-dev libdbus-1-dev` and restart
2. **Hotkeys not working**: Check virtual environment activation and permissions
3. **PyQt5 issues**: Try `pip uninstall PyQt5 && pip install PyQt5==5.15.9`
4. **Database reset**: `rm data/drip.db` (caution: deletes all data)

## 🛠️ Development

### Key Features
- **Event-driven design** with PyQt signals for thread safety
- **Layered architecture** with clear separation of concerns
- **Dark theme UI** with consistent styling across components
- **Cross-platform audio** support (Windows/Linux/macOS)
- **Comprehensive testing** suite for all components

### Recent Enhancements
- **Enhanced 5-Stage Learning System**: Progressive difficulty with spelling hints and mastery verification
- **Interactive Stage 1**: "What does this word mean?" → meaning reveal → auto-advance for active learning
- **Spelling Hints (Stage 4)**: 30% random character hints for gradual typing mastery
- **No-Hints Typing (Stage 5)**: Pure recall for long-term retention verification
- **Smart Intervals**: Stage 4 (48h→24h), Stage 5 (168h→79h) on wrong answers
- **Ultra-compact pre-review notification system** with smooth animations
- **Configurable sound notification system** with cross-platform support
- **Settings management** with JSON persistence and user-friendly UI
- **Enhanced database operations** with local timezone support and contextual learning
- **Organized package structure** with clear separation of concerns

For detailed development guidelines, see `CLAUDE.md`.

---

**Happy Learning! 🎓**

*Drip learns with you - transforming vocabulary acquisition from active effort to passive absorption.*
