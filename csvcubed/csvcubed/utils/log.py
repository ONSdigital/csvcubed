"""
Log
---
Utilities to help with logging.
"""
import logging
import sys
import io
import traceback

from typing import Union
from pathlib import Path

from appdirs import AppDirs


class CustomFormatter(logging.Formatter):

    grey = "\x1b[2;20m"
    light_grey = "\x1b[1;50m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    formatting = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + formatting + reset,
        logging.INFO: light_grey + formatting + reset,
        logging.WARNING: yellow + formatting + reset,
        logging.ERROR: red + formatting + reset,
        logging.CRITICAL: bold_red + formatting + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def start_logging(
    logdir: str,
    selected_logging_level: Union[str, None],
    root_logger_name: str = "csvcubed",
) -> None:
    if selected_logging_level == "err":
        logging_level: int = logging.ERROR
    elif selected_logging_level == "crit":
        logging_level: int = logging.CRITICAL
    elif selected_logging_level == "info":
        logging_level: int = logging.INFO
    elif selected_logging_level == "debug":
        logging_level: int = logging.DEBUG
    else:
        logging_level: int = logging.WARNING

    dirs = AppDirs(logdir, "csvcubed")
    log_file_path = Path(dirs.user_log_dir)
    log_file_already_exists = True
    if not log_file_path.exists():
        log_file_already_exists: bool = False
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(root_logger_name)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(CustomFormatter())

    file_handler = logging.FileHandler(dirs.user_log_dir)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(
        logging.Formatter(f"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    if not log_file_already_exists:
        logger.critical(
            "A log file containing the recordings of this cli, is at: "
            + dirs.user_log_dir
        )

def handle_exception(logger, exc_type, exc_value, exc_tb) -> None:
    
    file_stream = io.StringIO()
    traceback.print_exception(exc_type, exc_value, exc_tb,limit=None, chain=True, file=file_stream)
    file_stream.seek(0)
    stack_trace: str = file_stream.read()
    logger.critical(stack_trace)