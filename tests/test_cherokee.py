"""Cherokee: the syllabary table, the two schemes, the token hooks, and a draft tied to its OCR witness."""
from pathlib import Path

import yaml

from weft import cherokee as c

REPO = Path(__file__).resolve().parents[1]


def test_the_table_is_the_whole_syllabary_from_unicode_names():
    assert len(c.SIGNS) == 86
    assert c.romanize("ᏣᎳᎩ") == "tsalagi"
    assert c.romanize("ꮳꮃꭹ") == "tsalagi"                  # Unicode 8 lowercase reads as the capitals
    assert c.ROMAN["Ꮝ"] == "s" and c.ROMAN["Ꮐ"] == "nah" and c.ROMAN["Ᏽ"] == "mv"
    assert c.from_roman("tsalagi") == list("ᏣᎳᎩ")


def sound(word, scheme):
    fields, _ = c.token_fields(word, {}, {})
    return c.phonemize(fields["norm"], scheme)


def test_the_schemes_follow_worcester_1828_and_oklahoma_today():
    # Worcester 1828: ts as ts (Tsa-tsi, George), g between g and k, nearer g; Guess wrote the name Tsah-lah-keeh
    assert sound("ᏣᎳᎩ", "c1828") == {"ipa": "t͡sa.la.ɡ̊i", "respell": "tsah-lah-gee", "syllables": 3}
    assert sound("ᏣᎳᎩ", "modern") == {"ipa": "d͡ʒa.la.ki", "respell": "jah-lah-gee", "syllables": 3}
    # the d-row "better represented by D. than by T."; the t-row aspirated; v the French un
    assert sound("ᏚᏳᎪᏛ", "c1828")["ipa"] == "d̥u.ju.ɡ̊o.d̥ə̃"
    assert sound("Ꮤ", "c1828")["ipa"] == "tʰa"
    # s alone closes the syllable before it, or begins a word's first syllable
    assert sound("ᎾᏍᎩ", "c1828")["respell"] == "nahs-gee"
    assert sound("ᏍᎩ", "c1828")["respell"] == "sgee"
    # no capitals: the syllabary writes no tone or accent, so none is claimed
    assert not any(ch.isupper() for ch in sound("ᎪᎩᏁᏤᎸᎯ", "c1828")["respell"])


def test_token_hooks():
    f, fails = c.token_fields("ᎪᎩᏁᏤᎸᎯ,", {}, {})
    assert f == {"punct": ",", "surface": "ᎪᎩᏁᏤᎸᎯ", "norm": "goginetselvhi"} and fails == []
    _, fails = c.token_fields("1827", {}, {})
    assert fails == [("not-syllabary", "1827 (1827)")]
    said = {"c1828": {"ipa": "x", "respell": "eighteen twenty-seven"}, "modern": {"ipa": "x", "respell": "eighteen twenty-seven"}}
    f, fails = c.token_fields("1827", {"sound": said}, {})
    assert fails == [] and c.phonemize("1827", "c1828")["respell"] == "eighteen twenty-seven"
    f, fails = c.token_fields("ᎠᏫᏂᏗᏢ", {"uncertain": {"alt": "ᎠᏫᏂᏘᏢ", "why": "Ꮧ and Ꮨ alike at this resolution"}}, {})
    assert f["uncertain"] is True and "ᎠᏫᏂᏘᏢ (awinititlv)" in f["prov"]["text"]
    _, fails = c.token_fields("ᎠᏫᏂᏗᏢ", {"uncertain": {"alt": "ᎠᏫᏂᏘᏢ"}}, {})
    assert fails == [("uncertain-malformed", "ᎠᏫᏂᏗᏢ")]


