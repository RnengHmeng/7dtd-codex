# -*- coding: utf-8 -*-
"""Render the full item compendium page."""
import html
import json
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\items_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4全物品图鉴.html"
GAME_VERSION = "V 3.4.0 (b9)"

CATS = ["武器", "弹药", "工具", "护甲", "食物药品", "书籍", "资源", "其他"]
CAT_COLOR = {"武器": "#e0574c", "弹药": "#e08a3c", "工具": "#e2b03c", "护甲": "#57b95f",
             "食物药品": "#7fd487", "书籍": "#49b6e8", "资源": "#8fa3ad", "其他": "#7d7367"}

CSS = """
:root{--bg:#100e0c;--panel:#1a1714;--line:#332b24;--text:#e8e1d8;--dim:#a2988c;
  --accent:#e8a33d;--accent2:#c8762a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.65 "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif}
a{color:var(--accent);text-decoration:none}
.wrap{max-width:1240px;margin:0 auto;padding:0 20px 80px}
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
.chipbtn{font-size:13px;padding:5px 11px;border:1px solid var(--line);border-radius:20px;
  color:var(--text);background:var(--panel);cursor:pointer;font-family:inherit}
.chipbtn:hover{border-color:var(--accent);color:var(--accent)}
.chipbtn.on{background:var(--accent);color:#1a1208;border-color:var(--accent);font-weight:700}
.chipbtn small{opacity:.65;margin-left:4px;font-size:11px}
.search{display:flex;align-items:center;gap:6px;background:var(--panel);
  border:1px solid var(--line);border-radius:20px;padding:4px 12px}
.search input{background:transparent;border:0;outline:0;color:var(--text);
  font-size:13px;width:210px;font-family:inherit}
table.items{width:100%;border-collapse:separate;border-spacing:0;font-size:13px;
  background:var(--panel);border:1px solid var(--line);border-radius:8px}
table.items th{position:sticky;top:0;z-index:6;background:#211c18;color:#cdbfa9;
  font-size:11.5px;font-weight:600;text-align:left;padding:9px 10px;
  border-bottom:1px solid var(--line);box-shadow:0 1px 0 #332b24;white-space:nowrap}
table.items td{padding:7px 10px;border-bottom:1px solid #241f1b;vertical-align:top;color:#c9bdad}
table.items tr:last-child td{border-bottom:0}
table.items tr:hover td{background:#1f1a16}
td.n{color:#e8dccb;font-weight:600;min-width:150px}
td.n em{font-style:normal;color:#6f665c;font-size:10.5px;font-weight:400;margin-left:6px}
.pill{font-size:10.5px;padding:1px 7px;border-radius:10px;background:#2a231d;white-space:nowrap}
.badge{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:4px;margin:1px 4px 1px 0;
  border:1px solid #4a3a24;color:#d9b477;background:#2a2118;white-space:nowrap}
.badge.loot{color:#8fa3ad;border-color:#33414a;background:#1d2529}
.badge.trader{color:#c58ae0;border-color:#43304a;background:#251c2a}
td.mat{font-size:11.5px;color:#b9ab97;min-width:280px;line-height:1.5}
td.mat .rline + .rline{border-top:1px dashed #2c2520;margin-top:4px;padding-top:4px}
td.mat .st{color:#e8a33d}
td.src{min-width:110px}
.none{color:#5a5148}
footer{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
.hide{display:none!important}
@media (max-width:760px){
  .search input{width:120px}
  table.items{font-size:12px}
  table.items td,table.items th{padding:6px 7px}
  td.mat{min-width:0}
}
@media print{body{background:#fff;color:#000}nav.jump{display:none}
  table.items,table.items td,table.items th{background:#fff;color:#000;border-color:#ccc}}
"""

