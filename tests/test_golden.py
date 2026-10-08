"""Golden passage guards. Run: uv run --with pytest pytest -q"""
from pathlib import Path

import shutil

import pytest
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
        assert report["counts"] == {"lines": 1086, "tokens": 4046}   # all 164 stanzas (2026-10-04)
    r = check.run(REPO, "edda-havamal")
    assert r["ok"], r["problems"]


def test_vafthrudnismal_draft_and_check():
    """The first work built end to end with weft scaffold, pin (heimskringla, converted to stanza-text), overlay and image."""
    work = REPO / "texts" / "edda-vafthrudnismal"
    if sources_present(work):
        before = (work / "gen/stanzas.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/stanzas.yaml").read_text() == before
        assert report["counts"] == {"lines": 335, "tokens": 1235}   # all 55 stanzas (2026-10-08)
    gen = yaml.safe_load((work / "gen/stanzas.yaml").read_text())
    titles = {l["stanza"]: l.get("stanza_title") for l in gen["lines"]}
    assert titles[1] == "Stanza 1 · Óðinn kvað" and titles[2] == "Stanza 2 · Frigg kvað" and titles[5] is None   # 5 is narrative
    r = check.run(REPO, "edda-vafthrudnismal")
    assert r["ok"], r["problems"]


def test_grimnismal_draft_and_check():
    work = REPO / "texts" / "edda-grimnismal"
    if sources_present(work):
        before = (work / "gen/stanzas.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/stanzas.yaml").read_text() == before
        assert report["counts"] == {"lines": 361, "tokens": 1216}   # all 54 stanzas (2026-10-08)
    gen = yaml.safe_load((work / "gen/stanzas.yaml").read_text())
    assert all(l.get("stanza_title") is None for l in gen["lines"])   # a monologue: the prose names the speaker, the stanzas do not
    r = check.run(REPO, "edda-grimnismal")
    assert r["ok"], r["problems"]


def test_lokasenna_draft_and_check():
    work = REPO / "texts" / "edda-lokasenna"
    if sources_present(work):
        before = (work / "gen/stanzas.yaml").read_text()
        report = draft.run(work)
        assert (work / "gen/stanzas.yaml").read_text() == before
        assert report["counts"] == {"lines": 390, "tokens": 1461}   # all 65 stanzas (2026-10-08)
    gen = yaml.safe_load((work / "gen/stanzas.yaml").read_text())
    titles = {l["stanza"]: l.get("stanza_title") for l in gen["lines"]}
    assert titles[1] is None and titles[2] == "Stanza 2 · Eldir kvað" and titles[57] == "Stanza 57 · Þá kom Þórr at ok kvað"
    assert sum(1 for t in titles.values() if t) == 59
    r = check.run(REPO, "edda-lokasenna")
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
        assert report["counts"] == {"lines": 18, "tokens": 252}   # John 1:1-18, the prologue
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
        assert report["counts"] == {"lines": 34, "tokens": 469}   # Genesis 1:1-2:3, the creation account
    g1 = yaml.safe_load((work / "gen/chapter01.yaml").read_text())
    lahem = next(t for l in g1["lines"] for t in l["tokens"] if t["id"] == "gen.1.28.5")
    assert lahem["lemma"] == "לְ"            # a preposition with a pronoun suffix is its own word
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
        assert report["counts"] == {"lines": 27, "tokens": 68}   # nine haiku, 1680-1694
        assert report["failures"] == {}
    g = yaml.safe_load((work / "gen/sections.yaml").read_text())
    assert [l["metre"] for l in g["lines"] if l["id"].startswith("ba.1686.")] == ["5 morae", "7 morae", "5 morae"]
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
    assert "later2000" in [r["id"] for r in data["references"]]
    assert "later2000" not in [t["id"] for t in data["translations"]]
    assert all(s["tr"] != "later2000" for s in data["sense"])


def test_renaissance_works_check():
    """Italian, Renaissance Latin and Middle French works pass their checks."""
    for work in ("dante-inferno-1", "petrarch-canzoniere-1", "pico-oration", "luther-95-theses", "erasmus-praise-of-folly", "machiavelli-prince",
                 "more-utopia", "montaigne-essais"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])


