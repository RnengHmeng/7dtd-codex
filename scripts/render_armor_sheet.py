# -*- coding: utf-8 -*-
"""Render the parsed armor model into a single self-contained Chinese HTML sheet
with a quality (1-6) slider that re-renders every number."""
import html
import json
import sys
from datetime import datetime

JSON_IN = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\armor_v34.json"
OUT_HTML = r"C:\Users\RunHao\Documents\ChatGPT\fgo小助手\七日杀V3.4装甲速查表.html"
PERK_PAGE = "七日杀V3.4天赋速查表.html"
GAME_VERSION = "V 3.4.0 (b9)"
QS = [1, 2, 3, 4, 5, 6]

CLS_META = {
    "light": {"color": "#57b95f", "emoji": "🥾", "intro":
              "没有移动和噪音惩罚，护甲值最低（满品质每件 12.3，全套 49.2）。"
              "适合跑图、潜行和长距离搜刮，靠模组和套装效果吃饭。"},
    "medium": {"color": "#49b6e8", "emoji": "🧥", "intro":
               "每件 -5% 移动速度、-2.8% 走动体力、-5.6% 跑动体力、+10% 噪音，"
               "护甲值中等（满品质 17.3/件）。四件套合计移动 -20%、噪音 +40%。"},
    "heavy": {"color": "#e0574c", "emoji": "🛡", "intro":
              "每件 -7.5% 移动速度、-4.5% 走动体力、-9% 跑动体力、+20% 噪音，"
              "护甲值最高（满品质 21/件）。四件套合计移动 -30%、跑动体力 -36%、噪音 +80%。"},
}

PEN_ORDER = [("mobility", "移动"), ("walk", "走动体力"), ("run", "跑动体力"), ("noise", "噪音")]

