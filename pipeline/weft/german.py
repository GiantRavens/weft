"""German (Kant, 1784 and 1788; Nietzsche, 1882 and 1883): modern spelling -> syllables -> sound.

Scope. Two works use this module: Kant (Was ist Aufklärung?, Berlin 1784; the conclusion of the
Critik der practischen Vernunft, Riga 1788) and Nietzsche (Die fröhliche Wissenschaft §125,
Chemnitz 1882; Also sprach Zarathustra, Vorrede 1, Chemnitz 1883). The printed text keeps the
spelling of the first editions (Muth, Gemüth, Theil, Zwey, Bewußtseyn; dreissig, todt, gieng).
Each token gives by hand, in n, the modern spelling of the same word form (Mut, Gemüt, Teil, zwei,
Bewusstsein; dreißig, tot, ging); the form itself is not modernized (drohet and einsperreten stay).
The page shows n under the original as "Modern spelling". The sound of both schemes is computed
from n. The old spellings carry no sound information that n lacks: th in Muth and Theil was [t],
and y in seyn and Zwey was the diphthong of sein, as the grammarians of the period say.

Syllable division and stress come from a hand-written lexicon, `pipeline/weft/data/de_lexicon.yaml`,
keyed by n (lowercased). The division follows the morphemes (ver.stan.des, Fens.ter), which lets
the rules below tell a morpheme-initial st (ver-stehen, [ʃt]) from a medial one (Fenster, [st]).
A colon after a vowel marks it long in a closed syllable (ge.ˈmü:t); h after a vowel, a doubled
vowel and ie are long by spelling; a stressed vowel in an open syllable is long. Letters become
sounds by the rules below, one syllable at a time. Words whose letters do not give the sound (the
Latin of Kant's text, French and Latin loans) carry an IPA form per scheme in the lexicon.

Schemes
-------
northern  Educated northern German before the stage norm, approximate. The same scheme serves both
          works; each manifest names its time and place through scheme_labels. Kant: educated
          German as read aloud in Königsberg in the 1780s. Nietzsche: educated German of the 1880s.
          Theodor Siebs's Deutsche Bühnenaussprache (1898) fixed a stage norm out of north German
          practice with some southern features; before it there was no codified norm, and the
          scheme models the features the evidence shows for educated northern speech of the
          period and that a per-word respelling can show:
          - g at the end of a syllable after a vowel is a fricative: [ç] after front vowels and
            [x] after back vowels (Weg [veːç], Tag [taːx], trug [truːx]). This was usual in the
            north; Siebs's stage norm kept the fricative only in the ending -ig and otherwise
            prescribed [k], which is the modern standard. Initial g and g between vowels are
            written as the stop [g]. Northern speakers also had a fricative between
            vowels (sagen with [ɣ]); the scheme does not model it, because the evidence for
            educated reading pronunciation is weaker there.
          - final devoicing: b d g s at the end of a syllable are voiceless, as today.
          - r is a tongue-tip trill [r] in every position, also after a vowel and in -er. The
            uvular r was spreading in the towns during the 18th and 19th centuries; how far it had
            reached educated speech in Königsberg in the 1780s, or Nietzsche's circles in the 1880s,
            is not known. The trill is the conservative choice and is the r Siebs prescribed.
          - st and sp at the start of a morpheme are [ʃt] and [ʃp] (Stand, verstehen, Sprung),
            elsewhere [st] and [sp] (ist, Fenster). The [st] of Hamburg and Hanover (the
            "s-pitze S-tein") is a northwestern feature and is not modelled.
          - long ä is [ɛː], kept apart from long e [eː]: a reading pronunciation that follows the
            spelling. Many northern speakers merged long ä with long e, and either value may have
            been heard; the evidence does not decide between them for these two speakers.
          - vowel length is that of the modern language. Where 18th- or 19th-century length is
            known to differ for a word, the lexicon says so.
          Evidence: the descriptions collected in the historical grammars and histories of the
          standard pronunciation (Viëtor, Die Aussprache des Schriftdeutschen, 1885 and later
          editions; Siebs, Deutsche Bühnenaussprache, 1898, which records the northern usage it
          set aside; von Polenz, Deutsche Sprachgeschichte, volumes 2 and 3, 1994-1999).
          Not modelled: the glottal stop before initial vowels; any East Prussian features of
          Kant's own speech, for which the scheme has no reliable description; the Central German
          features of Nietzsche's home region (the
          merger of p and b, t and d, the unrounding of ü and ö), which educated reading avoided
          and for which there is no testimony about his own speech. There are no recordings of
          either author.
modern    Standard German today (as in the Duden Aussprachewörterbuch), each word said alone: the r
          after a long vowel and the ending -er are vocalized ([ɐ]); r at the start of a syllable
          and after a short vowel is uvular [ʁ]; g at the end of a syllable is [k] except in the
          ending -ig ([ɪç]); long ä is [ɛː].

Luther's Bible (luther-bible: John 1:1-14 and Psalm 23 in the Wittenberg edition of 1545)
-----------------------------------------------------------------------------------------
The third work is Early New High German of the 1540s, and its first scheme is not computed from
the modern spelling. Each token may give, in o, its 1545 form normalized for reading: the letters
u/v and i/j by their sound value (vnd: und, jmerdar: imerdar, Awen: auen), long s as s, the
doubled s before ch (frisschen: frischen) reduced, and the form itself kept (gleuben, Heubt, on,
wonet, Liecht). Without o the form is derived from the printed word by those rules (old_form).
The modern scheme is computed from n, as for Kant and Nietzsche. Lexicon entries are keyed by both
the modern spellings and the old forms.

ecg1545   East Central German as spoken and read in Wittenberg in the 1540s (the Saxon chancery
          language and the spoken German of Electoral Saxony), approximate. Evidence: Luther's own
          spelling in the 1545 Bible, which follows the Saxon chancery usage he said he followed;
          the spellings of the region; the reading and spelling books of the period, which
          describe the letters by their sounds (Valentin Ickelsamer, Die rechte weis aufs kürtzist
          lesen zu lernen, 1527, and Ein Teütsche Grammatica, about 1534; Fabian Frangk,
          Orthographia, 1531, which names Luther's prints and the chancery of Emperor Maximilian
          as models); and the histories of the language (von Polenz, Deutsche Sprachgeschichte,
          volume 1, 2nd edition 2000; Besch, Luther und die deutsche Sprache, 2014). Features
          modelled:
          - the new diphthongs: MHG î, û, iu were already ei, au, eu in East Central German, as
            Luther's spelling shows (bey, sein, Hause, auff for MHG bî, sîn, hûs, ûf). Their values
            are given as [aɪ], [aʊ], [ɔʏ]; the first element may have been closer ([ɛɪ], [ɔʊ]),
            and the old ei and the new one may still have differed in parts of the region. The
            scheme does not decide this.
          - the old diphthongs ie, uo, üe were long monophthongs in Central German; Luther's ie
            (Liecht, nie) is read as long [iː], as the spelling suggests. Modern Licht has a
            short vowel; when the shortening came is uncertain.
          - the Central German weakening of the stops: p and t at the start of a syllable are
            said as the unaspirated lenis stops of the region, written b and d (Tal: daal,
            trösten: drös-den, Vater: faa-duhr). Luther's spellings Deudsch and Heubt (Haupt)
            reflect the merger. It is not applied in st and sp at the start of a word part
            (Stab, Strasse), nor in pf, ps or z (ts).
          - w is a bilabial [β], between English w and v; the labiodental [v] of the modern
            language spread later. The timing is uncertain.
          - r is a tongue-tip trill; g at the end of a syllable after a vowel is a fricative, as in
            the northern scheme; final b d g s are voiceless.
          - the final -e that Luther keeps (Hause, Gnade, Seele) is said.
          Not modelled: the unrounding of ü, ö and eu to i, e and ei, which the dialects of Upper
          Saxony show and which the histories date to the late Middle Ages in the region. Luther's
          prints keep ü and ö (Geblüt, trösten), and the scheme follows the print, as a reading
          of Scripture likely would; how far unrounding reached such a reading is not known.
          Vowel length follows the modern word unless the old form says otherwise. There is no
          description of Luther's own speech specific enough to model.

A ˌ before a syllable in the lexicon keeps its full vowel without the main stress (the second
element of a compound: ˈsin.nen.ˌwelt); such syllables are not written in capitals.

Stress falls on the syllable the lexicon marks (ˈ). Native words stress the root; be-, ge-, er-,
ver-, zer-, ent- and emp- are unstressed; separable prefixes (auf-, aus-, ab-, an-, ein-, vor-,
zu-) are stressed; loans keep the stress of their source (Natur, Publikum, Persönlichkeit). The same
stress is used in both schemes. Monosyllabic function words (articles, pronouns, prepositions,
conjunctions) are written without capitals.

Edition token fields (texts/<work>/edition.yaml)
-----------------------------------------------
t      the word as printed, punctuation attached ("Muth,", "Mensch. —"); the punctuation moves to
       punct, an opening quotation mark or dash to lead
n      the modern spelling of the same form, German capitalization kept (Mut, Gemüt, dreißig)
src    the source's reading of this token where it differs from t: an OCR misreading, or a
       transcription that prints a space the edition does not (see line_checks)
ipa    {scheme: ipa} override for this occurrence

Section field (edition.yaml): `check: {file, format}` names the source the section's lines are
compared against, for sources that verify_in cannot read: `dta-tei` (a Deutsches Textarchiv TEI
file, read with long s, the superscript e of the umlauts, line-end hyphens and running heads
normalized) or `plain` (an OCR text); `strip`, a regular expression removed from the source first
(running page numbers).
"""
from __future__ import annotations

