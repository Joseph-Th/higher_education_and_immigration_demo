const cards = [...document.querySelectorAll('.library-card')];
const search = document.querySelector('#library-search');
const populationFilter = document.querySelector('#library-population-filter');
const typeFilter = document.querySelector('#library-type-filter');
const publisherFilter = document.querySelector('#library-publisher-filter');
const reset = document.querySelector('#library-reset');
const resultCount = document.querySelector('#library-result-count');
const empty = document.querySelector('#library-empty');

function applyLibraryFilters() {
  const query = search.value.trim().toLowerCase();
  const population = populationFilter.value;
  const type = typeFilter.value;
  const publisher = publisherFilter.value;
  let visible = 0;

  cards.forEach(card => {
    const matchesQuery = !query || card.dataset.search.includes(query);
    const populations = (card.dataset.populations || '').split(';').filter(Boolean);
    const matchesPopulation = !population || populations.includes(population) || populations.includes('All populations');
    const matchesType = !type || card.dataset.type === type;
    const matchesPublisher = !publisher || card.dataset.publisher === publisher;
    const show = matchesQuery && matchesPopulation && matchesType && matchesPublisher;
    card.hidden = !show;
    if (show) visible += 1;
  });

  resultCount.textContent = `${visible} of ${cards.length} resources`;
  empty.hidden = visible !== 0;
}

[search, populationFilter, typeFilter, publisherFilter].forEach(control => {
  control.addEventListener('input', applyLibraryFilters);
  control.addEventListener('change', applyLibraryFilters);
});

reset.addEventListener('click', () => {
  search.value = '';
  populationFilter.value = '';
  typeFilter.value = '';
  publisherFilter.value = '';
  applyLibraryFilters();
  search.focus();
});
