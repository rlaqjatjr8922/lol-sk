import json
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

BASE = "https://docs.gcsim.app/reference/characters/"

CHARACTER_NAMES = [
    "Albedo","Alhaitham","Aloy","Amber","Arlecchino","Kamisato Ayaka","Kamisato Ayato",
    "Baizhu","Barbara","Beidou","Bennett","Candace","Charlotte","Chasca","Chevreuse",
    "Chiori","Chongyun","Citlali","Clorinde","Collei","Cyno","Dahlia","Dehya","Diluc",
    "Diona","Dori","Emilie","Escoffier","Eula","Faruzan","Fischl","Flins","Freminet",
    "Furina","Gaming","Ganyu","Gorou","Shikanoin Heizou","Hu Tao","Ineffa","Arataki Itto",
    "Jean","Kaeya","Kaveh","Kaedehara Kazuha","Keqing","Kinich","Kirara","Klee",
    "Sangonomiya Kokomi","Kuki Shinobu","Lan Yan","Lauma","Layla","Lisa","Lynette",
    "Lyney","Mavuika","Mika","Yumemizuki Mizuki","Mona","Mualani","Nahida","Navia",
    "Neuvillette","Nilou","Ningguang","Noelle","Ororon","Qiqi","Raiden Shogun","Razor",
    "Rosaria","Kujou Sara","Sayu","Sethos","Shenhe","Sigewinne","Skirk","Sucrose",
    "Tartaglia","Thoma","Tighnari","Traveler (Anemo)","Traveler (Dendro)",
    "Traveler (Electro)","Traveler (Geo)","Traveler (Hydro)","Traveler (Pyro)",
    "Varesa","Venti","Wanderer","Wriothesley","Xiangling","Xianyun","Xiao",
    "Xilonen","Xingqiu","Xinyan","Yae Miko","Yanfei","Yaoyao","Yelan","Yoimiya",
    "Yun Jin","Zhongli"
]

# 🔥 최종 slug (에러 수정 완료)
SPECIAL_SLUGS = {
    "Kamisato Ayaka": "ayaka",
    "Kamisato Ayato": "ayato",
    "Shikanoin Heizou": "heizou",
    "Arataki Itto": "itto",
    "Kaedehara Kazuha": "kazuha",
    "Sangonomiya Kokomi": "kokomi",

    "Kuki Shinobu": "kuki",
    "Raiden Shogun": "raiden",
    "Kujou Sara": "sara",
    "Yae Miko": "yaemiko",
    "Yun Jin": "yunjin",
    "Tartaglia": "tartaglia",
    "Yumemizuki Mizuki": "mizuki",

    "Traveler (Anemo)": "traveleranemo",
    "Traveler (Dendro)": "travelerdendro",
    "Traveler (Electro)": "travelerelectro",
    "Traveler (Geo)": "travelergeo",
    "Traveler (Hydro)": "travelerhydro",
    "Traveler (Pyro)": "travelerpyro",
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

def name_to_slug(name):
    if name in SPECIAL_SLUGS:
        return SPECIAL_SLUGS[name]
    slug = name.lower()
    slug = re.sub(r"\(.*?\)", "", slug)
    slug = slug.replace("'", "")
    slug = slug.replace("-", "")
    slug = re.sub(r"[^a-z0-9]+", "", slug)
    return slug

def fetch_legal_actions(slug):
    url = urljoin(BASE, f"{slug}/")
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    header = None
    for tag in soup.find_all(["h2","h3"]):
        if "legal actions" in tag.get_text().lower():
            header = tag
            break

    if not header:
        raise Exception("Legal Actions 없음")

    table = header.find_next("table")
    rows = table.find_all("tr")

    result = {}
    for tr in rows[1:]:
        cols = [td.get_text(" ", strip=True) for td in tr.find_all(["td","th"])]
        if len(cols) < 3:
            continue

        action = cols[0]
        result[action] = {
            "legal": cols[1],
            "notes": cols[2]
        }

    return result

def main():
    all_data = {}
    failed = {}

    # 🔥 파이썬 파일 위치 기준 저장
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for i, name in enumerate(CHARACTER_NAMES):
        slug = name_to_slug(name)
        print(f"[{i+1}/{len(CHARACTER_NAMES)}] {name} -> {slug}")

        try:
            data = fetch_legal_actions(slug)
            all_data[name] = data
            print("  OK")
        except Exception as e:
            failed[name] = {
                "slug": slug,
                "error": str(e)
            }
            print("  FAIL:", e)

        time.sleep(0.2)

    # 저장
    with open(os.path.join(base_dir, "gcsim_legal_actions_all.json"), "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    with open(os.path.join(base_dir, "gcsim_legal_actions_failed.json"), "w", encoding="utf-8") as f:
        json.dump(failed, f, ensure_ascii=False, indent=2)

    print("\n완료")
    print("성공:", len(all_data))
    print("실패:", len(failed))
    print("저장 위치:", base_dir)

if __name__ == "__main__":
    main()