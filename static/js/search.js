document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;

  let searchTimeout;
  let dropdown = null;
  let currentFocus = -1;

  // Create dropdown container — appended to body to avoid overflow clipping
  function createDropdown() {
    if (dropdown) return;
    dropdown = document.createElement('div');
    dropdown.id = 'search-dropdown';
    document.body.appendChild(dropdown);
    positionDropdown();
  }

  function positionDropdown() {
    if (!dropdown) return;
    const rect = searchInput.getBoundingClientRect();
    dropdown.style.cssText = `
      position: fixed;
      top: ${rect.bottom + 4}px;
      left: ${rect.left}px;
      width: ${rect.width}px;
      background: #1B263B;
      border: 1px solid rgba(255,214,10,0.4);
      border-radius: 0 0 12px 12px;
      max-height: 420px;
      overflow-y: auto;
      z-index: 99999;
    `;
  }

  function removeDropdown() {
    if (dropdown) {
      dropdown.remove();
      dropdown = null;
      currentFocus = -1;
    }
  }

  function renderResults(data) {
    createDropdown();
    positionDropdown();
    dropdown.innerHTML = '';
    currentFocus = -1;

    const { filmes = [], cinemas = [], menus = [], produtos = [], acessibilidade = [] } = data;
    const total = filmes.length + cinemas.length + menus.length + produtos.length + acessibilidade.length;

    if (total === 0) {
      dropdown.innerHTML = `<div style="padding:16px; color:rgba(255,255,255,0.5); text-align:center; font-size:14px;">Sem resultados para "${searchInput.value}"</div>`;
      return;
    }

    function addSection(title, items, renderItem) {
      if (!items.length) return;
      const header = document.createElement('div');
      header.style.cssText = 'padding:8px 16px 4px; color:#FFD60A; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; border-top:1px solid rgba(255,255,255,0.05);';
      header.textContent = title;
      dropdown.appendChild(header);
      items.forEach(item => dropdown.appendChild(renderItem(item)));
    }

    function makeRow(href, imgSrc, title, subtitle, square = false) {
      const row = document.createElement('a');
      row.href = href;
      row.style.cssText = 'display:flex; align-items:center; gap:12px; padding:10px 16px; text-decoration:none; transition:background 0.15s; cursor:pointer;';
      row.addEventListener('mouseenter', () => row.style.background = 'rgba(255,214,10,0.08)');
      row.addEventListener('mouseleave', () => { if (!row.classList.contains('focused')) row.style.background = ''; });

      if (imgSrc) {
        const img = document.createElement('img');
        img.src = imgSrc.startsWith('http') ? imgSrc : `/static/${imgSrc}`;
        img.style.cssText = square
          ? 'width:48px; height:48px; object-fit:cover; border-radius:6px; flex-shrink:0;'
          : 'width:40px; height:56px; object-fit:cover; border-radius:4px; flex-shrink:0;';
        img.onerror = () => img.style.display = 'none';
        row.appendChild(img);
      }

      const text = document.createElement('div');
      text.innerHTML = `<div style="color:#fff; font-size:14px; font-weight:600;">${title}</div>${subtitle ? `<div style="color:rgba(255,255,255,0.45); font-size:12px; margin-top:2px;">${subtitle}</div>` : ''}`;
      row.appendChild(text);
      return row;
    }

    function makeSimpleRow(href, title, subtitle) {
      const row = document.createElement('a');
      row.href = href;
      row.style.cssText = 'display:flex; align-items:center; gap:12px; padding:10px 16px; text-decoration:none; transition:background 0.15s; cursor:pointer;';
      row.addEventListener('mouseenter', () => row.style.background = 'rgba(255,214,10,0.08)');
      row.addEventListener('mouseleave', () => { if (!row.classList.contains('focused')) row.style.background = ''; });

      const icon = document.createElement('i');
      icon.className = 'fas fa-universal-access';
      icon.style.cssText = 'width:40px; height:40px; display:flex; align-items:center; justify-content:center; background:rgba(255,214,10,0.1); border-radius:8px; color:#FFD60A; font-size:18px; flex-shrink:0;';
      row.appendChild(icon);

      const text = document.createElement('div');
      text.innerHTML = `<div style="color:#fff; font-size:14px; font-weight:600;">${title}</div>${subtitle ? `<div style="color:rgba(255,255,255,0.45); font-size:12px; margin-top:2px;">${subtitle}</div>` : ''}`;
      row.appendChild(text);
      return row;
    }

    addSection('Filmes', filmes, f =>
      makeRow(`/filme/${f.id}`, f.poster_url, f.titulo, f.duracao ? `${f.duracao} min` : '')
    );
    addSection('Cinemas', cinemas, c =>
      makeRow(`/cinemas/${c.id}/filmes`, c.imagem_url, c.nome, c.localizacao || '')
    );
    addSection('Acessibilidade', acessibilidade, a =>
      makeSimpleRow(a.url, a.nome, a.descricao)
    );
    addSection('Bar', menus, m =>
      makeRow(`/bar`, m.imagem_url, m.nome, m.preco ? `€${parseFloat(m.preco).toFixed(2)}` : '', true)
    );
    addSection('Produtos', produtos, p =>
      makeRow(`/bar`, p.imagem_url, p.nome, p.preco ? `€${parseFloat(p.preco).toFixed(2)}` : '', true)
    );

    // "Ver todos os resultados" link
    const seeAll = document.createElement('a');
    seeAll.href = `/pesquisa?q=${encodeURIComponent(searchInput.value.trim())}`;
    seeAll.style.cssText = 'display:block; padding:12px 16px; text-align:center; color:#FFD60A; font-size:13px; font-weight:600; border-top:1px solid rgba(255,214,10,0.2); text-decoration:none;';
    seeAll.textContent = `Ver todos os resultados →`;
    seeAll.addEventListener('mouseenter', () => seeAll.style.background = 'rgba(255,214,10,0.08)');
    seeAll.addEventListener('mouseleave', () => seeAll.style.background = '');
    dropdown.appendChild(seeAll);
  }

  function doSearch(query) {
    fetch(`/api/pesquisa?q=${encodeURIComponent(query)}`)
      .then(r => r.json())
      .then(data => renderResults(data))
      .catch(() => removeDropdown());
  }

  // Input handler — search from 1st character, keep focus
  searchInput.addEventListener('input', function () {
    clearTimeout(searchTimeout);
    const query = this.value.trim();

    if (query.length === 0) {
      removeDropdown();
      // Se estiver na página de pesquisa, volta à página anterior ou home
      if (window.location.pathname === '/pesquisa') {
        const prev = document.referrer;
        window.location.href = (prev && new URL(prev).host === window.location.host) ? prev : '/';
      }
      return;
    }

    searchTimeout = setTimeout(() => doSearch(query), 200);
  });

  // Keyboard navigation
  searchInput.addEventListener('keydown', function (e) {
    if (!dropdown) {
      // No dropdown open yet — just let the user type, don't navigate on Enter
      return;
    }

    const rows = dropdown.querySelectorAll('a');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      currentFocus = Math.min(currentFocus + 1, rows.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      currentFocus = Math.max(currentFocus - 1, -1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (currentFocus >= 0 && rows[currentFocus]) {
        rows[currentFocus].click();
      }
      // If nothing focused, do nothing — user must pick from dropdown or click "Ver todos"
      return;
    } else if (e.key === 'Escape') {
      removeDropdown();
      return;
    }

    rows.forEach((r, i) => {
      r.style.background = i === currentFocus ? 'rgba(255,214,10,0.12)' : '';
      r.classList.toggle('focused', i === currentFocus);
    });
  });

  // Reposition on scroll/resize
  window.addEventListener('scroll', () => positionDropdown(), { passive: true });
  window.addEventListener('resize', () => positionDropdown(), { passive: true });

  // Click outside closes dropdown
  document.addEventListener('click', function (e) {
    if (!searchInput.contains(e.target) && (!dropdown || !dropdown.contains(e.target))) {
      removeDropdown();
    }
  });

  // Search icon click — focus the input so the user can type
  const searchIcon = document.querySelector('.search_icon') || document.getElementById('searchIcon');
  if (searchIcon) {
    searchIcon.addEventListener('click', function () {
      searchInput.focus();
      // If there's already a query, trigger search
      const q = searchInput.value.trim();
      if (q) doSearch(q);
    });
  }
});
