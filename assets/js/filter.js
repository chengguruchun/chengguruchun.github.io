(function () {
  var bars = document.querySelectorAll("[role=toolbar]");
  if (!bars.length) return;

  function apply() {
    var needed = [];
    bars.forEach(function (bar) {
      var btn = bar.querySelector(".filter-btn.is-active, [data-filter].is-active");
      var f = btn && btn.getAttribute("data-filter");
      if (f && f !== "all") needed.push(f);
    });
    document.querySelectorAll("[data-tags]").forEach(function (card) {
      var tags = (card.getAttribute("data-tags") || "").split(/\s+/);
      var stage = card.getAttribute("data-stage") || "";
      var route = card.getAttribute("data-route") || "";
      var show = needed.every(function (f) {
        return tags.indexOf(f) !== -1 || stage === f || route === f;
      });
      card.style.display = show ? "" : "none";
    });
  }

  bars.forEach(function (bar) {
    var buttons = bar.querySelectorAll("[data-filter]");
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) {
          b.classList.toggle("is-active", b === btn);
        });
        apply();
      });
    });
  });

  document.addEventListener("thoughts:loaded", apply);
})();
