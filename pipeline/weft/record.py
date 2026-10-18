"""The recording page: site/build/<work>.record.html, for a speaker reading a work aloud line by line.

Written for every work with a stewardship block (pipeline/weft/stewardship.py). It shows one line at a time in
the original script only, with no romanization, sound guide or gloss, so that the reading is the speaker's own
and not an echo of Weft's reconstruction. It records each line in the browser (MediaRecorder), lets the speaker
listen and record again, then offers the single words Weft is unsure of (no dictionary form found, or a sign in doubt), each said twice, with
a box for the speaker's own sense of the word, as an optional pass. At the end it saves
one zip: a file per line or token id, and speaker.json with the speaker's choices (docs/speakers.md). Nothing is
uploaded; the speaker sends the zip. Plain HTML and JS, no libraries, so it works from file:// as the site does.
"""
from __future__ import annotations

import html as H
import json
from pathlib import Path

# the script's face; the page loads it from Google Fonts like the work page, with system fallbacks
FONTS = {"chr": '"Noto Sans Cherokee", "Plantagenet Cherokee", "Gadugi", sans-serif'}


def doubtful(line: dict) -> list[dict]:
    """Tokens a speaker should say on their own: no lemma found, or a sign in doubt. (A gloss taken from the English
    is not enough on its own: the word itself is often known, and the list is meant to stay short.)"""
    out = []
    for t in line.get("tokens") or []:
        if t.get("lemma") == "?" or t.get("uncertain"):
            out.append(t)
    return out


def items(data: dict) -> list[dict]:
    lines = [{"id": ln["id"], "text": ln.get("text") or " ".join(t["surface"] for t in ln["tokens"]), "kind": "line"}
             for ln in data["lines"]]
    words, seen = [], set()
    for ln in data["lines"]:
        for t in doubtful(ln):
            if t["surface"] not in seen:
                seen.add(t["surface"])
                words.append({"id": t["id"], "text": t["surface"], "kind": "word"})
    return lines + words


def render(data: dict, art: dict) -> str:
    w = data["work"]
    lang = w.get("language", "")
    payload = {"work": w["work"], "title": w["title"], "lang": lang, "items": items(data),
               "contact": (w.get("stewardship") or {}).get("contact")}
    js = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    return (PAGE.replace("{{TITLE}}", H.escape(w["title"]))
                .replace("{{WORKPAGE}}", H.escape(f"{w['work']}.html"))
                .replace("{{FONT}}", FONTS.get(lang, '"Gentium Book Plus", Palatino, serif'))
                .replace("{{FAVICON}}", art.get("favicon", ""))
                .replace("/*{{DATA}}*/", f"const R = {js};"))


