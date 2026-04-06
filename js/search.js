let idx = null;
let documents = [];
let docMap = {};
let debounceTimer = null;

document.addEventListener("DOMContentLoaded", () => {
  const searchBox = document.getElementById("searchBox");
  const modal = document.getElementById("searchModal");
  const resultsContainer = document.getElementById("searchResults");
  const closeBtn = document.getElementById("searchClose");

  if (!searchBox || !modal || !resultsContainer || !closeBtn) {
    console.error("Search UI missing");
    return;
  }

  searchBox.disabled = true;
  searchBox.placeholder = "Search index loading...";

  initSearch();

  searchBox.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(() => {
      const query = e.target.value.trim();

      if (query.length < 3) {
        modal.classList.remove("open");
        return;
      }

      if (!idx) return;

      const results = idx.search(query + "*");

      renderResults(results, query);
      modal.classList.add("open");

    }, 200);
  });

  closeBtn.onclick = () => modal.classList.remove("open");
});


// ==========================
// 🚀 INIT
// ==========================

async function initSearch() {
  try {
    const [idxRes, docsRes] = await Promise.all([
      fetch("/js/search-index.json"),
      fetch("/js/search-docs.json")
    ]);

    const idxData = await idxRes.json();
    documents = await docsRes.json();

    idx = lunr.Index.load(idxData);

    // Build lookup map
    documents.forEach(d => docMap[d.id] = d);

    const searchBox = document.getElementById("searchBox");
    searchBox.disabled = false;
    searchBox.placeholder = "Search...";

    console.log("Search ready");

  } catch (e) {
    console.error("Search init failed:", e);
  }
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

  results.slice(0, 50).forEach(r => {
    const d = docMap[r.ref];

    const div = document.createElement("div");
    div.innerHTML = `
      <a href="${d.url}">
        <strong>${highlight(d.title || d.url, query)}</strong>
      </a>
      <p>${highlight(d.content.substring(0,150), query)}...</p>
    `;

    container.appendChild(div);
  });
}


// ==========================
// 🔦 HIGHLIGHT
// ==========================

function highlight(text, query) {
  const safe = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return text.replace(new RegExp(`(${safe})`, "gi"), "<mark>$1</mark>");
}
