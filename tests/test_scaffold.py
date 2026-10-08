"""weft scaffold / pin / image / overlay: the building tools (docs/building.md)."""
from pathlib import Path

import pytest
import yaml

from weft import scaffold

REPO = Path(__file__).resolve().parents[1]


def test_expand_code_matches_the_havamal_grammar():
    e = scaffold.expand_code
    assert e("N.afp") == "NOUN|Case=Acc|Gender=Fem|Number=Plur"
    assert e("PN.gms") == "PROPN|Case=Gen|Gender=Masc|Number=Sing"
    assert e("A.nms.c") == "ADJ|Case=Nom|Degree=Cmp|Gender=Masc|Number=Sing"
    assert e("V.i3s.pr.neg") == "VERB|Mood=Ind|Number=Sing|Person=3|Polarity=Neg|Tense=Pres"
    assert e("AUX.i3s.pr") == "AUX|Mood=Ind|Number=Sing|Person=3|Tense=Pres"
    assert e("V.pp.nms") == "VERB|Case=Nom|Gender=Masc|Number=Sing|Tense=Past|VerbForm=Part"
    assert e("V.inf") == "VERB|VerbForm=Inf"
    assert e("V.imp2s") == "VERB|Mood=Imp|Number=Sing|Person=2|Tense=Pres"
    assert e("V.i1s.pr.m") == "VERB|Mood=Ind|Number=Sing|Person=1|Tense=Pres|Voice=Mid"
    assert e("P.ns1") == "PRON|Case=Nom|Number=Sing|Person=1"
    assert e("P.as3m") == "PRON|Case=Acc|Gender=Masc|Number=Sing|Person=3"
    assert e("P.ds3") == "PRON|Case=Dat|Person=3|Reflex=Yes"
    assert e("DEM.nms") == "PRON|Case=Nom|Gender=Masc|Number=Sing|PronType=Dem"
    assert e("POSS.ams") == "DET|Case=Acc|Gender=Masc|Number=Sing|Poss=Yes"
    assert e("D.fs") == "DET|Definite=Def|Gender=Fem|Number=Sing|PronType=Art"
    assert e("CC") == "CCONJ" and e("ADP") == "ADP"
    assert e("NOUN|Case=Nom") == "NOUN|Case=Nom"          # already UD: passed through
    assert e("ADP + PRON") == "ADP + PRON"
    with pytest.raises(ValueError):
        e("N.xyz")
    with pytest.raises(ValueError):
        e("Q.nms")


def test_expand_code_reproduces_a_committed_overlay():
    """Every morph string in the Hávamál 81-110 overlay is reachable from the compact grammar
    (the overlay was produced by it); spot-check a sample against the file."""
    text = (REPO / "texts/edda-havamal/curated/stanzas-81-110.yaml").read_text()
    assert 'hav.81.1.2: {lemma: "kveld", morph: "NOUN|Case=Dat|Gender=Neut|Number=Sing"' in text
    assert scaffold.expand_code("N.dns") == "NOUN|Case=Dat|Gender=Neut|Number=Sing"
    assert 'hav.81.2.3: {lemma: "brenna", morph: "VERB|Case=Nom|Gender=Fem|Number=Sing|Tense=Past|VerbForm=Part"' in text
    assert scaffold.expand_code("V.pp.nfs") == "VERB|Case=Nom|Gender=Fem|Number=Sing|Tense=Past|VerbForm=Part"


def test_parse_line_spec_metre_staves_and_note():
    metre, toks = scaffold.parse_line_spec("a g :: *Gáttir|doorways|gátt|N.nfp ;; allar,|all|allr|A.nfp | irregular")
    assert metre == "long line, a-verse · stave g · irregular"
    assert [t["surface"] for t in toks] == ["Gáttir", "allar,"]
    assert toks[0]["stave"] and not toks[1]["stave"]
    assert toks[0]["morph"] == "NOUN|Case=Nom|Gender=Fem|Number=Plur"
    metre, toks = scaffold.parse_line_spec("f sk :: skal|shall|skulu|AUX.i3s.pr")
    assert metre == "full line · staves sk"
    metre, toks = scaffold.parse_line_spec("Die|the|der|D.fs")        # prose: no metre
    assert metre is None and toks[0]["lemma"] == "der"
    with pytest.raises(ValueError):
        scaffold.parse_line_spec("Die|the|der")


def _fake_work(tmp_path: Path, surfaces) -> Path:
    wd = tmp_path / "texts" / "fake-work"
    (wd / "gen").mkdir(parents=True)
    (wd / "manifest.yaml").write_text("work: fake-work\n")
    lines = [{"id": "fk.1.1", "tokens": [{"id": f"fk.1.1.{i}", "surface": s} for i, s in enumerate(surfaces, 1)]}]
    (wd / "gen" / "lines.yaml").write_text(yaml.dump({"work": "fake-work", "lines": lines}, allow_unicode=True))
    (wd / "gen" / "lines.run.yaml").write_text("run: {}\n")
    return wd


