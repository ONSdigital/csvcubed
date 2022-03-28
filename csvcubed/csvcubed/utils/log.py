"""
Log
---
Utilities to help with logging.
"""
import logging
import logging.handlers
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
    log_dir_name: str,
    selected_logging_level: Union[str, int, None],
    root_logger_name: str = "csvcubed",
) -> None:
    logging_level = _get_logging_level(selected_logging_level)

    dirs = AppDirs(log_dir_name, "csvcubed")
    log_file_path = Path(dirs.user_log_dir) / "out.log"
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(root_logger_name)
    logger.setLevel(logging_level)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(CustomFormatter())

    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file_path,
        encoding="utf-8",
        when="D",
        interval=7,  # Keep one week's worth of logs
    )
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(
        logging.Formatter(f"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def _get_logging_level(selected_logging_level: Union[int, str, None]) -> int:
    if isinstance(selected_logging_level, int):
        return selected_logging_level
    elif isinstance(selected_logging_level, str):
        selected_logging_level = selected_logging_level.lower()
        if selected_logging_level == "err":
            return logging.ERROR
        elif selected_logging_level == "crit":
            return logging.CRITICAL
        elif selected_logging_level == "info":
            return logging.INFO
        elif selected_logging_level == "debug":
            return logging.DEBUG
        elif selected_logging_level == "warn":
            return logging.WARN
        else:
            raise ValueError(f"Unexpected logging level {selected_logging_level}.")

    return logging.WARNING


def log_exception(logger: logging.Logger, error: Exception) -> None:
    file_stream = io.StringIO()
    traceback.print_exception(
        type(error),
        error,
        error.__traceback__,
        limit=None,
        chain=True,
        file=file_stream,
    )
    file_stream.seek(0)
    stack_trace: str = file_stream.read()
    logger.critical(stack_trace)
