(function () {
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
  var themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) {
    var html = document.documentElement;

    function getTheme() {
      return html.getAttribute('data-theme') || 'light';
    }

    function updateBtn() {
      var dark = getTheme() === 'dark';
      themeBtn.textContent = dark ? '☀️' : '🌙';
      themeBtn.title = dark ? 'Passer en mode clair' : 'Passer en mode sombre';
    }

    themeBtn.addEventListener('click', function () {
      var newTheme = getTheme() === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateBtn();
    });

    // Suivre la préférence OS (seulement si pas de choix explicite)
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', function () {
      if (!localStorage.getItem('theme')) {
        html.setAttribute('data-theme', mq.matches ? 'dark' : 'light');
        updateBtn();
      }
    });

    updateBtn();
  }

  // ── Pied de page : année dynamique ───────────────────────────────────────
  var year = new Date().getFullYear();
  var footer = document.querySelector('footer');
  if (footer) {
    footer.textContent = 'Analyse quantitative en sciences humaines — Balthazar Charles, ' + year;
  }
})();
