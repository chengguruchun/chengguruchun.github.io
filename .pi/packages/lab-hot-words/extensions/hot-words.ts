/**
 * Hot Words weekly loop tools for AI Knowledge Lab.
 * Designed to run under Pi / Oh My Pi with DeepSeek as the model.
 */
import * as fs from "node:fs";
import * as path from "node:path";

type AnyPi = {
  registerCommand: (name: string, opts: Record<string, unknown>) => void;
  registerTool: (tool: Record<string, unknown>) => void;
};

function findRepoRoot(start = process.cwd()): string {
  let cur = path.resolve(start);
  for (let i = 0; i < 12; i++) {
    if (fs.existsSync(path.join(cur, "times", "index.html")) && fs.existsSync(path.join(cur, "content"))) {
      return cur;
    }
    const parent = path.dirname(cur);
    if (parent === cur) break;
    cur = parent;
  }
  return path.resolve(start);
}

function todayISOShanghai(): string {
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  return fmt.format(new Date()); // YYYY-MM-DD
}

function periodToSlug(period: string): string {
  // 2026-09-W2 -> 2026-09-w2
  return period.trim().toLowerCase();
}

function readStatus(repo: string) {
  const timesDir = path.join(repo, "content", "times");
  const files = fs.existsSync(timesDir)
    ? fs.readdirSync(timesDir).filter((f) => f.endsWith(".md")).sort()
    : [];
  const latest = files.length ? files[files.length - 1] : null;
  let latestMeta: Record<string, string> = {};
  if (latest) {
    const raw = fs.readFileSync(path.join(timesDir, latest), "utf8");
    const m = raw.match(/^---\n([\s\S]*?)\n---/);
    if (m) {
      for (const line of m[1].split("\n")) {
        const i = line.indexOf(":");
        if (i > 0) latestMeta[line.slice(0, i).trim()] = line.slice(i + 1).trim();
      }
    }
  }
  let api: unknown = null;
  const apiPath = path.join(repo, "api", "times.json");
  if (fs.existsSync(apiPath)) {
    try {
      api = JSON.parse(fs.readFileSync(apiPath, "utf8"));
    } catch {
      api = { error: "invalid json" };
    }
  }
  return {
    repo,
    latestFile: latest,
    latestMeta,
    allFiles: files,
    api,
  };
}

function applyHotWord(repo: string, args: {
  period: string;
  word: string;
  why: string;
  cadence?: string;
  dryRun?: boolean;
}) {
  const period = args.period.trim();
  const word = args.word.trim();
  const why = args.why.trim();
  const cadence = (args.cadence || "weekly").trim();
  const dryRun = !!args.dryRun;
  const slug = periodToSlug(period);
  const date = todayISOShanghai();
  const id = `times-${slug}`;
  const mdPath = path.join(repo, "content", "times", `${slug}.md`);
  const htmlPath = path.join(repo, "times", "index.html");
  const apiPath = path.join(repo, "api", "times.json");

  const md = `---
id: ${id}
type: Times
title: ${period} · ${word}
period: ${period}
cadence: ${cadence}
date: ${date}
word: ${word}
---

# ${word}

${why}
`;

  const weekLabel = period.includes("-W")
    ? period.replace(/^(\d{4})-(\d{2})-W(\d+)$/i, (_, y, m, w) => `${y}-${m} · Week ${Number(w)}`)
    : period;

  let html = fs.readFileSync(htmlPath, "utf8");
  html = html.replace(
    /<meta name="description" content="[^"]*">/,
    `<meta name="description" content="Hot Words · ${word} · ${period}">`,
  );
  // Replace featured article block (first times-period article)
  const article = `        <article class="times-year times-period" data-period="${period}" data-cadence="${cadence}" data-word="${word}">
          <p class="times-year__meta">
            <span class="times-year__badge">${cadence === "weekly" ? "Weekly" : cadence}</span>
            <span>${weekLabel}</span>
            <span>更新于 ${date}</span>
          </p>
          <h2 class="times-year__word">${word}</h2>
          <p class="times-year__why">${why}</p>
          <div class="times-vote" data-times-vote>
            <p class="times-vote__label">你的态度</p>
            <div class="times-vote__actions" role="group" aria-label="Like or dislike this hot word">
              <button type="button" class="times-vote__btn" data-vote="like" aria-pressed="false">Like</button>
              <button type="button" class="times-vote__btn" data-vote="dislike" aria-pressed="false">Dislike</button>
            </div>
            <p class="times-vote__hint" data-vote-hint></p>
          </div>
        </article>`;

  if (/<article class="times-year times-period"[\s\S]*?<\/article>/.test(html)) {
    html = html.replace(/<article class="times-year times-period"[\s\S]*?<\/article>/, article);
  } else {
    html = html.replace(
      /(<div class="wrap">)\s*/,
      `$1\n${article}\n        `,
    );
  }

  const titleNice = period.match(/^(\d{4}-\d{2})-W(\d+)$/i)
    ? period.replace(/^(\d{4}-\d{2})-W(\d+)$/i, (_, ymo, w) => `${ymo} Week ${Number(w)} · ${word}`)
    : `${period} · ${word}`;
  const entry: any = {
    id,
    period,
    cadence,
    word,
    title: titleNice,
    why,
    date,
    url: "/times/",
    markdown: `/content/times/${slug}.md`,
  };

  let api: any = {
    type: "Times",
    format: "one-word-per-issue (annual-hotword style)",
    cadence: "weekly-or-monthly",
    issues: [],
  };
  if (fs.existsSync(apiPath)) {
    try {
      api = JSON.parse(fs.readFileSync(apiPath, "utf8"));
    } catch {
      /* keep default */
    }
  }
  let issues = Array.isArray(api.issues) ? api.issues : [];
  if (!issues.length && Array.isArray(api.items)) {
    issues = api.items;
    delete api.items;
  }
  api.issues = [entry, ...issues.filter((x: any) => x && x.id !== id && x.period !== period)];
  api.updated = date;
  api.current = period;

  const changed = [mdPath, htmlPath, apiPath];
  if (!dryRun) {
    fs.mkdirSync(path.dirname(mdPath), { recursive: true });
    fs.writeFileSync(mdPath, md, "utf8");
    fs.writeFileSync(htmlPath, html, "utf8");
    fs.mkdirSync(path.dirname(apiPath), { recursive: true });
    fs.writeFileSync(apiPath, JSON.stringify(api, null, 2) + "\n", "utf8");
  }

  return { dryRun, period, word, date, changed, markdown: `/content/times/${slug}.md` };
}

