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


def test_connected_speech():
    """Pin 18: the proem spoken whole. Elision and clitics are tied (‿); the correptions are the four
    places the hexameter's dactyls need a long final vowel or diphthong read short."""
    import unicodedata as ud
    nfc = lambda x: ud.normalize("NFC", x)
    g = yaml.safe_load(nfc((WORK / "gen/book01.yaml").read_text()))
    ph = {l["id"]: l["phrase"]["restored"] for l in g["lines"]}
    assert ph["od.1.1"]["ipa"].startswith("án.dra‿moj én.ne.pe")          # μοι ἔννεπε: correption
    assert ph["od.1.3"]["ipa"].startswith("pol.lɔ̂ːn d‿an.tʰrɔ́ː.pɔːn")      # δʼ ἀνθρώπων: elision
    assert "d‿hó ɡ‿en‿pón.tɔːi" in ph["od.1.4"]["ipa"]                    # two elisions, then ἐν leans forward
    assert "kàj hɛː.mîːn" in ph["od.1.10"]["ipa"]                         # καὶ ἡμῖν: diphthong to glide
    assert sum(r["respell"].count("˘") for r in ph.values()) == 4
    # the later scheme ties the same words but keeps the long vowels: correption is the verse's, scheme one only
    er = g["lines"][0]["phrase"]["erasmian"]["respell"]
    assert er.startswith("AN-dra‿moy EN-ne-pe") and "˘" not in er
    # clitics from the spelling, and the article told from the pronoun by its lemma
    assert greek.clitic("μοι") == "en" and greek.clitic("τις") == "en" and greek.clitic("ἐν") == "pro"
    assert greek.clitic("οἱ", "ὁ") == "pro" and greek.clitic("οἱ", "ἕ") == "en"
    assert greek.clitic("ἄνδρα") is None and greek.clitic("δʼ") is None     # accented; elided
    assert nfc(greek._correpted("pɛ̂ː")) == nfc("pɛ̂") and nfc(greek._correpted("kaì")) == nfc("kàj")
    # the scanner names the words it shortened, by their index among the printed words
    _, _, corr = greek.scan_hexameter("ἄνδρα μοι ἔννεπε, μοῦσα, πολύτροπον, ὃς μάλα πολλὰ".split(), Q, detail=True)
    assert corr == [1]


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
        assert report["counts"] == {"lines": 396, "tokens": 1494}   # all 65 stanzas; +6 lines in 23 and 33, recovered by pin 72
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
        assert report["counts"] == {"lines": 124, "tokens": 1248}   # all the prose of chapter 14
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
    # one inscription per work since the 2026-10-09 split; together the same 4 lines and 41 tokens
    for name, counts in (("runes-kylver", {"lines": 1, "tokens": 24}), ("runes-gallehus", {"lines": 1, "tokens": 5}),
                         ("runes-rok", {"lines": 2, "tokens": 12})):
        work = REPO / "texts" / name
        if sources_present(work):
            before = (work / "gen/inscriptions.yaml").read_text()
            report = draft.run(work)
            assert (work / "gen/inscriptions.yaml").read_text() == before
            assert report["counts"] == counts
            assert report["failures"] == {}
        r = check.run(REPO, name)
        assert r["ok"], (name, r["problems"])


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