import html
import re
import unicodedata as ud
from pathlib import Path

import yaml

VERSION = "0.1"
SHOW_TRANSLIT = True
TRANSLIT_LABEL = "Modern spelling"

LEAD_P = re.compile(r"^([„“‚‘»«(\[—–]+\s?)")
TRAIL_P = re.compile(r"((?:\s?[—–]|\s?/|[,.;:!?)\]“”‘’«»])+)$")   # / is Luther's virgule
ABBR = re.compile(r"^\w(\.\w)+\.$")          # u.s.w. keeps its points

_LEX: dict | None = None
NORTHLIKE = ("northern", "ecg1545")   # trilled r, fricative g at the end of a syllable
_CTX: dict = {}

# monosyllables said without stress in running text; every other monosyllable is stressed
UNSTRESSED = {"der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem", "einer",
              "eines", "und", "oder", "aber", "als", "wie", "zu", "zum", "zur", "in", "im", "an",
              "am", "auf", "aus", "von", "vom", "mit", "bei", "nach", "für", "vor", "über", "um",
              "durch", "bis", "ob", "dass", "daß", "wenn", "denn", "doch", "ja", "so", "es", "er",
              "sie", "ich", "du", "wir", "ihr", "ihn", "ihm", "ihnen", "mich", "mir", "dich", "dir",
              "sich", "uns", "euch", "man", "sein", "seine", "seiner", "seinen", "seinem", "mein",
              "meine", "meiner", "meinen", "meinem", "dein", "deine", "deiner", "deinen", "deines",
              "seines", "meines", "ihre", "ihrer", "ihren", "nicht", "noch", "nur", "schon", "wohl",
              "da", "dort", "hier", "je", "wo", "was", "wer", "hat", "ist", "sind", "war", "wird",
              "hin", "nun", "dann",
              "bey", "auff", "umb"}             # Luther's 1545 forms of bei, auf, um


