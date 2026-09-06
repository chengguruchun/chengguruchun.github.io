(function () {
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  var hint = document.getElementById("search-hint");
  if (!input || !results) return;

  var base = document.body.getAttribute("data-base") || "";
  var indexUrl = base + "/content/index.json";
  var data = [];
  var tagFilter = null;

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function render(items) {
    if (!items.length) {
      results.innerHTML = '<p class="search-empty">没有匹配结果。试试「Agent」「控制面」「Kubernetes」等关键词。</p>';
      return;
    }
    results.innerHTML = items
      .map(function (item) {
        var tags = (item.tags || [])
          .map(function (t) {
            return '<span class="tag">' + escapeHtml(t) + "</span>";
          })
          .join("");
        return (
          '<article class="card search-card">' +
          '<a class="search-card__main" href="' +
          base +
          item.url +
          '">' +
          '<div class="card__meta"><span>' +
          escapeHtml(item.type) +
          "</span><span>" +
          escapeHtml(item.date || "") +
          "</span></div>" +
          '<h3 class="card__title">' +
          escapeHtml(item.title) +
          "</h3>" +
          '<p class="card__excerpt">' +
          escapeHtml(item.excerpt) +
          "</p>" +
          "</a>" +
          '<div class="card__tags">' +
          tags +
          "</div></article>"
        );
      })
      .join("");
  }

  function filter() {
    var q = (input.value || "").trim().toLowerCase();
    var params = new URLSearchParams(location.search);
    if (tagFilter === null && params.get("tag")) tagFilter = params.get("tag");

    var items = data.filter(function (item) {
      if (tagFilter && !(item.tags || []).includes(tagFilter)) return false;
      if (!q) return true;
      var hay = [item.title, item.excerpt, (item.tags || []).join(" "), item.type]
        .join(" ")
        .toLowerCase();
      return hay.indexOf(q) !== -1;
    });
    if (hint) {
      hint.textContent = tagFilter
        ? "标签筛选：" + tagFilter + " · " + items.length + " 条"
        : items.length + " 条结果" + (q ? " · 关键词「" + q + "」" : "");
    }
    render(items);
  }

  fetch(indexUrl)
    .then(function (r) {
      return r.json();
    })
    .then(function (json) {
      data = json.items || [];
      var params = new URLSearchParams(location.search);
      if (params.get("q")) input.value = params.get("q");
      if (params.get("tag")) tagFilter = params.get("tag");
      filter();
    })
    .catch(function () {
      results.innerHTML = '<p class="search-empty">无法加载索引。请确认 content/index.json 可访问。</p>';
    });

  input.addEventListener("input", filter);

  document.querySelectorAll("[data-tag-filter]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      tagFilter = btn.getAttribute("data-tag-filter") || null;
      if (tagFilter === "all") tagFilter = null;
      document.querySelectorAll("[data-tag-filter]").forEach(function (b) {
        b.classList.toggle("is-active", b === btn);
      });
      filter();
    });
  });
})();