def test_hexameter_scanner_matches_hand_scansion():
    """The generated metre row equals every hand scansion in curated/ (Odyssey 1.1-10, Iliad 1.1-52):
    the hand work is the scanner's regression test."""
    for work in ("homer-odyssey", "homer-iliad"):
        wd = REPO / "texts" / work
        gen = yaml.safe_load((wd / "gen" / "book01.yaml").read_text())
        made = {l["id"]: l.get("metre") for l in gen["lines"]}
        hand = {}
        for f in sorted((wd / "curated").glob("*.yaml")):
            for cs in yaml.safe_load(f.read_text()) or []:
                for k, v in (cs.get("set") or {}).items():
                    if isinstance(v, dict) and "metre" in v:
                        hand[k] = v["metre"]
        assert hand, work
        wrong = {k: (made.get(k), v) for k, v in hand.items() if made.get(k) != v}
        assert not wrong, (work, wrong)


def test_glaux_works_keep_treebank_lemmas():
    """A GLAUx work whose reconciliation breaks loses lemmas silently (Marcus once lost 91%):
    nearly every generated token must carry a treebank lemma."""
    for work in ("marcus-meditations", "epictetus-enchiridion", "aristotle-metaphysics"):
        g = yaml.safe_load((REPO / "texts" / work / "gen" / "sections.yaml").read_text())
        toks = [t for l in g["lines"] for t in l["tokens"]]
        with_lemma = sum(1 for t in toks if t.get("lemma"))
        assert with_lemma / len(toks) > 0.98, (work, with_lemma, len(toks))


def test_voyages_check():
    """The voyages strand: Spanish, Franco-Italian and early modern Dutch works pass their checks."""
    for work in ("polo-cipangu", "columbus-letter-1493", "linschoten-japan"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])


def test_german_works_check():
    """Kant and Nietzsche (German, first editions) pass their checks."""
    for work in ("kant", "nietzsche", "luther-bible"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])


def test_oldest_texts_check():
    """The oldest works: Old Egyptian (Pyramid Texts) and Sumerian (Temple Hymns) pass their checks."""
    for work in ("pyramid-texts-unas", "enheduanna-temple-hymns"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])


def test_norse_norman_and_papal_works_check():
    """The 2026-10-01 batch: Þrymskviða, the Bayeux Tapestry captions, Inter caetera, Gylfaginning, the Res Gestae."""
    for work in ("edda-thrymskvida", "bayeux-tapestry", "inter-caetera-1493", "res-gestae-augusti", "snorri-gylfaginning", "edda-fafnismal", "yijing"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])


def test_docs_render_clean(tmp_path):
    """The reader pages (docs/about.md, docs/languages.md) render with no stray Markdown and only working internal links."""
    import re
    from weft import docs
    docs.build_docs(REPO, tmp_path, {})
    pages = {p.name: p.read_text() for p in tmp_path.glob("*.html")}
    assert "about.html" in pages
    for name, html in pages.items():
        body = html.split("<main>", 1)[1]
        text = re.sub(r"<pre>.*?</pre>|<code>.*?</code>", "", body, flags=re.S)
        assert "**" not in text and "](" not in text and "\n#" not in text, name
        for anchor in re.findall(r'href="#([^"]+)"', body):
            assert f'id="{anchor}"' in body, (name, anchor)
        for target in re.findall(r'href="([a-z-]+)\.html', body):
            assert target == "index" or f"{target}.html" in pages, (name, target)



def _link_site(tmp_path):
    """site/ for a fixture repo: the template, script and stylesheet linked, but its own empty build/,
    so a fixture build never writes into the real site/build (it once overwrote the library index
    with a fixture's title)."""
    (tmp_path / "site").mkdir()
    for f in ("template.html", "weft.css", "weft.js"):
        (tmp_path / "site" / f).symlink_to(REPO / "site" / f)
    (tmp_path / "site" / "build").mkdir()

def _private_fixture(tmp_path):
    """A repo whose private/ holds one private work (a copy of the Bashō work under a new name)."""
    for d in ("texts", "art", "docs", "pipeline"):
        (tmp_path / d).symlink_to(REPO / d)
    _link_site(tmp_path)
    pw = tmp_path / "private" / "basho-private"
    shutil.copytree(REPO / "texts" / "basho-furuike", pw, ignore=shutil.ignore_patterns("sources"))
    m = yaml.safe_load((pw / "manifest.yaml").read_text())
    m.update(work="basho-private", title="A private test work")
    (pw / "manifest.yaml").write_text(yaml.dump(m, allow_unicode=True, sort_keys=False))
    return tmp_path


def test_private_work_builds_privately_only(tmp_path):
    """A private work builds into private/build/ with the public library around it; the public
    build refuses it, and the public library never lists it."""
    from weft import build, paths
    repo = _private_fixture(tmp_path)
    assert paths.private_works(repo) == ["basho-private"]
    assert "basho-private" not in [m["work"] for m in build.library_order(repo)]
    with pytest.raises(SystemExit):
        build.run(repo, "basho-private", private=False)
    out = build.run(repo, "basho-private", private=True)
    assert out == repo / "private" / "build" / "basho-private.html"
    page = out.read_text()
    assert '"private_work": true' in page and "issues/new" not in page.split("window.WEFT", 1)[1].split("</script>", 1)[0]
    idx = (repo / "private" / "build" / "index.html").read_text()
    assert "A private test work" in idx and "Private build" in idx


