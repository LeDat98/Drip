# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Drip is a micro vocabulary learning system that integrates into the user's work environment. It displays non-intrusive flashcard reviews as periodic notifications using a spaced repetition system (SRS). The application runs in the background with a system tray icon and uses global hotkeys for quick access.

## Github Repo link (no change it)
'https://github.com/LeDat98/Drip.git'
## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source DripEnv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Main entry point (recommended)
python launch_drip.py

# Debug mode with detailed logging
python launch_drip.py --debug

# Alternative direct launch (not recommended)
python main.py

# Check if dependencies are installed
python -c "import PyQt5, pystray, pynput; print('All dependencies OK')"
```

### Testing and Development
```bash
# Test all 5 reviewer stages independently (GUI-based)
python src/tests/test_reviewer_stages.py

# Test individual components
python -c "from src.ui.create_new_flashcard import CreateNewFlashcard; print('Flashcard creator OK')"
python -c "from src.ui.reviewer_module import ReviewerModule; print('Reviewer module OK')"
python -c "from src.database.database_manager import DatabaseManager; print('Database manager OK')"
python -c "from src.core.reviewer_schedule_maker import ReviewerScheduleMaker; print('Schedule maker OK')"

# Test pre-review notification system (current session feature)
python src/tests/test_pre_review_notification.py

# Test sound notification system (current session feature)  
python -c "from src.utils.sound_manager import get_sound_manager; sm = get_sound_manager(); print(f'Sound enabled: {sm.is_sound_enabled()}'); sm.play_notification()"
```

### Testing Features in src/tests/test_reviewer_stages.py
- **Individual Stage Testing**: Test each stage (1-4) independently
- **Multi-Flashcard Testing**: Test with 5 flashcards in sequence
- **Timeout Scenario Testing**: Test early exit on timeout (short timeouts)
- **ESC Scenario Testing**: Test early exit on ESC key press
- **Results Analysis**: Detailed breakdown of True/False/TIMEOUT/ESCAPE results
- **Interactive GUI**: Visual test controller with buttons for each test scenario

### Testing Pre-Review Notification in src/tests/test_pre_review_notification.py
- **Standalone Notification Testing**: Test notification modal independently
- **Integrated Workflow Testing**: Test full workflow with database integration
- **Empty Database Testing**: Test behavior when no flashcards are due
- **User Interaction Testing**: Test both "Let's Go!" and "Not Now" responses
- **Auto-timeout Testing**: Test 5-second auto-close functionality

### Dependencies
- PyQt5==5.15.9 (GUI framework)
- pystray==0.19.4 (system tray icon)
- pynput==1.7.6 (global hotkeys)
- Pillow==9.5.0 (image processing)

## Architecture

### Project Structure (Organized Package Layout)

```
src/
├── core/               # Business logic layer
│   └── reviewer_schedule_maker.py
├── database/           # Data access layer  
│   └── database_manager.py
├── ui/                 # User interface layer
│   ├── create_new_flashcard.py
│   ├── notification_modal.py
│   ├── pre_review_notification.py
│   ├── reviewer_module.py
│   ├── settings_window.py
│   └── modal_style.html
├── utils/              # Utility/service layer
│   ├── auto_insert_new_word.py
│   └── sound_manager.py
└── tests/              # Test modules
    ├── test_auto_insert.py
    ├── test_pre_review_notification.py
    └── test_reviewer_stages.py

# Entry points (at root level)
main.py               # System manager and entry point
launch_drip.py        # Application launcher with environment setup

