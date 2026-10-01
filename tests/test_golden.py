"""Golden passage guards. Run: uv run --with pytest pytest -q"""
from pathlib import Path

import yaml

from weft import check, draft, greek, latin, norse

REPO = Path(__file__).resolve().parents[1]


def sources_present(work: Path) -> bool:
    """True when every source the manifest pins is on disk. Sources are fetched by `weft acquire`
    and never committed, so on a fresh clone (and in CI) the draft-reproduction checks skip and
    the phonology and selftest checks still run."""
    m = yaml.safe_load((work / "manifest.yaml").read_text())
    specs = [m["edition"], m.get("treebank") or {}] + m.get("translations", []) + m.get("sources_extra", [])
    return all((work / s["file"]).exists() for s in specs if s.get("file"))
WORK = REPO / "texts" / "homer-odyssey"
Q = yaml.safe_load((REPO / "pipeline/weft/data/grc_quantities.yaml").read_text())

# Hand-verified expectations: the cases each rule exists for.
EXPECT = {
    # word: (restored respell, erasmian respell)
    "ἄνδρα": ("AN-dra", "AN-dra"),                 # stop+liquid onset
    "ἔννεπε": ("EN-ne-pe", "EN-ne-pe"),            # geminate split
    "μοῦσα": ("MOO-sa", "MOO-sa"),                 # circumflex on ου
    "πολλὰ": ("pol-la", "pol-LA"),                 # grave: no pitch rise, but Erasmian stress
    "πλάγχθη": ("PLANGKʰ-tʰê", "PLANGKH-thay"),   # γ before velar = ng; aspirates
    "ψυχὴν": ("psüü-kʰên", "psüü-KHAYN"),          # quantity table long upsilon
    "πόντῳ": ("PON-tawi", "PON-toh"),              # iota subscript: sounded vs silent
    "ἱέμενός": ("hee-E-me-NOS", "hee-E-me-NOS"),   # rough breathing, enclitic double accent
    "ἀφείλετο": ("a-PʰAY-le-to", "a-FAY-le-to"),   # spurious diphthong ει; φ
    "Ἠελίοιο": ("ê-e-LI-oy-o", "ay-e-LI-oy-o"),    # hiatus vs diphthong
    "δʼ": ("d’", "d’"),                            # elided particle
}


def test_expectations():
    for w, (r, e) in EXPECT.items():
        assert greek.phonemize(w, "restored", Q)["respell"] == r, w
        assert greek.phonemize(w, "erasmian", Q)["respell"] == e, w


def test_draft_is_deterministic_and_matches_committed_gen():
    if sources_present(WORK):   # draft needs the licensed sources; CI has none
        before = (WORK / "gen/book01.yaml").read_text()
        report = draft.run(WORK)
        after = (WORK / "gen/book01.yaml").read_text()
        assert before == after, "draft output changed: review the diff, then commit the new gen"
        assert report["counts"] == {"lines": 10, "tokens": 74}
        assert report["shift_left"] == []


def test_check_passes():
    r = check.run(REPO, "homer-odyssey")
    assert r["ok"], r["problems"]


LQ = yaml.safe_load((REPO / "pipeline/weft/data/lat_quantities.yaml").read_text())
LATIN = {
    # word: (classical, ecclesiastical)
    "dicere": ("DEE-ke-re", "DEE-che-re"),          # light penult: stress the antepenult; soft c
    "mutastis": ("moo-TAAS-tis", "moo-TAS-tees"),   # closed penult is heavy
    "primaque": ("pree-MAA-kwe", "pree-MA-kwe"),     # enclitic pulls stress to the host's last syllable
    "caelum": ("KAI-lum", "CHE-loom"),               # ae: ai vs e
    "vos": ("wohs", "vos"),                          # v = w; monosyllable unstressed caps
    "iunctarum": ("yoongk-TAA-rum", "yoongk-TA-room"),  # consonantal i; n before c = ng
    "dixere": ("deek-SAY-re", "deek-SE-re"),         # x makes position
    "chaos": ("KʰA-os", "KA-os"),                    # Greek aspirate
}


