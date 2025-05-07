import os
import hashlib
import subprocess
from typing import List
import time
from datetime import datetime
from library.utils.file_handler import FileHandler
from library.utils.logging_config import logger


def get_last_100_lines(log_file_path):
    result = subprocess.run(
        ["tail", "-n", "100", log_file_path], stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8")


def execution_timer(fn):
    start_time = time.time()
    print(f"Execution started: {datetime.now()}")

    fn()

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"script ran for {elapsed_time:.2f} seconds")


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


class Utils:
    def __init__(self, root_dir="./", language="Python"):
        self.root_dir = root_dir
        self.language = language

    def get_file_handler(self, file_name):
        return FileHandler(self, file_name)

    def read_file_to_string(self, filename):
        """
        Reads the contents of a file into a string.

        :param file_path: Path to the file to be read.
        :return: A string containing the contents of the file.
        """
        file_path = filename

        if not filename.startswith(self.root_dir):
            file_path = os.path.join(self.root_dir, filename)
        if os.path.isdir(file_path):
            return ""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file_contents = file.read()
            return file_contents
        except FileNotFoundError:
            return ""
        except IOError as e:
            raise Exception(f"Error: An I/O error occurred: {e}")

    def write_string_to_file(self, filename, file_content, operation="w"):
        """
        :param filename: filename with extension
        :return: An MD-5 hash of the new file
        """

        file_path = filename

        if not filename.startswith(self.root_dir):
            file_path = os.path.join(self.root_dir, filename)

        if os.path.isdir(file_path):
            return None

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            if operation == "a":
                with open(file_path, "a", encoding="utf-8") as file:
                    file.write(file_content)
            else:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(file_content)

            # Generate MD-5 hash of the file
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

    def run_script(self, script_path, command=None):
        if not os.path.isfile(script_path):
            raise FileNotFoundError(
                f"The script {script_path} does not exist.")

        # Ensure the script is executable
        if not os.access(script_path, os.X_OK):
            os.chmod(script_path, 0o755)

        if self.language == "Kotlin":
            if command:
                # Use the provided command for Java
                command_arr = [
                    "docker-compose",
                    "run",
                    "--rm",
                    "java",
                    "bash",
                    "-c",
                    command,
                ]
            else:
                raise ValueError("Command must be provided for Java language.")
        else:
            command_arr = ["/bin/bash", script_path]

        # Run the script
        process = subprocess.Popen(
            command_arr, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        try:
            # Wait for the process to complete with a timeout
            stdout, stderr = process.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            # Terminate the process if it exceeds the timeout
            process.terminate()
            stdout, stderr = process.communicate()
            raise TimeoutError(f"Script {script_path} timed out.")

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, script_path, output=stdout, stderr=stderr
            )

        return stdout, stderr

    def run_subprocess(self, command):
        command_arr = command.split(" ")
        try:
            # Run the shell script, and capture the output
            process = subprocess.Popen(
                command_arr, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            try:
                # Wait for the process to complete with a timeout
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Terminate the process if it exceeds the timeout
                return process.communicate()
            # Return the output
            finally:
                process.terminate()
                return process.communicate()

        except Exception:
            logger.error(
                f"An error occurred while running the command: {command}.")
            raise

    def get_folder_structure(self, directory="", add_hide_list=[]) -> tuple:
        try:
            hide_list = [
                "build",
                ".gradle",
                ".idea",
                "gradle",
                "gradlew",
                "gradlew.bat",
                "__pycache__",
                "pytest_cache",
                ".cache",
                ".coverage",
                ".git",
                "node_modules",
                "package-lock.json",
                "yarn.lock",
            ] + add_hide_list

            if not directory.startswith(self.root_dir):
                file_path = os.path.join(self.root_dir, directory)

            find_command = f"find {file_path}"
            find_result = self.run_subprocess(find_command)

            sanitized_list = []
            for p in find_result[0].splitlines():

                # skip hidden files and folders
                if any(substring in p for substring in hide_list):
                    continue
                sanitized_string = p.replace("\n", "")

                if len(sanitized_string):
                    sanitized_list.append(sanitized_string)

            return tuple(sanitized_list)
        except Exception as e:
            raise Exception(
                f"An error occurred while reading list of files and folders file_path {directory}\n{e}"
            )

    def read_file_between_lines(self, filename, start_line, end_line):
        start_line = int(start_line)
        end_line = int(end_line)
        lines = []
        with open(filename, "r") as file:
            for current_line_number, line in enumerate(file, start=1):
                if start_line <= current_line_number <= end_line:
                    lines.append(line)
                elif current_line_number > end_line:
                    break
        return "".join(lines)

    def read_files_and_concatenate(self, file_list: List[str]) -> str:
        concatenated_content = ""
        for file in file_list:
            file_handler = self.get_file_handler(file)
            file_content = file_handler.read()
            concatenated_content += f"File: {file}\n{file_content}\n\n"
        return concatenated_content
