(function () {
  var forms = document.querySelectorAll('form[data-confirm]');
  forms.forEach(function (form) {
    form.addEventListener('submit', function (event) {
      var message = form.getAttribute('data-confirm') || '确认继续操作吗？';
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });

  var actionButtons = document.querySelectorAll('.btn');
  actionButtons.forEach(function (button) {
    button.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        button.classList.add('is-key-active');
      }
    });
    button.addEventListener('keyup', function () {
      button.classList.remove('is-key-active');
    });
  });
})();
