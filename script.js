(function () {
  // ── Thème : lecture depuis l'URL, localStorage ou OS ─────────────────────
  var html = document.documentElement;
  var urlParams = new URLSearchParams(window.location.search);
  var themeFromUrl = urlParams.get('theme');
  var themeFromStorage = localStorage.getItem('theme');

  // Appliquer le thème : URL > localStorage > OS
  var initialTheme;
  if (themeFromUrl) {
    initialTheme = themeFromUrl;
  } else if (themeFromStorage) {
    initialTheme = themeFromStorage;
  } else {
    initialTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  html.setAttribute('data-theme', initialTheme);

  // ── Propager le thème dans l'URL (sans rechargement) ────────────────────
  function setUrlTheme(theme) {
    var url = new URL(window.location);
    if (theme === 'dark') {
      url.searchParams.set('theme', 'dark');
    } else {
      url.searchParams.set('theme', 'light');
    }
    window.history.replaceState({}, '', url);
  }

  // ── Intercepter les liens internes pour propager le thème ────────────────
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a');
    if (!link) return;
    var href = link.getAttribute('href');
    if (!href) return;
    // Ne pas intercepter les ancres internes (#...), les liens externes, ou vides
    if (href.startsWith('#') || href.startsWith('http') || href.startsWith('//') || href.startsWith('mailto:')) return;
    var currentTheme = html.getAttribute('data-theme') || 'light';
    var linkUrl = new URL(href, window.location.origin);
    linkUrl.searchParams.set('theme', currentTheme);
    // Sauvegarder aussi dans localStorage pour les pages qui n'auraient pas JS
    localStorage.setItem('theme', currentTheme);
    link.href = linkUrl.toString();
  });

  // ── Sidebar toggle (mobile) ───────────────────────────────────────────────
  var toggle = document.getElementById('sidebar-toggle');
  var sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    document.addEventListener('click', function (e) {
      if (!sidebar.contains(e.target) && e.target !== toggle) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Highlight de la section visible ──────────────────────────────────────
  var navItems = document.querySelectorAll('.nav-item[data-id]');
  if (navItems.length) {
    var headings = [];
    navItems.forEach(function (item) {
      var el = document.getElementById(item.dataset.id);
      if (el) headings.push({ el: el, nav: item });
    });

    function setActive(id) {
      navItems.forEach(function (n) { n.classList.remove('active'); });
      var found = Array.from(navItems).find(function(n){ return n.dataset.id === id; });
      if (found) {
        found.classList.add('active');
        found.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) setActive(entry.target.id);
      });
    }, { rootMargin: '-15% 0px -75% 0px', threshold: 0 });

    headings.forEach(function (h) { observer.observe(h.el); });

    navItems.forEach(function (item) {
      item.addEventListener('click', function () { setActive(item.dataset.id); });
    });
  }

  // ── Bouton mode sombre / clair ───────────────────────────────────────────
  var themeBtns = document.querySelectorAll('#theme-toggle, .theme-toggle');
  if (themeBtns.length) {
    function getTheme() {
      return html.getAttribute('data-theme') || 'light';
    }

    function updateBtns() {
      var dark = getTheme() === 'dark';
      themeBtns.forEach(function (btn) {
        btn.textContent = dark ? '☀️' : '🌙';
        btn.title = dark ? 'Passer en mode clair' : 'Passer en mode sombre';
      });
    }

    themeBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var newTheme = getTheme() === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        setUrlTheme(newTheme);
        updateBtns();
      });
    });

    // Suivre la préférence OS (seulement si pas de choix explicite)
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', function () {
      if (!localStorage.getItem('theme') && !urlParams.get('theme')) {
        html.setAttribute('data-theme', mq.matches ? 'dark' : 'light');
        updateBtns();
      }
    });

    updateBtns();
  }

  // ── Pied de page : année dynamique ───────────────────────────────────────
  var year = new Date().getFullYear();
  var footer = document.querySelector('footer');
  if (footer) {
    footer.textContent = 'Analyse quantitative en sciences humaines — Balthazar Charles, ' + year;
  }
})();
