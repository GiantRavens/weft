# Languages and pronunciation

This page sets out, for each language in the library, what the sound row on the page claims, what
the code says it rests on, and where it is weakest. It is written for specialists deciding whether
to trust the pronunciation row for their language and how to correct it. Every statement here is
taken from the module in `pipeline/weft/`, its data files, or the manifests and notes of the works
that use it. Where the repository names no source, this page says so.

## What the sound row is

- **Schemes.** Each language module defines one or more pronunciation schemes. For every word and
  every scheme it produces an IPA transcription, which is canonical, and a respelling for an English
  reader, which is a projection of the IPA. The word panel shows both; the row under the text shows
  the respelling.
- **Order.** The first scheme a work's manifest lists is the page default. By Weft's rule it
  is the reconstruction Weft judges best supported of how the text most likely sounded when it was first
  written; later traditions (Erasmian Greek, ecclesiastical Latin, modern Icelandic, the modern
  standard languages) come second.
- **Respelling conventions.** Hyphens divide syllables (in Japanese, morae). CAPS mark the stressed
  syllable, or the raised pitch where the scheme models a pitch accent (restored Greek, Vedic).
  Long vowels are doubled or given their own symbol. Some schemes mark no syllable at all because
  the module treats stress as unknown or not distinctive: Sumerian, Tamil, French, Old Chinese,
  Japanese. The Chinese Tang, Mandarin and Cantonese rows use Stimson's notation, pinyin and
  Jyutping rather than an English respelling.
- **The Sound key.** The masthead button opens the key for the scheme in use: the scheme's label
  and a table of every symbol. The key text is the `KEY` dictionary in the language module; the
  label is the manifest's `scheme_labels` entry if it has one, otherwise the module's
  `SCHEME_LABELS`.
- **Confidence.** A manifest may set `sound_confidence`. At `low` the page opens with "The
  pronunciation here is a reconstruction"; at `medium`, "Parts of the pronunciation here are
  reconstructed". Both link to the Pronunciation and Recording forms and to this page. Works with
  no value show no invitation. Twenty-seven of the sixty-one public works set a value (see the table, and the
  last section).
- **Each word alone.** Unless a section below says otherwise, each word is phonemized on its own:
  elision, sandhi and assimilation across words are not modelled in the sound row.

### How to propose a change

A pronunciation change is made only with a citation: a grammar, an article or a corpus.

1. **The Pronunciation issue form** (`.github/ISSUE_TEMPLATE/pronunciation.yml`), linked from each
   page with the work and scheme filled in. It asks for the scope (one word, a rule, the stress or
   accent rule, or a new scheme alongside the existing ones), the words affected, what the sound
   should be (IPA if possible), the citation, and how you wish to be credited. No git is needed.
2. **A pull request** against `pipeline/weft/<module>.py` and its data files under
   `pipeline/weft/data/`. For languages where the reading is entered per word (Egyptian,
   Akkadian, Sumerian, Vedic, Tamil, Persian, the runes, Japanese), the per-word form lives in the
   work's edition file, `texts/<work>/edition.yaml`. After a rule change, run `weft acquire` and `weft draft` for each work in
   that language, then `weft check <work>` and `uv run --with pytest pytest -q tests` before submitting.
   `weft say <Greek words>` prints Greek words in the restored and Erasmian schemes; other
   languages have no command-line phonemizer yet.

A different reconstruction can be added as a new scheme rather than replacing the current one;
schemes sit side by side and the reader chooses.

## Summary

"First" marks the page default. Confidence is the manifest's `sound_confidence`; "not set" means
the page shows no invitation.

| Language | Module | Works | Schemes | Confidence |
|---|---|---|---|---|
| Old Egyptian | `egyptian` | Pyramid Texts of Unas | old-egyptian (first), egyptological | low |
| Sumerian | `sumerian` | Enheduanna, Temple Hymn 5 | recon-2300 (first), classroom | low |
| Akkadian | `akkadian` | Hammurabi, prologue | ob-1750 (first), classroom | low |
| Vedic Sanskrit | `sanskrit` | Rigveda 1.1 | vedic (first), modern | medium |
| Ancient Greek | `greek` | Iliad, Odyssey, Aristotle | restored (first), erasmian | not set |
| | | Nicene Creed (381) | koine (first), erasmian | medium |
| | | John, Beatitudes, 1 Corinthians 13 | koine (first), erasmian | not set |
| | | Epictetus, Marcus Aurelius | koine (first), restored, erasmian | not set |
| Biblical Hebrew | `hebrew` | Genesis | tiberian (first), modern-israeli | not set |
| Biblical Aramaic | `hebrew` | Daniel 5 | tiberian (first), modern-israeli | medium |
| Classical Chinese | `chinese` | Sunzi, Daodejing | old-chinese (first), tang, mandarin | medium |
| | | Li Bai | tang (first), mandarin, cantonese | medium |
| Sahidic Coptic | `coptic` | Gospel of Mark 1 | sahidic (first), bohairic | medium |
| Latin | `latin` | Ovid, Res Gestae | classical (first), ecclesiastical | not set |
| | | Bayeux Tapestry | anglo-norman (first), classical | medium |
| | | Magna Carta | anglo-latin (first), classical | not set |
| | | Saer de Quincy, two charters | anglo-latin (first), classical | medium |
| | | Pico | italian-humanist (first), classical | not set |
| | | Inter caetera | italian-humanist (first), classical | medium |
| | | Erasmus | low-countries (first), classical | not set |
| | | More, Utopia | tudor-english (first), classical | not set |
| | | Luther, Ninety-five Theses | german-humanist (first), ecclesiastical, classical | not set |
| | | Descartes and Newton | as-first-read (first), classical | not set |
| Old Tamil | `tamil` | Tirukkural | old-tamil (first), modern | medium |
| Runic | `runic` | Kylver, Gallehus, Rök | as-carved (only) | low |
| Old English | `oldenglish` | Beowulf | west-saxon (only) | not set |
| Old Norse | `norse` | Völuspá, Hávamál, Þrymskviða, Grettis saga | old-norse (first), modern-icelandic | not set |
| | | Snorri, Gylfaginning | old-norse (first), modern-icelandic | medium |
| Old East Slavic | `oldeastslavic` | Primary Chronicle, 859-862 | orv1100 (first), ru | low |
| Persian | `persian` | Rubaiyat | early (first), modern | medium |
| Middle Mongolian | `mongolian` | Secret History of the Mongols, 1-10 | mm-1250 (only) | low |
| Japanese | `japanese` | Bashō | edo-1686 (first), modern | not set |
| Franco-Italian | `oldfrench` | Marco Polo, Cipangu | fr1300 (first), it1300 | medium |
| Italian | `italian` | Dante, Petrarch, Machiavelli | florentine (first), modern | not set |
| Spanish | `spanish` | Columbus, 1493 | c1492 (first), modern | not set |
| Portuguese | `portuguese` | Camões, Os Lusíadas I.1-3 | lisboa1540 (first), europeu, brasileiro | medium |
| | | Caminha, letter of 1500 | lisboa1540 (first), europeu, brasileiro | medium |
| Dutch | `dutch` | Linschoten | h1596 (first), modern | not set |
| French | `french` | Montaigne | m1580 (first), modern | not set |
| | | Declaration of the Rights of Man (1789) | fr1791 (first), modern | medium |
| | | de Gouges, Rights of Woman (1791) | fr1791 (first), modern | not set |
| | | Rouget de Lisle, La Marseillaise (1792) | fr1791 (first), modern | medium |
| | | Berlin Act, 1885 | fr1885 (first), modern | not set |
| German | `german` | Kant, Nietzsche | northern (first), modern | not set |
| | | Marx and Engels, Manifest (1848) | northern (first), modern | medium |
| | | Luther's Bible | ecg1545 (first), modern | not set |
| Swahili | `swahili` | Steere, The Kites and the Crows | z1870 (first), modern | medium |
| Esperanto | `esperanto` | Zamenhof, Unua Libro specimens (1887) | zamenhof (only) | not set |
| Quenya, Sindarin | `elvish` | private works only (Tolkien, in copyright) | tolkien (only) | not set |

