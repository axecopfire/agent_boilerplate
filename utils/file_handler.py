from library.utils.logging_config import logger


class FileHandler:
    def __init__(self, utils, filename):
        self.filename = filename
        self.utils = utils

    def read(self):
        try:
            return self.utils.read_file_to_string(self.filename)
        except Exception as e:
            logger.error(f"Error reading file {self.filename}: {e}")
            return None

    def write(self, content, operation="w"):
        try:
            return self.utils.write_string_to_file(self.filename, content, operation)
        except Exception as e:
            logger.error(f"Error writing to file {self.filename}: {e}")
