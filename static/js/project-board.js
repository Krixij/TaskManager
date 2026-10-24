document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-project-task-toggle]').forEach(function (button) {
    button.addEventListener('click', function () {
      var details = document.getElementById(button.getAttribute('aria-controls'));
      if (!details) return;
      var opening = details.hidden;
      details.hidden = !opening;
      button.setAttribute('aria-expanded', String(opening));
      button.setAttribute('aria-label', (opening ? 'Скрыть' : 'Показать') + ' подробности задачи');
      button.closest('[data-project-task]').classList.toggle('is-expanded', opening);
    });
  });
  if (location.hash && /^#task-\d+$/.test(location.hash)) {
    var card = document.getElementById(location.hash.slice(1));
    if (card) {
      card.scrollIntoView({block: 'center'});
      card.classList.add('project-task--highlighted');
    }
  }
});
