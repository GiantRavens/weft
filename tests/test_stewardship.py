"""Texts of living communities: the stewardship block and its check; the OCR witness and its collation."""
from pathlib import Path

from weft import check, hebrew, ocr, stewardship

REPO = Path(__file__).resolve().parents[1]

FULL = {
    "work": "w",
    "translations": [{"id": "tr1", "translator": "Elias Boudinot", "year": 1828}],
    "stewardship": {
        "community": "Cherokee Nation",
        "content": "secular",
        "transcription": {"by": "Weft", "relation": "outsider", "method": "hand and OCR, collated on the scan"},
        "translations": {"tr1": {"relation": "community"}},
        "position": {"none_found": "searched the language department site, 2026-10-13"},
    },
}


def classes(m, required=True):
    return [c for c, _ in stewardship.problems(m, required)]


def test_a_complete_block_passes():
    assert classes(FULL) == []


def test_the_block_is_required_only_for_the_strand():
    bare = {"work": "w", "translations": []}
    assert classes(bare, required=True) == ["stewardship-missing"]
    assert classes(bare, required=False) == []


def test_each_rule_fails_on_its_own():
    import copy
    m = copy.deepcopy(FULL); m["stewardship"]["transcription"]["relation"] = "ethnographer"
    assert classes(m) == ["stewardship-relation"]
    m = copy.deepcopy(FULL); m["stewardship"]["translations"] = {}
    assert classes(m) == ["stewardship-translation-unstated"]
    m = copy.deepcopy(FULL); m["stewardship"]["position"] = {"source": "https://example.org"}      # no summary
    assert classes(m) == ["stewardship-position"]
    m = copy.deepcopy(FULL); m["stewardship"]["content"] = "ceremonial"
    assert classes(m) == ["stewardship-ceremonial-no-consent"]
    m["stewardship"]["consent"] = {"source": "https://example.org/letter", "summary": "approved by the council"}
    assert classes(m) == []
    m = copy.deepcopy(FULL); del m["stewardship"]["community"]
    assert classes(m) == ["stewardship-incomplete"]


def test_check_refuses_a_strand_work_without_the_block(monkeypatch):
    # any language module marked INDIGENOUS makes the block required; Hebrew stands in for the test
    monkeypatch.setattr(hebrew, "INDIGENOUS", True, raising=False)
    r = check.run(REPO, "kaddish")
    assert r["problems"].get("stewardship-missing") == 1 and not r["ok"]


def test_the_page_names_each_translator_with_their_relation():
    page = stewardship.for_page(FULL, FULL["translations"])
    assert page["translations"] == [{"who": "Elias Boudinot (1828)", "relation": "community"}]
    assert page["position"]["none_found"].startswith("searched")
    assert stewardship.for_page({"work": "w"}, []) is None


def test_ocr_compares_letters_and_finds_the_best_stretch():
    assert ocr.letters("ᎪᎪ-\nᏪᎳ, ᏣᎳᎩ!", "chr") == "ᎪᎪᏪᎳᏣᎳᎩ"
    witness = ocr.letters("noise ᎠᏴ ᎬᏂᏉ ᎠᏫᏂᏘᏢ ᎪᎦᎪᎥ more", "chr")
    cost, a, b = ocr.best_window("ᎬᏂᏉᎠᏫᏂᏗᏢ", witness)
    assert cost == 1 and witness[a:b] == "ᎬᏂᏉᎠᏫᏂᏘᏢ"
    assert ocr.sign_diff("ᎠᏫᏂᏗᏢ", "ᎠᏫᏂᏘᏢ") == ["Ꮒ[Ꮧ/Ꮨ]Ꮲ"]


