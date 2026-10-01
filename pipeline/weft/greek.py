"""Ancient Greek orthography -> syllables -> IPA and respelling, per pronunciation scheme.

Deterministic rules only. The one input the orthography does not carry is the length of
alpha, iota and upsilon; that comes from a quantity table (``data/grc_quantities.yaml``),
keyed by the unaccented-insensitive surface form, which writes macrons onto the long ones.

Schemes
-------
restored  Scholarly reconstruction of 5th-century Attic (after W. S. Allen, *Vox Graeca*),
          the classroom "restored" pronunciation. Accent is pitch: acute and circumflex
          syllables are raised; a grave marks a suppressed rise and is not raised.
erasmian  The traditional English-speaking classroom scheme. Every written accent,
          grave included, is read as stress.
"""
from __future__ import annotations

import unicodedata as ud
from dataclasses import dataclass, field

VERSION = "0.1"

PSILI, DASIA = "̓", "̔"
ACUTE, GRAVE, CIRC = "́", "̀", "͂"
IOTA_SUB, DIAER, MACRON, BREVE = "ͅ", "̈", "̄", "̆"
ACCENTS = {ACUTE: "acute", GRAVE: "grave", CIRC: "circ"}

VOWELS = set("αεηιουω")
DIPHTHONGS = {"αι", "ει", "οι", "υι", "αυ", "ευ", "ηυ", "ου", "ωυ"}
ELISION_MARKS = "'’ʼ᾽᾿"
PUNCT = ",.·;:!?—()[]·;"
# Medial clusters that go whole to the following syllable: stop + liquid (muta cum liquida).
ONSETS = {a + b for a in "πβφτδθκγχ" for b in "ρλ"}


@dataclass
class Letter:
    base: str
    marks: set[str] = field(default_factory=set)


@dataclass
class Syllable:
    onset: list[Letter]
    nucleus: list[Letter]
    coda: list[Letter]
    rough: bool = False

    @property
    def accent(self) -> str | None:
        for l in self.nucleus:
            for m, name in ACCENTS.items():
                if m in l.marks:
                    return name
        return None

    @property
    def key(self) -> str:
        return "".join(l.base for l in self.nucleus)

    @property
    def long(self) -> bool:
        if len(self.nucleus) > 1:
            return True
        l = self.nucleus[0]
        if l.base in "ηω":
            return True
        if l.base in "εο":
            return False
        return bool(l.marks & {CIRC, IOTA_SUB, MACRON})

    @property
    def subscript(self) -> bool:
        return any(IOTA_SUB in l.marks for l in self.nucleus)


def normalize_elision(s: str) -> str:
    """Unify the several apostrophes editions and treebanks use for elision into U+2019."""
    s = ud.normalize("NFD", s)
    out = []
    for i, ch in enumerate(s):
        if ch in ELISION_MARKS:
            out.append("’")
        elif ch == PSILI and i > 0 and ud.normalize("NFD", s[i - 1])[0].lower() not in VOWELS | {"ρ"}:
            out.append("’")  # treebank style: combining psili on a consonant = elision
        else:
            out.append(ch)
    return ud.normalize("NFC", "".join(out))


def letters(word: str) -> list[Letter]:
    out: list[Letter] = []
    for ch in ud.normalize("NFD", word):
        if ud.combining(ch):
            if out:
                out[-1].marks.add(ch)
        elif ch.lower() in VOWELS or ("α" <= ch.lower() <= "ω") or ch.lower() == "ς":
            out.append(Letter(ch.lower().replace("ς", "σ")))
    return out


def nuclei_split(ls: list[Letter]) -> list[list[Letter] | Letter]:
    """Group vowel letters into nuclei (diphthongs); consonants stay single."""
    seq: list = []
    i = 0
    while i < len(ls):
        l = ls[i]
        if l.base in VOWELS:
            nxt = ls[i + 1] if i + 1 < len(ls) else None
            if (
                nxt
                and l.base + nxt.base in DIPHTHONGS
                and DIAER not in nxt.marks
                and not (l.marks & {ACUTE, GRAVE, CIRC, PSILI, DASIA})
                and IOTA_SUB not in l.marks
            ):
                seq.append([l, nxt])
                i += 2
                continue
            seq.append([l])
        else:
            seq.append(l)
        i += 1
    return seq


