document.addEventListener("click", function (e) {
  if (e.target.closest("[data-sidebar-toggle]")) document.body.classList.toggle("sidebar-open");
  if (e.target.closest("[data-sidebar-close]")) document.body.classList.remove("sidebar-open");
  const c = e.target.closest("[data-confirm]");
  if (c && !window.confirm(c.dataset.confirm)) e.preventDefault();
});
document.addEventListener("keydown", e => { if (e.key === "Escape") document.body.classList.remove("sidebar-open"); });
