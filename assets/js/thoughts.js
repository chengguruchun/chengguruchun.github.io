(function () {
  var root = document.getElementById("lab-thoughts");
  if (!root) return;

  window.LabBench = window.LabBench || {};
  window.LabBench.modelGates = function (it) {
    if (it.model_gates && it.model_gates.length) {
      return it.model_gates.map(function (g) {
        return {
          key: g.id,
          name: g.name || g.id,
          pass: !!g.pass,
          status: g.status || (g.pass ? "pass" : "unpass"),
          note: g.note || ""
        };
      });
    }
    return [];
  };

  window.LabBench.gates = function (it) {
    if (it.gates && it.gates.length) {
      return it.gates.map(function (g) {
        return { key: g.id, name: g.name || g.id, pass: !!g.pass };
      });
    }
    return [
      { key: "origin", name: "Origin", pass: !!it.origin },
      { key: "contribution", name: "Contribution", pass: !!it.contribution },
      { key: "articles_ok", name: "¬ ai+known", pass: !(it.origin === "ai" && it.contribution === "known") },
      { key: "evidence", name: "Evidence", pass: Array.isArray(it.evidence) && it.evidence.length > 0 },
      { key: "route", name: "Route", pass: !!it.route },
      { key: "published", name: "Published", pass: it.stage === "published" && !!it.published_url }
    ];
  };

  var LANDING = {
    diverse: "../diverse/",
    articles: "../articles/",
    videos: "../videos/",
    projects: "../projects/"
  };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function hrefOf(it) {
    if (it.published_url) return it.published_url;
    if (it.route && LANDING[it.route]) return LANDING[it.route];
    return "";
  }

  function card(it) {
    var href = hrefOf(it);
    var stage = it.stage || "topic";
    var route = it.route || "";
    var also = Array.isArray(it.also) ? it.also : [];
    var origin = (it.origin || "") + (it.contribution ? " · " + it.contribution : "");
    var excerpt = "";
    if (it.status === "hold" || !route) {
      excerpt = "未分流。停在 Bench 是刻意的。";
    } else if (it.critiques && it.critiques[0]) {
      excerpt = it.critiques[0];
    }
    var routeLabel = route ? "→ " + route : "未分流";
    if (also.length) routeLabel += " · " + also.join(" · ");
    var gateHtml = window.LabBench.gates(it)
      .map(function (g) {
        return (
          '<span class="gate-pill gate-pill--' +
          (g.pass ? "pass" : "unpass") +
          '" title="' +
          esc(g.name) +
          '">' +
          esc(g.name) +
          " " +
          (g.pass ? "PASS" : "UNPASS") +
          "</span>"
        );
      })
      .join("");
    var modelGates = window.LabBench.modelGates(it);
    var modelHtml = modelGates
      .map(function (g) {
        var label = g.status === "pending" ? "待判" : g.status === "stale" ? "过期" : g.pass ? "PASS" : "UNPASS";
        return (
          '<span class="gate-pill gate-pill--model gate-pill--' +
          esc(g.status) +
          '" title="' +
          esc(g.note || g.name) +
          '">' +
          esc(g.name) +
          " " +
          label +
          "</span>"
        );
      })
      .join("");
    var inner =
      '<div class="card__meta"><span>Thought</span><span>' +
      esc(stage) +
      "</span></div>" +
      '<h2 class="card__title">' +
      esc(it.thought || it.id) +
      "</h2>" +
      (excerpt ? '<p class="card__excerpt">' + esc(excerpt) + "</p>" : "") +
      '<div class="card__tags">' +
      '<span class="tag tag--stage">' +
      esc(stage) +
      "</span>" +
      '<span class="tag tag--route">' +
      esc(routeLabel) +
      "</span>" +
      '<span class="tag tag--origin">' +
      esc(origin) +
      "</span></div>" +
      '<div class="thought-gates">' +
      '<p class="thought-gates__label">字段</p>' +
      gateHtml +
      "</div>" +
      (modelHtml
        ? '<div class="thought-gates thought-gates--model"><p class="thought-gates__label">模型 · 标准提示词</p>' +
          modelHtml +
          "</div>"
        : "");
    var hold = it.status === "hold" || !route;
    var modelStatus = modelGates.map(function (g) {
      return "model-" + g.status;
    });
    var tags = [stage, route, hold ? "hold" : "pass"]
      .concat(also, [it.origin, it.contribution], modelStatus)
      .filter(Boolean)
      .join(" ");
    var attrs =
      ' data-stage="' +
      esc(stage) +
      '" data-route="' +
      esc(route) +
      '" data-tags="' +
      esc(tags) +
      '"';
    if (href) {
      return (
        '<a class="card thought-card" href="' +
        esc(href) +
        '"' +
        attrs +
        ">" +
        inner +
        "</a>"
      );
    }
    return (
      '<article class="card thought-card thought-card--hold"' +
      attrs +
      ">" +
      inner +
      "</article>"
    );
  }

  var url = root.getAttribute("data-src") || "../api/thoughts.json";
  fetch(url, { headers: { Accept: "application/json" } })
    .then(function (r) {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    })
    .then(function (data) {
      var items = (data && data.items) || [];
      if (root.getAttribute("data-mode") === "stage") {
        root.innerHTML = "";
        root.hidden = true;
      } else {
        root.innerHTML = items.map(card).join("");
      }
      document.dispatchEvent(
        new CustomEvent("thoughts:loaded", {
          detail: {
            items: items,
            criteria: data.criteria,
            criteria_version: data.criteria_version
          }
        })
      );
    })
    .catch(function () {
      root.innerHTML = "";
    });
})();
