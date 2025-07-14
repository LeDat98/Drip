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
# Test all 4 reviewer stages independently (GUI-based)
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
│   ├── pre_review_notification.py
│   ├── reviewer_module.py
│   ├── settings_window.py
│   └── modal_style.html
├── utils/              # Utility/service layer
│   └── sound_manager.py
└── tests/              # Test modules
    ├── test_pre_review_notification.py
    └── test_reviewer_stages.py

# Entry points (at root level)
main.py               # System manager and entry point
launch_drip.py        # Application launcher with environment setup

# Data and assets
data/                 # Database and settings storage
assets/sound/         # Audio notification files
```

### Core Components

**main.py** - System manager and entry point
- Manages system tray icon and global hotkeys (Ctrl+Space, Ctrl+Shift+R)
- Handles automatic review scheduling using QTimer
- Coordinates between all modules
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
- Reset to Default functionality
- Settings auto-save to data/drip_settings.json
- ESC key support for quick close

### Learning Stages
1. **New** (stage 1) - Info display with "Got It!" button (only button press advances stage)
2. **Learning** (stage 2) - Multiple choice meaning selection (contextual options)
3. **Reviewing** (stage 3) - Multiple choice word selection (contextual options)
4. **Mastered** (stage 4) - Type the word

### Stage Progression Logic
- **Stage 1**: Only "Got It!" button advances to Stage 2, timeouts keep Stage 1
- **Stage 2-3**: Correct answers advance stage, wrong answers/timeouts/ESC maintain stage
- **Stage 4**: Correct answers stay at Stage 4 with longer intervals (7→10.5→15.75 days), achieving true long-term retention
- **Timeout behavior**: Stage 1 reschedules in 30 minutes, Stage 2-4 use SRS intervals

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
1. **Pre-Review Notification System**: 
   - Ultra-compact modal (260x100px) with smooth slide-down animation
   - 3-field design: message with icon, flashcard count, action buttons
   - User choice: "Let's Go!" or "Not Now" before review starts
   - 5-second auto-close with real-time countdown
   - Positioned at top-right corner to minimize workflow interruption

2. **Sound Notification System**:
   - Custom notification sound (DripSoud3.wav) plays when pre-review modal appears
   - QSound-based audio playback with multiple fallback sounds
   - User-configurable on/off toggle in Settings window
   - Cross-platform audio support (Windows/Linux/macOS)
   - Settings auto-save to drip_settings.json

3. **Settings Management**:
   - New Settings window accessible via system tray menu
   - Dark-themed modal with Alert Settings group
   - Simple checkbox to enable/disable notification sounds
   - Reset to Default functionality
   - ESC key support for quick close

4. **Database Enhancements**:
   - Added 10 AI vocabulary words (algorithm, neural, transformer, etc.)
   - Fixed TIMEOUT logic to preserve next_review_time for better scheduling
   - All stages now handle TIMEOUT/ESC consistently (no artificial delays)
   - Calculate_next_test_interval() optimized with 30-minute max interval to handle new flashcard creation scenarios

5. **Improved User Experience**:
   - Non-intrusive pre-review workflow respects user's current focus
   - Smooth animations with OutCubic easing for natural feel
   - Immediate audio feedback when review opportunity arises
   - User maintains complete control over when to engage with reviews

### Technical Improvements
- **Animation System**: QPropertyAnimation with slide-down effect (300ms)
- **Audio Architecture**: SoundManager singleton with file path prioritization
- **Settings Persistence**: JSON-based configuration with graceful fallbacks
- **Modal Positioning**: Dynamic screen width calculation for consistent placement
- **Thread Safety**: Proper signal/slot connections and cleanup procedures

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
- **src/ui/pre_review_notification.py** - Ultra-compact pre-review modal with slide animation and sound
- **src/utils/sound_manager.py** - Cross-platform audio notification system with QSound
- **src/ui/settings_window.py** - Dark-themed settings UI with alert configuration
- **src/tests/test_pre_review_notification.py** - Comprehensive testing suite for features

### Configuration & Assets  
- **data/drip_settings.json** - User settings persistence (sound preferences, etc.)
- **data/drip.db** - SQLite database for flashcard storage
- **assets/sound/DripSoud1.wav** - Primary notification sound file
- **assets/sound/DripSoud2.wav** - Fallback notification sound file  
- **assets/sound/DripSoud3.wav** - Alternative notification sound file

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

# Reset database (caution: deletes all data)
rm data/drip.db
python -c "from src.database.database_manager import DatabaseManager; DatabaseManager()"
```

## Memories

- **To memorize**: Placeholder memory entry