The registry that maps a manifest's `language` code to a module is `PHON` in
`pipeline/weft/draft.py`.

## Old Egyptian

**Schemes.**
- `old-egyptian`, "Reconstructed Old Egyptian, about 2350 BC (conjectural)". Consonant values: ꜣ
  as a uvular r, ꜥ as a pharyngeal, ḥ as a pharyngeal h, ṯ and ḏ as palatal stops, d and ḏ as
  ejectives. Vowels and stress come from Weft's hand vocalization (`n`), entered only where a
  Coptic descendant or a Greek rendering of a name was used.
- `egyptological`, "Egyptological convention (not a reconstruction)": e inserted between
  consonants, ꜣ and ꜥ as a, j as i, w as u. No stress.

**What it rests on.** The consonant values follow "the outline of Loprieno (1995) and Allen
(2013)" (module docstring; the notes cite Loprieno, *Ancient Egyptian: A Linguistic Introduction*,
chapter 3, and Allen, *The Ancient Egyptian Language: An Historical Study*). The ejective reading
of d and ḏ is attributed to Loprieno. Each of the fourteen vocalized forms names its evidence in
the `vocalization` map of `texts/pyramid-texts-unas/edition.yaml` (for example Coptic ⲛⲟⲩⲧⲉ for
nā́ṯir, Greek Ὄννος for the king's name), and the page shows it in the word's provenance. The
module states that these are Weft's inferences by the sound correspondences in those grammars,
not forms quoted from them.

**Where it is weakest.** The module calls this "the most reconstructed sound row in the library"
and "conjectural word by word". Only fourteen forms are vocalized; every other word falls back to
the Egyptological convention inside the first scheme, in lower case without stress, and is flagged
per token. Each consonant value in the list above is marked as debated; the key notes that ꜣ may
have weakened to a glottal stop or y by the Middle Kingdom and that some scholars take ꜥ as a
d-like stop in the earliest texts. Several vocalization entries call individual vowels uncertain
or a guess.

**What a specialist could improve.** Add or correct entries in the `vocalization` map and the `n`
field of the tokens, with the evidence named; revise consonant values in `egyptian.py`; propose an
alternative consonant system as a second reconstruction.

## Sumerian

**Schemes.**
- `recon-2300`, "Reconstructed Sumerian, late third millennium BC (conjectural)": b, d, g as
  voiceless unaspirated [p t k]; p, t, k as aspirated; z as [ts]; ŋ as [ŋ]; h as [x]. A consonant
  or vowel written twice across a sign boundary is read once. No stress, no vowel length.
- `classroom`, "Assyriological classroom reading (modern convention)": each sign said as
  transliterated.

**What it rests on.** Jagersma, *A Descriptive Grammar of Sumerian* (2010), "in broad agreement
with Edzard, *Sumerian Grammar* (2003)" (module docstring). The notes add Foxvog, *Introduction to
Sumerian Grammar*, on pronunciation. Lemma and morphology come from the Oracc lemmatization
(epsd2/literary); the cuneiform row from the Oracc Sign List value table.

**Where it is weakest.** The module describes the language as an isolate whose sound "is known
only indirectly" and the row as "among the most reconstructed" in the library. Stress and vowel
length are unknown and not shown. The phoneme conventionally written dr or ř is not applied to any
word (manifest and module). One broken sign has no sound.

**What a specialist could improve.** The rules in `sumerian.py` (stop series, the treatment of
written doubling, whether and where to apply ř); per-token readings in the optional `n` field of
`texts/enheduanna-temple-hymns/edition.yaml` where the spelling misleads (the module's example is
a-a for aya).

## Akkadian

**Schemes.**
- `ob-1750`, "Old Babylonian, around 1750 BC (approximate)": š as plain s; s, z, ṣ as affricates
  (ts, dz, ts'); the emphatics ṭ, q, ṣ as ejectives.
- `classroom`, "Assyriological classroom reading": š as sh, emphatics as plain t, s and a back q.

**What it rests on.** The sibilant view is attributed to "Streck and Kogan among others" (module);
the notes cite M. P. Streck, "Sibilants in the Old Babylonian texts of Hammurapi and of the
governors in Qaṭṭunān" (2006). Stress in both schemes follows the rule in Huehnergard, *A Grammar
of Akkadian* (3rd edition, 2011). The sound is computed from a hand normalization (`n`) in the
edition; the cuneiform row is generated from a modern sign reading (`sg`) through the Oracc Sign
List (`pipeline/weft/data/akk_osl_values.tsv`, CC0).

**Where it is weakest.** The manifest: the values of š, s, z and the emphatics are debated, and
stress is inferred by a modern rule. The key says the exact sound of the emphatics is not known.
The transliteration is Harper's of 1904, with older conventions; the sound does not depend on it,
since it reads `n`.

**What a specialist could improve.** The normalizations in `texts/akkadian-hammurabi/edition.yaml`
(vowel length and contraction drive both sound and stress); the consonant values and the stress
rule in `akkadian.py`; a second reconstruction that keeps š as sh, which the notes name as the
competing view.

## Vedic Sanskrit

**Schemes.**
- `vedic`, "Vedic: as recited around 1200 BC, with the pitch accent (approximate)". CAPS mark the
  raised pitch (udātta), not stress. Short a is close; e and o are long monophthongs; c and j are
  palatal stops; v is between v and w; ṛ is syllabic r; intervocalic ḍ is ḷ.
- `modern`, "Modern Indian reading of Sanskrit": ṛ as ri, ś and ṣ both sh, jñ as gy, final visarga
  echoing the vowel. Pitch not marked.

**What it rests on.** The ancient phonetic treatises (prātiśākhyas) and Pāṇini's statement on short
a (module). The notes cite W. S. Allen, *Phonetics in Ancient India* (1953), and Macdonell, *A Vedic
Grammar for Students* (1916), appendix III; and Arnold, *Vedic Metre* (1905), for the metre. The
accent is hand-entered in the IAST form `n`; `decode_marks` reads the Devanagari accent strokes back
into raised syllables so the two can be checked against each other (tested in
`tests/test_golden.py`).

**Where it is weakest.** The manifest: the treatises are several centuries later than the hymns.
Some pādas count seven syllables as written where recitation restored a lost syllable; the metre row
shows the written count. The treebank's words are unaccented, so the accent comes from the edition
alone.

**What a specialist could improve.** Vowel and consonant values in `sanskrit.py`; the accented
forms in `texts/rigveda-1-1/edition.yaml`; a rule for the restored syllables, which the metre row
does not yet count.

## Ancient Greek

**Schemes.**
- `restored`, "Restored: reconstructed classical pitch accent". The module defines it as the
  "scholarly reconstruction of 5th-century Attic". Accent is pitch: acute and circumflex syllables
  are raised; a grave is not. Aspirates are tʰ pʰ kʰ, ζ is zd, η is long open e, ει long close e.
- `koine`, "Koine: Greek as spoken in the first century (after Randall Buth)": no vowel length;
  η as close e; ι and ει as i; υ and οι as ü; αι as e; αυ, ευ as av, ev; β γ δ as fricatives;
  rough breathing silent; every accent read as stress.
- `erasmian`, "Erasmian: traditional classroom stress": every written accent, grave included, read
  as stress; θ φ χ as fricatives.

Homer and Aristotle open in `restored`; the New Testament books, Epictetus and Marcus Aurelius open
in `koine`. There is no separate Homeric or archaic scheme. The Iliad and Odyssey manifests relabel
`restored` for their pages: "classical Attic of the 5th century BC with its pitch accent; for Homer,
the nearest well-studied stage, not the poet's own (approximate)".

**What it rests on.** W. S. Allen, *Vox Graeca*, for `restored` (module); Randall Buth for `koine`
(module label and the New Testament manifests); the Epictetus notes cite Horrocks, *Greek: A
History of the Language and its Speakers* (2nd edition, 2010), chapter 5. The length of α, ι, υ,
which the spelling does not show, comes from quantity tables: `grc_quantities.yaml` (shared),
`grc_quantities_iliad.yaml` and `grc_quantities_marcus.yaml`, each entry from the LSJ headword and,
for verse, the foot where the hexameter shows it.

**The hexameter scanner.** `greek.scan_hexameter` (version 0.1) scores every arrangement of five
dactyls or spondees plus a final foot, with a cost for each rule it leans on (epic correption, muta
cum liquida, metrical lengthening, an unlisted long α ι υ, synizesis, neglected digamma), and
reports each costed choice as a failure class. `test_hexameter_scanner_matches_hand_scansion` in
`tests/test_golden.py` requires its output to equal every hand scansion in the curated overlays:
62 lines (Odyssey 1.1-10 and Iliad 1.1-52). Not modelled: digamma beyond a short list of stems,
lengthening before initial liquids except as a costed option, and synizesis beyond word-final -εω.

**Where it is weakest.**
- Vowel length of α ι υ: words not in a quantity table default to short (Iliad and Aristotle
  manifests).
- Koine: the New Testament manifests note that scholars differ on how far η and υ had moved by the
  first century. The scheme models the first century; the Epictetus (early second century) and
  Marcus Aurelius (late second century) pages relabel it to say their texts are later.
- Homer: the editor's accentuation of Πηληϊάδεω and the synizesis of -εω are not modelled in the
  sound row (Iliad manifest). Each word is phonemized alone, so elision and correption across
  words appear in the metre row only.

**What a specialist could improve.** Entries in the quantity tables; the digamma stem list and the
costs in the scanner; the Koine vowel and consonant tables in `greek.py`; a scheme for the language
of the Homeric poems, which the repository does not yet have.

## Biblical Hebrew

**Schemes.**
- `tiberian`, "Tiberian: the reading the vowel points record, about AD 900 (after Khan)": qamets
  [ɔ], vocal shewa short [a], uvular r, ו as [v], pharyngeal ח and ע, emphatic ט צ ק, begadkefat
  softening.
- `modern-israeli`, "Modern Israeli Hebrew": weakened gutturals, no emphatics, qamets [a].

**What it rests on.** Geoffrey Khan, *The Tiberian Pronunciation Tradition of Biblical Hebrew*
(2020) (module). The pointing gives the vowels, dagesh gives gemination and hard stops, and the
cantillation accent gives the stressed syllable, so no quantity table is used. Shewa and
begadkefat follow "the standard grammars" (module; no grammar is named).

**Where it is weakest.** The manifest: the vowels are the Masoretes' of about AD 900, so "as first
written" reaches the pointing, not the period of composition. Vocal against silent shewa and
qamets gadol against qatan are guessed where the pointing is ambiguous. The verse-final silluq is
recovered from the sof pasuq.

**What a specialist could improve.** The shewa and qamets heuristics in `hebrew.py`, with a named
grammar; an earlier reconstruction as a scheme placed before `tiberian`, if one can be stated per
word.

**Aramaic.** The Aramaic chapters of Daniel carry the same Tiberian pointing, so Daniel 5 is read by this
module unchanged, under the language code `arc`. What differs is the morphology: the OSHB parsing strings are
prefixed A, and the verb-stem letters then mean the Aramaic stems (Peal, Pael, Haphel, Hithpeel and the rest),
which `treebank.py` decodes from its own table. Words written one way and read another (Ketiv and Qere) reach
the digital text as consonants without vowels, and their sound row is a reading supplied by the reader, which
the page's notes say.

## Classical Chinese

**Schemes.**
- `old-chinese`: Baxter-Sagart (2014), version 1.1. Manifest labels date it to the compilation of
  each text (Sunzi, 5th to 4th century BC; Daodejing, 4th to 3rd century BC), approximate. No
  capitals: the model has no tones. The details panel shows the scholarly notation, brackets
  included.
- `tang`, "Tang: as Li Bai's generation read it, 8th century (Stimson, via Unicode)". Stimson's
  notation, with tone marks for level, rising, departing and entering.
- `mandarin` (pinyin) and `cantonese` (Jyutping), from Unihan.

**What it rests on.** Old Chinese readings are taken per character from Wiktionary's data modules,
each pinned to a revision id, into `pipeline/weft/data/lzh_oc_bs.yaml` (CC BY-SA 4.0). A character
Baxter-Sagart lacks falls back to Zhengzhang Shangfang (2003) and says so. Tang readings are Unihan
`kTang`, which follows Hugh M. Stimson, *T'ang Poetic Vocabulary* (1976). A character with no reading
of its own borrows one from a glyph variant (kZVariant, then kSemanticVariant) and says so.

**Where it is weakest.**
- Old Chinese is a reconstruction; brackets and parentheses mark uncertain segments (both
  manifests). Fallbacks to Zhengzhang: 較 in the Daodejing; 佚, 校, 驕 in Sunzi.
- Tang coverage is about 3,800 characters (Li Bai manifest). Characters with no Tang reading show
  ?: 弗 in the Daodejing; 佐, 佚, 察, 算, 詭, 誘 in Sunzi. Readings borrowed from variants: 為, 眾
  (and 於 in Sunzi).
- On the Sunzi and Daodejing pages the `tang` scheme is relabelled as the 8th-century reading of a
  much older text.
- Sunzi: 校 is read jiào, which Unihan does not give (mandarin-reading-unattested).

**What a specialist could improve.** Entries in `lzh_oc_bs.yaml` (a reading, or a better fallback
for the four characters outside Baxter-Sagart); Tang readings for the missing characters, which
need a source other than Unihan; Mandarin choices for polyphonic characters.

## Latin

All Latin schemes keep the classical penultimate stress rule (except the French method, below), so
every word needs its vowel length from a quantity table: `pipeline/weft/data/lat_quantities.yaml`,
plus per-work tables for the Bayeux Tapestry, Inter caetera, the Ninety-five Theses, the Res
Gestae and the Saer de Quincy charters. Entries follow Lewis and Short headword quantities plus inflectional endings, confirmed
against the hexameter for Ovid. A word missing from the table is reported as `quantity-unknown`.

**Schemes.**

| Id | Label | Used by | What it represents |
|---|---|---|---|
| `classical` | Classical: restored pronunciation of Cicero's and Ovid's Rome | first for Ovid and the Res Gestae; third for Luther; second elsewhere | after W. S. Allen, *Vox Latina*: c and g hard, v as w, ae as ai, length audible |
| `ecclesiastical` | Ecclesiastical: Italianate church Latin | second for Ovid and the Res Gestae; second of three for Luther | soft c and g before front vowels, v as v, ae as e, length heard only in stress |
| `anglo-norman` | As first read: Latin in Normandy and Norman England around 1070 (approximate) | Bayeux Tapestry | c before front vowels ts, g and j dʒ, h silent, u as French u, s between vowels z |
| `anglo-latin` | Anglo-Latin: as a clerk in England read Latin around 1215 (approximate) | Magna Carta; the Saer de Quincy charters | soft c ts, soft g and j dʒ, h silent, v as v, s between vowels z |
| `italian-humanist` | As first read: Latin in northern Italy in the 1480s (approximate) | Pico; Inter caetera | Italian vowels, soft c ch, gn ny, sc sh, ti ts, h silent, s between vowels z |
| `low-countries` | As first read: Latin in the Low Countries around 1500 (approximate) | Erasmus | Dutch vowel values long in open syllables, u as Dutch uu, g a fricative, ch kh, ti ts |
| `tudor-english` | As first read: Latin in England around 1516 (approximate) | More | English long values in stressed open syllables at an earlier stage of the Great Vowel Shift, ti as si |
| `german-humanist` | As first read: Latin in Saxony around 1517 (approximate) | Luther, Ninety-five Theses | German lengthening rule, c before front vowels ts, g hard, qu kv, v as f, final devoicing |
| `as-first-read` | As first read: Newton in the English manner, Descartes in the French (approximate) | Descartes and Newton | per section `dialect`: english (1680s English method) or french (1640s French method, final stress, nasal vowels) |

Manifests relabel some of these for their page (Erasmus, Pico, Inter caetera, More, Luther, the
Res Gestae).

**What it rests on.**
- `classical`: Allen, *Vox Latina* (module). The Res Gestae table marks hidden quantities where the
  handbooks agree, after Allen and Cicero, *Orator* 159, and lists disputed ones in its header.
- `as-first-read`: "contemporary grammars and later accounts (W. S. Allen, Vox Latina, appendix)"
  (module comment).
- `low-countries`, `tudor-english`, `italian-humanist`: Middle Dutch sound history and the later
  Dutch school tradition; English sound history; Italian sound history and the later ecclesiastical
  tradition (module comments). The notes for Erasmus and More cite Allen's appendix on national
  pronunciations. No period grammar is named.
- `german-humanist`: the later German school pronunciation of Latin, Early New High German sound
  history, and humanist complaints such as Erasmus's *De recta pronuntiatione* (1528) (module).
- `anglo-norman`: Old French sound history, Anglo-Norman spelling and the captions' own spellings
  (PRELIUM, EDIFICARE), Roger Wright's argument on the reading of Latin before and after the
  Carolingian reform, and Allen's appendix on French reading (module). The notes cite Pope, *From
  Latin to Modern French* (1934), and Wright, *Late Latin and Early Romance* (1982).
- `anglo-latin`: spelling and French and English sound history (key); no work is named. The
  charters' quantity table follows Lewis and Short, with the charter vocabulary (elemosina,
  warantizo, ius patronatus) after Niermeyer and Du Cange (manifest).

**Where it is weakest.**
- Every national scheme is labelled approximate. None rests on a description by the author.
- `anglo-norman`: u as [y], silent h (Harold may have kept his), and whether qu was still [kw]
  (module).
- `german-humanist`: v as f; v or w is also possible (module and manifest). The module has no eu
  diphthong, so seu is read as two syllables (Luther manifest).
- `italian-humanist` on Inter caetera: the scheme was built for northern Italy and voices s
  between vowels, which a Roman or Spanish-born chancery reader may not have done (manifest).
- Abbreviations and misprints are read through the quantity tables (Luther and Res Gestae
  manifests), so a table entry decides both length and the word that is sounded. Forms that differ
  only in a final long vowel share one entry, so the classical reading shows one length for both
  (Luther manifest).
- `anglo-latin` on the Duglyn charter: the scheme was built for England about 1215, and the charter
  was most likely written by a clerk in Scotland, whose Latin may have differed in ways not
  modelled (manifest). Medieval spellings (Vniuersis, hec, Scocie) are shown as written, and the
  quantity table restores the classical spelling so that the classical reading is classical
  (manifest). Personal and place names take no long vowels unless a Latin form is attested.
- Each word is phonemized alone; verse elision is not modelled (Ovid manifest).

**What a specialist could improve.** Quantity-table entries, especially hidden quantities and
medieval words keyed by their classical stems; the rule functions in `latin.py` (`_humanist`,
`_german`, `_norman`, `_national`) for a named period grammar; an eu diphthong; a separate
southern Italian or Roman reading for the papal chancery.

## Sahidic Coptic

**Schemes.**
- `sahidic`, "Sahidic, 4th-5th century (approximate reconstruction)": letter values after Peust: ⲃ a
  bilabial fricative, ⲏ a close e against ⲉ an open e (reduced to ə when unstressed), ⲟ an open o
  against ⲱ a close o, ϫ the affricate of church, ϭ a palatalized k, ⲑ ⲫ ⲭ aspirates. The Greek
  letters for voiced sounds in Greek words (ⲅ ⲇ ⲍ) are read k t s. A consonant with no vowel beside
  it is read as syllabic, with ə before it. A doubled vowel is read as the vowel followed by a glottal
  stop. Stress falls on the last syllable with a full vowel; Greek loanwords keep the Greek accent.
- `bohairic`, "Modern Coptic church pronunciation (Greco-Bohairic), applied to Sahidic spelling": the
  reformed pronunciation taught since the 1850s, how a reader trained in today's liturgy would sound
  the letters. The church reads Bohairic, not Sahidic, so this is a convention applied to a text it
  was not made for, not a tradition of reading this text (module).

**What it rests on.** Peust, *Egyptian Phonology* (1999), for the letter values; Layton for the
reading of a doubled vowel; the letter table published by the Coptic Orthodox Diocese of the
Southern United States for `bohairic` (module). The accent of Greek loanwords and the list of
unstressed particles are in `pipeline/weft/data/cop_stress.yaml`. Lemma and morphology come from
UD_Coptic-Scriptorium (CC BY 4.0), which annotates a different digital text of Mark; spelling
differences are normalized before the two are compared, and what remains is reported as
`edition-differs-from-treebank` (manifest). Glosses are hand-written against the treebank's lemmas,
with Crum's *Coptic Dictionary* (1939) and Lambdin's *Introduction to Sahidic Coptic* (1983) as
references (manifest).

**Where it is weakest.** The edition prints no supralinear strokes and no punctuation, so the
syllabic vowel is supplied by rule rather than read from the manuscript (manifest). That Greek
loanwords keep the Greek accent is an assumption (manifest). The value of ⲩ standing alone in Greek
words may already have shifted (key). Each word is phonemized alone.

**What a specialist could improve.** The stress table and the particle list in `cop_stress.yaml`;
the syllabic-consonant rule and the Greek-letter values in `coptic.py`; the normalization list used
to compare the edition with the treebank's text.

## Old Tamil

**Schemes.**
- `old-tamil`, "Old Tamil: as the Kural was likely first recited (approximate)": the six stops
  voiceless initially and doubled, voiced after a nasal and between vowels; c a palatal stop; ṟ a
  trill, ṟṟ an alveolar stop; ḻ the retroflex approximant; the āytam a weak fricative of unknown
  value; final shortened u.
- `modern`, "Modern Tamil recitation": c as s, k between vowels as gh, ṟṟ as tr, glides before
  initial e and o.

No syllable is capitalized: the module states that Tamil stress does not distinguish meaning.

**What it rests on.** "The description of sounds in the Tolkāppiyam and the usual reconstructions of
Old Tamil" (module). No modern reconstruction is named. The sound is computed from a hand ISO 15919
transliteration, checked against the script by `tamil_to_iso`.

**Where it is weakest.** The date of the text is uncertain (4th to 6th century AD, with earlier
estimates), so the reading is "an approximation of an approximate period" (manifest). The values of
c, ṟ, ṟṟ, ḻ and the āytam are the least certain. Sandhi across words is written but not modelled.

**What a specialist could improve.** Consonant allophony and the āytam in `tamil.py`, with a named
reconstruction; the transliterations in `texts/tamil-tirukkural/edition.yaml`.

## Runic inscriptions (Proto-Norse and Old East Norse)

**Scheme.** `as-carved`, "As carved: Proto-Norse around 400, Old East Norse around 800". One scheme;
each token's `dialect` (pn or oen) selects the rules. The Proto-Norse z is a buzzing sound; Old
Norse ʀ is "between z and r"; v and w are both w; stress always on the first syllable. There is no
second scheme.

**What it rests on.** The module does not cite a source. Sound is derived from each word's scholarly
normalization in `texts/runes/edition.yaml`, never from the runes, because the younger futhark has
16 runes for about 30 sounds.

**Where it is weakest.** Runes do not mark vowel length or many consonant contrasts; the sound
inherits every choice in the normalization (manifest). The Gallehus runes survive only in
18th-century drawings.

**What a specialist could improve.** The normalizations, with a named edition; the values of z and
ʀ and of the fricatives in `runic.py`; a citation for the scheme as a whole.

## Old English

**Scheme.** `west-saxon`, "Late West Saxon, around the year 1000". One scheme. Stress on the first
syllable of the root; ge-, be- and, on verbs, a-, for-, of-, on-, to-, un-, ymb- unstressed.
Palatal c and g, sc, cg, voicing of f s þ between voiced sounds, and h by position.

**What it rests on.** Consonant rules after Mitchell and Robinson, *A Guide to Old English*
(module). Vowel length comes from the edition's marks (Harrison and Sharp), corrected by
`pipeline/weft/data/ang_quantities.yaml` (values after Clark Hall, *A Concise Anglo-Saxon
Dictionary*), then from the hand-annotated lemma, whose macrons carry over along a shared prefix.
`ang_prefixes.yaml` lists prefixes the rules cannot see without the part of speech.

**Where it is weakest.** Palatal c and g are inferred from spelling; an edition that dots them
would remove the guess (manifest). Forms that diverge from their lemma before the last macron are
reported `quantity-uncertain`. Compound stress relies on the editor's hyphens.

**What a specialist could improve.** The quantity table (three entries at present) and the prefix list;
the palatalization rules in `oldenglish.py`; a second scheme, since none is offered.

## Old Norse

**Schemes.**
- `old-norse`, "Old Norse: reconstructed Old Icelandic, around 1200" (Snorri's manifest relabels it
  "around 1220"). Long vowels pure and long; ö read as ǫ; v as w; f as v between voiced sounds; g
  a fricative after a vowel; hv as xw; hl, hr, hn voiceless. Stress on the first syllable.
- `modern-icelandic`, "Modern Icelandic: how the Edda is read aloud in Iceland today": á ow, é ye,
  au öy, ll tl, nn tn after a long vowel, hv kv, epenthetic u before final r.

**What it rests on.** E. V. Gordon, *An Introduction to Old Norse*, and Haugen (module; no Haugen
title is given). The normalized spelling marks length, so no quantity table is used.

**Where it is weakest.** The editions' ö covers both ǫ and ø and is read as ǫ by default (Eddic
and Snorri manifests). For Snorri, ǫ and ø were merging about 1220 and long vowels may have begun
to change. Grettis saga is read from IcePaHC's modern Icelandic spelling, so its Old Norse reading
is reconstructed from modern forms; its notes date the saga to about 1310, later than the scheme.

