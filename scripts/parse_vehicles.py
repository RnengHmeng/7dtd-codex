# -*- coding: utf-8 -*-
"""Parse vehicles (placeable items) + speed from vehicles.xml."""
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\vehicles_v34.json"

csv.field_size_limit(10 ** 9)
COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")

SLOTS = {"vengine": "引擎", "vlight": "车灯", "vseat": "座位", "vfuel": "油箱",
         "vstorage": "储物", "varmor": "车体装甲", "vplow": "车铲"}
SKIP = {"vehicleJokeblimp", "vehicleBicyclePlaceableAdmin"}


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


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(key, fallback=""):
        if not key:
            return fallback
        return clean(zh.get(key, "")) or clean(en.get(key, "")) or fallback

    # speed table from vehicles.xml: vehicleBicycle -> max velocityMax_turbo
    speeds = {}
    vroot = ET.parse(CFG + r"\vehicles.xml").getroot()
    for v in vroot.iter("vehicle"):
        props = {p.get("name"): p.get("value") for p in v.findall("property")}
        raw = props.get("velocityMax_turbo") or props.get("velocityMax")
        if raw:
            try:
                speeds[v.get("name")] = max(float(x) for x in raw.split(","))
            except ValueError:
                pass

    items = ET.parse(CFG + r"\items.xml").getroot()
    out = []
    for it in items.iter("item"):
        name = it.get("name")
        props = {p.get("name"): p.get("value") for p in it.findall("property") if p.get("class") is None}
        tags = [x.strip() for x in (props.get("Tags") or "").split(",") if x.strip()]
        if "vehicle" not in tags or name in SKIP:
            continue
        dur = mods = None
        for pe in it.iter("passive_effect"):
            if pe.get("name") == "DegradationMax" and pe.get("operation") == "base_set":
                dur = float(pe.get("value").split(",")[0])
            if pe.get("name") == "ModSlots" and pe.get("operation") == "base_set":
                mods = int(float(pe.get("value").split(",")[-1]))
        base = name.replace("Placeable", "")
        out.append({
            "id": name,
            "name": t(base, base),
            "name_en": clean(en.get(base, "")),
            "tier": next((x for x in tags if re.fullmatch(r"T\d", x)), ""),
            "durability": dur,
            "modslots": mods,
            "slots": [SLOTS[x] for x in tags if x in SLOTS],
            "speed": speeds.get(base),
            "desc": t(base + "Desc"),
        })

    out.sort(key=lambda v: (v["tier"] or "T9", v["name"]))
    json.dump({"vehicles": out}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("vehicles:", len(out))
    for v in out:
        print("  ", v["tier"], v["name"], "| 耐久", v["durability"], "| 槽", v["modslots"],
              "| 极速", v["speed"], "|", v["slots"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
