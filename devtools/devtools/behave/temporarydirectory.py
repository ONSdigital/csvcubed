from pathlib import Path
from tempfile import TemporaryDirectory


def get_context_temp_dir_path(context) -> Path:
    if not hasattr(context, "temp_dir"):
        context.temp_dir = TemporaryDirectory()
        context.add_cleanup(lambda: context.temp_dir.cleanup())

    return Path(context.temp_dir.name)