def lexicon() -> dict:
    global _LEX
    if _LEX is None:
        p = Path(__file__).parent / "data" / "de_lexicon.yaml"
        _LEX = {ud.normalize("NFC", str(k)): v for k, v in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).items()}
    return _LEX


def key(word: str) -> str:
    return ud.normalize("NFC", word.replace("’", "'")).lower()


# ---------------------------------------------------------------- spelling -> syllables
VOWEL_G = ["äu", "eu", "ei", "ey", "ai", "ay", "au", "ie", "aa", "ee", "oo",
           "a", "e", "i", "o", "u", "ä", "ö", "ü", "y"]
CONS_G = ["tsch", "sch", "ch", "ck", "tz", "ph", "th", "qu", "ng", "pf", "dt", "ß", "ss",
          "b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r", "s", "t", "v", "w",
          "x", "z", "-", "'"]
ONSETS = {"bl", "br", "dr", "fl", "fr", "gl", "gn", "gr", "kl", "kn", "kr", "pl", "pr", "tr", "schl",
          "schm", "schn", "schr", "schw", "sp", "spr", "st", "str", "zw", "pfl", "pfr", "kw", "qu"}
FRONT_V = ("i", "e", "ä", "ö", "ü", "y", "ie", "ee", "ei", "ey", "ai", "ay", "eu", "äu")
BACK_V = ("a", "o", "u", "aa", "oo", "au")


def graphemes(s: str) -> list[tuple[str, str]]:
    """Split a spelling into (grapheme, 'V', 'C' or ':')."""
    out, i = [], 0
    while i < len(s):
        if s[i] == ":":
            out.append((":", ":")); i += 1; continue
        for g in VOWEL_G:
            if s.startswith(g, i):
                out.append((g, "V")); i += len(g); break
        else:
            for g in CONS_G:
                if s.startswith(g, i):
                    out.append((g, "C")); i += len(g); break
            else:
                out.append((s[i], "C")); i += 1
    return out


def syllabify_rule(word: str) -> list[str]:
    """Rule division, used only when the lexicon has no entry: one consonant goes to the next
    syllable; of a cluster, the longest permitted onset; ch, sch, ck and ng stay whole."""
    gs = graphemes(word)
    vidx = [k for k, (_, t) in enumerate(gs) if t == "V"]
    if len(vidx) < 2:
        return [word]
    cuts = []
    for a, b in zip(vidx, vidx[1:]):
        cl = [g for g, _ in gs[a + 1:b]]
        if not cl:
            cuts.append(b); continue
        take = 0 if cl[-1] in ("ng", "ck") and len(cl) == 1 else 1
        for n in range(len(cl), 1, -1):
            if "".join(cl[-n:]) in ONSETS:
                take = n; break
        cuts.append(b - take)
    sylls, start = [], 0
    for c in cuts:
        sylls.append("".join(g for g, _ in gs[start:c])); start = c
    sylls.append("".join(g for g, _ in gs[start:]))
    return sylls


