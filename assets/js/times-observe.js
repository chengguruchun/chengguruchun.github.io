(function () {
  var root = document.querySelector("[data-hotwords-observe]");
  if (!root) return;

  var panelEl = root.querySelector("[data-observe-panel]");
  var visitsPage = document.querySelector("[data-visits-page]");
  var article = document.querySelector(".times-period[data-period]");

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function phaseLabel(p) {
    var map = {
      published: "已发布",
      skipped: "已跳过",
      failed: "失败",
      applied: "已写入",
      validated: "已校验",
      proposed: "已提案",
      started: "开始"
    };
    return map[p] || p || "—";
  }

  function gateLabel(k) {
    var map = { schema: "结构", duplicate: "去重", editorial: "编辑", evidence: "证据" };
    return map[k] || k;
  }

  function gateClass(v) {
    if (v === "pass") return "is-pass";
    if (v === "fail") return "is-fail";
    if (v === "weak") return "is-weak";
    return "is-skip";
  }

  function gateText(v) {
    var map = { pass: "通过", fail: "未过", weak: "偏弱", skip: "跳过" };
    return map[v] || v || "—";
  }

  function localVote(period) {
    try {
      return localStorage.getItem("lab-hotwords-vote:" + period) || "";
    } catch (e) {
      return "";
    }
  }

  function getJSON(url) {
    return fetch(url, { credentials: "omit" }).then(function (r) {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    });
  }

  function render(latest, index, feedback) {
    if (!panelEl) return;
    if (!latest && !feedback) {
      panelEl.innerHTML = '<p class="hotwords-observe__empty">还没有可展示的运行记录。</p>';
      return;
    }

    var m = latest || {};
    var fb = feedback || {};
    var proposal = m.proposal || {};
    var gates = m.gates || ((fb.lastRun && fb.lastRun.gates) || {});
    var publish = m.publish || ((fb.lastRun && fb.lastRun.publish) || {});
    var period = m.period || fb.period || (article && article.getAttribute("data-period")) || "";
    var word = proposal.word || fb.word || (article && article.getAttribute("data-word")) || "—";
    var vote = localVote(period);
    var pageVisits = visitsPage && visitsPage.textContent && visitsPage.textContent !== "-" ? visitsPage.textContent : "—";
    var hints = fb.learnHints || {};
    var rejected = (hints.rejectedCandidates || []).map(function (x) { return x.word; }).filter(Boolean);
    var runs = ((index && index.items) || fb.recentRuns || []).slice(0, 5);

    var gateHtml = ["schema", "duplicate", "editorial", "evidence"].map(function (k) {
      var v = gates[k] || "skip";
      return (
        '<span class="hotwords-gate ' + gateClass(v) + '">' +
        esc(gateLabel(k)) + " · " + esc(gateText(v)) +
        "</span>"
      );
    }).join("");

    var runsHtml = runs.length
      ? "<ul class=\"hotwords-observe__list\">" +
        runs.map(function (it) {
          return (
            "<li>" +
            "<span class=\"hotwords-observe__phase\">" + esc(phaseLabel(it.phase)) + "</span> " +
            esc(it.period || "") + " · " + esc(it.word || "—") +
            "</li>"
          );
        }).join("") +
        "</ul>"
      : '<p class="hotwords-observe__empty">尚无历史轮次。</p>';

    var evidenceNote = "";
    if (gates.evidence === "pass") evidenceNote = "本轮有带 URL 的结构化证据。";
    else if (gates.evidence === "weak") evidenceNote = "本轮证据偏弱（多为口头说明，缺 URL）。";
    else if (gates.evidence === "skip") evidenceNote = "本轮未记录证据（常见于存量发布或跳过）。";
    else if (gates.evidence === "fail") evidenceNote = "本轮证据门禁未通过。";

    panelEl.innerHTML =
      '<div class="hotwords-observe__card">' +
      '<p class="hotwords-observe__meta">' +
      '<span class="hotwords-observe__phase">' + esc(phaseLabel(m.phase || (fb.lastRun && fb.lastRun.phase))) + "</span>" +
      "<span>" + esc(period) + "</span>" +
      "<span>" + esc(word) + "</span>" +
      "</p>" +
      '<div class="hotwords-observe__gates" aria-label="质量门禁">' + gateHtml + "</div>" +
      (evidenceNote ? '<p class="hotwords-observe__note">' + esc(evidenceNote) + "</p>" : "") +
      '<dl class="hotwords-observe__dl">' +
      "<div><dt>本机投票</dt><dd>" + esc(vote === "like" ? "Like" : vote === "dislike" ? "Dislike" : "未选") + "</dd></div>" +
      "<div><dt>本页访问</dt><dd>" + esc(pageVisits) + "</dd></div>" +
      "<div><dt>证据条数</dt><dd>" + esc((proposal.evidenceCount != null ? proposal.evidenceCount : (fb.lastRun && fb.lastRun.evidenceCount)) || 0) + "</dd></div>" +
      "</dl>" +
      (rejected.length
        ? '<p class="hotwords-observe__note">未入选候选：' + esc(rejected.join("、")) + "</p>"
        : "") +
      (hints.prefer ? '<p class="hotwords-observe__note"><strong>下一轮倾向</strong>：' + esc(hints.prefer) + "</p>" : "") +
      (hints.avoid ? '<p class="hotwords-observe__note"><strong>下一轮回避</strong>：' + esc(hints.avoid) + "</p>" : "") +
      '<div class="hotwords-observe__history"><p class="hotwords-observe__hist-label">最近轮次</p>' + runsHtml + "</div>" +
      '<p class="hotwords-observe__links">原始数据 · ' +
      '<a href="../api/hot-words/runs/latest.json">latest</a> · ' +
      '<a href="../api/hot-words/feedback.json">feedback</a> · ' +
      '<a href="../api/hot-words/runs/index.json">runs</a>' +
      "</p>" +
      "</div>";
  }

  Promise.all([
    getJSON("../api/hot-words/runs/latest.json").catch(function () { return null; }),
    getJSON("../api/hot-words/runs/index.json").catch(function () { return null; }),
    getJSON("../api/hot-words/feedback.json").catch(function () { return null; }),
  ]).then(function (all) {
    render(all[0], all[1], all[2]);
    setTimeout(function () { render(all[0], all[1], all[2]); }, 1200);
  });
})();
