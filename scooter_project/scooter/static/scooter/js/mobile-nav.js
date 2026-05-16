/**
 * Mobile navigation and user menu toggle
 * Handles responsive navigation menu with backdrop overlay
 */
(function () {
  const toggle = document.querySelector('[data-mobile-nav-toggle]');
  const userMenu = document.querySelector('[data-user-menu]');
  const desktopMedia = window.matchMedia('(min-width: 768px)');

  if (!toggle || !userMenu) {
    if (process.env.NODE_ENV === 'development') {
      console.warn('Mobile nav elements not found');
    }
    return;
  }

  function setUserMenu(open) {
    userMenu.classList.toggle('is-open', open);
    userMenu.setAttribute('aria-hidden', open ? 'false' : 'true');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close user menu' : 'Open user menu');
  }

  function closeUserMenu() {
    setUserMenu(false);
  }

  toggle.addEventListener('click', function () {
    const isOpen = userMenu.classList.contains('is-open');
    setUserMenu(!isOpen);
  });

  userMenu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      closeUserMenu();
    });
  });

  userMenu.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      closeUserMenu();
    });
  });

  document.addEventListener('click', function (event) {
    const clickedInside = userMenu.contains(event.target) || toggle.contains(event.target);
    if (!clickedInside) {
      closeUserMenu();
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && userMenu.classList.contains('is-open')) {
      closeUserMenu();
      toggle.focus();
    }
  });

  function handleResizeChange() {
    closeUserMenu();
  }

  // Modern addEventListener only (deprecated addListener removed)
  desktopMedia.addEventListener('change', handleResizeChange);

  closeUserMenu();
})();