def test_danish_medieval_latin():
    """Latin in Denmark around 1200 (Saxo), read from Holder's medieval spellings."""
    q = LQ
    cases = {"gracia": "GRA-see-a",          # ci before a vowel; c before i = s
             "gratia": "GRA-see-a",          # ti before a vowel takes the value of ci
             "Regnerus": "REG-ne-roos",      # g hard before n; no quantity, so the antepenult
             "Iuarus": "EE-va-roos",         # iu before a vowel is I + v, not j + u
             "michi": "MEE-kee",             # ch = k
             "mihi": "MEE-kee",              # h between vowels in mihi = k, as michi shows
             "nichil": "NEE-keel",
             "celum": "SE-loom",             # e for ae
             "caelum": "SE-loom",
             "cuius": "KOO-yoos",            # i between vowels = j
             "uirtus": "VEER-toos",          # initial u before a vowel = v
             "Siuardus": "see-VAR-doos",     # u between vowels = v; closed penult stressed
             "Syuardus": "see-VAR-doos",     # y = i
             "homo": "HO-mo",                 # h sounded
             "incipit": "EEN-see-peet",      # n stays n before soft c
             "quia": "KVEE-a"}               # the u of qu is not a vowel, so i stays a vowel
    for w, want in cases.items():
        assert latin.phonemize(w, "danish-medieval", q)["respell"] == want, w
    assert latin.phonemize("gracia", "as-first-read", q, dialect="danish")["respell"] == "GRA-see-a"
    assert latin.SCHEME_LABELS["danish-medieval"] == "As first read: Latin in Denmark around 1200 (approximate)"
    assert latin.phonemize("cuius", "danish-medieval", q)["known"]          # through the table's cujus
    # the existing schemes are untouched by the new one
    assert latin.phonemize("caelum", "anglo-norman", q)["respell"] == "TSE-lüm"


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
    # Descartes and Newton, one page each since the 2026-10-09 split; together the same 10 lines and 91 tokens
    for name, counts in (("descartes-principia", {"lines": 4, "tokens": 32}), ("newton-principia", {"lines": 6, "tokens": 59})):
        work = REPO / "texts" / name
        if sources_present(work):
            before = (work / "gen/sections.yaml").read_text()
            report = draft.run(work)
            assert (work / "gen/sections.yaml").read_text() == before
            assert report["counts"] == counts
            assert report["failures"] == {}             # every line verbatim in its own source
        r = check.run(REPO, name)
        assert r["ok"], (name, r["problems"])


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
    """The generated meter row equals every hand scansion in curated/ (Odyssey 1.1-10, Iliad 1.1-52):
    the hand work is the scanner's regression test."""
    for work in ("homer-odyssey", "homer-iliad"):
        wd = REPO / "texts" / work
        gen = yaml.safe_load((wd / "gen" / "book01.yaml").read_text())
        made = {l["id"]: l.get("metre") for l in gen["lines"]}
        hand = {}
        for f in sorted((wd / "curated").glob("*.yaml")):
            for cs in yaml.safe_load(f.read_text()) or []:
                for k, v in (cs.get("set") or {}).items():
                    # a line the scanner cannot fit (synecphonesis at Iliad 1.277) is scanned by hand and
                    # marked scanner: no-fit; it is the scanner's open case, not a regression
                    if isinstance(v, dict) and "metre" in v and v.get("scanner") != "no-fit":
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
    for work in ("kant-aufklaerung", "kant-practical-reason", "nietzsche-gay-science", "nietzsche-zarathustra", "luther-bible"):
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
            assert target in ("index", "search") or f"{target}.html" in pages, (name, target)   # search.html is written by weft index



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
    assert E.word_sound("Calacirya", "qya")[0].startswith("ˌka.la.")       # secondary stress, RGEO Càlacíryo
    assert E.word_sound("nef", "sjn")[0] == "nɛv"
    assert E.word_sound("emyn", "sjn")[1] == "E-mün"
    assert E.word_sound("aear", "sjn")[1] == "AI-ar"
    assert E.word_sound("thalion", "sjn")[0].endswith("ɔn")
    # RGEO p. 71: Sindarin ng at the start of a word is the ng of sing; the long diphthongs prolong
    # their first vowel. Inside a word ng is the ng of finger (and the IPA table must hold it)
    assert E.word_sound("nguruthos", "sjn")[0].startswith("ˈŋu")
    assert "uˑi̯" in E.word_sound("Fanuilos", "sjn")[0]
    assert E.word_sound("Ingwë", "qya") == ("ˈiŋ.gʷɛ", "ING-gwe", 2)
    assert E.word_sound("Angband", "sjn")[1] == "ANG-band"


def test_elvish_secondary_stress_matches_rgeo():
    """Quenya secondary stress (RGEO pp. 68-69) against the marks Tolkien printed on Namárië (RGEO
    p. 66): every syllable he marks major (acute) or minor (grave) carries ˈ or ˌ in the IPA, and no
    other. Words in the Lord of the Rings spelling; RGEO's hyphenated compounds as their parts;
    monosyllables, which take sentence stress, are left out."""
    from weft import elvish as E
    marks = {"súrinen": {0, 2}, "únótimë": {0, 1, 3}, "aldaron": {0, 2}, "avánier": {1, 3}, "oromardi": {0, 2},
             "lisse": {0}, "miruvóreva": {0, 2, 4}, "Andúnë": {0, 1}, "tellumar": {0, 2}, "tintilar": {0, 2},
             "eleni": {0, 2}, "ómaryo": {0, 1}, "lirinen": {0, 2}, "enquantuva": {0, 1, 3}, "Tintallë": {0, 1},
             "Oiolossëo": {0, 2, 4}, "Elentári": {0, 2}, "ortanë": {0, 2}, "undu": {0}, "lávë": {0}, "lumbulë": {0, 2},
             "sinda": {0}, "noriello": {0, 2}, "mornië": {0, 2}, "falmalinnar": {0, 2}, "hísië": {0, 2},
             "Calaciryo": {0, 2}, "oialë": {0, 2}, "Rómello": {0, 1}, "Valimar": {0, 2}, "Namárië": {1, 3},
             "hiruvalyë": {0, 2}, "hiruva": {0, 2}, "luini": {0}, "caita": {0}, "aire": {0}}
    stressed = lambda w: {k for k, s in enumerate(E.word_sound(w, "qya")[0].split(".")) if s[:1] in "ˈˌ"}
    for w, want in marks.items():
        assert stressed(w) == want, w
    # the one divergence: laurië (line 1) ends in two short syllables after the stress, so the rule
    # gives its last a light stress, but the light stress is one that "could be used metrically" and
    # the line does not use it; Tolkien leaves it unmarked
    assert stressed("laurië") == {0, 2}
    assert "ˌ" not in E.word_sound("Elbereth", "sjn")[0]           # no secondary stress in Sindarin


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


