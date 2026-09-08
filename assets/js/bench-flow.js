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

  var viewAt = 0;
  var liveAt = 1;
  var items = [];
  var item = null;
  var meta = {};
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function stageAt(stage) {
    if (stage === "published") return 4;
    if (stage === "validated" || stage === "article_candidate") return 3;
    if (stage === "candidate") return 2;
    if (stage === "topic") return 1;
    return 0;
  }

  function fieldOf(it, key) {
    var gates = window.LabBench && window.LabBench.gates ? window.LabBench.gates(it) : [];
    return (
      gates.filter(function (g) {
        return g.key === key;
      })[0] || { key: key, name: key, pass: false }
    );
  }

  function modelOf(it, key) {
    var gates = window.LabBench && window.LabBench.modelGates ? window.LabBench.modelGates(it) : [];
    return (
      gates.filter(function (g) {
        return g.key === key;
      })[0] || { key: key, name: key, pass: false, status: "pending" }
    );
  }

  function whyBlocked(it, want) {
    if (want <= liveAt) return "";
    if (want >= 2 && (!fieldOf(it, "origin").pass || !fieldOf(it, "contribution").pass)) {
      return "Origin / Contribution 还没过。出不了 Topic。";
    }
    if (want >= 3 && !fieldOf(it, "evidence").pass) {
      return "Evidence 还是空的。字段都没过，更别提模型判「证据真相关」。";
    }
    if (want >= 3) {
      var ev = modelOf(it, "evidence_real");
      if (ev.status !== "pass") return "模型门禁还没判，或没过。字段非空不等于证据真相关。";
    }
    if (want >= 4 && !fieldOf(it, "route").pass) {
      return "没有 route。未分流的句子不会进右边栏目。";
    }
    if (want >= 4 && !fieldOf(it, "published").pass) {
      return "还不是 published。过门之前不当结论。";
    }
    return "还停在这一档。往前走要过门，不是点一下。";
  }

  function lamp(g, kind) {
    var status = g.status || (g.pass ? "pass" : "unpass");
    var word = status === "pending" ? "待判" : status === "stale" ? "过期" : g.pass ? "PASS" : "UNPASS";
    return (
      '<span class="bench-lamp bench-lamp--' +
      esc(status) +
      '" title="' +
      esc(g.note || g.name) +
      '"><i></i>' +
      esc(g.name || g.key) +
      " <em>" +
      word +
      "</em></span>"
    );
  }

  function setToken(at) {
    viewAt = at;
    el.style.setProperty("--at", String(at / (STOPS.length - 1)));
    el.querySelectorAll("[data-stop]").forEach(function (btn) {
      var i = Number(btn.getAttribute("data-stop"));
      btn.classList.toggle("is-here", i === at);
      btn.classList.toggle("is-past", i < liveAt);
      btn.classList.toggle("is-live", i === liveAt);
      btn.classList.toggle("is-ahead", i > liveAt);
    });
    var note = el.querySelector("[data-why]");
    if (note) {
      var blocked = item ? whyBlocked(item, at) : "";
      if (at > liveAt && blocked) {
        note.textContent = blocked;
        note.hidden = false;
        el.classList.add("is-blocked");
      } else if (at === liveAt && item && (item.status === "hold" || !item.route)) {
        var stop = STOPS[liveAt] ? STOPS[liveAt].name : "这一档";
        note.textContent = "停在 " + stop + " 是刻意的。没过门就不会进右边栏目。";
        note.hidden = false;
        el.classList.remove("is-blocked");
      } else {
        note.textContent = STOPS[at] ? STOPS[at].zh : "";
        note.hidden = false;
        el.classList.remove("is-blocked");
      }
    }
  }

  function go(want) {
    if (!item) return;
    if (want > liveAt) {
      setToken(want);
      el.classList.remove("is-shake");
      void el.offsetWidth;
      el.classList.add("is-shake");
      window.setTimeout(function () {
        el.classList.remove("is-shake");
        setToken(liveAt);
      }, reduce ? 0 : 720);
      return;
    }
    setToken(want);
  }

  function playIn() {
    if (reduce) {
      setToken(liveAt);
      return;
    }
    setToken(0);
    window.setTimeout(function () {
      setToken(liveAt);
    }, 520);
  }

  function render() {
    if (!item) {
      el.innerHTML = '<p class="bench-stage__empty">Bench 上空着。先蒸馏一句，再入境。</p>';
      return;
    }
    liveAt = stageAt(item.stage);
    var v = meta.criteria_version || "—";
    var doors = DOORS.map(function (d) {
      var open = item.route === d.id || (item.also && item.also.indexOf(d.id) !== -1);
      return (
        '<a class="bench-door' +
        (open ? " is-open" : " is-locked") +
        '" href="' +
        d.href +
        '">' +
        "<strong>" +
        d.name +
        "</strong>" +
        "<span>" +
        (open ? "已定去向" : "未开门") +
        "</span></a>"
      );
    }).join("");

    var queue = "";
    if (items.length > 1) {
      queue =
        '<div class="bench-queue" role="tablist" aria-label="台上的句子">' +
        items
          .map(function (it, i) {
            return (
              '<button type="button" role="tab" class="bench-queue__item' +
              (it === item ? " is-on" : "") +
              '" data-pick="' +
              i +
              '"><span class="bench-queue__stage">' +
              esc(it.stage || "topic") +
              "</span>" +
              esc(it.thought) +
              "</button>"
            );
          })
          .join("") +
        "</div>";
    }

    el.innerHTML =
      queue +
      '<p class="bench-stage__kicker">思想实验台 · ' +
      esc(item.stage) +
      " · " +
      esc(item.origin || "") +
      (item.contribution ? " · " + esc(item.contribution) : "") +
      "</p>" +
      '<blockquote class="bench-line">' +
      esc(item.thought) +
      "</blockquote>" +
      (item.critiques && item.critiques[0]
        ? '<p class="bench-line__aside">' + esc(item.critiques[0]) + "</p>"
        : "") +
      '<div class="bench-rail" aria-label="Thought 走轨">' +
      '<div class="bench-rail__glow" aria-hidden="true"></div>' +
      '<div class="bench-rail__line" aria-hidden="true"></div>' +
      '<div class="bench-rail__spark" aria-hidden="true"></div>' +
      '<div class="bench-rail__token" aria-hidden="true"><span></span></div>' +
      '<div class="bench-rail__stops">' +
      STOPS.map(function (s, i) {
        return (
          '<button type="button" class="bench-stop" data-stop="' +
          i +
          '"><b>' +
          esc(s.name) +
          "</b><small>" +
          esc(s.zh) +
          "</small></button>"
        );
      }).join("") +
      "</div></div>" +
      '<p class="bench-stage__why" data-why></p>' +
      '<div class="bench-lamps">' +
      '<div><span class="bench-lamps__k">字段</span>' +
      lamp(fieldOf(item, "origin")) +
      lamp(fieldOf(item, "contribution")) +
      lamp(fieldOf(item, "evidence")) +
      lamp(fieldOf(item, "route")) +
      "</div>" +
      '<div><span class="bench-lamps__k">模型 v' +
      esc(v) +
      '</span>' +
      lamp(modelOf(item, "sharp")) +
      lamp(modelOf(item, "evidence_real")) +
      lamp(modelOf(item, "route_fit")) +
      "</div></div>" +
      '<div class="bench-doors" aria-label="过门之后">' +
      doors +
      '<span class="bench-door bench-door--hold is-locked"><strong>Hold</strong><span>没过门，停在这里</span></span>' +
      "</div>" +
      '<div class="bench-stage__acts">' +
      '<button type="button" class="bench-replay" data-replay>再走一遍</button>' +
      '<a href="../api/thoughts-criteria.json">标准提示词</a>' +
      '<a href="../THOUGHT_LOOP.md">过程说明</a>' +
      "</div>";

    el.querySelectorAll("[data-pick]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var i = Number(btn.getAttribute("data-pick"));
        item = items[i] || item;
        render();
      });
    });
    el.querySelectorAll("[data-stop]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        go(Number(btn.getAttribute("data-stop")));
      });
    });
    var replay = el.querySelector("[data-replay]");
    if (replay) {
      replay.addEventListener("click", function () {
        playIn();
      });
    }
    playIn();
  }

  document.addEventListener("thoughts:loaded", function (ev) {
    items = (ev.detail && ev.detail.items) || [];
    meta = ev.detail || {};
    item = items[0] || null;
    render();
  });
})();