# Data and assets
data/                 # Database and settings storage
assets/sound/         # Audio notification files
insert_new_words.json # Vocabulary data for auto-insert
```

### Core Components

**main.py** - System manager and entry point
- Manages system tray icon and global hotkeys (Ctrl+Space, Ctrl+Shift+R)
- Handles automatic review scheduling using QTimer
- Auto-insert daily vocabulary checking with precise single-shot timer
- Coordinates between all modules including new notification system
- Imports from organized src.* package structure

**src/database/database_manager.py** - Data access layer
- SQLite database with flashcards table (data/drip.db)
- Implements SRS algorithms for scheduling reviews
- Handles priority scoring and interval calculations
- Database schema includes stage_id (1-4), review statistics, and timing data
- Smart timeout handling: All stages (1-4) preserve next_review_time on TIMEOUT to keep flashcards due for next session
- ESCAPE key results handled separately from timeouts
- Local time usage for created_at and next_review_time (fixes timezone issues)
- New flashcards scheduled 30 minutes after creation (with optimized 30-minute max interval check)
- Contextual word selection: retrieves meanings/words from ±10 ID range for memory reinforcement
- Stage 2 contextual meanings: helps recall related vocabulary learned together
- Stage 3 contextual words: reinforces word associations from similar time periods

**src/ui/create_new_flashcard.py** - Flashcard creation UI
- Modal window for inputting new vocabulary with dark theme
- Fields: word, meaning, example, tag
- Keyboard shortcuts: Enter to save, Esc to close
- Consistent styling with modal_style.html color scheme

**src/ui/pre_review_notification.py** - Pre-review notification modal
- Ultra-compact notification modal (260x100px) that appears before main review session
- 3-field design: message with icon, flashcard count, mini action buttons
- Smooth slide-down animation (300ms) from top of screen for natural appearance
- **Sound notification**: Plays custom audio when modal appears (configurable)
- Shows flashcard count and gives user choice to proceed or postpone
- 5-second auto-close timeout (marks all flashcards as TIMEOUT)
- Two mini action buttons: "Let's Go!" (proceed) and "Not Now" (postpone)
- ESC key support for quick decline, Enter key for quick accept
- Positioned very close to top-right corner (20px from top) to minimize workflow interruption
- OutCubic easing for smooth deceleration animation effect

**src/ui/reviewer_module.py** - Review session UI
- Displays different test types based on flashcard stage (4 stages)
- Dark theme UI matching modal_style.html color scheme
- Stage-specific timeouts (configurable via ReviewerScheduleMaker)
- Countdown timer with real-time updates
- ESC key support for quick exit
- Early exit on timeout/ESC - marks remaining flashcards as TIMEOUT
- Immediate feedback after each answer (1 second for stages 2-4)
- Final summary screen with accuracy rate and motivational emojis (3 seconds)
- Returns results to ReviewerScheduleMaker
- Improved error handling for widget lifecycle management
- Stage 2 uses contextual multiple choice meanings for better memory reinforcement
- Stage 3 uses contextual multiple choice words for enhanced word association
- Adaptive modal sizing: adjusts height based on content (example text, multiple choice options)

**src/core/reviewer_schedule_maker.py** - Business logic controller
- Orchestrates review sessions between database and UI
- Manages pre-review notification workflow and main review execution
- Handles test preparation and result processing
- Handles scheduling of next review intervals
- Configurable stage-specific timeouts (Stage 1: 5s, Stage 2: 15s, Stage 3: 10s, Stage 4: 15s)
- API for timeout management (set_stage_timeout, get_stage_timeout, get_all_stage_timeouts)
- Prepares contextual meanings for Stage 2 and contextual words for Stage 3
- Pre-review notification integration with user choice handling

**src/utils/sound_manager.py** - Audio notification system
- Manages notification sounds with user settings integration
- Primary sound: assets/sound/ audio files via QSound (with multiple fallbacks)
- Supports WAV/OGG/AIFF formats for cross-platform compatibility
- Fallback to system beep if no audio files available
- User-configurable on/off toggle saved in data/drip_settings.json
- Cross-platform audio support (Windows/Linux/macOS)

**src/ui/settings_window.py** - Application settings UI
- Dark-themed settings modal with frameless design
- Alert Settings group with sound notification toggle
- Auto-Insert Settings group with daily count and time configuration
- Dataset completion display showing remaining days to finish vocabulary
- Reset to Default functionality
- Settings auto-save to data/drip_settings.json
- ESC key support for quick close

**src/ui/notification_modal.py** - General-purpose notification system
- Compact modal (280x85px) for various system notifications
- Slide-down animation with smooth OutCubic easing
- Auto-close timer with countdown display
- DripSoud3.wav sound notification support
- Dark theme consistent with existing UI components
- Reusable for vocabulary additions and other notifications

**src/utils/auto_insert_new_word.py** - Daily vocabulary insertion system
- Loads vocabulary from insert_new_words.json (48 words)
- Vietnamese meanings with English examples
- Duplicate word detection and prevention
- Time-based insertion scheduling with precise millisecond timing
- Daily count tracking and completion status
- Integration with database and settings system
- Single-shot timer implementation for exact scheduling

### Learning Stages
1. **New** (stage 1) - Info display with "Got It!" button (only button press advances stage)
2. **Learning** (stage 2) - Multiple choice meaning selection (contextual options)
3. **Reviewing** (stage 3) - Multiple choice word selection (contextual options)
4. **Spelling** (stage 4) - Type the word with spelling hints (30% characters shown)
5. **Mastered** (stage 5) - Type the word without hints

### Stage Progression Logic
- **Stage 1**: Only "Got It!" button advances to Stage 2, timeouts keep Stage 1
- **Stage 2-3**: Correct answers advance stage, wrong answers/timeouts/ESC maintain stage
- **Stage 4**: Correct answers advance to Stage 5, wrong answers maintain Stage 4 (48h→24h intervals)
- **Stage 5**: Correct answers stay at Stage 5 with longer intervals (168h), achieving true long-term retention
- **Timeout behavior**: Stage 1 reschedules in 30 minutes, Stage 2-5 use SRS intervals
- **Partial input rule**: Stage 4-5 with any typed input treat timeout/ESC as wrong answer

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

### Pre-Review Notification Workflow
1. **Trigger**: Automatic timer or manual review request
2. **Check**: Database query for due flashcards
3. **Notification**: Small modal shows with flashcard count and choice buttons
4. **User Decision**: 
   - "Let's Go!" → Proceed to main review session
   - "Not Now" → Mark all flashcards as TIMEOUT, reschedule
   - Auto-timeout (5s) → Same as "Not Now"
   - ESC key → Same as "Not Now"
5. **Result Processing**: Update database and schedule next session

## Key Features

### Global Hotkeys
- `Ctrl+Space` - Open flashcard creation window
- `Ctrl+Shift+R` - Start manual review session

### System Tray Menu
- Create Flashcard
- Start Review  
- **Settings**: Sound alerts toggle, reset to default
- Statistics (placeholder)
- Quit

### Automatic Scheduling
- Uses SRS intervals calculated by DatabaseManager
- Timer-based automatic reviews
- Priority scoring based on stage, overdue status, and performance

## Database Schema

The `flashcards` table tracks:
- Basic flashcard data (word, meaning, example, tag)
- Learning progress (stage_id, review_count, correct_count)
- Scheduling data (next_review_time, interval_hours)
- Priority scoring for review ordering

## Recent Updates (Current Session Summary)

### Major Features Added This Session
1. **Auto-Insert Daily Vocabulary System**:
   - Automatic insertion of vocabulary words from JSON file (`insert_new_words.json`)
   - Time-based insertion with user-configurable schedule (daily count + time)
   - Duplicate prevention and smart word selection from 48 vocabulary words
   - Vietnamese meanings with English examples for better comprehension
   - Settings integration with dataset completion calculation

2. **Modal Notification System**:
   - General-purpose notification modal (`src/ui/notification_modal.py`)
   - Compact design (280x85px) with slide-down animation
   - DripSoud3.wav sound notification on vocabulary insertion
   - Auto-close timer with countdown display
   - Dark theme consistent with existing UI components

3. **Settings Window Enhancements**:
   - Auto-Insert Settings group with enable/disable toggle
   - Daily count spinner (1-50 words per day)
   - Time picker for scheduling insertions
   - Dataset completion display showing days remaining
   - Real-time calculation of learning progress

4. **Precise Timer-Based Auto-Insert**:
   - Single-shot timer with exact millisecond precision for scheduled insertions
   - Calculates exact time until target and triggers at precise moment
   - Fixes issue where app opened before target time wouldn't insert
   - Automatic timer stop after successful insertion (single-shot behavior)
   - Today-only insertion logic prevents duplicate daily entries

5. **Database and JSON Integration**:
   - 48 vocabulary words with Vietnamese meanings and English examples
   - Simplified meaning format (removed explanatory text after "-")
   - Auto-insert tracks existing words to prevent duplicates
   - Contextual word selection respects database state

### Technical Improvements
- **Precise Timer System**: Single-shot timer with millisecond-level accuracy for auto-insert scheduling
- **Timer Bug Fix**: Resolved issue where app opened before target time wouldn't insert words
- **Auto-Insert Architecture**: Calculate exact time until target and trigger at precise moment
- **Modal System**: Reusable notification framework for future features
- **Settings Persistence**: Auto-insert configuration saved to drip_settings.json
- **Animation System**: Smooth slide-down effects with QPropertyAnimation
- **Sound Integration**: DripSoud3.wav notification on vocabulary additions
- **Database Logic**: Smart duplicate detection and word counting

### Session Implementation Details
- **Auto-Insert System**: Complete implementation with 48 Vietnamese vocabulary words
- **Timer Implementation**: Option 2 selected - precise single-shot timer with millisecond accuracy
- **Bug Resolution**: Fixed timer issue where app opened before target time wouldn't insert
- **User Testing**: Implemented per user feedback for minute-level precision vs 5-minute intervals
- **Setting Integration**: Auto-insert enabled at 2:05 AM with 10 words per day (from settings)
- **Notification System**: Modal notification with DripSoud3.wav audio feedback
- **Database Integration**: Smart duplicate detection and word insertion tracking

### Key Implementation Changes (main.py)
```python
# Timer for auto-insert check (precise timing)
self.auto_insert_timer = QTimer()
self.auto_insert_timer.timeout.connect(self.check_auto_insert_words)
self.auto_insert_timer.setSingleShot(True)  # Single shot timer for precise timing

