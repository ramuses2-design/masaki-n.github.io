# -*- coding: utf-8 -*-
import re, json, os, shutil, html

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT=os.path.join(BASE,"content")
OUT=BASE
ASSETS=os.path.join(OUT,"assets")
for d in (OUT,ASSETS,CONTENT): os.makedirs(d,exist_ok=True)
MASTER=os.path.join(CONTENT,"policy-master.md")
PLAY=os.path.join(CONTENT,"playbooks.md")

master_raw=open(MASTER,encoding="utf-8").read()
play_raw=open(PLAY,encoding="utf-8").read()

def strip_fm(t):
    if t.startswith("---"):
        parts=t.split("---",2)
        return parts[2].lstrip("\n") if len(parts)>=3 else t, parts[1]
    return t,""
master_body,_=strip_fm(master_raw)
play_body,_=strip_fm(play_raw)

LAST_UPDATED="2026-06-30"

GROUPS={
 "A":{"title":"定例・マネジメント","type":"定例","emoji":"📋"},
 "B":{"title":"異常対応","type":"異常","emoji":"🚨"},
 "C":{"title":"変化・プロジェクト","type":"変化","emoji":"🔧"},
 "D":{"title":"予防・維持・システム","type":"予防","emoji":"🛡️"},
}

def esc(s): return html.escape(s, quote=True)
def inline(s):
    s=esc(s)
    s=re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s=s.replace("【要確認】", '<span class="ic-rev">【要確認】</span>')
    return s

# ---------- generic markdown -> html (faithful) ----------
def render_blocks(lines):
    out=[]; i=0; n=len(lines)
    def flush_para(buf):
        if buf:
            out.append("<p>"+inline(" ".join(buf).strip())+"</p>")
    while i<n:
        line=lines[i].rstrip("\n")
        st=line.strip()
        if st=="":
            i+=1; continue
        # table
        if st.startswith("|"):
            tbl=[]
            while i<n and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip()); i+=1
            rows=[[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl]
            rows=[r for r in rows if not all(set(c)<=set("-: ") for c in r)]
            if rows:
                head=rows[0]; body=rows[1:]
                t='<div class="tbl-wrap"><table><thead><tr>'+"".join("<th>"+inline(c)+"</th>" for c in head)+"</tr></thead><tbody>"
                for r in body:
                    t+="<tr>"+"".join("<td>"+inline(c)+"</td>" for c in r)+"</tr>"
                t+="</tbody></table></div>"
                out.append(t)
            continue
        # heading
        m=re.match(r"^(#{1,4})\s+(.*)$", st)
        if m:
            lvl=len(m.group(1)); txt=m.group(2).strip()
            hid=""
            if "エスカレーション" in txt: hid=' id="esc"'
            tag={1:"h2",2:"h2",3:"h3",4:"h4"}.get(lvl,"h3")
            out.append(f"<{tag}{hid}>"+inline(txt)+f"</{tag}>")
            i+=1; continue
        # blockquote group
        if st.startswith(">"):
            q=[]
            while i<n and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip()); i+=1
            qt=" ".join([x for x in q if x])
            if "【要確認】" in qt:
                qt2=qt.replace("【要確認】","").strip()
                out.append('<div class="callout review"><span class="rev-badge">要確認</span><span>'+inline(qt2)+'</span></div>')
            else:
                out.append('<blockquote>'+inline(qt)+'</blockquote>')
            continue
        # checklist
        if re.match(r"^-\s*\[[ xX]\]\s+", st):
            items=[]
            while i<n and re.match(r"^-\s*\[[ xX]\]\s+", lines[i].strip()):
                it=re.sub(r"^-\s*\[[ xX]\]\s+","",lines[i].strip())
                items.append(it); i+=1
            li=[]
            for it in items:
                star="★" in it
                done=False
                t=it.replace("★","").strip()
                cls="chk"+(" star" if star else "")
                badge='<span class="star-badge">重点</span>' if star else ""
                li.append(f'<li class="{cls}"><span class="cb"></span><span class="t">'+inline(t)+f'</span>{badge}</li>')
            out.append('<ul class="checklist">'+"".join(li)+"</ul>")
            continue
        # ordered list
        if re.match(r"^\d+\.\s+", st):
            items=[]
            while i<n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+","",lines[i].strip())); i+=1
            star_any=False
            li=[]
            for it in items:
                star="★" in it
                t=it.replace("★","").strip()
                badge='<span class="star-badge">重点</span>' if star else ""
                li.append("<li>"+inline(t)+badge+"</li>")
            out.append("<ol>"+"".join(li)+"</ol>")
            continue
        # bold-only subheader
        mb=re.match(r"^\*\*(.+?)\*\*[:：]?\s*$", st)
        if mb:
            out.append("<h4>"+inline(mb.group(1))+"</h4>")
            i+=1; continue
        # unordered list
        if re.match(r"^-\s+", st):
            items=[]
            while i<n and re.match(r"^-\s+", lines[i].strip()) and not re.match(r"^-\s*\[",lines[i].strip()):
                items.append(re.sub(r"^-\s+","",lines[i].strip())); i+=1
            out.append("<ul>"+"".join("<li>"+inline(x)+"</li>" for x in items)+"</ul>")
            continue
        # paragraph
        buf=[st]; i+=1
        while i<n and lines[i].strip()!="" and not re.match(r"^(#|>|-|\d+\.|\|)", lines[i].strip()) and not re.match(r"^\*\*(.+?)\*\*[:：]?\s*$", lines[i].strip()):
            buf.append(lines[i].strip()); i+=1
        flush_para(buf)
    return "\n".join(out)

