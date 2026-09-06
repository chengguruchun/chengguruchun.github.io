(function () {
  var root = document.getElementById("github-projects");
  var statusEl = document.getElementById("github-projects-status");
  if (!root) return;

  var USER = "chengguruchun";
  var LIMIT = 3;
  var url =
    "https://api.github.com/users/" +
    USER +
    "/repos?per_page=100&sort=updated&type=owner";

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function isPersonalProject(repo) {
    if (!repo || repo.fork) return false;
    if (repo.archived) return false;
    var name = String(repo.name || "");
    if (/\.github\.io$/i.test(name)) return false;
    return true;
  }

  function render(repos) {
    if (!repos.length) {
      root.innerHTML =
        '<p class="search-empty">暂时没有可展示的个人仓库。</p>';
      return;
    }
    root.innerHTML = repos
      .map(function (repo) {
        var stars = repo.stargazers_count || 0;
        var desc = repo.description || "个人项目";
        var lang = repo.language ? '<span class="tag">' + escapeHtml(repo.language) + "</span>" : "";
        var updated = (repo.updated_at || "").slice(0, 10);
        return (
          '<a class="card project-card" href="' +
          escapeHtml(repo.html_url) +
          '" rel="noopener" target="_blank">' +
          '<div class="project-card__stars" aria-label="' +
          stars +
          ' stars">' +
          '<span class="project-card__star" aria-hidden="true">★</span>' +
          '<span class="project-card__star-count">' +
          stars +
          "</span>" +
          "</div>" +
          '<div class="card__meta"><span>GitHub</span><span>' +
          escapeHtml(updated) +
          "</span></div>" +
          '<h2 class="card__title">' +
          escapeHtml(repo.name) +
          "</h2>" +
          '<p class="card__excerpt">' +
          escapeHtml(desc) +
          "</p>" +
          '<div class="card__tags">' +
          lang +
          '<span class="tag">Personal</span></div>' +
          "</a>"
        );
      })
      .join("");
  }

  if (statusEl) statusEl.textContent = "加载 GitHub 个人项目…";

  fetch(url, {
    headers: { Accept: "application/vnd.github+json" },
  })
    .then(function (r) {
      if (!r.ok) throw new Error("GitHub API " + r.status);
      return r.json();
    })
    .then(function (list) {
      var repos = (list || []).filter(isPersonalProject).slice(0, LIMIT);
      if (statusEl) {
        statusEl.textContent =
          "按最近更新 · 个人仓库 Top " + repos.length;
      }
      render(repos);
    })
    .catch(function () {
      if (statusEl) statusEl.textContent = "无法从 GitHub 加载项目列表。";
      root.innerHTML =
        '<p class="search-empty">GitHub API 暂时不可用。可直接打开 <a href="https://github.com/' +
        USER +
        '" rel="noopener">github.com/' +
        USER +
        "</a>。</p>";
    });
})();
