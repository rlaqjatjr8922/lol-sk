import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

input_path = os.path.join(base_dir, "gcsim_legal_actions_all.json")
output_path = os.path.join(base_dir, "gcsim_unique_notes.json")

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

notes_set = set()

for character, actions in data.items():
    for action, info in actions.items():
        notes = str(info.get("notes", "")).strip()

        # "-" 제외
        if notes not in ["-", ""]:
            notes_set.add(notes)

# 리스트로 변환 + 정렬
unique_notes = sorted(list(notes_set))

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(unique_notes, f, ensure_ascii=False, indent=2)

print("완료")
print("개수:", len(unique_notes))
print("저장:", output_path)