def test_shema_large_letters_and_the_divine_name(tmp_path):
    """The OSHB wraps the Shema's enlarged ayin and dalet in a <seg> inside the word, and the reader keeps
    their text; the divine name is sounded as the word read in its place (qere perpetuum), accent carried
    over, and after a prefix the reading follows the prefix as written (pin 167)."""
    from weft import treebank as T
    osis = tmp_path / "x.xml"
    osis.write_text('<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace"><verse osisID="Deut.6.4">'
                    '<w lemma="8085" morph="HVqv2ms">שְׁמַ֖<seg type="x-large">ע</seg></w>'
                    '<w lemma="3068" morph="HNp">יְהוָ֥ה</w>'
                    '<w lemma="l/3068" morph="HR/Np">לַ/יהוָ֥ה</w></verse></osis>', encoding="utf-8")
    rows = T.load_oshb(osis, "Deut", 6, 4, 4, {})[4]
    assert rows[0]["word"] == "שְׁמַ֖ע"
    assert rows[1]["qere"] == "אֲדֹנָ֥י" and rows[1]["perpetuum"]
    assert rows[2]["qere"] == "לַאדֹנָ֥י" and rows[2]["perpetuum"]
    from weft import hebrew as he   # a verse-final name: the silluq (written as meteg) carries over to the reading
    osis.write_text('<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace"><verse osisID="Deut.6.4">'
                    '<w lemma="3068" morph="HNp">יְהוָֽה</w></verse></osis>', encoding="utf-8")
    q = T.load_oshb(osis, "Deut", 6, 4, 4, {})[4][0]["qere"]
    assert he.phonemize(q, "tiberian", silluq=True)["respell"] == "ʾa-dhoh-NAWY"
    g = yaml.safe_load((REPO / "texts/tanakh-shema/gen/chapter06.yaml").read_text())
    toks = {t["id"]: t for l in g["lines"] for t in l["tokens"]}
    assert toks["deut.6.4.1"]["sound"]["tiberian"]["respell"] == "sha-MAʿ"
    assert toks["deut.6.4.6"]["sound"]["tiberian"]["respell"] == "ʾe-ḤAWDH"
    assert toks["deut.6.4.3"]["sound"]["tiberian"]["respell"] == "ʾa-dhoh-NAWY"
    r = check.run(REPO, "tanakh-shema")
    assert r["ok"], r["problems"]


def test_kaddish_prayer_book_pointing():
    """The Kaddish is pointed without cantillation: the stress is declared (final by default, the penult where the
    edition says so); כָּל standing alone is qamets qatan; the yod of the suffix ָיו is not sounded."""
    from weft import hebrew as he
    assert he.phonemize("יִתְגַּדַּל", "tiberian", stress=1)["respell"] == "yith-gad-DAL"
    assert he.phonemize("עָלֵינוּ", "modern-israeli", stress=2)["respell"] == "a-LE-noo"
    assert he.phonemize("דְּכָל", "modern-israeli", stress=1)["respell"] == "de-KHOL"
    assert he.phonemize("בִּמְרוֹמָיו", "tiberian", stress=1)["respell"] == "bim-roh-MAWV"
    for w in ("וַתּוּכָֽל", "מַאֲכָל֙", "הֵיכָל"):   # only כל and its prefixes, not any word ending in -כָל
        assert "KHOL" not in he.phonemize(w, "modern-israeli", stress=1)["respell"].upper(), w
    assert he.phonemize("בְּרֵאשִׁ֖ית", "tiberian", stress=1)["respell"] == "ba-ray-SHEETH"   # an accent wins
    r = check.run(REPO, "kaddish")
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


