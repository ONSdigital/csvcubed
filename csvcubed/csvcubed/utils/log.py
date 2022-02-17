"""
Log
---
Utilities to help with logging.
"""
import logging
import sys
from appdirs import AppDirs
from typing import Union
from pathlib import Path

class CustomFormatter(logging.Formatter):

    grey = "\x1b[2;20m"
    light_grey = "\x1b[1;50m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: light_grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def start_logging(
    logdir:str,selected_logging_level: Union[str,None], root_logger_name: str = "csvcubed"
) -> None:
    if selected_logging_level == 'err':
        logging_level: int = logging.ERROR
    elif selected_logging_level == 'crit':
        logging_level: int = logging.CRITICAL
    elif selected_logging_level == 'info':
        logging_level: int = logging.INFO
    elif selected_logging_level == 'debug':
        logging_level: int = logging.DEBUG
    else:
        logging_level: int = logging.WARNING

    dirs = AppDirs(logdir, "csvcubed")
    log_file_path = Path(dirs.user_log_dir)
    log_file_path.parent.mkdir(parents=True,exist_ok=True)

    logger = logging.getLogger(root_logger_name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging_level)
    console_handler.addFilter(ConsoleColourFilter())
    console_handler.setFormatter(CustomFormatter())

    file_handler = logging.FileHandler(dirs.user_log_dir)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(
        logging.Formatter(
            f"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.critical("A log file containing the recordings of this cli, is at: "+dirs.user_log_dir)
    logger.error("A log file containing the recordings of this cli, is at: "+dirs.user_log_dir)
    logger.warning("A log file containing the recordings of this cli, is at: "+dirs.user_log_dir)
    logger.info("A log file containing the recordings of this cli, is at: "+dirs.user_log_dir)
    logger.debug("A log file containing the recordings of this cli, is at: "+dirs.user_log_dir)

class ConsoleColourFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # if record.levelno >= logging.ERROR:
        #     record.colour = Fore.RED + Style.BRIGHT  # type: ignore
        # elif record.levelno >= logging.WARNING:
        #     record.colour = Fore.YELLOW  # type: ignore
        # else:
        #     record.colour = Fore.LIGHTBLACK_EX  # type: ignore
        # todo: Sort colouring out in Issue #322.
        record.colour = ""  # type: ignore

        return True