CSS = """
:root{
  --bg:#100e0c; --panel:#1a1714; --panel2:#221d19; --line:#332b24;
  --text:#e8e1d8; --dim:#a2988c; --accent:#e8a33d; --accent2:#c8762a;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.65 "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif;}
a{color:var(--accent);text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 80px}
header.top{padding:34px 0 18px;border-bottom:1px solid var(--line)}
h1{margin:0 0 6px;font-size:27px;letter-spacing:.5px}
h1 .ver{font-size:14px;color:var(--accent);border:1px solid var(--accent2);
  border-radius:4px;padding:2px 7px;margin-left:10px;vertical-align:middle}
.sub{color:var(--dim);font-size:13px}
.sub code{background:#251f1a;padding:1px 5px;border-radius:3px;color:#d8c9b6}
.rules{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:22px 0 4px}
.rule{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:6px;padding:12px 14px}
.rule b{display:block;color:var(--accent);font-size:13px;letter-spacing:.5px;margin-bottom:4px}
.rule span{color:var(--dim);font-size:13px}
.rule span em{color:var(--text);font-style:normal}

.cmp{width:100%;border-collapse:collapse;margin:24px 0 6px;font-size:13.5px;
  background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.cmp th,.cmp td{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left}
.cmp th{color:#cdbfa9;font-size:12.5px;font-weight:600;background:#211c18}
.cmp td:first-child{color:var(--dim);white-space:nowrap}
.cmp tr:last-child td{border-bottom:0}
.cmp .c-light{color:#7fd487}.cmp .c-medium{color:#6ec6ef}.cmp .c-heavy{color:#ef8377}
.cmp .tot{font-size:12.5px;color:#c8bcaa}
.note{color:#8b8175;font-size:12px;margin:8px 0 0;line-height:1.7}
.note strong{color:#c4b8a9}

nav.jump{position:sticky;top:0;z-index:20;background:rgba(16,14,12,.97);
  border-bottom:1px solid var(--line);padding:10px 0 8px;margin:26px 0}
.navrow{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.navrow .spacer{flex:1}
.chipbtn{font-size:13px;padding:5px 12px;border:1px solid var(--line);border-radius:20px;
  color:var(--text);background:var(--panel);cursor:pointer;font-family:inherit}
.chipbtn:hover{border-color:var(--accent);color:var(--accent)}
.chipbtn.on{background:var(--accent);color:#1a1208;border-color:var(--accent);font-weight:700}
.search{display:flex;align-items:center;gap:6px;background:var(--panel);
  border:1px solid var(--line);border-radius:20px;padding:4px 12px}
.search input{background:transparent;border:0;outline:0;color:var(--text);
  font-size:13px;width:190px;font-family:inherit}
.search input::placeholder{color:#6f665c}

section.cls{margin:0 0 46px;scroll-margin-top:76px}
.cls-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;
  padding:0 0 10px;border-bottom:2px solid var(--line);margin-bottom:8px}
.cls-head .bar{width:6px;height:26px;border-radius:3px;display:inline-block}
.cls-head h2{margin:0;font-size:21px}
.cls-head .en{color:var(--dim);font-size:13px;letter-spacing:1px}
.cls-head .cnt{margin-left:auto;color:var(--dim);font-size:12px}
.cls-intro{color:#c4b8a9;font-size:13.5px;margin:0 0 18px;max-width:900px}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(370px,1fr));gap:14px}
.set{background:var(--panel);border:1px solid var(--line);border-radius:9px;overflow:hidden;
  display:flex;flex-direction:column}
.shead{display:flex;align-items:center;gap:9px;padding:12px 15px 10px;flex-wrap:wrap}
.shead h3{margin:0;font-size:17px;color:#f3eadc}
.shead h3 em{font-style:normal;font-weight:400;font-size:11.5px;color:#7d7367;
  letter-spacing:.4px;margin-left:7px}
.badge{font-size:11px;font-weight:700;padding:2px 8px;border-radius:11px;color:#141210}
.badge.light{background:#57b95f}.badge.medium{background:#49b6e8}.badge.heavy{background:#e0574c}
.pieces-n{margin-left:auto;font-size:11.5px;color:var(--dim)}
.setq{display:flex;align-items:center;gap:9px;padding:0 15px 9px}
.setq .qlbl{font-size:11px;color:#8b8175;letter-spacing:.5px;white-space:nowrap}
.setq input[type=range]{-webkit-appearance:none;appearance:none;width:160px;height:5px;
  border-radius:3px;background:linear-gradient(90deg,#4a3c2b,#c8762a,#e8a33d);outline:0}
.setq input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;
  border-radius:50%;background:#f3eadc;border:3px solid var(--accent);cursor:pointer;
  box-shadow:0 0 5px rgba(232,163,61,.55)}
.setq input[type=range]::-moz-range-thumb{width:12px;height:12px;border-radius:50%;
  background:#f3eadc;border:3px solid var(--accent);cursor:pointer}
.setq .qnow{font-size:12.5px;color:var(--accent);font-weight:700;min-width:12px}
.strip{display:flex;flex-wrap:wrap;gap:6px 14px;padding:0 15px 10px;font-size:12px;color:var(--dim)}
.strip b{color:#e2d5c3;font-weight:600}
.penline{padding:0 15px 10px;font-size:11.5px;color:#c08a5a}
.penline.ok{color:#6f9a72}
.plist{list-style:none;margin:0;padding:0 15px;border-top:1px solid var(--line)}
.prow{display:grid;grid-template-columns:40px 1fr;gap:10px;padding:10px 0;
  border-bottom:1px dashed #2c2520}
.prow:last-child{border-bottom:0}
.slot{font-size:11.5px;color:#9a8f80;background:#241e19;border:1px solid #332b24;
  border-radius:4px;text-align:center;padding:2px 0;height:20px;line-height:16px}
.pname{font-size:13.5px;color:#e8dccb;font-weight:600}
.pname em{font-style:normal;font-weight:400;font-size:10.5px;color:#6f665c;margin-left:6px}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin:4px 0 0}
.chips i{font-style:normal;font-size:11px;color:#d9b477;background:#2a2118;
  border:1px solid #4a3a24;border-radius:4px;padding:1px 6px;white-space:nowrap}
.chips i b{font-weight:700;color:#f0c98a}
.chips i.dev{color:#e08a72;border-color:#4a2f24;background:#291b16}
.chips i.dev b{color:#ef9d83}
.pdesc{margin:4px 0 0;font-size:11.5px;color:#8f857a;line-height:1.55}
.sbonus{margin:auto 0 0;padding:11px 15px 13px;background:#1e1a16;border-top:1px solid var(--line)}
.btitle{font-size:11.5px;color:var(--accent);font-weight:700;letter-spacing:.5px;margin-bottom:3px}
.sbonus .flavor{margin:0 0 4px;font-size:11.5px;color:#7f766b;font-style:italic}
.sbonus .eff{margin:0;font-size:12.5px;color:#d8c9b4}
.sbonus .none{margin:0;font-size:12px;color:#6f665c}
.qv{display:none}
.qv.on{display:inline}

.appendix{margin-top:52px;padding-top:22px;border-top:2px solid var(--line)}
.appendix h2{font-size:19px;margin:0 0 10px}
.appendix p{color:var(--dim);font-size:13px;margin:0 0 12px}
.perkrow{display:grid;grid-template-columns:150px 1fr;gap:12px;padding:9px 0;
  border-top:1px dashed #2c2520;font-size:12.5px;color:#c2b6a6}
.perkrow b{color:#e8dccb;font-size:13px}
.perkrow small{display:block;color:#7d7367;font-size:11px}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);
  color:#6f665c;font-size:12px;line-height:1.9}
.hide{display:none !important}
@media (max-width:620px){
  .grid{grid-template-columns:1fr}
  .search input{width:100px}
  h1{font-size:22px}
  .cmp{font-size:12px}
  .cmp th,.cmp td{padding:7px 8px}
  .setq input[type=range]{width:120px}
}
@media print{
  body{background:#fff;color:#000}
  nav.jump,.setq{display:none}
  .set{background:#fff;border-color:#ccc;break-inside:avoid}
  .sbonus{background:#f6f4f1}
  .shead h3,.pname,.pdesc,.sbonus .eff,.cmp td{color:#000}
}
"""

