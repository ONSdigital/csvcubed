"""
Temporary Testing Directory
---------------------------
"""

from pathlib import Path
from tempfile import TemporaryDirectory
import shutil


def get_context_temp_dir_path(context) -> Path:
    if not hasattr(context, "temp_dir"):
        context.temp_dir = TemporaryDirectory()

        context.add_cleanup(lambda: context.temp_dir.cleanup())


        context.add_cleanup(
            lambda: shutil.move(context.temp_dir.name, Path.home() /  "last_run_behave")
        )

    return Path(context.temp_dir.name)
