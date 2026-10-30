# -*- coding: utf-8 -*-
"""Parse 7 Days to Die progression.xml + Localization.csv into a JSON model."""
import csv, json, re, sys
import xml.etree.ElementTree as ET

GAME = r"E:\Steam\steamapps\common\7 Days To Die"
CFG = GAME + r"\Data\Config"
OUT_JSON = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\perks_v34.json"

csv.field_size_limit(10 ** 9)

COLOR_RE = re.compile(r"\[[0-9A-Fa-f]{6}\]|\[-\]")
MAIN_ATTRS = ["attPerception", "attStrength", "attFortitude", "attAgility", "attIntellect", "attGeneralPerks"]


def clean(s):
    if not s:
        return ""
    s = s.replace("\\n", "\n").replace("\\t", " ")
    s = COLOR_RE.sub("", s)
    s = s.replace("\r", "")
    return s.strip()


def load_loc():
    loc = {"schinese": {}, "english": {}}
    with open(CFG + r"\Localization.csv", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        idx = {n: i for i, n in enumerate(header)}
        i_s, i_e, i_t = idx["schinese"], idx["english"], idx["tchinese"]
        for row in r:
            if not row or not row[0]:
                continue
            k = row[0]
            zh = row[i_s] if i_s < len(row) else ""
            tw = row[i_t] if i_t < len(row) else ""
            en = row[i_e] if i_e < len(row) else ""
            loc["schinese"][k] = zh or tw
            loc["english"][k] = en
    return loc


def main():
    loc = load_loc()
    zh, en = loc["schinese"], loc["english"]

    def t(key, fallback=""):
        if not key:
            return fallback
        v = clean(zh.get(key, ""))
        if not v:
            v = clean(en.get(key, ""))
        return v or fallback

    tree = ET.parse(CFG + r"\progression.xml")
    root = tree.getroot()

    lvl = root.find("level")
    level_info = {
        "max_level": int(lvl.get("max_level", "300")),
        "skill_points_per_level": int(lvl.get("skill_points_per_level", "1")),
        "exp_to_level": int(lvl.get("exp_to_level", "10000")),
        "experience_multiplier": lvl.get("experience_multiplier", "1.05"),
    }

    # ---- skills -> attribute map, skill display names; book groups
    skill_parent, skill_name = {}, {}
    book_groups = []
    for sk in root.find("skills"):
        if sk.tag == "skill":
            skill_parent[sk.get("name")] = sk.get("parent")
            skill_name[sk.get("name")] = t(sk.get("name_key"), sk.get("name"))
        elif sk.tag == "book_group":
            skill_parent[sk.get("name")] = sk.get("parent")
            skill_name[sk.get("name")] = t(sk.get("name_key"), sk.get("name"))
            book_groups.append({
                "id": sk.get("name"),
                "name": t(sk.get("name_key"), sk.get("name")),
                "name_en": clean(en.get(sk.get("name_key", ""), "")),
                "desc": t(sk.get("desc_key")),
                "icon": sk.get("icon", ""),
            })

    def reqs_of(node):
        out = {}
        for lr in node.findall("level_requirements"):
            info = {"attr_level": None, "cost": None, "desc": ""}
            for rq in lr.findall("requirement"):
                if rq.get("name") == "ProgressionLevel":
                    try:
                        info["attr_level"] = int(float(rq.get("value")))
                    except Exception:
                        pass
                dk = rq.get("desc_key", "")
                if dk.startswith("reqGenericPoints"):
                    digits = re.sub(r"\D", "", dk)
                    if digits:
                        info["cost"] = int(digits)
                if dk and not info["desc"]:
                    info["desc"] = t(dk)
            out[int(lr.get("level"))] = info
        return out

    def ranks_of(node):
        out = {}
        for ed in node.iter("effect_description"):
            short = t(ed.get("desc_key"))
            long_ = t(ed.get("long_desc_key"))
            out[int(ed.get("level"))] = {"short": short, "long": long_ or short}
        return out

    # ---- attributes
    attributes = []
    for at in root.find("attributes"):
        name = at.get("name")
        if name not in MAIN_ATTRS:
            continue
        attributes.append({
            "id": name,
            "name": t(at.get("name_key"), name),
            "name_en": clean(en.get(at.get("name_key", ""), "")),
            "desc": t(at.get("desc_key")),
            "icon": at.get("icon", ""),
            "reqs": reqs_of(at),
            "ranks": ranks_of(at),
        })

    # ---- perks (only point-buyable ones: 5 attributes + general)
    perks, all_perks = [], []
    for p in root.find("perks"):
        pid = p.get("name")
        parent = p.get("parent", "")
        attr = parent if parent in MAIN_ATTRS else skill_parent.get(parent, "")
        item = {
            "id": pid,
            "name": t(p.get("name_key"), pid),
            "name_en": clean(en.get(p.get("name_key", ""), "")),
            "desc": t(p.get("desc_key")),
            "attr": attr,
            "group": parent,
            "group_name": skill_name.get(parent, ""),
            "icon": p.get("icon", ""),
            "reqs": reqs_of(p),
            "ranks": ranks_of(p),
        }
        all_perks.append(item)
        if attr in MAIN_ATTRS:
            perks.append(item)

    perks.sort(key=lambda x: (MAIN_ATTRS.index(x["attr"]), x["group"], x["id"]))

    # attach book-group perk counts
    for bg in book_groups:
        bg["perk_count"] = sum(1 for p in all_perks if p["group"] == bg["id"])

    # ---- book volumes (items.xml): item name + DescriptionKey + Unlocks perk
    perk_group = {p["id"]: p["group"] for p in all_perks}
    perk_by_id = {p["id"]: p for p in all_perks}
    vols_by_group = {}
    items_tree = ET.parse(CFG + r"\items.xml")
    for item in items_tree.getroot().iter("item"):
        iname = item.get("name") or ""
        if not iname.startswith("book"):
            continue
        props = {pr.get("name"): pr.get("value") for pr in item.findall("property")}
        unlocks = props.get("Unlocks") or ""
        group = perk_group.get(unlocks, "")
        if group not in {b["id"] for b in book_groups}:
            continue
        vols_by_group.setdefault(group, []).append({
            "item": iname,
            "perk": unlocks,
            "name": t(iname, iname),
            "name_en": clean(en.get(iname, "")),
            "desc": t(props.get("DescriptionKey", "")),
        })
    for bg in book_groups:
        vols = vols_by_group.get(bg["id"], [])
        bg["volumes"] = vols
        comp = next((p for p in all_perks
                     if p["group"] == bg["id"] and p["id"].endswith("Complete")), None)
        if comp:
            bg["complete"] = {"name": comp["name"], "desc": comp["desc"]}
            bg["volumes"] = [v for v in vols if v["perk"] != comp["id"]]
        if bg["volumes"]:
            bg["volume_count"] = len(bg["volumes"])
        else:
            bg["volume_count"] = max(bg["perk_count"] - 1, 0)

    # ---- crafting skills (magazines)
    magazines = []
    cs_root = root.find("crafting_skills")
    if cs_root is not None:
        for cs in cs_root:
            magazines.append({
                "id": cs.get("name"),
                "name": t(cs.get("name_key"), cs.get("name")),
                "name_en": clean(en.get(cs.get("name_key", ""), "")),
                "desc": t(cs.get("long_desc_key") or cs.get("desc_key")),
                "max_level": cs.get("max_level", ""),
            })

    model = {
        "level": level_info,
        "attributes": attributes,
        "perks": perks,
        "book_groups": book_groups,
        "magazines": magazines,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=1)

    print("attributes", len(attributes), "perks", len(perks),
          "book groups", len(book_groups), "magazines", len(magazines))
    for a in attributes:
        n = sum(1 for p in perks if p["attr"] == a["id"])
        print("  ", a["id"], a["name"], a["name_en"], "->", n, "perks; ranks", len(a["ranks"]))
    missing = [p["id"] for p in perks if len(p["ranks"]) < 1]
    print("perks without rank text:", missing)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
