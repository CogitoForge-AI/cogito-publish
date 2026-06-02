/*
 * docs-technical theme behaviour: light/dark toggle and the mobile sidebar
 * drawer. Vanilla JS, no dependencies. The pre-paint script in <head> sets the
 * initial `data-theme`; this only wires the controls.
 */
(function () {
  "use strict";

  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var el = document.documentElement;
      var next = el.dataset.theme === "dark" ? "light" : "dark";
      el.dataset.theme = next;
      localStorage.setItem("pref-theme", next);
    });
  }

  var sidebarToggle = document.querySelector(".td-sidebar-toggle");
  var sidebar = document.querySelector(".td-sidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function () {
      var open = sidebar.classList.toggle("open");
      sidebarToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
})();