def test_overlay_expands_a_spec_and_refuses_a_mismatch(tmp_path, monkeypatch):
    from weft import paths
    monkeypatch.setattr(paths, "work_dir", lambda repo, work: tmp_path / "texts" / work)
    _fake_work(tmp_path, ["Gáttir", "allar,"])
    spec = tmp_path / "spec.yaml"
    spec.write_text(yaml.dump({"by": "test", "date": "2026-10-05", "why": "test", "status": "draft",
                               "lines": {"fk.1.1": "a g :: *Gáttir|doorways|gátt|N.nfp ;; allar,|all|allr|A.nfp"}}, allow_unicode=True))
    r = scaffold.overlay(tmp_path, "fake-work", spec, "stanzas-1.yaml")
    assert r == {"wrote": "texts/fake-work/curated/stanzas-1.yaml", "lines": 1, "tokens": 2}
    out = yaml.safe_load((tmp_path / "texts/fake-work/curated/stanzas-1.yaml").read_text())
    assert out[0]["status"] == "draft" and out[0]["by"] == "test"
    s = out[0]["set"]
    assert s["fk.1.1"] == {"metre": "long line, a-verse · stave g"}
    assert s["fk.1.1.1"] == {"lemma": "gátt", "morph": "NOUN|Case=Nom|Gender=Fem|Number=Plur", "gloss": "doorways", "stave": True}
    assert s["fk.1.1.2"] == {"lemma": "allr", "morph": "ADJ|Case=Nom|Gender=Fem|Number=Plur", "gloss": "all"}
    # a surface that is not the text's: refused, nothing written
    spec.write_text(yaml.dump({"lines": {"fk.1.1": "Gáttir|doorways|gátt|N.nfp ;; allir,|all|allr|A.nmp"}}, allow_unicode=True))
    with pytest.raises(SystemExit, match="does not match"):
        scaffold.overlay(tmp_path, "fake-work", spec, "bad.yaml")
    assert not (tmp_path / "texts/fake-work/curated/bad.yaml").exists()
    spec.write_text(yaml.dump({"lines": {"fk.9.9": "x|x|x|N"}}))
    with pytest.raises(SystemExit, match="not in gen"):
        scaffold.overlay(tmp_path, "fake-work", spec, "bad.yaml")


def test_reuse_map_reads_the_library_overlays():
    m = scaffold.reuse_map(REPO, ["edda-havamal"])
    assert m["ek"][0][:2] == ["ek", "PRON|Case=Nom|Number=Sing|Person=1"]
    assert all(len(v) <= 3 for v in m.values())


def test_scaffold_writes_manifest_and_edition_skeletons(tmp_path):
    files = scaffold.scaffold(tmp_path, "test-work", "non", title="A test", author="Nobody", unit="stanza")
    assert [f.name for f in files] == ["manifest.yaml", "edition.yaml"]
    m = yaml.safe_load(files[0].read_text())
    assert m["work"] == "test-work" and m["language"] == "non" and m["unit"] == "stanza"
    assert m["schemes"][0] == "old-norse"                       # the module's first scheme is the default (rule 8)
    assert m["treebank"] is None and m["edition"]["format"] == "weft-edition"
    assert m["predicted_gaps"] and m["sources_extra"] == []
    e = yaml.safe_load(files[1].read_text())
    assert e["work"] == "test-work" and e["sections"][0]["lines"][0]["tokens"] == [{"t": "TODO"}]
    for d in ("curated", "sense", "notes", "sources"):
        assert (tmp_path / "texts/test-work" / d).is_dir()
    with pytest.raises(SystemExit, match="exists"):
        scaffold.scaffold(tmp_path, "test-work", "non")
    with pytest.raises(SystemExit, match="no language module"):
        scaffold.scaffold(tmp_path, "other-work", "xx")


def test_resolve_wikisource_without_network():
    """A URL that already names a revision is pinned as it is; a non-Wikisource URL passes through."""
    raw, name, rev, title = scaffold.resolve_wikisource("https://fr.wikisource.org/w/index.php?title=Page:X.djvu/26&oldid=9467932")
    assert raw == "https://fr.wikisource.org/w/index.php?oldid=9467932&action=raw" and rev == 9467932 and title == "Page:X.djvu/26"
    raw, name, rev, title = scaffold.resolve_wikisource("https://archive.org/download/x/x_djvu.txt")
    assert raw == "https://archive.org/download/x/x_djvu.txt" and rev is None


def test_pin_records_a_source_in_the_manifest(tmp_path, monkeypatch):
    from weft import paths
    monkeypatch.setattr(paths, "work_dir", lambda repo, work: tmp_path / "texts" / work)
    monkeypatch.setattr(scaffold, "fetch", lambda url, timeout=60: b"Gattir allar\n")
    wd = tmp_path / "texts" / "fake-work"; wd.mkdir(parents=True)
    (wd / "manifest.yaml").write_text("work: fake-work\nedition: {format: weft-edition, file: edition.yaml}\n")
    r = scaffold.pin(tmp_path, "fake-work", "https://non.wikisource.org/w/index.php?title=Havamal&oldid=42", sid="ws-hav")
    assert r["saved"] == "texts/fake-work/sources/ws-hav.txt" and r["revision"] == 42 and r["manifest"] == "sources_extra"
    m = yaml.safe_load((wd / "manifest.yaml").read_text())
    assert m["sources_extra"][0]["url"] == "https://non.wikisource.org/w/index.php?oldid=42&action=raw"
    assert m["sources_extra"][0]["sha256"] == scaffold.sha256(b"Gattir allar\n")
    # pinning the same id again replaces the record rather than duplicating it
    scaffold.pin(tmp_path, "fake-work", "https://non.wikisource.org/w/index.php?title=Havamal&oldid=42", sid="ws-hav")
    assert len(yaml.safe_load((wd / "manifest.yaml").read_text())["sources_extra"]) == 1
    # --edition sets the edition record instead
    r = scaffold.pin(tmp_path, "fake-work", "https://example.org/text.txt", sid="ed", edition=True)
    m = yaml.safe_load((wd / "manifest.yaml").read_text())
    assert r["manifest"] == "edition" and m["edition"]["file"] == "sources/ed.txt" and m["edition"]["sha256"] == r["sha256"]
