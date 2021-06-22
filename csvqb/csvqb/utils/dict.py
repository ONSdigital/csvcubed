from typing import Any


def get_from_dict_ensure_exists(config: dict, key: str) -> Any:
    val = config.get(key)
    if val is None:
        raise Exception(f"Couldn't find value for key '{key}'")
    return val
