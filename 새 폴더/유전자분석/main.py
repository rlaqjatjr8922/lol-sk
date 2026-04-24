import json
import os

from state_logic import build_note_condition_map
from ga_logic import search_best_rotation


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    LEGAL_ACTIONS_JSON = os.path.join(BASE_DIR, "gcsim_legal_actions_all.json")
    CONDITIONS_JSON = os.path.join(BASE_DIR, "a.json")

    legal_actions_data = load_json(LEGAL_ACTIONS_JSON)
    condition_defs = load_json(CONDITIONS_JSON)
    note_condition_map = build_note_condition_map(condition_defs)

    party = ["Albedo", "Bennett", "Fischl", "Navia"]
    main_dps_idx = 0

    # 동시에 몇 개 평가할지
    MAX_WORKERS = 32

    best_result, history = search_best_rotation(
        party=party,
        main_dps_idx=main_dps_idx,
        legal_actions_data=legal_actions_data,
        note_condition_map=note_condition_map,
        start_T=4,
        drop_threshold=0.05,
        drop_streak_limit=3,
        max_workers=MAX_WORKERS
    )

    print("=== GLOBAL BEST RESULT ===")
    print(json.dumps(best_result, ensure_ascii=False, indent=2))

    print("\n=== HISTORY ===")
    for row in history:
        print(f"T={row['T']}, best_dps={row['best_dps']:.2f}, split={row['token_split']}")