def syllabify(word: str) -> list[Syllable]:
    seq = nuclei_split(letters(word))
    idx = [i for i, x in enumerate(seq) if isinstance(x, list)]
    if not idx:
        return []
    syls: list[Syllable] = []
    for n, vi in enumerate(idx):
        syls.append(Syllable(onset=[], nucleus=seq[vi], coda=[]))
    # initial consonants
    syls[0].onset = [x for x in seq[: idx[0]]]
    # final consonants
    syls[-1].coda = [x for x in seq[idx[-1] + 1 :]]
    # medial clusters
    for n in range(len(idx) - 1):
        cl = seq[idx[n] + 1 : idx[n + 1]]
        if not cl:
            continue
        if len(cl) >= 2 and cl[-2].base + cl[-1].base in ONSETS:
            cut = len(cl) - 2
        else:
            cut = len(cl) - 1
        syls[n].coda = cl[:cut]
        syls[n + 1].onset = cl[cut:]
    # breathing lives on the first nucleus
    first = syls[0]
    if any(DASIA in l.marks for l in first.nucleus):
        first.rough = True
    return syls


# ---------------------------------------------------------------- schemes
CONS = {
    "restored": {"β": "b", "γ": "ɡ", "δ": "d", "ζ": "zd", "θ": "tʰ", "κ": "k", "λ": "l",
                 "μ": "m", "ν": "n", "ξ": "ks", "π": "p", "ρ": "r", "σ": "s", "τ": "t",
                 "φ": "pʰ", "χ": "kʰ", "ψ": "ps"},
    "erasmian": {"β": "b", "γ": "ɡ", "δ": "d", "ζ": "dz", "θ": "θ", "κ": "k", "λ": "l",
                 "μ": "m", "ν": "n", "ξ": "ks", "π": "p", "ρ": "r", "σ": "s", "τ": "t",
                 "φ": "f", "χ": "x", "ψ": "ps"},
    "koine": {"β": "v", "γ": "ɣ", "δ": "ð", "ζ": "z", "θ": "θ", "κ": "k", "λ": "l",
              "μ": "m", "ν": "n", "ξ": "ks", "π": "p", "ρ": "r", "σ": "s", "τ": "t",
              "φ": "f", "χ": "x", "ψ": "ps"},
}
VOW = {
    "restored": {"α": ("a", "aː"), "ε": ("e", "e"), "η": ("ɛː", "ɛː"), "ι": ("i", "iː"),
                 "ο": ("o", "o"), "υ": ("y", "yː"), "ω": ("ɔː", "ɔː"),
                 "αι": "ai", "ει": "eː", "οι": "oi", "υι": "yi", "αυ": "au", "ευ": "eu",
                 "ηυ": "ɛːu", "ου": "uː", "ωυ": "ɔːu",
                 "ᾳ": "aːi", "ῃ": "ɛːi", "ῳ": "ɔːi"},
    "erasmian": {"α": ("a", "aː"), "ε": ("e", "e"), "η": ("ɛː", "ɛː"), "ι": ("i", "iː"),
                 "ο": ("o", "o"), "υ": ("y", "yː"), "ω": ("ɔː", "ɔː"),
                 "αι": "ai", "ει": "ei", "οι": "oi", "υι": "yi", "αυ": "au", "ευ": "eu",
                 "ηυ": "ɛːu", "ου": "uː", "ωυ": "ɔːu",
                 "ᾳ": "aː", "ῃ": "ɛː", "ῳ": "ɔː"},
    # first-century Koine: no vowel length; η, ι, ει, οι, υ narrowing; αυ, ευ with a consonant
    "koine": {"α": ("a", "a"), "ε": ("ɛ", "ɛ"), "η": ("e", "e"), "ι": ("i", "i"),
              "ο": ("o", "o"), "υ": ("y", "y"), "ω": ("o", "o"),
              "αι": "ɛ", "ει": "i", "οι": "y", "υι": "yi", "αυ": "av", "ευ": "ev",
              "ηυ": "ev", "ου": "u", "ωυ": "ou",
              "ᾳ": "a", "ῃ": "e", "ῳ": "o"},
}
# IPA segment -> respelling. Longest match first.
RESPELL = {
    "restored": [("aːi", "aai"), ("ɛːi", "êi"), ("ɔːi", "awi"), ("ɛːu", "êu"), ("ɔːu", "awu"),
                 ("aː", "aa"), ("ɛː", "ê"), ("eː", "ay"), ("iː", "ee"), ("yː", "üü"),
                 ("ɔː", "aw"), ("uː", "oo"), ("ai", "ai"), ("oi", "oy"), ("yi", "üi"),
                 ("au", "ow"), ("eu", "eu"),
                 ("tʰ", "tʰ"), ("pʰ", "pʰ"), ("kʰ", "kʰ"), ("r̥", "hr"),
                 ("a", "a"), ("e", "e"), ("i", "i"), ("o", "o"), ("y", "ü"),
                 ("ŋ", "ng"), ("ɡ", "g")],
    "erasmian": [("ɛːu", "ayoo"), ("ɔːu", "ohoo"),
                 ("aː", "aa"), ("ɛː", "ay"), ("iː", "ee"), ("yː", "üü"), ("ɔː", "oh"),
                 ("uː", "oo"), ("ai", "ai"), ("ei", "ay"), ("oi", "oy"), ("yi", "wee"),
                 ("au", "ow"), ("eu", "yoo"),
                 ("θ", "th"), ("x", "kh"),
                 ("a", "a"), ("e", "e"), ("i", "i"), ("o", "o"), ("y", "ü"),
                 ("ŋ", "ng"), ("ɡ", "g")],
    "koine": [("ɛ", "e"), ("e", "ay"), ("i", "ee"), ("y", "ü"), ("u", "oo"),
              ("θ", "th"), ("ð", "dh"), ("ɣ", "gh"), ("x", "kh"), ("ŋ", "ng"), ("j", "y")],
}
KEY = {
    "restored": [
        ("a / aa", "a as in father, short / held long"),
        ("e", "e as in pet"),
        ("ê", "long open e, as in air, held (η)"),
        ("ay", "long close e, as in French été, held, no glide (ει)"),
        ("i / ee", "i as in machine, short / long"),
        ("o", "o as in French mot, short"),
        ("aw", "long open o, as in awe (ω)"),
        ("oo", "oo as in food (ου)"),
        ("ü / üü", "French u, German ü: lips round, say ee (υ)"),
        ("ai, oy, ow, eu", "diphthongs: eye, boy, cow, e+oo"),
        ("tʰ pʰ kʰ", "t, p, k with a puff of breath: never th as in thin, never f"),
        ("t p k", "unaspirated, as in stop, spin, skin"),
        ("r", "tapped or trilled"),
        ("zd", "ζ: z then d, as in wisdom"),
        ("CAPS", "raised pitch on the acute or circumflex syllable, not stress; a grave is not raised"),
    ],
    "erasmian": [
        ("a / aa", "a as in father"),
        ("e", "e as in pet"),
        ("ay", "ay as in they (η and ει)"),
        ("i / ee", "i as in machine"),
        ("o / oh", "o as in obey / as in go (ω)"),
        ("oo", "oo as in food (ου)"),
        ("ü", "French u, German ü (υ); many US classrooms say oo"),
        ("ai, oy, ow, yoo", "diphthongs: aisle, boy, cow, feud"),
        ("th, f, kh", "θ as in thin, φ as in fun, χ as in Bach"),
        ("dz", "ζ as in adze"),
        ("CAPS", "stressed syllable: every written accent, grave included"),
    ],
}


