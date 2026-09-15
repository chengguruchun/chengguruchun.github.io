(function () {
  var bars = document.querySelectorAll("[role=toolbar]");
  if (!bars.length) return;

  function parsePublishedDate(card) {
    var meta = card.querySelector(".card__meta span");
    if (!meta) return 0;
    var match = (meta.textContent || "").match(/发表\s+(\d{4}-\d{2}-\d{2})/);
    if (!match) return 0;
    var stamp = Date.parse(match[1] + "T00:00:00");
    return isNaN(stamp) ? 0 : stamp;
  }

  function sortCardsByPublishedDate() {
    document.querySelectorAll(".grid.grid--2").forEach(function (grid) {
      var cards = Array.prototype.slice.call(grid.querySelectorAll(":scope > .card"));
      if (cards.length < 2) return;
      cards.sort(function (a, b) {
        return parsePublishedDate(b) - parsePublishedDate(a);
      });
      cards.forEach(function (card) {
        grid.appendChild(card);
      });
    });
  }

  function apply() {
    sortCardsByPublishedDate();

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
  apply();
})();
