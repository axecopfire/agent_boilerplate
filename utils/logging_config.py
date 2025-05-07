from datetime import datetime
import sys
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Create a console handler and set the level to info
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(console_handler)

today = datetime.today()
month = today.month
day = today.day

# Optionally, you can also add a file handler if you want to log to a file as well
file_handler = logging.FileHandler(f"logs/{month}-{day}.log", mode="a")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def use_console_logger():
    logger.removeHandler(file_handler)
    logger.addHandler(console_handler)


def use_file_logger():
    logger.removeHandler(console_handler)
    logger.addHandler(file_handler)