def test_private_never_tracked():
    """Leak sensor: nothing under private/ (except its README) and no fetched source is in git,
    and the public site output holds no page for a private work."""
    import subprocess
    from weft import paths
    r = subprocess.run(["git", "ls-files", "private", "texts"], cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr          # no git, no sensor: fail loudly rather than pass on nothing
    tracked = r.stdout.split()
    assert "texts/homer-odyssey/manifest.yaml" in tracked, "git ls-files returned nothing: the sensor is blind"
    leaks = [f for f in tracked if (f.startswith("private/") and f != "private/README.md")
             or ("/sources/" in f and not f.endswith("/sources/README.md"))]
    assert leaks == [], leaks
    built = REPO / "site" / "build"
    for w in paths.private_works(REPO):
        assert not (built / f"{w}.html").exists(), w


def test_japanese_kanbun_and_heike_check():
    """The Japanese works: kanbun read in Japanese (1615, 1703) and the Heike opening pass their checks,
    and every kanbun line carries a whole-line reading."""
    for work in ("buke-shohatto-1615", "ronin-statement-1703", "heike-gion-shoja"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])
    g = yaml.safe_load((REPO / "texts" / "buke-shohatto-1615" / "gen" / "sections.yaml").read_text())
    assert all(l.get("reading") for l in g["lines"])


def test_mongol_rus_coptic_swahili_and_charters_check():
    """Middle Mongolian, Old East Slavic, Sahidic Coptic, Swahili, and the Berlin Act's 1885 French pass their checks."""
    for work in ("secret-history-mongols", "primary-chronicle-varangians", "coptic-mark", "swahili-tales-steere", "berlin-act-1885", "saer-de-quincy-charters"):
        r = check.run(REPO, work)
        assert r["ok"], (work, r["problems"])


def test_no_shadowed_tests():
    """Sensor: two test functions with the same name silently replace each other, so one never runs."""
    import collections, re
    names = re.findall(r"^def (test_\w+)", Path(__file__).read_text(), re.M)
    assert [n for n, k in collections.Counter(names).items() if k > 1] == []


def test_every_built_work_passes_check():
    """Every work with generated layers passes `weft check`, whether or not a test above names it.
    `weft build` does not run check, so this is the gate between a broken layer and a deployed page."""
    works = sorted(p.parent.parent.name for p in (REPO / "texts").glob("*/gen/*.yaml") if not p.name.endswith(".run.yaml"))
    assert len(works) >= 57
    bad = {w: check.run(REPO, w)["problems"] for w in works}
    assert {w: p for w, p in bad.items() if p} == {}


def test_render_confines_data_to_data(tmp_path):
    """Committed YAML cannot write markup into the page or read files from outside the repository:
    the title is escaped, every < in the payload is \\u003c, and a figure path that climbs out is refused."""
    from weft import build
    repo = tmp_path
    for d in ("art", "docs", "pipeline"):
        (repo / d).symlink_to(REPO / d)
    _link_site(repo)
    work = repo / "texts" / "basho-furuike"
    shutil.copytree(REPO / "texts" / "basho-furuike", work, ignore=shutil.ignore_patterns("sources"))
    m = yaml.safe_load((work / "manifest.yaml").read_text())
    m["title"] = 'X</title><script>window.pwned=1</script> & co'
    (work / "manifest.yaml").write_text(yaml.dump(m, allow_unicode=True, sort_keys=False))
    gen = [p for p in sorted((work / "gen").glob("*.yaml")) if not p.name.endswith(".run.yaml")][0]
    g = yaml.safe_load(gen.read_text())
    g["lines"][0]["tokens"][0]["surface"] = "枯枝<!--<script>"
    gen.write_text(yaml.dump(g, allow_unicode=True, sort_keys=False))
    page = build.run(repo, "basho-furuike").read_text()
    head = page.split("<body>", 1)[0]
    assert "<script>window.pwned" not in head and "&lt;script&gt;window.pwned" in head and "&amp; co" in head
    payload = page.split("window.WEFT = ", 1)[1].split("</script>", 1)[0]
    assert "<" not in payload and "\\u003c!--\\u003cscript>" in payload
    g["lines"][0]["figure"] = {"file": "../../etc/hostname", "caption": "x"}
    gen.write_text(yaml.dump(g, allow_unicode=True, sort_keys=False))
    with pytest.raises(SystemExit, match="escapes the repository"):
        build.assemble(work)


