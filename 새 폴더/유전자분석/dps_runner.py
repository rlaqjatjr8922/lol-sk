import json
import subprocess
import sys
import os

from state_logic import is_individual_fully_legal


def evaluate_individual_dps(
    individual,
    legal_actions_data,
    note_condition_map
) -> float:

    if not is_individual_fully_legal(individual, legal_actions_data, note_condition_map):
        return -1.0

    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        dps_path = os.path.join(BASE_DIR, "dps.py")

        payload = json.dumps(individual, ensure_ascii=False)

        result = subprocess.run(
            [sys.executable, dps_path, payload],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )

        return float(result.stdout.strip())

    except Exception:
        return -1.0