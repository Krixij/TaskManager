document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function () {
      var btn = form.querySelector('button[type="submit"]');

      if (btn) {
        btn.classList.add("is-loading");
      }
    });
  });
});