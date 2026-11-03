document.addEventListener("submit", function (event) {
  const form = event.target.closest("form[data-confirm]");
  if (form && !window.confirm(form.dataset.confirm || "Are you sure?")) {
    event.preventDefault();
  }
});
