#!/usr/bin/env python3
"""
Drip Application Launcher

This script provides a safe way to launch the Drip application with proper error handling.
"""

import sys
import os
import logging
import traceback

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging configuration"""
    # Check if debug mode is requested
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/drip.log'),
            logging.StreamHandler()
        ]
    )
    
    if debug_mode:
        print("Debug mode enabled - detailed logging active")

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = ['PyQt5', 'pystray', 'pynput']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Check dependencies
        if not check_dependencies():
            return 1
        
        # Import and run the main application
        from main import DripApp
        
        logger.info("Starting Drip - Vocabulary Learning System")
        app = DripApp()
        return app.run()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all required dependencies are installed")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return 1
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0

if __name__ == "__main__":
    sys.exit(main())