(function () {
  var toggle = document.querySelector('[data-mobile-nav-toggle]');
  var menu = document.querySelector('[data-mobile-nav]');

  if (!toggle || !menu) {
    return;
  }

  function setState(open) {
    menu.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  toggle.addEventListener('click', function () {
    var isOpen = menu.classList.contains('is-open');
    setState(!isOpen);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      setState(false);
    }
  });
})();
