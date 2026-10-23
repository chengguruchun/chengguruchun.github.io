(() => {
  "use strict";
  function cleanPath(path) {
    while (path.length > 1 && path.endsWith("/")) path = path.slice(0, -1);
    return path;
  }
  function init() {
    const article = document.querySelector("main article.article-body") || document.querySelector("main article") || document.querySelector("main");
    const hero = article && article.querySelector(".page-hero");
    const heading = hero && hero.querySelector("h1");
    if (!article || !hero || !heading || document.getElementById("article-actions")) return;

    const style = document.createElement("style");
    style.textContent = ".article-actions{display:flex;flex-wrap:wrap;gap:24px;align-items:center;margin:20px 0 30px;color:#62666d;font-size:16px}.article-actions button,.article-actions a{display:inline-flex;align-items:center;gap:8px;border:0;background:transparent;color:inherit;text-decoration:none;font:inherit;cursor:pointer;padding:8px 0}.article-actions button:hover,.article-actions a:hover{color:#1769ff}.article-actions button:focus-visible,.article-actions a:focus-visible{outline:2px solid #1769ff;outline-offset:4px}.article-actions__status{font-size:13px;color:#24834a}@media(max-width:640px){.article-actions{gap:16px;font-size:14px;margin:16px 0 24px}}";
    document.head.appendChild(style);

    const toolbar = document.createElement("div");
    toolbar.id = "article-actions";
    toolbar.className = "article-actions";
    toolbar.setAttribute("aria-label", "文章导出操作");
    toolbar.innerHTML = '<button type="button" class="article-actions__copy"><span>▢ LLM 副本</span></button><a class="article-actions__markdown" target="_blank" rel="noopener"><span>〈〉以 Markdown 格式查看</span></a><span class="article-actions__status" role="status" aria-live="polite"></span>';
    hero.appendChild(toolbar);

    const status = toolbar.querySelector(".article-actions__status");
    const copyButton = toolbar.querySelector(".article-actions__copy");
    const markdownLink = toolbar.querySelector(".article-actions__markdown");
    let markdownPath = "";

    fetch(new URL("/api/catalog.json", window.location.origin), { cache: "no-cache" })
      .then(response => { if (!response.ok) throw new Error("catalog unavailable"); return response.json(); })
      .then(catalog => {
        const currentPath = cleanPath(window.location.pathname);
        const item = (catalog.items || []).find(entry => {
          try { return cleanPath(new URL(entry.url, window.location.origin).pathname) === currentPath; }
          catch (_) { return false; }
        });
        markdownPath = item && (item.content || item.markdown) || "";
        if (!markdownPath) throw new Error("Markdown path missing");
        markdownLink.href = new URL(markdownPath, window.location.origin).href;
        markdownLink.title = "在新标签页中查看 Markdown 原文";
      })
      .catch(() => {
        markdownLink.setAttribute("aria-disabled", "true");
        markdownLink.style.opacity = ".55";
        status.textContent = "暂时无法获取原文路径";
      });

    copyButton.addEventListener("click", async () => {
      if (!markdownPath) { status.textContent = "原文路径尚未加载，请稍后重试"; return; }
      copyButton.disabled = true;
      status.textContent = "正在获取 Markdown…";
      try {
        const response = await fetch(new URL(markdownPath, window.location.origin).href, { cache: "no-cache" });
        if (!response.ok) throw new Error("Markdown fetch failed");
        const markdown = await response.text();
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(markdown);
        } else {
          const area = document.createElement("textarea");
          area.value = markdown; area.setAttribute("readonly", "");
          area.style.position = "fixed"; area.style.opacity = "0";
          document.body.appendChild(area); area.select();
          const ok = document.execCommand("copy"); area.remove();
          if (!ok) throw new Error("copy failed");
        }
        status.textContent = "Markdown 原文已复制";
      } catch (_) {
        status.textContent = "复制失败，请点击 Markdown 链接手动查看";
      } finally { copyButton.disabled = false; }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
