# -*- coding: utf-8 -*-
import re, json, os, html

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT=os.path.join(BASE,"content")
OUT=BASE
ASSETS=os.path.join(OUT,"assets")
for d in (OUT,ASSETS,CONTENT): os.makedirs(d,exist_ok=True)
MASTER=os.path.join(CONTENT,"policy-master.md")
PLAY=os.path.join(CONTENT,"playbooks.md")
AUDF=os.path.join(CONTENT,"audience-guides.md")
TSF=os.path.join(CONTENT,"troubleshooting.md")

def rd(p): return open(p,encoding="utf-8").read() if os.path.exists(p) else ""
master_raw=rd(MASTER); play_raw=rd(PLAY); aud_raw=rd(AUDF); ts_raw=rd(TSF)

def strip_fm(t):
    if t.startswith("---"):
        parts=t.split("---",2)
        return parts[2].lstrip("\n") if len(parts)>=3 else t
    return t
master_body=strip_fm(master_raw); play_body=strip_fm(play_raw)
aud_body=strip_fm(aud_raw) if aud_raw else ""; ts_body=strip_fm(ts_raw) if ts_raw else ""

LAST_UPDATED="2026-07-04"

GROUPS={
 "A":{"title":"定例・マネジメント","type":"定例","emoji":"📋"},
 "B":{"title":"異常対応","type":"異常","emoji":"🚨"},
 "C":{"title":"変化・プロジェクト","type":"変化","emoji":"🔧"},
 "D":{"title":"予防・維持・システム","type":"予防","emoji":"🛡️"},
}
AUD={
 "S":{"key":"sales","title":"営業向け","emoji":"🤝","who":"営業"},
 "T":{"key":"tech","title":"技術向け","emoji":"🛠️","who":"生産技術・開発"},
 "M":{"key":"mfg","title":"製造向け","emoji":"🏭","who":"製造現場"},
 "P":{"key":"buy","title":"購買向け","emoji":"🧺","who":"購買・調達"},
 "V":{"key":"vendor","title":"外注先向け","emoji":"📦","who":"お取引先（社外共有可）"},
}

def esc(s): return html.escape(s, quote=True)
def inline(s):
    s=esc(s)
    s=re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s=s.replace("【要確認】", '<span class="ic-rev">【要確認】</span>')
    return s