export default function (pi: AnyPi) {
  const runHelp = async (_args: string, ctx: any) => {
    ctx?.ui?.notify?.(
      "Hot Words loop: use tools lab_hot_words_status → research → lab_hot_words_apply. Model: DeepSeek via Pi/OMP.",
      "info",
    );
  };

  pi.registerCommand("hot-words", {
    description: "Run / explain the weekly Hot Words loop",
    handler: runHelp,
  });
  pi.registerCommand("hotwords", {
    description: "Alias of /hot-words",
    handler: runHelp,
  });

  pi.registerTool({
    name: "lab_hot_words_status",
    description: "Read current Hot Words state from the Knowledge Lab repo (content/times + api/times.json).",
    parameters: {
      type: "object",
      properties: {},
      additionalProperties: false,
    },
    async execute() {
      const repo = findRepoRoot();
      return { content: [{ type: "text", text: JSON.stringify(readStatus(repo), null, 2) }] };
    },
  });

  pi.registerTool({
    name: "lab_hot_words_propose",
    description:
      "Return a structured proposal brief for the next Hot Words cycle. The model should research and fill candidates; this tool does not call an LLM.",
    parameters: {
      type: "object",
      properties: {
        period: { type: "string", description: "e.g. 2026-09-W2" },
      },
      additionalProperties: false,
    },
    async execute(args: { period?: string }) {
      const repo = findRepoRoot();
      const status = readStatus(repo);
      const brief = {
        period: args?.period || "NEXT-WEEK",
        current: status.latestMeta,
        protocol: [
          "List 3 candidate hot words with evidence links/snippets",
          "Compare: novelty vs continuity vs engineering relevance",
          "Pick one; write why in direct Chinese (no hedging filler)",
          "Separate proxy buzz from real engineering outcome",
          "Call lab_hot_words_apply with dryRun=true first, then apply",
        ],
        output_schema: {
          candidates: [{ word: "", evidence: [], score_notes: "" }],
          chosen: { word: "", why: "", period: "", cadence: "weekly" },
        },
      };
      return { content: [{ type: "text", text: JSON.stringify(brief, null, 2) }] };
    },
  });

  pi.registerTool({
    name: "lab_hot_words_apply",
    description:
      "Write Hot Words markdown + times/index.html + api/times.json. Never git push. Use dryRun to preview.",
    parameters: {
      type: "object",
      properties: {
        period: { type: "string" },
        word: { type: "string" },
        why: { type: "string" },
        cadence: { type: "string" },
        dryRun: { type: "boolean" },
      },
      required: ["period", "word", "why"],
      additionalProperties: false,
    },
    async execute(args: {
      period: string;
      word: string;
      why: string;
      cadence?: string;
      dryRun?: boolean;
    }) {
      const repo = findRepoRoot();
      const result = applyHotWord(repo, args);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    },
  });
}
