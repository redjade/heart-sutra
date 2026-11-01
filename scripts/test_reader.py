"""Regression checks for lossless migration and reader integrity (stdlib only)."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location("build_reader",Path(__file__).with_name("build_reader.py"))
reader=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.data=reader.read_data()

    def test_canonical_translation_matches_generated_document(self):
        text=(reader.ROOT/"translation/01-heart-sutra.md").read_text(encoding="utf-8")
        self.assertEqual(reader.markdown(self.data),text)

    def test_markdown_reading_preserves_paragraphs_and_text(self):
        import re
        documents=reader.markdown_documents(self.data)
        reading=documents[reader.ROOT/"reader/korean.md"]
        scripture=reading.split("<!-- scripture:start -->\n\n",1)[1].split("\n\n<!-- scripture:end -->",1)[0]
        scripture=re.sub(r'<a name="[^"]+"></a>',"",scripture)
        self.assertEqual(scripture,reader.korean(self.data))
        self.assertEqual(len(scripture.split("\n\n")),11)
        reader.check_markdown_links(documents)

    def test_markdown_notes_terms_and_source_preserve_wording(self):
        documents=reader.markdown_documents(self.data)
        parallel=documents[reader.ROOT/"reader/parallel.md"]
        notes=documents[reader.ROOT/"reader/notes.md"]
        terms=documents[reader.ROOT/"reader/terms.md"]
        for unit in self.data["units"]:
            self.assertIn(unit["chinese"],parallel)
            self.assertIn(unit["reading"],parallel)
        for note in self.data["notes"]:
            self.assertIn(note["text"],notes)
        for term in self.data["terms"]:
            for field in ["sanskrit_comparison","translation","decision"]:
                self.assertIn(term[field],terms)

    def test_reading_edition_keeps_content_together_before_navigation(self):
        import re
        reading=reader.markdown_documents(self.data)[reader.ROOT/"reader/korean.md"]
        visible=re.sub(r'<a name="[^"]+"></a>',"",reading)
        self.assertEqual(re.findall(r"^## (.+)$",visible,re.M),[
            "한글 번역","번역 주","한문과 현토 독음","더 살펴보기",
        ])
        main,navigation=reading.split("\n\n---\n\n## 더 살펴보기",1)
        self.assertNotRegex(main,r"\]\(")
        self.assertTrue(main.rstrip().endswith(self.data["units"][-1]["reading"]))
        for note in self.data["notes"]:
            self.assertIn(note["text"],main)
        for unit in self.data["units"]:
            self.assertIn(unit["chinese"],main)
            self.assertIn(unit["reading"],main)
        self.assertIn("parallel.md",navigation)
        self.assertIn("terms.md",navigation)
        # Visible reading content matches the original, apart from hidden anchors
        # and the equivalent Markdown hard-break spelling.
        plain=re.sub(r"<!--.*?-->","",main,flags=re.S)
        plain=re.sub(r'<a name="[^"]+"></a>',"",plain)
        plain=plain.replace("\\\n","  \n")
        plain=re.sub(r"\n{3,}","\n\n",plain).strip()
        self.assertEqual(plain,reader.markdown(self.data).strip())

    def test_broken_markdown_return_link_fails(self):
        documents=reader.markdown_documents(self.data)
        path=reader.ROOT/"reader/notes.md"
        documents[path]=documents[path].replace("korean.md#hs-001","korean.md#hs-missing",1)
        with self.assertRaisesRegex(ValueError,"Missing Markdown anchor"):
            reader.check_markdown_links(documents)

    def test_duplicate_markdown_anchor_fails(self):
        documents=reader.markdown_documents(self.data)
        path=reader.ROOT/"reader/korean.md"
        documents[path]+='\n<a name="hs-001"></a>\n'
        with self.assertRaisesRegex(ValueError,"Duplicate Markdown anchor"):
            reader.check_markdown_links(documents)

    def test_duplicate_ids_fail(self):
        self.data["units"][1]["id"]=self.data["units"][0]["id"]
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            reader.validate(self.data)

    def test_dangling_note_and_term_fail(self):
        for kind,key in [("units","note_ids"),("terms","unit_ids")]:
            changed=copy.deepcopy(self.data)
            changed[kind][0][key].append("missing")
            with self.assertRaisesRegex(ValueError,"Dangling"):
                reader.validate(changed)

    def test_source_tamper_fails(self):
        import json
        lock=json.loads((reader.ROOT/"data/source-lock.json").read_text(encoding="utf-8"))
        raw=reader.source_bytes(lock)
        reader.check_source(self.data,raw)
        changed=copy.deepcopy(self.data)
        changed["units"][0]["chinese"]=changed["units"][0]["chinese"].replace("觀","見",1)
        with self.assertRaisesRegex(ValueError,"Chinese differs"):
            reader.check_source(changed,raw)

    def test_html_is_escaped(self):
        self.data["translation_blocks"][0]["segments"][0]["text"]='<img src=x onerror=alert(1)> </script>'
        rendered=reader.render(self.data)
        self.assertNotIn('<img src=x',rendered)
        self.assertIn('&lt;img src=x',rendered)
        self.assertNotIn('</script>"',rendered)

    def test_static_links_and_ids_resolve(self):
        from html.parser import HTMLParser
        class Anchors(HTMLParser):
            def __init__(self):
                super().__init__(); self.ids=[]; self.targets=[]
            def handle_starttag(self,tag,attrs):
                attrs=dict(attrs)
                if 'id' in attrs:self.ids.append(attrs['id'])
                if tag=='a' and attrs.get('href','').startswith('#'):self.targets.append(attrs['href'][1:])
        parser=Anchors(); parser.feed(reader.render(self.data))
        self.assertEqual(len(parser.ids),len(set(parser.ids)))
        self.assertTrue(set(parser.targets)<=set(parser.ids))

    def test_build_is_deterministic(self):
        import json
        lock=json.loads((reader.ROOT/"data/source-lock.json").read_text(encoding="utf-8"))
        raw=reader.source_bytes(lock)
        cache=reader.ROOT/".cache"
        cache.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as tmp:
            first,second=Path(tmp)/"a",Path(tmp)/"b"
            reader.build(self.data,raw,first); reader.build(self.data,raw,second)
            files=[p.relative_to(first) for p in first.rglob('*') if p.is_file()]
            self.assertEqual(sorted(map(str,files)),sorted(str(p.relative_to(second)) for p in second.rglob('*') if p.is_file()))
            for path in files:self.assertEqual((first/path).read_bytes(),(second/path).read_bytes())

    def test_stale_generated_asset_fails(self):
        import json
        lock=json.loads((reader.ROOT/"data/source-lock.json").read_text(encoding="utf-8"))
        raw=reader.source_bytes(lock)
        with tempfile.TemporaryDirectory(dir=reader.ROOT/".cache") as tmp:
            output=Path(tmp).resolve()
            self.assertTrue(output.is_relative_to(reader.ROOT.resolve()))
            reader.build(self.data,raw,output)
            (output/"reader.js").write_text("stale",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"stale"):
                reader.check_outputs(self.data,raw,output)

if __name__=="__main__":
    unittest.main()
