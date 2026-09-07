(function () {
  /**
   * Dedicated visit counters (not busuanzi).
   * Backend: https://abacus.jasoncameron.dev — namespace unique to this lab.
   * Local preview uses a separate namespace so it won't pollute production.
   */
  var host = (location.hostname || "").toLowerCase();
  var NS =
    host === "127.0.0.1" || host === "localhost"
      ? "chengguruchun-lab-local"
      : "chengguruchun-lab";

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function pageKey() {
    var path = (location.pathname || "/")
      .replace(/\/index\.html$/i, "/")
      .replace(/\/+$/, "") || "/";
    var key =
      "page-" +
      path
        .replace(/^\//, "")
        .replace(/[^a-zA-Z0-9/_-]+/g, "-")
        .replace(/\//g, "_");
    return key === "page-" ? "page-home" : key;
  }

  function setNum(sel, n) {
    var el = document.querySelector(sel);
    if (!el || n == null || isNaN(n)) return;
    el.textContent = Number(n).toLocaleString("zh-CN");
  }

  function hit(key) {
    var url =
      "https://abacus.jasoncameron.dev/hit/" +
      encodeURIComponent(NS) +
      "/" +
      encodeURIComponent(key);
    return fetch(url, { method: "GET", mode: "cors", cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("counter " + r.status);
        return r.json();
      })
      .then(function (data) {
        var n = data && data.value;
        return typeof n === "number" ? n : null;
      });
  }

  ready(function () {
    var siteEl = document.querySelector("[data-visits-site]");
    var pageEl = document.querySelector("[data-visits-page]");
    if (!siteEl && !pageEl) return;

    if (siteEl) siteEl.textContent = "…";
    if (pageEl) pageEl.textContent = "…";

    Promise.all([
      siteEl ? hit("site").catch(function () { return null; }) : Promise.resolve(null),
      pageEl ? hit(pageKey()).catch(function () { return null; }) : Promise.resolve(null),
    ]).then(function (nums) {
      if (nums[0] != null) setNum("[data-visits-site]", nums[0]);
      else if (siteEl) siteEl.textContent = "—";
      if (nums[1] != null) setNum("[data-visits-page]", nums[1]);
      else if (pageEl) pageEl.textContent = "—";
    });
  });
})();
