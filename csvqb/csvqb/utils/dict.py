from typing import Any, Optional, Callable


def get_from_dict_ensure_exists(config: dict, key: str) -> Any:
    val = config.get(key)
    if val is None:
        raise Exception(f"Couldn't find value for key '{key}'")
    return val


def get_with_func_or_none(d: dict, prop_name: str, func: Callable[[Any], Any]) -> Optional[Any]:
    return func(d[prop_name]) if d.get(prop_name) is not None else None
