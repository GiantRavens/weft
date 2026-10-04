<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="art/weft-lockup-reverse.svg">
    <img alt="Weft" src="art/weft-lockup.svg" width="320">
  </picture>
</h1>

<p align="center"><strong><a href="https://weftlibrary.org/">Read the library</a></strong> · <a href="docs/about.md">About Weft, for readers and scholars</a> · <a href="docs/languages.md">Languages and pronunciation</a></p>

Living interlinear editions of classical texts. Every line of the source is stitched to
its sound, its literal word-for-word gloss, and one or more published translations,
with scholarly notes attached to the words themselves.

    Ἄνδρα     μοι      ἔννεπε,   Μοῦσα,   πολύτροπον,        ὃς     μάλα    πολλὰ
    AN-dra    moy      EN-ne-pe  MOO-sa   po-LÜ-tro-pon      hos    MA-la   pol-la
    man       for-me   tell      Muse     of-many-turns      who    very    many-things

    Tell me, O Muse, of that ingenious hero who travelled far and wide   (Butler, 1900)

The name: the weft is the thread carried back and forth across the warp. The source text is the warp;
sound, gloss and sense are the weft that turns it into cloth. Dedicated to Neith, goddess of the loom,
and to my mother.

## The four layers

| Layer   | What it is                                                | Source of truth              |
|---------|-----------------------------------------------------------|------------------------------|
| source  | the text in its own script, pinned to one edition         | Perseus / PROIEL / Menota    |
| sound   | pronunciation respelling, derived from IPA per scheme      | rules over the orthography   |
| gloss   | one English cell per source word, order preserved         | treebank lemma + lexicon     |
| sense   | published translations, any number, each attributed       | public domain editions       |

Later layers: metre, notes, audio. Layers are named, never numbered.

## Principles

- **Text as code.** Every passage is a YAML file under `texts/`, addressed by CTS URN, versioned in git.
- **Generated and curated never share a file.** `gen/` is regenerable by the pipeline. `curated/` is a sparse human overlay that wins on conflict and carries attribution.
- **Provenance on every field.** Each value says what produced it and how confident it is.
- **Translations are a list, not a slot.** Adding one costs one alignment pass.
- **Public and private builds from one codebase.** Your own material lives in `private/` (gitignored): licensed translations, your own annotations and notes, and whole private works. It appears only in your own build (`weft build all --private`); see `private/README.md`.
- **No framework.** The site is static HTML, CSS and JS that works offline and prints.

## Layout

    texts/<work>/manifest.yaml   what, from where, which schemes, predicted gaps
    texts/<work>/sources/        raw fetched files, hashed, never edited, never in git (weft acquire)
    texts/<work>/gen/            machine output, fully regenerable
    texts/<work>/curated/        human overlay, sparse, wins on conflict
    texts/<work>/notes/          harvested and authored commentary
        private/                     your own layer: licensed material and private works, never committed
    pipeline/                    the lifecycle steps as CLI commands
    site/                        renderer
    docs/                        about (for readers), languages, lifecycle, schema; about and languages
                                 are also built into the site as about.html and languages.html

## Viewing

The library is published to GitHub Pages on every push to `main`, at its own domain:
<https://weftlibrary.org/> (the older address giantravens.github.io/weft redirects there). The workflow in `.github/workflows/pages.yml` runs the
tests, builds every work with `weft build all`, and deploys `site/build/`. It needs no source
files, because the build reads only what is committed.

Each page is also a single self-contained file. `site/build/<work>.html` opens from disk with no
server, so a page or the whole folder can be sent as an attachment.

## Quickstart

    uv venv && uv pip install -e .
    .venv/bin/weft acquire homer-odyssey    # lists each source and its license; nothing downloads yet
    .venv/bin/weft acquire homer-odyssey --accept-licenses   # fetch, verify sha256 against the manifest
    .venv/bin/weft draft homer-odyssey      # text, lemma, morph, sound -> gen/, telemetry -> gen/*.run.yaml
    .venv/bin/weft check homer-odyssey      # selftest: every token has every layer, every reference resolves
    .venv/bin/weft build homer-odyssey      # -> site/build/homer-odyssey.html, opens from file://
    .venv/bin/weft build homer-odyssey --private   # adds licensed translations from private/
    .venv/bin/weft say πολύτροπον ψυχὴν      # phonemize words in every scheme