SCHEME_LABELS = {
    "restored": "Restored: reconstructed classical pitch accent",
    "erasmian": "Erasmian: traditional classroom stress",
    "koine": "Koine: Greek as spoken in the first century (after Randall Buth)",
}
KEY["koine"] = [
    ("a, e, o", "pure short vowels: father, pet, pot; length no longer matters"),
    ("ay", "η: a close e, as in French été"),
    ("ee", "ι and ει: as in machine"),
    ("ü", "υ and οι: French u, German ü"),
    ("oo", "ου: as in food"),
    ("av, ev", "αυ, ευ: the υ has become a consonant"),
    ("v, gh, dh", "β, γ, δ are soft: v, a breathy g, th as in this"),
    ("y", "γ before e and i sounds: as in yes"),
    ("th, f, kh", "θ, φ, χ: thin, fun, Bach"),
    ("z", "ζ as in zoo"),
    ("(silent h)", "the rough breathing is no longer sounded"),
    ("CAPS", "stressed syllable: every written accent is now stress, not pitch"),
]


def _nucleus_ipa(s: Syllable, scheme: str) -> str:
    table = VOW[scheme]
    k = s.key
    if len(k) == 1 and s.subscript:
        v = table[{"α": "ᾳ", "η": "ῃ", "ω": "ῳ"}[k]]
    elif len(k) == 1:
        short, long_ = table[k]
        v = long_ if s.long else short
    else:
        v = table[k]
    if scheme == "restored" and s.accent:
        mark = {"acute": ACUTE, "circ": "̂", "grave": GRAVE}[s.accent]
        # acute on a long nucleus rises on the second mora; circumflex on the first
        vowels = [i for i, c in enumerate(v) if c not in "ːʰ"]
        pos = vowels[0] if s.accent == "circ" or len(vowels) == 1 else vowels[-1]
        v = v[: pos + 1] + mark + v[pos + 1 :]
    return v


