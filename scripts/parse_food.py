# -*- coding: utf-8 -*-
"""Parse food / water / medical items from items.xml (nutrition lives in CVars)."""
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\consumables_v34.json"

csv.field_size_limit(10 ** 9)
COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")

CVAIRS = {
    "$foodAmountAdd": "food",
    "$waterAmountAdd": "water",
    "foodHealthAmount": "health",
    "medicalRegHealthAmount": "heal",
    ".foodStaminaBonusAdd": "stamina",
    "$buffInfectionAddCurePerc": "cure",
}
TAGS = {
    "canned": "罐头", "meat": "肉类", "vegetable": "蔬菜", "fruit": "水果",
    "drink": "饮品", "caffeine": "咖啡因", "alcohol": "酒精",
    "stopsBleeding": "止血", "cureInfection": "抗感染", "painRelief": "止痛",
    "medical": "医疗", "drug": "药物", "vitamins": "维生素",
}


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


def cat_of(dt, tags):
    if dt.startswith("foodWater") or "drink" in tags:
        return "drink"
    if dt.startswith("medical") or dt.startswith("cureInfection") or dt.startswith("drug"):
        return "medical"
    if dt.startswith("foodRaw") or "raw" in dt:
        return "raw"
    if dt.startswith("food"):
        return "food"
    return "medical"


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(key, fallback=""):
        if not key:
            return fallback
        return clean(zh.get(key, "")) or clean(en.get(key, "")) or fallback

    root = ET.parse(CFG + r"\items.xml").getroot()
    items = {it.get("name"): it for it in root.iter("item")}

    def props_of(it):
        return {p.get("name"): p.get("value") for p in it.findall("property") if p.get("class") is None}

    def chain(name):
        out, cur = [], name
        while cur and cur in items:
            out.append(items[cur])
            cur = props_of(items[cur]).get("Extends", "").split(",")[0].strip() or None
        return out

    out = []
    for it in root.iter("item"):
        p = props_of(it)
        dt = p.get("DisplayType", "") or ""
        tags = [x.strip() for x in (p.get("Tags") or "").split(",") if x.strip()]
        if not (dt.startswith("food") or dt.startswith("medical") or dt.startswith("cureInfection")
                or dt.startswith("drug") or "food" in tags or "medical" in tags):
            continue
        vals = {}
        for e in chain(it.get("name")):
            for te in e.iter("triggered_effect"):
                if te.get("action") != "ModifyCVar":
                    continue
                key = CVAIRS.get(te.get("cvar"))
                if not key or key in vals:
                    continue
                try:
                    vals[key] = float(te.get("value"))
                except (TypeError, ValueError):
                    pass
        if not vals:
            continue
        out.append({
            "id": it.get("name"),
            "name": t(it.get("name"), it.get("name")),
            "name_en": clean(en.get(it.get("name"), "")),
            "cat": cat_of(dt, tags),
            "dt": dt,
            "desc": t(p.get("DescriptionKey") or it.get("name") + "Desc"),
            "effect_tags": [TAGS[x] for x in tags if x in TAGS][:3],
            "food": vals.get("food"),
            "water": vals.get("water"),
            "health": vals.get("health"),
            "heal": vals.get("heal"),
            "stamina": vals.get("stamina"),
            "cure": vals.get("cure"),
        })

    order = {"food": 0, "raw": 1, "drink": 2, "medical": 3}
    out.sort(key=lambda x: (order.get(x["cat"], 9), -(x["food"] or 0), x["name"]))
    model = {"items": out}
    json.dump(model, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("items:", len(out))
    for c in ("food", "raw", "drink", "medical"):
        print("  ", c, sum(1 for x in out if x["cat"] == c))
    for x in out[:6]:
        print("   ", x["name"], x["cat"], "food", x["food"], "water", x["water"], "hp", x["health"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
