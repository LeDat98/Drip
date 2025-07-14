from typing import Tuple, List, Optional
import logging
from PyQt5.QtWidgets import QApplication

from src.database.database_manager import DatabaseManager, FlashCard
from src.ui.reviewer_module import ReviewerModule
from src.ui.pre_review_notification import PreReviewNotification

logger = logging.getLogger(__name__)

class ReviewerScheduleMaker:
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager
        self.reviewer_module = None
        self.pre_review_notification = None
        self.current_session_results = {}
        self.pending_flashcards = []
        self.pending_contextual_words = []
        self.pending_contextual_meanings = []
        
        # Timeout settings for each stage (in seconds)
        self.stage_timeouts = {
            1: 20,   # Stage 1: Info display - shorter timeout
            2: 30,  # Stage 2: Input meaning - more time for typing
            3: 20,  # Stage 3: Multiple choice - medium time
            4: 30   # Stage 4: Input word - more time for typing
        }
        self.default_timeout = 10  # Fallback timeout
        
    def start_review_session(self) -> Tuple[bool, int]:
        """
        Start a review session with pre-review notification
        
        Returns:
            Tuple[bool, int]: (success, next_interval_minutes)
        """
        try:
            # Feature 1: Orchestrate Review Session
            due_flashcards = self.database_manager.get_due_flashcards(limit=5)
            
            if not due_flashcards:
                logger.info("No flashcards due for review")
                return False, self.database_manager.calculate_next_test_interval()
            
            logger.info(f"Starting review session with {len(due_flashcards)} flashcards")
            
            # Feature 2: Prepare Review Data
            contextual_words = self.prepare_contextual_words(due_flashcards)
            contextual_meanings = self.prepare_contextual_meanings(due_flashcards)
            
            # Store pending session data
            self.pending_flashcards = due_flashcards
            self.pending_contextual_words = contextual_words
            self.pending_contextual_meanings = contextual_meanings
            
            # Feature 3: Show Pre-Review Notification
            return self.show_pre_review_notification(len(due_flashcards))
            
        except Exception as e:
            logger.error(f"Error in review session: {e}")
            return False, self.database_manager.calculate_next_test_interval()
    
    def prepare_contextual_words(self, flashcards: List[FlashCard]) -> List[str]:
        """
        Feature 2: Prepare contextual words for Stage 3 multiple choice questions
        
        Args:
            flashcards: List of flashcards for the session
            
        Returns:
            List of contextual words for Stage 3 multiple choice options
        """
        try:
            # Get contextual words for Stage 3 flashcards
            contextual_words = []
            
            for flashcard in flashcards:
                if flashcard.stage_id == 3:  # Only needed for stage 3 (multiple choice word)
                    words = self.database_manager.get_contextual_words_for_stage3(
                        exclude_id=flashcard.id, 
                        count=5  # Get extra words for better randomization
                    )
                    contextual_words.extend(words)
            
            # Remove duplicates and return
            return list(set(contextual_words))
            
        except Exception as e:
            logger.error(f"Error preparing contextual words: {e}")
            return []
    
    def prepare_contextual_meanings(self, flashcards: List[FlashCard]) -> List[str]:
        """
        Feature 2: Prepare contextual meanings for Stage 2 multiple choice questions
        
        Args:
            flashcards: List of flashcards for the session
            
        Returns:
            List of contextual meanings for Stage 2 multiple choice options
        """
        try:
            # Get contextual meanings for Stage 2 flashcards
            contextual_meanings = []
            
            for flashcard in flashcards:
                if flashcard.stage_id == 2:  # Only needed for stage 2 (multiple choice meaning)
                    meanings = self.database_manager.get_contextual_meanings_for_stage2(
                        exclude_id=flashcard.id, 
                        count=5  # Get extra meanings for better randomization
                    )
                    contextual_meanings.extend(meanings)
            
            # Remove duplicates and return
            return list(set(contextual_meanings))
            
        except Exception as e:
            logger.error(f"Error preparing contextual meanings: {e}")
            return []
    
    def show_pre_review_notification(self, flashcard_count: int) -> Tuple[bool, int]:
        """
        Show pre-review notification modal
        
        Args:
            flashcard_count: Number of flashcards ready for review
            
        Returns:
            Tuple[bool, int]: (session_started, next_interval_minutes)
        """
        try:
            # Clean up any existing notification
            if self.pre_review_notification:
                try:
                    self.pre_review_notification.review_accepted.disconnect()
                    self.pre_review_notification.review_declined.disconnect()
                except:
                    pass
                self.pre_review_notification.close()
                self.pre_review_notification = None
            
            # Create new notification instance
            self.pre_review_notification = PreReviewNotification(flashcard_count)
            
            # Connect signals
            self.pre_review_notification.review_accepted.connect(self.proceed_with_review)
            self.pre_review_notification.review_declined.connect(self.postpone_review)
            
            # Show notification
            self.pre_review_notification.show_notification()
            
            # Process Qt events to handle the notification
            app = QApplication.instance()
            if app:
                import time
                start_time = time.time()
                timeout = 10  # 10 seconds max wait for notification response
                
                while (self.pre_review_notification and 
                       self.pre_review_notification.isVisible() and 
                       time.time() - start_time < timeout):
                    app.processEvents()
                    time.sleep(0.1)
                
                # Check if we have results from the main review
                if self.current_session_results:
                    # Update flashcard results
                    self.update_flashcard_results(self.current_session_results)
                    next_interval = self.database_manager.calculate_next_test_interval()
                    logger.info(f"Review session completed successfully. Next session in {next_interval} minutes")
                    return True, next_interval
                else:
                    # Review was declined or timed out
                    next_interval = self.database_manager.calculate_next_test_interval()
                    logger.info(f"Review session postponed. Next session in {next_interval} minutes")
                    return False, next_interval
            else:
                logger.error("No QApplication instance found")
                return False, self.database_manager.calculate_next_test_interval()
                
        except Exception as e:
            logger.error(f"Error showing pre-review notification: {e}")
            return False, self.database_manager.calculate_next_test_interval()
    
    def proceed_with_review(self):
        """
        User accepted review - proceed with main review session
        """
        try:
            logger.info("User accepted review - starting main review session")
            
            # Execute the main review session with pending data
            results = self.execute_review_session(
                self.pending_flashcards, 
                self.pending_contextual_words, 
                self.pending_contextual_meanings
            )
            
            if results is not None:
                self.current_session_results = results
            else:
                logger.warning("Main review session failed after user acceptance")
                self.current_session_results = {}
                
        except Exception as e:
            logger.error(f"Error proceeding with review: {e}")
            self.current_session_results = {}
    
    def postpone_review(self):
        """
        User declined review or notification timed out - mark all as timeout
        """
        try:
            logger.info("User declined review or notification timed out")
            
            # Mark all pending flashcards as TIMEOUT
            timeout_results = {}
            for flashcard in self.pending_flashcards:
                timeout_results[flashcard.id] = "TIMEOUT"
            
            self.current_session_results = timeout_results
            
            # Clear pending data
            self.pending_flashcards = []
            self.pending_contextual_words = []
            self.pending_contextual_meanings = []
            
        except Exception as e:
            logger.error(f"Error postponing review: {e}")
            self.current_session_results = {}
    
    def execute_review_session(self, flashcards: List[FlashCard], 
                              contextual_words: List[str], contextual_meanings: List[str]) -> Optional[dict]:
        """
        Feature 3: Execute the review session using ReviewerModule
        
        Args:
            flashcards: List of flashcards to review
            contextual_words: Contextual words for Stage 3 multiple choice
            contextual_meanings: Contextual meanings for Stage 2 multiple choice
            
        Returns:
            Dictionary of results {flashcard_id: result} or None if failed
        """
        try:
            # Always create a fresh ReviewerModule instance to avoid state pollution
            if self.reviewer_module:
                logger.info("Closing previous reviewer instance to ensure clean state")
                self.reviewer_module.close()
                # Disconnect any existing signals to prevent memory leaks
                try:
                    self.reviewer_module.review_completed.disconnect()
                except:
                    pass  # Ignore if already disconnected
                self.reviewer_module = None
            
            # Create new instance for this session
            self.reviewer_module = ReviewerModule()
            logger.info("Created fresh ReviewerModule instance for new session")
            
            # Set up result tracking
            self.current_session_results = {}
            
            # Connect signal to handle results
            self.reviewer_module.review_completed.connect(self.on_review_completed)
            
            # Start the review session with stage-specific timeouts
            self.reviewer_module.start_review(flashcards, self.stage_timeouts, contextual_words, contextual_meanings)
            
            # Process Qt events to handle the review session
            # This is a simplified approach - in a real app, you'd use proper async handling
            app = QApplication.instance()
            if app:
                # Wait for review to complete (with timeout)
                import time
                start_time = time.time()
                # Calculate max timeout based on longest stage timeout
                max_stage_timeout = max(self.stage_timeouts.values())
                timeout = len(flashcards) * max_stage_timeout + 30  # Extra time for user interaction
                
                while not self.current_session_results and time.time() - start_time < timeout:
                    app.processEvents()
                    time.sleep(0.1)
                
                if self.current_session_results:
                    return self.current_session_results
                else:
                    logger.warning("Review session timed out")
                    return None
            else:
                logger.error("No QApplication instance found")
                return None
                
        except Exception as e:
            logger.error(f"Error executing review session: {e}")
            return None
    
    def on_review_completed(self, results: dict):
        """
        Handle review completion signal from ReviewerModule
        
        Args:
            results: Dictionary of results {flashcard_id: result}
        """
        logger.info(f"Review completed with {len(results)} results")
        self.current_session_results = results
    
    def update_flashcard_results(self, results: dict):
        """
        Feature 4: Update flashcard results in database
        
        Args:
            results: Dictionary of results {flashcard_id: result}
        """
        try:
            for flashcard_id, result in results.items():
                logger.info(f"Updating flashcard {flashcard_id} with result: {result}")
                self.database_manager.update_flashcard_after_review(flashcard_id, result)
                
            logger.info(f"Updated {len(results)} flashcards with review results")
            
        except Exception as e:
            logger.error(f"Error updating flashcard results: {e}")
    
    def get_review_statistics(self) -> dict:
        """
        Get statistics about the current review session
        
        Returns:
            Dictionary with session statistics
        """
        try:
            if not self.current_session_results:
                return {}
            
            total_reviews = len(self.current_session_results)
            correct_answers = sum(1 for result in self.current_session_results.values() if result == "True")
            wrong_answers = sum(1 for result in self.current_session_results.values() if result == "False")
            timeouts = sum(1 for result in self.current_session_results.values() if result == "TIMEOUT")
            
            accuracy = (correct_answers / total_reviews * 100) if total_reviews > 0 else 0
            
            return {
                'total_reviews': total_reviews,
                'correct_answers': correct_answers,
                'wrong_answers': wrong_answers,
                'timeouts': timeouts,
                'accuracy_percentage': round(accuracy, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting review statistics: {e}")
            return {}
    
    def cleanup(self):
        """
        Cleanup resources
        """
        try:
            if self.reviewer_module:
                self.reviewer_module.close()
                self.reviewer_module = None
            
            if self.pre_review_notification:
                try:
                    self.pre_review_notification.review_accepted.disconnect()
                    self.pre_review_notification.review_declined.disconnect()
                except:
                    pass
                self.pre_review_notification.close()
                self.pre_review_notification = None
            
            self.current_session_results = {}
            self.pending_flashcards = []
            self.pending_contextual_words = []
            self.pending_contextual_meanings = []
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def is_review_in_progress(self):
        """
        Check if a review session is currently in progress
        """
        notification_visible = (self.pre_review_notification is not None and 
                              self.pre_review_notification.isVisible())
        review_visible = (self.reviewer_module is not None and 
                         self.reviewer_module.isVisible())
        return notification_visible or review_visible
    
    def force_review_session(self, limit: int = 5) -> Tuple[bool, int]:
        """
        Force a review session with any available flashcards (for testing/manual review)
        
        Args:
            limit: Maximum number of flashcards to review
            
        Returns:
            Tuple[bool, int]: (success, next_interval_minutes)
        """
        try:
            # Get any flashcards (not just due ones)
            from src.database.database_manager import DatabaseManager
            
            with DatabaseManager(self.database_manager.db_path).database_manager.db_path as db_path:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get any flashcards for forced review
                cursor.execute("""
                    SELECT * FROM flashcards 
                    ORDER BY priority_score DESC, created_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                conn.close()
                
                if not rows:
                    logger.info("No flashcards available for forced review")
                    return False, 30  # Default 30 minutes
                
                # Convert to FlashCard objects
                flashcards = [self.database_manager._row_to_flashcard(row) for row in rows]
                
                logger.info(f"Starting forced review session with {len(flashcards)} flashcards")
                
                # Use the same process as normal review
                contextual_words = self.prepare_contextual_words(flashcards)
                contextual_meanings = self.prepare_contextual_meanings(flashcards)
                
                results = self.execute_review_session(flashcards, contextual_words, contextual_meanings)
                
                if results is None:
                    logger.info("Forced review session was cancelled or failed")
                    return False, 30
                
                self.update_flashcard_results(results)
                next_interval = self.database_manager.calculate_next_test_interval()
                
                logger.info(f"Forced review session completed successfully. Next session in {next_interval} minutes")
                return True, next_interval
                
        except Exception as e:
            logger.error(f"Error in forced review session: {e}")
            return False, 30
    
    def set_stage_timeout(self, stage_id: int, timeout_seconds: int):
        """
        Set timeout for a specific stage
        
        Args:
            stage_id: Stage ID (1-4)
            timeout_seconds: Timeout in seconds
        """
        if 1 <= stage_id <= 4:
            self.stage_timeouts[stage_id] = timeout_seconds
            logger.info(f"Updated Stage {stage_id} timeout to {timeout_seconds} seconds")
        else:
            logger.warning(f"Invalid stage_id: {stage_id}. Must be between 1 and 4")
    
    def get_stage_timeout(self, stage_id: int) -> int:
        """
        Get timeout for a specific stage
        
        Args:
            stage_id: Stage ID (1-4)
            
        Returns:
            Timeout in seconds
        """
        return self.stage_timeouts.get(stage_id, self.default_timeout)
    
    def get_all_stage_timeouts(self) -> dict:
        """
        Get all stage timeouts
        
        Returns:
            Dictionary of stage timeouts {stage_id: timeout_seconds}
        """
        return self.stage_timeouts.copy()