def lex_entry(word: str) -> tuple[list[str], int | None, dict]:
    """(syllables, index of the stressed syllable or None, per-scheme IPA overrides)."""
    k = key(word)
    e = lexicon().get(k)
    over = {}
    if isinstance(e, dict):
        over = {s: v for s, v in e.items() if s in ("northern", "modern", "ecg1545")}
        e = e.get("syl")
    if isinstance(e, str):
        sylls = e.split(".")
        st = next((i for i, s in enumerate(sylls) if s.startswith("ˈ")), None)
        return [s.lstrip("ˈ") for s in sylls], st, over
    sylls = syllabify_rule(k)
    if len(sylls) == 1:
        return sylls, (None if k in UNSTRESSED else 0), over
    st = 1 if sylls[0] in ("be", "ge", "er", "ver", "zer", "ent", "emp") else 0
    return sylls, st, over


# ---------------------------------------------------------------- syllable -> IPA
LONG = {"a": "aː", "e": "eː", "i": "iː", "o": "oː", "u": "uː", "ä": "ɛː", "ö": "øː", "ü": "yː", "y": "yː",
        "aa": "aː", "ee": "eː", "oo": "oː", "ie": "iː"}
SHORT = {"a": "a", "e": "ɛ", "i": "ɪ", "o": "ɔ", "u": "ʊ", "ä": "ɛ", "ö": "œ", "ü": "ʏ", "y": "ʏ",
         "aa": "a", "ee": "e", "oo": "o", "ie": "i"}
TENSE = {"a": "a", "e": "e", "i": "i", "o": "o", "u": "u", "ä": "ɛ", "ö": "ø", "ü": "y", "y": "y",
         "aa": "a", "ee": "e", "oo": "o", "ie": "i"}
DIPH = {"ei": "aɪ", "ey": "aɪ", "ai": "aɪ", "ay": "aɪ", "au": "aʊ", "eu": "ɔʏ", "äu": "ɔʏ"}


def nucleus(v: str, stressed: bool, long_mark: bool, closed: bool, first: bool, coda: str, scheme: str) -> str:
    if v in DIPH:
        return DIPH[v]
    if v in ("aa", "ee", "oo", "ie") or long_mark:
        return LONG[v]
    if stressed:
        return SHORT[v] if closed else LONG[v]
    if v == "e":
        if first and coda:
            return "ɛ"                     # ent-, emp-, er-, ver-, zer-, ex-: a full vowel
        if coda.startswith("r"):
            return "ə"                     # -er, -ern, -ers: the r is handled with the coda
        return "ə"
    return SHORT[v] if closed else TENSE[v]


def consonant(c: str, scheme: str, coda: bool, prev_v: str, nxt: str, morph_initial: bool) -> str:
    if c == "c":
        return "ts" if nxt[:1] in ("e", "i", "ä", "y") else "k"
    if c == "ch":
        return "x" if prev_v in BACK_V else "ç"
    if c == "g" and coda:
        if scheme in NORTHLIKE and prev_v:
            return "x" if prev_v in BACK_V else "ç"
        return "k"
    if c == "s":
        return "s" if coda or nxt in ("", "C") else "z"
    if c == "r":
        return "r" if scheme in NORTHLIKE else "ʁ"
    m = {"sch": "ʃ", "tsch": "tʃ", "ck": "k", "tz": "ts", "z": "ts", "ph": "f", "th": "t", "qu": "kv",
         "ng": "ŋ", "pf": "pf", "dt": "t", "ß": "s", "ss": "s", "v": "f", "w": "v", "x": "ks",
         "j": "j", "-": "", "'": ""}
    out = m.get(c, c)
    if coda:
        out = {"b": "p", "d": "t", "v": "f", "z": "s"}.get(out, out) if c in ("b", "d") else out
    return out


