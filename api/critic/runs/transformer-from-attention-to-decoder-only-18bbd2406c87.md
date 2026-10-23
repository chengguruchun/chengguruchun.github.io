## 🤖 Critic Lab Report

Article: `articles/transformer-from-attention-to-decoder-only.html`
Commit: `18bbd2406c87dd27c3e925affe07d601d6aa8664`
Model: `deepseek-chat`
Status: **needs_review**

The article is a coherent, appropriately hedged conceptual walkthrough of Transformer → Decoder-only → pretraining/post-training → train-vs-inference. Its strongest content (mask-mode over block-name, alignment stage, parallelism as engineering consequence) is largely established knowledge, framed honestly as personal re-understanding rather than novel theory. Main risks are medium-severity: a few mechanism claims are compressed to the point of being misleading (Attention as 'relation computation', the RLHF/DPO causal attribution of honesty/tool-calling, Exposure Bias framing), and the article under-specifies engineering boundary conditions (KV-cache, context-rot evidence, why decoder-only won) that materially affect the conclusions. The git diff itself is a cache-busting version bump only and carries no substantive editorial change.

## 1. Logic

- **MEDIUM** — '真正决定行为差异的是 Mask 模式，而不是块的标签'
  - Issue: True for attention directionality, but Encoder/Decoder blocks differ in more than mask: cross-attention (encoder output as K/V), per-layer depth/stacking, positional handling, and training objective/interface. Reducing the distinction to mask alone overstates the case.
  - Why it matters: A reader could infer that swapping masks converts an encoder into a decoder, which is wrong and would misguide anyone reasoning about architecture choice.
  - Test / fix: Qualify: '对于注意力可见性，mask 是决定性的；但 Encoder-Decoder 还存在 cross-attention 与训练目标差异。' Add one sentence listing those.

- **MEDIUM** — 'Transformer 把序列处理转化成了关系计算' + 长上下文信息利用问题
  - Issue: The article correctly says long window ≠ effective use, but offers no mechanism (lost-in-the-middle, attention dilution, KV-cache cost, positional extrapolation). The jump from 'Attention computes relations' to 'context engineering is the real problem' is intuitive but unsupported in-text.
  - Why it matters: This is the hinge to the author's Context Engineering thread; without a mechanism the connection reads as rhetorical rather than analytical.
  - Test / fix: Name at least one mechanism class (attention sink / positional degradation / retrieval-vs-in-context) and mark the causal story as hypothesis, citing a local article if one exists.

- **MEDIUM** — '训练是在已知序列上并行学习；推理是在未知未来上逐步执行'，并称并行度是工程后果
  - Issue: The caveat is good, but the framing still frames inference as inherently sequential. Prefill is parallel; only decode is autoregressive-per-step. The distinction is really 'teacher-forced full-sequence vs autoregressive generation with KV-cache,' not 'parallel vs serial' per se.
  - Why it matters: Blurring prefill/decode is exactly the confusion that later bites when discussing latency, batching, and speculative decoding.
  - Test / fix: Split explicitly: 训练=teacher forcing 全序列；推理 prefill=并行处理已知上下文，decode=逐步自回归。KV-cache 是使 decode 可行的关键，值得点出。

- **LOW** — '指令跟随和工具调用的格式，正是对齐阶段显式教给模型的'
  - Issue: Overly strong attribution. Base models can follow some instructions zero-shot; tool-call format is largely SFT/chat-template artifacts, but 'explicitly taught' conflates format specification, SFT data, and RL. Also 'RLHF largely decides honesty/tool use' conflates preference optimization with capability.
  - Why it matters: Over-attributing behavior to alignment can mislead engineers about what fine-tuning can and cannot add (it shapes format/style more reliably than capability).
  - Test / fix: Downgrade to: 对齐阶段主要塑造格式、语气、拒答倾向；能力主体来自预训练，工具调用格式属于 SFT/模板约定。

- **LOW** — Exposure Bias 被用作推理错误被放大的解释
  - Issue: Exposure bias is a training/inference distribution mismatch concept from seq2seq; for LLMs with massive data the practical phenomenon is more 'error accumulation / compounding' than classical exposure bias. Conflating them is a mild definitional stretch.
  - Why it matters: The term is used loosely enough that a careful reader may object, weakening credibility of an otherwise careful section.
  - Test / fix: Use 'distribution shift between teacher-forced training and self-generated prefixes' and note error compounding as the observable, labeling exposure bias as the classical name.

## 2. Counterexamples

- **MEDIUM** — Thesis: Decoder-only 更适合开放域对话/指令跟随，Encoder-Decoder 仍常见于翻译/ASR
  - Counterexample: Several strong open models are not decoder-only (e.g., encoder-decoder or hybrid/MoE-with-encoder designs; T5-family scaling studies; some multimodal stacks use vision encoders + decoder). Also, decoder-only dominance is partly an ecosystem/serving/infra and scaling-law artifact, not purely a task-fit result.
  - Boundary: The claim is a correlation observed in one product era, not a law; hardware efficiency of a single stack, KV-cache maturity, and data availability confound it.