**What a specialist could improve.** A per-word distinction of ǫ and ø; rules in `norse.py` for a
later date (about 1300) as a separate scheme; old forms for Grettis saga.

## Old East Slavic

**Schemes.**
- `orv1100`, "Old East Slavic about 1100 (approximate)": the language of Rus' when the chronicle was
  compiled in Kiev. The jers ъ and ь are still sounded, as very short vowels; ѣ is a close e,
  distinct from е; ѧ and ꙗ are the same sound as я, the nasal vowels having been lost; ы is a back
  i; г is a stop; consonants before ь, я and ю are soft; syllables are open. Both schemes read the
  hand-typed reading form `n` of the edition (abbreviations written out, superscripts lowered), not
  the manuscript spelling.
- `ru`, "Read as Russian today (a convention)": the text as a reader of Russian reads it aloud in a
  class on the history of the language: ъ silent, ь a soft consonant, ѣ as е, modern vowel
  reduction, final devoicing. A convention of reading, not a reconstruction.

**What it rests on.** The handbooks of Russian historical phonology, which rest on the spelling of
dated manuscripts and birchbark letters: Shakhmatov; Kuznetsov; Shevelov, *A Prehistory of Slavic*
(1964); Schenker, *The Dawn of Slavic* (1995) (module). The text is Weft's transcription of the
Laurentian copy of 1377 as printed by Karsky in *Полное собрание русских летописей*, vol. 1 (1926),
checked against the OCR of the scan with declared corrections (manifest). No treebank is used:
TOROT covers the chronicle but is licensed NC (manifest).

