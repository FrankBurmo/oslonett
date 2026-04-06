let idx = null;
let documents = [];
let debounceTimer = null;

// ==========================
// 🚀 INIT
// ==========================

document.addEventListener("DOMContentLoaded", () => {
  const searchBox = document.getElementById("searchBox");
  const modal = document.getElementById("searchModal");
  const resultsContainer = document.getElementById("searchResults");
  const closeBtn = document.getElementById("searchClose");

  if (!searchBox || !modal || !resultsContainer || !closeBtn) {
    console.error("Search UI elements missing");
    return;
  }

  // Disable input + loading animation
  searchBox.disabled = true;
  startLoadingAnimation(searchBox);

  initSearch();

  // ==========================
  // 🔍 INPUT HANDLER
  // ==========================

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
        resultsContainer.innerHTML = "<p>Search not ready</p>";
        return;
      }

      const results = search(query);
      renderResults(results, query);

      modal.style.display = "block";
    }, 200);
  });

  // ==========================
  // ❌ CLOSE MODAL
  // ==========================

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      modal.style.display = "none";
    }
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});


// ==========================
// 📦 LOAD ALL CHUNKS IN PARALLEL
// ==========================

async function loadAllDocuments() {
  const res = await fetch("/js/index/manifest.json");
  const meta = await res.json();

  const promises = [];

  for (let i = 0; i < meta.chunks; i++) {
    promises.push(
      fetch(`/js/index/data-${i}.json`).then(r => r.json())
    );
  }

  const chunks = await Promise.all(promises);

  return chunks.flat();
}


// ==========================
// 📦 INIT SEARCH
// ==========================

async function initSearch() {
  const searchBox = document.getElementById("searchBox");

  try {
    documents = await loadAllDocuments();

    // Build Lunr index
    idx = lunr(function () {
      this.ref("id");

      this.field("title", { boost: 10 });
      this.field("headings", { boost: 5 });
      this.field("content");

      documents.forEach(doc => this.add(doc));
    });

    stopLoadingAnimation(searchBox);
    searchBox.disabled = false;
    searchBox.placeholder = "Search...";

  } catch (err) {
    console.error(err);
    stopLoadingAnimation(searchBox);
    searchBox.placeholder = "Search unavailable";
  }
}


// ==========================
// 🔍 SEARCH
// ==========================

function search(query) {
  if (!query || !idx) return [];

  try {
    const terms = query.split(/\s+/).map(term => {
      if (term.length < 3) return term;
      return `${term}*`;
    });

    const lunrQuery = terms.join(" ");
    const results = idx.search(lunrQuery);

    return results.map(r => {
      const doc = documents.find(d => d.id === r.ref);
      return { item: doc };
    });

  } catch (e) {
    return [];
  }
}


// ==========================
// 🎨 RENDER RESULTS
// ==========================

function renderResults(results, query) {
  const container = document.getElementById("searchResults");
  container.innerHTML = "";

  if (!results.length) {
    container.innerHTML = "<p><strong>0</strong> results</p><p>No results found.</p>";
    return;
  }

  // Result count
  const count = document.createElement("p");
  count.innerHTML = `<strong>${results.length}</strong> results`;
  container.appendChild(count);

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

  const safe = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
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
