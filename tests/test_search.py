"""weft index and site/search.js: what the public index holds, and what a reader finds."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from weft import about, search
from weft.paths import private_works

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def index():
    return search.build_index(REPO)


def test_the_public_index_holds_every_public_work_and_nothing_private(index):
    names = [w["w"] for w in index["works"]]
    public = sorted(p.parent.name for p in (REPO / "texts").glob("*/manifest.yaml"))
    assert sorted(names) == public
    assert not set(names) & set(private_works(REPO))
    assert index["private"] is False


def test_no_reference_translation_is_indexed(index):
    """A translation still in copyright (kind: reference) is cited on the page, never printed or indexed."""
    for w in index["works"]:
        m = yaml.safe_load((REPO / "texts" / w["w"] / "manifest.yaml").read_text())
        cited = {t["translator"] for t in m.get("translations", []) if t.get("kind") == "reference"}
        assert not cited & {s[2] for s in w["S"]}, w["w"]


def test_every_work_has_an_about_and_token_ids_are_positional(index):
    r = search.report(index)
    assert r["failures"] == {}, r["samples"]
    # the index stores no token IDs: a token's ID is its line's ID and its position, which the data keeps true
    from weft.build import assemble
    d = assemble(REPO / "texts" / "homer-odyssey")
    assert [t["id"] for t in d["lines"][0]["tokens"]] == [f"{d['lines'][0]['id']}.{i}" for i in range(1, len(d["lines"][0]["tokens"]) + 1)]


def test_a_curated_about_stands_in_where_no_article_fits():
    a = about.load(REPO / "texts" / "swahili-tales-steere")
    assert a["source"] == "curated" and "fable" in a["subjects"] and a["summary"]
    a = about.load(REPO / "texts" / "inter-caetera-1493")
    assert a["source"] == "wikipedia" and "papal bull" in a["subjects"]
    assert about.curated_problems({"by": "x", "date": "2026", "status": "maybe", "summary": "s", "subjects": ["a", 3]}) == \
        ["about-curated-status", "about-curated-subjects"]


NODE = shutil.which("node")


@pytest.mark.skipif(not NODE, reason="node is not installed")
def test_what_a_reader_finds(index, tmp_path):
    """The acceptance searches, run through site/search.js itself."""
    (tmp_path / "index.json").write_text(json.dumps(index, ensure_ascii=False))
    script = tmp_path / "q.js"
    script.write_text(f"""
const S = require({json.dumps(str(REPO / "site" / "search.js"))});
const idx = JSON.parse(require("fs").readFileSync({json.dumps(str(tmp_path / "index.json"))}, "utf8"));
const out = {{}};
for (const q of ["fable", "saga", "pope", "god", "epic", "ulfr", "θεος", "王"]) {{
  const r = S.search(idx, q);
  out[q] = {{works: r.works.map(x => x.work.w), gloss: r.word.filter(g => g.kind === "gloss").map(g => [g.lang, g.lemma]),
            form: r.word.filter(g => g.kind === "form").map(g => g.lemma), lines: r.lines.map(x => x.work.w)}};
}}
console.log(JSON.stringify(out));""")
    r = json.loads(subprocess.run([NODE, str(script)], capture_output=True, text=True, check=True).stdout)
    assert r["fable"]["works"][0] == "swahili-tales-steere"
    assert r["saga"]["works"][0] == "saga-grettir" and "edda-grimnismal" in r["saga"]["lines"]
    assert r["pope"]["works"][0] == "inter-caetera-1493" and r["pope"]["lines"][0] == "luther-95-theses"
    langs = {lang for lang, _ in r["god"]["gloss"]}
    assert len(langs) >= 10 and {"θεός", "deus", "Gott"} <= {lemma for _, lemma in r["god"]["gloss"]}
    assert "epictetus-enchiridion" not in r["epic"]["works"] and "homer-iliad" in r["epic"]["works"]   # whole words
    assert {"úlfr", "ulfr"} <= set(r["ulfr"]["form"])        # accents folded
    assert "θεός" in r["θεος"]["form"]
    assert "yijing" in r["王"]["lines"]                      # Chinese: matched within the text
