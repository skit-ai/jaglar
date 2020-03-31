from typing import Dict


def map_keys(d: Dict, fn) -> Dict:
    """
    Map fn on d's keys
    """

    new_d = {}
    for k, v in d:
        if isinstance(v, dict):
            new_d[fn(k)] = map_keys(v, fn)
        else:
            new_d[fn(k)] = v

    return new_d
