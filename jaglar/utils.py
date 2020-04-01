from typing import Dict


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
