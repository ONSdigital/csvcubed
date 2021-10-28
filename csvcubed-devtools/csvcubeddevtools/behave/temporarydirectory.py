"""
Temporary Testing Directory
---------------------------
"""
import distutils.util
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
from behave.model import Scenario
import re


def get_context_temp_dir_path(context) -> Path:
    if not hasattr(context, "temp_dir"):
        context.temp_dir = TemporaryDirectory()

        context.add_cleanup(lambda: context.temp_dir.cleanup())

        if "KEEP_FILES" in os.environ and bool(distutils.util.strtobool(os.environ["KEEP_FILES"])):
            def copy_temp_files_to_dir(dir: Path) -> None:
                if dir.exists():
                    # clean up old test files
                    shutil.rmtree(dir)

                dir.mkdir()

                temp_dir_path = Path(context.temp_dir.name)
                for file in temp_dir_path.glob("*"):
                    shutil.move(file, dir)

            scenario: Scenario = context.scenario
            output_dir = Path.home() / "last_run_behave" / _file_safe(scenario.name)
            context.add_cleanup(lambda: copy_temp_files_to_dir(output_dir))

    return Path(context.temp_dir.name)


def _file_safe(label: str) -> str:
    return re.sub("[^A-Za-z0-9]+", "-", label)