- **MEDIUM** — Thesis: '结构可以相同，但计算过程并不相同' 解释训练/推理差异
  - Counterexample: With chunked prefill, continuous batching, and speculative decoding, decode steps are batched and partially parallel; conversely training with sequence packing and gradient checkpointing is less 'free parallelism' than implied.
  - Boundary: The clean train/infer dichotomy holds pedagogically but breaks at the systems layer the author later cares about (runtime).

- **LOW** — Thesis: 长 Context 的信息利用不充分问题源于注意力机制本身
  - Counterexample: Retrieval-augmented pipelines with short contexts can also fail to use relevant passages; and models can attend to irrelevant tokens strongly. The failure is often data/instruction/prompt-organization, not attention capacity.
  - Boundary: Context Engineering value exists independent of window size; the article's causal link to Attention is weaker than stated.

## 3. Novelty

- **established** — 用 Mask 模式而非块名来解释 Encoder/Decoder 区别
  - Basis: Standard textbook/practitioner framing; widely stated in ML courses and blogs.

- **common_combination** — 预训练=并行 teacher forcing，推理=自回归；并行度是工程后果而非定义
  - Basis: Well-known distinction; the explicit 'parallelism is consequence not definition' framing is a useful pedagogical phrasing, not new theory.

- **common_combination** — 训练→参数→推理→真实结果 作为 Agent 理解基础（能力≠完成）
  - Basis: Common in agent-engineering writing; the author's distinctive move is connecting it forward to runtime/verification, which lives in the next article.

- **potentially_distinctive** — 把 Attention 关系计算与 Context Engineering 作为连续叙事
  - Basis: Preliminary (no browsing): the narrative stitching from mechanism to context engineering is a plausible author signature, but the underlying claims are individually established; novelty is in framing, not content.

## 4. Facts

- **HIGH** — 文章日期 2026-09-21，且 git diff 仅为 article-actions.js 版本号 bump
  - Why verify: Date is in the future relative to typical review; the diff shows no content change, so either the article body was already present or the change is purely cache-busting. Confirm the article text reviewed matches what is actually deployed.
  - Preferred source: `primary`

- **MEDIUM** — 'GPT、Qwen、DeepSeek 等生成式大模型很多采用 Decoder-only'
  - Why verify: True for the named chat models, but 'DeepSeek' spans MoE/MLA and reasoning variants; the claim is version-sensitive and should be dated.
  - Preferred source: `official`

- **MEDIUM** — RLHF 用偏好训练奖励模型 + PPO；DPO 不需单独奖励模型
  - Why verify: Accurate as of DPO's introduction, but the RL landscape has moved (GRPO, verifiable-reward RL, RLAIF). The article mentions verifiable-reward RL generally; specific algorithm attributions are time-sensitive.
  - Preferred source: `primary`

- **LOW** — Whisper 为 Encoder-Decoder；T5/BART 为 Encoder-Decoder
  - Why verify: Correct for current known versions, but model families evolve; treat as illustrative rather than canonical.
  - Preferred source: `official`

## 5. Missing Points

- **HIGH** — KV-cache 与 decode 的实际工程约束
  - Why it matters: Without it, the '推理逐步自回归' section omits why long context is expensive (memory grows with sequence × layers) — directly relevant to the Context Engineering thread and to why parallelism is an engineering consequence.

- **MEDIUM** — 为什么 decoder-only 在规模上更省/更统一（单栈训练、单一目标、serving 复用）
  - Why it matters: The article asserts decoder-only dominance but doesn't give the infra/scaling rationale, leaving 'mask 模式' as an incomplete explanation. A short 'simplicity + scaling + serving reuse' paragraph would close the loop.

- **MEDIUM** — SFT 与 RL 的能力边界（format vs capability）
  - Why it matters: The author's own later claim '能力≠完成' depends on distinguishing what alignment can teach. Without it, the alignment section overpromises.

- **LOW** — Tokenizer / positional encoding 省略说明
  - Why it matters: Readers may assume Attention alone explains token relations; subword tokenization and RoPE/ALiBi materially affect long-context behavior the article discusses.

## 6. Recommended Changes

- Add one sentence distinguishing mask from cross-attention/training-objective when defining Encoder vs Decoder.
- Split the train/infer section into prefill (parallel) vs decode (autoregressive) and introduce KV-cache as the enabling mechanism.
- Downgrade 'alignment explicitly teaches tool use' to a format/SFT/chat-template claim and mark capability attribution as hypothesis.
- In the long-context section, name at least one failure mechanism (attention sink / positional degradation / lost-in-the-middle) and label the Attention→Context Engineering link as a hypothesis.
- Explicitly mark the date and version sensitivity of model-family and RL-algorithm examples (DPO/PPO/GRPO).
- Confirm whether the reviewed body corresponds to the deployed file, since the diff is only a cache-busting script version bump.

Evidence level: `E1`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
