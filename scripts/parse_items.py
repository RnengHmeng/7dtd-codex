# -*- coding: utf-8 -*-
"""Build the full item compendium: every localized item with recipes + sources."""
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\items_v34.json"

csv.field_size_limit(10 ** 9)
COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")

AREAS = {"campfire": "营火", "workbench": "工作台", "chemistryStation": "化学工作台",
         "forge": "锻造炉", "cementMixer": "水泥搅拌机"}
TOOLS = {"toolCookingPot": "烹饪锅", "toolCookingGrill": "烤架", "toolBeaker": "烧杯",
         "toolForgeCrucible": "坩埚"}

CAT_ORDER = ["武器", "弹药", "工具", "护甲", "食物药品", "书籍", "资源", "其他"]


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


def cat_of(tags, name):
    tags = set(tags)
    if "food" in tags or "medical" in tags or name.startswith(("food", "medical", "drug")):
        return "食物药品"
    if "armor" in tags or name.startswith("armor"):
        return "护甲"
    if "ammo" in tags or name.startswith("ammo"):
        return "弹药"
    if "tool" in tags or name.startswith("meleeTool"):
        return "工具"
    if "weapon" in tags or name.startswith(("gun", "meleeWpn")):
        return "武器"
    if "book" in tags or "magazine" in tags or name.startswith(("book", "magazine")) or "SkillMagazine" in name:
        return "书籍"
    if "resource" in tags or name.startswith("resource"):
        return "资源"
    return "其他"


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(k, fb=""):
        return (clean(zh.get(k, "")) or clean(en.get(k, "")) or fb) if k else fb

    # recipes: name -> [ {area, tool, ingredients} ]
    recipes = {}
    for rec in ET.parse(CFG + r"\recipes.xml").getroot().iter("recipe"):
        rn = rec.get("name")
        if not rn:
            continue
        ings = [{"id": i.get("name"), "c": int(float(i.get("count", "1")))}
                for i in rec.findall("ingredient")]
        scaled = any(pe.get("name") == "CraftingIngredientCount"
                     for pe in rec.iter("passive_effect"))
        recipes.setdefault(rn, []).append({
            "area": AREAS.get(rec.get("craft_area", ""), "") or "随身制作",
            "tool": TOOLS.get(rec.get("craft_tool", ""), ""),
            "ings": ings,
            "scaled": scaled,
        })

    loot = {el.get("name") for el in ET.parse(CFG + r"\loot.xml").getroot().iter("item")}
    trader = set()
    for el in ET.parse(CFG + r"\traders.xml").getroot().iter("item"):
        if el.get("name"):
            trader.add(el.get("name"))

    out = []
    for it in ET.parse(CFG + r"\items.xml").getroot().iter("item"):
        name = it.get("name")
        if name not in zh or not (zh[name] or en.get(name)):
            continue
        props = {p.get("name"): p.get("value") for p in it.findall("property") if p.get("class") is None}
        if props.get("CreativeMode") in ("Dev", "Test"):
            continue
        tags = [x.strip() for x in (props.get("Tags") or "").split(",") if x.strip()]
        if props.get("Hidden") == "true":
            continue
        recs = []
        for rc in recipes.get(name, []):
            recs.append({
                "area": rc["area"], "tool": rc["tool"], "scaled": rc["scaled"],
                "ings": [{"n": t(i["id"], i["id"]), "c": i["c"]} for i in rc["ings"]],
            })
        out.append({
            "id": name,
            "name": t(name, name),
            "name_en": clean(en.get(name, "")),
            "cat": cat_of(tags, name),
            "recipes": recs,
            "loot": name in loot,
            "trader": name in trader,
        })

    out.sort(key=lambda x: (CAT_ORDER.index(x["cat"]) if x["cat"] in CAT_ORDER else 99, x["name"]))
    model = {"items": out}
    json.dump(model, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    import collections
    c = collections.Counter(x["cat"] for x in out)
    print("items:", len(out), dict(c))
    print("with recipe:", sum(1 for x in out if x["recipes"]),
          "| loot:", sum(1 for x in out if x["loot"]),
          "| trader:", sum(1 for x in out if x["trader"]))
    print("sample:", [(x["name"], x["cat"], len(x["recipes"])) for x in out[:5]])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
