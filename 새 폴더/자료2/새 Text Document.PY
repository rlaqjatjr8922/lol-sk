import os
import csv
import re
import time

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE = "https://genshin-builds.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

TARGET_CHARACTERS = [
    "Albedo","Alhaitham","Aloy","Amber","Arlecchino",
    "Kamisato Ayaka","Kamisato Ayato","Baizhu","Barbara","Beidou",
    "Bennett","Candace","Charlotte","Chasca","Chevreuse",
    "Chiori","Chongyun","Citlali","Clorinde","Collei",
    "Cyno","Dahlia","Dehya","Diluc","Diona","Dori",
    "Emilie","Escoffier","Eula","Faruzan","Fischl",
    "Flins","Freminet","Furina","Gaming","Ganyu","Gorou",
    "Shikanoin Heizou","Hu Tao","Ineffa","Arataki Itto",
    "Jean","Kaeya","Kaveh","Kaedehara Kazuha","Keqing",
    "Kinich","Kirara","Klee","Sangonomiya Kokomi",
    "Kuki Shinobu","Lan Yan","Lauma","Layla","Lisa",
    "Lynette","Lyney","Mavuika","Mika","Yumemizuki Mizuki",
    "Mona","Mualani","Nahida","Navia","Neuvillette",
    "Nilou","Ningguang","Noelle","Ororon","Qiqi",
    "Raiden Shogun","Razor","Rosaria","Kujou Sara",
    "Sayu","Sethos","Shenhe","Sigewinne","Skirk",
    "Sucrose","Tartaglia","Thoma","Tighnari",
    "Traveler (Anemo)","Traveler (Dendro)","Traveler (Electro)",
    "Traveler (Geo)","Traveler (Hydro)","Traveler (Pyro)",
    "Varesa","Venti","Wanderer","Wriothesley",
    "Xiangling","Xianyun","Xiao","Xilonen",
    "Xingqiu","Xinyan","Yae Miko","Yanfei",
    "Yaoyao","Yelan","Yoimiya","Yun Jin","Zhongli",
]

NAME_TO_SLUG = {
    "Albedo": "albedo",
    "Alhaitham": "alhaitham",
    "Aloy": "aloy",
    "Amber": "amber",
    "Arlecchino": "arlecchino",
    "Kamisato Ayaka": "kamisato_ayaka",
    "Kamisato Ayato": "kamisato_ayato",
    "Baizhu": "baizhu",
    "Barbara": "barbara",
    "Beidou": "beidou",
    "Bennett": "bennett",
    "Candace": "candace",
    "Charlotte": "charlotte",
    "Chasca": "chasca",
    "Chevreuse": "chevreuse",
    "Chiori": "chiori",
    "Chongyun": "chongyun",
    "Citlali": "citlali",
    "Clorinde": "clorinde",
    "Collei": "collei",
    "Cyno": "cyno",
    "Dahlia": "dahlia",
    "Dehya": "dehya",
    "Diluc": "diluc",
    "Diona": "diona",
    "Dori": "dori",
    "Emilie": "emilie",
    "Escoffier": "escoffier",
    "Eula": "eula",
    "Faruzan": "faruzan",
    "Fischl": "fischl",
    "Flins": "flins",
    "Freminet": "freminet",
    "Furina": "furina",
    "Gaming": "gaming",
    "Ganyu": "ganyu",
    "Gorou": "gorou",
    "Shikanoin Heizou": "shikanoin_heizou",
    "Hu Tao": "hu_tao",
    "Ineffa": "ineffa",
    "Arataki Itto": "arataki_itto",
    "Jean": "jean",
    "Kaeya": "kaeya",
    "Kaveh": "kaveh",
    "Kaedehara Kazuha": "kaedehara_kazuha",
    "Keqing": "keqing",
    "Kinich": "kinich",
    "Kirara": "kirara",
    "Klee": "klee",
    "Sangonomiya Kokomi": "sangonomiya_kokomi",
    "Kuki Shinobu": "kuki_shinobu",
    "Lan Yan": "lan_yan",
    "Lauma": "lauma",
    "Layla": "layla",
    "Lisa": "lisa",
    "Lynette": "lynette",
    "Lyney": "lyney",
    "Mavuika": "mavuika",
    "Mika": "mika",
    "Yumemizuki Mizuki": "yumemizuki_mizuki",
    "Mona": "mona",
    "Mualani": "mualani",
    "Nahida": "nahida",
    "Navia": "navia",
    "Neuvillette": "neuvillette",
    "Nilou": "nilou",
    "Ningguang": "ningguang",
    "Noelle": "noelle",
    "Ororon": "ororon",
    "Qiqi": "qiqi",
    "Raiden Shogun": "raiden_shogun",
    "Razor": "razor",
    "Rosaria": "rosaria",
    "Kujou Sara": "kujou_sara",
    "Sayu": "sayu",
    "Sethos": "sethos",
    "Shenhe": "shenhe",
    "Sigewinne": "sigewinne",
    "Skirk": "skirk",
    "Sucrose": "sucrose",
    "Tartaglia": "tartaglia",
    "Thoma": "thoma",
    "Tighnari": "tighnari",
    "Traveler (Anemo)": "traveler_anemo",
    "Traveler (Dendro)": "traveler_dendro",
    "Traveler (Electro)": "traveler_electro",
    "Traveler (Geo)": "traveler_geo",
    "Traveler (Hydro)": "traveler_hydro",
    "Traveler (Pyro)": "traveler_pyro",
    "Varesa": "varesa",
    "Venti": "venti",
    "Wanderer": "wanderer",
    "Wriothesley": "wriothesley",
    "Xiangling": "xiangling",
    "Xianyun": "xianyun",
    "Xiao": "xiao",
    "Xilonen": "xilonen",
    "Xingqiu": "xingqiu",
    "Xinyan": "xinyan",
    "Yae Miko": "yae_miko",
    "Yanfei": "yanfei",
    "Yaoyao": "yaoyao",
    "Yelan": "yelan",
    "Yoimiya": "yoimiya",
    "Yun Jin": "yun_jin",
    "Zhongli": "zhongli",
}