def plain_text(lines):
    t=" ".join(lines)
    t=re.sub(r"[#>*\-\[\]★|]"," ",t)
    t=re.sub(r"\s+"," ",t)
    return t.strip()

# ---------- parse playbook into scenarios ----------
def parse_play(body):
    lines=body.split("\n")
    groups={}; order=[]
    cur_g=None; cur_s=None
    gnote={}
    for idx,raw in enumerate(lines):
        line=raw.rstrip()
        mg=re.match(r"^#\s+([A-D])\.\s+(.*)$", line)
        ms=re.match(r"^##\s+([A-D][0-9]+(?:-[a-z])?)\.\s+(.*)$", line)
        if mg:
            cur_g=mg.group(1); groups.setdefault(cur_g,{"title":mg.group(2).strip(),"scenarios":[],"note":[]}); cur_s=None; continue
        if ms:
            sid=ms.group(1); title=ms.group(2).strip()
            cur_s={"id":sid,"title":title,"group":cur_g,"lines":[]}
            groups[cur_g]["scenarios"].append(cur_s); order.append(cur_s); continue
        if line.startswith("# 更新") or line.startswith("# ") and "更新" in line:
            cur_g=None; cur_s=None; continue
        if cur_s is not None:
            cur_s["lines"].append(raw)
        elif cur_g is not None:
            # group-level note (before first scenario)
            if line.strip() and not line.startswith("---"):
                groups[cur_g]["note"].append(raw)
    return groups, order

pgroups, scenarios = parse_play(play_body)

def slug(sid): return "s-"+sid.lower()+".html"

# ---------- master parse: 6 principles, glossary, escalation, review ----------
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

# ---------- HTML scaffolding ----------
def nav(active):
    items=[("index.html","ハンドブック"),("policy.html","方針"),
           ("group-a.html","A 定例"),("group-b.html","B 異常"),
           ("group-c.html","C 変化"),("group-d.html","D 予防"),
           ("glossary.html","用語・索引"),("review.html","要確認")]
    lis=""
    for href,label in items:
        cls=' class="on"' if href==active else ""
        lis+=f'<a href="{href}"{cls}>{esc(label)}</a>'
    return lis

