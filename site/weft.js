/* Weft renderer. Reads window.WEFT (inlined by `weft build`) and draws the interlinear.
   No framework, no fetch: the page must open from file:// and print. */
(function () {
  "use strict";
  const D = window.WEFT;
  const $ = (s, el = document) => el.querySelector(s);
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
    ...(D.work.show_translit ? [["translit", D.work.translit_label || "Transliteration"]] : []), ["sound", "Sound"], ["gloss", "Gloss, word for word"],
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
  const STORE = "weft:" + D.work.work;
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
  /* ---------- masthead and colophon */
  document.title = `${D.work.title} · Weft`;
  $("#work-title").textContent = D.work.title;
  const first = D.lines[0], last = D.lines[D.lines.length - 1];
  $("#work-byline").textContent = D.work.unit === "inscription"
    ? `${D.work.author} · ${new Set(D.lines.map((l) => l.stanza)).size} inscriptions`
    : D.work.unit === "section"
    ? (D.work.section_noun === "chapter"
        ? `${D.work.author} · chapters ${[...new Set(D.lines.map((l) => l.stanza))].join(", ")}`
        : (() => { const n = new Set(D.lines.map((l) => l.stanza)).size, noun = D.work.section_noun || "section";
                   return `${D.work.author} · ${n} ${noun}${n === 1 ? "" : "s"}`; })())
    : STANZAS
    ? `${D.work.author} · stanzas ${ranges([...new Set(D.lines.map((l) => l.stanza))])}`
    : `${D.work.author} · ${shortRef(first.id)}–${lineNo(last.id)}`;
  const anyDraft = D.lines.some((l) => l.curated || l.tokens.some((t) => t.curated && Object.values(t.curated).some((c) => c.status !== "reviewed")));
  $("#colophon").append(
    h("p", { text: `Text: ${D.edition.name} (${D.edition.license}). Lemma and morphology: ${D.treebank.name} (${D.treebank.license}).` }),
    h("p", { text: "Translations: " + D.translations.map((t) => `${t.translator}, ${t.year} (${t.license})`).join("; ") + "." }),
    anyDraft ? h("p", { text: "Glosses, scansion and editorial notes are a phase 0 draft awaiting scholarly review." }) : null,
    h("p", { text: `Built with Weft ${D.build.weft}${D.build.private ? " · private build, includes licensed translations" : ""}.` }),
  );

  /* ---------- the collection: previous and next work in date order, and the library */
  (function worknav() {
    const nav = $("#worknav");
    if (!nav || !D.nav) return;
    const card = (w, dir, cls) => w
      ? h("a", { class: cls, href: w.href }, h("span", { class: "dir", text: dir }), h("span", { class: "t", text: w.title }))
      : h("span", { class: cls + " empty" });
    const mark = document.querySelector(".home svg");
    const lib = h("a", { class: "lib", href: "index.html" }, mark ? mark.cloneNode(true) : null, h("span", { class: "dir", text: "The library" }));
    nav.append(card(D.nav.prev, "← Older", "prev"), lib, card(D.nav.next, "Newer →", "next"));
  })();

  /* ---------- the text */
  const text = $("#text");
  function renderText() {
    text.replaceChildren();
    let prevStanza = null;
    for (const line of D.lines) {
      const lnotes = notesByAttach[line.id] || [];
      const gutter = h("div", { class: "lnum" }, lineNo(line.id),
        lnotes.length ? h("button", { class: "lnote", type: "button", title: `Notes on this ${UNIT}`, "aria-label": `Notes on ${UNIT} ${lineNo(line.id)}`, onclick: () => showLine(line) }, "¶") : null);
      const strip = h("div", { class: "strip", role: "group", "aria-label": `${Unit} ${lineNo(line.id)}` });
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
      if (newStanza) text.append(h("h2", { class: "stanza-head", text: line.stanza_title || `Stanza ${line.stanza}` }));
      prevStanza = line.stanza;
      text.append(h("section", { class: "lineset" + (newStanza ? " stanza-first" : ""), id: line.id },
        gutter, h("div", { class: "body" }, strip, metre, spans.length ? sense : null)));
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
      ...(t.enclitic ? [h("dt", { text: "enclitic" }), h("dd", { lang: LANG, text: `${t.enclitic.form} (${t.enclitic.lemma}, 'and'), attached to the end of the word` })] : []),
      ...(t.prefixes || []).flatMap((pf) => [h("dt", { text: "prefix" }),
        h("dd", {}, h("span", { lang: LANG, text: pf.form + " " }), `'${pf.gloss}'${pf.morph_text ? ", " + pf.morph_text : ""}`)]),
      ...(t.lexgloss ? [h("dt", { text: "dictionary" }), h("dd", { text: `${t.lexgloss}${t.strong ? " (Strong's " + t.strong + ")" : ""}` })] : []),
      h("dt", { text: "gloss" }), h("dd", { text: t.gloss || "—" }),
      ...D.schemes.flatMap((s) => {
        const snd = (t.sound || {})[s] || {};
        return [h("dt", { text: s }), h("dd", {}, h("div", { text: snd.respell || "" }), h("div", { class: "ipa", text: snd.ipa ? `/${snd.ipa}/` : "" }))];
      }),
    );
    const prov = [];
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
        h("input", { type: "radio", name: "scheme", value: s, checked: S.scheme === s, onchange: () => { S.scheme = s; renderText(); applySettings(); save(); fillKey(); } }),
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

  /* ---------- sound key */
  const keyDlg = $("#key");
  function fillKey() {
    $("#key-title").textContent = "Sound key · " + S.scheme;
    const rows = (D.keys[S.scheme] || []).map(([sym, desc]) => h("tr", {}, h("td", { text: sym }), h("td", { text: desc })));
    $("#key-body").replaceChildren(
      h("p", { class: "scheme-note", text: schemeLabel(S.scheme) + ". Syllables are hyphenated; long vowels are doubled or written with their own symbol." }),
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
})();
