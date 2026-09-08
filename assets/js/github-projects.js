(function () {
  var researchRoot = document.getElementById("github-projects-research");
  var personalRoot = document.getElementById("github-projects-personal");
  if (!researchRoot && !personalRoot) return;

  var RESEARCH = [
    "TencentCloud/TencentDB-Agent-Memory",
    "cobusgreyling/loop-engineering",
    "deepseek-ai/deepseek-harness",
  ];
  var PERSONAL = ["chengguruchun/llm-trace-reuse"];

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

  function card(repo, kind) {
    var stars = repo.stargazers_count || 0;
    var desc = repo.description || "";
    var lang = repo.language
      ? '<span class="tag">' + escapeHtml(repo.language) + "</span>"
      : "";
    var updated = (repo.updated_at || "").slice(0, 10);
    var title =
      kind === "personal"
        ? repo.name || repo.full_name
        : repo.full_name || repo.name;
    var tag =
      kind === "personal"
        ? '<span class="tag">Personal</span>'
        : '<span class="tag">Research</span>';
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
      '<h3 class="card__title">' +
      escapeHtml(title) +
      "</h3>" +
      '<p class="card__excerpt">' +
      escapeHtml(desc) +
      "</p>" +
      '<div class="card__tags">' +
      lang +
      tag +
      "</div></a>"
    );
  }

  function render(el, repos, kind) {
    if (!el) return;
    if (!repos.length) {
      el.innerHTML = "";
      return;
    }
    el.innerHTML = repos.map(function (r) { return card(r, kind); }).join("");
  }

  function fetchRepo(full) {
    return fetch("https://api.github.com/repos/" + full, {
      headers: { Accept: "application/vnd.github+json" },
    }).then(function (r) {
      if (!r.ok) throw new Error(full + " " + r.status);
      return r.json();
    });
  }

  function loadResearch() {
    return Promise.all(RESEARCH.map(fetchRepo)).catch(function () {
      return stubs(RESEARCH);
    });
  }

  function stubs(fulls) {
    return fulls.map(function (full) {
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
  }

  function loadPersonal() {
    return Promise.all(PERSONAL.map(fetchRepo)).catch(function () {
      return stubs(PERSONAL);
    });
  }

  Promise.all([loadResearch(), loadPersonal()]).then(function (parts) {
    render(researchRoot, parts[0], "research");
    render(personalRoot, parts[1], "personal");
  });
})();