def test_elvish_stress_matches_tolkien():
    """Quenya and Sindarin: the stress rule of Appendix E reproduces Tolkien's twelve worked examples
    (stressed vowel in capitals, his notation) and the stress he marked on words of Namárië in
    The Road Goes Ever On (1967), as cited by Eldamo."""
    from weft import elvish as E
    appendix_e = {"Isildur": "i-SIL-dur", "Oromë": "O-ro-me", "Eressëa": "e-RES-se-a", "Fëanor": "FE-a-nor", "ancalima": "an-KA-li-ma",
                  "Elentári": "e-len-TAA-ri", "Andúnë": "an-DOO-ne"}
    for w, want in appendix_e.items():
        assert E.word_sound(w, "qya")[1] == want, w
    for w, want in {"Denethor": "DE-ne-thor", "Periannath": "pe-ri-AN-nath", "Ecthelion": "ek-THE-li-on", "Pelargir": "pe-LAR-gir", "silivren": "si-LIV-ren"}.items():
        assert E.word_sound(w, "sjn")[1] == want, w
    rgeo = {"súrinen": "SOO-ri-nen", "únótimë": "oo-NOH-ti-me", "oromardi": "o-ro-MAR-di", "tellumar": "TEL-lu-mar", "ómaryo": "oh-MAR-yo",
            "Oiolossëo": "oy-o-LOS-se-o", "máryat": "MAAR-yat", "Calaciryo": "ka-la-KIR-yo", "Rómello": "roh-MEL-lo", "hiruvalyë": "hi-ru-VAL-ye",
            "enquantuva": "en-KWAN-tu-va", "falmalinnar": "fal-ma-LIN-nar", "Valimar": "VA-li-mar"}
    for w, want in rgeo.items():
        assert E.word_sound(w, "qya")[1] == want, w
    # letter values: c = k, qu = kw, final f = v, Sindarin y = ü, ae read as ai, ng final as in sing
    assert E.word_sound("Calacirya", "qya")[0].startswith("ka.la.")
    assert E.word_sound("nef", "sjn")[0] == "nɛv"
    assert E.word_sound("emyn", "sjn")[1] == "E-mün"
    assert E.word_sound("aear", "sjn")[1] == "AI-ar"
    assert E.word_sound("thalion", "sjn")[0].endswith("ɔn")


def test_aramaic_daniel():
    """Daniel 5 (Biblical Aramaic) reads through the Hebrew module: the OSHB's Aramaic verb stems decode
    from their own table, and a Ketiv (unpointed, as written) takes its sound from the Qere reading."""
    from weft import treebank as T
    assert "Stem=Peal" in T.oshb_to_ud("Vqp3ms", "A")
    assert "Stem=Qal" in T.oshb_to_ud("Vqp3ms", "H") and "Stem=Haphel" in T.oshb_to_ud("Vhp3ms", "A")
    g = yaml.safe_load((REPO / "texts/tanakh-daniel/gen/chapter05.yaml").read_text())
    toks = {t["id"]: t for l in g["lines"] for t in l["tokens"]}
    kasdaye = toks["dan.5.7.6"]
    import unicodedata
    letters = lambda x: "".join(c for c in x if not unicodedata.combining(c))
    assert kasdaye["surface"] == "כשדיא" and letters(kasdaye["norm"]) == "כשדאי"
    assert kasdaye["sound"]["tiberian"]["respell"] == "kas-daw-ʾAY"
    assert sum(1 for t in toks.values() if t.get("norm")) == 24
    r = check.run(REPO, "tanakh-daniel")
    assert r["ok"], r["problems"]