def test_every_work_has_a_kind_and_the_index_groups_them():
    """Every manifest names one of the seven kinds, and the library page's 'By kind' disclosure lists the
    kinds in their fixed order with every built work under exactly one of them."""
    import re
    from weft import build
    repo = Path(__file__).resolve().parents[1]
    ms = build.library_order(repo)
    assert all(m.get("kind") in build.KINDS for m in ms), [m["work"] for m in ms if m.get("kind") not in build.KINDS]
    out = repo / "site" / "build"
    html = build.kind_index(ms, out)
    built = [m for m in ms if (out / f"{m['work']}.html").exists()]
    if built:
        heads = re.findall(r"<li><b>([^<]+)</b>", html)
        assert heads == [build.KINDS[k] for k in build.KINDS if any(m["kind"] == k for m in built)]
        assert html.count("<a href=") == len(built)


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


def test_german_monosyllables_stress_by_one_rule():
    """Every monosyllable in the German lexicon is stressed unless it is a function word (UNSTRESSED) or its
    entry says otherwise with ˈ: an entry made for a long vowel (zehn: ze:hn) once silently unstressed the word."""
    from weft import german
    for k, v in german.lexicon().items():
        syl = v.get("syl") if isinstance(v, dict) else v
        if not isinstance(syl, str) or "." in syl:
            continue
        ipa = german.word_ipa(k, "modern")[0]
        # an explicit ˈ is a judgment and wins (war, marked stressed); otherwise the rule decides
        assert ipa.startswith("ˈ") == ("ˈ" in syl or k not in german.UNSTRESSED), (k, syl, ipa)
    assert german.phonemize("zehn", "northern")["respell"] == "TSAYN"
    assert german.phonemize("gleich", "northern")["respell"] == "GLAIHY"
    assert german.phonemize("wär", "northern")["respell"] == "vehr"        # an auxiliary, as war
    assert german.phonemize("el", "modern")["respell"] == "EL"             # a letter name given as IPA


def test_latin_initial_i():
    """Word-initial i before a vowel is the consonant of iam, except before another i (iīs, iīdem: no
    Latin word begins ji-) and in declared Greek words (iambus, Iōnia). Pin 75."""
    from weft import latin as L
    syl = lambda w: L.phonemize(w, "classical")["syllables"]
    assert L.phonemize("iam", "classical")["ipa"] == "jam" and syl("iūnctus") == 2
    assert syl("iīs") == 2 and syl("iīsdem") == 3 and syl("iambus") == 3 and syl("Iōnia") == 4


def test_elvish_tengwar():
    """The Tengwar row (weft#196). Quenya: the words below were read letter by letter off Tolkien's
    Tengwar of Namárië (The Road Goes Ever On, 3rd ed. p. 65) and the classical mode reproduces each;
    the rest of the poem awaits the same reading (private/tolkien-namarie/review/). Sindarin: App. E's
    general use, Weft's transcription."""
    from weft import elvish as E
    cps = lambda w, l: " ".join("%04X" % ord(c) for c in E.tengwar(w, l))
    read_from_p65 = {
        "laurië": "E022 E02B E040 E020 E044 E02E E046",      # au: úre carries the a
        "lantar": "E022 E040 E00C E040 E014",                # nt anto; final r óre
        "súrinen": "E024 E02C E04C E020 E044 E010 E046 E010",  # ú on the long carrier; r rómen before a vowel
        "yéni": "E016 E043 E048 E010 E044",                  # anna with the y-dots; é a doubled accent
        "únótimë": "E02C E04C E010 E02C E04A E000 E044 E011 E046",
        "ve": "E015 E046",
        "rámar": "E020 E02C E040 E011 E040 E014",
        "aldaron": "E02E E040 E023 E040 E020 E04A E010",     # ld alda
        "yuldar": "E016 E043 E04C E023 E040 E014",
        "avánier": "E02E E040 E015 E02C E040 E010 E044 E02E E046 E014",
    }
    for w, want in read_from_p65.items():
        assert cps(w, "qya") == want, w
    assert cps("vanwa", "qya") == "E015 E040 E010 E017 E040"       # medial nw: númen + vilya, as Tolkien writes vanwa
    # Sindarin, general use: the vowel sign over the consonant after it; ng at the start is nwalme
    assert cps("Elbereth", "sjn") == "E022 E046 E005 E020 E046 E008 E046"
    assert cps("nguruthos", "sjn").startswith("E013")
    assert cps("Angband", "sjn") == "E007 E050 E040 E005 E004 E050 E040"


