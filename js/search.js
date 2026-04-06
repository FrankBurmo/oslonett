let indexes = [];
let documents = [];
let docMap = {};
let debounceTimer = null;

document.addEventListener("DOMContentLoaded", () => {
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

  // ==========================
  // 🔍 INPUT HANDLER
  // ==========================
  searchBox.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(() => {
      const query = e.target.value.trim();

      if (query.length < 3) {
        modal.classList.remove("open");
        resultsContainer.innerHTML = "";
        return;
      }

      if (!indexes.length) {
        console.warn("Indexes not ready yet");
        return;
      }

      const results = searchAll(query);

      renderResults(results, query);
      modal.classList.add("open");

    }, 200);
  });

  // ==========================
  // ❌ CLOSE HANDLERS
  // ==========================
  closeBtn.addEventListener("click", () => {
    modal.classList.remove("open");
  });

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
});


// ==========================
// 🚀 INIT SEARCH
// ==========================

async function initSearch() {
  try {
    // Load manifest
    const meta = await fetch("/js/index/manifest.json").then(r => r.json());

    console.log("Chunks:", meta.chunks);

    // Load all index chunks in parallel
    const indexPromises = [];

    for (let i = 0; i < meta.chunks; i++) {
      indexPromises.push(
        fetch(`/js/index/index-${i}.json`)
          .then(r => {
            if (!r.ok) throw new Error(`Index ${i} failed`);
            return r.json();
          })
          .then(data => lunr.Index.load(data))
      );
    }

    indexes = await Promise.all(indexPromises);

    console.log("Indexes loaded:", indexes.length);

    // Load document store
    documents = await fetch("/js/index/docs.json").then(r => r.json());

    // Build lookup map (fast access)
    documents.forEach(d => {
      docMap[d.id] = d;
    });

    console.log("Documents loaded:", documents.length);

    const searchBox = document.getElementById("searchBox");
    searchBox.disabled = false;
    searchBox.placeholder = "Search...";

    console.log("Search ready");

  } catch (err) {
    console.error("Search init failed:", err);

    const searchBox = document.getElementById("searchBox");
    searchBox.placeholder = "Search failed";
  }
}


// ==========================
// 🔍 SEARCH ACROSS ALL INDEXES
// ==========================

function searchAll(query) {
  let results = [];

  // Prefix search for better UX
  const q = query + "*";

  indexes.forEach(idx => {
    try {
      const r = idx.search(q);
      results = results.concat(r);
    } catch (e) {
      console.warn("Search error in chunk:", e);
    }
  });

  return results;
}


// ==========================
// 🎨 RENDER RESULTS
// ==========================

function renderResults(results, query) {
  const container = document.getElementById("searchResults");
  container.innerHTML = "";

  // Result count
  const count = document.createElement("p");
  count.innerHTML = `<strong>${results.length}</strong> results`;
  container.appendChild(count);

  if (!results.length) {
    const p = document.createElement("p");
    p.textContent = "No results found.";
    container.appendChild(p);
    return;
  }

  // Limit results (important!)
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
// 🔦 HIGHLIGHT MATCHES
// ==========================

function highlight(text, query) {
  if (!text) return "";

  const safe = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(${safe})`, "gi");

  return text.replace(regex, "<mark>$1</mark>");
}
