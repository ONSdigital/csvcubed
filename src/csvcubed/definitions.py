"""
Definitions
-----------

Currently defines the root project path.
"""

import os
from pathlib import Path

APP_ROOT_DIR_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
"""
Defines a variable to the project root path.
Ref: https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure/25389715#25389715

**Must not be used to refer to anything that is not bundled into the whl package**.
"""