## Status

Sixty-one works built across twenty-six languages, oldest first in the library:

| Work | Passage | Schemes | Translations |
|---|---|---|---|
| Pyramid Texts of Unas, PT 273 | columns 496-509, the opening of the 'Cannibal Hymn' | Old Egyptian (conjectural), Egyptological convention; hieroglyphs generated | Breasted 1912, Topmann (TLA, German), Weft editorial; Faulkner 1969 and Allen 2005 cited |
| Enheduanna, Temple Hymn 5 | the E-šumeša of Ninurta at Nippur, 19 lines | Sumerian (conjectural, after Jagersma), Assyriological convention; cuneiform generated | Weft editorial; Sjöberg and Bergmann 1969, ETCSL, Meador 2009, Helle 2023 cited |
| Laws of Hammurabi, prologue | column I, lines 1-53 | Old Babylonian (reconstructed), classroom Akkadian; cuneiform row generated | Harper 1904, King 1910 |
| Rigveda 1.1, Hymn to Agni | 9 verses | Vedic (with the pitch accent), modern Indian | Griffith 1896, Wilson 1850 |
| Homer, Iliad | 1.1-52 (proem, Chryses, the plague); metre generated by a hexameter scanner | restored, Erasmian | Butler 1898, Lang, Leaf and Myers 1883 |
| Homer, Odyssey | 1.1-10 | restored, Erasmian | Butler 1900, Butcher and Lang 1879 |
| Aristotle, Metaphysics | A.1, 980a21-27 | restored, Erasmian | Taylor 1801, M'Mahon 1857 |
| Genesis (Bereshit) | 1:1-2:3, the creation account | Tiberian, modern Israeli | JPS 1917, Geneva 1599, King James 1611 |
| Daniel 5: Belshazzar's feast | the whole chapter (Hebrew numbering, 30 verses), in Biblical Aramaic | Tiberian, modern reading | JPS 1917, Geneva 1599, King James 1611 |
| Gospel of John | 1:1-18, the prologue | Koine, Erasmian | Tyndale 1534, Geneva 1599, King James 1611 |
| The Beatitudes (Matthew 5:3-12) | 10 verses | Koine, Erasmian | Tyndale 1534, Geneva 1599, King James 1611 |
| 1 Corinthians 13 | the whole chapter | Koine, Erasmian | Tyndale 1534, Geneva 1599, King James 1611 |
| The Nicene-Constantinopolitan Creed | the exposition of the 150 fathers (381), the conciliar text in the plural | Koine of 381, Erasmian | Schaff 1877 |
| Ovid, Metamorphoses | 1.1-9 | classical, ecclesiastical | Golding 1567, More 1922 |
| Res Gestae Divi Augusti | heading, chapters 1-4, 34-35 | classical (Rome under Augustus), ecclesiastical | Fairley 1898, Shipley 1924 |
| Yijing (I Ching), the Zhouyi | all 64 hexagrams: names, judgments and line statements; a three-coin casting panel | Old Chinese (Baxter-Sagart), Tang, Mandarin | Legge 1882; Wilhelm and Baynes 1950 cited |
| Sunzi, The Art of War | chapter 1, Laying Plans | Old Chinese (Baxter-Sagart), Tang, Mandarin | Giles 1910, Calthrop 1908 |
| Daodejing (Laozi) | chapters 1-2 | Old Chinese (Baxter-Sagart), Tang, Mandarin | Legge 1891, Chalmers 1868 |
| The Gospel of Mark in Sahidic Coptic | 1:1-20 | Sahidic (approximate, 4th-5th c.), Bohairic church reading | Horner 1911 (from the Coptic), King James 1611 |
| Epictetus, Enchiridion | 1.1-3 | Koine, restored, Erasmian | Long 1877, Higginson 1865 |
| Marcus Aurelius, Meditations | Book 2, complete | Koine, restored, Erasmian | Long 1862, Casaubon 1634 |
| Völuspá (Poetic Edda) | complete, stanzas 1-66 | Old Norse, modern Icelandic | Bellows 1923, Thorpe 1866 |
| Hávamál (Poetic Edda) | stanzas 1-80, the guest's wisdom | Old Norse, modern Icelandic | Bellows 1923, Thorpe 1866 |
| Þrymskviða (Poetic Edda) | complete, stanzas 1-32 | Old Norse, modern Icelandic | Bellows 1923, Thorpe 1866 |
| Fáfnismál (Poetic Edda) | complete, 44 stanzas and the prose links | Old Norse, modern Icelandic | Bellows 1923, Thorpe 1866 |
| Snorri, Gylfaginning (Prose Edda) | chapters 5-8, the making of the world from Ymir; 49, the death of Baldr | Old Norse (about 1220), modern Icelandic | Brodeur 1916, Anderson 1880 |
| Li Bai, Quiet Night Thought | 4 lines | Tang, Mandarin, Cantonese | Cranmer-Byng 1909 |
| Tirukkural | chapter 1, kurals 1-10 | Old Tamil (reconstructed), modern | Pope 1886, Drew 1840 |
| Runic inscriptions: Kylver, Gallehus, Rök | 3 inscriptions | Proto-Norse, Old East Norse | Stephens 1884; Weft editorial reading |
| Beowulf | 1-11 | late West Saxon | Gummere 1910, Morris and Wyatt 1895 |
| Rubaiyat, quatrains attributed to Omar Khayyam | 6 quatrains | Early New Persian (about 1100), modern Persian | FitzGerald 1889, Heron-Allen 1899 |
| Marco Polo, on Cipangu (Japan) | the whole chapter, F text | Franco-Italian: French of about 1300, and an Italian reader's reading | Yule 1903, Marsden 1818 |
| Bayeux Tapestry, the embroidered captions | 24 scenes, Edward to the English in flight; a picture of each scene | Anglo-Norman Latin (about 1070), classical | Fowke 1898, Bruce 1856 (partial) |
| The Rus' Primary Chronicle: the calling of the Varangians | annals 859-862 | Old East Slavic about 1100 (approximate), modern Russian reading | Cross 1930; Cross and Sherbowitz-Wetzor 1953 cited |
| The charters of Saer de Quincy, earl of Winchester | two grants: Gask to Brackley Hospital (1218-19) and Duglyn to Cambuskenneth (c. 1207-14) | Anglo-Latin (England, early 13th c.), classical | the 1908 and 1872 editors' English abstracts, Weft editorial |
| Magna Carta | chapters 39-40 | Anglo-Latin (England, 1215), classical | McKechnie 1905, Bell 1910 |
| The Secret History of the Mongols | sections 1-10, the wolf and the doe to Alan Qo'a's sons; Ming transcription with its own word glosses | Middle Mongolian about 1250 (reconstructed) | Weft editorial, the Ming summary translation; de Rachewiltz 2015 cited |
| Dante, Inferno 1 | the whole canto, 136 lines | Florentine (about 1307), modern Italian; lemma and form from UD Italian-Old | Longfellow 1867, Cary 1814 |
| Pero Vaz de Caminha, letter on the finding of Brazil | folios 1r-3r (1 May 1500): the salutation, the sighting of Monte Pascoal, the first men on the beach, the reef harbour, and the description of the people, with their lip-plugs and feather head-dress; the manuscript's spelling | Lisbon about 1500-1540, modern European, modern Brazilian | Weft editorial (draft); Greenlee 1938 cited |
| Columbus, letter of 1493 | the landfall and first description | Castilian of about 1492, modern Spanish | Major 1870, Quaritch 1893 |
| Petrarch, Canzoniere 1 | sonnet, 14 lines | Florentine (about 1350), modern Italian | Nott in Bohn 1859, Higginson 1903; Auslander 1931 cited |
| Pico della Mirandola, Oration on the Dignity of Man | opening and God's speech to Adam | Italian humanist Latin (1480s), classical | Greswell 1805 (partial), Weft editorial; Forbes 1948 and Caponigri 1956 cited |
| Alexander VI, the bull Inter caetera | 4 May 1493: the address, Columbus's voyage, the grant and the line | Latin of the papal chancery (Italian manner, 1493), classical | Davenport 1917, Blair and Robertson 1903 |
| Camões, Os Lusíadas | Canto I, stanzas 1-3, the proposition | Lisbon about 1540 (after Oliveira and Barros), modern European, modern Brazilian | Burton 1880; Mickle 1776 cited |
| Erasmus, The Praise of Folly | Folly's opening | Low Countries Latin (about 1500), classical | Wilson 1668, Kennett 1683 |
| Tale of the Heike, the opening | Gion shōja, 11 lines (vulgate text) | as recited about 1371, modern | Sadler 1918 (public domain in the US only), Weft editorial |
| Machiavelli, The Prince | chapters 17-18 | Florentine (about 1513), modern Italian | Marriott 1908, Ricci 1903 |
| Luther's German Bible (1545) | John 1:1-14, Psalm 23 | East Central German of the 1540s, modern German | Tyndale 1534, Coverdale 1535, King James |
| Luther, the Ninety-five Theses | all 95, with the preamble | Latin as read in Saxony (about 1517), ecclesiastical, classical | Works of Martin Luther (Philadelphia, 1915) |
| More, Utopia | Book 1, the sheep that devour men | Tudor English Latin (about 1516), classical | Robinson 1551, Burnet 1684 |
| Linschoten, Itinerario: Japan | chapter 26, opening | Holland Dutch of about 1596, modern Dutch | Phillip 1598 |
| Montaigne, Essais | To the Reader; I.19 opening | French of about 1580, modern French | Florio 1603, Cotton 1685, Hazlitt 1877 |
| Laws for the Military Houses (Buke shohatto) | the 1615 text, 13 articles, with return marks and a whole-line Japanese reading | as read about 1615, modern | Murdoch 1903 (digest, partial), Weft editorial |
| The Akō retainers' statement (the Forty-seven Rōnin) | the declaration of 1703 | Genroku Edo (1703), modern | Mitford 1871, Weft editorial |
| National Assembly, Declaration of the Rights of Man and of the Citizen | the preamble and all seventeen articles (1789), in the official printing's spelling; the text de Gouges answered | Paris reading of 1789, modern | Thomas Paine 1791 (Rights of Man) |
| Da Ponte and Mozart, Le nozze di Figaro | Se vuol ballare, Non più andrai, Voi che sapete and Dove sono (Vienna, 1786) | stage Italian of 1786, modern | Weft editorial (draft); Macfarren and Dent cited |
| Schikaneder and Mozart, Die Zauberflöte | Der Vogelfänger, Dies Bildniß, Der Hölle Rache, In diesen heil'gen Hallen and Ein Mädchen oder Weibchen (Vienna, 1791), from the first edition's spelling | educated German of 1791, modern | Weft editorial (draft); Macfarren and Dent cited |
| Olympe de Gouges, Declaration of the Rights of Woman and of the Female Citizen | the preamble and all seventeen articles (1791), in the pamphlet's spelling | Paris reading of 1791, modern | Weft editorial (draft); Levy, Applewhite and Johnson 1979 cited |
| Rouget de Lisle, La Marseillaise | the six couplets and the refrain of the Chant de guerre pour l'Armée du Rhin (1792), in Fiaux's 1918 printing of the 1792 text | Paris reading of 1792, modern | Weft editorial (draft); the English singing version 'Ye sons of France' (1795, couplets 1-2) |
| Marx and Engels, Manifest der Kommunistischen Partei | the opening, the first lines of section I, the ten measures and the closing call (London, 1848), in the first printing's spelling | educated German of the 1840s, modern | Samuel Moore 1888 (Kerr edition, 1910) |
| Verdi: the Brindisi and Iago's Credo | 'Libiam ne' lieti calici' from La traviata (Piave, 1853) and 'Credo in un Dio crudel' from Otello (Boito, 1887) | stage Italian of Verdi's day, modern | Weft editorial (draft); Macfarren and Hueffer cited |
| Einstein, Is the inertia of a body dependent on its energy content? | the opening (the principle of relativity) and the conclusion (mass as a measure of energy content, L/V²) of the 1905 note | educated German of 1905, modern | Weft editorial (draft); Perrett and Jeffery 1923 cited |
| Kant: What is Enlightenment? and the starry heavens | 1784 essay, opening; 1788 Critique of Practical Reason, conclusion | northern German before 1898, modern German | Richardson 1798, Abbott |
| Science in Latin: Descartes, Newton | cogito (1644); laws of motion (1687) | as first read (French, English manner), classical | Veitch 1853, Motte 1729 |
| Swahili tales from Zanzibar: The Kites and the Crows | the whole tale (Steere 1870) | Zanzibar Swahili about 1870, modern standard | Steere 1870 |
| Nietzsche: the madman and Zarathustra's descent | Gay Science 125 (1882); Zarathustra, prologue 1 (1883) | northern German before 1898, modern German | Common 1909 and 1910, Tille 1896 |
| General Act of the Berlin Conference | the preamble, chapter I (free trade in the Congo basin) and articles 34-35 (effective occupation) | diplomatic French of 1885, modern | Hertslet's Foreign Office translation, American Journal of International Law 1909 |
| Zamenhof, the Unua Libro specimens | the Lord's Prayer, Mi'a pens'o, El Heine and Ho, mi'a kor’ (1887), in the print's divided spelling; the first invented language in the public library | as Zamenhof described it | Weft editorial (draft); the King James prayer |
| Haiku of Bashō | 9 haiku, 1680-1694 | Edo (1680s-90s), modern | Chamberlain 1902, Aston 1899, Hearn 1898 and 1900, Noguchi 1914; Yuasa 1966 cited |
| Grettis saga | chapter 14, sentences 1-9 | Old Norse, modern Icelandic | Morris and Magnússon 1869, Hight 1914 |

