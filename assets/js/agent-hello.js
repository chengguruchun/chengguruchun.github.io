(function () {
  /**
   * Shows how many agents have called lab_hello.
   * Reads via /get/ so that humans browsing the page never inflate the number.
   * Counter is written only by agents hitting /hit/ per the SKILL.md protocol.
   */
  var READ_URL =
    "https://abacus.jasoncameron.dev/get/chengguruchun-lab/agent-connect";

  function render(el, text) {
    el.textContent = text;
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    var el = document.querySelector("[data-agent-hello]");
    if (!el) return;
    render(el, "…");

    fetch(READ_URL, { method: "GET", mode: "cors", cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("counter " + r.status);
        return r.json();
      })
      .then(function (data) {
        var n = data && data.value;
        if (typeof n !== "number") throw new Error("bad payload");
        render(el, Number(n).toLocaleString("zh-CN"));
      })
      .catch(function () {
        render(el, "—");
      });
  });
})();