def test_index_newest_strip():
    """The library's 'newest texts' strip: every committed work has an arrival date from git, the strip
    lists the newest first, and a work git does not know still gets a date (from its manifest's mtime)."""
    import re
    from weft import build
    repo = Path(__file__).resolve().parents[1]
    ms = build.library_order(repo)
    dates = build.added_dates(repo, ms)
    assert set(dates) >= {m["work"] for m in ms}
    assert all(re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", d) for d in dates.values())
    out = repo / "site" / "build"
    html = build.newest_index(ms, out, dates, n=4)
    if any((out / f"{m['work']}.html").exists() for m in ms):
        shown = re.findall(r'datetime="([^"]+)"', html)
        assert 1 <= len(shown) <= 4 and shown == sorted(shown, reverse=True)
    ghost = dict(ms[0], work="not-in-git-" + ms[0]["work"])
    assert re.match(r"\d{4}-\d{2}-\d{2}T", build.added_dates(repo, [ghost])[ghost["work"]])


def test_esperanto_rules():
    """Esperanto: one letter one sound, penultimate stress, glides in one syllable, the elided o leaving the
    stress in place, and the rule-based reading of the 1887 divided words (Fundamento rules 9, 10, 16)."""
    from weft import esperanto as E
    assert E.word_sound("ĉielo") == ("tʃi.ˈe.lo", "chee-E-lo", 3)
    assert E.word_sound("kaj")[2] == 1 and E.word_sound("ankaŭ")[1] == "AN-kow" and E.word_sound("hodiaŭ")[1] == "ho-DEE-ow"
    assert E.word_sound("estas")[0] == "ˈes.tas" and E.word_sound("patro")[0] == "ˈpa.tro"
    assert E.word_sound("kor’")[1] == "kor" and E.word_sound("l’mondo")[1] == "LMON-do"
    assert E.word_sound("senmoveco")[0] == "sen.mo.ˈve.tso" and E.word_sound("ĝi")[0] == "dʒi" and E.word_sound("ŝuldantoj")[0] == "ʃul.ˈdan.toj"
    assert E.analyze("Pan'o'n") == ("pano", "NOUN|Case=Acc|Number=Sing")
    assert E.analyze("ŝuld'ant'o'j") == ("ŝuldanto", "NOUN|VerbForm=Part|Tense=Pres|Voice=Act|Case=Nom|Number=Plur")
    assert E.analyze("liber'ig'u") == ("liberigi", "VERB|Mood=Imp|VerbForm=Fin")
    assert E.analyze("detru'it'a")[0] == "detrui" and "Voice=Pass" in E.analyze("detru'it'a")[1]
    assert E.analyze("ni'a'j'n") == ("nia", "DET|Poss=Yes|PronType=Prs|Person=1|Case=Acc|Number=Plur")
    assert E.analyze("kor’") == ("koro", "NOUN|Case=Nom|Number=Sing") and E.analyze("kiu") == ("kiu", "PRON|PronType=Rel")
    assert E.analyze("konduku") == ("konduki", "VERB|Mood=Imp|VerbForm=Fin")   # an undivided word, read from its ending


def test_german_fraktur_ocr_normalizer(tmp_path):
    """The fraktur-ocr source format: long s to s, superscript-e umlauts to umlauts, the Fraktur hyphen
    rejoined, page numbers stripped; the comparison is without spaces, and a misreading left in the OCR
    (fie for sie) is not matched unless the token declares it in src."""
    from weft import german
    p = tmp_path / "ocr.txt"
    p.write_text("Der Vogelfaͤnger bin ich ja,\nStets luſtig, heißa! hopſaſa!\n89\nwenn ich dich ver⸗\nſtehen ſoll! Ich fing’ fie.\n", encoding="utf-8")
    src = german.source_text(p, "fraktur-ocr", r"(?m)^\s*\d+\s*$")
    assert "DerVogelfängerbinichja,Stetslustig,heißa!hopsasa!" in src
    assert "wennichdichverstehensoll!" in src and "89" not in src
    assert "Ichfing’fie." in src and "Ichfing’sie." not in src


def test_equation_lines_in_einstein():
    """A displayed equation is a line of its own: its TeX is checked against the source like any line, the page
    gets a MathML tree (never markup), and the words a reader says for it carry a sound row. The tree holds only
    MathML element names, so the page's builder can whitelist them."""
    import json
    from weft import draft
    gen = yaml.safe_load((Path(__file__).resolve().parents[1] / "texts" / "einstein-1905-energieinhalt" / "gen" / "sections.yaml").read_text())
    eqs = [l for l in gen["lines"] if l.get("equation")]
    assert len(eqs) == 8 and not any(l["tokens"] for l in eqs)
    e = eqs[-1]["equation"]
    assert e["tex"].startswith("K_{0}-K_{1}=") and e["mathml"]["t"] == "math" and e["mathml"]["a"]["display"] == "block"
    def tags(n): return {n["t"]} | set().union(*(tags(c) for c in n.get("c", []) if isinstance(c, dict)))
    assert tags(e["mathml"]) <= {"math", "mrow", "mi", "mn", "mo", "mfrac", "msup", "msub", "msqrt", "mtext", "mspace", "mstyle", "mpadded"}
    assert "<" not in json.dumps(e["mathml"]) and e["sound"]["modern"]["respell"]
    assert draft.mathml_tree(r"\frac{a}{b}")["c"][0]["c"][0]["t"] == "mfrac"
