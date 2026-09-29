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