def _cons_ipa(cs: list[Letter], scheme: str, after: list[Letter] | None = None, initial_rho=False) -> str:
    out = []
    seq = cs + (after or [])
    for i, l in enumerate(cs):
        nxt = seq[i + 1].base if i + 1 < len(seq) else ""
        if l.base == "γ" and nxt in "γκχξ" and nxt:
            out.append("ŋ")
        elif l.base == "γ" and scheme == "koine" and nxt and nxt in "εηιυ":
            out.append("j")
        elif l.base == "σ" and nxt and nxt in "βγδμ" and scheme == "restored":
            out.append("z")
        elif l.base == "ρ" and (DASIA in l.marks or (initial_rho and i == 0)) and scheme == "restored":
            out.append("r̥")
        else:
            out.append(CONS[scheme][l.base])
    return "".join(out)


def syllable_ipa(syls: list[Syllable], scheme: str) -> list[str]:
    parts = []
    for n, s in enumerate(syls):
        nxt_onset = syls[n + 1].onset if n + 1 < len(syls) else []
        onset = _cons_ipa(s.onset, scheme, s.nucleus, initial_rho=(n == 0))
        if s.rough and scheme in ("restored", "erasmian"):
            onset = "h" + onset
        coda = _cons_ipa(s.coda, scheme, nxt_onset)
        parts.append(onset + _nucleus_ipa(s, scheme) + coda)
    return parts


def stressed(s: Syllable, scheme: str) -> bool:
    if scheme == "restored":
        return s.accent in ("acute", "circ")
    return s.accent is not None


def _respell_one(ipa: str, scheme: str) -> str:
    ipa = ud.normalize("NFD", ipa)
    ipa = "".join(c for c in ipa if c not in (ACUTE, GRAVE, "̂"))
    ipa = ud.normalize("NFC", ipa)
    out, i = [], 0
    table = RESPELL[scheme]
    while i < len(ipa):
        for a, b in table:
            if ipa.startswith(a, i):
                out.append(b)
                i += len(a)
                break
        else:
            out.append(ipa[i])
            i += 1
    return "".join(out)


def apply_quantity(word: str, table: dict[str, str]) -> tuple[str, bool]:
    """Return the word with macrons on long dichrona if the table knows it."""
    key = ud.normalize("NFC", word.lower())
    if key in table:
        return table[key], True
    return word, False