def test_namarie_pauses():
    """Tolkien's pause marks on Namárië (RGEO p. 76, weft#197): every mark on his page, on the word it
    follows, and the key quotes his definition. Private work: skipped where the owner's copy is absent."""
    p = REPO / "private/tolkien-namarie/curated/pauses.yaml"
    if not p.exists():
        pytest.skip("private work not present")
    marks = {k: v["pause"] for cs in yaml.safe_load(p.read_text()) for k, v in cs["set"].items()}
    assert marks == {
        "nam.1.1.5": "|", "nam.1.2.5": "|||", "nam.1.4.3": "||", "nam.1.6.2": "|", "nam.1.7.2": "|||",
        "nam.1.8.6": "|||", "nam.1.9.5": "|", "nam.1.10.5": "||", "nam.1.11.5": "|||", "nam.1.13.4": "||",
        "nam.1.14.4": "||", "nam.1.15.6": "|||", "nam.1.16.1": "|||", "nam.1.16.4": "||", "nam.1.17.3": "||",
        "nam.1.17.4": "|||"}
    from weft import elvish as E
    assert any("ascending order of time-length and tone-fall" in d for _, d in E.KEY["tolkien"])


def test_namarie_feet():
    """Tolkien's foot divisions on Namárië (RGEO p. 76, weft#200), recorded only where read clearly. Each
    string is the line's own text with | where a hairline is drawn; no line has more than 6 feet
    (RGEO p. 68: 5 or 6), and the lines read in full divide as he says (trochee opening line 2, anapaest
    in the second foot of line 1). Private work: skipped where absent."""
    p = REPO / "private/tolkien-namarie/curated/metre.yaml"
    if not p.exists():
        pytest.skip("private work not present")
    metre = {k: v["metre"] for cs in yaml.safe_load(p.read_text()) for k, v in cs["set"].items()}
    ed = yaml.safe_load((REPO / "private/tolkien-namarie/edition.yaml").read_text())
    text = {f"nam.1.{n}": " ".join(t["t"] for t in l["tokens"]) for n, l in enumerate(ed["sections"][0]["lines"], 1)}
    norm = lambda s: " ".join(s.replace("|", "").split())
    for k, m in metre.items():
        assert norm(m) == " ".join(text[k].split()), k       # the line itself, only dividers added
        assert m.count("|") <= 5, k
    assert metre["nam.1.1"].split("|")[1].strip() == "rië lan"      # the anapaest, foot 2
    assert metre["nam.1.2"].split("|")[0] == "yéni"                  # the opening trochee
    assert {"nam.1.10", "nam.1.12", "nam.1.14"}.isdisjoint(metre)    # not yet read


def test_oshb_short_segments_and_prefixed_divine_name():
    """Pin 167. A short OSHB segment no longer indexes past its end ("" in "123" is True, so a pronoun
    with no person broke Dan. 8), and empty features are dropped. The divine name after a prefix is sounded
    from the qere perpetuum: the prefix as written (its vowel is the reading's), then אדני without the
    hateph under its aleph, so לַיהוָה reads laʾdōnāy (Gen 4:3)."""
    from weft import treebank as T
    assert T.oshb_to_ud("Pp", "A") == "PRON|PronType=Prs" and T.oshb_to_ud("V", "A") == "VERB"
    if not (sources_present(REPO / "texts/tanakh-daniel") and sources_present(REPO / "texts/tanakh-genesis")):
        pytest.skip("OSHB sources not fetched (weft acquire); the segment checks above still ran")
    w = REPO / "texts/tanakh-daniel"
    m = yaml.safe_load((w / "manifest.yaml").read_text())
    lex = T.load_strong_lexicon(w / m["edition"]["lexicon"])
    assert len(T.load_oshb(w / m["edition"]["file"], "Dan", 8, 1, 60, lex)) == 27
    g = REPO / "texts/tanakh-genesis"
    gm = yaml.safe_load((g / "manifest.yaml").read_text())
    v = T.load_oshb(g / gm["edition"]["file"], gm["edition"]["osis_book"], 4, 3, 3, T.load_strong_lexicon(g / gm["edition"]["lexicon"]))
    name = next(r for r in v[3] if r.get("perpetuum"))
    assert name["qere"] == "לַֽאדֹנָֽי"