def page(title, breadcrumb, body, active, desc=""):
    return f"""<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}｜品質保証グループ ハンドブック</title>
<meta name="description" content="{esc(desc or '品質保証グループ 場面別ハンドブック')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Shippori+Mincho:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Crect%20width='24'%20height='24'%20rx='5'%20fill='%2316314D'/%3E%3Cpath%20d='M6%205h8a3%203%200%200%201%203%203v11a3%203%200%200%200-3-3H6z'%20fill='%230E8074'/%3E%3C/svg%3E">
</head><body>
<header class="hb-top">
  <div class="wrap hb-top-in">
    <a class="hb-brand" href="index.html"><span class="hb-logo">QA</span><span>品質保証グループ ハンドブック</span></a>
    <div class="hb-search-wrap">
      <input id="hbsearch" type="text" placeholder="検索（例: クレーム / 特採 / 校正 / 4M / 1on1）" autocomplete="off" aria-label="ハンドブック内検索">
      <div id="hbresults" class="hb-results" hidden></div>
    </div>
    <a class="hb-board" href="../" title="Daily Insight Board へ">← ボード</a>
  </div>
  <nav class="hb-nav"><div class="wrap hb-nav-in">{nav(active)}</div></nav>
</header>
<main class="wrap hb-main">
  <div class="crumb">{breadcrumb}</div>
  {body}
</main>
<footer class="hb-foot"><div class="wrap">
  <div><b>品質保証グループ ハンドブック</b>｜金井重要工業 不織布事業部 品質保証グループ</div>
  <div class="hb-foot-sub">本文の正（Single Source of Truth）は <a href="content/playbooks.md">場面別プレイブック集.md</a> ／ <a href="content/policy-master.md">方針マスター.md</a>。最終更新 {LAST_UPDATED}。運用は <a href="content/README.md">README</a> 参照。</div>
</div></footer>
<script src="assets/app.js"></script>
</body></html>"""

def crumb(*parts):
    out=[]
    for i,(label,href) in enumerate(parts):
        if href and i<len(parts)-1:
            out.append(f'<a href="{href}">{esc(label)}</a>')
        else:
            out.append(f'<span>{esc(label)}</span>')
    return '<span class="sep">/</span>'.join(out)

# ---------- scenario pages ----------
search_index=[]
def purpose_and_body(s):
    lines=[l for l in s["lines"]]
    # trim leading blanks
    while lines and lines[0].strip()=="": lines.pop(0)
    purpose=None; start=0
    if lines:
        first=lines[0].strip()
        if re.match(r"^\*\*(目的|考え方|位置づけ|トリガー|最大のリスク).*?\*\*", first):
            # capture this paragraph (until blank)
            j=0; buf=[]
            while j<len(lines) and lines[j].strip()!="":
                buf.append(lines[j].strip()); j+=1
            purpose=" ".join(buf); start=j
    rest=lines[start:]
    return purpose, rest

for s in scenarios:
    g=s["group"]; gi=GROUPS[g]
    purpose, rest = purpose_and_body(s)
    body_html=render_blocks(rest)
    # related = siblings
    sibs=[x for x in pgroups[g]["scenarios"] if x["id"]!=s["id"]]
    rel='<div class="rel"><h3>関連する場面（同じグループ）</h3><div class="rel-list">'+ "".join(
        f'<a href="{slug(x["id"])}"><span class="rel-id">{esc(x["id"])}</span>{esc(x["title"])}</a>' for x in sibs)+'</div></div>'
    pbox=""
    if purpose:
        ptxt=re.sub(r"^\*\*(.+?)\*\*\s*[:：]?\s*","",purpose).strip()
        plabel=re.match(r"^\*\*(.+?)\*\*", purpose)
        lab=plabel.group(1) if plabel else "目的"
        pbox=f'<div class="purpose"><span class="p-tag">{esc(lab)}</span><p>{inline(ptxt)}</p></div>'
    head=f'''<div class="s-head">
      <div class="s-tags"><span class="gtag g-{g}">{gi["emoji"]} {esc(g)}・{esc(gi["title"])}</span><span class="ttag">種類：{esc(gi["type"])}</span></div>
      <h1><span class="s-id">{esc(s["id"])}</span>{esc(s["title"])}</h1>
    </div>'''
    body=f'''{head}{pbox}<div class="s-body">{body_html}</div>{rel}
    <div class="s-meta">最終更新日：{LAST_UPDATED}　|　<a href="content/playbooks.md">原本（Markdown）を開く</a></div>'''
    bc=crumb(("ハンドブック","index.html"),(f"{g} {gi['title']}",f"group-{g.lower()}.html"),(f"{s['id']} {s['title']}",None))
    html_out=page(f"{s['id']} {s['title']}", bc, body, f"group-{g.lower()}.html",
                  desc=(purpose or s['title']))
    open(os.path.join(OUT,slug(s["id"])),"w",encoding="utf-8").write(html_out)
    # search index
    txt=(s["title"]+" "+(purpose or "")+" "+plain_text(rest))
    search_index.append({"url":slug(s["id"]),"title":f"{s['id']} {s['title']}","g":f"{g}・{gi['type']}","t":txt})

