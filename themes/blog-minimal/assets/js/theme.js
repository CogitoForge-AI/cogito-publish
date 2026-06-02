/*
 * blog-minimal color-scheme handling, adapted from hugo-coder (MIT); see
 * THEME-LICENSE. Vanilla JS, no dependencies. The compiled stylesheet keys dark
 * mode off the body `colorscheme-dark` / `colorscheme-auto` classes, so this
 * only resolves the initial scheme and wires the toggle.
 */
(function () {
  "use strict";
  var body = document.body;
  var media = window.matchMedia("(prefers-color-scheme: dark)");

  function setTheme(theme) {
    body.classList.remove("colorscheme-auto");
    body.classList.remove("colorscheme-" + (theme === "dark" ? "light" : "dark"));
    body.classList.add("colorscheme-" + theme);
    document.documentElement.style["color-scheme"] = theme;
  }

  // A saved choice wins; otherwise honor a server-pinned light/dark body class;
  // otherwise follow the OS preference (the "auto" case).
  var saved = localStorage.getItem("colorscheme");
  if (saved) {
    setTheme(saved);
  } else if (body.classList.contains("colorscheme-light") || body.classList.contains("colorscheme-dark")) {
    setTheme(body.classList.contains("colorscheme-dark") ? "dark" : "light");
  } else {
    setTheme(media.matches ? "dark" : "light");
  }

  if (document.currentScript.dataset.themeToggle === "true") {
    var toggle = document.getElementById("dark-mode-toggle");
    if (toggle) {
      toggle.addEventListener("click", function () {
        var next = body.classList.contains("colorscheme-dark") ? "light" : "dark";
        setTheme(next);
        localStorage.setItem("colorscheme", next);
      });
    }
  }

  // Drop the transition-suppression class once the page is ready, matching coder.
  document.addEventListener("DOMContentLoaded", function () {
    var node = document.querySelector(".preload-transitions");
    if (node) node.classList.remove("preload-transitions");
  });
})();
