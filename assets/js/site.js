(function () {
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var path = location.pathname.replace(/\/$/, "") || "/";
  document.querySelectorAll(".nav a[href]").forEach(function (a) {
    var href = a.getAttribute("href");
    if (!href || href.startsWith("http") || href.startsWith("mailto")) return;
    var clean = href.replace(/\/$/, "") || "/";
    // Normalize for GitHub Pages project/user site paths
    var full = a.pathname.replace(/\/$/, "") || "/";
    if (full === path || (path.endsWith(clean) && clean !== "/")) {
      a.setAttribute("aria-current", "page");
    }
  });


  var brand = document.querySelector("[data-brand-rotate]");
  if (brand && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var items = Array.prototype.slice.call(brand.querySelectorAll(".brand__item"));
    var i = 0;
    setInterval(function () {
      var cur = items[i];
      var next = items[(i + 1) % items.length];
      cur.classList.remove("is-active");
      cur.classList.add("is-exit");
      next.classList.add("is-active");
      setTimeout(function () { cur.classList.remove("is-exit"); }, 450);
      i = (i + 1) % items.length;
    }, 2400);
  }

  var y = document.getElementById("year");
  if (y) y.textContent = String(new Date().getFullYear());
})();
