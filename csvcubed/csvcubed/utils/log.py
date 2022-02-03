"""
Log
---

Utilities to help with logging.
"""
import logging
import sys
from colorama import Fore, Style


def start_logging(
    root_logger_name: str = "csvcubed", console_level: int = logging.DEBUG
) -> None:
    logger = logging.getLogger(root_logger_name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(console_level)
    console_handler.addFilter(ConsoleColourFilter())
    console_handler.setFormatter(
        logging.Formatter(
            f"%(colour)s%(asctime)s - %(name)s - %(levelname)s - %(message)s {Style.RESET_ALL}"
        )
    )

    logger.addHandler(console_handler)


class ConsoleColourFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno >= logging.ERROR:
            record.colour = Fore.RED + Style.BRIGHT  # type: ignore
        elif record.levelno >= logging.WARNING:
            record.colour = Fore.YELLOW  # type: ignore
        else:
            record.colour = Fore.LIGHTBLACK_EX  # type: ignore

        return True
