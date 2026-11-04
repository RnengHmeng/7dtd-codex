# -*- coding: utf-8 -*-
"""Render the vehicles page."""
import html
import json
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\vehicles_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4载具表.html"
GAME_VERSION = "V 3.4.0 (b9)"

CSS = """
:root{--bg:#100e0c;--panel:#1a1714;--line:#332b24;--text:#e8e1d8;--dim:#a2988c;
  --accent:#e8a33d;--accent2:#c8762a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.65 "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif}
a{color:var(--accent);text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 80px}
header.top{padding:34px 0 18px;border-bottom:1px solid var(--line)}
h1{margin:0 0 6px;font-size:27px}
h1 .ver{font-size:14px;color:var(--accent);border:1px solid var(--accent2);
  border-radius:4px;padding:2px 7px;margin-left:10px;vertical-align:middle}
.sub{color:var(--dim);font-size:13px}
.sub code{background:#251f1a;padding:1px 5px;border-radius:3px;color:#d8c9b6}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;margin-top:26px}
.vcard{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 16px 14px}
.vhead{display:flex;align-items:baseline;gap:9px;margin-bottom:10px}
.vhead h3{margin:0;font-size:18px;color:#f3eadc}
.vhead em{font-style:normal;font-size:11px;color:#7d7367}
.tier{margin-left:auto;font-size:11px;font-weight:700;color:#d9b477;border:1px solid #4a3a24;
  border-radius:4px;padding:1px 7px}
.stats{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12px;color:var(--dim);margin-bottom:10px}
.stats b{color:#e2d5c3}
.slots{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px}
.slots span{font-size:11px;color:#d9b477;background:#2a2118;border:1px solid #4a3a24;
  border-radius:4px;padding:1px 7px}
.desc{margin:0;font-size:12px;color:#8f857a;border-top:1px dashed #2c2520;padding-top:9px}
footer{margin-top:36px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
@media (max-width:620px){.grid{grid-template-columns:1fr}}
@media print{body{background:#fff;color:#000}
  .vcard{background:#fff;border-color:#ccc;break-inside:avoid}
  .vhead h3,.desc{color:#000}}
"""


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def build():
    data = json.load(open(JSON_IN, encoding="utf-8"))
    vs = data["vehicles"]

    out = []
    w = out.append
    w("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    w("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    w("<title>七日杀 V3.4 载具表</title>")
    w("<style>" + CSS + "</style></head><body><div class='wrap'>")

    w("<header class='top'><h1>七日杀 · 载具表<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据取自本机 <code>items.xml</code>（载具物品）与 <code>vehicles.xml</code>（速度）"
      "<br>生成时间 %s ｜ %d 台载具</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), len(vs)))
    w("<div class='sub' style='margin-top:8px'>耐久和模组槽来自载具物品；"
      "极速是 <code>velocityMax_turbo</code> 的相对值，只适合横向比较，不代表实际 km/h。</div></header>")

    w("<div class='grid'>")
    for v in vs:
        w("<article class='vcard' id='%s'>" % e(v["id"]))
        w("<div class='vhead'><h3>%s<em>%s</em></h3>%s</div>"
          % (e(v["name"]), e(v["name_en"]),
             ("<span class='tier'>%s</span>" % e(v["tier"])) if v["tier"] else ""))
        w("<div class='stats'>")
        if v["durability"]:
            w("<span>耐久 <b>%d</b></span>" % int(v["durability"]))
        if v["modslots"]:
            w("<span>模组槽 <b>%d</b></span>" % v["modslots"])
        if v["speed"]:
            w("<span>极速 <b>%s</b></span>" % ("%.1f" % v["speed"]).rstrip("0").rstrip("."))
        w("</div>")
        if v["slots"]:
            w("<div class='slots'>%s</div>" % "".join("<span>%s</span>" % e(s) for s in v["slots"]))
        if v["desc"]:
            w("<p class='desc'>%s</p>" % e(v["desc"]).replace("\n", "<br>"))
        w("</article>")
    w("</div>")

    w("<footer>数据来源：本机 <code>Data/Config/items.xml</code> 与 <code>vehicles.xml</code>，"
      "中文文本来自 <code>Localization.csv</code>。"
      "<br>游戏更新后重新运行 <code>parse_vehicles.py</code> 与 <code>render_vehicles_sheet.py</code> 即可刷新。</footer>")
    w("</div></body></html>")

    open(OUT_HTML, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