# ---------- group pages ----------
for g,gi in GROUPS.items():
    scs=pgroups[g]["scenarios"]
    note="".join(l for l in pgroups[g]["note"])
    note_html=render_blocks(pgroups[g]["note"]) if pgroups[g]["note"] else ""
    cards="".join(
        f'<a class="sc-card" href="{slug(x["id"])}"><span class="sc-id">{esc(x["id"])}</span><span class="sc-t">{esc(x["title"])}</span></a>'
        for x in scs)
    body=f'''<h1 class="g-title"><span class="g-emoji">{gi["emoji"]}</span>{esc(g)}. {esc(gi["title"])}</h1>
    <p class="g-sub">種類：{esc(gi["type"])}　|　{len(scs)} 場面</p>
    {('<div class="g-note">'+note_html+'</div>') if note_html else ''}
    <div class="sc-grid">{cards}</div>'''
    bc=crumb(("ハンドブック","index.html"),(f"{g} {gi['title']}",None))
    open(os.path.join(OUT,f"group-{g.lower()}.html"),"w",encoding="utf-8").write(
        page(f"{g} {gi['title']}", bc, body, f"group-{g.lower()}.html", desc=f"{gi['title']}の場面一覧"))
    search_index.append({"url":f"group-{g.lower()}.html","title":f"{g}. {gi['title']}","g":f"{g}・{gi['type']}","t":g+" "+gi["title"]+" "+plain_text(pgroups[g]["note"])})

# ---------- policy page ----------
policy_html=render_blocks(master_body.split("\n"))
bc=crumb(("ハンドブック","index.html"),("方針マスター",None))
open(os.path.join(OUT,"policy.html"),"w",encoding="utf-8").write(
    page("方針マスター", bc, '<h1 class="g-title">方針マスター（単一情報源）</h1>'+policy_html, "policy.html",
         desc="品質保証グループの使命・価値観・ルール・エスカレーション基準"))
search_index.append({"url":"policy.html","title":"方針マスター（使命・ルール・エスカレーション）","g":"方針","t":plain_text(master_body.split("\n"))})

# ---------- glossary page (master §8) ----------
gl_lines=section_lines(master_body,"用語メモ")
gl_html=render_blocks(gl_lines)
# index of all scenarios
sc_index="".join(
    f'<a href="{slug(x["id"])}"><span class="rel-id">{esc(x["id"])}</span>{esc(x["title"])}</a>'
    for x in scenarios)
body=f'''<h1 class="g-title">用語・索引</h1>
<h2>用語メモ</h2><div class="s-body">{gl_html}</div>
<h2>場面インデックス（全{len(scenarios)}場面）</h2><div class="rel-list idx">{sc_index}</div>'''
bc=crumb(("ハンドブック","index.html"),("用語・索引",None))
open(os.path.join(OUT,"glossary.html"),"w",encoding="utf-8").write(page("用語・索引",bc,body,"glossary.html",desc="用語メモと全場面の索引"))
search_index.append({"url":"glossary.html","title":"用語・索引","g":"索引","t":"用語 索引 "+plain_text(gl_lines)})

# ---------- review (要確認) page ----------
def collect_review(body):
    items=[]
    lines=body.split("\n")
    in_appendix=False
    for l in lines:
        st=l.strip()
        if re.match(r"^#{1,4}\s+", st):
            in_appendix = ("要確認リスト" in st)
            continue
        if "【要確認】" in st:
            t=re.sub(r"^>\s*","",st)
            t=re.sub(r"^[-*]\s*\[[ xX]\]\s*","",t)
            t=t.replace("【要確認】","").strip()
            if t: items.append(t)
            continue
        if in_appendix:
            m=re.match(r"^-\s*\[ \]\s+(.*)$", st)
            if m: items.append(m.group(1).strip())
    seen=set(); res=[]
    for it in items:
        if it not in seen: seen.add(it); res.append(it)
    return res

