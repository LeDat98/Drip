# I. Application Overview

🧠 Introducing “Drip” – A Micro Vocabulary Learning System Integrated into the Work Environment
🎯 Main Goal
Drip aims to address the problem of forgetting vocabulary after learning, targeting office workers and developers — people who work extensively on computers and lack time for traditional studying.

❗ Real-World Problem
Users can't dedicate continuous study time throughout the day.
Learning too many words at once overwhelms short-term memory and leads to fast forgetting if not reviewed at the right time (based on the Ebbinghaus forgetting curve).
Traditional flashcard apps like Anki require proactive access → ineffective for busy people.

✅ Drip’s Proposed Solution
Drip applies the microlearning model with the following core logic:

* Seamlessly inserts mini vocabulary quizzes into the workday, appearing as small, periodic notifications.
* Non-intrusive: If the user doesn’t interact within a few seconds, the test auto-closes.
* Optimal recall timing: Uses spacing algorithms (SRS) so tests appear right before the memory starts to fade.
* Very short interaction time (5–10s/test) to avoid disrupting the workflow.

⚙️ Core Logic (Developer-Friendly)
Each flashcard is a vocabulary data unit (includes: word, meaning, example, memory state).
Tests are displayed as mini-popups (overlays on the screen corner or top).

User interactions:

* Click → answer → update state → reschedule.
* Ignore → test auto-closes → no penalty, just rescheduled.

🧩 Minimal UI Integration – Non-Disruptive
UI resembles a "water droplet" – compact and non-intrusive to the main UI.
Developers should ensure tests don’t interrupt the workflow: no focus capture, no sound, no large popups.

📈 Expected Impact

* Increase frequency of vocabulary exposure without disrupting work.
* Help users form long-term memory through micro-spaced repetition.
* Create an “invisible” learning experience — users don't feel burdened.

💡 Summary
Drip is not a traditional learning app. It’s an intelligent reminder system that integrates into the user’s workflow, shifting learning from active → passive → natural.
The design philosophy is like Slack or Notion — embedded into workflow so that learning can happen even when busy.

---

# II. System Architecture

## Module Role Breakdown:

* **main.py**: System manager and entry point
* **CreateNewFlashcard**: UI module for creating flashcards
* **ReviewerModule**: UI module for displaying tests
* **ReviewerScheduleMaker**: Business logic controller
* **DatabaseManager**: Data access layer with calculation algorithms

---

# III. Core Features

## 0. main.py (System Manager)

This file is the **system manager** and **entry point** that initiates and runs the background application.

### 0.1 Features:

* **System tray icon manager** with menu options: "Create Flashcard", "Start Review", "Settings", "Statistics", "Exit"
* **Global hotkey manager**:

  * `Ctrl+Space`: Launch CreateNewFlashcard
  * `Ctrl+Shift+R`: Launch manual review (ReviewerScheduleMaker)
* **Automatic timer** for ReviewerScheduleMaker based on intervals calculated by DatabaseManager
* **Initialize and manage modules**: DatabaseManager, ReviewerScheduleMaker
* **Graceful shutdown handling** upon application exit

### 0.2 Inputs/Outputs:

* **Inputs**: User actions (hotkeys, system tray), timer events
* **Outputs**: Launch corresponding modules, manage app lifecycle

### 0.3 Dependencies:

* Imports and initializes: DatabaseManager, ReviewerScheduleMaker, CreateNewFlashcard
* Libraries: pystray, pynput for hotkeys, threading, PyQt5

---

## 1. CreateNewFlashcard (UI Module - Input)

A **pure UI module** that displays a flashcard creation form and collects data from the user.

### 1.1 Features:

* **Modal window**: Appears at the top-left corner when triggered by main.py
* **Form fields**: Word (required), Meaning (required), Example (optional), Tag (optional)
* **Keyboard shortcuts**:

  * `Enter`: Save and reset form
  * `Esc` or `Ctrl+Space`: Close modal
* **Window properties**: Frameless, draggable, always on top, non-focus grabbing
* **Auto-focus**: Focuses on the Word field when opened
* **Validation**: Ensures Word and Meaning are not empty

### 1.2 Inputs/Outputs:

* **Input**: Keyboard input
* **Output**: Flashcard dictionary `{word, meaning, example, tag}` sent to DatabaseManager.create\_flashcard()

### 1.3 System Interaction:

* **Triggered by**: main.py (via hotkey or system tray)
* **Calls**: DatabaseManager.create\_flashcard()
* **Does not interact directly with**: ReviewerModule, ReviewerScheduleMaker

---

## 2. ReviewerModule (UI Module - Output)

A **pure UI module** for displaying tests and collecting responses from the user. Works only with data from ReviewerScheduleMaker.

### 2.1 Features:

* **Modal windows**: Displays one test at a time at the top-right of the screen
* **Window properties**: Minimal, no focus grab, auto-close after timeout
* **Auto-close**: Automatically closes if no user response (for all flashcards)

### 4 Test Types for 4 Stages:

#### Stage 1 (New) – Info Display:

* Shows: Word, Meaning, Example, Tag
* Display only — no input required
* Auto-closes after 5–10s

#### Stage 2 (Learning) – Input Meaning:

