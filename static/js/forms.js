document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[required]").forEach(function (field) {
    field.addEventListener("input", function () {
      field.classList.toggle("is-invalid", !field.value.trim());
    });
  });

  // Для того чтобы в форме поля даты календарь при клике на сам блок открылся, а не значок календаря в поле - только блоки с датой
  document.addEventListener("click", function (e) {
    const el = e.target;
    if (el.matches('input[type="date"], input[type="datetime-local"]')) {
      if (el.showPicker) {
        try {
          el.showPicker();
        } catch (err) {
          console.warn('showPicker failed:', err);
        }
      }
    }
  });

 // Для скролла до задачи и ее подсветки
  if (window.location.hash && window.location.hash.indexOf('#task-') === 0) {
  const el = document.querySelector(window.location.hash);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.classList.add('task-card--highlighted');

    setTimeout(function () {
      el.classList.remove('task-card--highlighted');
    }, 2000);
  }
}
});