def test_latin_expectations():
    for w, (c, e) in LATIN.items():
        assert latin.phonemize(w, "classical", LQ)["respell"] == c, w
        assert latin.phonemize(w, "ecclesiastical", LQ)["respell"] == e, w
    assert latin.phonemize("agnus", "ecclesiastical", {})["respell"] == "A-nyoos"


def test_ovid_draft_and_check():
    work = REPO / "texts" / "ovid-metamorphoses"
    if sources_present(work):   # draft needs the licensed sources; CI has none
        before = (work / "gen/book01.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/book01.yaml").read_text() == before
        assert report["counts"] == {"lines": 9, "tokens": 62}
        assert report["failures"] == {}
    r = check.run(REPO, "ovid-metamorphoses")
    assert r["ok"], r["problems"]


NORSE = {
    # word: (old-norse, modern-icelandic)
    "Gáttir": ("GAAT-tir", "GOWT-tir"),        # acute = long; á diphthongized today
    "allar": ("AL-lar", "AT-lar"),              # modern ll = tl
    "frændr": ("frêndr", "FRAIN-dür"),          # modern epenthetic u before final r
    "orðstírr": ("ORDHS-teerr", "ORDHS-teerr"), # no epenthesis after rr
    "hvar": ("khwar", "kvar"),                  # hv
    "því": ("thwee", "thvee"),                  # þ, v = w in Old Norse
    "einn": ("einn", "aytn"),                   # modern nn after long vowel = tn
    "aldregi": ("ALD-re-ghi", "ALD-re-ghi"),    # g after a vowel is a fricative
}


def test_norse_expectations():
    for w, (o, m) in NORSE.items():
        assert norse.phonemize(w, "old-norse")["respell"] == o, w
        assert norse.phonemize(w, "modern-icelandic")["respell"] == m, w


def test_havamal_draft_and_check():
    work = REPO / "texts" / "edda-havamal"
    if sources_present(work):   # draft needs the licensed sources; CI has none
        before = (work / "gen/stanzas.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/stanzas.yaml").read_text() == before
        assert report["counts"] == {"lines": 19, "tokens": 58}
    r = check.run(REPO, "edda-havamal")
    assert r["ok"], r["problems"]


def test_heyne_and_old_english():
    from weft import oldenglish as oe
    assert oe.heyne_to_macron("Hwät") == "Hwæt"            # ä is short æ
    assert oe.heyne_to_macron("æghwylc") == "ǣghwylc"      # plain æ is long ǣ
    assert oe.heyne_to_macron("geâr-dagum") == "gēar-dagum"  # accent on the diphthong's second vowel
    assert oe.heyne_to_macron("þreátum") == "þrēatum"
    P = {"oftēah": "of"}
    cases = {
        "Gār-Dena": "GAAHR-de-nah",        # compound: first element stressed
        "gēar-dagum": "YǢAR-dah-ghum",     # g before a front vowel = y; g between back vowels = gh
        "meodo-setla": "MEO-do-se-tlah",   # s after a compound boundary stays voiceless
        "gefrūnon": "ye-FROO-non",         # ge- is never stressed
        "oftēah": "of-TǢAKH",              # verb prefix from the stress table
        "Scyld": "shüld",                  # sc = sh; y = ü
        "frōfre": "FROH-vre",              # f between voiced sounds = v
        "cyning": "KÜ-ning",               # c before y stays k; final ng sounds its g
    }
    for w, want in cases.items():
        assert oe.phonemize(w, "west-saxon", {}, prefixes=P)["respell"] == want, w


def test_beowulf_draft_and_check():
    work = REPO / "texts" / "beowulf"
    if sources_present(work):   # draft needs the licensed sources; CI has none
        before = (work / "gen/lines.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/lines.yaml").read_text() == before
        assert report["counts"] == {"lines": 11, "tokens": 54}
    r = check.run(REPO, "beowulf")
    assert r["ok"], r["problems"]