def work(tmp_path) -> Path:
    wd = tmp_path / "cherokee-test"
    (wd / "gen" / "ocr").mkdir(parents=True)
    (wd / "gen" / "ocr" / "p1.txt").write_text("ᎠᏴ ᎬᏂᏉ ᎠᏫᏂᏘᏢ ᎪᎦᎪᎥ ᎪᎪ-\nᏪᎳ, ᏣᎳᎩ ᎾᏅᎾᏛ ᎪᎩᏁᏤᎸᎯ, !\n", encoding="utf-8")
    (wd / "manifest.yaml").write_text(yaml.safe_dump({
        "work": "cherokee-test", "title": "t", "language": "chr", "kind": "law", "prefix": "cht", "urn": "urn:weft:chr:test",
        "unit": "section", "treebank": None, "schemes": ["c1828", "modern"], "translations": [],
        "edition": {"id": "weft", "name": "test", "format": "weft-edition", "file": "edition.yaml", "license": "CC BY-SA 4.0"},
        "pilot": {"sections": ["preamble"]}}, allow_unicode=True))
    toks = [{"t": "ᎠᏴ"}, {"t": "ᎬᏂᏉ"}, {"t": "ᎠᏫᏂᏗᏢ", "ocr": "ᎠᏫᏂᏘᏢ"}, {"t": "ᎪᎦᎪᎥ"}, {"t": "ᎪᎪᏪᎳ,"},
            {"t": "ᏣᎳᎩ"}, {"t": "ᎾᏅᎾᏛ"}, {"t": "ᎪᎩᏁᏤᎸᎯ,"}]
    (wd / "edition.yaml").write_text(yaml.safe_dump({"work": "cherokee-test", "ocr_check": {"file": "gen/ocr/p1.txt"},
        "sections": [{"id": "preamble", "title": "Preamble", "lines": [{"tokens": toks}]}]}, allow_unicode=True))
    return wd


def test_a_draft_is_tied_to_its_witness(tmp_path, monkeypatch):
    from weft import draft, ocr, paths
    wd = work(tmp_path)
    monkeypatch.setattr(paths, "work_dir", lambda repo, w: tmp_path / w)
    ocr._WITNESS.clear()
    r = draft.run(wd)
    assert r["failures"] == {} and r["counts"]["tokens"] == 8
    g = yaml.safe_load((wd / "gen" / "sections.yaml").read_text())
    t = g["lines"][0]["tokens"][4]
    assert (t["surface"], t["punct"], t["norm"]) == ("ᎪᎪᏪᎳ", ",", "gogowela")
    assert g["layers"]["translit"]["src"].startswith("weft.cherokee")
    # the declared OCR reading removed: the line no longer matches its witness, and the draft says where
    ed = yaml.safe_load((wd / "edition.yaml").read_text())
    del ed["sections"][0]["lines"][0]["tokens"][2]["ocr"]
    (wd / "edition.yaml").write_text(yaml.safe_dump(ed, allow_unicode=True))
    ocr._WITNESS.clear()
    r = draft.run(wd)
    assert r["failures"] == {"edition-not-in-ocr": 1} and "Ꮒ[Ꮧ/Ꮨ]Ꮲ" in r["samples"]["edition-not-in-ocr"][0]


def test_check_requires_stewardship_for_cherokee(tmp_path, monkeypatch):
    from weft import check, draft, ocr, paths
    wd = work(tmp_path)
    monkeypatch.setattr(paths, "work_dir", lambda repo, w: tmp_path / w)
    ocr._WITNESS.clear()
    draft.run(wd)
    assert check.run(REPO, "cherokee-test")["problems"].get("stewardship-missing") == 1


def test_review_fixes():
    # a sound override belongs to its own token only
    said = {"c1828": {"ipa": "x", "respell": "eighteen twenty-seven"}}
    c.token_fields("1827", {"sound": said}, {})
    assert c.phonemize("tsalagi", "c1828")["respell"] == "tsah-lah-gee"
    # nah before a vowel is na + an h-row sign; a doubled lone s stays in the syllabary's own values
    assert c.from_roman("nahi") == list("ᎾᎯ") and c.from_roman("nah") == ["Ꮐ"]
    assert c.word_sound(list("ᏍᏍᎩ"), "c1828")[0] == "ssɡ̊i"
    # a dash or guillemet is punctuation, not a stray letter
    f, fails = c.token_fields("ᏣᎳᎩ—", {}, {})
    assert fails == [] and f["punct"] == "—" and f["norm"] == "tsalagi"
