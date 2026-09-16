(function () {
  function resolveKnowledgeUrl() {
    var scripts = document.querySelectorAll("script[src]");
    for (var i = scripts.length - 1; i >= 0; i--) {
      var src = scripts[i].getAttribute("src") || "";
      if (src.indexOf("assets/js/") !== -1) {
        return src.replace(/assets\/js\/[^/?]+(\?.*)?$/, "api/knowledge.json");
      }
    }
    return "/api/knowledge.json";
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  var LABELS = {
    fresh: "已验证",
    stale: "待复查",
    changed: "可能已变",
    contested: "有争议",
    archived: "已归档"
  };

  function badge(rec) {
    if (!rec || !rec.status) return "";
    var status = rec.status;
    var label = LABELS[status] || status;
    var bits = [
      '<span class="knowledge-status knowledge-status--' +
        esc(status) +
        '" title="Knowledge status">' +
        esc(label) +
        "</span>"
    ];
    if (rec.last_verified) {
      bits.push('<span class="knowledge-status__meta">验证 ' + esc(rec.last_verified) + "</span>");
    }
    if (rec.next_review) {
      bits.push('<span class="knowledge-status__meta">下次 ' + esc(rec.next_review) + "</span>");
    }
    return '<span class="knowledge-status__group">' + bits.join("") + "</span>";
  }

  function matchItem(items, href) {
    if (!href) return null;
    var clean = href.split("#")[0].split("?")[0];
    var file = clean.split("/").pop();
    for (var i = 0; i < items.length; i++) {
      var url = String(items[i].url || "");
      if (!url) continue;
      if (clean === url || clean.endsWith(url) || url.endsWith(clean)) return items[i];
      if (file && url.split("/").pop() === file) return items[i];
    }
    return null;
  }

  function paintArticle(item) {
    var rec = item.knowledge;
    if (!rec) return;
    var metas = document.querySelectorAll(".article-meta");
    if (!metas.length) return;
    metas.forEach(function (meta) {
      if (meta.querySelector(".knowledge-status__group")) return;
      meta.insertAdjacentHTML("beforeend", badge(rec));
    });
  }

  function paintCards(items) {
    document.querySelectorAll("a.card[href]").forEach(function (card) {
      if (card.querySelector(".knowledge-status")) return;
      var item = matchItem(items, card.getAttribute("href"));
      if (!item || !item.knowledge) return;
      var rec = item.knowledge;
      var tags = card.querySelector(".card__tags") || card.querySelector(".card__meta");
      if (!tags) return;
      var el = document.createElement("span");
      el.className = "tag knowledge-status knowledge-status--" + rec.status;
      el.textContent = LABELS[rec.status] || rec.status;
      tags.appendChild(el);
      card.setAttribute("data-knowledge", rec.status);
    });
  }

  function paintBoard(items) {
    var root = document.getElementById("lab-knowledge");
    if (!root) return;
    var counts = {};
    items.forEach(function (it) {
      var s = (it.knowledge && it.knowledge.status) || "fresh";
      counts[s] = (counts[s] || 0) + 1;
    });
    var rows = items
      .map(function (it) {
        var kn = it.knowledge || {};
        var href = it.url || "#";
        if (href.charAt(0) === "/") href = ".." + href;
        return (
          "<tr>" +
          '<td><a href="' +
          esc(href) +
          '">' +
          esc(it.title) +
          "</a></td>" +
          "<td>" +
          esc(it.type) +
          "</td>" +
          '<td><span class="knowledge-status knowledge-status--' +
          esc(kn.status || "") +
          '">' +
          esc(LABELS[kn.status] || kn.status || "") +
          "</span></td>" +
          "<td>" +
          esc(kn.last_verified || "") +
          "</td>" +
          "<td>" +
          esc(kn.next_review || "") +
          "</td>" +
          "</tr>"
        );
      })
      .join("");
    var summary = Object.keys(LABELS)
      .filter(function (k) {
        return counts[k];
      })
      .map(function (k) {
        return LABELS[k] + " " + counts[k];
      })
      .join(" · ");
    root.innerHTML =
      '<p class="knowledge-board__lead">已发表知识的有效性，和 Bench 入境门禁分开。STALE 是过期，不是错误。</p>' +
      '<p class="knowledge-board__counts">' +
      esc(summary || "尚无条目") +
      "</p>" +
      '<div class="knowledge-board__table"><table><thead><tr><th>条目</th><th>栏目</th><th>状态</th><th>最近验证</th><th>下次复查</th></tr></thead><tbody>' +
      rows +
      "</tbody></table></div>";
  }

  function apply(data) {
    var items = (data && data.items) || [];
    var here = location.pathname;
    var current = matchItem(items, here);
    if (current) paintArticle(current);
    paintCards(items);
    paintBoard(items);
  }

  var url = resolveKnowledgeUrl();
  fetch(url)
    .then(function (res) {
      if (!res.ok) throw new Error("knowledge " + res.status);
      return res.json();
    })
    .then(apply)
    .catch(function () {});
})();
