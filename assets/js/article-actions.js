(() => {
  "use strict";
  const STYLE_ID = "article-actions-style";
  const TOOLBAR_ID = "article-actions";
  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
    .article-actions{display:flex;flex-wrap:wrap;gap:24px;align-items:center;margin:20px 0 30px;color:#62666d;font-size:16px}
    .article-actions button,.article-actions a{display:inline-flex;align-items:center;gap:8px;border:0;background:transparent;color:inherit;text-decoration:none;font:inherit;cursor:pointer;padding:8px 0}
    .article-actions button:hover,.article-actions a:hover{color:#1769ff}
    .article-actions button:focus-visible,.article-actions a:focus-visible{outline:2px solid #1769ff;outline-offset:4px;border-radius:3px}
    .article-actions__icon{width:19px;height:19px;flex:none}
    .article-actions__status{font-size:13px;color:#24834a}
    @media(max-width:640px){.article-actions{gap:16px;font-size:14px;margin:16px 0 24px}}
  `;
  document.head.appendChild(style);

  async function init() {
    const article = document.querySelector("main article");
    const heading = article && article.querySelector(".page-hero h1");
    if (!article || !heading || document.getElementById(TOOLBAR_ID)) return;

    const meta = article.querySelector(".page-hero .article-meta");
    const target = meta || article.querySelector(".page-hero .prose-wrap");
    if (!target) return;

    const toolbar = document.createElement("div");
    toolbar.className = "article-actions";
    toolbar.id = TOOLBAR_ID;
    toolbar.setAttribute("aria-label", "文章导出操作");
    toolbar.innerHTML = `
      <button type="button" class="article-actions__copy" aria-label="复制 Markdown 原文到剪贴板">
        <svg class="article-actions__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M8 7V3h10l4 4v14H8z"/><path d="M18 3v5h4M4 7H3v14h13"/></svg>
        <span>LLM 副本</span>
      </button>
      <a class="article-actions__markdown" target="_blank" rel="noopener" aria-label="以 Markdown 格式查看原文">
        <svg class="article-actions__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="m9 8-4 4 4 4m6-8 4 4-4 4"/></svg>
        <span>以 Markdown 格式查看</span>
      </a>
      <span class="article-actions__status" role="status" aria-live="polite"></span>
    `;
    target.insertAdjacentElement("afterend", toolbar);

    const status = toolbar.querySelector(".article-actions__status");
    const copyButton = toolbar.querySelector(".article-actions__copy");
    const markdownLink = toolbar.querySelector(".article-actions__markdown");
    const pagePath = window.location.pathname.replace(/\\/+$/, "");
    let markdownPath = "";

    try {
      const response = await fetch(new URL("../api/catalog.json", window.location.href), { cache: "no-cache" });
      if (!response.ok) throw new Error("无法读取文章索引");
      const catalog = await response.json();
      const item = (catalog.items || []).find(entry => {
        try { return new URL(entry.url, window.location.origin).pathname.replace(/\\/+$/, "") === pagePath; }
        catch (_) { return false; }
      });
      markdownPath = item && (item.content || item.markdown) || "";
      if (!markdownPath) throw new Error("索引中没有原文路径");
      const markdownURL = new URL(markdownPath, window.location.origin);
      markdownLink.href = markdownURL.href;
      markdownLink.title = "在新标签页中查看 Markdown 原文";
    } catch (error) {
      markdownLink.setAttribute("aria-disabled", "true");
      markdownLink.removeAttribute("href");
      markdownLink.style.opacity = ".55";
      markdownLink.style.cursor = "not-allowed";
      status.textContent = "暂时无法获取原文路径";
      copyButton.disabled = true;
    }

    copyButton.addEventListener("click", async () => {
      if (!markdownPath) return;
      copyButton.disabled = true;
      status.textContent = "正在获取 Markdown…";
      try {
        const url = new URL(markdownPath, window.location.origin);
        const response = await fetch(url.href, { cache: "no-cache" });
        if (!response.ok) throw new Error("原文获取失败");
        const markdown = await response.text();
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(markdown);
        } else {
          const textarea = document.createElement("textarea");
          textarea.value = markdown;
          textarea.setAttribute("readonly", "");
          textarea.style.position = "fixed";
          textarea.style.opacity = "0";
          document.body.appendChild(textarea);
          textarea.select();
          const success = document.execCommand("copy");
          textarea.remove();
          if (!success) throw new Error("浏览器不允许复制");
        }
        status.textContent = "Markdown 原文已复制";
        const label = copyButton.querySelector("span");
        label.textContent = "已复制";
        window.setTimeout(() => {
          label.textContent = "LLM 副本";
          status.textContent = "";
        }, 2200);
      } catch (error) {
        status.textContent = "复制失败，请点击 Markdown 链接手动复制";
      } finally {
        copyButton.disabled = false;
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