JS = r"""
(function(){
  function trim(x){
    var r = Math.round(x * 10) / 10;
    if (Math.abs(r - Math.round(r)) < 0.0001) return String(Math.round(r));
    return String(r);
  }
  var FMT = {
    num:   function(v){ return trim(v); },
    pct:   function(v){ var x = Math.round(v * 1000) / 10; return (x > 0 ? '+' : '') + trim(x) + '%'; },
    raw:   function(v){ return (v > 0 ? '+' : '') + trim(v); },
    mult:  function(v){ return '×' + trim(1 + v); },
    const: function(){ return '消除'; }
  };

  function applyTo(root, q){
    q = Math.max(1, Math.min(6, q));
    var nodes = root.querySelectorAll('[data-vals]');
    for (var i = 0; i < nodes.length; i++){
      var el = nodes[i];
      var vals = el.getAttribute('data-vals').split(',');
      var v = parseFloat(vals[q - 1]);
      var f = FMT[el.getAttribute('data-fmt')] || FMT.num;
      el.textContent = f(v);
    }
    var spans = root.querySelectorAll('.qv');
    for (var j = 0; j < spans.length; j++){
      spans[j].classList.toggle('on', spans[j].getAttribute('data-q') === String(q));
    }
  }

  // one independent quality slider per armor set card
  var cards = [].slice.call(document.querySelectorAll('.set'));
  cards.forEach(function(card){
    var slider = card.querySelector('.qslider');
    var qnow = card.querySelector('.setq .qnow');
    if (!slider) return;
    function sync(){
      var q = parseInt(slider.value, 10);
      if (qnow) qnow.textContent = q;
      applyTo(card, q);
    }
    slider.addEventListener('input', sync);
    slider.addEventListener('change', sync);
    card.querySelector('.setq').addEventListener('mousedown', function(ev){ ev.stopPropagation(); });
    sync();
  });

  // class filter + search
  var btns = [].slice.call(document.querySelectorAll('.chipbtn[data-cls]'));
  var secs = [].slice.call(document.querySelectorAll('section.cls'));
  var q = document.getElementById('q');
  var cls = 'all';

  function filter(){
    var v = (q.value || '').trim().toLowerCase();
    cards.forEach(function(c){
      var okCls = (cls === 'all' || c.dataset.cls === cls);
      var okTxt = !v || c.dataset.text.indexOf(v) !== -1;
      c.classList.toggle('hide', !(okCls && okTxt));
    });
    secs.forEach(function(s){
      s.classList.toggle('hide', s.querySelectorAll('.set:not(.hide)').length === 0);
    });
  }
  btns.forEach(function(b){
    b.addEventListener('click', function(){
      cls = b.dataset.cls;
      btns.forEach(function(x){ x.classList.toggle('on', x === b); });
      filter();
    });
  });
  q.addEventListener('input', filter);
  document.addEventListener('keydown', function(ev){
    var tag = (document.activeElement && document.activeElement.type) || '';
    if (ev.key === '/' && document.activeElement !== q && tag !== 'range'){
      ev.preventDefault(); q.focus();
    }
    if (ev.key === 'Escape' && document.activeElement === q){ q.value=''; filter(); q.blur(); }
  });
})();
"""


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def trim(x):
    x = round(float(x), 1)
    if abs(x - round(x)) < 0.0001:
        return str(int(round(x)))
    return ("%.1f" % x).rstrip("0").rstrip(".")


