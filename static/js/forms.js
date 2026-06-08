document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[required]").forEach(function (field) {
    field.addEventListener("input", function () {
      field.classList.toggle("is-invalid", !field.value.trim());
    });
  });
});