**Where it is weakest.** The jers: their loss in weak position is dated to the 12th century, so at
1100 the weak ones were fading, and the scheme treats every written jer alike; the module calls this
its weakest point. The value of ѣ varied by region, and г in Kiev was probably a fricative, which is
not shown. The manuscript does not mark stress; it is hand-entered in `n` from the stress of the
same words in Russian and Ukrainian and from the accent paradigms of the handbooks (module and
manifest). Softening before е, ѣ and и is assumed and not marked. The years, written in letter
numerals, are read as numbers; the number words are not reconstructed (manifest).

**What a specialist could improve.** The stress marks in `texts/primary-chronicle-varangians/edition.yaml`;
the jer rule and a southern variant with fricative г in `oldeastslavic.py`; the regional value of ѣ.

## Persian

**Schemes.**
- `early`, "Early New Persian: as spoken around 1100 (approximate)": majhul ē and ō kept apart from
  ī and ū; w as [w]; xw a rounded kh; the old diphthongs ay and aw; q and ġ distinct; d after a
  vowel in the same morpheme as ð. Stress by the modern rules.
- `modern`, "Modern Iranian Persian": the mergers, æ and ɒ, v for w.

**What it rests on.** The grammarians, early manuscripts, and Dari and Tajik (module). The notes
cite Lazard, *La langue des plus anciens monuments de la prose persane* (1963), for phonology, and
Whinfield's notes; the rubāʿī metre follows Elwell-Sutton, *The Persian Metres* (1976), and
Farzaad's division of the line. The sound is computed from a hand transliteration that writes every
vowel.