def setup_auto_insert_timer(self):
    """Setup precise timer for auto-insert checking"""
    # Calculate exact milliseconds until target time
    time_until_target = (target_datetime - current_time).total_seconds() * 1000
    # Start timer to trigger exactly at target time
    self.auto_insert_timer.start(int(time_until_target))
```

### Previous Session Features (Maintained)
- **Pre-Review Notification System**: Ultra-compact modal with user choice
- **Sound Notification System**: Configurable audio alerts
- **Settings Management**: Complete settings window with reset functionality

### Previous Session Features (Maintained)
- **Countdown Timer**: Real-time countdown display that actually decreases
- **ESC Key Support**: Press ESC to exit any review modal immediately
- **Early Exit System**: Timeout/ESC on one flashcard closes entire session
- **Immediate Feedback**: 1-second feedback screen for stages 2-4 showing ✅/❌
- **Final Summary**: 3-second summary with accuracy rate and motivational emojis
- **Stage 1 Logic Fix**: Only "Got It!" button advances stage, timeouts keep Stage 1
- **Timeout Management**: Moved to ReviewerScheduleMaker for centralized configuration
- **Database Timezone Fix**: Uses local time instead of UTC for created_at
- **Scheduling Fix**: New flashcards appear after 30 minutes, not immediately
- **Enhanced Testing**: Comprehensive test scenarios for all new features

### Result Types
- **"True"**: Correct answer
- **"False"**: Wrong answer  
- **"TIMEOUT"**: User didn't interact, time ran out
- **"ESCAPE"**: User pressed ESC key

### Feedback System
- **Stages 2-4**: Show ✅ "Correct!" or ❌ "Incorrect!" with correct answer
- **Final Summary**: 
  - 🏆 "Excellent!" (90%+)
  - 🎉 "Great job!" (70-89%)
  - 👍 "Good work!" (50-69%)
  - 💪 "Keep practicing!" (<50%)
- **Timeout/ESC**: ⏰ "No worries! Come back when you're ready"

## Development Workflow

### Getting Started
1. **Clone and setup environment**:
   ```bash
   cd /path/to/Drip
   source DripEnv/bin/activate
   pip install -r requirements.txt
   ```

2. **Test installation**:
   ```bash
   python -c "import PyQt5, pystray, pynput; print('All dependencies OK')"
   ```

3. **Run application**:
   ```bash
   python launch_drip.py --debug
   ```

### Development Cycle
1. **Make changes** to Python files
2. **Test changes** using `python test_reviewer_stages.py`
3. **Test integration** by running `python launch_drip.py --debug`
4. **Check logs** with `tail -f drip.log`
5. **Kill old instance** if needed: `pkill -f "python.*launch_drip.py"`

### Code Style Guidelines
- **File structure**: Follow existing modular architecture
- **Imports**: Group standard library, third-party, and local imports
- **Error handling**: Use try-except blocks with proper logging
- **UI styling**: Follow dark theme color scheme from existing components
- **Threading**: Use PyQt signals for thread-safe communication

### Adding New Features
- **Database changes**: Update `database_manager.py` schema and methods
- **UI components**: Follow existing modal styling patterns
- **Business logic**: Add to `reviewer_schedule_maker.py`
- **System integration**: Modify `main.py` for new hotkeys or tray actions

## Development Notes

### Architecture Patterns
- **Event-driven design**: PyQt signals for thread-safe communication
- **Layered architecture**: Presentation, business logic, data access layers
- **Modular components**: Clear separation of concerns for testability
- **Single application instance**: System tray prevents multiple instances

### Threading Model
- **Main thread**: PyQt5 event loop, UI rendering, database operations
- **Background thread**: Daemon thread for global hotkey monitoring
- **Thread safety**: PyQt signals and set-based key state tracking

### UI & Styling
- All UI components use PyQt5 with custom dark theme styling
- Modal components follow consistent color scheme from `modal_style.html`
- Frameless windows with custom decoration and transparency support
- Always-on-top behavior for non-intrusive overlay

### System Integration
- Global hotkeys use pynput with key state tracking
- System tray icon is created programmatically as a water drop shape
- Logging is configured in launch_drip.py with optional debug mode
- Application uses thread-safe signals for hotkey → UI communication

### Data Management
- Database connections use context managers for proper resource cleanup
- SQLite database file created as `data/drip.db` in data directory
- SRS algorithms with priority scoring and adaptive intervals
- Virtual environment located at `DripEnv/` (activate before development)
- Application logs written to `drip.log` file
- Settings configuration stored in `data/drip_settings.json`
- Audio files located in `assets/sound/` directory (DripSoud1/2/3.wav)

## UI Color Scheme

All modal components use consistent dark theme:
- **Background**: `#676767` (window) / `rgba(68, 68, 68, 0.75)` (container)
- **Borders**: `#444444` with 8px radius
- **Text**: `#FFFFFF` (titles), `#E0E0E0` (content), `#B0B0B0` (labels)
- **Inputs**: `rgba(18, 18, 18, 0.5)` background with `#888888` focus border
- **Buttons**: Save (`#888888`), Clear (`#E0E0E0`), Close (`#B0B0B0`)

