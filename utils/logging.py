import logging
import os
from .config import get_config # Assuming config.py is in the same directory

# Global flag to ensure setup_logging is called only once
_logging_configured = False

def setup_logging():
    """
    Configures the logging for the application based on settings
    from config.ini (via utils.config).
    """
    global _logging_configured
    if _logging_configured:
        return

    config = get_config()
    log_settings = config.get("Paths", {})
    app_settings = config.get("App", {})

    log_file_path = log_settings.get("log_file", "logs/app.log") # Default if not in config
    debug_mode = app_settings.get("debug_mode", False) # Get debug_mode, defaults to False

    log_level = logging.DEBUG if debug_mode else logging.INFO

    # Ensure log directory exists
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            print(f"INFO: Log directory '{log_dir}' created.")
        except OSError as e:
            # Fallback to console logging if directory creation fails
            print(f"ERROR: Could not create log directory '{log_dir}': {e}. Logging to console only.")
            log_file_path = None

    # Basic configuration
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Remove any existing handlers to avoid duplicate logs if this function is ever called again
    # (though _logging_configured should prevent it)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler (if path is valid)
    if log_file_path:
        try:
            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            print(f"INFO: Logging configured. Level: {logging.getLevelName(log_level)}. File: '{log_file_path}'")
        except Exception as e:
            print(f"ERROR: Could not set up file logger for '{log_file_path}': {e}. Logging to console only.")
    else:
        print(f"INFO: Logging configured. Level: {logging.getLevelName(log_level)}. Console only.")

    _logging_configured = True

def get_logger(name):
    """
    Returns a logger instance with the specified name.
    Ensures logging is set up before returning the logger.
    """
    if not _logging_configured:
        setup_logging() # Ensure logging is configured
    return logging.getLogger(name)

# Automatically configure logging when this module is first imported
if not _logging_configured:
    setup_logging()

if __name__ == '__main__':
    # For testing purposes
    print("Testing logging setup...")

    # This will trigger setup_logging if not already done by direct import
    logger = get_logger("LoggingTest")

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    # Test with another logger name
    another_logger = get_logger("AnotherModule")
    another_logger.info("Message from another logger.")

    print(f"Logging should be visible in console and potentially in the configured log file.")
    config_for_log_path = get_config().get("Paths", {})
    print(f"Expected log file: {config_for_log_path.get('log_file', 'logs/app.log')}")
