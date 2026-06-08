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
document.addEventListener("DOMContentLoaded", function () {
  var modal = document.querySelector("[data-delete-modal]");
  var modalForm = document.querySelector("[data-delete-modal-form]");
  var modalObject = document.querySelector("[data-delete-modal-object]");
  var openButtons = document.querySelectorAll("[data-delete-open]");
  var closeButtons = document.querySelectorAll("[data-delete-modal-close]");

  if (!modal || !modalForm || !modalObject) {
    return;
  }

  function openDeleteModal(title, url) {
    modalObject.textContent = title;
    modalForm.setAttribute("action", url);
    modal.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeDeleteModal() {
    modal.hidden = true;
    modalForm.removeAttribute("action");
    modalObject.textContent = "";
    document.body.style.overflow = "";
  }

  openButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var title = button.getAttribute("data-delete-title");
      var url = button.getAttribute("data-delete-url");

      openDeleteModal(title, url);
    });
  });

  closeButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      closeDeleteModal();
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !modal.hidden) {
      closeDeleteModal();
    }
  });
});