def phonemize(word: str, scheme: str, quantities: dict[str, str] | None = None) -> dict:
    """-> {'ipa': str, 'respell': str, 'syllables': int} for one token."""
    w = normalize_elision(word)
    for p in PUNCT:
        w = w.replace(p, "")
    elided = w.endswith("’")
    w = w.rstrip("’")
    if quantities:
        w, _ = apply_quantity(w, quantities)
    syls = syllabify(w)
    if not syls:  # consonant-only token (an elided particle like δ’ with its vowel gone)
        cons = "".join(CONS[scheme].get(l.base, l.base) for l in letters(w))
        return {"ipa": cons, "respell": _respell_one(cons, scheme) + "’", "syllables": 0}
    ipas = syllable_ipa(syls, scheme)
    spells = []
    for s, ip in zip(syls, ipas):
        r = _respell_one(ip, scheme)
        spells.append(r.upper() if stressed(s, scheme) else r)
    ipa = ".".join(ipas)
    if scheme in ("erasmian", "koine"):
        ipa = ".".join(("ˈ" if stressed(s, scheme) else "") + ip for s, ip in zip(syls, ipas))
    resp = "-".join(spells)
    if elided:
        resp += "’"
    return {"ipa": ipa, "respell": resp, "syllables": len(syls)}


# ---------------------------------------------------------------- hexameter scanner
# Scans one dactylic hexameter from its words and returns the Weft metre string
# ("—◡◡|——|...|—×"). Each syllable of the line gets the weights it can bear and a cost for each:
# a long vowel or diphthong, or a vowel before two consonants, is long at no cost; a short vowel
# before one consonant is short at no cost. The rules that let a syllable go the other way carry
# a cost (epic correption, muta cum liquida, metrical lengthening, an alpha, iota or upsilon
# whose length the quantity table does not give). Every scheme of five dactyls or spondees plus
# a final —× is tried, and the cheapest one that fits wins. Each costed choice the winner used is
# reported as a failure class, so a reviewer sees where the scan leaned on a rule.
# Not modeled: digamma beyond the short list below, lengthening before initial liquids other than
# as a costed option, and synizesis beyond word-final -εω (others are tried at a cost).

SCANNER_VERSION = "0.1"
DOUBLE_CONS = {"ζ", "ξ", "ψ"}
STOPS, LIQUIDS = set("πβφτδθκγχ"), set("λρμν")
# words that began with digamma (ϝ) in Homer's language, unaccented and lowercase stems; the lost
# consonant can block correption and resyllabification, so it is offered as an optional consonant
DIGAMMA_STEMS = ("αναξ", "ανακτ", "ανασσ", "οικ", "ιφι", "εκηβολ", "εκαεργ", "εκαστ", "εργ",
                 "εοικ", "οινο", "αστυ", "ιδε", "ιδω", "ειδ")
# word-internal digamma after the augment: ἔδϝεισεν makes the first syllable heavy
INTERNAL_DIGAMMA = ("εδεισ",)
COST = {
    "correption-kept-long": 0.05,   # long final vowel before a vowel, scanned long
    "mcl-short": 0.4,               # stop + liquid not making position
    "digamma-neglected": 0.4,       # the lost ϝ not counted
    "lengthening-final-consonant": 1.0,
    "lengthening-before-liquid": 1.5,
    "internal-correption": 1.5,
    "synizesis-assumed": 1.5,
    "dichronon-long": 2.0,          # an unlisted α ι υ scanned long
    "lengthening": 3.0,             # a short vowel scanned long with nothing to make it so
    "position-ignored": 4.0,
}
FLAGGED = {"internal-correption", "synizesis-assumed", "dichronon-long", "lengthening",
           "lengthening-before-liquid", "lengthening-final-consonant", "position-ignored"}


def _bare(w: str) -> str:
    return "".join(c for c in ud.normalize("NFD", w.lower()) if not ud.combining(c)).replace("ς", "σ")


