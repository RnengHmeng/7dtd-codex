# -*- coding: utf-8 -*-
"""Render the consumables table page."""
import html
import json
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\consumables_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4食物药品表.html"
GAME_VERSION = "V 3.4.0 (b9)"

CATS = [("all", "全部", "#e8a33d"), ("food", "料理", "#e0574c"), ("raw", "生食", "#8fa3ad"),
        ("drink", "饮品", "#49b6e8"), ("medical", "药品", "#57b95f")]

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
nav.jump{position:relative;z-index:20;background:rgba(16,14,12,.97);
  border-bottom:1px solid var(--line);padding:10px 0;margin:26px 0}
.navrow{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.navrow .spacer{flex:1}
.chipbtn{font-size:13px;padding:5px 12px;border:1px solid var(--line);border-radius:20px;
  color:var(--text);background:var(--panel);cursor:pointer;font-family:inherit}
.chipbtn:hover{border-color:var(--accent);color:var(--accent)}
.chipbtn.on{background:var(--accent);color:#1a1208;border-color:var(--accent);font-weight:700}
.chipbtn small{opacity:.65;margin-left:4px;font-size:11px}
.search{display:flex;align-items:center;gap:6px;background:var(--panel);
  border:1px solid var(--line);border-radius:20px;padding:4px 12px}
.search input{background:transparent;border:0;outline:0;color:var(--text);
  font-size:13px;width:190px;font-family:inherit}
table.food{width:100%;border-collapse:separate;border-spacing:0;font-size:13.5px;
  background:var(--panel);border:1px solid var(--line);border-radius:8px}
table.food th{position:sticky;top:0;background:#211c18;color:#cdbfa9;font-size:12px;
  font-weight:600;text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);z-index:6;
  box-shadow:0 1px 0 #332b24}
table.food td{padding:8px 12px;border-bottom:1px solid #241f1b;color:#c9bdad}
table.food tr:last-child td{border-bottom:0}
table.food tr:hover td{background:#1f1a16}
table.food td.n{color:#e8dccb;font-weight:600}
table.food td.n em{font-style:normal;color:#6f665c;font-size:11px;font-weight:400;margin-left:6px}
table.food td.num{text-align:right;font-variant-numeric:tabular-nums;color:#d9b477;width:74px}
table.food td.num.zero{color:#5a5148}
.catpill{font-size:11px;padding:1px 7px;border-radius:10px;background:#2a231d;color:#b9ab97}
.catpill.food{color:#ef8377}.catpill.raw{color:#9aa8b0}
.catpill.drink{color:#6ec6ef}.catpill.medical{color:#7fd487}
.tags{color:#8b8175;font-size:11.5px}
footer{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
.hide{display:none!important}
@media (max-width:620px){
  .search input{width:110px}
  table.food{font-size:12px}
  table.food th,table.food td{padding:6px 7px}
  table.food td.num{width:52px}
}
@media print{body{background:#fff;color:#000}nav.jump{display:none}
  table.food,table.food td,table.food th{background:#fff;color:#000;border-color:#ccc}}
"""

JS = r"""
(function(){
  var rows=[].slice.call(document.querySelectorAll('table.food tbody tr'));
  var btns=[].slice.call(document.querySelectorAll('.chipbtn[data-cat]'));
  var q=document.getElementById('q'); var cat='all';
  function filter(){
    var v=(q.value||'').trim().toLowerCase();
    rows.forEach(function(r){
      var okCat=(cat==='all'||r.dataset.cat===cat);
      var okTxt=!v||r.dataset.text.indexOf(v)!==-1;
      r.classList.toggle('hide',!(okCat&&okTxt));
    });
  }
  btns.forEach(function(b){b.addEventListener('click',function(){
    cat=b.dataset.cat;btns.forEach(function(x){x.classList.toggle('on',x===b)});filter();});});
  q.addEventListener('input',filter);
  document.addEventListener('keydown',function(e){
    if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus();}
    if(e.key==='Escape'&&document.activeElement===q){q.value='';filter();q.blur();}
  });
})();
"""


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def num(v):
    if v is None:
        return ("0", "zero")
    v = float(v)
    if abs(v - round(v)) < 0.05:
        return (str(int(round(v))), "")
    return (("%.1f" % v).rstrip("0").rstrip("."), "")


def build():
    data = json.load(open(JSON_IN, encoding="utf-8"))
    items = data["items"]
    counts = {c: sum(1 for i in items if i["cat"] == c) for c in ("food", "raw", "drink", "medical")}

    out = []
    w = out.append
    w("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    w("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    w("<title>七日杀 V3.4 食物药品表</title>")
    w("<style>" + CSS + "</style></head><body><div class='wrap'>")

    w("<header class='top'><h1>七日杀 · 食物药品表<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据取自本机 <code>items.xml</code> 与 <code>Localization.csv</code>"
      "<br>生成时间 %s ｜ %d 种消耗品（料理 %d · 生食 %d · 饮品 %d · 药品 %d）</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), len(items),
         counts["food"], counts["raw"], counts["drink"], counts["medical"]))
    w("<div class='sub' style='margin-top:8px'>数值来自物品的食用/使用效果（食物、水、生命、治疗量）。"
      "生食大多需要烹饪，部分带疾病风险，表里只列数值。</div></header>")

    w("<nav class='jump'><div class='navrow'>")
    for cid, label, _ in CATS:
        n = len(items) if cid == "all" else counts.get(cid, 0)
        w("<button class='chipbtn%s' data-cat='%s'>%s<small>%d</small></button>"
          % (" on" if cid == "all" else "", cid, label, n))
    w("<span class='spacer'></span>")
    w("<label class='search'>🔍<input id='q' type='search' placeholder='搜索食物 / 药品'></label>")
    w("</div></nav>")

    w("<table class='food'><thead><tr><th>名称</th><th>类别</th>"
      "<th style='text-align:right'>食物</th><th style='text-align:right'>水</th>"
      "<th style='text-align:right'>生命</th><th style='text-align:right'>治疗</th>"
      "<th>标签</th></tr></thead><tbody>")
    for it in items:
        tags = " · ".join(it["effect_tags"])
        blob = " ".join([it["name"], it["name_en"], it["desc"], tags]).lower()
        w("<tr id='%s' data-cat='%s' data-text='%s'>" % (e(it["id"]), it["cat"], e(blob)))
        w("<td class='n'>%s<em>%s</em></td>" % (e(it["name"]), e(it["name_en"])))
        w("<td><span class='catpill %s'>%s</span></td>"
          % (it["cat"], {"food": "料理", "raw": "生食", "drink": "饮品", "medical": "药品"}[it["cat"]]))
        for key in ("food", "water", "health", "heal"):
            txt, cls = num(it.get(key))
            w("<td class='num %s'>%s</td>" % (cls, txt))
        w("<td class='tags'>%s</td></tr>" % e(tags))
    w("</tbody></table>")

    w("<footer>数据来源：本机 <code>Data/Config/items.xml</code>（食用效果写在该物品及其 Extends 父物品的 CVar 里）"
      "与 <code>Localization.csv</code>。"
      "<br>游戏更新后重新运行 <code>parse_food.py</code> 与 <code>render_food_sheet.py</code> 即可刷新。</footer>")
    w("</div><script>" + JS + "</script></body></html>")

    open(OUT_HTML, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