* Shows: Word, Example (if any)
* Input: User types in the meaning
* Validation: Case-insensitive, whitespace-trimmed comparison

#### Stage 3 (Reviewing) – Multiple Choice:

* Shows: Meaning
* 4 buttons: 1 correct word + 3 random incorrect options
* User selects one answer

#### Stage 4 (Mastered) – Input Word:

* Shows: Meaning, Example (if any)
* Input: User types in the word
* Validation: Case-insensitive, whitespace-trimmed comparison

### 2.2 Inputs/Outputs:

* **Inputs**:

  * List of flashcards from ReviewerScheduleMaker
  * Timeout value (in seconds)
  * List of random words for multiple choice
* **Outputs**: Result dictionary `{flashcard_id: result}` with result = "True"/"False"/"TIMEOUT"

### 2.3 System Interaction:

* **Called by**: ReviewerScheduleMaker.start\_review\_session()
* **Returns results to**: ReviewerScheduleMaker
* **No direct interaction with**: main.py, CreateNewFlashcard, DatabaseManager

---

## 3. ReviewerScheduleMaker (Business Logic Controller)

A **business logic module** orchestrating the review cycle and acting as a controller between DatabaseManager and ReviewerModule.

### 3.1 Features:

#### Feature 1: Orchestrate Review Session

* Gets due flashcards from `DatabaseManager.get_due_flashcards(limit=5)`
* If none, returns early
* Prepares data for ReviewerModule

#### Feature 2: Prepare Review Data

* Gets random words for multiple choice via `get_random_words_for_options()`
* Formats flashcards for ReviewerModule
* Sets timeout (default: 10s per flashcard)

#### Feature 3: Execute Review Session

* Calls `ReviewerModule.start_review()`
* Receives test results

#### Feature 4: Update Results

* Updates flashcard status with `update_flashcard_after_review(id, result)`
* Logs session stats (optional)

#### Feature 5: Schedule Next Session

* Calls `calculate_next_test_interval()`
* Returns interval to main.py for timer

### 3.2 Inputs/Outputs:

* **Inputs**: Triggered by main.py (timer or manual)
* **Outputs**:

  * Session result (success/failure)
  * Next review interval (minutes) for main.py

### 3.3 System Interaction:

* **Called by**: main.py (by timer or hotkey)
* **Calls**: DatabaseManager (for data), ReviewerModule (for UI)
* **Returns result to**: main.py

---

## 4. DatabaseManager (Data Access Layer)

The **data access layer** with all database interactions and algorithm implementations. This is the only module directly interacting with SQLite.

### 4.1 Database Schema:

```sql
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    meaning TEXT NOT NULL, 
    example TEXT,
    tag TEXT,
    stage_id INTEGER NOT NULL DEFAULT 1,
    correct BOOLEAN DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_reviewed_at TIMESTAMP DEFAULT NULL,
    next_review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    review_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    wrong_count INTEGER DEFAULT 0,
    priority_score REAL DEFAULT 0,
    interval_hours REAL DEFAULT 0.5,
    
    CHECK (stage_id IN (1, 2, 3, 4))
);
```

### 4.2 Core Functions:

* `create_flashcard(flashcard_data)`: Create new flashcard
* `get_due_flashcards(limit=5)`: Get flashcards due for review
* `update_flashcard_after_review(id, result)`: Update review result
* `get_random_words_for_options(exclude_id, count=3)`: Get distractor words
* `calculate_next_test_interval()`: Compute interval for next review session

### 4.3 Algorithms:

#### Priority Algorithm (in `get_due_flashcards`):

```python
def _calculate_priority_score(flashcard):
    # Stage priority: 1=100, 2=80, 3=60, 4=40
    # + Overdue bonus (max 50)
    # + Wrong answer penalty (30) 
    # + New flashcard bonus (20)
```

#### Interval Algorithm (in `update_flashcard_after_review`):

```python
def _calculate_next_interval(flashcard, result):
    # Base intervals: 1=0.5h, 2=2h, 3=24h, 4=168h
    # True: multiply by 2.0 (stage 1-2) or 1.5 (stage 3-4)
    # False: multiply by 0.5
    # TIMEOUT: keep same
```

### 4.4 System Interaction:

* **Called by**: CreateNewFlashcard, ReviewerScheduleMaker
* **Does not call**: Any other module (pure data layer)

---

# IV. Data Flow

```
User Input (Hotkey) 
    ↓
main.py (System Manager)
    ↓
CreateNewFlashcard (UI) → DatabaseManager (Data)
    ↑                         ↓
ReviewerScheduleMaker (Controller)
    ↓                         ↑  
ReviewerModule (UI) ←─────────┘
```

---

# V. Dependencies Summary

* **main.py**: pystray, pynput hotkey, threading, timer
* **CreateNewFlashcard**: PyQt5, validation logic
* **ReviewerModule**: PyQt5, UI components
* **ReviewerScheduleMaker**: Business logic only
* **DatabaseManager**: sqlite3, datetime, algorithms

---

# VI. Error Handling

* Each module has its own exception handling
* Database errors are handled in DatabaseManager
* UI errors are handled in their respective UI modules
* main.py includes a global exception handler to prevent crashes

---

Make it look professional but simple 