def syllable_ipa(syl: str, scheme: str, stressed: bool, first: bool, last: bool, prev_v: str,
                 prev_stressed: bool, prev_open: bool, nxt_onset: str, mono: bool = False,
                 prev_long: bool = False) -> tuple[str, str]:
    """IPA of one syllable, and its vowel grapheme (for ch and g in the next syllable)."""
    gs = graphemes(syl)
    vi = next((k for k, (_, t) in enumerate(gs) if t == "V"), None)
    if vi is None:
        return "".join(consonant(g, scheme, True, prev_v, "", False) for g, t in gs if t == "C"), prev_v
    onset = [g for g, _ in gs[:vi]]
    v = gs[vi][0]
    rest = gs[vi + 1:]
    long_mark = False
    if rest and rest[0][1] == ":":
        long_mark = True; rest = rest[1:]
    # h after a vowel in the same syllable marks length and is silent
    if rest and rest[0][0] == "h":
        long_mark = True; rest = rest[1:]
    coda = []
    for g, _ in rest:                     # a doubled letter in the coda is one sound (kommt)
        if not (coda and coda[-1] == g):
            coda.append(g)
    coda_s = "".join(coda)
    out = ""
    for k, g in enumerate(onset):
        nx = onset[k + 1] if k + 1 < len(onset) else v
        if g == "h" and k == 0 and len(onset) == 1 and prev_open and (prev_stressed or prev_long) and v in ("e", "i"):
            continue                      # gehen, drohet, ruhig: the h between vowels is silent
        if g == "s" and k == 0 and len(onset) > 1 and onset[1] in ("t", "p"):
            out += "ʃ"; continue          # st, sp at the start of a morpheme
        if g == "r" and scheme == "modern":
            out += "ʁ"; continue
        out += consonant(g, scheme, False, prev_v, "V" if nx == v else "C", k == 0)
    nuc = nucleus(v, stressed, long_mark, bool(coda), first, coda_s, scheme)
    if nuc == "i" and not stressed and v == "i" and nxt_onset[:1] not in ("", "a", "e", "i", "o", "u", "ä", "ö", "ü"):
        nuc = "ɪ"                         # ruhigen, heiligen: lax, except before a vowel (Materie)
    out += nuc
    cod = ""
    for k, g in enumerate(coda):
        nx = coda[k + 1] if k + 1 < len(coda) else ""
        if g == "n" and (nx in ("k", "ck") or (not nx and nxt_onset[:1] == "k")):
            cod += "ŋ"; continue
        if g == "r":
            if scheme in NORTHLIKE:
                cod += "r"
            elif nuc == "ə":
                out = out[:-1] + "ɐ"      # -er: one vocalized vowel
            elif nuc.endswith("ː") or (first and not stressed and not mono):
                cod += "ɐ"                # der, mir; the prefixes er-, ver-, zer-
            else:
                cod += "ʁ"
            continue
        if g == "g":
            if scheme == "modern":
                cod += "ç" if (v == "i" and not stressed) else "k"
            else:
                cod += "k" if k > 0 and coda[k - 1] in ("l", "r", "n") else ("x" if v in BACK_V else "ç")
            continue
        if g == "ch" and k == 0:
            cod += "x" if v in BACK_V else "ç"; continue
        if g == "ch":
            cod += "ç"; continue
        cod += consonant(g, scheme, True, v, nx, False)
    return out + cod, v


def word_ipa(word: str, scheme: str) -> tuple[str, int, bool]:
    """(ipa, syllable count, from_lexicon)."""
    k = key(word)
    sylls, st, over = lex_entry(word)
    if over.get(scheme):
        ipa = over[scheme]
        return ipa, len(ipa.split(".")), True
    parts = []
    prev_v, prev_stressed, prev_open, prev_long = "", False, False, False
    # ˌ marks a syllable that keeps a full vowel without the main stress (the second element of
    # a compound: Sinnen-ˌwelt); it is not written in capitals
    sec = {i for i, x in enumerate(sylls) if x.startswith("ˌ")}
    sylls = [x.lstrip("ˌ") for x in sylls]
    for i, s in enumerate(sylls):
        nxt = sylls[i + 1] if i + 1 < len(sylls) else ""
        if nxt and s.endswith("s") and nxt.startswith("s") and not nxt.startswith(("sch", "st", "sp")):
            sylls[i + 1] = nxt = "ß" + nxt[1:]      # Wasser, müssen: a doubled s is voiceless
        # a monosyllable has the vowel of its stressed citation form, capitals or not
        mono = len(sylls) == 1
        # a function word written without stress keeps the vowels of its citation form
        vst = st if st is not None else 0
        ip, v = syllable_ipa(s, scheme, i == vst or mono or i in sec, i == 0, i == len(sylls) - 1, prev_v, prev_stressed,
                             prev_open, nxt, mono, prev_long)
        # a doubled consonant letter (Mutter, hatten) is one consonant: said once, at the start
        # of the next syllable
        if nxt and (s[-1:] == nxt[:1] or (s[-1:] == "s" and nxt[:1] == "ß")) and s[-1:] not in "aeiouäöüy" and len(ip) > 1 and ip[-1] != "ɐ":
            ip = ip[:-1]
        parts.append(("ˈ" if i == st and len(sylls) > 1 else "") + ip)
        prev_v, prev_stressed, prev_long = v, i == vst, s.endswith(":")
        prev_open = s[-1:] in "aeiouäöüy" or s.endswith(":") or (s.endswith("h") and len(s) > 1 and s[-2] in "aeiouäöüy")
    if len(sylls) == 1 and st is not None:
        parts[0] = "ˈ" + parts[0]
    ipa = ".".join(parts)
    if scheme == "ecg1545":
        ipa = ecg_lenis(ipa)
    return ipa, len(sylls), k in lexicon()


