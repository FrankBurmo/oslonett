let idx = null;
let documents = [];
let selectedIndex = -1;
let loadingInterval = null;

document.addEventListener("DOMContentLoaded", () => {
  const searchBox = document.getElementById("searchBox");
  const modal = document.getElementById("searchModal");
  const resultsContainer = document.getElementById("searchResults");

  if (!searchBox || !modal || !resultsContainer) {
    console.error("Search UI elements missing");
    return;
  }

  // --- Loading animation ---
  startLoadingAnimation(searchBox);
  searchBox.disabled = true;

  initSearch();

  // --- Keyboard shortcuts ---
  document.addEventListener("keydown", (e) => {
    // Open search with "/" (not inside input)
    if (e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      e.preventDefault();
      openSearchModal();
    }

    // Ctrl+K / Cmd+K
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openSearchModal();
    }

    // ESC closes
    if (e.key === "Escape") {
      modal.style.display = "none";
    }

    handleKeyboardNavigation(e);
  });

  // --- Typing ---
  let debounce;
  searchBox.addEventListener("input", (e) => {
    clearTimeout(debounce);

    debounce = setTimeout(() => {
      const query = e.target.value.trim();

      if (!query) {
        resultsContainer.innerHTML = "";
        selectedIndex = -1;
        return;
      }

      if (!idx) {
        resultsContainer.innerHTML = "<p>Search not ready</p>";
        return;
      }

      const results = search(query);
      renderResults(results);

    }, 200);
  });
});


// ==========================
// 🔍 SEARCH
// ==========================

function search(query) {
  if (!query || !idx) return [];

  try {
    // Wildcard + fuzzy fix
    const lunrQuery = `${query}* ${query}~1`;

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
// 🧱 INIT
// ==========================

async function initSearch() {
  const searchBox = document.getElementById("searchBox");
  const resultsContainer = document.getElementById("searchResults");

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

    resultsContainer.innerHTML = "<p>Search ready.</p>";

  } catch (err) {
    console.error(err);
    stopLoadingAnimation(searchBox);
    searchBox.placeholder = "Search unavailable";
  }
}


// ==========================
// 🪟 MODAL
// ==========================

function openSearchModal() {
  const modal = document.getElementById("searchModal");
  const searchBox = document.getElementById("searchBox");

  modal.style.display = "block";

  setTimeout(() => {
    searchBox.focus();
  }, 50);
}


// ==========================
// 🎨 RENDER
// ==========================

function renderResults(results) {
  const container = document.getElementById("searchResults");
  container.innerHTML = "";
  selectedIndex = -1;

  if (!results.length) {
    container.innerHTML = "<p>No results found.</p>";
    return;
  }

  const query = document.getElementById("searchBox").value;
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
// 🔦 HIGHLIGHT
// ==========================

function highlight(text, query) {
  if (!text) return "";

  const safeQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${safeQuery})`, "gi");

  return text.replace(regex, "<mark>$1</mark>");
}


// ==========================
// ⌨️ KEYBOARD NAVIGATION
// ==========================

function handleKeyboardNavigation(e) {
  const items = document.querySelectorAll("#searchResults div");

  if (!items.length) return;

  if (e.key === "ArrowDown") {
    e.preventDefault();
    selectedIndex = (selectedIndex + 1) % items.length;
    updateSelection(items);
  }

  if (e.key === "ArrowUp") {
    e.preventDefault();
    selectedIndex = (selectedIndex - 1 + items.length) % items.length;
    updateSelection(items);
  }

  if (e.key === "Enter" && selectedIndex >= 0) {
    const link = items[selectedIndex].querySelector("a");
    if (link) window.location.href = link.href;
  }
}

function updateSelection(items) {
  items.forEach((el, i) => {
    el.style.background = i === selectedIndex ? "#e0e0e0" : "";
  });
}


// ==========================
// ⏳ LOADING ANIMATION
// ==========================

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
  if (loadingInterval) {
    clearInterval(loadingInterval);
    loadingInterval = null;
  }

  input.placeholder = "Search...";
}