def test_ocr_witness_check_is_order_aware():
    """Pin 170. The OCR witness check walks the edition's lines in order through the witness: a line whose
    readings are copied from a later printed line is out of order, and witness letters left between two
    lines (a dropped line edge) are unattributed. The real Cherokee Constitution passes; two altered copies
    fail with those classes."""
    import copy
    from weft import ocr
    ed = yaml.safe_load((REPO / "texts/cherokee-constitution-1827/edition.yaml").read_text())
    lines = [l for s in ed["sections"] for l in s["lines"]]
    run = lambda e, ls: [c for l in ls for c, _ in ocr.witness_check(l["tokens"], e, "chr")]
    assert run(ed, lines) == []
    # (a) line 3 carries line 6's words: found only after the cursor has moved past it on the next pass
    e2 = copy.deepcopy(ed); l2 = [l for s in e2["sections"] for l in s["lines"]]
    l2[2]["tokens"] = copy.deepcopy(l2[5]["tokens"])
    assert "ocr-line-out-of-order" in run(e2, l2)
    # (b) a line loses its last word: the witness keeps letters no line accounts for
    e3 = copy.deepcopy(ed); l3 = [l for s in e3["sections"] for l in s["lines"]]
    l3[4]["tokens"] = l3[4]["tokens"][:-1]
    assert "ocr-letters-unattributed" in run(e3, l3)


def test_note_links_to_other_works(tmp_path):
    """Pin 77. A note's see: [work, ...] becomes links titled from those works' manifests; a public work's
    note never links to a private work, and a name that is no work is left for weft check to report."""
    import shutil
    from weft import build as B
    d = B.assemble(REPO / "texts/inter-caetera-1493")
    links = [l for n in d["notes"] for l in n.get("see_links", [])]
    assert {"href": "columbus-letter-1493.html", "title": yaml.safe_load((REPO / "texts/columbus-letter-1493/manifest.yaml").read_text())["title"]} in links
    shutil.copytree(REPO / "texts/basho-furuike", tmp_path / "texts/basho-furuike")
    (tmp_path / "private/secret").mkdir(parents=True)
    (tmp_path / "private/secret/manifest.yaml").write_text("work: secret\ntitle: Secret\n")
    nf = tmp_path / "texts/basho-furuike/notes/zz-see.yaml"
    first = yaml.safe_load(next((tmp_path / "texts/basho-furuike/notes").glob("*.yaml")).read_text())[0]["attach"]
    nf.write_text(yaml.safe_dump([{"id": "n.see", "attach": first, "kind": "editorial", "text": "x", "see": ["secret", "no-such-work"]}]))
    n = next(n for n in B.assemble(tmp_path / "texts/basho-furuike")["notes"] if n["id"] == "n.see")
    assert "see_links" not in n and n["see_unknown"] == ["secret", "no-such-work"]


def test_manifest_sound_key_override(tmp_path):
    """Pin 59. A manifest's sound_key replaces a scheme's shared key on that work's page only, and
    weft check reports a sound_key for a scheme the work does not use."""
    import shutil
    from weft import build as B, check as C
    shutil.copytree(REPO / "texts/basho-furuike", tmp_path / "texts/basho-furuike")
    mp = tmp_path / "texts/basho-furuike/manifest.yaml"
    m = yaml.safe_load(mp.read_text())
    m["sound_key"] = {"modern": [["CAPS", "a key written for this work"]], "no-such": [["x", "y"]]}
    mp.write_text(yaml.safe_dump(m, allow_unicode=True))
    d = B.assemble(tmp_path / "texts/basho-furuike")
    assert d["keys"]["modern"] == [("CAPS", "a key written for this work")]
    assert d["keys"]["edo-1686"] == B.assemble(REPO / "texts/basho-furuike")["keys"]["edo-1686"]   # the other scheme keeps the shared key
    r = C.run(tmp_path, "basho-furuike")
    assert "manifest-sound-key" in r["problems"]