## Testing Components

**test_reviewer_stages.py** - Interactive GUI testing for reviewer stages
- Tests all 4 learning stages with sample data
- Stage 1: Info display (word: "hello")
- Stage 2: Multiple choice meaning selection (word: "computer") 
- Stage 3: Multiple choice word selection (word: "beautiful", contextual options)
- Stage 4: Type word (meaning: "process of creating software")
- Provides immediate feedback and results display
- Uses same UI styling as main application
- Multi-flashcard testing with early exit scenarios
- Timeout and ESC key testing with detailed result analysis
- Includes contextual meanings for Stage 2 and contextual words for Stage 3 testing

**test_pre_review_notification.py** - Interactive testing for pre-review notification system
- Tests standalone notification modal with different flashcard counts (260x100px, ultra-compact design)  
- Tests full integrated workflow with database integration
- Tests empty database scenarios and edge cases
- Tests user interaction scenarios: accept, decline, timeout, ESC key
- Tests smooth slide-down animation with 300ms duration
- Visual test controller with informative status updates

## Key Files and Locations

### Core Components
- **src/ui/notification_modal.py** - General-purpose notification modal with slide animation and sound
- **src/utils/auto_insert_new_word.py** - Daily vocabulary insertion system with timer-based scheduling
- **src/ui/settings_window.py** - Enhanced settings UI with auto-insert configuration and dataset completion
- **src/utils/sound_manager.py** - Cross-platform audio notification system with DripSoud3.wav priority
- **src/tests/test_auto_insert.py** - Comprehensive testing suite for auto-insert functionality

