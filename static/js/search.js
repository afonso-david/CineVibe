document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  const searchIcon = document.getElementById('searchIcon');
  let isSearchPage = window.location.pathname === '/pesquisa';
  let previousPage = document.referrer || '/';
  let searchTimeout;

  function performSearch() {
    const query = searchInput.value.trim();
    if (query) {
      window.location.href = `/pesquisa?q=${encodeURIComponent(query)}`;
    }
  }

  if (searchInput) {
    if (!isSearchPage) {
      searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length >= 1) {
          searchTimeout = setTimeout(() => {
            window.location.href = `/pesquisa?q=${encodeURIComponent(query)}`;
          }, 300);
        }
      });
    } else {
      searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length === 0) {
          searchTimeout = setTimeout(() => {
            if (previousPage && previousPage.includes(window.location.host)) {
              window.location.href = previousPage;
            } else {
              window.location.href = '/';
            }
          }, 300);
        }
      });
    }

    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        clearTimeout(searchTimeout);
        performSearch();
      }
    });
  }

  if (searchIcon) {
    searchIcon.addEventListener('click', performSearch);
  }
});