IGNORE_ICON_SLUGS = {
    "anemo", "cryo", "dendro", "electro", "geo", "hydro", "pyro",
    "sword", "bow", "claymore", "polearm", "catalyst", "none",
    "image", "open", "full", "guide"
}

STAT_SUFFIXES = [
    "CRIT Rate", "CRIT DMG", "ATK%", "DEF%", "HP%",
    "Energy Recharge", "Elemental Mastery", "Physical DMG Bonus",
    "Healing Bonus", "Pyro DMG Bonus", "Hydro DMG Bonus",
    "Cryo DMG Bonus", "Electro DMG Bonus", "Anemo DMG Bonus",
    "Geo DMG Bonus", "Dendro DMG Bonus"
]


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def normalize_slug_text(text: str) -> str:
    text = clean_text(text).lower()
    text = text.replace("-", "_")
    text = re.sub(r"\s+", "_", text)
    return text


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_heading_text(tag) -> str:
    return clean_text(tag.get_text(" ", strip=True)).lower()


def find_first_heading(soup: BeautifulSoup, keywords):
    for tag in soup.find_all(["h2", "h3", "h4"]):
        text = get_heading_text(tag)
        if all(k in text for k in keywords):
            return tag
    return None


def find_section_heading_after(start_tag, target_words):
    node = start_tag
    while node:
        node = node.find_next()
        if node is None:
            break

        name = getattr(node, "name", None)
        if name == "h2":
            break

        if name in ("h3", "h4"):
            text = get_heading_text(node)
            if all(word in text for word in target_words):
                return node

    return None


def collect_links_until_next_heading(start_heading):
    results = []
    node = start_heading.find_next_sibling()

    while node:
        name = getattr(node, "name", None)
        if name in ("h2", "h3", "h4"):
            break

        if hasattr(node, "find_all"):
            for a in node.find_all("a", href=True):
                text = clean_text(a.get_text(" ", strip=True))
                href = a.get("href", "")
                if text:
                    results.append((text, href))

        node = node.find_next_sibling()

    return results


def normalize_weapon_name(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"^\d+\s*", "", text)
    text = re.sub(r"\bR\s*\d+\b", "", text).strip()

    for suffix in STAT_SUFFIXES:
        if text.endswith(suffix):
            text = text[:-len(suffix)].strip()
            break

    return clean_text(text)