def test_grettir_draft_and_check():
    work = REPO / "texts" / "saga-grettir"
    if sources_present(work):   # draft needs the licensed sources; CI has none
        before = (work / "gen/chapter14.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/chapter14.yaml").read_text() == before
        assert report["counts"] == {"lines": 9, "tokens": 80}
        assert report["failures"] == {}
    r = check.run(REPO, "saga-grettir")
    assert r["ok"], r["problems"]


def test_koine_and_john():
    k = {"λόγος": "LO-ghos", "ἐγένετο": "e-YE-ne-to", "αὐτοῦ": "av-TOO", "καὶ": "KE",
         "κατέλαβεν": "ka-TE-la-ven", "φαίνει": "FE-nee", "οὗτος": "OO-tos"}
    for w, want in k.items():
        assert greek.phonemize(w, "koine")["respell"] == want, w
    work = REPO / "texts" / "nt-john"
    if sources_present(work):   # draft needs the licensed sources; CI has none
        before = (work / "gen/chapter01.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/chapter01.yaml").read_text() == before
        assert report["counts"] == {"lines": 5, "tokens": 61}
    r = check.run(REPO, "nt-john")
    assert r["ok"], r["problems"]


def test_hebrew_and_genesis():
    from weft import hebrew as he
    cases = [  # (word, silluq, tiberian, modern-israeli)
        ("בְּרֵאשִׁ֖ית", False, "ba-ray-SHEETH", "be-re-SHEET"),    # vocal shewa; soft ת; hard בּ
        ("בָּרָ֣א", False, "baw-RAW", "ba-RA"),                       # qamets = ɔ; quiescent aleph
        ("וְר֣וּחַ", False, "va-ROO-aḥ", "ve-ROO-akh"),                # shureq; furtive patah
        ("א֑וֹר", False, "ʾohr", "or"),                               # holam waw after aleph
        ("הָאָֽרֶץ", True, "haw-ʾAW-reṣ", "ha-A-rets"),               # silluq marks the stress
        ("הַשָּׁמַ֖יִם", False, "hash-shaw-MA-yim", "ha-sha-MA-yeem"),  # gemination: Tiberian only
        ("וַֽיְהִי", False, "vay-hee", "vay-hee"),                      # before maqaf: unstressed
    ]
    for w, sil, t, m in cases:
        assert he.phonemize(w, "tiberian", silluq=sil)["respell"] == t, w
        assert he.phonemize(w, "modern-israeli", silluq=sil)["respell"] == m, w
    work = REPO / "texts" / "tanakh-genesis"
    if sources_present(work):   # draft needs the licensed sources; CI has none
        before = (work / "gen/chapter01.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/chapter01.yaml").read_text() == before
        assert report["counts"] == {"lines": 5, "tokens": 52}
    r = check.run(REPO, "tanakh-genesis")
    assert r["ok"], r["problems"]


def test_chinese_and_libai():
    from weft import chinese as zh
    assert zh.tang_tone("ngiuæt") == "entering"
    assert zh.tang_tone("giǔ") == "rising"
    assert zh.tang_tone("dhì") == "departing"
    assert zh.tang_tone("guɑng") == "level"
    assert zh.tang_final("shriɑng") == "ɑng"
    work = REPO / "texts" / "libai-jingyesi"
    if sources_present(work):   # draft needs the licensed sources; CI has none
        before = (work / "gen/lines.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/lines.yaml").read_text() == before
        assert report["counts"] == {"lines": 4, "tokens": 20}
        assert report["failures"] == {"reading-from-variant": 1}      # 鄉 borrows from 鄕, by design
        g = yaml.safe_load(before)
        assert [l["metre"] for l in g["lines"]] == [
            "○○○●○ · rhyme -ɑng", "○●●●○ · rhyme -ɑng", "●○○○● · rhyme -uæt", "○○○●○ · rhyme -ɑng"]
    r = check.run(REPO, "libai-jingyesi")
    assert r["ok"], r["problems"]


