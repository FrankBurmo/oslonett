let idx = null;
let documents = [];

document.addEventListener("DOMContentLoaded", () => {
  const searchBox = document.getElementById("searchBox");
  const modal = document.getElementById("searchModal");
  const resultsContainer = document.getElementById("searchResults");
  const closeBtn = document.getElementById("searchClose");



  searchBox.disabled = true;
  searchBox.placeholder = "Laster søkeindeks...";
  
  resultsContainer.innerHTML = "<p>Laster søkeindeks...</p>";

  initSearch();

  // Modal controls
  closeBtn.onclick = () => modal.style.display = "none";

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") modal.style.display = "none";
  });

  window.onclick = (e) => {
    if (e.target === modal) modal.style.display = "none";
  };

  let debounce;
  searchBox.addEventListener("input", (e) => {
    clearTimeout(debounce);

    debounce = setTimeout(() => {
      const query = e.target.value.trim();

      if (!query) {
        modal.style.display = "none";
        resultsContainer.innerHTML = "";
        return;
      }

      if (!idx) {
        resultsContainer.innerHTML = "<p>Ikke klart for søk</p>";
        modal.style.display = "block";
        return;
      }

      const results = search(query);
      renderResults(results);

      modal.style.display = "block";
    }, 200);
  });
});

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

    searchBox.disabled = false;
    searchBox.placeholder = "Søk ..";

    resultsContainer.innerHTML = "<p>Søk klart</p>";


  } catch (err) {
    console.error(err);
    resultsContainer.innerHTML = "<p>Klarte ikke å laste søkeindeks</p>";
  }
}

function search(query) {
  try {
    const results = idx.search(query);

    return results.map(r => {
      const doc = documents.find(d => d.id === r.ref);
      return { item: doc };
    });

  } catch (e) {
    // fallback for invalid query syntax
    return [];
  }
}

function renderResults(results) {
  const container = document.getElementById("searchResults");
  container.innerHTML = "";

  if (results.length === 0) {
    container.innerHTML = "<p>No results found.</p>";
    return;
  }

  container.innerHTML += `<p>${results.length} result(s)</p>`;

  results.forEach(r => {
    const item = r.item;

    const div = document.createElement("div");
    div.style.marginBottom = "1em";

    div.innerHTML = `
      <a href="${item.url}">
        <strong>${item.title || item.url}</strong>
      </a>
      <p>${item.content.substring(0, 150)}...</p>
    `;

    container.appendChild(div);
  });
}
