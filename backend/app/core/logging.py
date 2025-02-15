import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

def setup_logging(
    level: str = "INFO",
) -> None:
    """
    Configure the root logger with customizable options.

    Args:
        level: Logging level (default: "INFO")
        enable_wlui: Whether to use WLUI filtering and formatting (default: True)
        log_file: Optional file path to write logs to
        format_string: Optional custom format string for logging
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler setup
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # file handler setup
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "app.log")

    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Set third-party loggers to a higher level to reduce noise
    tortoise_loggers = [
        "tortoise",
        "tortoise.models",
        "tortoise.orm",
        "tortoise.transactions",
        "tortoise.fields",
        "tortoise.fields.relational",
    ]
    uvicorn_logger = ["uvicorn", "uvicorn.error", "uvicorn.access"]
    all_removed_loggers = tortoise_loggers + uvicorn_logger + ["httpx", "httpcore"]

    for logger_name in all_removed_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
