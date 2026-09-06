(function () {
  var buttons = document.querySelectorAll("[data-filter]");
  var cards = document.querySelectorAll("[data-tags]");
  if (!buttons.length || !cards.length) return;

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var f = btn.getAttribute("data-filter");
      buttons.forEach(function (b) {
        b.classList.toggle("is-active", b === btn);
      });
      cards.forEach(function (card) {
        var tags = (card.getAttribute("data-tags") || "").split(/\s+/);
        var show = f === "all" || tags.indexOf(f) !== -1;
        card.style.display = show ? "" : "none";
      });
    });
  });
})();