def test_lemma_not_in_lexicon_sensor():
    """Pin 47. With the curated corrections ignored, GLAUx's invented lemmas in Epictetus and Marcus are
    caught (the four named in the ticket among them); with corrections and the declared exceptions, the
    drafts report none. Needs the LSJ headword list (weft lexica); skipped where it is absent."""
    from weft import lexica as L
    hw = L.lsj_headwords()
    if hw is None:
        pytest.skip("LSJ headword list not fetched (weft lexica)")
    raw = set()
    for w in ("epictetus-enchiridion", "marcus-meditations"):
        g = yaml.safe_load((REPO / f"texts/{w}/gen/sections.yaml").read_text())
        for l in g["lines"]:
            for t in l["tokens"]:
                lem = t.get("lemma") or ""
                if lem and not lem[:1].isupper() and not (t.get("morph") or "").startswith(("d-", "ADV")) \
                        and lem not in L.grc_lemma_ok() and L.bare_grc(lem) not in hw:
                    raw.add(lem)
    assert {"ταραχθαίνω", "περιβαλέω", "ἀπαραποδύς", "συντεύχω"} <= raw
    for w in ("epictetus-enchiridion", "marcus-meditations"):
        run = yaml.safe_load((REPO / f"texts/{w}/gen/sections.run.yaml").read_text())
        assert "lemma-not-in-lexicon" not in run["failures"], w


def test_tang_falls_back_to_baxter_middle_chinese():
    """Pin 154. A character with no Tang reading in Unihan shows Baxter's Middle Chinese, marked °,
    from the Baxter-Sagart list; a character in neither source stays ?, and the key says both."""
    from weft import chinese as C
    assert C.phonemize("弗", "tang", {})["respell"] == "°pjut"
    assert C.phonemize("〇", "tang", {})["respell"] == "?"
    assert any(sym.startswith("°") for sym, _ in C.KEY["tang"])


def test_notes_check_measures_closeness(tmp_path):
    """Pin 114. weft notes-check: an editorial note sharing a run of 6+ words with the commentary, or quoting
    15+ words, is reported; a retelling in other words passes."""
    from weft import notescheck as N
    src = tmp_path / "commentary.txt"
    src.write_text("The epithet is best taken as of many turns, a man who is never at a loss for a plan.", encoding="utf-8")
    (tmp_path / "w" / "notes").mkdir(parents=True)
    notes = [
        {"id": "n.ok", "kind": "editorial", "text": "The scholar reads the word as describing a resourceful man."},
        {"id": "n.run", "kind": "editorial", "text": "He says it means a man who is never at a loss for words."},
        {"id": "n.quote", "kind": "editorial", "text": "He writes \"one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen\"."},
        {"id": "n.pd", "kind": "quoted", "source": "x", "text": "best taken as of many turns, a man who is never at a loss"},
    ]
    (tmp_path / "w" / "notes" / "n.yaml").write_text(yaml.safe_dump(notes, allow_unicode=True))
    r = N.run(tmp_path / "w", src)
    assert r["notes"] == 3 and not r["ok"]
    assert r["failures"] == {"note-shares-run": 1, "note-quote-too-long": 1}
    assert r["samples"]["note-shares-run"][0].startswith("n.run: 9 words")


def test_tls_context_supplies_intermediates_without_weakening():
    """Pin 69. weft's fetches use the system roots plus pinned intermediates that some servers omit (Oracc);
    hostname checking and verification stay on, and partial chains stay off, so an intermediate never ends
    a chain on its own."""
    import ssl
    from weft import tls
    ctx = tls.context()
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname
    assert not ctx.verify_flags & ssl.VERIFY_X509_PARTIAL_CHAIN
    assert all((tls.DIR / n).exists() for n in tls.PINS)


def test_hocr_check_is_core():
    """Pin 63. The hOCR body-column check lives in weft.ocr and runs for any edition whose ocr_check names
    pages: Linschoten's lines pass, and a line with a word changed is reported."""
    import copy
    from weft import ocr, dutch
    assert not hasattr(dutch, "line_checks")            # the check is core, not the Dutch module's
    if not sources_present(REPO / "texts/linschoten-japan"):
        pytest.skip("Linschoten's hOCR not fetched (weft acquire)")
    ed = yaml.safe_load((REPO / "texts/linschoten-japan/edition.yaml").read_text())
    lines = [l for s in ed["sections"] for l in s["lines"] if isinstance(l, dict)]
    assert all(ocr.hocr_check(l["tokens"], ed) == [] for l in lines)
    bad = copy.deepcopy(lines[0]["tokens"]); bad[0]["t"] = "Xyzzy"; bad[0].pop("ocr", None)
    assert ocr.hocr_check(bad, ed)[0][0] == "edition-not-in-source"