def ecg_lenis(ipa: str) -> str:
    """East Central German of the 1540s: p and t at the start of a syllable are the unaspirated
    lenis stops b and d (not after s or sch, and not in pf or ts); w is bilabial."""
    ipa = re.sub(r"(^|[.ˈ ])t(?![sʃ])", r"\1d", ipa)
    ipa = re.sub(r"(^|[.ˈ ])p(?![fs])", r"\1b", ipa)
    return ipa.replace("v", "β")


# ---------------------------------------------------------------- IPA -> respelling
RESPELL = [("aːɐ", "aa"), ("aɪ", "ai"), ("aʊ", "ow"), ("ɔʏ", "oy"), ("tʃ", "tch"), ("ts", "ts"), ("pf", "pf"),
           ("aː", "aa"), ("eː", "ay"), ("ɛː", "eh"), ("iː", "ee"), ("oː", "oh"), ("uː", "oo"),
           ("yː", "üü"), ("øː", "öö"), ("a", "ah"), ("ɛ", "e"), ("e", "ay"), ("ɪ", "i"), ("i", "ee"),
           ("ɔ", "o"), ("o", "oh"), ("ʊ", "u"), ("u", "oo"), ("ʏ", "ü"), ("y", "ü"), ("œ", "ö"),
           ("ø", "ö"), ("ə", "uh"), ("ɐ", "a"), ("ç", "hy"), ("x", "kh"), ("ʃ", "sh"), ("ʒ", "zh"),
           ("ŋ", "ng"), ("ʁ", "r"), ("j", "y"), ("ɡ", "g"), ("β", "w")]


def respell_syl(s: str) -> str:
    out, i = "", 0
    while i < len(s):
        for a, b in RESPELL:
            if s.startswith(a, i):
                out += b; i += len(a); break
        else:
            out += s[i]; i += 1
    return out


def respell(ipa: str) -> str:
    words = []
    for w in ipa.split(" "):
        sy = []
        for s in w.split("."):
            r = respell_syl(s.lstrip("ˈ"))
            sy.append(r.upper() if s.startswith("ˈ") else r)
        words.append("-".join(sy))
    return " ".join(words)


# ---------------------------------------------------------------- Luther: the 1545 form
def old_form(word: str) -> str:
    """The printed 1545 word normalized for reading: u/v and i/j by sound value, aw and ew as au
    and eu, ssch as sch, lowercased. The form is kept (gleuben, Heubt, on)."""
    w = ud.normalize("NFC", word).lower().replace("ſ", "s")
    w = re.sub(r"v(?![aeiouäöüy])", "u", w)            # vnd, vmb, vnter, dv: u
    w = re.sub(r"^j(?=[^aeiouäöüy])", "i", w)           # jm, jr, jmerdar: i
    w = w.replace("aw", "au").replace("ew", "eu").replace("ssch", "sch")
    return w


# ---------------------------------------------------------------- language hooks
def token_fields(surface: str, et: dict, group: dict) -> tuple[dict, list[tuple[str, str]]]:
    """Split punctuation off the printed word, check every polysyllable against the lexicon, and
    hold the token's ipa override for phonemize, which draft calls next for this token."""
    global _CTX
    fields: dict = {}
    fails: list[tuple[str, str]] = []
    word = surface
    ml = LEAD_P.search(word)
    if ml:
        fields["lead"] = ml.group(1)
        word = word[ml.end():]
    if not ABBR.match(word):
        mt = TRAIL_P.search(word)
        if mt:
            fields["punct"] = mt.group(1)
            word = word[:mt.start()]
    if word != surface:
        fields["surface"] = word
    n = et.get("n")
    if not n:
        fails.append(("modern-spelling-missing", surface))
    else:
        for w in n.split():
            sylls, _, over = lex_entry(w)
            if len(sylls) > 1 and key(w) not in lexicon() and not et.get("ipa"):
                fails.append(("syllables-by-rule", w))
    # an edition with an old-form scheme (ecg1545) reads the 1545 form: o, or derived from the print
    o = None
    if group.get("old_forms") or et.get("o"):
        o = et.get("o") or old_form(word)
        fields["old"] = o
        for w in o.split():
            sylls, _, over = lex_entry(w)
            if len(sylls) > 1 and key(w) not in lexicon() and not (et.get("ipa") or {}).get("ecg1545"):
                fails.append(("old-form-syllables-by-rule", w))
    _CTX = {"n": n, "ipa": et.get("ipa") or {}, "o": o}
    return fields, fails