**Where it is weakest.** Stress is placed by the modern rules, "the least certain part of the
reconstruction" (module); the ð rule and the vowel qualities are approximate (manifest). Short
vowels are supplied from Whinfield's notes, the metre and the dictionaries and are checked against
the script only for its letters. The metre's licences are a reciter's judgment.

**What a specialist could improve.** The stress rule and the ð rule in `persian.py`; the
transliterations in `texts/persian-rubaiyat/edition.yaml`.

## Middle Mongolian

**Scheme.**
- `mm-1250`, "Middle Mongolian, mid-13th century (approximate)", the only scheme: vowels a e i o u ö
  ü, with ö and ü front rounded; stops and affricates contrast in aspiration rather than voicing;
  q uvular and γ a voiced uvular fricative; h a plain h; two vowels in hiatus said as two
  syllables; stress on the first syllable. There is no second scheme because a modern Khalkha
  reading would mean substituting modern words, not reading these (module).

**What it rests on.** The Ming transcription itself: which Chinese characters the transcribers chose
for which sounds (aspirated initials for t, č, k, q and unaspirated for d, j, g, b, as Shiratori's
preface also notes); the Uyghur-script spelling of later Mongolian; and comparison with modern
Mongolian (module). The sound is derived from the romanization row, not from the Chinese characters
read aloud. That row is Shiratori's romanization (1943) converted by rule into current conventions
and hand-corrected for eighteen words, each correction marked in the word's provenance (module and
manifest). Two sensors test it against the Ming spelling: the shoulder marks 舌 and 中 (every r has
its mark, every mark its r or q) and vowel harmony (manifest).

