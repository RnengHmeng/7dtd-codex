# -*- coding: utf-8 -*-
"""Render the zombie bestiary page."""
import html
import json
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\zombies_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4丧尸图鉴.html"
GAME_VERSION = "V 3.4.0 (b9)"

CSS = """
:root{--bg:#100e0c;--panel:#1a1714;--line:#332b24;--text:#e8e1d8;--dim:#a2988c;
  --accent:#e8a33d;--accent2:#c8762a;--red:#e0574c}
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
nav.jump{position:sticky;top:0;z-index:20;background:rgba(16,14,12,.97);
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
section.cat{margin:0 0 40px}
.cat-head{display:flex;align-items:baseline;gap:12px;padding-bottom:10px;
  border-bottom:2px solid var(--line);margin-bottom:16px}
.cat-head .bar{width:6px;height:24px;border-radius:3px;display:inline-block}
.cat-head h2{margin:0;font-size:20px}
.cat-head .cnt{margin-left:auto;color:var(--dim);font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px}
.zfam{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:13px 15px}
.zhead{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:8px}
.zhead h3{margin:0;font-size:16px;color:#f3eadc}
.zhead em{font-style:normal;font-size:11px;color:#7d7367;margin-left:6px}
.ztags{margin-left:auto;font-size:11px;color:#8b8175}
table.zvar{width:100%;border-collapse:collapse;font-size:12.5px}
table.zvar th{text-align:left;color:#7d7367;font-weight:400;font-size:11px;
  padding:2px 4px;border-bottom:1px solid #2c2520}
table.zvar td{padding:4px;border-bottom:1px dashed #2c2520;color:#c9bdad}
table.zvar tr:last-child td{border-bottom:0}
table.zvar td.v{color:#e8dccb;font-weight:600}
table.zvar td.v.feral{color:#e08a72}
table.zvar td.v.rad{color:#7fd487}
.hp{color:#ef8377;font-weight:700}
.note{color:#7d7367;font-size:11px;margin-top:6px}
footer{margin-top:36px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
.hide{display:none!important}
@media (max-width:620px){.grid{grid-template-columns:1fr}.search input{width:110px}}
@media print{body{background:#fff;color:#000}nav.jump{display:none}
  .zfam{background:#fff;border-color:#ccc;break-inside:avoid}
  .zhead h3,table.zvar td{color:#000}}
"""

JS = r"""
(function(){
  var btns=[].slice.call(document.querySelectorAll('.chipbtn[data-cat]'));
  var secs=[].slice.call(document.querySelectorAll('section.cat'));
  var cards=[].slice.call(document.querySelectorAll('.zfam'));
  var q=document.getElementById('q'); var cat='all';
  function filter(){
    var v=(q.value||'').trim().toLowerCase();
    cards.forEach(function(c){
      c.classList.toggle('hide',(cat!=='all'&&c.dataset.cat!==cat)||(!!v&&c.dataset.text.indexOf(v)===-1));
    });
    secs.forEach(function(s){s.classList.toggle('hide',s.querySelectorAll('.zfam:not(.hide)').length===0);});
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


def fnum(v):
    if v is None:
        return "—"
    v = float(v)
    return str(int(round(v))) if abs(v - round(v)) < 0.05 else ("%.2f" % v).rstrip("0").rstrip(".")


def vclass(name):
    return {"凶残": "feral", "辐射": "rad", "带电": "rad"}.get(name, "")


def build():
    data = json.load(open(JSON_IN, encoding="utf-8"))
    fams = data["families"]
    zs = [f for f in fams if "动物" not in f["tags"]]
    animals = [f for f in fams if "动物" in f["tags"]]

    out = []
    w = out.append
    w("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    w("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    w("<title>七日杀 V3.4 丧尸图鉴</title>")
    w("<style>" + CSS + "</style></head><body><div class='wrap'>")

    w("<header class='top'><h1>七日杀 · 丧尸图鉴<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据取自本机 <code>entityclasses.xml</code> 与 <code>Localization.csv</code>"
      "<br>生成时间 %s ｜ %d 个丧尸系 · %d 个动物系 · 共 %d 个实体</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), len(zs), len(animals),
         sum(len(f["variants"]) for f in fams)))
    w("<div class='sub' style='margin-top:8px'>血量是<strong>基础血量</strong>；凶残/辐射变体单独列出，"
      "速度是 <code>MoveSpeedAggro</code> 的「走 / 跑」值（游戏内相对速度）。</div>")
    w("</header>")

    w("<nav class='jump'><div class='navrow'>")
    w("<button class='chipbtn on' data-cat='all'>全部<small>%d</small></button>" % len(fams))
    w("<button class='chipbtn' data-cat='zombie'>丧尸<small>%d</small></button>" % len(zs))
    w("<button class='chipbtn' data-cat='animal'>动物<small>%d</small></button>" % len(animals))
    w("<span class='spacer'></span>")
    w("<label class='search'>🔍<input id='q' type='search' placeholder='搜索丧尸 / 动物'></label>")
    w("</div></nav>")

    for cid, title, members in (("zombie", "丧尸", zs), ("animal", "动物", animals)):
        w("<section class='cat' id='%s'>" % cid)
        w("<div class='cat-head'><span class='bar' style='background:%s'></span>"
          "<h2>%s</h2><span class='cnt'>%d 系</span></div>"
          % ("#e0574c" if cid == "zombie" else "#57b95f", title, len(members)))
        w("<div class='grid'>")
        for f in members:
            blob = " ".join([f["name"], f["name_en"]] + f["tags"] + f["biomes"]).lower()
            w("<article class='zfam' id='%s' data-cat='%s' data-text='%s'>" % (e(f["id"]), cid, e(blob)))
            w("<div class='zhead'><h3>%s<em>%s</em></h3>" % (e(f["name"]), e(f["name_en"])))
            tagline = " · ".join(f["tags"] + f["biomes"])
            w("<span class='ztags'>%s</span></div>" % e(tagline))
            w("<table class='zvar'><tr><th>变体</th><th>血量</th><th>经验</th><th>速度</th></tr>")
            for v in f["variants"]:
                sp = " / ".join(fnum(x) for x in v["speed"]) if v["speed"] else "—"
                w("<tr><td class='v %s'>%s</td><td class='hp'>%s</td><td>%s</td><td>%s</td></tr>"
                  % (vclass(v["variant"]), e(v["variant"]), fnum(v["hp"]), fnum(v["xp"]), e(sp)))
            w("</table></article>")
        w("</div></section>")

    w("<footer>数据来源：本机 <code>Data/Config/entityclasses.xml</code>（血量/经验/速度/标签）与 "
      "<code>Localization.csv</code>。掉落物在游戏里由战利品表随机生成，因此没有逐项列出。"
      "<br>游戏更新后重新运行 <code>parse_zombies.py</code> 与 <code>render_zombies_sheet.py</code> 即可刷新。</footer>")
    w("</div><script>" + JS + "</script></body></html>")

    open(OUT_HTML, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
