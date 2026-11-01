"""Validate canonical reader data; generate Markdown and an offline static reader."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import urllib.request
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TEI = "{http://www.tei-c.org/ns/1.0}"
CB = "{http://www.cbeta.org/ns/1.0}"
HAN = re.compile(r"[\u3400-\u9fff]")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read_data():
    return json.loads((ROOT/"data/heart-sutra.json").read_text(encoding="utf-8"))

def korean(data):
    return "\n\n".join("".join(s["text"] for s in b["segments"]) for b in data["translation_blocks"])

def unit_korean(data, unit_id):
    return "\n\n".join(s["text"].strip() for b in data["translation_blocks"] for s in b["segments"] if s["unit_id"]==unit_id)

def markdown(data):
    notes="".join(f'{n["number"]}. {n["text"]}{n["gap_after"]}' for n in data["notes"]).rstrip("\n")
    pairs="\n\n".join(f'**{u["chinese"]}**  \n{u["reading"]}' for u in data["units"])
    return f'# {data["title"]}\n\n## 한글 번역\n\n{korean(data)}\n\n## 번역 주\n\n{notes}\n\n## 한문과 현토 독음\n\n{pairs}\n'

def validate(data):
    require(data["schema_version"]==1,"Unsupported schema")
    require(data["work_id"]=="heart-sutra","Unexpected work")
    ids=[]
    for kind in ["units","notes","terms"]:
        ids += [item["id"] for item in data[kind]]
    require(len(ids)==len(set(ids)),"Duplicate ID")
    units={u["id"] for u in data["units"]}
    notes={n["id"] for n in data["notes"]}
    require(all(re.fullmatch(r"hs-\d{3}",i) for i in units),"Invalid unit ID")
    require([n["number"] for n in data["notes"]]==list(range(1,len(notes)+1)),"Invalid note numbering")
    require(all(set(u["note_ids"])<=notes for u in data["units"]),"Dangling note reference")
    require(set().union(*(set(u["note_ids"]) for u in data["units"]))==notes,"Unlinked note")
    require(all(set(t["unit_ids"])<=units for t in data["terms"]),"Dangling term reference")
    segments=[s for b in data["translation_blocks"] for s in b["segments"]]
    require({s["unit_id"] for s in segments}==units,"Missing or dangling translation unit")
    require(all(isinstance(s["text"],str) and s["text"].strip() for s in segments),"Empty translation")
    order=[s["unit_id"] for s in segments]
    require(list(dict.fromkeys(order))==[u["id"] for u in data["units"]],"Translation order differs")
    require(order==sorted(order,key=lambda i:[u["id"] for u in data["units"]].index(i)),"Discontinuous unit")
    require(korean(data).count("“")==korean(data).count("”"),"Unbalanced quotes")
    require(all(not HAN.search(u["reading"]) for u in data["units"]),"Chinese in Hangul reading")
    for collection in (data["units"],data["notes"],data["terms"]):
        require(all(re.fullmatch(r"[a-z]+-\d+",item["id"]) for item in collection),"Unsafe ID")

def source_bytes(lock, fetch=False):
    path=ROOT/lock["cache"]
    if fetch or not path.exists():
        raw=urllib.request.urlopen(lock["url"],timeout=30).read()
        require(hashlib.sha256(raw).hexdigest()==lock["sha256"],"Downloaded source checksum differs")
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
    raw=path.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==lock["sha256"],"Cached source checksum differs")
    return raw

def check_source(data, raw):
    root=ET.fromstring(raw)
    sutra=root.find(f".//{TEI}body/{CB}div[@type='jing']")
    require(sutra is not None,"CBETA sutra body missing")
    expected="".join(HAN.findall("".join(sutra.itertext())))
    actual="".join(HAN.findall("".join(u["chinese"] for u in data["units"])))
    require(len(expected)==260 and actual==expected,"Chinese differs from pinned CBETA body")
    return len(expected)

def check_migration(data):
    original=subprocess.check_output(["git","show",f'{data["import"]["commit"]}:translation/01-heart-sutra.md'],cwd=ROOT).decode("utf-8").replace("\r\n","\n")
    require(hashlib.sha256(original.encode()).hexdigest()==data["import"]["markdown_sha256_lf"],"Migration baseline checksum differs")
    require(markdown(data)==original,"Migration changed existing Markdown")
    print("PASS: lossless migration of translation, notes, Chinese, reading and paragraph layout")

def inline(text):
    # Source notes support only escaped prose and inline code. Never execute Markdown HTML.
    return re.sub(r"`([^`]+)`",r"<code>\1</code>",html.escape(text))

def link(unit_id,label=None):
    return f'<a href="#compare-{unit_id}" data-unit-link="{unit_id}">{html.escape(label or unit_id[-3:])}</a>'

def render(data):
    esc=html.escape
    nav="".join(f'<a href="#{u["id"]}" data-jump="{u["id"]}"><span>{i:02}</span>{esc(u["label"])}</a>' for i,u in enumerate(data["units"],1))
    paragraphs=[]
    for block in data["translation_blocks"]:
        spans=[]
        for segment in block["segments"]:
            uid=segment["unit_id"]
            # Unit 14 crosses a paragraph boundary: only its first fragment owns the ID.
            seen=any(f'id="{uid}"' in p for p in paragraphs) or any(f'id="{uid}"' in s for s in spans)
            anchor="" if seen else f' id="{uid}"'
            spans.append(f'<span{anchor} data-unit="{uid}">{esc(segment["text"])}</span>')
        paragraphs.append('<p>'+"".join(spans)+'</p>')
    rows=[]
    for i,u in enumerate(data["units"],1):
        uid=u["id"]
        note_links=" ".join(f'<a href="#{n}" data-note-link="{n}">주 {int(n[-2:])}</a>' for n in u["note_ids"])
        ko="".join(f'<p>{esc(p)}</p>' for p in unit_korean(data,uid).split("\n\n"))
        rows.append(f'<article class="comparison" id="compare-{uid}"><header><span class="number">{i:02}</span><h3>{esc(u["label"])}</h3><a class="permalink" href="#compare-{uid}" aria-label="구절 {i} 고유 링크">#</a></header><div class="pair"><div class="translated">{ko}</div><div><p lang="zh-Hant" class="chinese">{esc(u["chinese"])}</p><p class="reading">{esc(u["reading"])}</p></div></div><div class="references">{note_links}</div></article>')
    notes=[]
    for n in data["notes"]:
        back=" · ".join(link(u["id"],f'{int(u["id"][-3:]):02} {u["label"]}') for u in data["units"] if n["id"] in u["note_ids"])
        notes.append(f'<article class="note" id="{n["id"]}"><h3>번역 주 {n["number"]}</h3><p>{inline(n["text"])}</p><div class="backlinks">관련 구절 {back}</div></article>')
    terms=[]
    for t in data["terms"]:
        reading=f'<span class="term-reading">{esc(t["conventional_reading"])}</span>' if t["conventional_reading"] else ''
        refs=" · ".join(link(uid) for uid in t["unit_ids"]) or '제목'
        terms.append(f'<article class="term" id="{t["id"]}"><h3><span lang="zh-Hant">{esc(t["chinese"])}</span>{reading}</h3><p class="sanskrit">{inline(t["sanskrit_comparison"])}</p><p class="chosen"><span>이 번역</span> {esc(t["translation"])}</p><details><summary>선택 이유와 판본 차이</summary><p>{inline(t["decision"])}</p></details><div class="backlinks">관련 구절 {refs}</div></article>')
    substitutions={"NAV":nav,"READING":"\n".join(paragraphs),"PARALLEL":"\n".join(rows),"NOTES":"\n".join(notes),"TERMS":"\n".join(terms),"DATA":json.dumps(data,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")}
    template=(ROOT/"reader/index.html").read_text(encoding="utf-8")
    return re.sub(r"@@([A-Z]+)@@",lambda m:substitutions[m[1]],template)

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding="utf-8",newline="\n")

def outputs(data,raw,site_dir):
    result={ROOT/"translation/01-heart-sutra.md":markdown(data).encode("utf-8")}
    parallel="# 반야심경 구절별 대조\n\n이 문서는 `data/heart-sutra.json`에서 생성한다. 구절 소제목은 편집상 안내다.\n\n"
    for u in data["units"]:
        parallel+=f'## {u["id"]} · {u["label"]}\n\n{unit_korean(data,u["id"])}\n\n**{u["chinese"]}**\\\n{u["reading"]}\n\n관련 번역 주: '+", ".join(str(int(n[-2:])) for n in u["note_ids"])+"\n\n"
    result[ROOT/"reader/parallel.md"]=(parallel.rstrip()+"\n").encode("utf-8")
    terms="# 반야심경 용어 대응표\n\n이 문서는 `data/heart-sutra.json`에서 생성한다. 산스크리트는 기존 근거 기록의 대조 어구이며 한역의 일대일 대응 원본을 뜻하지 않는다. 관용 독음은 일반 번역어의 전체 조사를 대신하지 않는다.\n\n"
    terms+="| 한역 용어 | 관용 독음 | 산스크리트 대조 어구 | 이 번역의 표기 | 관련 구절 |\n| --- | --- | --- | --- | --- |\n"
    for t in data["terms"]:
        terms+=f'| {t["chinese"]} | {t["conventional_reading"] or "—"} | {t["sanskrit_comparison"]} | {t["translation"]} | '+", ".join(t["unit_ids"])+" |\n"
    result[ROOT/"reader/terms.md"]=terms.encode("utf-8")
    result[site_dir/"index.html"]=render(data).encode("utf-8")
    for name in ["reader.css","reader.js"]:
        result[site_dir/name]=(ROOT/"reader/assets"/name).read_bytes()
    for name in ["SOURCES.md","LICENSE.md"]:
        text=(ROOT/name).read_text(encoding="utf-8")
        # The research document links back to repository documents, not nonexistent site paths.
        base='https://github.com/redjade/heart-sutra/blob/main/'
        text=re.sub(r"\]\(([^)]+)\)",lambda m:"]("+(m[1] if re.match(r"https?://|#",m[1]) else urljoin(base,m[1]))+")",text)
        result[site_dir/name]=text.encode("utf-8")
    for name in ["heart-sutra.json","source-lock.json"]:
        result[site_dir/name]=(ROOT/"data"/name).read_bytes()
    result[site_dir/"translation.md"]=markdown(data).encode("utf-8")
    result[site_dir/"sources/T08n0251.xml"]=raw # Entire original header retained.
    return result

def build(data,raw,site_dir):
    for path,content in outputs(data,raw,site_dir).items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(content)

def check_outputs(data,raw,site_dir):
    for path,expected in outputs(data,raw,site_dir).items():
        require(path.is_file(),f"Generated file missing: {path}")
        actual=path.read_bytes()
        if path.suffix==".md":
            actual=actual.replace(b"\r\n",b"\n")
        require(actual==expected,f"Generated file is stale: {path}")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true",help="validate data and generated files, without writing")
    parser.add_argument("--check-migration",action="store_true",help="assert exact equality with import baseline; use for initial migration only")
    parser.add_argument("--fetch-source",action="store_true")
    parser.add_argument("--site-dir",type=Path,default=ROOT/"dist")
    args=parser.parse_args()
    data=read_data()
    validate(data)
    lock=json.loads((ROOT/"data/source-lock.json").read_text(encoding="utf-8"))
    raw=source_bytes(lock,args.fetch_source)
    count=check_source(data,raw)
    if args.check_migration:
        check_migration(data)
    if args.check:
        check_outputs(data,raw,args.site_dir.resolve())
    else:
        build(data,raw,args.site_dir.resolve())
    print(f'PASS: {len(data["units"])} units, {len(data["notes"])} notes, {len(data["terms"])} terms, {count} pinned Chinese characters')

if __name__=="__main__":
    main()