**Where it is weakest.** The whole scheme is a reconstruction (manifest `sound_confidence: low`). The
aspiration contrast is inferred from the Chinese characters; the hiatus written ' may already have
been a long vowel by the 14th century, and the scheme does not decide where; first-syllable stress
is assumed and not attested for the period (module and manifest). The romanization is a
transcription of the Ming spelling, not a reconstruction of the lost Uyghur-script original. The
shoulder-mark sensors report disagreements as telemetry rather than failures, because the base text
sometimes omits a mark.

**What a specialist could improve.** The conversion rule and the eighteen `n` overrides in
`texts/secret-history-mongols/edition.yaml`; the vowel values and the aspiration reading in
`mongolian.py`; evidence for where hiatus had become length.

## Japanese

**Schemes.**
- `edo-1686`, labelled in the manifest "Edo, 1680s and 1690s: as Bashō's contemporaries spoke
  (approximate)": medial は as wa; づ and ぢ as dzu and dji; え, ゑ and medial へ as ye; medial -afu
  as ō.
- `modern`, standard Hepburn.

Hyphens divide morae; pitch accent is not marked in either scheme.

**What it rests on.** Reconstructions that keep づ and ぢ distinct into the 1600s, and the
Portuguese missionaries' spellings around 1600 (Rodrigues) for ye (module). The sound is computed
from each token's reading in historical kana.

**Where it is weakest.** The dzu of づ, the ye of え and ゑ, and the ō of medial -afu are each
uncertain by the 1680s (manifest and key). The module reads a token written only は as the
particle wa; a noun spelled は alone would be misread. Pitch accent is absent.

**What a specialist could improve.** The three uncertain rules in `japanese.py`; pitch accent, if a
period source supports it; the kana readings in `texts/basho-furuike/edition.yaml`.

## Old French and Franco-Italian

**Schemes.**
- `fr1300`, "French about 1300: the language the book is written in (approximate)": final e sounded,
  s before a consonant silent with a long vowel, final consonants dropped before a consonant, oi as
  [wɛ], affricate ch and j, nasal vowels with the nasal still sounded, tongue-tip r.
- `it1300`, "Franco-Italian read by an Italian about 1300 (hypothesis)": every letter sounded with
  its Tuscan value, no nasal vowels, French stress kept.

**What it rests on.** Nyrop, *Grammaire historique de la langue française*, vol. 1 (1899), and Pope,
*From Latin to Modern French* (1934) (module and notes). The sound comes from
`pipeline/weft/data/fro_lexicon.yaml`, keyed by a hand normalization into central French spelling.
For `it1300`, the spelling of Franco-Italian manuscripts; the module states that no grammarian of the
period describes such a reading.

**Where it is weakest.** When final consonants fell silent before consonants, and whether ch and j
were still affricates (manifest; the module calls the first "the weakest point of the scheme").
`it1300` is a hypothesis. The speech of the writers (a Venetian and a Pisan) is not modelled.

**What a specialist could improve.** Lexicon entries; the final-consonant rule in `oldfrench.py`;
evidence for or against the Italian reading.

## Italian

**Schemes.**
- `florentine`, "Florentine of the author's day (approximate)", dated per work by the manifest
  (about 1307, 1350, 1513). One reconstruction for all three dates, because the module finds no
  per-word difference the evidence supports. Open and closed e and o from the lexicon; s between
  vowels voiceless unless marked; no gorgia toscana; no syntactic doubling.
- `modern`, "Standard modern Italian": the same, with s between vowels voiced.