def normalize_artifact_name(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"^\d+\s*", "", text)
    text = re.sub(r"\s+\d+$", "", text).strip()
    return clean_text(text)


def extract_top_weapon(soup: BeautifulSoup) -> str:
    build_heading = find_first_heading(soup, ["best", "build"])
    if not build_heading:
        return ""

    weapon_heading = find_section_heading_after(build_heading, ["weapon"])
    if not weapon_heading:
        return ""

    links = collect_links_until_next_heading(weapon_heading)
    for text, href in links:
        if "/weapon/" in href or text:
            name = normalize_weapon_name(text)
            if name:
                return name

    return ""


def extract_top_artifact(soup: BeautifulSoup) -> str:
    build_heading = find_first_heading(soup, ["best", "build"])
    if not build_heading:
        return ""

    artifact_heading = find_section_heading_after(build_heading, ["artifact"])
    if not artifact_heading:
        return ""

    links = collect_links_until_next_heading(artifact_heading)
    for text, href in links:
        if "/artifact/" in href or text:
            name = normalize_artifact_name(text)
            if name:
                return name

    return ""


def slug_from_img(img_tag) -> str:
    alt = clean_text(img_tag.get("alt", ""))
    if alt:
        alt_slug = normalize_slug_text(alt)
        if alt_slug not in IGNORE_ICON_SLUGS:
            return alt_slug

    src = img_tag.get("src", "") or ""
    m = re.search(r"/characters/([^/?#]+)", src)
    if m:
        slug = normalize_slug_text(m.group(1))
        if slug not in IGNORE_ICON_SLUGS:
            return slug

    return ""


def extract_top_team(soup: BeautifulSoup) -> str:
    team_heading = find_first_heading(soup, ["best", "teams"])
    if not team_heading:
        team_heading = find_first_heading(soup, ["best", "team"])
    if not team_heading:
        return ""

    chars = []
    node = team_heading.find_next()

    while node:
        name = getattr(node, "name", None)

        if name == "h2":
            break

        if name == "img":
            slug = slug_from_img(node)
            if slug:
                if not chars or chars[-1] != slug:
                    chars.append(slug)

                if len(chars) == 4:
                    return "/".join(chars)

        node = node.find_next()

    return ""


def is_invalid_row(row: dict) -> bool:
    return (
        not row["파티"] or
        not row["무기"] or
        not row["세트"]
    )


def scrape_one(name: str) -> dict:
    slug = NAME_TO_SLUG[name]
    url = f"{BASE}/en/character/{slug}"
    soup = get_soup(url)

    weapon = extract_top_weapon(soup)
    artifact = extract_top_artifact(soup)
    team = extract_top_team(soup)

    row = {
        "캐릭": name,
        "파티": team,
        "무기": weapon,
        "세트": artifact,
    }

    if is_invalid_row(row):
        missing = []
        if not row["파티"]:
            missing.append("파티")
        if not row["무기"]:
            missing.append("무기")
        if not row["세트"]:
            missing.append("세트")
        raise ValueError(f"데이터 비어있음: {', '.join(missing)}")

    return row


def main():
    rows = []
    failures = []

    for i, name in enumerate(TARGET_CHARACTERS, 1):
        print(f"[{i}/{len(TARGET_CHARACTERS)}] {name}")

        try:
            row = scrape_one(name)
            rows.append(row)

        except Exception as e:
            failures.append((name, str(e)))

        time.sleep(0.4)

    csv_path = os.path.join(BASE_DIR, "genshin_character_party_weapon_set.csv")
    fail_path = os.path.join(BASE_DIR, "genshin_failures.txt")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["캐릭", "파티", "무기", "세트"])
        writer.writeheader()
        writer.writerows(rows)

    with open(fail_path, "w", encoding="utf-8") as f:
        for name, err in failures:
            f.write(f"{name}\t{err}\n")

    print(f"saved: {csv_path}")
    print(f"saved: {fail_path}")
    print(f"성공: {len(rows)}개")
    print(f"실패: {len(failures)}개")


if __name__ == "__main__":
    main()