// Sistema de Pesquisa Global com Redirecionamento Automático
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  const searchIcon = document.getElementById('searchIcon');
  let isSearchPage = window.location.pathname === '/pesquisa';
  let previousPage = document.referrer || '/';

  function performSearch() {
    const query = searchInput.value.trim();
    if (query) {
      window.location.href = `/pesquisa?q=${encodeURIComponent(query)}`;
    }
  }

  if (searchInput) {
    // Se não estiver na página de pesquisa, redirecionar automaticamente
    if (!isSearchPage) {
      searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        if (query.length >= 1) {
          // Redirecionar imediatamente para a página de pesquisa
          window.location.href = `/pesquisa?q=${encodeURIComponent(query)}`;
        }
      });
    } else {
      // Se estiver na página de pesquisa, voltar quando apagar tudo
      searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        if (query.length === 0) {
          // Voltar para a página anterior
          if (previousPage && previousPage.includes(window.location.host)) {
            window.location.href = previousPage;
          } else {
            window.location.href = '/';
          }
        }
      });
    }

    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        performSearch();
      }
    });
  }

  if (searchIcon) {
    searchIcon.addEventListener('click', performSearch);
  }
});