def render_blocks(lines):
    out=[]; i=0; n=len(lines)
    def flush_para(buf):
        if buf: out.append("<p>"+inline(" ".join(buf).strip())+"</p>")
    while i<n:
        line=lines[i].rstrip("\n"); st=line.strip()
        if st=="": i+=1; continue
        if st.startswith("|"):
            tbl=[]
            while i<n and lines[i].strip().startswith("|"): tbl.append(lines[i].strip()); i+=1
            rows=[[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl]
            rows=[r for r in rows if not all(set(c)<=set("-: ") for c in r)]
            if rows:
                head=rows[0]; body=rows[1:]
                t='<div class="tbl-wrap"><table><thead><tr>'+"".join("<th>"+inline(c)+"</th>" for c in head)+"</tr></thead><tbody>"
                for r in body: t+="<tr>"+"".join("<td>"+inline(c)+"</td>" for c in r)+"</tr>"
                t+="</tbody></table></div>"; out.append(t)
            continue
        m=re.match(r"^(#{1,4})\s+(.*)$", st)
        if m:
            lvl=len(m.group(1)); txt=m.group(2).strip(); hid=""
            if "エスカレーション" in txt: hid=' id="esc"'
            tag={1:"h2",2:"h2",3:"h3",4:"h4"}.get(lvl,"h3")
            out.append(f"<{tag}{hid}>"+inline(txt)+f"</{tag}>"); i+=1; continue
        if st.startswith(">"):
            q=[]
            while i<n and lines[i].strip().startswith(">"): q.append(lines[i].strip()[1:].strip()); i+=1
            qt=" ".join([x for x in q if x])
            if "【要確認】" in qt:
                out.append('<div class="callout review"><span class="rev-badge">要確認</span><span>'+inline(qt.replace("【要確認】","").strip())+'</span></div>')
            else:
                out.append('<blockquote>'+inline(qt)+'</blockquote>')
            continue
        if re.match(r"^-\s*\[[ xX]\]\s+", st):
            items=[]
            while i<n and re.match(r"^-\s*\[[ xX]\]\s+", lines[i].strip()):
                items.append(re.sub(r"^-\s*\[[ xX]\]\s+","",lines[i].strip())); i+=1
            li=[]
            for it in items:
                star="★" in it; t=it.replace("★","").strip()
                cls="chk"+(" star" if star else "")
                badge='<span class="star-badge">重点</span>' if star else ""
                li.append(f'<li class="{cls}"><span class="cb"></span><span class="t">'+inline(t)+f'</span>{badge}</li>')
            out.append('<ul class="checklist">'+"".join(li)+"</ul>"); continue
        if re.match(r"^\d+\.\s+", st):
            items=[]
            while i<n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+","",lines[i].strip())); i+=1
            li=[]
            for it in items:
                star="★" in it; t=it.replace("★","").strip()
                badge='<span class="star-badge">重点</span>' if star else ""
                li.append("<li>"+inline(t)+badge+"</li>")
            out.append("<ol>"+"".join(li)+"</ol>"); continue
        mb=re.match(r"^\*\*(.+?)\*\*[:：]?\s*$", st)
        if mb: out.append("<h4>"+inline(mb.group(1))+"</h4>"); i+=1; continue
        if re.match(r"^-\s+", st):
            items=[]
            while i<n and re.match(r"^-\s+", lines[i].strip()) and not re.match(r"^-\s*\[",lines[i].strip()):
                items.append(re.sub(r"^-\s+","",lines[i].strip())); i+=1
            out.append("<ul>"+"".join("<li>"+inline(x)+"</li>" for x in items)+"</ul>"); continue
        buf=[st]; i+=1
        while i<n and lines[i].strip()!="" and not re.match(r"^(#|>|-|\d+\.|\|)", lines[i].strip()) and not re.match(r"^\*\*(.+?)\*\*[:：]?\s*$", lines[i].strip()):
            buf.append(lines[i].strip()); i+=1
        flush_para(buf)
    return "\n".join(out)

def plain_text(lines):
    t=" ".join(lines); t=re.sub(r"[#>*\-\[\]★|]"," ",t); t=re.sub(r"\s+"," ",t); return t.strip()

# ---------- parse playbook ----------
def parse_play(body):
    groups={}; order=[]; cur_g=None; cur_s=None
    for raw in body.split("\n"):
        line=raw.rstrip()
        mg=re.match(r"^#\s+([A-D])\.\s+(.*)$", line)
        ms=re.match(r"^##\s+([A-D][0-9]+(?:-[a-z])?)\.\s+(.*)$", line)
        if mg:
            cur_g=mg.group(1); groups.setdefault(cur_g,{"title":mg.group(2).strip(),"scenarios":[],"note":[]}); cur_s=None; continue
        if ms:
            cur_s={"id":ms.group(1),"title":ms.group(2).strip(),"group":cur_g,"lines":[]}
            groups[cur_g]["scenarios"].append(cur_s); order.append(cur_s); continue
        if line.startswith("# ") and "更新" in line: cur_g=None; cur_s=None; continue
        if cur_s is not None: cur_s["lines"].append(raw)
        elif cur_g is not None:
            if line.strip() and not line.startswith("---"): groups[cur_g]["note"].append(raw)
    return groups, order
pgroups, scenarios = parse_play(play_body)
sc_title={x["id"]:x["title"] for x in scenarios}
def slug(sid): return "s-"+sid.lower()+".html"

# ---------- parse audience guides ----------
def parse_aud(body):
    groups={}; order=[]; cur=None; cur_t=None
    for raw in body.split("\n"):
        line=raw.rstrip()
        mg=re.match(r"^#\s+([STMPV])\.\s+(.*)$", line)
        mt=re.match(r"^##\s+([STMPV][0-9]+)\.\s+(.*)$", line)
        if mg:
            cur=mg.group(1); groups.setdefault(cur,{"title":mg.group(2).strip(),"topics":[],"note":[]}); cur_t=None; continue
        if mt:
            cur_t={"id":mt.group(1),"title":mt.group(2).strip(),"aud":cur,"lines":[],"related":[]}
            groups[cur]["topics"].append(cur_t); order.append(cur_t); continue
        if line.startswith("# ") and "更新" in line: cur=None; cur_t=None; continue
        if cur_t is not None:
            m=re.match(r"^関連場面[:：]\s*(.+)$", line.strip())
            if m:
                cur_t["related"]=[x.strip() for x in re.split(r"[,、/\s]+", m.group(1)) if x.strip()]; continue
            cur_t["lines"].append(raw)
        elif cur is not None:
            if line.strip() and not line.startswith("---"): groups[cur]["note"].append(raw)
    return groups, order
agroups, atopics = parse_aud(aud_body) if aud_body else ({},[])
def aslug(tid): return "ag-"+tid.lower()+".html"
def ahub(code): return "aud-"+AUD[code]["key"]+".html"

# ---------- parse troubleshooting ----------
def parse_ts(body):
    entries=[]; cur=None
    for raw in body.split("\n"):
        line=raw.rstrip()
        mt=re.match(r"^##\s+(TS[0-9]+)\.\s+(.*)$", line)
        if mt:
            cur={"id":mt.group(1),"title":mt.group(2).strip(),"lines":[],"related":[]}
            entries.append(cur); continue
        if line.startswith("# ") and "更新" in line: cur=None; continue
        if cur is not None:
            m=re.match(r"^関連場面[:：]\s*(.+)$", line.strip())
            if m:
                cur["related"]=[x.strip() for x in re.split(r"[,、/\s]+", m.group(1)) if x.strip()]; continue
            cur["lines"].append(raw)
    return entries
ts_entries=parse_ts(ts_body) if ts_body else []
ts_title={e["id"]:e["title"] for e in ts_entries}
CHANGE=os.path.join(CONTENT,"changelog.md")
change_raw=rd(CHANGE); change_body=strip_fm(change_raw) if change_raw else ""
def parse_change(body):
    days=[]; cur=None
    for raw in body.split("\n"):
        st=raw.strip()
        m=re.match(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", st)
        if m: cur={"date":m.group(1),"items":[]}; days.append(cur); continue
        if cur is not None:
            mm=re.match(r"^-\s+(.*)$", st)
            if mm: cur["items"].append(mm.group(1).strip())
    return days
change_days=parse_change(change_body)
latest_date=change_days[0]["date"] if change_days else ""
latest_n=len(change_days[0]["items"]) if change_days else 0
def tsslug(tid):
    num=re.sub(r"\D","",tid); return f"ts-{num}.html"

def rel_links(ids):
    out=[]
    for r in ids:
        if r in sc_title: out.append((slug(r), r, sc_title[r]))
        elif r in ts_title: out.append((tsslug(r), r, ts_title[r]))
    return out

# ---------- master parse ----------
def section_lines(body, key):
    lines=body.split("\n"); cap=[]; on=False
    for l in lines:
        if re.match(r"^##\s+", l):
            on = key in l
            if on: continue
        if on and re.match(r"^---\s*$", l): break
        if on: cap.append(l)
    return cap
principles=[]
for l in section_lines(master_body,"ブレ防止"):
    m=re.match(r"^\d+\.\s+\*\*(.+?)\*\*\s*…\s*(.*)$", l.strip())
    if m: principles.append((m.group(1).strip(), m.group(2).strip()))

# ---------- membership for sidebar open-state ----------
grp_members={g:set([f"group-{g.lower()}.html"]+[slug(x["id"]) for x in pgroups[g]["scenarios"]]) for g in GROUPS}
aud_members={c:set([ahub(c)]+[aslug(x["id"]) for x in agroups.get(c,{}).get("topics",[])]) for c in AUD if c in agroups}
ts_members=set(["ts-index.html"]+[tsslug(e["id"]) for e in ts_entries])

# ---------- sidebar ----------
def build_sidebar(active):
    def on(u): return ' class="on"' if u==active else ''
    def op(members): return ' open' if active in members else ''
    p=[]
    p.append('<nav class="side-nav">')
    p.append(f'<a class="side-home"{(" data-on" if active=="index.html" else "")} href="index.html">🏠 ハンドブック トップ</a>' if active=="index.html" else '<a class="side-home" href="index.html">🏠 ハンドブック トップ</a>')
    p.append(f'<a class="side-item"{on("policy.html")} href="policy.html">📘 方針マスター</a>'.replace('class="side-item" class="on"','class="side-item on"'))
    p.append('<div class="side-cap">場面別プレイブック</div>')
    for g,gi in GROUPS.items():
        p.append(f'<details class="side-grp"{op(grp_members[g])}>')
        p.append(f'<summary class="side-sum"><span class="sd sd-{g}"></span>{gi["emoji"]} {esc(g)}. {esc(gi["title"])}</summary>')
        p.append(f'<a{on("group-"+g.lower()+".html")} href="group-{g.lower()}.html">概要（一覧）</a>')
        for x in pgroups[g]["scenarios"]:
            p.append(f'<a{on(slug(x["id"]))} href="{slug(x["id"])}">{esc(x["id"])} {esc(x["title"])}</a>')
        p.append('</details>')
    p.append('<div class="side-cap">読者別ガイド</div>')
    for c,ai in AUD.items():
        if c not in agroups: continue
        p.append(f'<details class="side-grp"{op(aud_members[c])}>')
        p.append(f'<summary class="side-sum"><span class="sd sd-{ai["key"]}"></span>{ai["emoji"]} {esc(ai["title"])}</summary>')
        p.append(f'<a{on(ahub(c))} href="{ahub(c)}">概要（一覧）</a>')
        for x in agroups[c]["topics"]:
            p.append(f'<a{on(aslug(x["id"]))} href="{aslug(x["id"])}">{esc(x["id"])} {esc(x["title"])}</a>')
        p.append('</details>')
    if ts_entries:
        p.append('<div class="side-cap">トラブルシューティング</div>')
        p.append(f'<details class="side-grp"{op(ts_members)}>')
        p.append(f'<summary class="side-sum"><span class="sd sd-ts"></span>🧯 症状から引く</summary>')
        p.append(f'<a{on("ts-index.html")} href="ts-index.html">一覧</a>')
        for e in ts_entries:
            p.append(f'<a{on(tsslug(e["id"]))} href="{tsslug(e["id"])}">{esc(e["title"])}</a>')
        p.append('</details>')
    p.append('<div class="side-cap">リファレンス</div>')
    p.append(f'<a class="side-item"{on("glossary.html")} href="glossary.html">📑 用語・索引</a>'.replace('class="side-item" class="on"','class="side-item on"'))
    p.append(f'<a class="side-item"{on("review.html")} href="review.html">🟡 要確認リスト</a>'.replace('class="side-item" class="on"','class="side-item on"'))
    if change_days:
        p.append(f'<a class="side-item"{on("whatsnew.html")} href="whatsnew.html">🆕 更新履歴</a>'.replace('class="side-item" class="on"','class="side-item on"'))
    p.append('</nav>')
    return "\n".join(p)

# ---------- page scaffold (sidebar layout) ----------
def page(title, body, active, desc="", crumb_html=""):
    side=build_sidebar(active)
    crumb=f'<div class="crumb">{crumb_html}</div>' if crumb_html else ''
    return f"""<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}｜ものづくりハンドブック</title>
<meta name="description" content="{esc(desc or 'ものづくりハンドブック')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Shippori+Mincho:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Crect%20width='24'%20height='24'%20rx='5'%20fill='%2316314D'/%3E%3Cpath%20d='M6%205h8a3%203%200%200%201%203%203v11a3%203%200%200%200-3-3H6z'%20fill='%230E8074'/%3E%3C/svg%3E">
</head><body>
<header class="hb-top">
  <div class="hb-top-in">
    <button class="hb-burger" id="hbburger" aria-label="メニューを開閉">☰</button>
    <a class="hb-brand" href="index.html"><span class="hb-logo">本</span><span class="hb-brand-t">ものづくりハンドブック</span></a>
    <div class="hb-search-wrap">
      <input id="hbsearch" type="text" placeholder="検索（例: クレーム / 特採 / 校正 / 4M / 異物 / 目付）" autocomplete="off" aria-label="ハンドブック内検索">
      <div id="hbresults" class="hb-results" hidden></div>
    </div>
    <a class="hb-board" href="../" title="Daily Insight Board へ">← ボード</a>
  </div>
</header>
<div class="hb-shell">
  <aside class="hb-side" id="hbside">{side}</aside>
  <main class="hb-main">
  {crumb}
  {body}
  </main>
</div>
<div class="hb-ov" id="hbov"></div>
<footer class="hb-foot"><div class="wrap">
  <div><b>ものづくりハンドブック</b></div>
  <div class="hb-foot-sub">本文の正（Single Source of Truth）は <a href="content/playbooks.md">プレイブック集</a> ／ <a href="content/policy-master.md">方針マスター</a> ／ <a href="content/audience-guides.md">読者別ガイド</a> ／ <a href="content/troubleshooting.md">トラブルシューティング</a>。最終更新 {LAST_UPDATED}。運用は <a href="content/README.md">README</a> 参照。</div>
</div></footer>
<script src="assets/app.js"></script>
</body></html>"""

def crumb2(section_label, section_href, title):
    a=f'<a href="{section_href}">{esc(section_label)}</a>' if section_href else f'<span>{esc(section_label)}</span>'
    return a+'<span class="sep">/</span>'+f'<span>{esc(title)}</span>'

# ---------- purpose extractor ----------
def purpose_and_body(item):
    lines=[l for l in item["lines"]]
    while lines and lines[0].strip()=="": lines.pop(0)
    purpose=None; start=0
    pat=r"^\*\*(目的|考え方|位置づけ|トリガー|最大のリスク|合言葉|症状|本ページについて).*?\*\*"
    if lines and re.match(pat, lines[0].strip()):
        j=0; buf=[]
        while j<len(lines) and lines[j].strip()!="": buf.append(lines[j].strip()); j+=1
        purpose=" ".join(buf); start=j
    return purpose, lines[start:]

def purpose_box(purpose):
    if not purpose: return ""
    ptxt=re.sub(r"^\*\*(.+?)\*\*\s*[:：]?\s*","",purpose).strip()
    plabel=re.match(r"^\*\*(.+?)\*\*", purpose)
    lab=plabel.group(1) if plabel else "目的"
    return f'<div class="purpose"><span class="p-tag">{esc(lab)}</span><p>{inline(ptxt)}</p></div>'

def related_box(title, ids):
    ls=rel_links(ids)
    if not ls: return ""
    links="".join(f'<a href="{u}"><span class="rel-id">{esc(i)}</span>{esc(t)}</a>' for u,i,t in ls)
    return f'<div class="rel"><h3>{esc(title)}</h3><div class="rel-list">{links}</div></div>'

search_index=[]

# ---------- scenario pages ----------
for s in scenarios:
    g=s["group"]; gi=GROUPS[g]
    purpose, rest = purpose_and_body(s)
    body_html=render_blocks(rest)
    sibs=[x for x in pgroups[g]["scenarios"] if x["id"]!=s["id"]]
    rel='<div class="rel"><h3>関連する場面（同じグループ）</h3><div class="rel-list">'+ "".join(
        f'<a href="{slug(x["id"])}"><span class="rel-id">{esc(x["id"])}</span>{esc(x["title"])}</a>' for x in sibs)+'</div></div>'
    head=f'''<div class="s-head">
      <div class="s-tags"><span class="gtag g-{g}">{gi["emoji"]} {esc(g)}・{esc(gi["title"])}</span><span class="ttag">種類：{esc(gi["type"])}</span></div>
      <h1><span class="s-id">{esc(s["id"])}</span>{esc(s["title"])}</h1>
    </div>'''
    body=f'''{head}{purpose_box(purpose)}<div class="s-body">{body_html}</div>{rel}
    <div class="s-meta">最終更新日：{LAST_UPDATED}　|　<a href="content/playbooks.md">原本（Markdown）を開く</a></div>'''
    cr=crumb2(f"{g} {gi['title']}", f"group-{g.lower()}.html", f"{s['id']} {s['title']}")
    open(os.path.join(OUT,slug(s["id"])),"w",encoding="utf-8").write(
        page(f"{s['id']} {s['title']}", body, slug(s["id"]), desc=(purpose or s['title']), crumb_html=cr))
    search_index.append({"url":slug(s["id"]),"title":f"{s['id']} {s['title']}","g":f"{g}・{gi['type']}","t":s["title"]+" "+(purpose or "")+" "+plain_text(rest)})

# ---------- group pages ----------
for g,gi in GROUPS.items():
    scs=pgroups[g]["scenarios"]
    note_html=render_blocks(pgroups[g]["note"]) if pgroups[g]["note"] else ""
    cards="".join(f'<a class="sc-card" href="{slug(x["id"])}"><span class="sc-id">{esc(x["id"])}</span><span class="sc-t">{esc(x["title"])}</span></a>' for x in scs)
    body=f'''<h1 class="g-title"><span class="g-emoji">{gi["emoji"]}</span>{esc(g)}. {esc(gi["title"])}</h1>
    <p class="g-sub">種類：{esc(gi["type"])}　|　{len(scs)} 場面</p>
    {('<div class="g-note">'+note_html+'</div>') if note_html else ''}
    <div class="sc-grid">{cards}</div>'''
    open(os.path.join(OUT,f"group-{g.lower()}.html"),"w",encoding="utf-8").write(
        page(f"{g} {gi['title']}", body, f"group-{g.lower()}.html", desc=f"{gi['title']}の場面一覧",
             crumb_html=crumb2("ハンドブック","index.html",f"{g} {gi['title']}")))
    search_index.append({"url":f"group-{g.lower()}.html","title":f"{g}. {gi['title']}","g":f"{g}・{gi['type']}","t":g+" "+gi["title"]+" "+plain_text(pgroups[g]["note"])})

# ---------- policy page ----------
policy_html=render_blocks(master_body.split("\n"))
open(os.path.join(OUT,"policy.html"),"w",encoding="utf-8").write(
    page("方針マスター", '<h1 class="g-title">方針マスター（単一情報源）</h1>'+policy_html, "policy.html",
         desc="使命・価値観・ルール・エスカレーション基準",
         crumb_html=crumb2("ハンドブック","index.html","方針マスター")))
search_index.append({"url":"policy.html","title":"方針マスター（使命・ルール・エスカレーション）","g":"方針","t":plain_text(master_body.split("\n"))})

# ---------- glossary page ----------
gl_lines=section_lines(master_body,"用語メモ"); gl_html=render_blocks(gl_lines)
sc_index="".join(f'<a href="{slug(x["id"])}"><span class="rel-id">{esc(x["id"])}</span>{esc(x["title"])}</a>' for x in scenarios)
body=f'''<h1 class="g-title">用語・索引</h1>
<h2>用語メモ</h2><div class="s-body">{gl_html}</div>
<h2>場面インデックス（全{len(scenarios)}場面）</h2><div class="rel-list idx">{sc_index}</div>'''
open(os.path.join(OUT,"glossary.html"),"w",encoding="utf-8").write(
    page("用語・索引",body,"glossary.html",desc="用語メモと全場面の索引",crumb_html=crumb2("ハンドブック","index.html","用語・索引")))
search_index.append({"url":"glossary.html","title":"用語・索引","g":"索引","t":"用語 索引 "+plain_text(gl_lines)})

# ---------- review page ----------
def collect_review(body):
    items=[]; in_appendix=False
    for l in body.split("\n"):
        st=l.strip()
        if re.match(r"^#{1,4}\s+", st):
            in_appendix = ("要確認リスト" in st); continue
        if "【要確認】" in st:
            t=re.sub(r"^>\s*","",st); t=re.sub(r"^[-*]\s*\[[ xX]\]\s*","",t); t=t.replace("【要確認】","").strip()
            if t: items.append(t); continue
        if in_appendix:
            m=re.match(r"^-\s*\[ \]\s+(.*)$", st)
            if m: items.append(m.group(1).strip())
    seen=set(); res=[]
    for it in items:
        if it not in seen: seen.add(it); res.append(it)
    return res
rev_play=collect_review(play_body); rev_master=collect_review(master_body)
rev_aud=collect_review(aud_body) if aud_body else []; rev_ts=collect_review(ts_body) if ts_body else []
def rev_block(title,href,items):
    if not items: return ""
    lis="".join(f'<li class="chk"><span class="cb"></span><span class="t">{inline(it)}</span></li>' for it in items)
    return f'<h2>{esc(title)} <a class="src-link" href="{href}">原本</a></h2><ul class="checklist">{lis}</ul>'
body=f'''<h1 class="g-title">付録：要確認リスト</h1>
<div class="callout review"><span class="rev-badge">要確認</span><span>未確定（GLの確認待ち）の項目です。確定したら原本Markdownを更新してください。本サイトは原本を反映したものです。</span></div>
{rev_block("方針マスター 由来","content/policy-master.md",rev_master)}
{rev_block("プレイブック集 由来","content/playbooks.md",rev_play)}
{rev_block("読者別ガイド 由来","content/audience-guides.md",rev_aud)}
{rev_block("トラブルシューティング 由来","content/troubleshooting.md",rev_ts)}'''
open(os.path.join(OUT,"review.html"),"w",encoding="utf-8").write(
    page("要確認リスト",body,"review.html",desc="未確定（要確認）項目の一覧",crumb_html=crumb2("ハンドブック","index.html","要確認リスト")))
search_index.append({"url":"review.html","title":"付録：要確認リスト","g":"要確認","t":"要確認 未確定 "+" ".join(rev_master+rev_play+rev_aud+rev_ts)})

# ---------- audience topic + hub pages ----------
for t in atopics:
    code=t["aud"]; ai=AUD[code]
    purpose, rest = purpose_and_body(t)
    sibs=[x for x in agroups[code]["topics"] if x["id"]!=t["id"]]
    sibhtml='<div class="rel"><h3>同じ読者向けの他トピック</h3><div class="rel-list">'+ "".join(
        f'<a href="{aslug(x["id"])}"><span class="rel-id">{esc(x["id"])}</span>{esc(x["title"])}</a>' for x in sibs)+'</div></div>'
    head=f'''<div class="s-head">
      <div class="s-tags"><span class="gtag g-{ai["key"]}">{ai["emoji"]} {esc(ai["title"])}</span><span class="ttag">連携先：{esc(ai["who"])}</span></div>
      <h1><span class="s-id">{esc(t["id"])}</span>{esc(t["title"])}</h1>
    </div>'''
    body=f'''{head}{purpose_box(purpose)}<div class="s-body">{render_blocks(rest)}</div>{related_box("関連する場面（品証プレイブック）",t["related"])}{sibhtml}
    <div class="s-meta">最終更新日：{LAST_UPDATED}　|　<a href="content/audience-guides.md">原本（Markdown）を開く</a></div>'''
    cr=crumb2(ai["title"], ahub(code), f"{t['id']} {t['title']}")
    open(os.path.join(OUT,aslug(t["id"])),"w",encoding="utf-8").write(
        page(f"{t['id']} {t['title']}", body, aslug(t["id"]), desc=(purpose or t["title"]), crumb_html=cr))
    search_index.append({"url":aslug(t["id"]),"title":f"{t['id']} {t['title']}","g":f"読者別・{ai['title']}","t":t["title"]+" "+(purpose or "")+" "+plain_text(rest)})

for code,ai in AUD.items():
    if code not in agroups: continue
    tps=agroups[code]["topics"]
    note_html=render_blocks(agroups[code]["note"]) if agroups[code]["note"] else ""
    cards="".join(f'<a class="sc-card" href="{aslug(x["id"])}"><span class="sc-id">{esc(x["id"])}</span><span class="sc-t">{esc(x["title"])}</span></a>' for x in tps)
    body=f'''<h1 class="g-title"><span class="g-emoji">{ai["emoji"]}</span>{esc(ai["title"])}</h1>
    <p class="g-sub">連携先：{esc(ai["who"])}　|　{len(tps)} トピック</p>
    {('<div class="g-note">'+note_html+'</div>') if note_html else ''}
    <div class="sc-grid">{cards}</div>'''
    open(os.path.join(OUT,ahub(code)),"w",encoding="utf-8").write(
        page(ai["title"], body, ahub(code), desc=f"{ai['title']}：品証との連携ガイド",
             crumb_html=crumb2("読者別","aud-index.html",ai["title"])))
    search_index.append({"url":ahub(code),"title":ai["title"],"g":f"読者別・{ai['title']}","t":ai["title"]+" "+ai["who"]+" "+plain_text(agroups[code]["note"])})

# audience index
agc=""
for code,ai in AUD.items():
    if code not in agroups: continue
    tps=agroups[code]["topics"]
    lst="".join(f'<a href="{aslug(x["id"])}">{esc(x["id"])} {esc(x["title"])}</a>' for x in tps)
    agc+=f'''<div class="hub-gcard g-{ai["key"]}">
      <a class="hub-gh" href="{ahub(code)}"><span class="hub-gemoji">{ai["emoji"]}</span><span><b>{esc(ai["title"])}</b><span class="hub-gtype">連携先：{esc(ai["who"])}・{len(tps)}トピック</span></span></a>
      <div class="hub-glist">{lst}</div></div>'''
if agroups:
    body=f'''<h1 class="g-title">👥 読者別ハンドブック（連携ガイド）</h1>
    <p class="g-sub">品証から各部門・取引先への連携の手引き。「いつ・何を・どう連携するか」を場面別に。各トピック末尾から品証プレイブック（A〜D）へ辿れます。</p>
    <div class="hub-gcards">{agc}</div>'''
    open(os.path.join(OUT,"aud-index.html"),"w",encoding="utf-8").write(
        page("読者別ハンドブック", body, "aud-index.html", desc="営業・技術・製造・購買・外注先 向けの品証連携ガイド",
             crumb_html=crumb2("ハンドブック","index.html","読者別")))
    search_index.append({"url":"aud-index.html","title":"読者別ハンドブック（営業・技術・製造・購買・外注先）","g":"読者別","t":"読者別 営業 技術 製造 購買 外注先 連携 "+plain_text(aud_body.split("\n"))})

# ---------- troubleshooting pages ----------
if ts_entries:
    for e in ts_entries:
        purpose, rest = purpose_and_body(e)
        sibs=[x for x in ts_entries if x["id"]!=e["id"]]
        sibhtml='<div class="rel"><h3>他の症状</h3><div class="rel-list">'+ "".join(
            f'<a href="{tsslug(x["id"])}"><span class="rel-id">TS</span>{esc(x["title"])}</a>' for x in sibs)+'</div></div>'
        head=f'''<div class="s-head">
      <div class="s-tags"><span class="gtag g-ts">🧯 トラブルシューティング</span><span class="ttag">症状から引く</span></div>
      <h1><span class="s-id">{esc(e["id"])}</span>{esc(e["title"])}</h1>
    </div>'''
        body=f'''{head}{purpose_box(purpose)}<div class="s-body">{render_blocks(rest)}</div>{related_box("関連する場面・症状",e["related"])}{sibhtml}
    <div class="s-meta">最終更新日：{LAST_UPDATED}　|　<a href="content/troubleshooting.md">原本（Markdown）を開く</a></div>'''
        cr=crumb2("トラブルシューティング","ts-index.html",e["title"])
        open(os.path.join(OUT,tsslug(e["id"])),"w",encoding="utf-8").write(
            page(e["title"], body, tsslug(e["id"]), desc=(purpose or e["title"]), crumb_html=cr))
        search_index.append({"url":tsslug(e["id"]),"title":f"{e['title']}","g":"トラブル","t":e["title"]+" "+(purpose or "")+" "+plain_text(rest)})
    tsintro=render_blocks([l for l in ts_body.split("\n") if l.strip().startswith(">")][:6])
    cards="".join(f'<a class="sc-card" href="{tsslug(e["id"])}"><span class="sc-id">🧯</span><span class="sc-t">{esc(e["title"])}</span></a>' for e in ts_entries)
    body=f'''<h1 class="g-title">🧯 トラブルシューティング（症状から引く）</h1>
    <p class="g-sub">不織布で起こりやすい不良を症状から。初動→4M切り分け→恒久対策の型で整理（たたき台）。全{len(ts_entries)}症状</p>
    <div class="g-note">{tsintro}</div>
    <div class="sc-grid">{cards}</div>'''
    open(os.path.join(OUT,"ts-index.html"),"w",encoding="utf-8").write(
        page("トラブルシューティング", body, "ts-index.html", desc="症状から引く不良対応（たたき台）",
             crumb_html=crumb2("ハンドブック","index.html","トラブルシューティング")))
    search_index.append({"url":"ts-index.html","title":"トラブルシューティング（症状から引く）","g":"トラブル","t":"トラブルシューティング 症状 不良 "+plain_text(ts_body.split("\n"))})

# ---------- hub ----------
prin_html="".join(f'<li><span class="pn">{i+1}</span><div><b>{esc(t)}</b><span>{inline(d)}</span></div></li>' for i,(t,d) in enumerate(principles))
gcards=""
for g,gi in GROUPS.items():
    scs=pgroups[g]["scenarios"]
    lst="".join(f'<a href="{slug(x["id"])}">{esc(x["id"])} {esc(x["title"])}</a>' for x in scs)
    gcards+=f'''<div class="hub-gcard g-{g}">
      <a class="hub-gh" href="group-{g.lower()}.html"><span class="hub-gemoji">{gi["emoji"]}</span><span><b>{esc(g)}. {esc(gi["title"])}</b><span class="hub-gtype">種類：{esc(gi["type"])}・{len(scs)}場面</span></span></a>
      <div class="hub-glist">{lst}</div></div>'''
aud_sec=""
if agc:
    aud_sec=f'<section class="hub-sec"><h2>読者別ガイド（営業・技術・製造・購買・外注先）</h2><p class="g-sub">品証から各部門・取引先への連携の手引き。</p><div class="hub-gcards">{agc}</div></section>'
ts_sec=""
if ts_entries:
    tscards="".join(f'<a href="{tsslug(e["id"])}">{esc(e["title"])}</a>' for e in ts_entries)
    ts_sec=f'''<section class="hub-sec"><h2>トラブルシューティング（症状から引く）</h2>
  <p class="g-sub">不織布の不良を症状から。初動→4M→恒久対策（たたき台・全{len(ts_entries)}症状）。</p>
  <div class="hub-gcard g-ts"><a class="hub-gh" href="ts-index.html"><span class="hub-gemoji">🧯</span><span><b>症状一覧を開く</b><span class="hub-gtype">{len(ts_entries)} 症状</span></span></a><div class="hub-glist">{tscards}</div></div></section>'''
wn_banner=('<a class="hub-updated" href="whatsnew.html">🆕 最新更新 '+latest_date+'・'+str(latest_n)+'件 — 更新履歴を見る →</a>') if change_days else ''
body=f'''<div class="hub-hero">
  <h1>ものづくりハンドブック</h1>
  <p>方針・場面別プレイブック・読者別ガイド・トラブルシューティングを1か所に。左のメニュー、または上の検索から探してください。</p>
</div>
{wn_banner}
<div class="quick">
  <span class="quick-lab">困ったとき</span>
  <a class="quick-b urgent" href="{slug('B2')}">🚑 クレーム・不適合の初動（B2）</a>
  <a class="quick-b urgent" href="{slug('B1')}">⚠ 優先順位（B1 トリアージ）</a>
  <a class="quick-b" href="policy.html#esc">📣 エスカレーション基準</a>
  <a class="quick-b" href="ts-index.html">🧯 症状から引く</a>
</div>
<section class="hub-sec"><h2>品質の6原則（ブレ防止の共通言語）</h2><ul class="principles">{prin_html}</ul></section>
<section class="hub-sec"><h2>場面別プレイブック（A〜D）</h2><div class="hub-gcards">{gcards}</div></section>
{aud_sec}
{ts_sec}
<section class="hub-sec links"><h2>その他</h2>
  <a href="aud-index.html">👥 読者別ガイド</a>
  <a href="policy.html">📘 方針マスター</a>
  <a href="glossary.html">📑 用語・索引</a>
  <a href="review.html">🟡 要確認リスト</a>
  <a href="whatsnew.html">🆕 更新履歴</a>
  <a href="../">← Daily Insight Board に戻る</a>
</section>'''
open(os.path.join(OUT,"index.html"),"w",encoding="utf-8").write(
    page("ハンドブック", body, "index.html", desc="ものづくりハンドブック（場面別・読者別・トラブルシューティング）"))

# ---------- whatsnew (changelog) ----------
if change_days:
    tagmap={"改称":"t-brand","追加":"t-add","改善":"t-imp","新設":"t-new","修正":"t-fix"}
    wn_sections=[]
    for d in change_days:
        lis=[]
        for it in d["items"]:
            lab=""; txt=it
            m=re.match(r"^([^:：]{1,6})[:：]\s*(.*)$", it)
            if m and m.group(1) in tagmap: lab=m.group(1); txt=m.group(2)
            badge=('<span class="wn-tag '+tagmap.get(lab,"t-other")+'">'+esc(lab)+'</span>') if lab else ''
            lis.append('<li class="wn-item">'+badge+'<span>'+inline(txt)+'</span></li>')
        wn_sections.append('<section class="wn-day"><h2 class="wn-date">'+esc(d["date"])+' <span class="wn-count">'+str(len(d["items"]))+'件</span></h2><ul class="wn-list">'+"".join(lis)+'</ul></section>')
    wn_title="更新履歴（What\'s new）"
    wn_body='<h1 class="g-title">🆕 '+wn_title+'</h1><p class="g-sub">ハンドブックの追加・改善の記録。毎朝の自動更新でここに積み上がります。</p><div class="wn">'+"".join(wn_sections)+'</div>'
    open(os.path.join(OUT,"whatsnew.html"),"w",encoding="utf-8").write(
        page("更新履歴", wn_body, "whatsnew.html", desc="ハンドブックの更新履歴（What\'s new）",
             crumb_html=crumb2("ハンドブック","index.html","更新履歴")))
    search_index.append({"url":"whatsnew.html","title":"更新履歴（What\'s new）","g":"更新","t":"更新履歴 whatsnew 更新 "+" ".join(it for d in change_days for it in d["items"])})

open(os.path.join(ASSETS,"search-index.json"),"w",encoding="utf-8").write(json.dumps(search_index,ensure_ascii=False))
print("scenarios:",len(scenarios))
print("audiences:",{c:len(agroups[c]["topics"]) for c in agroups})
print("troubleshooting:",len(ts_entries))
print("search entries:",len(search_index))
print("html files:",len([f for f in os.listdir(OUT) if f.endswith('.html')]))
