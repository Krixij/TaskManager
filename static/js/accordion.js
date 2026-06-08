document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-toggle-section]").forEach(function (button) {
    button.addEventListener("click", function () {
      var section = document.querySelector('[data-task-section="' + button.dataset.toggleSection + '"]');

      if (!section) return;

      var isCollapsed = section.classList.toggle("is-collapsed");
      var isExpanded = !isCollapsed;

      button.classList.toggle("is-expanded", isExpanded);
      button.setAttribute("aria-expanded", String(isExpanded));
      button.setAttribute("aria-label", isExpanded ? "Скрыть задачи раздела" : "Показать задачи раздела");
    });
  });

  document.querySelectorAll("[data-toggle-task]").forEach(function (button) {
    button.addEventListener("click", function () {
      var card = document.querySelector('[data-task-card="' + button.dataset.toggleTask + '"]');

      if (!card) return;

      var isExpanded = card.classList.toggle("is-expanded");

      card.classList.toggle("is-collapsed", !isExpanded);
      button.classList.toggle("is-expanded", isExpanded);
      button.setAttribute("aria-expanded", String(isExpanded));
      button.setAttribute("aria-label", isExpanded ? "Скрыть описание задачи" : "Показать описание задачи");
    });
  });
});