**What it rests on.** `pipeline/weft/data/it_lexicon.yaml`, following the DOP (Migliorini,
Tagliavini, Fiorelli, *Dizionario d'ortografia e di pronunzia*), checked against the Latin source
vowel (module). The notes add Migliorini, *Storia della lingua italiana* (1960), and Izzo, *Tuscan
and Etruscan* (1972).

**Where it is weakest.** The vowel lexicon is built on the modern Tuscan standard; learned words are
less certain for these dates. Latinizing spellings are read as written, which may be ornament rather
than speech. The gorgia is left out as not securely attested this early (module and all three
manifests).

**What a specialist could improve.** Lexicon entries, especially those marked `# learned`; a
separate scheme for 1513 if the evidence supports one; the metre rules for synaeresis and dialefe.

## Portuguese

**Schemes.**
- `lisboa1540`, "Lisbon about 1540: Oliveira's and Barros's day (approximate)": four sibilants (dental ç and z,
  apical s and ss), ch still the affricate, unstressed vowels unreduced except a final o read u, ei and ou
  still diphthongs, a trilled r, final -em a plain nasal e.
- `europeu`, "Modern European Portuguese (Lisbon)": unstressed a, e, o reduced to [ɐ ɨ u], ei as [ɐj], ou as
  [o], uvular r, s at the end of a syllable [ʃ].
- `brasileiro`, "Modern Brazilian Portuguese (São Paulo norm)": final e and o as [i u], t and d before [i] as
  [tʃ dʒ], syllable-final l as [w], initial r as [h].

All three read one normalized spelling per word, written by hand in `pipeline/weft/data/pt_lexicon.yaml`
with the stressed e and o marked for quality; a stressed e or o left unmarked is reported.

**What it rests on.** Fernão de Oliveira, *Grammatica da lingoagem portuguesa* (1536), and João de Barros,
*Grammatica da lingua portuguesa* (1540), the first native descriptions of the sounds; Paul Teyssier,
*História da língua portuguesa* (1980), and Ivo Castro, *Introdução à história do português* (2006), for the
dating of the changes (module). Stress follows the written rule of modern Portuguese.

**Where it is weakest.** The final unstressed o read u in 1540, which Teyssier dates to that century but
not to a year; the exact values of the apical and dental sibilants; the metre's elisions, which are not
modelled since each word is sounded alone (manifest). Camões's own speech is not modelled.

**What a specialist could improve.** The quality marks in the lexicon; the unstressed-vowel rules of the
1540 scheme in `portuguese.py`; a rule for synalepha in the decasyllable.

## Spanish

**Schemes.**
- `c1492`, "Castilian about 1492: Nebrija's day (approximate)": six sibilants (ts, dz, s, z, ʃ, ʒ),
  aspirated h from Latin f, b and v distinct, modern stress.
- `modern`, "Modern Castilian".

**What it rests on.** Nebrija, *Gramática de la lengua castellana* (1492) and *Reglas de
orthographía* (1517), and his *Vocabulario* for aspirated h; Lapesa, *Historia de la lengua
española*; Penny, *A History of the Spanish Language* (module). The sound comes from
`pipeline/weft/data/es_lexicon.yaml`, a normalized period spelling per word.

**Where it is weakest.** The value of h from Latin f, the b and v distinction, and the quality of the
sibilants (manifest). How far ts and dz had lost their stop element by 1492 is uncertain (module).
Columbus's own Genoese and Portuguese-coloured speech is not modelled.

**What a specialist could improve.** Lexicon entries; the b and v assignments word by word.

## Dutch

**Schemes.**
- `h1596`, "Holland Dutch about 1596: Linschoten's day (approximate)": ij as [ei] kept apart from ei,
  ui [øy], ou and au [ɔu], g [ɣ], -en with its n, final devoicing, trilled r.
- `modern`, "Modern Standard Dutch".

**What it rests on.** The *Twe-spraack vande Nederduitsche letterkunst* (1584); de Heuiter,
*Nederduitse orthographie* (1581); Schönfeld, *Historische grammatica van het Nederlands*, revised
by van Loey (1959); de Vooys, *Geschiedenis van de Nederlandse taal* (1952) (module). Syllables and
stress come from `pipeline/weft/data/nl_lexicon.yaml`.

**Where it is weakest.** Whether ij was a diphthong or still [iː] in Amsterdam in 1596; the n of -en;
the stress of French and Latin loans (manifest). The sound is computed from modern spelling, so the
sharp-long and soft-long ee and oo are not shown.

**What a specialist could improve.** Lexicon entries; the two long ee and oo, if a per-word source
exists.

## French

**Schemes.**
- `m1580`, "French about 1580: Montaigne's day (approximate)": liaison, s before a consonant silent,
  oi as [wɛ], un as [ỹ], nasal vowels before a following vowel, e caduc counted, tongue-tip r.
- `fr1791`, "French of 1791: a Paris reading (approximate)", for Olympe de Gouges's Declaration of the Rights
  of Woman: the modern values for nearly everything, after Féraud's dictionary of 1787-88 (oi already [wa] in
  loi and droit, the Paris uvular r, final consonants silent as today), with l mouillé, the palatal l of filles,
  still a lateral; written in the lexicon only where a word differs.
- `fr1885`, "French of the 1880s: formal Paris reading", for the General Act of the Berlin Conference
  (1885): close to modern French, with the differences the period's phoneticians record: long
  vowels in a final syllable closed by r, z, zh or v and in many words with a circumflex; a back a
  where Littré marks one (pas, droits); more liaisons in formal reading (marked `zf` in the
  edition); a few words whose final consonant was then silent (but); the uvular r.
- `modern`, "Modern French".

No syllable is capitalized: the module states that French has no distinctive word stress.

**What it rests on.** For `fr1791`: Féraud, *Dictionnaire critique de la langue française* (1787-88), and the
grammarians of the decade as collected by Thurot (module). For `m1580`: Meigret (1542, 1550), Peletier du Mans (1550), Ramus (1562, 1572), Bèze
(1584) and Henri Estienne (1578), as collected by Thurot (1881-1883); Palsgrave (1530) on final
consonants (module). For `fr1885` the evidence is direct, not reconstructed from rhymes or spelling:
Passy, *Les sons du français* (1887), the transcriptions of *Le Maître phonétique* (from 1886), and
Littré's *Dictionnaire de la langue française* (1863-1872), which gives a pronunciation for each
word (module). The sound comes from `pipeline/weft/data/fr_lexicon.yaml`; where the lexicon has no
`fr1885` form, the word is taken from its modern form with the length rule applied.

**Where it is weakest.** `m1580`: the value of oi, the r of -er infinitives, and the strength of the e caduc
(manifest). Montaigne's Gascon-coloured speech is not modelled. `fr1885`: vowel length is shown for
the word said alone and was reduced inside a phrase; the optional liaisons of formal reading are
marked by judgment, following Littré where he gives a note; the scheme models the Paris norm of the
language the Act was written in, not the accents of the delegates, who were not French (manifest).

**What a specialist could improve.** Lexicon entries, including `fr1885` forms from Littré; the
liaison exceptions (`nz`) and formal liaisons (`zf`) in the editions; the length rule in `french.py`.

## German

**Schemes.**
- `northern`, "Educated northern German before the stage norm (approximate)", relabelled per work
  (Königsberg in the 1780s for Kant; the 1880s for Nietzsche): final g a fricative, trilled r,
  long ä kept apart from long e, modern vowel length.
- `ecg1545`, "East Central German of the 1540s, Wittenberg (approximate)", for Luther's Bible:
  new diphthongs, ie as long [iː], lenis p and t, bilabial w, final -e said. Computed from the
  1545 form of each word.
- `modern`, "Modern Standard German" (Duden).

**What it rests on.** For `northern`: Viëtor, *Die Aussprache des Schriftdeutschen* (1885); Siebs,
*Deutsche Bühnenaussprache* (1898); von Polenz, *Deutsche Sprachgeschichte*, vols. 2 and 3. For
`ecg1545`: Luther's own spelling and the Saxon chancery usage; Ickelsamer (1527, about 1534);
Frangk, *Orthographia* (1531); von Polenz, vol. 1; Besch, *Luther und die deutsche Sprache* (2014)
(module). Syllables and stress come from `pipeline/weft/data/de_lexicon.yaml`. Kant's Latin phrases
are given in the German school pronunciation of Latin (manifest).

**Where it is weakest.** `northern`: postvocalic r and long ä (manifests); no description of either
author's speech; regional features not modelled. `ecg1545`: the diphthong values, the extent of the
p/b and t/d merger, the value of w, and whether unrounding of ü and ö reached a reading of
Scripture (manifest). Dauid with f is a judgment (manifest).

**What a specialist could improve.** Lexicon entries, including old vowel lengths where they differ
from modern ones; the lenis rule and w in `german.py`.

