(function () {
  var root = document.querySelector("[data-times-vote]");
  var article = document.querySelector(".times-period[data-period]");
  if (!root || !article) return;

  var period = article.getAttribute("data-period");
  var key = "lab-hotwords-vote:" + period;
  var likeBtn = root.querySelector('[data-vote="like"]');
  var dislikeBtn = root.querySelector('[data-vote="dislike"]');
  var hint = root.querySelector("[data-vote-hint]");

  function read() {
    try {
      return localStorage.getItem(key) || "";
    } catch (e) {
      return "";
    }
  }

  function write(v) {
    try {
      if (!v) localStorage.removeItem(key);
      else localStorage.setItem(key, v);
    } catch (e) {}
  }

  function paint(v) {
    var likeOn = v === "like";
    var dislikeOn = v === "dislike";
    likeBtn.classList.toggle("is-active", likeOn);
    dislikeBtn.classList.toggle("is-active", dislikeOn);
    likeBtn.setAttribute("aria-pressed", likeOn ? "true" : "false");
    dislikeBtn.setAttribute("aria-pressed", dislikeOn ? "true" : "false");
    if (hint) {
      if (likeOn) hint.textContent = "Liked";
      else if (dislikeOn) hint.textContent = "Disliked";
      else hint.textContent = "";
    }
  }

  function onVote(next) {
    var cur = read();
    var v = cur === next ? "" : next;
    write(v);
    paint(v);
  }

  likeBtn.addEventListener("click", function () { onVote("like"); });
  dislikeBtn.addEventListener("click", function () { onVote("dislike"); });
  paint(read());
})();
