"use strict";
(() => {
  const data = JSON.parse(document.getElementById("reader-data").textContent);
  const units = new Map(data.units.map(u => [u.id, u]));
  const notes = new Map(data.notes.map(n => [n.id, n]));
  const dialog = document.getElementById("inspector");
  const content = document.getElementById("inspector-content");
  const views = new Set(["reading", "parallel", "notes", "terms"]);
  const readPreference = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const savePreference = (key, value) => { try { localStorage.setItem(key, value); } catch { /* Reading works without storage. */ } };
  let currentView = "reading";
  function showView(view) {
    if (!views.has(view)) return;
    currentView = view;
    document.querySelectorAll(".view").forEach(el => { el.hidden = el.id !== view; });
    document.querySelectorAll(".tabs a").forEach(a => {
      if (a.dataset.view === view) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }
  function route() {
    const id = location.hash.slice(1);
    let view = views.has(id) ? id : id.startsWith("compare-") ? "parallel" : id.startsWith("note-") ? "notes" : id.startsWith("term-") ? "terms" : "reading";
    showView(view);
    document.querySelectorAll(".rail a").forEach(a => a.classList.toggle("active", a.dataset.jump === id.replace("compare-", "")));
    if (id) requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({block: "start"}));
  }
  function go(hash) {
    if (dialog.open) dialog.close();
    if (location.hash === hash) route();
    else location.hash = hash;
  }
  function element(tag, text, className) {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  }
  function addLink(parent, text, hash) {
    const a = element("a", text);
    a.href = hash;
    parent.append(a);
  }
  function ko(uid) {
    return data.translation_blocks.flatMap(b => b.segments.filter(s => s.unit_id === uid).map(s => s.text.trim())).join("\n\n");
  }
  function openUnit(uid) {
    const u = units.get(uid);
    if (!u) return;
    document.getElementById("inspector-title").textContent = `${Number(uid.slice(-3))}. ${u.label}`;
    content.replaceChildren();
    const chinese = element("p", u.chinese, "chinese");
    chinese.lang = "zh-Hant";
    content.append(element("p", ko(uid), "inspector-ko"), chinese, element("p", u.reading, "reading"));
    const links = element("div", undefined, "inspector-links");
    addLink(links, "한문과 나란히 보기", `#compare-${uid}`);
    content.append(links, element("h3", "관련 번역 주"));
    for (const nid of u.note_ids) {
      const original = document.getElementById(nid);
      const section = element("section", undefined, "mini-note");
      const heading = element("h4");
      addLink(heading, `번역 주 ${notes.get(nid).number}`, `#${nid}`);
      section.append(heading, original.querySelector("p").cloneNode(true));
      content.append(section);
    }
    const associated = data.terms.filter(t => t.unit_ids.includes(uid));
    if (associated.length) {
      content.append(element("h3", "관련 용어"));
      for (const t of associated) {
        const section = element("section", undefined, "term");
        const heading = element("h4");
        addLink(heading, `${t.chinese} · ${t.translation}`, `#${t.id}`);
        section.append(heading, document.getElementById(t.id).querySelector(".sanskrit").cloneNode(true));
        content.append(section);
      }
    }
    const source = element("p", "한문 기준: 현장 역 T251 · CBETA 교감 주본문. 관련 산스크리트 문구는 대조 자료입니다.");
    content.append(source);
    dialog.showModal();
    dialog.scrollTop = 0;
  }
  document.documentElement.classList.add("js");
  document.querySelectorAll("[data-unit]").forEach(el => {
    el.tabIndex = 0;
    el.setAttribute("role", "button");
    el.setAttribute("aria-haspopup", "dialog");
    el.setAttribute("aria-description", "이 구절의 번역 주와 용어 살피기");
    el.addEventListener("click", () => openUnit(el.dataset.unit));
    el.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openUnit(el.dataset.unit); }
    });
  });
  document.addEventListener("click", e => {
    const a = e.target.closest("a[href^='#']");
    if (!a || a.classList.contains("skip")) return;
    let hash = a.getAttribute("href");
    if (a.dataset.jump && currentView === "parallel") hash = `#compare-${a.dataset.jump}`;
    e.preventDefault();
    go(hash);
  });
  document.getElementById("close-inspector").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => document.body.classList.remove("dialog-open"));
  new MutationObserver(() => document.body.classList.toggle("dialog-open", dialog.open)).observe(dialog, {attributes: true, attributeFilter: ["open"]});
  let fontSize = Number(readPreference("heart.reader.font-size")) || 22;
  const applySize = () => {
    fontSize = Math.min(28, Math.max(18, fontSize));
    document.documentElement.style.setProperty("--body-size", `${fontSize}px`);
    document.getElementById("smaller").disabled = fontSize === 18;
    document.getElementById("larger").disabled = fontSize === 28;
    savePreference("heart.reader.font-size", String(fontSize));
  };
  document.getElementById("smaller").addEventListener("click", () => { fontSize--; applySize(); });
  document.getElementById("larger").addEventListener("click", () => { fontSize++; applySize(); });
  applySize();
  const readingToggle = document.getElementById("show-reading");
  readingToggle.checked = readPreference("heart.reader.reading") !== "hidden";
  const applyReading = () => {
    document.documentElement.classList.toggle("hide-reading", !readingToggle.checked);
    savePreference("heart.reader.reading", readingToggle.checked ? "visible" : "hidden");
  };
  readingToggle.addEventListener("change", applyReading);
  applyReading();
  const normalize = text => text.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
  const index = [
    ...data.units.map(u => ({hash: `#compare-${u.id}`, title: `${Number(u.id.slice(-3))}. ${u.label}`, text: `${ko(u.id)} ${u.chinese} ${u.reading}`})),
    ...data.notes.map(n => ({hash: `#${n.id}`, title: `번역 주 ${n.number}`, text: n.text})),
    ...data.terms.map(t => ({hash: `#${t.id}`, title: `${t.chinese} · ${t.translation}`, text: `${t.conventional_reading || ""} ${t.sanskrit_comparison} ${t.translation} ${t.decision}`}))
  ];
  const input = document.getElementById("query");
  function search() {
    const query = normalize(input.value.trim());
    const results = document.getElementById("results");
    results.replaceChildren();
    document.getElementById("search-results").hidden = !query;
    if (!query) return;
    const matches = index.filter(item => normalize(`${item.title} ${item.text}`).includes(query));
    document.getElementById("result-count").textContent = matches.length ? `${matches.length}곳에서 찾았습니다.` : "일치하는 구절이나 용어가 없습니다.";
    for (const item of matches) {
      const a = element("a");
      a.href = item.hash;
      const normalizedPosition = normalize(item.text).indexOf(query);
      // Normalizing Korean syllables expands them; map the match back to the visible text.
      let position = 0, normalizedOffset = 0;
      for (const character of item.text) {
        if (normalizedOffset >= normalizedPosition) break;
        normalizedOffset += normalize(character).length;
        position += character.length;
      }
      const start = Math.max(0, position - 25);
      const excerpt = item.text.slice(start, start + 140).replace(/`/g, "");
      a.append(element("strong", item.title), element("p", `${start ? "…" : ""}${excerpt}${item.text.length > start + 140 ? "…" : ""}`));
      results.append(a);
    }
  }
  document.querySelector("form.search").addEventListener("submit", e => { e.preventDefault(); search(); });
  input.addEventListener("input", search);
  window.addEventListener("hashchange", route);
  route();
})();