def _scan_units(words: list[str], quantities: dict | None, merge: set[tuple[int, int]]):
    """-> list of nuclei, each a dict: word index, Letter list, consonants after it (with the word
    index each consonant belongs to)."""
    units = []  # ("V", wi, [Letter]) or ("C", wi, Letter)
    for wi, raw in enumerate(words):
        w = normalize_elision(raw)
        for p in PUNCT:
            w = w.replace(p, "")
        w = w.rstrip("’")
        if quantities:
            w, _ = apply_quantity(w, quantities)
        seq = nuclei_split(letters(w))
        vi = [k for k, x in enumerate(seq) if isinstance(x, list)]
        # synizesis: two adjacent nuclei in one word sounded as one syllable
        for k in range(len(vi) - 1, 0, -1):
            a, b = vi[k - 1], vi[k]
            if b == a + 1 and (wi, k - 1) in merge:
                seq[a] = seq[a] + seq[b] + [Letter("·")]   # "·" marks a merged, long nucleus
                del seq[b]
        for x in seq:
            units.append(("V", wi, x) if isinstance(x, list) else ("C", wi, x))
    nuclei = []
    for k, u in enumerate(units):
        if u[0] != "V":
            continue
        cons = []
        j = k + 1
        while j < len(units) and units[j][0] == "C":
            cons.append((units[j][1], units[j][2].base))
            j += 1
        nxt_wi = units[j][1] if j < len(units) else None
        nuclei.append({"wi": u[1], "nuc": u[2], "cons": cons, "next_wi": nxt_wi})
    return nuclei


def _synizesis_candidates(words: list[str], quantities, marked: set[str]):
    """-> (forced merges, optional merges): (word index, nucleus index) pairs whose nucleus joins
    the next. Word-final -εω (the Homeric genitive) and marked words are forced; any other ε
    before a vowel is optional at a cost."""
    forced, optional = set(), set()
    for wi, raw in enumerate(words):
        w = normalize_elision(raw)
        for p in PUNCT:
            w = w.replace(p, "")
        w = w.rstrip("’")
        if quantities:
            w, _ = apply_quantity(w, quantities)
        seq = nuclei_split(letters(w))
        vi = [k for k, x in enumerate(seq) if isinstance(x, list)]
        for k in range(len(vi) - 1):
            a, b = vi[k], vi[k + 1]
            if b != a + 1 or seq[a][-1].base != "ε" or len(seq[a]) != 1 or DIAER in seq[b][0].marks:
                continue
            is_final = k + 1 == len(vi) - 1 and b == len(seq) - 1
            if (is_final and _bare(seq[b][0].base) == "ω" and len(seq[b]) == 1) or _bare(raw).rstrip("’") in marked:
                forced.add((wi, k))
            else:
                optional.add((wi, k))
    return forced, optional


