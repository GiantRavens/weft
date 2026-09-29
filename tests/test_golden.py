"""Golden passage guards. Run: uv run --with pytest pytest -q"""
from pathlib import Path

import yaml

from weft import check, draft, greek, latin, norse

REPO = Path(__file__).resolve().parents[1]
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
    before = (work / "gen/lines.yaml").read_text()
    report = draft.run(work)
    assert (work / "gen/lines.yaml").read_text() == before
    assert report["counts"] == {"lines": 11, "tokens": 54}
    r = check.run(REPO, "beowulf")
    assert r["ok"], r["problems"]


def test_grettir_draft_and_check():
    work = REPO / "texts" / "saga-grettir"
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
