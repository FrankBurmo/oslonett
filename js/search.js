let fuse = null;
let data = [];

document.addEventListener("DOMContentLoaded", () => {
  const searchBox = document.getElementById("searchBox");
  const resultsContainer = document.getElementById("results");
  const modal = document.getElementById("searchModal");
  const closeBtn = document.getElementById("searchClose");

  if (!searchBox || !resultsContainer || !modal || !closeBtn) {
    console.error("Search UI elements not found in DOM");
    return;
  }

  // Disable input until ready
  searchBox.disabled = true;
  resultsContainer.innerHTML = "<p>Loading search index...</p>";

  initSearch();

  // --- Modal controls ---

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  // Close on ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      modal.style.display = "none";
    }
  });

  // Close if clicking outside modal content
  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });

  // --- Search input (debounced) ---

  let debounceTimer;

  searchBox.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(() => {
      const query = e.target.value.trim();

      // Empty query → clear + close modal
      if (!query) {
        resultsContainer.innerHTML = "";
        modal.style.display = "none";
        return;
      }

      // Not ready yet
      if (!fuse) {
        resultsContainer.innerHTML = "<p>Search not ready yet...</p>";
        modal.style.display = "block";
        return;
      }

      const results = fuse.search(query, { limit: 20 });

      renderResults(results);

      // Show modal when results exist
      modal.style.display = "block";

    }, 200);
  });
});

async function initSearch() {
  const resultsContainer = document.getElementById("results");
  const searchBox = document.getElementById("searchBox");

  try {
    const res = await fetch("/js/search-index.json");

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    data = await res.json();

    fuse = new Fuse(data, {
      keys: [
        { name: "title", weight: 0.5 },
        { name: "headings", weight: 0.3 },
        { name: "content", weight: 0.2 }
      ],
      threshold: 0.3,
      ignoreLocation: true,
      useExtendedSearch: true,
      minMatchCharLength: 3
    });

    searchBox.disabled = false;
    resultsContainer.innerHTML = "<p>Search ready.</p>";

  } catch (err) {
    console.error("Failed to load search index:", err);
    resultsContainer.innerHTML = "<p>Failed to load search index.</p>";
  }
}

function renderResults(results) {
  const container = document.getElementById("results");
  container.innerHTML = "";

  if (!results || results.length === 0) {
    container.innerHTML = "<p>No results found.</p>";
    return;
  }

  // Show result count
  const count = document.createElement("p");
  count.textContent = `${results.length} result(s) found`;
  container.appendChild(count);

  results.forEach(r => {
    const item = r.item;

    const div = document.createElement("div");
    div.style.marginBottom = "1em";

    div.innerHTML = `
      <a href="${item.url}" target="_self">
        <strong>${item.title || item.url}</strong>
      </a>
      <p>${(item.content || "").substring(0, 150)}...</p>
    `;

    container.appendChild(div);
  });
}