def _options(n: dict, words: list[str], last: bool, digamma) -> dict:
    """-> {"L": (cost, reason), "S": (cost, reason)} for one syllable."""
    if last:
        return {"L": (0, None), "S": (0, None)}
    nuc = n["nuc"]
    merged = nuc[-1].base == "·"
    letters_ = [l for l in nuc if l.base != "·"]
    if merged or len(letters_) > 1:
        length = "long"
    else:
        l = letters_[0]
        if l.base in "ηω" or l.marks & {CIRC, IOTA_SUB, MACRON}:
            length = "long"
        elif l.base in "εο":
            length = "short"
        else:
            length = "unknown"   # α ι υ with no mark and no table entry
    cons = n["cons"]
    wi, nwi = n["wi"], n["next_wi"]
    word_final = nwi is not None and nwi != wi
    nxt_digamma = word_final and digamma(words[nwi])
    units = sum(2 if c in DOUBLE_CONS else 1 for _, c in cons)
    if not word_final and n.get("first_in_word") and len(cons) == 1 \
            and _bare(normalize_elision(words[wi])).startswith(INTERNAL_DIGAMMA):
        units += 1
    if units >= 2:
        if length == "long":
            return {"L": (0, None)}
        if len(cons) == 2 and cons[0][1] in STOPS and cons[1][1] in LIQUIDS and cons[0][0] == cons[1][0]:
            return {"L": (0, None), "S": (COST["mcl-short"], "mcl-short")}
        return {"L": (0, None), "S": (COST["position-ignored"], "position-ignored")}
    # open syllable, or one consonant that goes to the next syllable
    if nxt_digamma:
        if units == 1 or length == "long":
            return {"L": (0, None), "S": (COST["digamma-neglected"], "digamma-neglected")}
    if length == "long":
        if units == 0 and word_final:
            return {"L": (COST["correption-kept-long"], None), "S": (0, "correption")}
        if units == 0:
            return {"L": (0, None), "S": (COST["internal-correption"], "internal-correption")}
        return {"L": (0, None)}
    if word_final and units == 1 and cons[0][0] == wi:
        # a short final syllable closed by its own consonant, before a vowel: the consonant goes
        # to the next word, but Homer often scans such a syllable long in the princeps
        return {"S": (0, None), "L": (COST["lengthening-final-consonant"], "lengthening-final-consonant")}
    if length == "unknown":
        return {"S": (0, None), "L": (COST["dichronon-long"], "dichronon-long")}
    if word_final and units == 1 and not cons[0][0] == wi and cons[0][1] in LIQUIDS | {"σ"}:
        return {"S": (0, None), "L": (COST["lengthening-before-liquid"], "lengthening-before-liquid")}
    return {"S": (0, None), "L": (COST["lengthening"], "lengthening")}


def _feet_patterns():
    for mask in range(32):
        feet = ["D" if mask >> (4 - i) & 1 else "S" for i in range(5)]
        yield feet


def scan_hexameter(words: list[str], quantities: dict | None = None, synizesis: set[str] | None = None,
                   digamma_stems: tuple[str, ...] = DIGAMMA_STEMS) -> tuple[str | None, list[tuple[str, str]]]:
    """Scan one dactylic hexameter. ``words`` are the line's surfaces as printed (elision marks
    kept, punctuation tolerated). ``quantities`` is the work's merged quantity table; ``synizesis``
    names words (unaccented, lowercase) to read with synizesis. Returns (metre string or None,
    [(failure class, sample)])."""
    marked = {_bare(s) for s in (synizesis or set())}
    digamma = lambda w: _bare(normalize_elision(w)).startswith(digamma_stems)
    forced, optional = _synizesis_candidates(words, quantities, marked)
    optional = sorted(optional)
    best = []   # (cost, metre, flags)
    for m in range(1 << len(optional)):
        use = {optional[k] for k in range(len(optional)) if m >> k & 1}
        nuclei = _scan_units(words, quantities, forced | use)
        seen = set()
        for n in nuclei:
            n["first_in_word"] = n["wi"] not in seen
            seen.add(n["wi"])
        opts = [_options(n, words, k == len(nuclei) - 1, digamma) for k, n in enumerate(nuclei)]
        base = COST["synizesis-assumed"] * len(use)
        for feet in _feet_patterns():
            tmpl = [w for f in feet for w in ("LSS" if f == "D" else "LL")] + ["L", "X"]
            if len(tmpl) != len(opts):
                continue
            cost, flags = base, [("metre-synizesis-assumed", words[wi]) for wi, _ in sorted(use)]
            for k, (t, o) in enumerate(zip(tmpl, opts)):
                if t == "X":
                    continue
                if t not in o:
                    break
                c, why = o[t]
                cost += c
                if why in FLAGGED:
                    flags.append((f"metre-{why}", f"{words[nuclei[k]['wi']]} (syllable {k + 1})"))
            else:
                metre = "|".join({"D": "—◡◡", "S": "——"}[f] for f in feet) + "|—×"
                best.append((round(cost, 3), metre, flags))
    if not best:
        return None, [("metre-no-fit", " ".join(words))]
    best.sort(key=lambda b: b[0])
    cost, metre, flags = best[0]
    ties = [b for b in best[1:] if b[0] == cost and b[1] != metre]
    if ties:
        flags = flags + [("metre-ambiguous", f"{metre} or {ties[0][1]}")]
    return metre, flags
