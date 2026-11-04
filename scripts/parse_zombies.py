# -*- coding: utf-8 -*-
"""Parse zombie entities from entityclasses.xml."""
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\zombies_v34.json"

csv.field_size_limit(10 ** 9)
COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")

VARIANTS = [("", "普通", "Normal"), ("Feral", "凶残", "Feral"),
            ("Radiated", "辐射", "Radiated"), ("Charged", "带电", "Charged")]

KNOWN_TAGS = {
    "walker": "步行", "runner": "奔跑", "spider": "蜘蛛", "dog": "狗", "vulture": "秃鹫",
    "bear": "熊", "boar": "野猪", "wolf": "狼", "snake": "蛇", "bomber": "自爆",
    "cop": "吐酸", "demo": "拆迁", "wight": "夜魇", "boss": "首领", "animal": "动物",
    "zombie": "丧尸", "feral": "凶残", "radiated": "辐射", "charged": "带电",
    "sleeper": "睡眠", "scout": "侦察", "screamer": "尖叫", "spiderpounce": "扑击",
}
BIOMES = {"forest": "森林", "burnt": "焦土", "desert": "沙漠", "snow": "雪地",
          "wasteland": "荒地", "allbiome": "全群系", "pine": "松林"}


def clean(s):
    return COLOR_RE.sub("", (s or "").replace("\\n", "\n")).strip()


def load_loc():
    loc = {"schinese": {}, "english": {}}
    with open(CFG + r"\Localization.csv", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        h = next(r)
        idx = {n: i for i, n in enumerate(h)}
        for row in r:
            if not row or not row[0]:
                continue
            loc["schinese"][row[0]] = row[idx["schinese"]] or row[idx["tchinese"]]
            loc["english"][row[0]] = row[idx["english"]]
    return loc


def num(v, variables):
    if v is None:
        return None
    v = str(v).strip()
    if v.startswith("^"):
        v = variables.get(v[1:], "")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(key, fallback=""):
        if not key:
            return fallback
        return clean(zh.get(key, "")) or clean(en.get(key, "")) or fallback

    root = ET.parse(CFG + r"\entityclasses.xml").getroot()

    variables = {}
    for rp in root.iter("replace_passive_effect"):
        for p in rp.findall("property"):
            variables[p.get("name")] = p.get("value")

    families = {}
    for e in root.iter("entity_class"):
        name = e.get("name")
        props = {}
        for p in e.findall("property"):
            if p.get("class") is None:
                props[p.get("name")] = p.get("value")
        tags = [x.strip() for x in (props.get("Tags") or "").split(",") if x.strip()]
        if "zombie" not in tags and "animal" not in tags:
            continue
        if name.startswith("zombieTemplate") or name.startswith("animalTemplate"):
            continue

        hp = None
        for pe in e.iter("passive_effect"):
            if pe.get("name") == "HealthMax" and pe.get("operation") == "base_set":
                hp = num(pe.get("value"), variables)
                break
        xp = num(props.get("ExperienceGain"), variables)
        speed = None
        ms = props.get("MoveSpeedAggro") or props.get("MoveSpeed")
        if ms:
            parts = [num(x, variables) for x in ms.split(",")]
            parts = [p for p in parts if p is not None]
            if parts:
                speed = parts

        base, variant = name, ""
        for suffix, cn, enn in VARIANTS[1:]:
            if name.endswith(suffix):
                base, variant = name[: -len(suffix)], cn
                break
        variant = variant or "普通"

        fam = families.setdefault(base, {
            "id": base,
            "name": t(base, base),
            "name_en": clean(en.get(base, "")),
            "tags": [KNOWN_TAGS[x] for x in tags if x in KNOWN_TAGS and x not in
                     ("zombie", "feral", "radiated", "charged")],
            "biomes": [BIOMES[x] for x in tags if x in BIOMES],
            "variants": [],
            "drops": [],
        })
        fam["variants"].append({
            "variant": variant,
            "id": name,
            "hp": hp,
            "xp": xp,
            "speed": speed,
            "loot_prob": num(props.get("LootDropProb"), variables),
        })
        if props.get("LootDropEntityClass") and t(props["LootDropEntityClass"], "") not in fam["drops"]:
            fam["drops"].append(t(props["LootDropEntityClass"], ""))

    order = {"普通": 0, "凶残": 1, "辐射": 2, "带电": 3}
    out = []
    for fam in families.values():
        fam["variants"].sort(key=lambda v: order.get(v["variant"], 9))
        if not fam["variants"]:
            continue
        fam["hp"] = max((v["hp"] or 0) for v in fam["variants"])
        out.append(fam)
    out.sort(key=lambda f: (-(f["hp"] or 0), f["name"]))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"families": out}, f, ensure_ascii=False, indent=1)

    print("families:", len(out), "entities:", sum(len(f["variants"]) for f in out))
    for fam in out[:6]:
        print("  ", fam["name"], fam["tags"], "|", [(v["variant"], v["hp"], v["xp"], v["speed"]) for v in fam["variants"]])
    missing_hp = [f["name"] for f in out if not f["hp"]]
    print("no hp:", missing_hp[:8], "count", len(missing_hp))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