JS = r"""
(function(){
  var rows=[].slice.call(document.querySelectorAll('table.items tbody tr'));
  var btns=[].slice.call(document.querySelectorAll('.chipbtn[data-f]'));
  var q=document.getElementById('q');
  var filter='all';
  function apply(){
    var v=(q.value||'').trim().toLowerCase();
    rows.forEach(function(r){
      var okF = filter==='all' || r.dataset.f.indexOf(filter)!==-1;
      var okT = !v || r.dataset.text.indexOf(v)!==-1;
      r.classList.toggle('hide', !(okF && okT));
    });
  }
  btns.forEach(function(b){ b.addEventListener('click', function(){
    filter=b.dataset.f;
    btns.forEach(function(x){ x.classList.toggle('on', x===b); });
    apply();
  }); });
  q.addEventListener('input', apply);
  document.addEventListener('keydown', function(e){
    if(e.key==='/' && document.activeElement!==q){ e.preventDefault(); q.focus(); }
    if(e.key==='Escape' && document.activeElement===q){ q.value=''; apply(); q.blur(); }
  });
})();
"""


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def build():
    data = json.load(open(JSON_IN, encoding="utf-8"))
    items = data["items"]
    n_craft = sum(1 for i in items if i["recipes"])
    n_loot = sum(1 for i in items if i["loot"])
    n_trader = sum(1 for i in items if i["trader"])

    out = []
    w = out.append
    w("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    w("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    w("<title>七日杀 V3.4 全物品图鉴</title>")
    w("<style>" + CSS + "</style></head><body><div class='wrap'>")

    w("<header class='top'><h1>七日杀 · 全物品图鉴<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据取自本机 <code>items.xml</code>、<code>recipes.xml</code>、"
      "<code>loot.xml</code>、<code>traders.xml</code> 与 <code>Localization.csv</code>"
      "<br>生成时间 %s ｜ %d 种物品 · %d 种可制作 · %d 种可搜刮 · %d 种商人出售</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), len(items), n_craft, n_loot, n_trader))
    w("<div class='sub' style='margin-top:8px'>「设施」是制作地点（随身 / 工作台 / 锻造炉 / 营火 / 化学工作台 / 水泥搅拌机）；"
      "没有配方的物品在「来源」里标出搜刮或商人。同一物品有多条配方时分行显示。"
      "<br><span style='color:#e8a33d'>⁺</span> 表示该材料数量会随制作品质提高而增加（游戏内 1–6 档不同）。</div></header>")

    w("<nav class='jump'><div class='navrow'>")
    w("<button class='chipbtn on' data-f='all'>全部<small>%d</small></button>" % len(items))
    w("<button class='chipbtn' data-f='craft'>可制作<small>%d</small></button>" % n_craft)
    w("<button class='chipbtn' data-f='loot'>可搜刮<small>%d</small></button>" % n_loot)
    w("<button class='chipbtn' data-f='trader'>商人<small>%d</small></button>" % n_trader)
    for c in CATS:
        n = sum(1 for i in items if i["cat"] == c)
        if n:
            w("<button class='chipbtn' data-f='%s'>%s<small>%d</small></button>" % (c, c, n))
    w("<span class='spacer'></span>")
    w("<label class='search'>🔍<input id='q' type='search' placeholder='搜索物品'></label>")
    w("</div></nav>")

    w("<table class='items'><thead><tr><th>物品</th><th>类别</th>"
      "<th>设施</th><th>配方</th><th>来源</th></tr></thead><tbody>")
    for it in items:
        flags = []
        if it["recipes"]:
            flags.append("craft")
        if it["loot"]:
            flags.append("loot")
        if it["trader"]:
            flags.append("trader")
        flags.append(it["cat"])
        blob = " ".join([it["name"], it["name_en"], it["cat"]]).lower()

        w("<tr id='%s' data-f='%s' data-text='%s'>" % (e(it["id"]), " ".join(flags), e(blob)))
        w("<td class='n'>%s<em>%s</em></td>" % (e(it["name"]), e(it["name_en"])))
        w("<td><span class='pill' style='color:%s'>%s</span></td>"
          % (CAT_COLOR.get(it["cat"], "#8b8175"), e(it["cat"])))

        # facilities
        if it["recipes"]:
            seen, badges = set(), []
            for rc in it["recipes"]:
                key = rc["area"] + ("·" + rc["tool"] if rc["tool"] else "")
                if key in seen:
                    continue
                seen.add(key)
                badges.append("<span class='badge'>%s</span>" % e(key))
            w("<td>%s</td>" % "".join(badges))
        else:
            w("<td><span class='none'>—</span></td>")

        # recipe lines
        if it["recipes"]:
            lines = []
            multi = len(it["recipes"]) > 1
            for rc in it["recipes"]:
                st = ("<span class='st'>%s</span> " % e(rc["area"] + ("·" + rc["tool"] if rc["tool"] else ""))) if multi else ""
                mark = "⁺" if rc.get("scaled") else ""
                mats = " · ".join("%s×%d%s" % (e(m["n"]), m["c"], mark) for m in rc["ings"]) or "—"
                lines.append("<div class='rline'>%s%s</div>" % (st, mats))
            w("<td class='mat'>%s</td>" % "".join(lines))
        else:
            w("<td class='mat'><span class='none'>—</span></td>")

        # sources
        src = []
        if it["loot"]:
            src.append("<span class='badge loot'>搜刮</span>")
        if it["trader"]:
            src.append("<span class='badge trader'>商人</span>")
        if not it["recipes"] and not src:
            src.append("<span class='none'>—</span>")
        w("<td class='src'>%s</td></tr>" % "".join(src))
    w("</tbody></table>")

    w("<footer>数据来源：本机 <code>Data/Config/items.xml</code>（物品）、<code>recipes.xml</code>（配方与设施）、"
      "<code>loot.xml</code>（搜刮表）、<code>traders.xml</code>（商人货单）。"
      "<br>说明：搜刮/商人只表示「该物品出现在对应表里」，具体掉落率与货架刷新受游戏阶段影响；"
      "已排除开发/测试物品与无中文名的内部条目。"
      "<br>游戏更新后重新运行 <code>parse_items.py</code> 与 <code>render_items_sheet.py</code> 即可刷新。</footer>")
    w("</div><script>" + JS + "</script></body></html>")

    open(OUT_HTML, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