def write(data: dict, out_dir: Path, art: dict) -> Path:
    out = out_dir / f"{data['work']['work']}.record.html"
    out.write_text(render(data, art))
    return out


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Read aloud: {{TITLE}} · Weft</title>
<link rel="icon" type="image/svg+xml" href="{{FAVICON}}">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Cherokee:wght@400;600&family=Gentium+Book+Plus:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#f6f1e6;--ink:#221d16;--soft:#5d5446;--rule:#ddd3c0;--accent:#9a3b1f;--card:#fbf8f1;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15130f;--ink:#ece4d2;--soft:#b9ad96;--rule:#342f26;--accent:#e08a5f;--card:#1d1a15;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#15130f;--ink:#ece4d2;--soft:#b9ad96;--rule:#342f26;--accent:#e08a5f;--card:#1d1a15;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--ink);font:1.05rem/1.55 Inter,system-ui,sans-serif}
main{max-width:820px;margin:0 auto;padding:28px 16px 64px}
a{color:var(--accent)}h1{font:700 1.5rem/1.25 "Gentium Book Plus",Palatino,serif;margin:.3rem 0 .6rem}
.soft{color:var(--soft);font-size:.92rem}
fieldset{border:1px solid var(--rule);border-radius:8px;padding:12px 14px;margin:16px 0}
legend{font-weight:600;padding:0 6px}label{display:block;margin:8px 0}
input[type=text],select{font:inherit;padding:6px 8px;border:1px solid var(--rule);border-radius:5px;background:var(--card);color:var(--ink);width:100%;max-width:360px;box-sizing:border-box}
select{max-width:100%}
.card{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:22px 18px;margin:18px 0;text-align:center}
.which{font-size:.85rem;color:var(--soft);letter-spacing:.03em}
.text{font-family:{{FONT}};font-size:clamp(1.8rem,6vw,3rem);line-height:1.5;margin:14px 0;overflow-wrap:anywhere}
.say{font-size:.9rem;color:var(--soft)}
.bar{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:14px}
button{font:600 1rem Inter,system-ui,sans-serif;padding:10px 18px;border-radius:8px;border:1px solid var(--rule);background:var(--bg);color:var(--ink);cursor:pointer;min-width:96px}
button.rec{background:var(--accent);color:#fff;border-color:var(--accent)}button.on{animation:pulse 1s infinite}
button:disabled{opacity:.45;cursor:default}
@keyframes pulse{50%{opacity:.6}}
.dots{display:flex;flex-wrap:wrap;gap:4px;justify-content:center;margin-top:12px}
.dots span{width:12px;height:12px;border-radius:50%;border:1px solid var(--soft);cursor:pointer}
.dots span.done{background:var(--accent);border-color:var(--accent)}.dots span.here{outline:2px solid var(--ink);outline-offset:1px}
#msg{min-height:1.4em;color:var(--accent);font-size:.92rem;margin:8px 0}
@media print{.bar,.dots,fieldset{display:none}}
</style></head><body><main>
<p class="soft"><a href="{{WORKPAGE}}">Back to the text</a> · <a href="speakers.html">What Weft asks and promises</a></p>
<h1>Read aloud: {{TITLE}}</h1>
<p>Each line appears on its own, in the original writing only, so that the reading is yours. Read it as you would say it.
Record, listen, and record again until it sounds right, then go on. After the lines come single words
Weft is unsure of: say each one twice, and if you like, write what it means. Do as many or as few as you like. At the end, save the recordings and send the file to Weft. Nothing leaves this
computer until you send it.</p>
<fieldset><legend>About you (goes with the recordings)</legend>
<label>Credit: your name, a name you choose, or leave empty to stay anonymous<br><input type="text" id="credit"></label>
<label>Your way of speaking (for example Oklahoma, Kituwah)<br><input type="text" id="dialect"></label>
<label>License<br><select id="license">
<option value="rights-retained">I keep all rights; Weft may display the recording by my permission only</option>
<option value="CC BY-SA 4.0">CC BY-SA 4.0: others may reuse it with credit, under the same terms</option>
<option value="CC0">CC0: public domain</option></select></label>
<p class="soft">Weft does not use these recordings to train any AI model, and you can withdraw them at any time.</p>
</fieldset>
<div class="card">
  <div class="which" id="which"></div>
  <div class="text" id="text"></div>
  <div class="say" id="say"></div>
  <label class="say" id="senselabel" hidden>What this word means, in your words (optional)<br><input type="text" id="sense"></label>
  <div class="bar">
    <button id="back">Back</button>
    <button id="rec" class="rec">Record</button>
    <button id="play" disabled>Listen</button>
    <button id="next">Next</button>
  </div>
  <div class="dots" id="dots"></div>
</div>
<div id="msg" role="status"></div>
<div class="bar"><button id="save" disabled>Save all recordings</button></div>
<p class="soft" id="send"></p>
</main>
<script>
/*{{DATA}}*/
(() => {
  const $ = (id) => document.getElementById(id);
  const takes = {};               // item id -> {blob, ext}
  const senses = {};              // word id -> the speaker's own sense of it
  let i = 0, rec = null, chunks = [], stream = null, audio = null;
  $("text").lang = R.lang;
  const mime = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg;codecs=opus"]
    .find((m) => window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(m)) || "";
  const extOf = (m) => (m.includes("mp4") ? "m4a" : m.includes("ogg") ? "ogg" : "webm");
  const lines = R.items.filter((x) => x.kind === "line").length;

  const show = () => {
    const it = R.items[i];
    const n = it.kind === "line" ? `Line ${i + 1} of ${lines}` : `Word ${i - lines + 1} of ${R.items.length - lines}`;
    $("which").textContent = `${n} · ${it.id}`;
    $("text").textContent = it.text;
    $("say").textContent = it.kind === "word"
      ? "A word Weft is unsure of. Say it twice, with a short pause between. As many or as few as you like: save whenever you stop."
      : "";
    $("senselabel").hidden = it.kind !== "word";
    $("sense").value = senses[it.id] || "";
    $("play").disabled = !takes[it.id];
    $("rec").textContent = takes[it.id] ? "Record again" : "Record";
    $("back").disabled = i === 0;
    $("next").disabled = i === R.items.length - 1;
    $("save").disabled = !Object.keys(takes).length;
    [...$("dots").children].forEach((d, k) => {
      d.className = (takes[R.items[k].id] ? "done" : "") + (k === i ? " here" : "");
    });
  };
  $("sense").oninput = () => { const v = $("sense").value.trim(); const id = R.items[i].id; if (v) senses[id] = v; else delete senses[id]; };
  R.items.forEach((it, k) => {
    const d = document.createElement("span");
    d.title = it.id;
    d.onclick = () => { if (!rec) { i = k; show(); } };
    $("dots").append(d);
  });

  const stop = () => { if (rec && rec.state !== "inactive") rec.stop(); };
  $("rec").onclick = async () => {
    if (rec) return stop();
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      $("msg").textContent = "Recording needs permission to use the microphone. If the browser did not ask, open this page from weftlibrary.org, or allow the microphone in the browser's settings.";
      return;
    }
    const id = R.items[i].id;
    chunks = [];
    rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
    rec.ondataavailable = (e) => e.data.size && chunks.push(e.data);
    rec.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      stream = null;
      const type = rec.mimeType || mime || "audio/webm";
      takes[id] = { blob: new Blob(chunks, { type }), ext: extOf(type) };
      rec = null;
      $("rec").classList.remove("on");
      $("msg").textContent = "";
      show();
    };
    rec.start();
    $("rec").textContent = "Stop";
    $("rec").classList.add("on");
    $("msg").textContent = "Recording…";
  };
  $("play").onclick = () => {
    const t = takes[R.items[i].id];
    if (!t) return;
    if (audio) audio.pause();
    audio = new Audio(URL.createObjectURL(t.blob));
    audio.play();
  };
  $("back").onclick = () => { stop(); if (i > 0) { i--; show(); } };
  $("next").onclick = () => { stop(); if (i < R.items.length - 1) { i++; show(); } };

  // a zip without compression (audio is compressed already): local headers, the files, the central directory
  const CRC = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
    return (b) => { let c = 0xffffffff; for (let k = 0; k < b.length; k++) c = t[(c ^ b[k]) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
  })();
  const zip = (files) => {
    const enc = new TextEncoder(), parts = [], dir = [];
    const now = new Date();
    const dosTime = (now.getHours() << 11) | (now.getMinutes() << 5) | (now.getSeconds() >> 1);
    const dosDate = ((now.getFullYear() - 1980) << 9) | ((now.getMonth() + 1) << 5) | now.getDate();
    let off = 0;
    for (const f of files) {
      const name = enc.encode(f.name), crc = CRC(f.data), n = f.data.length;
      const h = new DataView(new ArrayBuffer(30));
      h.setUint32(0, 0x04034b50, true); h.setUint16(4, 20, true); h.setUint16(6, 0x0800, true);
      h.setUint16(10, dosTime, true); h.setUint16(12, dosDate, true);
      h.setUint32(14, crc, true); h.setUint32(18, n, true); h.setUint32(22, n, true); h.setUint16(26, name.length, true);
      parts.push(h, name, f.data);
      const c = new DataView(new ArrayBuffer(46));
      c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true); c.setUint16(8, 0x0800, true);
      c.setUint16(12, dosTime, true); c.setUint16(14, dosDate, true);
      c.setUint32(16, crc, true); c.setUint32(20, n, true); c.setUint32(24, n, true); c.setUint16(28, name.length, true);
      c.setUint32(42, off, true);
      dir.push(c, name);
      off += 30 + name.length + n;
    }
    const size = dir.reduce((s, x) => s + x.byteLength, 0);
    const e = new DataView(new ArrayBuffer(22));
    e.setUint32(0, 0x06054b50, true); e.setUint16(8, files.length, true); e.setUint16(10, files.length, true);
    e.setUint32(12, size, true); e.setUint32(16, off, true);
    return new Blob([...parts, ...dir, e], { type: "application/zip" });
  };
  $("save").onclick = async () => {
    const files = [];
    for (const it of R.items) {
      const t = takes[it.id];
      if (t) files.push({ name: `${it.id}.${t.ext}`, data: new Uint8Array(await t.blob.arrayBuffer()) });
    }
    const credit = $("credit").value.trim();
    const meta = {
      work: R.work, kind: "speaker", dialect: $("dialect").value.trim(),
      reader: credit ? { credit, anonymous: false } : { anonymous: true },
      license: $("license").value,
      conditions: ["no-ai-training"].concat($("license").value === "rights-retained" ? ["display-by-permission"] : []),
      recorded: new Date().toISOString().slice(0, 10),
      files: Object.fromEntries(R.items.filter((it) => takes[it.id]).map((it) => [it.id, `${it.id}.${takes[it.id].ext}`])),
      missing: R.items.filter((it) => !takes[it.id]).map((it) => it.id),
      senses,
    };
    files.push({ name: "speaker.json", data: new TextEncoder().encode(JSON.stringify(meta, null, 2) + "\n") });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(zip(files));
    a.download = `${R.work}-reading.zip`;
    document.body.append(a); a.click(); a.remove();
    saved = true;
    $("send").textContent = R.contact ? `Saved as ${a.download}. Please send it to ${R.contact}.` : `Saved as ${a.download}.`;
  };
  let saved = false;
  window.addEventListener("beforeunload", (e) => { if (Object.keys(takes).length && !saved) { e.preventDefault(); e.returnValue = ""; } });
  show();
})();
</script></body></html>
"""
