let fuse = null;
let data = [];

document.addEventListener("DOMContentLoaded", () => {
  const searchBox = document.getElementById("searchBox");
  const resultsContainer = document.getElementById("results");

  if (!searchBox || !resultsContainer) {
    console.error("Search elements not found in DOM");
    return;
  }

  searchBox.disabled = true;
  resultsContainer.innerHTML = "<p>Loading search index...</p>";

  initSearch();

  // Debounce to avoid firing on every keystroke instantly
  let debounceTimer;
  searchBox.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(() => {
      const query = e.target.value.trim();

      if (!query) {
        resultsContainer.innerHTML = "";
        return;
      }

      if (!fuse) {
        resultsContainer.innerHTML = "<p>Search not ready yet...</p>";
        return;
      }

      const results = fuse.search(query, { limit: 20 });
      renderResults(results);
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
      minMatchCharLength: 2
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

  if (results.length === 0) {
    container.innerHTML = "<p>No results found.</p>";
    return;
  }

  results.forEach(r => {
    const item = r.item;

    const div = document.createElement("div");
    div.style.marginBottom = "1em";

    div.innerHTML = `
      <a href="${item.url}"><strong>${item.title || item.url}</strong></a>
      <p>${(item.content || "").substring(0, 150)}...</p>
    `;

    container.appendChild(div);
  });
}
