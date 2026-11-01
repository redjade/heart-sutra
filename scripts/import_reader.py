"""One-time, non-overwriting import of the reviewed Markdown into reader data."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CBETA_COMMIT = "dbdea41071e1e260ad84b72faefd4587333cf76d"
URL = f"https://raw.githubusercontent.com/cbeta-org/xml-p5/{CBETA_COMMIT}/T/T08/T08n0251.xml"
LABELS = ["다섯 무더기", "형상과 공", "나머지 네 무더기", "공의 특징", "오온의 부정", "감각 기관과 대상", "감각 영역", "무명에서 늙음과 죽음까지", "괴로움과 길, 앎과 얻음", "마음에 걸림이 없음", "두려움과 열반", "세 시대의 부처", "지혜의 완성과 진언", "진언의 선언", "진언을 말함", "진언"]
NOTE_LINKS = [[1,2,3,7,8],[4],[3,4],[13,16],[4,16],[3,10],[10],[10,16],[5,7,10,13],[5,11],[5,11],[15],[1,12,13],[14],[14],[6,9]]
READINGS = {"般若":"반야", "波羅蜜多":"바라밀다", "般若波羅蜜多":"반야바라밀다", "心經":"심경", "觀自在":"관자재", "菩薩":"보살", "五蘊":"오온", "皆空":"개공", "舍利子":"사리자", "色":"색", "受":"수", "想":"상", "行":"행", "識":"식", "空":"공", "諸法":"제법", "空相":"공상", "不生不滅":"불생불멸", "不垢不淨":"불구부정", "不增不減":"부증불감", "苦集滅道":"고집멸도", "智":"지", "得":"득", "以無所得故":"이무소득고", "心無罣礙":"심무가애", "無有恐怖":"무유공포", "遠離顛倒夢想":"원리전도몽상", "究竟涅槃":"구경열반", "三世":"삼세", "阿耨多羅三藐三菩提":"아뇩다라삼먁삼보리", "大神咒":"대신주", "大明咒":"대명주", "無上咒":"무상주", "無等等咒":"무등등주"}
# Editorial cross-references, not automated word matching or Sanskrit alignment.
TERM_UNITS = [[1,10,12,13,14],[1,10,12,13,14],[1,10,12,13,14],[],[1],[1,10],[1],[1],[1],[1],[1],[2,4],[2,5,6],[3,5],[3,5],[3,5],[3,5],[1,2,4,5],[2],[4],[4],[4],[4],[4],[6],[6],[7],[8],[8],[9],[9],[9],[10],[10,12],[10],[11],[11],[11],[12],[12],[13],[13],[13],[13],[14],[14]]

def main():
    destination = ROOT / "data/heart-sutra.json"
    if destination.exists():
        raise SystemExit("Refusing to overwrite canonical data")
    original = (ROOT / "translation/01-heart-sutra.md").read_text(encoding="utf-8")
    korean = original.split("## 한글 번역\n\n")[1].split("\n\n## 번역 주")[0]
    paragraphs = korean.split("\n\n")
    assert len(paragraphs) == 11
    # Each split consumes the existing text; no scripture is retyped here.
    mapping = [[(1,None)],[(2,"느낌과"),(3,None)],[(4,None)],[(5,None)],[(6,"눈의 영역"),(7,None)],[(8,"괴로움·"),(9,None)],[(10,"걸림이 없으므로"),(11,None)],[(12,None)],[(13,"모든 괴로움을"),(14,None)],[(14,"곧 진언은"),(15,None)],[(16,None)]]
    blocks = []
    for paragraph, parts in zip(paragraphs,mapping):
        segments = []
        remaining = paragraph
        for number, marker in parts:
            if marker:
                index = remaining.index(marker)
                text, remaining = remaining[:index],remaining[index:]
            else:
                text, remaining = remaining,""
            segments.append({"unit_id":f"hs-{number:03}","text":text})
        assert not remaining
        blocks.append({"segments":segments})
    lines = [line for line in original.split("## 한문과 현토 독음\n\n")[1].splitlines() if line.strip()]
    units = [{"id":f"hs-{i+1:03}","label":label,"chinese":lines[2*i][2:-4],"reading":lines[2*i+1],"note_ids":[f"note-{n:02}" for n in notes]} for i,(label,notes) in enumerate(zip(LABELS,NOTE_LINKS))]
    note_text = original.split("## 번역 주\n\n")[1].split("\n\n## 한문과 현토 독음")[0]
    notes = [{"id":f"note-{int(n):02}","number":int(n),"text":text,"gap_after":"\n\n" if int(n)==15 else "\n"} for n,text in re.findall(r"^(\d+)\. (.+)$",note_text,re.M)]
    terms=[]
    for line in (ROOT / "SOURCES.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells=[cell.strip() for cell in line.strip("|").split("|")]
        assert len(cells)==4
        chinese=cells[0].strip("`")
        terms.append({"id":f"term-{len(terms)+1:02}","chinese":chinese,"sanskrit_comparison":cells[1],"translation":cells[2],"decision":cells[3],"conventional_reading":READINGS.get(chinese),"unit_ids":[f"hs-{n:03}" for n in TERM_UNITS[len(terms)]]})
    assert len(terms)==len(TERM_UNITS), (len(terms),len(TERM_UNITS))
    revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    data={"schema_version":1,"work_id":"heart-sutra","title":"반야바라밀다심경(般若波羅蜜多心經)","short_title":"반야심경","status":"번역·교정 중인 초안","base_witness":"현장 역 T08 No.251 · CBETA 교감 주본문","comparison_witness":"GRETIL 산스크리트 소본 · 대응 어구와 판본 차이 대조","import":{"commit":revision,"markdown_sha256_lf":hashlib.sha256(original.encode()).hexdigest(),"terms_source":"SOURCES.md · 2026-11-01 반입 당시 표의 문구"},"translation_blocks":blocks,"units":units,"notes":notes,"terms":terms}
    raw=urllib.request.urlopen(URL,timeout=30).read()
    destination.parent.mkdir(exist_ok=True)
    cache=ROOT/".cache/T08n0251.xml"
    cache.parent.mkdir(exist_ok=True)
    cache.write_bytes(raw)
    lock={"id":"cbeta-t251","url":URL,"commit":CBETA_COMMIT,"sha256":hashlib.sha256(raw).hexdigest(),"han_count":260,"cache":".cache/T08n0251.xml"}
    (ROOT/"data/source-lock.json").write_text(json.dumps(lock,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"Imported {len(units)} units, {len(notes)} notes, {len(terms)} terms; source SHA-256 locked")

if __name__=="__main__":
    main()