def phonemize(word: str, scheme: str = "northern", quantities=None, **_) -> dict:
    """`word` is the token's modern spelling (n); a group written apart is said word by word."""
    ov = (_CTX.get("ipa") or {}).get(scheme) if _CTX.get("n") == word else None
    if ov:
        return {"ipa": ov, "respell": respell(ov), "syllables": len(re.split(r"[. ]", ov))}
    if scheme == "ecg1545" and _CTX.get("o") and _CTX.get("n") == word:
        word = _CTX["o"]                  # the 1545 form, not the modern spelling
    parts, n = [], 0
    for w in word.split():
        if ABBR.match(w):
            continue
        ipa, k, _ = word_ipa(w.strip(".,;:!?"), scheme)
        parts.append(ipa); n += k
    ipa = " ".join(parts)
    return {"ipa": ipa, "respell": respell(ipa), "syllables": n}


# ---------------------------------------------------------------- source sensor
_SRC: dict[str, str] = {}


def normalize_dta(xml: str) -> str:
    """A DTA TEI file as running text: body only; running heads, catchwords and signatures
    dropped; long s, the superscript e of the umlauts (aͤ) and line-end hyphens normalized."""
    body = xml[xml.find("<body"):]
    body = re.sub(r"<fw\b[^>]*>.*?</fw>", "", body, flags=re.S)
    body = re.sub(r"<note\b[^>]*>.*?</note>", "", body, flags=re.S)
    body = re.sub(r"[-¬]\s*<lb/>\s*", "", body)
    body = re.sub(r"<[^>]+>", " ", body)
    body = html.unescape(body)
    body = body.replace("ſ", "s")
    body = body.replace("aͤ", "ä").replace("oͤ", "ö").replace("uͤ", "ü")
    body = body.replace("Aͤ", "Ä").replace("Oͤ", "Ö").replace("Uͤ", "Ü")
    return ud.normalize("NFC", body)


