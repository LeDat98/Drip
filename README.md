# Drip - Micro Vocabulary Learning System

🧠 **Drip** is a non-intrusive vocabulary learning system that seamlessly integrates into your work environment, helping busy professionals learn vocabulary through spaced repetition without disrupting their workflow.

## ✨ Features

- **🎯 Microlearning Approach**: 5-10 second interactions that don't disrupt your work
- **🧩 Non-Intrusive Design**: Water droplet-inspired UI that appears as small notifications
- **🧠 Spaced Repetition**: Intelligent algorithms that show words right before you forget them
- **⌨️ Global Hotkeys**: Quick access without switching applications
- **📊 4 Learning Stages**: Progressive difficulty from info display to active recall
- **🔄 Auto-Close**: Tests automatically close if you're busy - no penalty!

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source DripEnv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Recommended way
python launch_drip.py

# Or run directly
python main.py
```

### 3. Start Learning

- **Ctrl+Space**: Create new flashcard
- **Ctrl+Shift+R**: Start manual review session
- **System Tray**: Right-click the blue droplet icon in your system tray

## 🎮 How It Works

### Learning Stages

1. **Stage 1 (New)**: Info display - just shows word, meaning, example
2. **Stage 2 (Learning)**: Input meaning when shown a word
3. **Stage 3 (Reviewing)**: Multiple choice - pick the word from meaning
4. **Stage 4 (Mastered)**: Input word when shown meaning

### Smart Scheduling

- New words appear every **30 minutes**
- Learning words appear every **2 hours**
- Reviewing words appear every **24 hours**
- Mastered words appear every **7 days**

Wrong answers reduce intervals, correct answers increase them.

## 🧪 Testing

```bash
# Run all tests
python test_drip.py

# Test individual GUI components
python test_gui.py create   # Test flashcard creation
python test_gui.py review   # Test review system
```

## 🏗️ Architecture

```
main.py                    # System manager & entry point
├── create_new_flashcard.py   # Flashcard creation UI
├── reviewer_module.py        # Review session UI (4 test types)
├── reviewer_schedule_maker.py # Business logic controller
└── database_manager.py       # Data layer with SRS algorithms
```

## 💡 Philosophy

Drip transforms vocabulary learning from:
- **Active** → **Passive** → **Natural**
- **Disruptive** → **Seamless** → **Invisible**

Just like Slack or Notion become part of your workflow, Drip becomes part of your learning routine.

## 🔧 Troubleshooting

### Testing Hotkeys

If hotkeys don't work, try these debugging steps:

```bash
# Test hotkeys manually
python manual_test.py

# Test with debug logging
python launch_drip.py --debug

# Test simple hotkey detection
python simple_hotkey_test.py
```

### Common Issues

1. **System tray icon not appearing**: Install `python3-dev` and restart
2. **Hotkeys not working**: 
   - Check if running in virtual environment
   - Try running with `sudo` if permission issues
   - Test with `python manual_test.py`
3. **GUI not showing**: Install PyQt5 dependencies: `sudo apt-get install python3-pyqt5`

### Log Files

Check `drip.log` for detailed error information.

## 📈 Tips for Effective Learning

1. **Add words during work**: When you encounter unknown words, quickly add them with Ctrl+Space
2. **Don't force reviews**: Let the auto-close feature work - if you're busy, the word will come back later
3. **Use examples**: Good examples help with context and memory retention
4. **Tag by topic**: Use tags to categorize words (e.g., "work", "tech", "business")

## 🛠️ Development

See `CLAUDE.md` for development guidelines and architecture details.

---

**Happy Learning! 🎓**

*Remember: Learning happens in the gaps between work, not during focused work time.*# Drip