rev_play=collect_review(play_body)
rev_master=collect_review(master_body)
def rev_block(title,href,items):
    lis="".join(f'<li class="chk"><span class="cb"></span><span class="t">{inline(it)}</span></li>' for it in items)
    return f'<h2>{esc(title)} <a class="src-link" href="{href}">原本</a></h2><ul class="checklist">{lis}</ul>'
body=f'''<h1 class="g-title">付録：要確認リスト</h1>
<div class="callout review"><span class="rev-badge">要確認</span><span>未確定（GLの確認待ち）の項目です。確定したら原本Markdownを更新してください。本サイトは原本を反映したものです。</span></div>
{rev_block("方針マスター 由来","content/policy-master.md",rev_master)}
{rev_block("プレイブック集 由来","content/playbooks.md",rev_play)}'''
bc=crumb(("ハンドブック","index.html"),("要確認リスト",None))
open(os.path.join(OUT,"review.html"),"w",encoding="utf-8").write(page("要確認リスト",bc,body,"review.html",desc="未確定（要確認）項目の一覧"))
search_index.append({"url":"review.html","title":"付録：要確認リスト","g":"要確認","t":"要確認 未確定 "+ " ".join(rev_master+rev_play)})

# ---------- hub ----------
prin_html="".join(f'<li><span class="pn">{i+1}</span><div><b>{esc(t)}</b><span>{inline(d)}</span></div></li>' for i,(t,d) in enumerate(principles))
gcards=""
for g,gi in GROUPS.items():
    scs=pgroups[g]["scenarios"]
    lst="".join(f'<a href="{slug(x["id"])}">{esc(x["id"])} {esc(x["title"])}</a>' for x in scs)
    gcards+=f'''<div class="hub-gcard g-{g}">
      <a class="hub-gh" href="group-{g.lower()}.html"><span class="hub-gemoji">{gi["emoji"]}</span><span><b>{esc(g)}. {esc(gi["title"])}</b><span class="hub-gtype">種類：{esc(gi["type"])}・{len(scs)}場面</span></span></a>
      <div class="hub-glist">{lst}</div></div>'''
body=f'''<div class="hub-hero">
  <h1>品質保証グループ ハンドブック</h1>
  <p>方針マスターとプレイブック集を、場面から引けるようにまとめたものです。上の検索、または下のグループから探してください。</p>
</div>
<div class="quick">
  <span class="quick-lab">困ったとき</span>
  <a class="quick-b urgent" href="{slug('B2')}">🚑 クレーム・不適合の初動（B2 封じ込め）</a>
  <a class="quick-b urgent" href="{slug('B1')}">⚠ 優先順位（B1 トリアージ）</a>
  <a class="quick-b" href="policy.html#esc">📣 エスカレーション基準（方針 5.2）</a>
</div>
<section class="hub-sec"><h2>品質の6原則（ブレ防止の共通言語）</h2><ul class="principles">{prin_html}</ul></section>
<section class="hub-sec"><h2>4グループから探す</h2><div class="hub-gcards">{gcards}</div></section>
<section class="hub-sec links"><h2>その他</h2>
  <a href="policy.html">📘 方針マスター（使命・価値観・ルール）</a>
  <a href="glossary.html">📑 用語・索引</a>
  <a href="review.html">🟡 要確認リスト（未確定項目）</a>
  <a href="../">← Daily Insight Board に戻る</a>
</section>'''
open(os.path.join(OUT,"index.html"),"w",encoding="utf-8").write(
    page("ハンドブック","<span>ハンドブック</span>",body,"index.html",
         desc="品質保証グループ 場面別ハンドブック（検索・4グループ・25場面）"))

# search index json
open(os.path.join(ASSETS,"search-index.json"),"w",encoding="utf-8").write(json.dumps(search_index,ensure_ascii=False))
print("scenarios:",len(scenarios),"pages:", len(os.listdir(OUT)))
print("groups counts:",{g:len(pgroups[g]["scenarios"]) for g in GROUPS})
print("principles:",len(principles))
print("review items: master",len(rev_master),"play",len(rev_play))
