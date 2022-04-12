"""
Definitions
-----------

Currently defines the root project path.
"""

import os
from pathlib import Path

"""
Defines a variable to the project root path.
Ref: https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure/25389715#25389715
"""
ROOT_DIR_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
