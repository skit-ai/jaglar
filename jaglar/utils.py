import re
from typing import Dict


def standardize_name(name: str) -> str:
    """
    Standardize name string to become a valid tj id
    """

    if not name:
        return name

    name = re.sub(r"[\./\- ]", "_", name.lower())

    if name[0].isdigit():
        name = "a_" + name

    return name


def map_keys(d: Dict, fn) -> Dict:
    """
    Map fn on d's keys
    """

    new_d = {}
    for k, v in d.items():
        if isinstance(v, dict):
            new_d[fn(k)] = map_keys(v, fn)
        elif isinstance(v, list):
            new_d[fn(k)] = [map_keys(it, fn) for it in v]
        else:
            new_d[fn(k)] = v

    return new_d
