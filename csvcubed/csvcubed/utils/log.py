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


def start_logging(
    selected_logging_level: Union[str,None], root_logger_name: str = "csvcubed"
) -> None:
    if selected_logging_level == 'err':
        logging_level: int = logging.ERROR
    elif selected_logging_level == 'crit':
        logging_level: int = logging.CRITICAL
    else:
        logging_level: int = logging.WARNING

    dirs = AppDirs("csvcubedcli", "csvcubed")
    if not Path(dirs.user_log_dir).exists():
        Path(dirs.user_log_dir).mkdir(parents=True,exist_ok=True)
        Path(dirs.user_log_dir).rmdir()

    logger = logging.getLogger(root_logger_name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging_level)
    console_handler.addFilter(ConsoleColourFilter())
    console_handler.setFormatter(
        logging.Formatter(
            f"%(colour)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )

    file_handler = logging.FileHandler(dirs.user_log_dir)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(
        logging.Formatter(
            f"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.warning("A log file containing the recorings of this cli, is at: "+dirs.user_log_dir)


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