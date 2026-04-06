let idx = null;
let documents = [];
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

  searchBox.disabled = true;
  startLoadingAnimation(searchBox);

  initSearch();

  // 🔍 INPUT HANDLER
  searchBox.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(() => {
      const query = e.target.value.trim();

      if (query.length < 3) {
        modal.style.display = "none";
        resultsContainer.innerHTML = "";
        return;
      }

      if (!idx) {
        console.warn("Index not ready yet");
        return;
      }

      const results = search(query);

      console.log("Query:", query, "Results:", results.length);

      renderResults(results, query);

      // ✅ ALWAYS open modal if query is valid
      modal.style.display = "block";

    }, 200);
  });

  // ❌ CLOSE BUTTON
  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  // ESC CLOSE
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      modal.style.display = "none";
    }
  });

  // CLICK OUTSIDE CLOSE
  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});


// ==========================
// 📦 LOAD CHUNKS IN PARALLEL
// ==========================

async function loadAllDocuments() {
  const res = await fetch("/js/index/manifest.json");

  if (!res.ok) {
    throw new Error("Failed to load manifest.json");
  }

  const meta = await res.json();
  console.log("Chunks:", meta.chunks);

  const promises = [];

  for (let i = 0; i < meta.chunks; i++) {
    promises.push(
      fetch(`/js/index/data-${i}.json`)
        .then(r => {
          if (!r.ok) throw new Error(`Chunk ${i} failed`);
          return r.json();
        })
    );
  }

  const chunks = await Promise.all(promises);
  const allDocs = chunks.flat();

  console.log("Documents loaded:", allDocs.length);

  return allDocs;
}


// ==========================
// 🚀 INIT SEARCH
// ==========================

async function initSearch() {
  const searchBox = document.getElementById("searchBox");

  try {
    documents = await loadAllDocuments();

    idx = lunr(function () {
      this.ref("id");

      this.field("title", { boost: 10 });
      this.field("headings", { boost: 5 });
      this.field("content");

      documents.forEach(doc => this.add(doc));
    });

    console.log("Index ready");

    stopLoadingAnimation(searchBox);
    searchBox.disabled = false;
    searchBox.placeholder = "Search...";

  } catch (err) {
    console.error("INIT FAILED:", err);
    stopLoadingAnimation(searchBox);
    searchBox.placeholder = "Search failed";
  }
}


// ==========================
// 🔍 SEARCH
// ==========================

function search(query) {
  try {
    const terms = query.split(/\s+/).map(term => {
      if (term.length < 3) return term;
      return `${term}*`;
    });

    const q = terms.join(" ");
    const results = idx.search(q);

    return results.map(r => {
      const doc = documents.find(d => d.id === r.ref);
      return { item: doc };
    });

  } catch (e) {
    console.error("Search error:", e);
    return [];
  }
}


// ==========================
// 🎨 RENDER RESULTS
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

  results.forEach(r => {
    const item = r.item;

    const div = document.createElement("div");
    div.style.marginBottom = "1em";

    div.innerHTML = `
      <a href="${item.url}">
        <strong>${highlight(item.title || item.url, query)}</strong>
      </a>
      <p>${highlight((item.content || "").substring(0, 150), query)}...</p>
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
  const regex = new RegExp(`(${safe})`, "gi");

  return text.replace(regex, "<mark>$1</mark>");
}


// ==========================
// ⏳ LOADING ANIMATION
// ==========================

let loadingInterval;

function startLoadingAnimation(input) {
  const states = [
    "Search index loading.",
    "Search index loading..",
    "Search index loading..."
  ];

  let i = 0;

  loadingInterval = setInterval(() => {
    input.placeholder = states[i % states.length];
    i++;
  }, 400);
}

function stopLoadingAnimation(input) {
  clearInterval(loadingInterval);
}