def test_the_witness_check_needs_every_difference_declared(tmp_path, monkeypatch):
    from weft import paths
    wd = tmp_path / "w"
    (wd / "gen" / "ocr").mkdir(parents=True)
    (wd / "gen" / "ocr" / "p1.txt").write_text("ᎠᏴ ᎬᏂᏉ ᎠᏫᏂᏘᏢ ᎪᎦᎪᎥ ᎪᎪ-\nᏪᎳ, ᏣᎳᎩ\n", encoding="utf-8")
    monkeypatch.setattr(paths, "work_dir", lambda repo, work: tmp_path / work)
    ocr._WITNESS.clear()
    ed = {"work": "w", "ocr_check": {"file": "gen/ocr/p1.txt"}}
    toks = [{"t": "ᎠᏴ"}, {"t": "ᎬᏂᏉ"}, {"t": "ᎠᏫᏂᏗᏢ"}, {"t": "ᎪᎦᎪᎥ"}, {"t": "ᎪᎪᏪᎳ,"}, {"t": "ᏣᎳᎩ"}]
    fails = ocr.witness_check(toks, ed, "chr")
    assert fails == [("edition-not-in-ocr", "Ꮒ[Ꮧ/Ꮨ]Ꮲ")]
    toks[2]["ocr"] = "ᎠᏫᏂᏘᏢ"                       # the OCR's reading, declared after settling on the scan
    assert ocr.witness_check(toks, ed, "chr") == []
    toks[0]["ocr"] = "ᎠᏴ"                            # a declaration that changes nothing
    assert ocr.witness_check(toks, ed, "chr") == [("ocr-reading-unneeded", "ᎠᏴ")]


def test_a_word_the_ocr_dropped_is_declared_empty(tmp_path, monkeypatch):
    from weft import paths
    (tmp_path / "w" / "gen" / "ocr").mkdir(parents=True)
    (tmp_path / "w" / "gen" / "ocr" / "p1.txt").write_text("ᏣᎳᎩ ᎪᎩᏁᏤᎸᎯ", encoding="utf-8")
    monkeypatch.setattr(paths, "work_dir", lambda repo, work: tmp_path / work)
    ocr._WITNESS.clear()
    ed = {"work": "w", "ocr_check": {"file": "gen/ocr/p1.txt"}}
    toks = [{"t": "ᏣᎳᎩ"}, {"t": "ᎾᏅᎾᏛ", "ocr": ""}, {"t": "ᎪᎩᏁᏤᎸᎯ"}]
    assert ocr.witness_check(toks, ed, "chr") == []


def test_agreement_is_measured_where_the_signs_stand(tmp_path, monkeypatch):
    # hand and OCR both misread the first ᎤᏁᎳᏅᎯ the same way; the word also occurs, correctly, later on:
    # the shared error is counted, not excused by the later occurrence
    wd = tmp_path / "w"
    (wd / "sources").mkdir(parents=True)
    (wd / "curated").mkdir()
    (wd / "curated" / "hand.txt").write_text("ᎤᏁᎳᏅᏗ ᎠᎴ ᎤᏁᎳᏅᎯ", encoding="utf-8")
    import yaml
    (wd / "manifest.yaml").write_text(yaml.dump({"work": "w", "edition": {"file": "edition.yaml"}, "sources_extra": [{"id": "s", "file": "sources/x.png"}],
        "ocr": {"model": {"lang": "chr", "sha256": "x"}, "hand": "curated/hand.txt",
                "pages": [{"id": "p", "source": "s", "sections": ["a"]}]}}, allow_unicode=True))
    (wd / "edition.yaml").write_text(yaml.dump({"sections": [{"id": "a", "lines": ["ᎤᏁᎳᏅᎯ ᎠᎴ ᎤᏁᎳᏅᎯ"]}]}, allow_unicode=True))
    monkeypatch.setattr(ocr, "model_path", lambda m: tmp_path)
    monkeypatch.setattr(ocr, "tesseract_version", lambda: "tesseract test")
    monkeypatch.setattr(ocr, "read_page", lambda *a: "ᎤᏁᎳᏅᏗ ᎠᎴ ᎤᏁᎳᏅᎯ")
    r = ocr.run(wd)
    assert r["agreed"] == "12 signs read alike by both; 1 of them wrong in the settled text"
    assert r["pages"][0]["collation"][0]["signs"] == ["Ꮕ[Ꭿ/Ꮧ]Ꭰ"]


def test_a_reference_translation_is_named_by_its_translator():
    m = {"stewardship": dict(FULL["stewardship"], translations={"tr1": {"relation": "outsider"}})}
    refs = [{"id": "tr1", "translator": "J. Doe", "year": 1999, "kind": "reference"}]
    assert stewardship.for_page(m, refs)["translations"] == [{"who": "J. Doe (1999)", "relation": "outsider"}]