def normalize_textgrid(xml: str) -> str:
    """A TextGrid Digitale Bibliothek TEI file (the Zeno.org text) as running text: body only;
    the verse numbers and note anchors (ref type="noteAnchor") dropped, tags removed."""
    body = xml[xml.find("<body"):]
    body = re.sub(r'<ref type="noteAnchor"[^>]*>.*?</ref>', "", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return ud.normalize("NFC", html.unescape(body))


def source_text(path: Path, fmt: str, strip: str | None = None) -> str:
    k = f"{path}|{fmt}|{strip}"
    if k not in _SRC:
        raw = path.read_text(encoding="utf-8")
        txt = (normalize_dta(raw) if fmt == "dta-tei" else normalize_textgrid(raw) if fmt == "textgrid-tei"
               else ud.normalize("NFC", raw))
        if strip:                          # running page numbers inside an OCR text
            txt = re.sub(strip, "", txt)
        _SRC[k] = re.sub(r"\s+", "", txt)
    return _SRC[k]


def line_checks(text: str, etoks: list[dict], edition: dict) -> list[tuple[str, str]]:
    """Sensor: for a section with `check`, the line, with each token's declared source reading
    (src) in place of the printed word, must occur in the source, compared without spaces
    (edition-not-in-source otherwise)."""
    sec = next((g for g in edition.get("sections", []) for ln in g["lines"]
                if not isinstance(ln, str) and ln.get("tokens") is etoks), None)
    chk = (sec or {}).get("check")
    if not chk:
        return []
    from .paths import work_dir
    p = work_dir(Path(__file__).resolve().parents[2], edition["work"]) / chk["file"]
    if not p.exists():
        return [("source-missing", chk["file"])]
    src = source_text(p, chk.get("format", "plain"), chk.get("strip"))
    want = re.sub(r"\s+", "", "".join(t.get("src") or t["t"] for t in etoks))
    if want not in src:
        return [("edition-not-in-source", " ".join(t["t"] for t in etoks[:4]) + " ...")]
    return []


KEY = {
    "ecg1545": [
        ("", "East Central German as spoken and read in Wittenberg in the 1540s, approximate: reconstructed from Luther's spelling, the Saxon chancery usage, the reading books of the period and the histories of the language. Computed from the 1545 form of each word, not from the modern spelling."),
        ("CAPS", "the stressed syllable; hyphens divide syllables. Small words (der, vnd, zu, jm) are unstressed"),
        ("uh", "the reduced vowel of unstressed syllables (ə), as in the a of about; Luther's final -e is said (Hause, HOW-zuh)"),
        ("-uhr", "the ending -er, with its r sounded"),
        ("aa ay eh ee oh oo", "long vowels: a as in father, ay as in say without a glide, eh a long e as in bed, ee as in see, oh as in so without a glide, oo as in too. Luther's ie (Liecht) is a long ee"),
        ("ah e i o u", "short vowels: ah a short a, e as in bed, i as in bit, o as in pot, u as in put"),
        ("ü üü", "say ee with rounded lips (short and long); the print keeps these, though the spoken dialect of the region may already have unrounded them to ee"),
        ("ö öö", "say ay with rounded lips (short and long); the same caution applies"),
        ("ai ow oy", "ei and ey (as in aisle), au and aw (as in how), eu (as in boy). Their exact values in the 1540s are uncertain"),
        ("b d", "also p and t at the start of a syllable (Tal, DAAL; Vater, FAA-duhr): the soft, unaspirated stops of Central German, where p and b, t and d were not kept apart. Not in st and sp at the start of a word part (Stab, Strasse), nor in pf, ps and z"),
        ("w", "the letter w: a w made with both lips, between English w and v"),
        ("hy", "ch after front vowels (Liecht): the h of huge. Also g at the end of a syllable after a front vowel"),
        ("kh", "ch after a, o, u (auch): the ch of Scottish loch. Also g at the end of a syllable after a back vowel"),
        ("sh", "sch, and the s of st and sp at the start of a word or word part (Stab, Strasse)"),
        ("ts", "z and tz"),
        ("z", "s before a vowel (Seele, sein), as in zoo"),
        ("f", "f and v (Vater, vol)"),
        ("r", "a trilled r with the tip of the tongue, in every position"),
        ("y", "j before a vowel (Jesus); j before a consonant is the vowel i (jm, IM)"),
    ],
    "northern": [
        ("", "Educated northern German before the stage norm of 1898, approximate: reconstructed from the grammarians and pronunciation handbooks of the period. The label above gives the time and place modelled for this work."),
        ("CAPS", "the stressed syllable; hyphens divide syllables. Small words (der, und, zu, ich) are unstressed"),
        ("uh", "the reduced vowel of unstressed syllables (ə), as in the a of about"),
        ("-uhr", "the ending -er, with its r sounded"),
        ("aa ay eh ee oh oo", "long vowels: a as in father, ay as in say without a glide, eh a long e as in bed, ee as in see, oh as in so without a glide, oo as in too"),
        ("ah e i o u", "short vowels: ah a short a, e as in bed, i as in bit, o as in pot, u as in put"),
        ("ü üü", "say ee with rounded lips (short and long)"),
        ("ö öö", "say ay with rounded lips (short and long)"),
        ("ai ow oy", "ei (as in aisle), au (as in how), eu and äu (as in boy)"),
        ("hy", "ch after front vowels (ich, Gemüth): the h of huge. Also g at the end of a syllable after a front vowel (Weg, wenig)"),
        ("kh", "ch after a, o, u (auch, Nacht): the ch of Scottish loch. Also g at the end of a syllable after a back vowel (Tag, trug)"),
        ("sh", "sch, and the s of st and sp at the start of a word or word part (Stand, verstehen)"),
        ("ts", "z and tz"),
        ("z", "s before a vowel (sein, Seele), as in zoo"),
        ("v", "w (Welt, wenn); the letter v is f"),
        ("r", "a trilled r with the tip of the tongue, in every position"),
        ("y", "j (ja, jeder)"),
    ],
    "modern": [
        ("", "Standard German today, each word said alone."),
        ("CAPS", "the stressed syllable; hyphens divide syllables. Small words (der, und, zu, ich) are unstressed"),
        ("uh", "the reduced vowel of unstressed syllables (ə), as in the a of about"),
        ("a", "a final -er, and an r after a long vowel: a short vowel between uh and ah, the r not sounded (Vater, FAA-ta; der, DAYa)"),
        ("aa ay eh ee oh oo", "long vowels: a as in father, ay as in say without a glide, eh a long e as in bed, ee as in see, oh as in so without a glide, oo as in too"),
        ("ah e i o u", "short vowels: ah a short a, e as in bed, i as in bit, o as in pot, u as in put"),
        ("ü üü", "say ee with rounded lips (short and long)"),
        ("ö öö", "say ay with rounded lips (short and long)"),
        ("ai ow oy", "ei (as in aisle), au (as in how), eu and äu (as in boy)"),
        ("hy", "ch after front vowels (ich), and the -ig ending: the h of huge"),
        ("kh", "ch after a, o, u (auch, Nacht): the ch of Scottish loch"),
        ("sh", "sch, and the s of st and sp at the start of a word or word part"),
        ("ts", "z and tz"),
        ("z", "s before a vowel, as in zoo"),
        ("v", "w; the letter v is f"),
        ("r", "the uvular r, at the back of the throat, at the start of a syllable and after a short vowel"),
        ("y", "j (ja, jeder)"),
    ],
}
SCHEME_LABELS = {"northern": "Educated northern German before the stage norm (approximate)",
                 "modern": "Modern Standard German",
                 "ecg1545": "East Central German of the 1540s, Wittenberg (approximate)"}
