(function () {
  var root = document.querySelector("[data-comments]");
  if (!root) return;

  var repo = root.getAttribute("data-repo") || "chengguruchun/chengguruchun.github.io";
  var pageId = root.getAttribute("data-page-id") || "page";
  var pageUrl = root.getAttribute("data-page-url") || location.href;
  var listEl = root.querySelector("[data-comments-list]");
  var statusEl = root.querySelector("[data-comments-status]");
  var form = root.querySelector("[data-comments-form]");
  var nameInput = root.querySelector('[name="name"]');
  var bodyInput = root.querySelector('[name="body"]');

  var marker = "[lab-comment:" + pageId + "]";

  function setStatus(text) {
    if (statusEl) statusEl.textContent = text || "";
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function render(items) {
    if (!listEl) return;
    if (!items.length) {
      listEl.innerHTML = '<p class="comments__empty">还没有留言。</p>';
      return;
    }
    listEl.innerHTML = items.map(function (it) {
      var who = escapeHtml(it.user || "anonymous");
      var when = escapeHtml(it.created || "");
      var body = escapeHtml(it.body || "").replace(/\n/g, "<br>");
      var link = it.url
        ? '<a class="comments__issue" href="' + escapeHtml(it.url) + '" rel="noopener">#' + it.number + "</a>"
        : "";
      return (
        '<article class="comments__item">' +
        '<header class="comments__meta"><strong>' + who + "</strong><span>" + when + "</span>" + link + "</header>" +
        '<div class="comments__body">' + body + "</div>" +
        "</article>"
      );
    }).join("");
  }

  function parseIssue(issue) {
    var raw = issue.body || "";
    var lines = raw.split(/\r?\n/);
    var author = "";
    var contentLines = [];
    var skipMeta = true;
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (skipMeta) {
        if (/^Author:\s*/i.test(line)) {
          author = line.replace(/^Author:\s*/i, "").trim();
          continue;
        }
        if (/^Page:\s*/i.test(line)) continue;
        if (line.indexOf(marker) !== -1) continue;
        if (line.trim() === "" && contentLines.length === 0) continue;
        skipMeta = false;
      }
      contentLines.push(line);
    }
    var body = contentLines.join("\n").trim();
    return {
      number: issue.number,
      url: issue.html_url,
      user: author || (issue.user && issue.user.login) || "guest",
      created: (issue.created_at || "").slice(0, 10),
      body: body
    };
  }

  function load() {
    setStatus("加载中…");
    var q = encodeURIComponent('repo:' + repo + ' is:issue in:body "' + marker + '"');
    var url = "https://api.github.com/search/issues?q=" + q + "&sort=created&order=desc&per_page=30";
    fetch(url, {
      headers: { Accept: "application/vnd.github+json" }
    })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        var items = (data.items || []).map(parseIssue);
        render(items);
        setStatus(items.length ? ("共 " + items.length + " 条") : "");
      })
      .catch(function () {
        render([]);
        setStatus("暂时无法从 GitHub 拉取留言。仍可通过下方表单提交。");
      });
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = (nameInput && nameInput.value.trim()) || "guest";
      var body = (bodyInput && bodyInput.value.trim()) || "";
      if (!body) {
        setStatus("先写一点内容再提交。");
        return;
      }
      var title = "[comment] " + pageId + " · " + body.slice(0, 40).replace(/\s+/g, " ");
      var issueBody =
        marker + "\n" +
        "Page: " + pageUrl + "\n" +
        "Author: " + name + "\n\n" +
        body;
      var href =
        "https://github.com/" + repo + "/issues/new?title=" +
        encodeURIComponent(title) +
        "&body=" +
        encodeURIComponent(issueBody);
      window.open(href, "_blank", "noopener");
      setStatus("已打开 GitHub 创建留言 Issue，登录后提交即可。");
    });
  }

  load();
})();
