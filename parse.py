import sys
from typing import Tuple, Dict


def parse_config(filename: str) -> Dict[str, str]:
    """Parse configuration file and validate mandatory keys."""
    config: Dict[str, str] = {}

    try:
        with open(filename, "r", encoding="utf-8") as file_obj:
            for line in file_obj:
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("#"):
                    continue

                if "=" not in clean_line:
                    raise ValueError(f"Invalid format: {clean_line}")

                key, val = clean_line.split("=", 1)
                config[key.strip().upper()] = val.strip()

    except Exception as error:
        print(f"Error parsing configuration file: {error}")
        sys.exit(1)

    required_keys = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
    ]

    for key in required_keys:
        if key not in config:
            print(f"Error: Missing mandatory key '{key}' in config.")
            sys.exit(1)

    return config


def parse_tuple(val: str) -> Tuple[int, int]:
    """Parse a coordinate tuple from a string like 'X,Y'."""
    try:
        x_str, y_str = val.split(",")
        return int(x_str), int(y_str)
    except Exception as error:
        raise ValueError(f"Invalid coordinate format '{val}'.") from error
