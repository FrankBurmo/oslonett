let indexes = [];
let documents = [];
let docMap = {};
let debounceTimer = null;


// ==========================
// 🚀 SAFE INIT (works on all pages)
// ==========================

function initWhenReady() {
  const searchBox = document.getElementById("searchBox");

  // wait until DOM element actually exists
  if (!searchBox) {
    setTimeout(initWhenReady, 50);
    return;
  }

  initSearchUI();
}

document.addEventListener("DOMContentLoaded", initWhenReady);


// ==========================
// 🎯 INIT UI + EVENTS
// ==========================

function initSearchUI() {
  const searchBox = document.getElementById("searchBox");
  const modal = document.getElementById("searchModal");
  const resultsContainer = document.getElementById("searchResults");
  const closeBtn = document.getElementById("searchClose");

  if (!searchBox || !modal || !resultsContainer || !closeBtn) {
    console.error("Search UI elements missing");
    return;
  }

  searchBox.placeholder = "Search index loading...";
  searchBox.disabled = true;

  initSearch();

  // 🔍 INPUT HANDLER
  searchBox.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(() => {
      const query = e.target.value.trim();

      if (query.length < 3) {
        modal.classList.remove("open");
        resultsContainer.innerHTML = "";
        return;
      }

      if (!indexes.length) return;

      const results = searchAll(query);

      renderResults(results, query);

      modal.classList.add("open");

    }, 200);
  });

  // ❌ CLOSE
  closeBtn.onclick = () => modal.classList.remove("open");

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      modal.classList.remove("open");
    }
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.classList.remove("open");
    }
  });
}


// ==========================
// 📦 LOAD INDEXES
// ==========================

async function initSearch() {
  try {
    const meta = await fetch("/js/index/manifest.json").then(r => r.json());

    // load all index chunks in parallel
    const indexPromises = [];

    for (let i = 0; i < meta.chunks; i++) {
      indexPromises.push(
        fetch(`/js/index/index-${i}.json`)
          .then(r => r.json())
          .then(data => lunr.Index.load(data))
      );
    }

    indexes = await Promise.all(indexPromises);

    // load documents
    documents = await fetch("/js/index/docs.json").then(r => r.json());

    // build lookup map
    documents.forEach(d => {
      docMap[d.id] = d;
    });

    const searchBox = document.getElementById("searchBox");
    searchBox.disabled = false;
    searchBox.placeholder = "Search...";

  } catch (err) {
    console.error("Search init failed:", err);

    const searchBox = document.getElementById("searchBox");
    if (searchBox) {
      searchBox.placeholder = "Search failed";
    }
  }
}


// ==========================
// 🔍 SEARCH
// ==========================

function searchAll(query) {
  let results = [];
  const q = query + "*";

  indexes.forEach(idx => {
    try {
      results = results.concat(idx.search(q));
    } catch (e) {}
  });

  return results;
}


// ==========================
// 🎨 RENDER
// ==========================

function renderResults(results, query) {
  const container = document.getElementById("searchResults");
  container.innerHTML = "";

  const count = document.createElement("p");
  count.innerHTML = `<strong>${results.length}</strong> results`;
  container.appendChild(count);

  if (!results.length) {
    const p = document.createElement("p");
    p.textContent = "No results found.";
    container.appendChild(p);
    return;
  }

  results.slice(0, 50).forEach(r => {
    const d = docMap[r.ref];
    if (!d) return;

    const div = document.createElement("div");
    div.style.marginBottom = "1em";

    div.innerHTML = `
      <a href="${d.url}">
        <strong>${highlight(d.title || d.url, query)}</strong>
      </a>
      <p>${highlight(d.content.substring(0, 150), query)}...</p>
    `;

    container.appendChild(div);
  });
}


// ==========================
// 🔦 HIGHLIGHT
// ==========================

function highlight(text, query) {
  if (!text) return "";

  const safe = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return text.replace(new RegExp(`(${safe})`, "gi"), "<mark>$1</mark>");
}
