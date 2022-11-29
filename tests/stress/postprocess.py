import shutil
from pathlib import Path


temp_file = Path("temp_dir")

shutil.rmtree(temp_file)
