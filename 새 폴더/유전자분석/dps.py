import sys
import random
import json

if __name__ == "__main__":
    # main.py에서 넘긴 JSON (안써도 되지만 파싱은 해둠)
    payload = sys.argv[1]
    _ = json.loads(payload)

    # 1~100 랜덤 DPS
    dps = random.uniform(1, 100)

    print(dps)