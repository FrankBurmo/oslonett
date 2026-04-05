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

  // Disable input + loading state
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

      // Require at least 3 characters
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
      renderResults(results);

      modal.style.display = "block";
    }, 200);
  });

  // ==========================
  // ❌ CLOSE MODAL
  // ==========================

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  // ESC closes modal
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      modal.style.display = "none";
    }
  });

  // Click outside closes modal
  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});


// ==========================
// 🔍 SEARCH (Lunr)
// ==========================

function search(query) {
  try {
    const q = `${query}* ${query}~1`;
    const results = idx.search(q);

    return results.map(r => {
      const doc = documents.find(d => d.id === r.ref);
      return { item: doc };
    });

  } catch (e) {
    return [];
  }
}


// ==========================
// 📦 LOAD INDEX
// ==========================

async function initSearch() {
  const searchBox = document.getElementById("searchBox");

  try {
    const [idxRes, dataRes] = await Promise.all([
      fetch("/js/search-index.json"),
      fetch("/js/search-data.json")
    ]);

    const idxJson = await idxRes.json();
    documents = await dataRes.json();

    idx = lunr.Index.load(idxJson);

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
// 🎨 RENDER RESULTS
// ==========================

function renderResults(results) {
  const container = document.getElementById("searchResults");
  const query = document.getElementById("searchBox").value;

  container.innerHTML = "";

  if (!results.length) {
    container.innerHTML = "<p>No results found.</p>";
    return;
  }

  const groups = {};

  // Group by folder
  results.forEach(r => {
    const item = r.item;
    const folder = item.url.split("/")[1] || "root";

    if (!groups[folder]) groups[folder] = [];
    groups[folder].push(item);
  });

  Object.keys(groups).forEach(folder => {
    const header = document.createElement("h3");
    header.textContent = folder;
    container.appendChild(header);

    groups[folder].forEach(item => {
      const div = document.createElement("div");

      div.innerHTML = `
        <a href="${item.url}">
          <strong>${highlight(item.title || item.url, query)}</strong>
        </a>
        <p>${highlight((item.content || "").substring(0, 120), query)}...</p>
      `;

      container.appendChild(div);
    });
  });
}


// ==========================
// 🔦 HIGHLIGHT MATCHES
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
