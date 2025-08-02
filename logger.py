import logging
from logging.handlers import RotatingFileHandler
import os

# Create 'logs' directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Set up logging configuration
log_file = "logs/app_errors.log"

logger = logging.getLogger("app_logger")
logger.setLevel(logging.ERROR)  # Log only errors and above

# Configure rotating file handler (5 files of 1MB each)
handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)
