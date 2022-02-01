# Behave environment file to add the python version number to each feature/scenario name/

import sys


def before_scenario(context, scenario):
    version = sys.version
    scenario.name = "py" + version + scenario.name