def test_runes():
    from weft import runic
    assert runic.to_runes("hlewagastiz", "elder") == ("ᚺᛚᛖᚹᚨᚷᚨᛊᛏᛁᛉ", [])
    assert runic.to_runes("stonta", "younger-short-twig") == ("ᛌᛐᚬᚿᛐᛆ", [])     # ᚬ spells nasal a
    assert runic.to_runes("fuþarkgwhnijpïzstbemlŋdo", "elder")[0] == "ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛈᛇᛉᛊᛏᛒᛖᛗᛚᛜᛞᛟ"
    cases = {("Hlewagastiz", "pn"): "HLE-wa-ghas-tiz",   # g between vowels is a fricative; z stays z
             ("tawidō", "pn"): "TA-wi-dhoh",             # d between vowels = dh; macron = long
             ("standa", "oen"): "STAN-da",               # sound from the normalized form, not the runes
             ("faigian", "oen"): "FAI-ghi-an"}
    for (w, d), want in cases.items():
        assert runic.phonemize(w, dialect=d)["respell"] == want, w
    work = REPO / "texts" / "runes"
    if sources_present(work):
        before = (work / "gen/inscriptions.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/inscriptions.yaml").read_text() == before
        assert report["counts"] == {"lines": 4, "tokens": 41}
        assert report["failures"] == {}
    r = check.run(REPO, "runes")
    assert r["ok"], r["problems"]


def test_anglo_latin_and_magna_carta():
    q = LQ
    cases = {"judicium": ("joo-DEE-tsee-oom", "yoo-DI-ki-um"),   # j = dʒ; ci before a vowel = tsi
             "legem": ("LE-jem", "LAY-gem"),                      # soft g before e
             "homo": ("O-mo", "HO-mo"),                           # h silent
             "imprisonetur": ("eem-pree-zo-NE-toor", "im-pri-so-NAY-tur"),  # s between vowels = z
             "utlagetur": ("oot-la-JE-toor", "ut-la-GAY-tur")}    # tl is not a Latin onset
    for w, (a, c) in cases.items():
        assert latin.phonemize(w, "anglo-latin", q)["respell"] == a, w
        assert latin.phonemize(w, "classical", q)["respell"] == c, w
    work = REPO / "texts" / "magna-carta"
    if sources_present(work):
        before = (work / "gen/sections.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/sections.yaml").read_text() == before
        assert report["counts"] == {"lines": 4, "tokens": 43}
        assert report["failures"] == {}             # includes: every line found verbatim in McKechnie
    r = check.run(REPO, "magna-carta")
    assert r["ok"], r["problems"]


def test_national_latin_and_science():
    q = LQ
    eng = {"statu": "STAY-tyoo", "mutare": "myoo-TAY-ree", "omne": "OM-nee", "nisi": "NYE-sye",
           "Mutationem": "myoo-ta-shi-OH-nem", "actiones": "ak-shi-OH-neez", "viribus": "VI-ri-bus",
           "contrarias": "kon-TRAY-ri-as"}
    fr = {"Ego": "e-GO", "cogito": "ko-zhee-TO", "sum": "som", "tempore": "tan-po-RE", "omnium": "om-nee-OM"}
    for w, want in eng.items():
        assert latin.phonemize(w, "as-first-read", q, dialect="english")["respell"] == want, w
    for w, want in fr.items():
        assert latin.phonemize(w, "as-first-read", q, dialect="french")["respell"] == want, w
    work = REPO / "texts" / "science-latin"
    if sources_present(work):
        before = (work / "gen/sections.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/sections.yaml").read_text() == before
        assert report["counts"] == {"lines": 10, "tokens": 91}
        assert report["failures"] == {}             # every line verbatim in its own source
    r = check.run(REPO, "science-latin")
    assert r["ok"], r["problems"]