### Configuration & Assets  
- **data/drip_settings.json** - User settings persistence (sound, auto-insert preferences)
- **data/drip.db** - SQLite database for flashcard storage
- **insert_new_words.json** - Vocabulary dataset (48 words) with Vietnamese meanings and English examples
- **assets/sound/DripSoud3.wav** - Primary notification sound file for auto-insert
- **assets/sound/DripSoud1.wav** - Fallback notification sound file
- **assets/sound/DripSoud2.wav** - Alternative notification sound file

## Testing and Debugging

### Application Monitoring
```bash
# Check application logs
tail -f drip.log

# Run with debug logging
python launch_drip.py --debug

# Monitor application process
ps aux | grep drip

# Kill running instance if needed  
pkill -f "python.*launch_drip.py"
```

### Database Operations
```bash
# Database inspection (SQLite)
sqlite3 drip.db "SELECT * FROM flashcards LIMIT 10;"

# Check database schema
sqlite3 drip.db ".schema flashcards"

# Monitor due flashcards
sqlite3 drip.db "SELECT word, stage_id, next_review_time, priority_score FROM flashcards WHERE next_review_time <= datetime('now') ORDER BY priority_score DESC;"

# Count flashcards by stage
sqlite3 drip.db "SELECT stage_id, COUNT(*) as count FROM flashcards GROUP BY stage_id;"

# View recent review activity
sqlite3 drip.db "SELECT word, stage_id, last_reviewed_at, correct_count, review_count FROM flashcards WHERE last_reviewed_at IS NOT NULL ORDER BY last_reviewed_at DESC LIMIT 10;"
```

