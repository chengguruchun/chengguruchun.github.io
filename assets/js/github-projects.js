(function () {
  var researchRoot = document.getElementById("github-projects-research");
  var personalRoot = document.getElementById("github-projects-personal");
  var skillsRoot = document.getElementById("github-projects-skills");
  if (!researchRoot && !personalRoot && !skillsRoot) return;

  var RESEARCH = ["TencentCloud/TencentDB-Agent-Memory", "cobusgreyling/loop-engineering", "deepseek-ai/deepseek-harness"];
  var PERSONAL = ["chengguruchun/llm-trace-reuse", "chengguruchun/SecondKill"];
  var SKILLS = ["chengguruchun/idealagent"];

  function escapeHtml(s) { return String(s == null ? "" : s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
  function card(repo, kind) {
    var lang = repo.language ? '<span class="tag">' + escapeHtml(repo.language) + '</span>' : '';
    var tag = kind === "skill" ? "Personal Skill" : kind === "personal" ? "Personal" : "Research";
    return '<a class="card project-card" href="' + escapeHtml(repo.html_url) + '" rel="noopener" target="_blank">' +
      '<div class="project-card__stars"><span class="project-card__star" aria-hidden="true">★</span><span class="project-card__star-count">' + (Number(repo.stargazers_count) || 0) + '</span></div>' +
      '<div class="card__meta"><span>GitHub</span><span>' + escapeHtml((repo.updated_at || "").slice(0,10)) + '</span></div>' +
      '<h3 class="card__title">' + escapeHtml(repo.name || repo.full_name) + '</h3>' +
      '<p class="card__excerpt">' + escapeHtml(repo.description || "") + '</p>' +
      '<div class="card__tags">' + lang + '<span class="tag">' + tag + '</span></div></a>';
  }
  function stubs(fulls) { return fulls.map(function(full) { return {full_name:full,name:full.split("/")[1],html_url:"https://github.com/"+full,description:"",stargazers_count:0,updated_at:"",language:null}; }); }
  function load(fulls) { return Promise.all(fulls.map(function(full) { return fetch("https://api.github.com/repos/"+full,{headers:{Accept:"application/vnd.github+json"}}).then(function(r){if(!r.ok) throw new Error(full); return r.json();}); })).catch(function(){ return stubs(fulls); }); }
  function render(root, repos, kind) { if (root) root.innerHTML = repos.map(function(r){return card(r,kind);}).join(""); }
  Promise.all([load(RESEARCH),load(PERSONAL),load(SKILLS)]).then(function(parts){ render(researchRoot,parts[0],"research"); render(personalRoot,parts[1],"personal"); render(skillsRoot,parts[2],"skill"); });
})();