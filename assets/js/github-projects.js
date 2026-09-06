(function () {
  var root = document.getElementById("github-projects");
  var statusEl = document.getElementById("github-projects-status");
  if (!root) return;

  // Curated non-personal projects (starred / watching)
  var REPOS = [
    "TencentCloud/TencentDB-Agent-Memory",
    "cobusgreyling/loop-engineering",
    "deepseek-ai/deepseek-harness",
  ];

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatStars(n) {
    n = Number(n) || 0;
    if (n >= 1000) {
      var k = n / 1000;
      return (k >= 100 ? Math.round(k) : Math.round(k * 10) / 10) + "k";
    }
    return String(n);
  }

  function card(repo) {
    var stars = repo.stargazers_count || 0;
    var desc = repo.description || "";
    var lang = repo.language
      ? '<span class="tag">' + escapeHtml(repo.language) + "</span>"
      : "";
    var updated = (repo.updated_at || "").slice(0, 10);
    var full = repo.full_name || repo.name;
    return (
      '<a class="card project-card" href="' +
      escapeHtml(repo.html_url) +
      '" rel="noopener" target="_blank">' +
      '<div class="project-card__stars" aria-label="' +
      stars +
      ' stars">' +
      '<span class="project-card__star" aria-hidden="true">★</span>' +
      '<span class="project-card__star-count">' +
      escapeHtml(formatStars(stars)) +
      "</span>" +
      "</div>" +
      '<div class="card__meta"><span>GitHub</span><span>' +
      escapeHtml(updated) +
      "</span></div>" +
      '<h2 class="card__title">' +
      escapeHtml(full) +
      "</h2>" +
      '<p class="card__excerpt">' +
      escapeHtml(desc) +
      "</p>" +
      '<div class="card__tags">' +
      lang +
      '<span class="tag">Starred</span></div>' +
      "</a>"
    );
  }

  function render(repos) {
    root.innerHTML = repos.map(card).join("");
  }

  if (statusEl) statusEl.textContent = "加载 star 与仓库信息…";

  Promise.all(
    REPOS.map(function (full) {
      return fetch("https://api.github.com/repos/" + full, {
        headers: { Accept: "application/vnd.github+json" },
      }).then(function (r) {
        if (!r.ok) throw new Error(full + " " + r.status);
        return r.json();
      });
    })
  )
    .then(function (repos) {
      if (statusEl) {
        statusEl.textContent = "关注的非个人项目 · " + repos.length + " 个";
      }
      render(repos);
    })
    .catch(function () {
      // Fallback: still show links without live stars
      var fallback = REPOS.map(function (full) {
        return {
          full_name: full,
          name: full.split("/")[1],
          html_url: "https://github.com/" + full,
          description: "",
          stargazers_count: 0,
          updated_at: "",
          language: null,
        };
      });
      if (statusEl) statusEl.textContent = "GitHub API 暂不可用，已显示仓库链接。";
      render(fallback);
    });
})();