### Component Testing
```bash
# Test auto-insert functionality
python src/tests/test_auto_insert.py

# Test reviewer stages independently
python src/tests/test_reviewer_stages.py

# Test flashcard creation modal
python -c "
import sys
from PyQt5.QtWidgets import QApplication
from src.ui.create_new_flashcard import CreateNewFlashcard
from src.database.database_manager import DatabaseManager

app = QApplication(sys.argv)
db = DatabaseManager()
window = CreateNewFlashcard(db)
window.show()
app.exec_()
"

# Test database operations
python -c "
from src.database.database_manager import DatabaseManager
db = DatabaseManager()
print('Database connection OK')
flashcards = db.get_due_flashcards(limit=5)
print(f'Found {len(flashcards)} due flashcards')
"

# Test auto-insert functionality
python -c "
from src.utils.auto_insert_new_word import AutoInsertNewWord
from datetime import datetime
auto_insert = AutoInsertNewWord()
words = auto_insert.load_words_from_json()
print(f'Loaded {len(words)} words from JSON')
current_time = datetime.now()
result = auto_insert.auto_insert_daily_words(3, current_time.hour, current_time.minute)
print(f'Auto-insert result: {result}')
"

# Test notification modal
python -c "
from src.ui.notification_modal import show_vocabulary_added_notification
import sys
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)
show_vocabulary_added_notification(5, 3)
"
```

### Common Issues and Solutions
```bash
# Fix permission issues (Linux)
sudo chmod +x launch_drip.py

# Fix missing system tray (Linux)
sudo apt-get install python3-dev libdbus-1-dev

# Fix PyQt5 installation issues
pip uninstall PyQt5
pip install PyQt5==5.15.9

# Fix Git authentication in Cursor IDE
./fix_git_env.sh

# Reset database (caution: deletes all data)
rm data/drip.db
python -c "from src.database.database_manager import DatabaseManager; DatabaseManager()"
```

### Git Setup for Cursor IDE
```bash
# If you encounter git push issues in Cursor, run this:
./fix_git_env.sh

# Or manually fix environment:
export GIT_ASKPASS=""
export GIT_TERMINAL_PROMPT=0
git config --global credential.helper store

# Verify setup:
git status
git remote -v
```

## Memories

- **To memorize**: Placeholder memory entry