def test_keyed_treebank_core_sensors(tmp_path):
    """Pin 70. A keyed treebank (format: keyed) is read by the language module's load_treebank and looked up
    by draft, which reports under the core names: a token whose identifier is not in the corpus as
    no-treebank-word, a form that differs as form-mismatch, an unlemmatized word as treebank-lemma-missing.
    Uses a copy of the Enheduanna work; skipped where its Oracc file is not fetched."""
    import shutil
    from weft import draft
    src = REPO / "texts/enheduanna-temple-hymns"
    if not sources_present(src):
        pytest.skip("Oracc file not fetched (weft acquire)")
    wd = tmp_path / "texts" / "enheduanna-temple-hymns"
    shutil.copytree(src, wd)
    ed = yaml.safe_load((wd / "edition.yaml").read_text())
    toks = [t for s in ed["sections"] for l in s["lines"] if isinstance(l, dict) for t in l["tokens"]]
    toks[0]["ref"] = "P346196.no.such"            # no row
    toks[1]["t"] = toks[1]["t"] + "x"               # a form Oracc does not have
    (wd / "edition.yaml").write_text(yaml.safe_dump(ed, allow_unicode=True, sort_keys=False))
    r = draft.run(wd)
    assert r["failures"].get("no-treebank-word") == 1
    assert r["failures"].get("form-mismatch") == 1
    assert r["failures"].get("treebank-lemma-missing") == 4
    assert not any(k.startswith(("oracc-", "tla-")) for k in r["failures"])


def test_greek_vowel_length_from_lexicon():
    """Pin 17. A long α, ι, υ the spelling does not show: the first-declension -ας is long (a rule, needs no
    data); with the LSJ quantity list (weft lexica), the lemma's headword marks carry over to the form's
    stem, and they agree with the hand tables, which were checked against the hexameter."""
    from weft import greek as G, lexica as L
    assert G.first_declension_as("ψυχὰς", "ψυχή") == "ψυχᾱ̀ς"          # accusative plural
    assert G.first_declension_as("ἄνδρας", "ἀνήρ") is None              # third declension: short
    assert G.unmarked_dichrona("ἄνδρα") == 2 and G.unmarked_dichrona("ψῡχήν") == 0 and G.unmarked_dichrona("παῖς") == 0
    if L.lsj_long_marks() is None:
        pytest.skip("LSJ quantity list not built (weft lexica)")
    assert G.quantity_from_lexicon("ψυχὰς", "ψυχή") == "ψῡχᾱ̀ς"
    assert G.quantity_from_lexicon("μυθήσασθαι", "μυθέομαι") is not None
    assert G.quantity_from_lexicon("φύσις", "φύσις") is None              # LSJ: short υ, nothing to mark


def test_latin_quantities_draft_from_lewis_and_short(tmp_path):
    """Pin 21. weft quantities proposes table entries from Lewis and Short for the forms no table lists. With
    the Res Gestae's own table withheld, its proposals are checked against that table: at least 85% of the
    long marks it places are long there (90% measured), no proposal marks a nominative ending onto another
    form (aedem stays short), and nothing is written to a table. Needs weft lexica; skipped without it."""
    import shutil, unicodedata as ud
    from weft import quantities as Q, lexica as L
    if L.ls_long_marks() is None:
        pytest.skip("Lewis and Short list not built (weft lexica)")
    wd = tmp_path / "texts" / "res-gestae-augusti"
    shutil.copytree(REPO / "texts/res-gestae-augusti", wd, ignore=shutil.ignore_patterns("sources"))
    (tmp_path / "pipeline/weft/data").mkdir(parents=True)
    shutil.copy(REPO / "pipeline/weft/data/lat_quantities.yaml", tmp_path / "pipeline/weft/data/")
    m = yaml.safe_load((wd / "manifest.yaml").read_text())
    m["quantities"] = ["pipeline/weft/data/lat_quantities.yaml"]
    (wd / "manifest.yaml").write_text(yaml.safe_dump(m, allow_unicode=True))
    r = Q.run(wd)
    prop = yaml.safe_load((wd / "gen/quantities-proposed.yaml").read_text())
    held = yaml.safe_load((REPO / "pipeline/weft/data/lat_quantities_resgestae.yaml").read_text())
    def longs(s):
        out, k = set(), -1
        for ch in ud.normalize("NFD", s.lower()):
            if ud.combining(ch):
                if ch == "̄" and k >= 0:
                    out.add(k)
            elif "a" <= ch <= "z":
                k += 1
        return out
    placed = agree = 0
    for f, v in prop.items():
        if isinstance(held.get(f), str):
            p, h = longs(v), longs(held[f].replace("+", ""))
            placed += len(p); agree += len(p & h)
    assert r["proposed"] > 300 and agree / placed >= 0.85, (agree, placed)
    assert "aedem" not in prop or "̄" not in ud.normalize("NFD", prop["aedem"])
    assert not any("[" in k or "]" in k for k in prop)