## Swahili

**Schemes.**
- `z1870`, "Zanzibar Swahili about 1870: Steere's day (approximate)": Steere's letters read by the
  values his Handbook gives them. Five vowels, each its own syllable, e and o open; a and e run
  together into a long e where they meet before a consonant; m and n before most consonants form a
  syllable of their own and can carry the accent; double consonants in Arabic loans sounded as
  written; the accent on the last syllable but one.
- `modern`, "Modern Standard Swahili": the same rules applied to the modern standard form of each
  word, typed by hand in `n`, without the a + e coalescence. The standard was fixed in the 1930s on
  the Zanzibar town dialect, so the two schemes differ mainly where the spelling of a word has
  changed (hatta/hata, assubui/asubuhi). The modern form changes spelling and the shape of a word,
  never its grammar (module).

**What it rests on.** Steere's own account of his spelling in *Swahili Tales* (1870), preface,
p. xiv ("the vowels are pronounced as in Italian, the consonants as in English, and ... there is
always an accent on the last syllable but one"), and the letter values in *A Handbook of the Swahili
Language as Spoken at Zanzibar*, third edition (1884), pp. 8-15 (module). The text is Weft's
transcription from the page scans, checked against the Wikisource transcription and the OCR, with the
OCR's misreadings declared token by token (manifest).

**Where it is weakest.** The Handbook used is the third edition, revised by Madan after Steere's
death, and no recording exists (manifest). Not modelled: the aspirated p, t and k Steere hears where
a nasal has been lost; the implosive b, d and g that later descriptions report; tone and intonation
(module). The long consonants of Arabic loans are uncertain, since the Handbook notes a tendency to
drop one of them (module and manifest).

**What a specialist could improve.** The syllabic-nasal rule and the a + e coalescence in
`swahili.py`; the modern forms in `texts/swahili-tales-steere/edition.yaml`; aspiration where a
nasal was lost.

## Esperanto

The first invented language in the public library, and the second (after Tolkien's, private) whose
author wrote down its pronunciation. Zamenhof's Unua Libro (1887) gives the alphabet with a sound for
each letter and the rule that the accent falls on the last syllable but one; the Fundamento (1905)
fixed both (rules 9 and 10). So the one scheme is the author's rule, not a reconstruction:

- `zamenhof`, "As Zamenhof described it: Unua Libro (1887), Fundamento (1905)": a e i o u one sound
  each; c ts, ĉ ch, ĝ j, ĥ the ch of Bach, ĵ the j of French jour, ŝ sh, ŭ w, j y, r trilled, g and
  s always hard; aj ej oj uj aŭ eŭ one syllable; stress on the penult, an elided final o (kor’, l’)
  leaving it where it was.

What the rule leaves open and Weft decides: the exact vowel qualities (Zamenhof gave them by
comparison with other languages), and where a consonant cluster divides between syllables (es.tas,
pa.tro: s + stop divides, obstruent + liquid holds). No lexicon is needed; the sound follows from the
letters. The module also reads the grammar: the 1887 print divides each word into its parts
(Patr'o ni'a), and `esperanto.analyze` turns the division into lemma and Universal Dependencies
features by the Fundamento's rules, which the overlay declares as an automatic analysis checked by
hand. The 1887 spellings that differ from later usage (Si for Ŝi, tranquil- for trankvil-) are kept
in t with the regular form in n.

## Quenya and Sindarin (Tolkien)

No public work is in either language: Tolkien's texts are in copyright until 2043, so Namárië and
the hymn to Elbereth exist only as private works built from a reader's own copy (`private/README.md`).
The module is public because it states pronunciation rules and holds no text.

**Scheme.**
- `tolkien`, "As Tolkien described it: Appendix E (1955)", the only scheme: c always k, qu kw, ch
  the sound of German bach, dh and th as in these and thin, r trilled everywhere, s always voiceless,
  f at the end of a word v; a e i o u as in father, were, machine, for, brute, long with the acute
  (Quenya long é and ó closer than the short vowels; Sindarin long vowels the same quality held);
  Sindarin y the French u; the diphthongs ai au eu iu oi ui (Quenya) and ae ai ei oe ui au
  (Sindarin), all falling; every other vowel pair two syllables; final e always sounded. Stress by
  Tolkien's rule: the first of two syllables; otherwise the last but one when it holds a long vowel,
  a diphthong or a vowel before two consonants, else the third from the end.

**What it rests on.** Appendix E, part I, "Pronunciation of Words and Names", in The Lord of the
Rings (1955): the author's own account of how his transcription is to be read. This is the one
language in the library whose author wrote down its pronunciation, so the scheme is a statement of
his rules rather than a reconstruction. The twelve stress examples Tolkien gives there are the
module's regression tests, and so are the stress marks he printed on Namárië in The Road Goes Ever
On (1967), as recorded word by word in Eldamo (P. Strack, eldamo.org): the module reproduces every
one. Lemma and gloss in the private works follow Tolkien's own word glosses through Eldamo's
citations to the page and line; Eldamo's neo-Eldarin forms (fan reconstructions) are never used.

**Where it is weakest.** Appendix E gives letter values "approximately" and only by English
keywords, so the IPA is broad. The quality of Sindarin ae and oe is not described (the respelling
reads them as ai, oi, which Appendix E allows). Written th in Quenya is read θ, though Tolkien says
the sound had become s in speech. Secondary stress in compounds, which Tolkien marks with a grave
in 1967, is not shown. Tolkien's 1952 recordings are not used: they differ from the printed text in
places and are a performance, not a rule.

**What a specialist could improve.** The digraph list and the syllable split in `elvish.py`;
whether ly, ny, ry count as one consonant or two for stress (Tolkien's 1967 marks on ómaryo and
Calaciryo support two, as the module has it); the Sindarin long-vowel qualities.

## Open inconsistencies

Known inconsistencies between the modules, the manifests and other documentation, listed so a
reviewer can weigh them. Several found while this page was written have been corrected (the Koine
and Tang labels on later or earlier texts, the Akkadian and runic language names, the scanner notes,
the README sample respelling, the Grettis saga scheme order, a Spanish key example).

- **Homer.** The Iliad and Odyssey pages open in `restored`, 5th-century Attic, and their labels
  say it stands in for the poet's own Greek; no archaic scheme exists.
- **Confidence is uneven within a scheme.** `italian-humanist` is medium for Inter caetera and not
  set for Pico. `old-norse` is medium for Snorri and not set for the three Eddic poems and Grettis
  saga (whose manifest calls its reading approximate). Of the national Latin schemes only
  `anglo-norman` and Inter caetera's `italian-humanist` set a value, though the module labels all of
  them approximate. Homer, Bashō, Genesis, the Koine works, Beowulf and every Italian, Spanish, Dutch,
  French and German work set none, although their manifests or modules call the first scheme
  reconstructed or approximate. Which pages carry the invitation is a policy still to be settled.
- **Swahili manifest.** Its predicted gaps say the morphology display does not decode `NounClass`
  or `Aspect`; `treebank.py` now decodes both, so the page shows the class and the aspect, and the
  gap text is out of date until the work is next drafted.
- **Latin docstring.** The opening docstring of `latin.py` describes two schemes and stress "in both
  schemes"; seven more were added later, and the French method of `as-first-read` puts stress on
  the last syllable.
