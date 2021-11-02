from pathlib import Path


def get_test_cases_dir(start_dir: Path = Path(".")):
    """First searches for child directories called "test-cases" and then searches recursively up the file system."""
    if str(start_dir) == "/":
        raise Exception(f"Could not find test-cases directory")

    child_test_cases_dirs = list(start_dir.rglob("test-cases"))
    if len(child_test_cases_dirs) == 1:
        return child_test_cases_dirs[0]
    elif len(child_test_cases_dirs) > 1:
        raise Exception(
            f"Found multiple child test-case directories: {', '.join([str(d) for d in child_test_cases_dirs])}"
        )

    return get_test_cases_dir(start_dir.absolute().parent)
