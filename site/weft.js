/* Weft renderer. Reads window.WEFT (inlined by `weft build`) and draws the interlinear.
   No framework, no fetch: the page must open from file:// and print. */
(function () {
  "use strict";
  const D = window.WEFT;
  const $ = (s, el = document) => el.querySelector(s);
  // a link or image address that came in with the data: http(s) only (images may also be inline data:)
  const safeUrl = (u, img = false) => (typeof u === "string" && (/^https?:\/\//i.test(u) || (img && /^data:image\//i.test(u)))) ? u : null;
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === "class") el.className = v;
      else if (k === "text") el.textContent = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat()) if (kid != null) el.append(kid);
    return el;
  };

  /* ---------- settings, persisted per viewer */
  const LAYERS = [
    ...(D.lines.some((l) => l.tokens.some((t) => t.script)) ? [["script", D.work.script_label || "Script (runes)"]] : []),
    ["source", "Source text"],
    ...(D.work.show_translit && D.lines.some((l) => l.tokens.some((t) => t.norm)) ? [["translit", D.work.translit_label || "Transliteration"]] : []), ["sound", "Sound"], ["gloss", "Gloss, word for word"],
    ...(D.lines.some((l) => l.reading) ? [["reading", D.work.reading_label || "Reading aloud, whole line"]] : []),
    ["metre", "Metre"], ["sense", "Translations"], ["notes", "Note markers"],
  ];
  const SLIDERS = [
    ["--src-size", "Source size", 1.0, 3.2, 0.05, "rem", 1.75],
    ["--snd-size", "Sound size", 0.6, 1.4, 0.02, "rem", 0.78],
    ["--gls-size", "Gloss size", 0.7, 1.5, 0.02, "rem", 0.92],
    ["--sense-size", "Translation size", 0.8, 1.5, 0.02, "rem", 1.02],
    ["--word-gap", "Space between words", 0.3, 3, 0.05, "rem", 1.1],
    ["--set-gap", "Space between line sets", 0.4, 5, 0.1, "rem", 2.4],
  ];
  const plural = (w) => (/[^aeiou]y$/.test(w) ? w.slice(0, -1) + "ies" : w + "s");   // entry -> entries
  const STORE = "weft:" + D.work.work;
  document.body.classList.add("lang-" + D.work.language);
  const defaults = () => ({
    layers: Object.fromEntries(LAYERS.map(([k]) => [k, true])),
    scheme: D.schemes[0],
    tr: Object.fromEntries(D.translations.map((t) => [t.id, true])),
    sizes: Object.fromEntries(SLIDERS.map(([v, , , , , , d]) => [v, d])),
    veil: false, wrap: false, cant: false,
  });
  let S = defaults();
  try {
    const saved = JSON.parse(localStorage.getItem(STORE) || "null");
    if (saved) S = Object.assign(defaults(), saved, {
      layers: Object.assign(defaults().layers, saved.layers),
      tr: Object.assign(defaults().tr, saved.tr),
      sizes: Object.assign(defaults().sizes, saved.sizes),
    });
    if (!D.schemes.includes(S.scheme)) S.scheme = D.schemes[0];
  } catch (e) { /* storage blocked: defaults are fine */ }
  const save = () => { try { localStorage.setItem(STORE, JSON.stringify(S)); } catch (e) {} };

  /* ---------- indexes */
  const trById = Object.fromEntries(D.translations.map((t) => [t.id, t]));
  const notesByAttach = {};
  for (const n of D.notes) (notesByAttach[n.attach] = notesByAttach[n.attach] || []).push(n);
  const lineOrder = Object.fromEntries(D.lines.map((l, i) => [l.id, i]));
  const senseByEnd = {}; // line id -> [{tr, span}]
  for (const s of D.sense) for (const sp of s.spans) {
    (senseByEnd[sp.lines[1]] = senseByEnd[sp.lines[1]] || []).push({ tr: s.tr, span: sp });
  }
  const trOrder = Object.fromEntries(D.translations.map((t, i) => [t.id, i]));
  const shortRef = (id) => id.split(".").slice(1).join(".");
  const STANZAS = ["stanza-line", "inscription", "section"].includes(D.work.unit);
  // stanza works label lines "76.3"; book works and inscriptions label them "3"
  const lineNo = (id) => D.work.unit === "stanza-line" ? id.split(".").slice(-2).join(".") : id.split(".").pop();
  const tokNo = (id) => id.split(".").pop();
  // what a numbered unit is called: poems have lines, scripture has verses, sagas have sentences
  const UNIT = { verse: "verse", sentence: "sentence" }[D.work.unit] || "line";
  const Unit = UNIT[0].toUpperCase() + UNIT.slice(1);

  const ranges = (xs) => {
    const out = [];
    for (const x of xs) {
      const last = out[out.length - 1];
      if (last && typeof x === "number" && x === last[1] + 1) last[1] = x; else out.push([x, x]);
    }
    return out.map(([a, b]) => (a === b ? `${a}` : `${a}–${b}`)).join(", ");
  };
  // GitHub issue forms (.github/ISSUE_TEMPLATE), prefilled with the work and the scheme in use
  const issueUrl = (kind) => {
    const repo = D.work.repo_url || "https://github.com/GiantRavens/weft";
    const template = { Correction: "correction.yml", Pronunciation: "pronunciation.yml", Recording: "recording.yml" }[kind] || "correction.yml";
    const q = new URLSearchParams({ template, title: `${kind}: ${D.work.title}`, work: D.work.work, scheme: S.scheme });
    return `${repo}/issues/new?${q}`;
  };
  const issueLink = (kind, text) => h("a", { href: issueUrl(kind), "data-issue": kind, text });
  const refreshIssueLinks = () => document.querySelectorAll("a[data-issue]").forEach((a) => { a.href = issueUrl(a.dataset.issue); });

  /* ---------- masthead and colophon */
  document.title = `${D.work.title} · Weft`;
  $("#work-title").textContent = D.work.title;
  const first = D.lines[0], last = D.lines[D.lines.length - 1];
  $("#work-byline").textContent = D.work.unit === "inscription"
    ? `${D.work.author} · ${new Set(D.lines.map((l) => l.stanza)).size} inscriptions`
    : D.work.unit === "section"
    ? (D.work.section_noun === "chapter"
        ? (() => { // numbered chapters only; a named section such as a heading ("praef") shows on the page
                   const cs = [...new Set(D.lines.map((l) => l.stanza))].filter((c) => /^\d+$/.test(c)).map(Number);
                   return `${D.work.author} · chapter${cs.length === 1 ? "" : "s"} ${ranges(cs)}`; })()
        : (() => { // count numbered sections only: prose links (p0, p22) and headings are not stanzas
                   const all = [...new Set(D.lines.map((l) => l.stanza))], num = all.filter((c) => /^\d+$/.test(c));
                   const n = num.length || all.length, noun = D.work.section_noun || "section";
                   return `${D.work.author} · ${n} ${n === 1 ? noun : plural(noun)}`; })())
    : STANZAS
    ? `${D.work.author} · stanzas ${ranges([...new Set(D.lines.map((l) => l.stanza))])}`
    : `${D.work.author} · ${shortRef(first.id)}–${shortRef(first.id).split(".")[0] === shortRef(last.id).split(".")[0] ? lineNo(last.id) : shortRef(last.id)}`;
  const unreviewed = (c) => c && Object.values(c).some((x) => x.status !== "reviewed");
  const anyDraft = D.lines.some((l) => unreviewed(l.curated) || l.tokens.some((t) => t.curated && Object.values(t.curated).some((c) => c.status !== "reviewed")));
  // the notes about the page are divs, not paragraphs: Safari's Reader counts paragraph text, and these
  // would make a work page look like an article whose text Reader then drops (the interlinear lines)
  $("#colophon").append(
    h("div", { text: `Text: ${D.edition.name} (${D.edition.license}). Lemma and morphology: ${D.treebank.name} (${D.treebank.license}).` }),
    h("div", { text: "Translations: " + D.translations.map((t) => `${t.translator}, ${t.year} (${t.license})`).join("; ") + "."
      + ((D.references || []).length ? " Cited, in copyright: " + D.references.map((r) => `${r.translator}, ${r.year}`).join("; ") + "." : "") }),
    anyDraft ? h("div", { text: "Glosses, scansion and editorial notes are a phase 0 draft awaiting scholarly review." }) : null,
    D.work.private_work ? h("div", { text: "A private work: it exists only in your own build, and has no public issue links." }) :
    h("div", {}, "Corrections and recordings are welcome: ",
      issueLink("Correction", "a gloss, reading or note"), ", ",
      issueLink("Pronunciation", "the pronunciation"), ", ",
      issueLink("Recording", "a recording"), ". You do not need git. ",
      h("a", { href: "about.html", text: "About Weft" }), "."),
    h("div", { text: `Built with Weft ${D.build.weft}${D.build.private ? " · private build, includes your own or licensed material; do not publish" : ""}.` }),
  );

  /* ---------- the collection: previous and next work in date order, and the library */
  (function worknav() {
    const nav = $("#worknav");
    if (!nav || !D.nav) return;
    const card = (w, dir, cls) => w
      ? h("a", { class: cls, href: w.href }, h("span", { class: "dir", text: dir }), h("span", { class: "t", text: w.title }))
      : h("span", { class: cls + " empty" });
    const mark = document.querySelector(".home svg");
    const lib = h("div", { class: "lib" },
      h("a", { class: "home-card", href: "index.html" }, mark ? mark.cloneNode(true) : null, h("span", { class: "dir", text: "The library" })),
      h("a", { class: "srch", href: "search.html" }, "Search the library"));
    nav.append(card(D.nav.prev, "← Older", "prev"), lib, card(D.nav.next, "Newer →", "next"));
  })();

  /* ---------- MathML from the data tree ({t, a, c}); only known elements and attributes are built */
  const MML = "http://www.w3.org/1998/Math/MathML";
  const MML_TAGS = new Set(["math", "mrow", "mi", "mn", "mo", "mfrac", "msup", "msub", "msubsup", "msqrt", "mroot", "mtext", "mspace", "mtable", "mtr", "mtd", "mover", "munder", "munderover", "mstyle", "mpadded", "mphantom", "mfenced"]);
  const MML_ATTRS = new Set(["display", "mathvariant", "stretchy", "fence", "separator", "lspace", "rspace", "accent", "accentunder", "columnalign", "rowalign", "columnspacing", "rowspacing", "linethickness", "form", "largeop", "movablelimits", "displaystyle", "scriptlevel", "width", "height", "depth", "open", "close"]);
  function mathEl(node) {
    if (typeof node === "string") return document.createTextNode(node);
    const el = document.createElementNS(MML, MML_TAGS.has(node.t) ? node.t : "mrow");
    for (const [k, v] of Object.entries(node.a || {})) if (MML_ATTRS.has(k)) el.setAttribute(k, String(v));
    for (const c of node.c || []) el.append(mathEl(c));
    return el;
  }

  /* ---------- the text */
  const text = $("#text");
  function renderText() {
    text.replaceChildren();
    let prevStanza = null;
    for (const line of D.lines) {
      const lnotes = notesByAttach[line.id] || [];
      const gutter = h("div", { class: "lnum" }, lineNo(line.id),
        lnotes.length ? h("button", { class: "lnote", type: "button", title: `Notes on this ${UNIT}`, "aria-label": `Notes on ${UNIT} ${lineNo(line.id)}`, onclick: () => showLine(line) }, "¶") : null);
      const strip = h("div", { class: "strip" + (line.equation ? " eq" : ""), role: "group", "aria-label": `${Unit} ${lineNo(line.id)}` });
      if (line.equation) {
        // a displayed equation: MathML built from the data (never markup), then its sound and gloss rows
        const eq = line.equation, esnd = (eq.sound && eq.sound[S.scheme]) || {};
        strip.append(mathEl(eq.mathml), h("span", { class: "snd", text: esnd.respell || "" }), h("span", { class: "gls", text: eq.gloss || "" }));
      }
      for (const t of line.tokens) {
        const snd = (t.sound && t.sound[S.scheme]) || {};
        const w = h("button", {
          type: "button", class: "w" + ((notesByAttach[t.id] || []).length ? " has-note" : "") + (t.stave ? " stave" : "") + (t.caesura ? " caesura" : ""),
          "data-id": t.id, onclick: () => showWord(t, line),
          "aria-label": `${t.surface}${t.gloss ? ", " + t.gloss : ""}`,
        },
          t.script ? h("span", { class: "scr", "aria-hidden": "true", text: t.script }) : null,
          h("span", { class: "src", lang: LANG }, t.lead ? h("span", { class: "p", text: t.lead }) : null, h("span", { class: "form", text: shown(t) }), t.punct ? h("span", { class: "p", text: t.punct }) : null),
          D.work.show_translit && t.norm ? h("span", { class: "tl", text: t.norm }) : null,
          h("span", { class: "snd", text: snd.respell || "" }),
          h("span", { class: "gls", text: t.gloss || "·" }),
        );
        strip.append(w);
      }
      const metre = line.metre ? h("p", { class: "metre" + (/[a-z]/i.test(line.metre) ? " metre-text" : ""), "aria-label": "Metrical pattern" },
        ...line.metre.split("|").map((f) => h("span", { class: "ft", text: f }))) : null;
      const sense = h("div", { class: "sense" });
      const spans = (senseByEnd[line.id] || []).filter((x) => S.tr[x.tr]).sort((a, b) => trOrder[a.tr] - trOrder[b.tr]);
      for (const { tr, span } of spans) {
        const t = trById[tr];
        const range = span.lines[0] === span.lines[1] ? `${UNIT} ${lineNo(span.lines[0])}` : `${UNIT}s ${lineNo(span.lines[0])}–${lineNo(span.lines[1])}`;
        const who = t.kind === "editorial" ? `${t.translator} · ${range}` : `${t.translator}, ${t.year} · ${range}`;
        sense.append(h("blockquote", { class: "tr" + (t.kind === "editorial" ? " editorial" : "") }, span.text, h("cite", { text: who })));
      }
      const newStanza = STANZAS && line.stanza !== prevStanza;
      if (newStanza) text.append(h("h2", { class: "stanza-head" + (line.hexagram ? " hex-head" : ""), id: `sec-${line.stanza}` },
        line.hexagram ? hexFigure(line.hexagram) : null, h("span", { text: line.stanza_title || `Stanza ${line.stanza}` })));
      if (newStanza && line.figure && line.figure.src) {
        const f = line.figure;
        text.append(h("figure", { class: "sec-fig" },
          h("img", { src: safeUrl(f.src, true), alt: f.alt || f.caption || "" }),
          h("figcaption", {}, f.caption || "",
            (f.credit || f.license || f.source) ? h("span", { class: "cred" }, [f.credit, f.license].filter(Boolean).join(" · "),
              safeUrl(f.source) ? " · " : "", safeUrl(f.source) ? h("a", { href: safeUrl(f.source), text: "source" }) : null) : null)));
      }
      prevStanza = line.stanza;
      text.append(h("section", { class: "lineset" + (newStanza ? " stanza-first" : ""), id: line.id },
        gutter, h("div", { class: "body" }, strip,
          line.reading ? h("p", { class: "reading" }, h("span", { class: "rl", text: "Read aloud" }), h("span", { lang: LANG, text: line.reading })) : null,
          metre, spans.length ? sense : null)));
    }
  }

  /* veil: tap a hidden gloss or translation to reveal it */
  text.addEventListener("click", (e) => {
    if (!S.veil) return;
    const el = e.target.closest(".gls, .tr");
    if (el && !el.classList.contains("shown")) { el.classList.add("shown"); e.stopPropagation(); e.preventDefault(); }
  }, true);

  /* ---------- word and line detail */
  const wordPanel = $("#word"), wordBody = $("#word-body");
  function openPanel(p) { p.hidden = false; }
  function closePanel(p) {
    p.hidden = true;
    if (p === wordPanel) document.querySelectorAll(".w.active").forEach((x) => x.classList.remove("active"));
    if (p.id === "loom") $("#open-loom").setAttribute("aria-expanded", "false");
  }
  function noteEl(n) {
    const badges = [h("span", { class: "badge", text: n.kind === "quoted" ? "quoted" : "editorial" })];
    if (n.status && n.status !== "reviewed") badges.push(h("span", { class: "badge draft", text: n.status }));
    return h("div", { class: "note" }, badges, h("p", { text: n.text }),
      n.source ? h("div", { class: "src-line", text: n.source }) : null,
      n.leans_on ? h("div", { class: "src-line", text: "Leans on " + n.leans_on }) : null);
  }
  function showWord(t, line) {
    document.querySelectorAll(".w.active").forEach((x) => x.classList.remove("active"));
    const btn = document.querySelector(`.w[data-id="${CSS.escape(t.id)}"]`);
    if (btn) btn.classList.add("active");
    $("#word-title").textContent = (STANZAS && line.stanza_title ? line.stanza_title + ", " + UNIT : Unit) + ` ${lineNo(line.id)}, word ${tokNo(t.id)}`;
    const dl = h("dl", {},
      h("dt", { text: "lemma" }), h("dd", { class: "lemma", lang: LANG, text: t.lemma || "—" }),
      h("dt", { text: "form" }), h("dd", { text: t.morph_text || "indeclinable" }),
      ...(t.script ? [h("dt", { text: D.work.script_word || "runes" }), h("dd", { class: "scr-big", text: t.script })] : []),
      ...(t.norm ? [h("dt", { text: { ja: "reading" }[D.work.language] || (D.work.show_translit ? (D.work.translit_label || "Transliteration").toLowerCase() : "normalized") }), h("dd", { lang: D.work.show_translit ? null : LANG, text: t.norm })] : []),
      ...(t.metre_form ? [h("dt", { text: "metrical reading" }), h("dd", { text: `${t.metre_form}: the metre sounds a syllable the written form lost` })] : []),
      ...(t.enclitic ? [h("dt", { text: "enclitic" }), h("dd", { lang: LANG, text: `${t.enclitic.form} (${t.enclitic.lemma}${t.enclitic.gloss ? ", '" + t.enclitic.gloss + "'" : t.enclitic.lemma === "que" ? ", 'and'" : ""}), attached to the word` })] : []),
      ...(t.prefixes || []).flatMap((pf) => [h("dt", { text: "prefix" }),
        h("dd", {}, h("span", { lang: LANG, text: pf.form + " " }), `'${pf.gloss}'${pf.morph_text ? ", " + pf.morph_text : ""}`)]),
      ...(t.lexgloss ? [h("dt", { text: "dictionary" }), h("dd", { text: `${t.lexgloss}${t.strong ? " (Strong's " + t.strong + ")" : ""}` })] : []),
      h("dt", { text: "gloss" }), h("dd", { text: t.gloss || "—" }),
      ...D.schemes.flatMap((s) => {
        const snd = (t.sound || {})[s] || {};
        return [h("dt", { text: s }), h("dd", {}, h("div", { text: snd.respell || "" }), h("div", { class: "ipa", text: snd.ipa ? `/${snd.ipa}/` : "" }))];
      }),
    );
    const prov = [`Word id: ${t.id} (quote it in a correction)`];
    prov.push(t.tb ? `Lemma and form: ${D.treebank.id} sentence/word ${t.tb}` : "Lemma and form: hand annotation (no treebank)");
    if (t.stave) prov.push("Stave: an alliterating sound that binds the verse");
    if (t.printed) prov.push(`Printed in the edition as ${t.printed}`);
    if (t.prov && t.prov.sound) prov.push(`Sound: ${t.prov.sound}`);
    if (t.curated) for (const [f, c] of Object.entries(t.curated)) prov.push(`${f}: ${c.by}, ${c.date} (${c.status})`);
    wordBody.replaceChildren(
      h("div", { class: "big", lang: LANG, text: t.surface }),
      dl,
      ...(notesByAttach[t.id] || []).map(noteEl),
      h("div", { class: "prov" }, ...prov.map((p) => h("div", { text: p }))),
    );
    openPanel(wordPanel);
  }
  function showLine(line) {
    document.querySelectorAll(".w.active").forEach((x) => x.classList.remove("active"));
    $("#word-title").textContent = `${Unit} ${lineNo(line.id)}`;
    wordBody.replaceChildren(
      h("div", { class: "big", lang: LANG, style: "font-size:1.5rem", text: line.text }),
      h("div", { class: "src-line", text: line.cite }),
      ...(notesByAttach[line.id] || []).map(noteEl),
      h("div", { class: "prov" }, h("div", { text: `Line id: ${line.id} (quote it in a correction or name a recording by it)` })),
    );
    openPanel(wordPanel);
  }

  /* ---------- the loom (settings) */
  function applySettings() {
    const b = document.body;
    for (const [k] of LAYERS) b.classList.toggle("hide-" + k, !S.layers[k]);
    b.classList.toggle("veil", !!S.veil);
    b.classList.toggle("wrap", !!S.wrap);
    for (const [v, , , , , unit] of SLIDERS) document.documentElement.style.setProperty(v, S.sizes[v] + unit);
    if (!S.veil) document.querySelectorAll(".shown").forEach((x) => x.classList.remove("shown"));
  }
  function buildLoom() {
    const lt = $("#layer-toggles"); lt.replaceChildren();
    for (const [k, label] of LAYERS) {
      lt.append(h("label", { class: "check" },
        h("input", { type: "checkbox", checked: S.layers[k], onchange: (e) => { S.layers[k] = e.target.checked; applySettings(); save(); } }), label));
    }
    $("#veil").checked = S.veil;
    $("#cant").checked = S.cant;
    $("#cant-row").hidden = !D.lines.some((l) => l.tokens.some((t) => t.surface_plain && t.surface_plain !== t.surface));
    $("#wrap").checked = S.wrap;
    const sc = $("#scheme-choice"); sc.replaceChildren();
    for (const s of D.schemes) {
      sc.append(h("label", { class: "radio" },
        h("input", { type: "radio", name: "scheme", value: s, checked: S.scheme === s, onchange: () => { S.scheme = s; renderText(); applySettings(); save(); fillKey(); refreshIssueLinks(); } }),
        schemeLabel(s)));
    }
    const tt = $("#tr-toggles"); tt.replaceChildren();
    for (const t of D.translations) {
      tt.append(h("label", { class: "check" },
        h("input", { type: "checkbox", checked: S.tr[t.id], onchange: (e) => { S.tr[t.id] = e.target.checked; renderText(); applySettings(); save(); } }),
        `${t.translator}, ${t.year}`));
    }
    const sl = $("#sliders"); sl.replaceChildren();
    for (const [v, label, min, max, step, unit] of SLIDERS) {
      const out = h("output", { text: (+S.sizes[v]).toFixed(2) });
      sl.append(h("label", { class: "slider" }, label, out,
        h("input", { type: "range", min, max, step, value: S.sizes[v], oninput: (e) => {
          S.sizes[v] = +e.target.value; out.textContent = S.sizes[v].toFixed(2); applySettings(); save(); } })));
    }
  }
  const schemeLabel = (s) => (D.scheme_labels && D.scheme_labels[s]) || s;
  const LANG = D.work.lang_html || D.work.language;
  const RTL = D.work.dir === "rtl";
  document.body.classList.toggle("rtl", RTL);
  if (RTL) {
    // tell the reader which way to read before the first line
    const note = $("#dir-note");
    note.append(h("span", { class: "arrow", "aria-hidden": "true", text: "←" }),
      h("strong", { text: "Read right to left. " }),
      `${D.work.lang_name || "This text"} runs from right to left: each ${D.work.unit === "verse" ? "verse" : "line"} begins at the right edge, and its first word is the rightmost. The pronunciation and gloss under each word read left to right.`);
    note.hidden = false;
  }
  // an invitation to specialists: corrections to a reconstructed pronunciation, or recordings
  if (!D.work.private_work && (D.work.sound_confidence === "low" || D.work.sound_confidence === "medium")) {
    const note = $("#sound-note");
    const low = D.work.sound_confidence === "low";
    note.append(h("strong", { text: low ? "The pronunciation here is a reconstruction. " : "Parts of the pronunciation here are reconstructed. " }),
      low ? `How ${D.work.lang_name || "this language"} sounded is inferred indirectly, and specialists disagree. If you work on its phonology, we would welcome corrections to the sound guide, and recordings read from this page. `
          : "Specialists are welcome to suggest corrections or contribute recordings. ",
      issueLink("Pronunciation", "Suggest a correction"), " or ",
      issueLink("Recording", "offer a recording"), ". ",
      h("a", { href: "languages.html", text: "What this reconstruction rests on" }), ".");
    note.hidden = false;
  }
  // translations still in copyright: cited here, never reproduced
  if ((D.references || []).length) {
    const note = $("#ref-note");
    note.append(h("strong", { text: "In copyright, not reproduced: " }),
      D.references.map((r) => `${r.translator}, ${r.title ? r.title + " " : ""}(${r.publisher ? r.publisher + ", " : ""}${r.year})${r.note ? ". " + r.note : ""}`).join("; ") + ". ",
      "The gloss row gives the meaning word for word.");
    note.hidden = false;
  }
  // Hebrew: show the text without cantillation unless the reader asks for it
  const shown = (t) => (t.surface_plain && !S.cant ? t.surface_plain : t.surface);
  $("#veil").addEventListener("change", (e) => { S.veil = e.target.checked; applySettings(); save(); });
  $("#cant").addEventListener("change", (e) => { S.cant = e.target.checked; save(); renderText(); applySettings(); });
  $("#wrap").addEventListener("change", (e) => { S.wrap = e.target.checked; applySettings(); save(); });
  $("#reset").addEventListener("click", () => { S = defaults(); save(); buildLoom(); renderText(); applySettings(); fillKey(); });
  $("#open-loom").addEventListener("click", () => {
    const p = $("#loom");
    if (p.hidden) { closePanel(wordPanel); openPanel(p); $("#open-loom").setAttribute("aria-expanded", "true"); } else closePanel(p);
  });
  document.querySelectorAll("[data-close]").forEach((b) => b.addEventListener("click", () => closePanel($("#" + b.dataset.close))));

  /* ---------- the Yijing: draw hexagrams, and cast one by the three-coin method */
  // a hexagram is six digits, bottom line first, 1 = unbroken (yang), 0 = broken (yin)
  function hexFigure(bits, changing = []) {
    const fig = h("span", { class: "hex", role: "img", "aria-label": `hexagram ${bits}` });
    for (let i = 5; i >= 0; i--)        // drawn top line first
      fig.append(h("span", { class: "hl " + (bits[i] === "1" ? "yang" : "yin") + (changing.includes(i) ? " chg" : "") }));
    return fig;
  }
  (function cast() {
    const box = $("#cast");
    const hexes = D.lines.filter((l) => l.hexagram);
    if (!box || !hexes.length) return;
    const bySig = Object.fromEntries(hexes.map((l) => [l.hexagram, l]));
    const VAL = { 6: "6, old yin: broken, changing", 7: "7, young yang: unbroken", 8: "8, young yin: broken", 9: "9, old yang: unbroken, changing" };
    const POS = ["first (bottom)", "second", "third", "fourth", "fifth", "top"];
    let throws = null;
    const coin = () => { const a = new Uint8Array(3); crypto.getRandomValues(a); return [...a].reduce((s, x) => s + (x & 1 ? 3 : 2), 0); };
    const link = (l) => h("a", { href: `#sec-${l.stanza}`, text: l.stanza_title || `Hexagram ${l.stanza}` });
    const result = h("div", { class: "cast-result", "aria-live": "polite" });
    const selects = POS.map((p, i) => h("select", { "aria-label": `${p} line`, onchange: () => { throws[i] = +selects[i].value; show(); } },
      ...[6, 7, 8, 9].map((v) => h("option", { value: v, text: VAL[v] }))));
    function show() {
      selects.forEach((s, i) => { s.value = throws[i]; });
      const bits = throws.map((v) => (v % 2 ? "1" : "0")).join("");
      const changing = throws.map((v, i) => (v === 6 || v === 9 ? i : -1)).filter((i) => i >= 0);
      const after = throws.map((v) => (v === 9 ? "0" : v === 6 ? "1" : v % 2 ? "1" : "0")).join("");
      const a = bySig[bits], b = changing.length ? bySig[after] : null;
      document.querySelectorAll(".lineset.cast-hit").forEach((x) => x.classList.remove("cast-hit"));
      if (a) {
        // the section's line 1 is the name and judgment; lines 2 to 7 are the line statements, bottom first
        const ids = D.lines.filter((l) => l.stanza === a.stanza).map((l) => l.id);
        changing.forEach((i) => { const el = document.getElementById(ids[i + 1]); if (el) el.classList.add("cast-hit"); });
      }
      result.replaceChildren(
        h("div", { class: "cast-pair" },
          h("div", {}, hexFigure(bits, changing), h("p", {}, a ? link(a) : `hexagram ${bits} is not in this edition`)),
          b ? h("div", { class: "arrow", "aria-hidden": "true", text: "→" }) : null,
          b ? h("div", {}, hexFigure(after), h("p", {}, link(b))) : null),
        h("div", { class: "cast-how", text: changing.length
          ? `Changing lines: ${changing.map((i) => POS[i]).join(", ")}. They are marked in the text. Read the judgment and the changing lines of the first hexagram, then the judgment of the second.`
          : "No changing lines: read the judgment of this hexagram." }));
    }
    box.append(
      h("h2", { text: "Cast a hexagram" }),
      h("div", { class: "cast-intro", text: "The three-coin method, as traditionally practised: three coins are thrown six times, building the hexagram from the bottom line up. Heads count 3 and tails 2, so each throw totals 6, 7, 8 or 9. Odd totals give an unbroken line, even totals a broken one; 6 and 9 are 'old' lines that change into their opposite, giving a second hexagram. This page describes the practice; it makes no claim about what the result means." }),
      h("div", { class: "cast-controls" },
        h("button", { type: "button", class: "tool tool-primary", onclick: () => { throws = Array.from({ length: 6 }, coin); show(); }, text: "Throw the coins" }),
        h("details", {}, h("summary", { text: "Enter your own throws" }),
          h("div", { class: "cast-manual" }, ...POS.map((p, i) => h("label", {}, `${p[0].toUpperCase() + p.slice(1)} line `, selects[i])).reverse(),
            h("button", { type: "button", class: "tool", onclick: () => { throws = selects.map((s) => +s.value); show(); }, text: "Show" })))),
      result);
    throws = [7, 7, 7, 7, 7, 7];
    selects.forEach((s) => { s.value = 7; });
    box.hidden = false;
  })();

  /* ---------- lightbox: a figure opens full size; click, Escape or the close button dismisses it */
  (function lightbox() {
    const dlg = h("dialog", { class: "lightbox", "aria-label": "Image, full size" },
      h("button", { type: "button", class: "close", "aria-label": "Close image", onclick: () => dlg.close() }, "×"),
      h("img", { alt: "" }), h("p", { class: "cap" }));
    document.body.append(dlg);
    dlg.addEventListener("click", (e) => { if (e.target === dlg || e.target.tagName === "IMG") dlg.close(); });
    document.addEventListener("click", (e) => {
      const img = e.target.closest("figure.frontis img, figure.sec-fig img");
      if (!img || !dlg.showModal) return;
      const cap = img.closest("figure").querySelector("figcaption");
      dlg.querySelector("img").src = img.src;
      dlg.querySelector("img").alt = img.alt || "";
      dlg.querySelector(".cap").textContent = cap ? cap.textContent : "";
      dlg.showModal();
    });
    document.querySelectorAll("figure.frontis img, figure.sec-fig img").forEach((i) => { i.style.cursor = "zoom-in"; i.title = "Click to enlarge"; });
  })();

  /* ---------- sound key */
  const keyDlg = $("#key");
  function fillKey() {
    $("#key-title").textContent = "Sound key · " + S.scheme;
    const rows = (D.keys[S.scheme] || []).map(([sym, desc]) => h("tr", {}, h("td", { text: sym }), h("td", { text: desc })));
    $("#key-body").replaceChildren(
      h("div", { class: "scheme-note", text: schemeLabel(S.scheme) + ". Syllables are hyphenated; long vowels are doubled or written with their own symbol." }),
      h("table", {}, h("tbody", {}, rows)));
  }
  $("#open-key").addEventListener("click", () => { fillKey(); if (keyDlg.showModal) keyDlg.showModal(); else keyDlg.setAttribute("open", ""); });
  $("#close-key").addEventListener("click", () => keyDlg.close ? keyDlg.close() : keyDlg.removeAttribute("open"));
  keyDlg.addEventListener("click", (e) => { if (e.target === keyDlg) keyDlg.close(); });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { closePanel(wordPanel); closePanel($("#loom")); }
  });

  buildLoom();
  renderText();
  applySettings();
  fillKey();

  /* a link to a line or a word (work.html#od.1.1, #od.1.1.5, from search or a citation): the page is
     drawn by script, so the browser's own jump to the anchor finds nothing; go there once it is drawn */
  function goToHash() {
    let id = "";
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }
    if (!id) return;
    const el = document.getElementById(id) || document.querySelector(`.w[data-id="${CSS.escape(id)}"]`);
    if (!el) return;
    document.querySelectorAll(".hit").forEach((x) => x.classList.remove("hit"));
    const line = el.closest(".lineset") || el;
    line.classList.add("hit");
    if (el.classList.contains("w")) el.classList.add("hit");
    const head = document.querySelector(".masthead");
    if (head) document.documentElement.style.setProperty("--head-h", head.offsetHeight + "px");
    line.scrollIntoView({ block: "start" });     // scroll-margin-top (weft.css) keeps it clear of the sticky header
  }
  window.addEventListener("hashchange", goToHash);
  goToHash();
})();