def fmt_val(vals, fmt, q=6):
    v = float(vals[q - 1])
    if fmt == "const":
        return "消除"
    if fmt == "mult":
        return "×" + trim(1 + v)
    if fmt == "pct":
        x = round(v * 100, 1)
        return ("+" if x > 0 else "") + trim(x) + "%"
    if fmt == "raw":
        return ("+" if v > 0 else "") + trim(v)
    return trim(v)


def vals_attr(vals):
    return ",".join(("%g" % float(v)) for v in vals)


def pct(v):
    x = round(float(v) * 100, 1)
    return ("+" if x > 0 else "") + trim(x) + "%"


def split_bonus(desc):
    chunks = [c.strip() for c in (desc or "").split("\n\n") if c.strip()]
    if len(chunks) > 1:
        return chunks[0], "\n\n".join(chunks[1:])
    return "", (chunks[0] if chunks else "")


def build():
    with open(JSON_IN, encoding="utf-8") as f:
        m = json.load(f)
    classes = m["classes"]
    sets = m["sets"]
    q = 6

    out = []
    w = out.append
    w("<!DOCTYPE html>")
    w('<html lang="zh-CN"><head><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w("<title>七日杀 V3.4 装甲速查表</title>")
    w("<style>" + CSS + "</style>")
    w("</head><body><div class='wrap'>")

    total_vol = sum(len(s["pieces"]) for s in sets) + len(m["singles"])
    w("<header class='top'>")
    w("<h1>七日杀 · 装甲速查表<span class='ver'>%s</span></h1>" % e(GAME_VERSION))
    w("<div class='sub'>数据取自本机 <code>Data/Config/items.xml</code>、"
      "<code>buffs.xml</code>、<code>Localization.csv</code>（简体中文）"
      "<br>生成时间 %s ｜ %d 套护甲 · %d 件装备 · 轻甲 %d 套 / 中甲 %d 套 / 重甲 %d 套</div>"
      % (datetime.now().strftime("%Y-%m-%d %H:%M"), len(sets), total_vol,
         classes["light"]["count_sets"], classes["medium"]["count_sets"], classes["heavy"]["count_sets"]))
    w("<div class='sub' style='margin-top:8px'>"
      "<span style='color:#e8a33d'>品质滑杆：</span>每套卡片标题下面有自己的 1–6 滑杆，"
      "拖动即可切换该套的护甲值、耐久、模组槽、逐件词条和 4 件套奖励，方便两套并排比较。<br>"
      "<span style='color:#e8a33d'>筛选：</span>按轻/中/重筛选，搜索框可搜套装名、部位名和效果（按 "
      "<code>/</code> 聚焦）。<br>"
      "<span style='color:#e8a33d'>配套页面：</span>"
      "<a href='七日杀V3.4武器速查表.html'>武器速查表</a> · "
      "<a href='七日杀V3.4模组速查表.html'>模组速查表</a>（护甲模组在这里）· "
      "<a href='七日杀V3.4天赋速查表.html'>天赋速查表</a></div>")
    w("</header>")

    w("<div class='rules'>")
    w("<div class='rule'><b>同一件装备，6 个品质</b>"
      "<span>品质 1 是刚捡到的样子，6 是满品质。数值随品质线性成长，用上面的滑杆逐级对比。</span></div>")
    w("<div class='rule'><b>护甲值 = 物理减伤</b>"
      "<span>面板上的<em>护甲等级</em>走的是物理伤害减免；元素抗性只对 "
      "<em>热、电</em> 生效，数值和护甲值相同。</span></div>")
    w("<div class='rule'><b>4 件套奖励</b>"
      "<span>同套装穿满 <em>4 件</em>才触发，数值看 4 件里<em>最低品质</em>那一件。</span></div>")
    w("</div>")

    # ---- comparison table (static 1 -> 6 ranges)
    L, M, H = classes["light"], classes["medium"], classes["heavy"]

    def range_cell(vals, color="", multiply=1, use_slash=False):
        cls_attr = (" class='%s'" % color) if color else ""
        vv = [v * multiply for v in vals]
        if use_slash:
            text = " / ".join(trim(v) for v in vv)
        else:
            text = "%s → %s" % (trim(vv[0]), trim(vv[-1]))
        return "<td%s>%s</td>" % (cls_attr, e(text))

    w("<table class='cmp'>")
    w("<tr><th>对比项</th><th class='c-light'>轻甲 Light</th>"
      "<th class='c-medium'>中甲 Medium</th><th class='c-heavy'>重甲 Heavy</th></tr>")

    def row(label, a_html, b_html, c_html):
        w("<tr><td>%s</td>%s%s%s</tr>" % (label, a_html, b_html, c_html))

    row("单件护甲值", range_cell(L["armor"], "c-light"), range_cell(M["armor"], "c-medium"),
        range_cell(H["armor"], "c-heavy"))
    row("全套护甲值", range_cell(L["armor"], "c-light", multiply=4),
        range_cell(M["armor"], "c-medium", multiply=4),
        range_cell(H["armor"], "c-heavy", multiply=4))
    row("元素抗性（热/电）", range_cell(L["element"], "c-light"),
        range_cell(M["element"], "c-medium"), range_cell(H["element"], "c-heavy"))
    row("单件耐久", range_cell(L["durability"], "c-light"),
        range_cell(M["durability"], "c-medium"), range_cell(H["durability"], "c-heavy"))
    row("模组槽", range_cell(L["modslots"], "c-light", use_slash=True),
        range_cell(M["modslots"], "c-medium", use_slash=True),
        range_cell(H["modslots"], "c-heavy", use_slash=True))
    row("移动速度 / 件", "<td>无</td>", "<td>%s</td>" % pct(M["pen"]["mobility"]),
        "<td>%s</td>" % pct(H["pen"]["mobility"]))
    row("跑动体力 / 件", "<td>无</td>", "<td>%s</td>" % pct(M["pen"]["run"]),
        "<td>%s</td>" % pct(H["pen"]["run"]))
    row("噪音 / 件", "<td>无</td>", "<td>%s</td>" % pct(M["pen"]["noise"]),
        "<td>%s</td>" % pct(H["pen"]["noise"]))
    row("4 件套合计", "<td class='tot'>无惩罚</td>",
        "<td class='tot'>移动 -20% · 跑动体力 -22.5% · 噪音 +40%</td>",
        "<td class='tot'>移动 -30% · 跑动体力 -36% · 噪音 +80%</td>")
    row("套装数量", "<td>%d 套</td>" % L["count_sets"], "<td>%d 套</td>" % M["count_sets"],
        "<td>%d 套</td>" % H["count_sets"])
    w("<tr><td>对应天赋</td><td><a href='%s#attGeneralPerks'>轻甲</a></td>"
      "<td><a href='%s#attGeneralPerks'>中型护甲</a></td>"
      "<td><a href='%s#attGeneralPerks'>重甲护身</a></td></tr>\n"
      % (e(PERK_PAGE), e(PERK_PAGE), e(PERK_PAGE)))
    w("</table>")
    w("<p class='note'>表格给的是<strong>品质 1 → 6 的区间</strong>；具体某一级看每套卡片上的滑杆。</p>")
    w("<p class='note'>粗糙套装（新手装）例外：模组槽只有 1→2，其余套装是 2→5。</p>")
    w("<p class='note'>体力相关数值正数代表更省体力，负数是惩罚；噪音正数是更吵。"
      "所有数值都是<strong>单件</strong>效果，穿 4 件就叠加 4 次。</p>")

    # ---- nav (filters + search only; quality lives on each card)
    w("<nav class='jump'>")
    w("<div class='navrow'>")
    w("<button class='chipbtn on' data-cls='all'>全部</button>")
    w("<button class='chipbtn' data-cls='light'>轻甲</button>")
    w("<button class='chipbtn' data-cls='medium'>中甲</button>")
    w("<button class='chipbtn' data-cls='heavy'>重甲</button>")
    w("<span class='spacer'></span>")
    w("<label class='search'>🔍<input id='q' type='search' placeholder='搜索套装 / 部位 / 效果'></label>")
    w("</div>")
    w("</nav>")

    # ---- sections
    for cls in ("light", "medium", "heavy"):
        meta = CLS_META[cls]
        c = classes[cls]
        members = [s for s in sets if s["cls"] == cls]
        w("<section class='cls' id='%s'>" % cls)
        w("<div class='cls-head'><span class='bar' style='background:%s'></span>"
          "<h2>%s %s</h2><span class='en'>%s Armor</span>"
          "<span class='cnt'>%d 套 · 每套 4 件</span></div>"
          % (meta["color"], meta["emoji"], e(c["name"]), e(c["name_en"]), len(members)))
        w("<p class='cls-intro'>%s</p>" % meta["intro"])
        w("<div class='grid'>")
        for s in members:
            blob = " ".join([s["name"], s["name_en"]] +
                            [p["name"] + " " + p["name_en"] + " " + p["desc"] +
                             " " + " ".join(x["k"] for x in p["chips"]) for p in s["pieces"]])
            w("<article class='set' data-cls='%s' data-text='%s'>" % (cls, e(blob.lower())))
            w("<div class='shead'><span class='badge %s'>%s</span>"
              "<h3>%s<em>%s</em></h3><span class='pieces-n'>%d 件</span></div>"
              % (cls, e(c["name"]), e(s["name"]), e(s["name_en"]), len(s["pieces"])))
            w("<div class='setq'><span class='qlbl'>品质</span>"
              "<input class='qslider' type='range' min='1' max='6' step='1' value='6' "
              "aria-label='%s 品质'>"
              "<b class='qnow'>6</b></div>" % e(s["name"]))

            st = s["stats"]
            tags = "热/电" if "heat" in (st.get("element_tags") or "") else "元素"
            w("<div class='strip'>"
              "<span>护甲 <b data-vals='%s' data-fmt='num'>%s</b></span>"
              "<span>元素抗 <b data-vals='%s' data-fmt='num'>%s</b> "
              "<span style='font-size:10.5px'>(%s)</span></span>"
              "<span>耐久 <b data-vals='%s' data-fmt='num'>%s</b></span>"
              "<span>槽位 <b data-vals='%s' data-fmt='num'>%s</b></span></div>"
              % (vals_attr(st["armor"]), e(fmt_val(st["armor"], "num", q)),
                 vals_attr(st["element"]), e(fmt_val(st["element"], "num", q)), tags,
                 vals_attr(st["durability"]), e(fmt_val(st["durability"], "num", q)),
                 vals_attr(st["modslots"]), e(fmt_val(st["modslots"], "num", q))))

            parts = []
            for key, label in PEN_ORDER:
                v = s["pen"].get(key, {}).get("vals") if key in s["pen"] else None
                cls_v = c["pen"].get(key)
                if v:
                    parts.append("%s %s" % (label, pct(v[q - 1])))
                elif cls_v not in (None, 0):
                    parts.append("%s 无" % label)
            if parts:
                w("<div class='penline'>每件：%s</div>" % e(" · ".join(parts)))
            else:
                w("<div class='penline ok'>无移动 / 体力 / 噪音惩罚</div>")

            w("<ul class='plist'>")
            for p in s["pieces"]:
                w("<li class='prow'><span class='slot'>%s</span><div>" % e(p["slot"]))
                w("<div class='pname'>%s<em>%s</em></div>" % (e(p["name"]), e(p["name_en"])))
                if p["chips"]:
                    items = []
                    for ch in p["chips"]:
                        items.append("<i class='%s'>%s <b data-vals='%s' data-fmt='%s'>%s</b></i>"
                                     % ("dev" if ch.get("dev") else "", e(ch["k"]),
                                        vals_attr(ch["vals"]), e(ch["fmt"]),
                                        e(fmt_val(ch["vals"], ch["fmt"], q))))
                    w("<div class='chips'>%s</div>" % "".join(items))
                if p["desc"]:
                    w("<p class='pdesc'>%s</p>" % e(p["desc"]).replace("\n", "<br>"))
                w("</div></li>")
            w("</ul>")

            w("<div class='sbonus'><div class='btitle'>4 件套奖励"
              "<span style='color:#7d7367;font-weight:400'> · 随最低品质变化</span></div>")
            if s["bonus"]["qdesc"][0]:
                flavor, _ = split_bonus(s["bonus"]["qdesc"][0])
                if flavor:
                    w("<p class='flavor'>%s</p>" % e(flavor))
                w("<p class='eff'>")
                for qi in QS:
                    _, eff = split_bonus(s["bonus"]["qdesc"][qi - 1])
                    w("<span class='qv%s' data-q='%d'>%s</span>"
                      % (" on" if qi == q else "", qi, e(eff).replace("\n", "<br>")))
                w("</p>")
            else:
                w("<p class='none'>新手装，没有套装奖励。</p>")
            w("</div></article>")
        w("</div></section>")

    # ---- appendix
    w("<div class='appendix'>")
    if m["singles"]:
        w("<h2>单件护甲</h2><p>不组成套装、也没有 4 件套奖励的护甲。</p>")
        for p in m["singles"]:
            chips = ""
            if p["chips"]:
                chips = "<div class='chips'>%s</div>" % "".join(
                    "<i>%s <b data-vals='%s' data-fmt='%s'>%s</b></i>"
                    % (e(ch["k"]), vals_attr(ch["vals"]), e(ch["fmt"]),
                       e(fmt_val(ch["vals"], ch["fmt"], q)))
                    for ch in p["chips"])
            w("<div class='perkrow'><b>%s<br><small>%s</small></b><div>%s%s</div></div>"
              % (e(p["name"]), e(p["name_en"]), chips, e(p["desc"])))

    w("<h2 style='margin-top:30px'>护甲天赋怎么减轻惩罚</h2>")
    w("<p>三个通用天赋分别对应一类护甲；点满 4 级后的效果：</p>")
    w("<div class='perkrow'><b>轻甲<small>Light Armor</small></b><div>"
      "耐久消耗 -15% / -30% / -45% / -60%；每装备一件轻甲额外 +1 / +2 / +3 / +4 护甲值。"
      "</div></div>")
    w("<div class='perkrow'><b>中型护甲<small>Medium Armor</small></b><div>"
      "中甲移动惩罚 -15% / -30% / -50% / -75%，体力惩罚 -10% / -20% / -35% / -50%，"
      "耐久消耗 -15% / -30% / -45% / -60%。</div></div>")
    w("<div class='perkrow'><b>重甲护身<small>Heavy Armor</small></b><div>"
      "重甲移动与体力惩罚 -5% / -10% / -17% / -25%，耐久消耗 -15% / -30% / -45% / -60%。"
      "</div></div>")
    w("<p style='margin-top:12px'>完整每级数值见 <a href='%s#attGeneralPerks'>天赋速查表 · 通用天赋</a>。</p>"
      % e(PERK_PAGE))
    w("</div>")

    w("<footer>数据来源：本机 <code>7 Days to Die</code> 安装目录下 "
      "<code>Data/Config/items.xml</code>（护甲与逐件效果）、<code>buffs.xml</code>（4 件套奖励）、"
      "<code>Localization.csv</code>（中文文本）。"
      "<br>品质数值按游戏文件里的 <code>tier</code> 区间线性展开成 1–6 级；"
      "被排除的开发/试玩物品：%s。游戏更新后重新运行 "
      "<code>parse_armor.py</code> 与 <code>render_armor_sheet.py</code> 即可刷新。"
      "</footer>" % e("、".join(m.get("skipped", [])))
      )
    w("</div><script>" + JS + "</script></body></html>")

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote", OUT_HTML, len("\n".join(out)) // 1024, "KB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