def test_japanese_and_basho():
    from weft import japanese as jp
    assert jp.phonemize("かはづ", "edo-1686")["respell"] == "ka-wa-dzu"   # medial は = wa; づ = dzu
    assert jp.phonemize("かはづ", "modern")["respell"] == "ka-wa-zu"
    assert jp.phonemize("ふるいけ", "modern")["syllables"] == 4           # morae, not syllables
    work = REPO / "texts" / "basho-furuike"
    if sources_present(work):
        before = (work / "gen/sections.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/sections.yaml").read_text() == before
        assert report["counts"] == {"lines": 3, "tokens": 7}
        assert report["failures"] == {}
    g = yaml.safe_load((work / "gen/sections.yaml").read_text())
    assert [l["metre"] for l in g["lines"]] == ["5 morae", "7 morae", "5 morae"]
    r = check.run(REPO, "basho-furuike")
    assert r["ok"], r["problems"]


def test_sanskrit_accent_strokes_decode():
    """Rigveda 1.1.1ab: the Devanagari accent strokes decode to the raised syllables written as
    acutes in the transliteration, and the gāyatrī pādas scan 8 + 8."""
    from weft import sanskrit as S
    deva = "अ॒ग्निमी॑ळे पु॒रोहि॑तं य॒ज्ञस्य॑ दे॒वमृ॒त्विज॑म् ।"
    words = ["agním", "īḷe", "puróhitaṃ", "yajñásya", "devám", "ṛtvíjam"]
    iast, marks = S.devanagari(deva)
    assert iast == S.strip_accents("".join(words))
    decoded = S.decode_marks(marks)
    written = S.accents_from_words(words)
    assert [d == "U" for d in decoded] == [w == "U" for w in written]
    assert S.metre(words, [3]) == ("—◡——◡—◡—|——◡—◡—◡×", [8, 8])
    assert S.phonemize("agním")["respell"] == "uhg-NIM"
    assert S.strip_accents("yaśásaṃ") == "yaśasaṃ"      # ś survives accent stripping


def test_voluspa_complete_and_annotated():
    """The whole Völuspá: 66 stanzas, every token hand-annotated (no treebank), every line scanned."""
    r = check.run(REPO, "edda-voluspa")
    assert r["ok"], r["problems"]
    g = yaml.safe_load((REPO / "texts/edda-voluspa/gen/stanzas.yaml").read_text())
    assert len({l["id"].split(".")[1] for l in g["lines"]}) == 66


def test_new_languages_check():
    """Akkadian, Classical Chinese prose, Old Tamil and Classical Persian works pass their checks."""
    for work in ("akkadian-hammurabi", "daodejing", "sunzi-art-of-war", "tamil-tirukkural", "persian-rubaiyat"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])


def test_reference_translation_is_cited_not_inlined(tmp_path):
    """A kind: reference translation (still in copyright) appears as a citation, never as text."""
    import shutil
    from weft import build
    work = tmp_path / "texts" / "basho-furuike"
    shutil.copytree(REPO / "texts" / "basho-furuike", work, ignore=shutil.ignore_patterns("sources"))
    m = yaml.safe_load((work / "manifest.yaml").read_text())
    m["translations"].append({"id": "later2000", "kind": "reference", "translator": "A. Translator",
                              "year": 2000, "title": "Haiku", "publisher": "A Press"})
    (work / "manifest.yaml").write_text(yaml.dump(m, allow_unicode=True))
    data = build.assemble(work)
    assert [r["id"] for r in data["references"]] == ["later2000"]
    assert "later2000" not in [t["id"] for t in data["translations"]]
    assert all(s["tr"] != "later2000" for s in data["sense"])


def test_renaissance_works_check():
    """Italian, Renaissance Latin and Middle French works pass their checks."""
    for work in ("petrarch-canzoniere-1", "pico-oration", "erasmus-praise-of-folly", "machiavelli-prince",
                 "more-utopia", "montaigne-essais"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])
