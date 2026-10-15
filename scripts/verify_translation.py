"""Verify the reading layout and optionally compare Chinese with pinned CBETA T251."""

import argparse
import difflib
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CBETA = "https://raw.githubusercontent.com/cbeta-org/xml-p5/dbdea41071e1e260ad84b72faefd4587333cf76d/T/T08/T08n0251.xml"
CJK = re.compile(r"[\u3400-\u9fff]")
TEI = "{http://www.tei-c.org/ns/1.0}"
CB = "{http://www.cbeta.org/ns/1.0}"


def han(text):
    return "".join(CJK.findall(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cbeta", action="store_true")
    args = parser.parse_args()
    path = ROOT / "translation" / "01-heart-sutra.md"
    text = path.read_text(encoding="utf-8")
    assert re.findall(r"^## (.+)$", text, re.MULTILINE) == [
        "한글 번역", "번역 주", "한문과 현토 독음"
    ], "Unexpected section order"
    korean = text.split("## 한글 번역", 1)[1].split("## 번역 주", 1)[0]
    assert korean.count("“") == korean.count("”"), "Unbalanced Korean quotation marks"
    lines = [line for line in text.split("## 한문과 현토 독음", 1)[1].splitlines() if line.strip()]
    assert len(lines) % 2 == 0, "Incomplete Chinese/reading pair"
    chinese = ""
    for source, reading in zip(lines[::2], lines[1::2]):
        assert re.fullmatch(r"\*\*.+\*\*  ", source), "Missing bold Chinese or Markdown line break"
        assert not CJK.search(reading), "Chinese character remains in Hangul reading"
        assert not reading.startswith(">"), "Unexpected reading blockquote"
        chinese += han(source)
    assert len(chinese) == 260, f"Expected 260 Chinese characters, got {len(chinese)}"
    for document in ROOT.rglob("*.md"):
        if ".git" in document.parts:
            continue
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if not re.match(r"https?://|#", target):
                assert (document.parent / target.split("#", 1)[0]).exists(), (document, target)
    print(f"PASS: headings, {len(lines) // 2} Chinese/reading pairs, 260 characters, quotes, local links")
    if not args.cbeta:
        return
    with urllib.request.urlopen(CBETA, timeout=30) as response:
        root = ET.fromstring(response.read())
    sutra = root.find(f".//{TEI}body/{CB}div[@type='jing']")
    assert sutra is not None, "CBETA sutra body not found"
    # Keep the concluding mantra; exclude prefaces, titles, and apparatus.
    remote = han("".join(sutra.itertext()))
    changes = [
        item for item in difflib.SequenceMatcher(None, remote, chinese, autojunk=False).get_opcodes()
        if item[0] != "equal"
    ]
    for operation, a, b, c, d in changes:
        print(f"{operation}: CBETA={remote[a:b]!r}; local={chinese[c:d]!r}")
    assert not changes, "Chinese text differs from pinned CBETA T251"
    print(f"PASS: exact match to CBETA T251 ({len(remote)} characters, including mantra)")


if __name__ == "__main__":
    main()
