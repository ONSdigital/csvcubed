import sys
from behave.__main__ import run_behave
from behave.configuration import Configuration

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    # args = [
    #     "csvcubedintegrationfeatures"
    # ]  # , "-n", "The infojson2csvqb build command should succeed when 'families' within info.json contains 'Climate Change'"]
    configuration = Configuration(args)
    sys.exit(run_behave(configuration))