Homer, Ovid, John, Grettis saga and the Rigveda take lemma and grammar from treebanks (AGDT, LDT, MorphGNT, IcePaHC, the Vedic Treebank); Aristotle, Epictetus and Marcus Aurelius from GLAUx, an automatic parse, corrected by hand where it errs; Genesis and the Aramaic of Daniel 5 from the Open Scriptures Hebrew Bible; Li Bai from the Kyoto Classical Chinese treebank, with Tang readings from Unicode's Unihan database. No open
treebank covers Eddic or Old English poetry or runic inscriptions, so Hávamál, the complete Völuspá, Þrymskviða, Fáfnismál, Snorri's Gylfaginning, Beowulf and the
runes are hand-annotated and marked draft (see CLAUDE.md rule 3). The runic page adds a script
row, generated from the transliteration, and a labelled Weft translation where no public-domain
modern one exists. The Rigveda page reads the accent strokes of the Devanagari back into pitch
accents, checks them against the transliteration, and computes the gāyatrī metre.

`weft build` also writes `site/build/index.html`, a library page listing every built work.
Glosses, scansion, treebank corrections and editorial notes are drafts awaiting scholarly
review. See `docs/lifecycle.md` and `pin ls`.

## License

Code: MIT (`LICENSE`). Text data under `texts/`: CC BY-SA 4.0 (`LICENSE-DATA.md`), because the
Perseus treebank data is share-alike. Every source records its own license in the work's manifest,
and the sources themselves are fetched by `weft acquire`, never committed.

Corrections, pronunciation fixes, recordings and proposals for new texts are welcome, with or
without git: see `CONTRIBUTING.md`, or open an issue and choose a form.
