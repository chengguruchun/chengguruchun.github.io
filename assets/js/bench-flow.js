(function () {
  var el = document.getElementById("bench-flow");
  if (!el) return;
  var STOPS = [
    { id: "chat", name: "Chat", zh: "站外蒸馏，原文不进站" },
    { id: "topic", name: "Topic", zh: "入境。还不是结论" },
    { id: "candidate", name: "Candidate", zh: "开始验证" },
    { id: "validated", name: "Validated", zh: "过证据，已定去向" },
    { id: "published", name: "Published", zh: "才算发表" }
  ];
  var DOORS = [
    { id: "diverse", name: "Diverse Lab", href: "../diverse/" },
    { id: "articles", name: "Articles", href: "../articles/" },
    { id: "videos", name: "Videos", href: "../videos/" },
    { id: "projects", name: "Projects", href: "../projects/" }
  ];
  var viewAt = 0, liveAt = 1, items = [], item = null, meta = {};
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
  function stageAt(stage) { if (stage === "published") return 4; if (stage === "validated" || stage === "article_candidate") return 3; if (stage === "candidate") return 2; if (stage === "topic") return 1; return 0; }
  function fieldOf(it, key) { var gs = window.LabBench && window.LabBench.gates ? window.LabBench.gates(it) : []; return gs.filter(function (g) { return g.key === key; })[0] || { key: key, name: key, pass: false }; }
  function modelOf(it, key) { var gs = window.LabBench && window.LabBench.modelGates ? window.LabBench.modelGates(it) : []; return gs.filter(function (g) { return g.key === key; })[0] || { key: key, name: key, pass: false, status: "pending" }; }
  function knowledgeOf(it) { var k = it && it.knowledge ? it.knowledge : {}; return { type: k.type || "UNDECLARED", confidence: k.confidence || "UNDECLARED", evidence: k.evidence_level || "UNDECLARED" }; }
  function qualityOf(it) { var q = it && it.quality ? it.quality : {}; return [
    { key: "fact_check", name: "Fact Check", status: q.fact_check || "pending" },
    { key: "inference_check", name: "Inference Check", status: q.inference_check || "pending" },
    { key: "evidence_check", name: "Evidence Check", status: q.evidence_check || "pending" },
    { key: "counterexample_check", name: "Counterexample Check", status: q.counterexample_check || "pending" }
  ]; }
  function qualityPill(q) { var status = q.status || "pending"; var label = (status === "passed" || status === "pass") ? "PASS" : status === "failed" ? "FAIL" : "待判"; return '<span class="bench-lamp bench-lamp--' + esc(status) + '" title="' + esc(q.name) + '"><i></i>' + esc(q.name) + " <em>" + label + "</em></span>"; }
  function whyBlocked(it, want) {
    if (want <= liveAt) return "";
    if (want >= 2 && (!fieldOf(it, "origin").pass || !fieldOf(it, "contribution").pass)) return "Origin / Contribution 还没过。出不了 Topic。";
    if (want >= 3 && !fieldOf(it, "evidence").pass) return "Evidence 还是空的。字段都没过，更别提模型判「证据真相关」。";
    if (want >= 3) { var ev = modelOf(it, "evidence_real"); if (ev.status !== "pass") return "模型门禁还没判，或没过。字段非空不等于证据真相关。"; }
    if (want >= 4 && !fieldOf(it, "route").pass) return "没有 route。未分流的句子不会进右边栏目。";
    if (want >= 4 && !fieldOf(it, "published").pass) return "还不是 published。过门之前不当结论。";
    return "还停在这一档。往前走要过门，不是点一下。";
  }
  function lamp(g) { var status = g.status || (g.pass ? "pass" : "unpass"); var word = status === "pending" ? "待判" : status === "stale" ? "过期" : g.pass ? "PASS" : "UNPASS"; return '<span class="bench-lamp bench-lamp--' + esc(status) + '" title="' + esc(g.note || g.name) + '"><i></i>' + esc(g.name || g.key) + " <em>" + word + "</em></span>"; }
  function setToken(at) {
    viewAt = at; el.style.setProperty("--at", String(at / (STOPS.length - 1)));
    el.querySelectorAll("[data-stop]").forEach(function (btn) { var i = Number(btn.getAttribute("data-stop")); btn.classList.toggle("is-here", i === at); btn.classList.toggle("is-past", i < liveAt); btn.classList.toggle("is-live", i === liveAt); btn.classList.toggle("is-ahead", i > liveAt); });
    var note = el.querySelector("[data-why]");
    if (!note) return;
    var blocked = item ? whyBlocked(item, at) : "";
    if (at > liveAt && blocked) { note.textContent = blocked; note.hidden = false; el.classList.add("is-blocked"); }
    else if (at === liveAt && item && (item.status === "hold" || !item.route)) { note.textContent = "停在 " + STOPS[liveAt].name + " 是刻意的。没过门就不会进右边栏目。"; note.hidden = false; el.classList.remove("is-blocked"); }
    else { note.textContent = STOPS[at] ? STOPS[at].zh : ""; note.hidden = false; el.classList.remove("is-blocked"); }
  }
  function go(want) { if (!item) return; if (want > liveAt) { setToken(want); el.classList.remove("is-shake"); void el.offsetWidth; el.classList.add("is-shake"); window.setTimeout(function () { el.classList.remove("is-shake"); setToken(liveAt); }, reduce ? 0 : 720); return; } setToken(want); }
  function playIn() { if (reduce) { setToken(liveAt); return; } setToken(0); window.setTimeout(function () { setToken(liveAt); }, 520); }
  var detailCache = {};
  var detailRequest = 0;
  function listHtml(values) {
    if (!Array.isArray(values) || !values.length) return '<p class="bench-detail__empty">暂未记录</p>';
    return '<ul>' + values.map(function (v) {
      var value = typeof v === "string" ? v : (v && (v.detail || v.name || v.title || v.question || v.summary)) || JSON.stringify(v);
      return '<li>' + esc(value) + '</li>';
    }).join("") + '</ul>';
  }
  function detailSection(title, body, extra) {
    if (!body) return "";
    return '<section class="bench-detail__section' + (extra ? " " + extra : "") + '"><h4>' + esc(title) + '</h4>' + body + '</section>';
  }
  function renderTopicDetails(data) {
    var context = data.context || {};
    var thesis = data.thesis || {};
    var evolution = data.evolution || {};
    var directions = Array.isArray(evolution.directions) ? evolution.directions : [];
    var progress = Array.isArray(data.progress_log) ? data.progress_log : [];
    var directionHtml = directions.length ? '<div class="bench-detail__directions">' + directions.map(function (d) {
      return '<article class="bench-detail__direction"><h5>' + esc(d.title || d.id) + '</h5>' +
        (d.question ? '<p><strong>研究问题：</strong>' + esc(d.question) + '</p>' : '') +
        (d.explore && d.explore.length ? '<div><strong>可以继续：</strong>' + listHtml(d.explore) + '</div>' : '') +
        (d.expected_output ? '<p class="bench-detail__output"><strong>预期产物：</strong>' + esc(d.expected_output) + '</p>' : '') +
      '</article>';
    }).join("") + '</div>' : '<p class="bench-detail__empty">尚未规划演进方向</p>';
    var progressHtml = progress.length ? '<ol class="bench-detail__history">' + progress.slice().reverse().map(function (p) {
      return '<li><time>' + esc(p.date || "") + '</time><strong>' + esc(p.summary || p.type || "推进记录") + '</strong>' +
        (p.changes && p.changes.length ? listHtml(p.changes) : '') +
        (p.next ? '<p><strong>下一步：</strong>' + esc(p.next) + '</p>' : '') +
      '</li>';
    }).join("") + '</ol>' : '<p class="bench-detail__empty">还没有推进记录；后续每次讨论可以追加到这里。</p>';
    var html = '<section class="bench-detail" aria-label="Topic 研究档案">' +
      '<div class="bench-detail__head"><div><p class="bench-detail__eyebrow">TOPIC NOTEBOOK</p><h3>研究档案</h3></div><span class="bench-detail__status">' + esc(data.status || item.status || "hold") + ' · ' + esc((data.knowledge && data.knowledge.confidence) || "LOW") + '</span></div>' +
      '<div class="bench-detail__grid">' +
        detailSection("01 · 背景与来源", (context.trigger ? '<p>' + esc(context.trigger) + '</p>' : '') +
          (context.original_observation ? '<p>' + esc(context.original_observation) + '</p>' : '') +
          (context.problem_space ? '<p><strong>研究范围：</strong>' + esc(context.problem_space) + '</p>' : '') +
          (context.why_it_matters ? '<div><strong>为什么值得研究</strong>' + listHtml(context.why_it_matters) + '</div>' : '') +
          (context.prior_discussion ? '<div><strong>已有讨论</strong>' + listHtml(context.prior_discussion) + '</div>' : '') +
          (context.assumptions_to_test ? '<div><strong>待验证假设</strong>' + listHtml(context.assumptions_to_test) + '</div>' : '') +
          (!context.trigger && !context.original_observation && !context.problem_space ? '<p class="bench-detail__empty">尚无背景记录</p>' : '')) +
        detailSection("02 · 当前认知", (thesis.core ? '<p>' + esc(thesis.core) + '</p>' : '') +
          (thesis.reframing ? '<p><strong>重新表述：</strong>' + esc(thesis.reframing) + '</p>' : '') +
          (thesis.key_question ? '<p class="bench-detail__question"><strong>核心问题：</strong>' + esc(thesis.key_question) + '</p>' : '') +
          (data.mechanisms && data.mechanisms.length ? '<div><strong>作用机制</strong>' + listHtml(data.mechanisms) + '</div>' : '') +
          (data.critiques && data.critiques.length ? '<div><strong>反例与风险</strong>' + listHtml(data.critiques) + '</div>' : '') +
          (!thesis.core && !thesis.reframing && !thesis.key_question ? '<p class="bench-detail__empty">尚无当前认知记录</p>' : '')) +
      '</div>' +
      detailSection("03 · 后续演进方向", directionHtml) +
      '<div class="bench-detail__grid">' +
        detailSection("04 · 开放问题", listHtml(evolution.open_questions || [])) +
        detailSection("05 · 下一步行动", listHtml(evolution.next_actions || [])) +
        detailSection("06 · 重新审视的触发条件", listHtml(evolution.revisit_triggers || [])) +
      '</div>' +
      (data.experiments && data.experiments.length ? detailSection("可验证的实验", listHtml(data.experiments)) : '') +
      (data.evidence && data.evidence.length ? detailSection("证据记录", listHtml(data.evidence)) : '') +
      detailSection("07 · 推进历史", progressHtml) +
      '</section>';
    return html;
  }
  function loadTopicDetails(target) {
    if (!target) return;
    var id = target.id || "";
    var panel = el.querySelector("[data-topic-details]");
    if (!panel) return;
    if (detailCache[id]) { panel.innerHTML = renderTopicDetails(detailCache[id]); return; }
    if (!target.content) {
      panel.innerHTML = '<section class="bench-detail"><p class="bench-detail__empty">该条目尚未关联独立研究档案。</p></section>';
      return;
    }
    var requestId = ++detailRequest;
    panel.innerHTML = '<section class="bench-detail"><p class="bench-detail__loading">正在载入研究档案…</p></section>';
    fetch(target.content, { headers: { Accept: "application/json" } })
      .then(function (response) { if (!response.ok) throw new Error(String(response.status)); return response.json(); })
      .then(function (data) {
        if (requestId !== detailRequest || !item || item.id !== id) return;
        detailCache[id] = data;
        panel.innerHTML = renderTopicDetails(data);
      })
      .catch(function () {
        if (requestId !== detailRequest || !item || item.id !== id) return;
        panel.innerHTML = '<section class="bench-detail"><p class="bench-detail__empty">研究档案暂时无法载入。请稍后重试。</p><button type="button" class="bench-detail__retry" data-retry-detail>重新载入</button></section>';
        var retry = panel.querySelector("[data-retry-detail]");
        if (retry) retry.addEventListener("click", function () { loadTopicDetails(target); });
      });
  }
  function render() {
    if (!item) { el.innerHTML = '<p class="bench-stage__empty">Bench 上空着。先蒸馏一句，再入境。</p>'; return; }
    liveAt = stageAt(item.stage); var v = meta.criteria_version || "—"; var k = knowledgeOf(item); var quality = qualityOf(item);
    var doors = DOORS.map(function (d) { var open = item.route === d.id || (item.also && item.also.indexOf(d.id) !== -1); return '<a class="bench-door' + (open ? " is-open" : " is-locked") + '" href="' + d.href + '"><strong>' + d.name + '</strong><span>' + (open ? "已定去向" : "未开门") + "</span></a>"; }).join("");
    var queue = "";
    if (items.length > 1) queue = '<div class="bench-queue" role="tablist" aria-label="台上的句子">' + items.map(function (it, i) { return '<button type="button" role="tab" class="bench-queue__item' + (it === item ? " is-on" : "") + '" data-pick="' + i + '"><span class="bench-queue__stage">' + esc(it.stage || "topic") + "</span>" + esc(it.thought) + "</button>"; }).join("") + "</div>";
    el.innerHTML = queue + '<p class="bench-stage__kicker">思想实验台 · ' + esc(item.stage) + " · " + esc(item.origin || "") + (item.contribution ? " · " + esc(item.contribution) : "") + "</p>" +
      '<blockquote class="bench-line">' + esc(item.thought) + "</blockquote>" +
      (item.critiques && item.critiques[0] ? '<p class="bench-line__aside">' + esc(item.critiques[0]) + "</p>" : "") +
      '<div class="bench-knowledge-meta" aria-label="Knowledge metadata"><span><b>Type</b> ' + esc(k.type) + '</span><span><b>Confidence</b> ' + esc(k.confidence) + '</span><span><b>Evidence</b> ' + esc(k.evidence) + '</span></div>' +
      '<div class="bench-rail" aria-label="Thought 走轨"><div class="bench-rail__glow" aria-hidden="true"></div><div class="bench-rail__line" aria-hidden="true"></div><div class="bench-rail__spark" aria-hidden="true"></div><div class="bench-rail__token" aria-hidden="true"><span></span></div><div class="bench-rail__stops">' + STOPS.map(function (s, i) { return '<button type="button" class="bench-stop" data-stop="' + i + '"><b>' + esc(s.name) + '</b><small>' + esc(s.zh) + '</small></button>'; }).join("") + "</div></div>" +
      '<p class="bench-stage__why" data-why></p>' +
      '<div class="bench-lamps"><div><span class="bench-lamps__k">字段</span>' + lamp(fieldOf(item, "origin")) + lamp(fieldOf(item, "contribution")) + lamp(fieldOf(item, "evidence")) + lamp(fieldOf(item, "route")) + '</div><div><span class="bench-lamps__k">模型 v' + esc(v) + '</span>' + lamp(modelOf(item, "sharp")) + lamp(modelOf(item, "evidence_real")) + lamp(modelOf(item, "route_fit")) + '</div><div><span class="bench-lamps__k">知识质量</span>' + quality.map(qualityPill).join("") + '</div></div>' +
      '<div class="bench-doors" aria-label="过门之后">' + doors + '<span class="bench-door bench-door--hold is-locked"><strong>Hold</strong><span>没过门，停在这里</span></span></div>' +
      '<div class="bench-stage__acts"><button type="button" class="bench-replay" data-replay>再走一遍</button><a href="../api/thoughts-criteria.json">标准提示词</a><a href="../THOUGHT_LOOP.md">过程说明</a></div>' + '<div data-topic-details></div>';
    el.querySelectorAll("[data-pick]").forEach(function (btn) { btn.addEventListener("click", function () { item = items[Number(btn.getAttribute("data-pick"))] || item; render(); }); });
    el.querySelectorAll("[data-stop]").forEach(function (btn) { btn.addEventListener("click", function () { go(Number(btn.getAttribute("data-stop"))); }); });
    var replay = el.querySelector("[data-replay]"); if (replay) replay.addEventListener("click", function () { playIn(); }); loadTopicDetails(item); playIn();
  }
  document.addEventListener("thoughts:loaded", function (ev) { items = (ev.detail && ev.detail.items) || []; meta = ev.detail || {}; item = items[0] || null; render(); });
})();
