/* Weft search: the matching core and the search page. The core is a pure function over the index
   (window.WEFT_INDEX, written by `weft index`) and is shared with the tests, which run it under Node.

   Matching. Text and query are folded alike: decomposed, combining marks dropped, lowercased, and a few
   letters spelled out (ß ss, æ ae, œ oe, ø o, ð d, þ th, final ς σ), so θεος finds θεός and ulfr finds
   úlfr. Words are runs of letters and digits; a query word matches a whole word, or the word with a
   plural -s or -es (god finds gods, of-God). Chinese and Japanese have no spaces between words, so a
   query in those scripts matches anywhere in the text. Every query word must match.

   Results, in order: works (what a work is: title, subjects, author, date, kind, language, summary);
   the word across languages (source words whose gloss holds the query, grouped by language and lemma,
   and source words or lemmas equal to it); then lines (translations, notes, the text itself), by work. */
(function (root) {
  "use strict";
  const LETTERS = { "ß": "ss", "æ": "ae", "œ": "oe", "ø": "o", "ð": "d", "þ": "th", "ς": "σ", "ı": "i", "ł": "l" };
  const fold = (s) => String(s || "").normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().replace(/[ßæœøðþςıł]/g, (c) => LETTERS[c]);
  const WORD = /[\p{L}\p{N}]+/gu;
  const words = (s) => fold(s).match(WORD) || [];
  const CJK = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}]/u;

  function terms(query) {
    return words(query).filter((t, i, a) => a.indexOf(t) === i);
  }
  const wordMatch = (w, t) => w === t || w === t + "s" || w === t + "es" || (t.length > 3 && t.endsWith("s") && w === t.slice(0, -1));
  /* the terms a text matches, as a set; a text matches the query when it matches every term */
  function hits(text, ts) {
    const f = fold(text), ws = f.match(WORD) || [];
    const got = new Set();
    for (const t of ts) {
      if (CJK.test(t) ? f.includes(t) : ws.some((w) => wordMatch(w, t))) got.add(t);
    }
    return got;
  }
  const all = (text, ts) => hits(text, ts).size === ts.length;

  /* works: weighted by the field that matched; every term must match somewhere in the work's record */
  const FIELDS = [["t", 6], ["st", 6], ["sub", 5], ["desc", 3], ["a", 3], ["k", 2], ["f", 2], ["l", 2], ["wl", 1], ["sum", 1]];
  function workFields(w) {
    return { t: w.t, st: w.st, sub: (w.ab.subjects || []).join(" · "), desc: w.ab.description || "", a: w.a, k: w.k, f: w.f, l: w.l,
             wl: w.wl + " " + w.d, sum: w.ab.summary || "" };
  }
  function matchWorks(idx, ts) {
    const out = [];
    idx.works.forEach((w, order) => {
      const f = workFields(w), seen = new Set(), where = [];
      let score = 0;
      for (const [k, wt] of FIELDS) {
        const h = hits(f[k], ts);
        if (h.size) { score += wt * h.size; where.push(k); h.forEach((t) => seen.add(t)); }
      }
      if (seen.size === ts.length) out.push({ work: w, score, where, order });
    });
    return out.sort((a, b) => b.score - a.score || a.order - b.order);
  }

  /* the word across languages: tokens whose gloss matches every term, grouped by language family and lemma;
     and tokens whose folded surface or lemma equals a one-word query */
  function matchWord(idx, ts) {
    const groups = new Map();
    const add = (kind, w, line, i) => {
      const lemma = line[3][i] || line[2][i];
      const key = kind + "\u0000" + w.f + "\u0000" + lemma;
      let g = groups.get(key);
      if (!g) groups.set(key, g = { kind, lang: w.f, lemma, glosses: new Map(), n: 0, works: new Set(), first: null });
      g.n++; g.works.add(w.w);
      g.glosses.set(line[4][i], (g.glosses.get(line[4][i]) || 0) + 1);
      if (!g.first) g.first = { work: w, id: `${line[0]}.${i + 1}`, surface: line[2][i] };
    };
    const one = ts.length === 1 ? ts[0] : null;
    for (const w of idx.works) {
      for (const line of w.L) {
        for (let i = 0; i < line[2].length; i++) {
          if (line[4][i] && all(line[4][i].replace(/-/g, " "), ts)) add("gloss", w, line, i);
          else if (one && (fold(line[2][i]).match(WORD) || []).join("") === one) add("form", w, line, i);
          else if (one && line[3][i] && (fold(line[3][i]).match(WORD) || []).join("") === one) add("form", w, line, i);
        }
      }
    }
    const list = [...groups.values()].map((g) => ({ ...g, works: [...g.works], glosses: [...g.glosses.entries()].sort((a, b) => b[1] - a[1]) }));
    // words translated by the query first; words that only look like it (folded góðr and gōd for god) after
    list.sort((a, b) => (a.kind === b.kind ? 0 : a.kind === "gloss" ? -1 : 1) || b.n - a.n || a.lang.localeCompare(b.lang));
    return list;
  }

  /* lines: translation spans, notes and the text, by work; at most `per` samples a work, every hit counted */
  function matchLines(idx, ts, per = 3) {
    const out = [];
    for (const w of idx.works) {
      const found = [];
      for (const s of w.S) if (all(s[4], ts)) found.push({ kind: "translation", id: s[0], to: s[1], who: `${s[2]}${s[3] ? ", " + s[3] : ""}`, text: s[4] });
      for (const n of w.N) if (all(n[1], ts)) found.push({ kind: "note", id: n[0], text: n[1] });
      for (const l of w.L) if (l[1] && all(l[1], ts)) found.push({ kind: "text", id: l[0], text: l[1] });
      if (found.length) out.push({ work: w, n: found.length, kinds: [...new Set(found.map((f) => f.kind))], samples: found.slice(0, per) });
    }
    return out.sort((a, b) => b.n - a.n);
  }

  function search(idx, query) {
    const ts = terms(query);
    if (!ts.length) return { terms: ts, works: [], word: [], lines: [] };
    return { terms: ts, works: matchWorks(idx, ts), word: matchWord(idx, ts), lines: matchLines(idx, ts) };
  }

  const api = { fold, words, terms, hits, search };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.WeftSearch = api;

  /* ---------------------------------------------------------------- the page */
  if (typeof document === "undefined") return;
  const $ = (s) => document.querySelector(s);
  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === "text") el.textContent = v; else el.setAttribute(k, v);
    }
    for (const c of kids.flat()) if (c != null && c !== false) el.append(c);
    return el;
  }
  /* the text with matching words marked; built as nodes, never as markup */
  function marked(text, ts, max) {
    let s = String(text || "");
    if (max && s.length > max) {
      // a window of max characters that starts a little before the first match
      const f = fold(s), found = ts.map((t) => f.indexOf(t)).filter((i) => i >= 0);
      const at = found.length ? Math.max(0, Math.min(...found) - 60) : 0;
      s = (at > 0 ? "… " : "") + s.slice(at, at + max) + (s.length > at + max ? " …" : "");
    }
    const frag = document.createDocumentFragment();
    let last = 0;
    for (const m of s.matchAll(WORD)) {
      const w = fold(m[0]);
      if (ts.some((t) => (CJK.test(t) ? w.includes(t) : wordMatch(w, t)))) {
        frag.append(s.slice(last, m.index), h("mark", { text: m[0] }));
        last = m.index + m[0].length;
      }
    }
    frag.append(s.slice(last));
    return frag;
  }
  const href = (w, id) => `${w.w}.html` + (id ? `#${encodeURIComponent(id)}` : "");

  function render(idx, q) {
    const out = $("#results");
    out.replaceChildren();
    const r = search(idx, q);
    if (!r.terms.length) { $("#count").textContent = `${idx.works.length} works. Search for a word in any language or in English, a name, or a subject.`; return; }
    const nLines = r.lines.reduce((a, x) => a + x.n, 0);
    $("#count").textContent = `${r.works.length} ${r.works.length === 1 ? "work" : "works"} · ${r.word.length} source ${r.word.length === 1 ? "word" : "words"} · ${nLines} ${nLines === 1 ? "passage" : "passages"}`;
    if (r.works.length) {
      out.append(h("h2", { text: "Works" }), h("ul", { class: "works" }, r.works.slice(0, 30).map(({ work: w }) =>
        h("li", {}, h("a", { href: href(w), class: "wt" }, marked(w.t, r.terms)),
          h("span", { class: "meta" }, `${w.a} · ${w.d} · ${w.l}`),
          (w.ab.subjects || []).length ? h("span", { class: "subj" }, marked(w.ab.subjects.join(" · "), r.terms)) : null,
          w.ab.summary ? h("p", { class: "sum" }, marked(w.ab.summary, r.terms, 260)) : null))));
    }
    const wordList = (groups) => h("ul", { class: "word" }, groups.slice(0, 80).map((g) =>
      h("li", {}, h("span", { class: "lang", text: g.lang }),
        h("a", { href: href(g.first.work, g.first.id), class: "lemma", lang: "", dir: "auto", text: g.lemma }),
        h("span", { class: "gl" }, marked(g.glosses.slice(0, 3).map(([x]) => x).join(", "), r.terms)),
        h("span", { class: "n", text: `${g.n}× · ${g.works.length === 1 ? g.first.work.st : g.works.length + " works"}` }))));
    const glossed = r.word.filter((g) => g.kind === "gloss"), spelled = r.word.filter((g) => g.kind === "form");
    if (glossed.length) {
      const langs = new Set(glossed.map((g) => g.lang));
      out.append(h("h2", { text: `Translated “${q.trim()}” in the gloss` }, h("span", { class: "n", text: `${langs.size} ${langs.size === 1 ? "language" : "languages"}` })), wordList(glossed));
    }
    if (spelled.length) {
      out.append(h("h2", { text: `Spelled “${q.trim()}” in the source` }, h("span", { class: "n", text: "accents and marks ignored" })), wordList(spelled));
    }
    if (r.lines.length) {
      out.append(h("h2", { text: "In the texts" }), ...r.lines.slice(0, 40).map((x) =>
        h("section", { class: "hitwork" },
          h("h3", {}, h("a", { href: href(x.work), text: x.work.st }), h("span", { class: "n", text: `${x.n} · ${x.kinds.join(", ")}` })),
          h("ul", {}, x.samples.map((s) => h("li", {},
            h("a", { href: href(x.work, s.id), class: "at", text: s.kind === "translation" ? s.who : s.kind === "note" ? "note" : "text" }),
            h("span", { class: "snip", dir: "auto" }, marked(s.text, r.terms, 240))))))));
    }
    if (!r.works.length && !r.word.length && !r.lines.length) out.append(h("p", { class: "none", text: "Nothing in the library matches every word of the search." }));
  }

  function start() {
    const idx = root.WEFT_INDEX;
    const input = $("#q");
    if (!idx) { $("#count").textContent = "The search index (search-index.js) did not load. Build it with weft build all."; return; }
    const q0 = new URLSearchParams(location.search).get("q") || "";
    input.value = q0;
    render(idx, q0);
    let timer = null;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        render(idx, input.value);
        try { history.replaceState(null, "", input.value ? `?q=${encodeURIComponent(input.value)}` : location.pathname); } catch (e) { /* file:// in some browsers */ }
      }, 160);
    });
    $("#form").addEventListener("submit", (e) => e.preventDefault());
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})(typeof window !== "undefined" ? window : globalThis);
