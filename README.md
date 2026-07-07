<div align="center">

# 🜂 make-opus-fable

**Translate Fable 5's trained-in work habits into explicit process + structure Opus 4.8 can execute.**
*Turn Claude Opus 4.8 into a more Fable-like operator — with discipline, audit breadth, and quant reflexes it wasn't trained to reach for.*

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![For Claude Code](https://img.shields.io/badge/for-Claude%20Code-8A2BE2.svg)](https://claude.com/claude-code)
[![Model: Opus 4.8](https://img.shields.io/badge/model-Opus%204.8-1f6feb.svg)](#)
[![Skills: 6](https://img.shields.io/badge/skills-6-informational.svg)](#-six-skills)
[![Evidence: 13 batches](https://img.shields.io/badge/evals-13%20batches-orange.svg)](evals/HARDBENCH.md)

An **evidence-backed** suite of behavior / orchestration skills, built on the most exhaustive public Opus↔Fable eval sweep we're aware of — 13 batches of objective three-arm testing (bare Opus / Opus+suite / Fable) across nearly every axis that could conceivably separate them, **including conclusions our own held-out testing later overturned**. The result: near-total parity everywhere, and this suite closes most of what's left.

</div>

---

## ⚡ One-command install

```bash
git clone https://github.com/LewenW/make-opus-fable.git
cd make-opus-fable && bash install.sh
```

**Start a new Claude Code session** for it to take effect. Try it right away:

```text
/verify-before-done      pre-flight check before declaring anything done — catches "looks right but isn't"
/deep-audit              audit a whole repo for bugs (per-file fan-out reviewers + xhigh, buys recall)
/quant-thesis            forecast a downstream number from messy upstream signals, with shown arithmetic and two-tier conviction
```

| Command | What it does |
| :-- | :-- |
| `bash install.sh` | Installs 6 skills + the `verifier` subagent + the behavior discipline block |
| `bash install.sh --with-hooks` | Also installs two deterministic hooks: the audit trigger (makes `deep-audit` fire more reliably) and `verify-after-edit` (runs your project's tests after every code edit) |
| `bash install.sh --uninstall` | One-command removal (manages `CLAUDE.md` via a marked block, **never touches your existing content**) |

> Idempotent, safe to re-run. Installs to the user-level `~/.claude/`; the behavior core is **appended** to `~/.claude/CLAUDE.md` inside a block marked `make-opus-fable`, and precisely removed on uninstall. Tested end to end: install → reinstall → uninstall leaves your original content untouched.

---

## 🎯 How comprehensive is this, really?

We didn't guess where Opus might lag Fable — we swept for it. **13 batches of three-arm evals** (bare Opus / Opus+suite / Fable) covered nearly every axis we could think of: self-checkable coding, terminal-agentic repair, instruction-following (up to 85 concurrent constraints), long-context multi-hop retrieval, knowledge density, honesty under missing context, financial calculation, quant forecasting, judgment calls, and exhaustive code audits.

**The result across that whole sweep: near-total parity.** On coding, terminal repair, instruction-following, retrieval, knowledge, and financial calculation, the two models are indistinguishable — both already at ceiling — and the suite's discipline layer holds Opus at that same ceiling with no drag. The only places a real, measured gap showed up were three axes, and this suite closes most of what's closable:

| Axis | Gap before the suite | With the suite |
| :-- | :-- | :-- |
| **Quant thesis / forecasting** (forming a call from messy data) | Opus lost the vote 6:27 | ✅ **15:18 — 86% of the gap closed** (`quant-thesis`) |
| **Exhaustive defect recall** (finding every bug in an audit) | Opus 5.5/10 | ✅ **~43% closed**, near Fable on real production code (`deep-audit`) |
| **Behavioral discipline** (honest reporting / no fabrication / scope control) | Fable more consistent | ✅ **Effectively closed** (blind eval: 15 wins, 2 losses) |
| Visual perception / raw knowledge density | Fable stronger | ❌ Not closeable by any suite — baked into model weights |

That's the whole picture: an exhaustive, evidence-first sweep, near-total parity everywhere a clean task lets the two models compete fairly, and full transparency about the one place (perception) that no amount of structure or prompting can fix. We looked — there's no comparably broad, held-out-validated Opus↔Fable eval sweep we're aware of in any public skill suite. What we won't do is claim to be "the closest to Fable on the market": we haven't run a head-to-head against every other project out there, and we'd rather under-claim than repeat the mistake this suite's own eval history caught and corrected (see [`evals/HARDBENCH.md`](evals/HARDBENCH.md) — an earlier "beats Fable" claim from batch 4 was overturned by held-out testing in batch 6).

---

## 🧩 Six skills

Once installed, each can be triggered manually with `/<name>`, or automatically based on its `description` (skills are known to under-trigger — **manual invocation is recommended for anything that matters**).

| Skill | When to use it | What it does |
| :-- | :-- | :-- |
| 🔍 **verify-before-done** | Before declaring any substantive work "done / fixed / passing" | Evidence audit → adversarial five-point pass → only findings go into the deliverable, never the process narration. Kills "looks right but isn't" |
| 🗂 **deep-audit** | The goal is to find **every** defect: pre-merge multi-file audits, "review this module for bugs", regression / security passes | Enumerate files → one fresh `xhigh` reviewer per file, in parallel → union, then de-dupe and re-verify. Trades tokens and wall-clock for coverage |
| 📈 **quant-thesis** | Forecasting a downstream number from upstream signals: "what does X imply for Y", "will revenue accelerate", "read-through" | Shows the decomposition arithmetic explicitly, sizes pass-through with coefficients, gives a numbered band, splits conviction into direction vs. magnitude, checks base effects / stock-vs-flow |
| ⚖️ **judgment** | The deliverable is a **decision / design / assessment**, not an edit: "should we do X or Y", "is this design sound" | Assess before editing, lead with the call plus its one real tradeoff, run a blindspot pass, don't implement until agreed |
| 🧭 **long-horizon-protocol** | Spans multiple files / steps / sessions: refactors, migrations, whole features, cross-module debugging, long research | Consolidate requirements → plan-gate → slice into ≤1h units → checkpoint state, don't lose the thread |
| 🧠 **memory-discipline** | Reading or writing cross-session memory: `CLAUDE.md`, progress notes, lesson ledgers | What to write / how to write it / verify before recalling — never carry an assumption into a future session as if it were fact |

> Plus `agents/verifier.md` — a fresh-context adversarial verification subagent. Invoke `@verifier` by name on high-stakes changes to guarantee the check actually runs (stronger than self-review).

---

## 🔬 Why it works (the mechanism, in one line)

The gap isn't that Opus "can't" — it's that it **hasn't built the reflex**.

- **Auditing**: Opus can find bugs, but doesn't reach for **exhaustively enumerating every file** on its own. → `deep-audit` uses fan-out orchestration to turn "breadth" into N in-window units — recall climbs from 5.5/10 on bare Opus to near Fable.
- **Quant**: Opus can compute `1.14 / 1.08`, but doesn't reach for **showing the decomposition** on its own. → `quant-thesis` codifies Fable's technique reflexes into a protocol, closing 86% of the vote-level gap.
- **Capability axes** (vision / knowledge): these are baked into the weights, and **no prompt can add them** — the suite is honest that it can't help here.

So the levers that actually work are **configuration (effort) + structure (fan-out orchestration) + targeted reflex protocols** — not "writing a smarter prompt." Plain-text skills, tested against held-out cases, repeatedly close **0%** of the capability-axis gap.

---

## 📊 Evidence

Every conclusion (including the ones held-out testing overturned) lives in **[`evals/HARDBENCH.md`](evals/HARDBENCH.md)** — 13 batches of objective three-arm evals, graded by hidden tests, on-disk state, Python, or blind pairwise panels. Highlights:

- **6 self-checkable coding tasks** → all three arms hit 100%, zero gap (clean single-turn tasks never separate the two models).
- **Defect recall** → bare Opus 5.5/10; xhigh + fan-out closes most of the gap; on real production code under the same protocol, head-to-head: **Opus 7/9 vs. Fable 9/9** (closer, not closed).
- **Quant thesis** (n=11, blind pairwise panel) → bare Opus loses to Fable **6:27** on votes → `quant-thesis` closes it to **15:18**, nearly even (**86% closed**).
- **Four capability-axis follow-ups** (terminal agentic / instruction-following at 85 concurrent constraints / long-context multi-hop / knowledge density) → all four axes show **zero separation** across all three arms — every one at ceiling.
- **Real-world validation** → a full fan-out audit of a production repo surfaced **1 critical + 8 high-severity bugs, all confirmed real** ([`evals/AUDIT-PARALLAX.md`](evals/AUDIT-PARALLAX.md)).

---

## 🛠 Usage notes

- **Auto-triggering isn't fully reliable** (a known Anthropic limitation). For anything that matters, invoke manually: `/long-horizon-protocol`, `/verify-before-done` before declaring done, `@verifier` for review.
- **Don't apply process to small tasks** — every skill has a trivial-task escape hatch; if the overhead feels noticeable, that's a sign the trigger scope should be narrowed.
- **Token cost tiers** (measured): generation / judgment / everyday work ≈ **1×**; long-horizon ≈ 1.2–1.5×; `deep-audit` fan-out ≈ **4–5×** (the one real cost center — only pay it when you actually want audit-grade recall).
- **For quant / audit work, pair with `effort=xhigh`** (already built into `deep-audit`'s frontmatter).

---

## 📁 Layout

```text
skills/
  verify-before-done/     pre-done check: evidence audit → adversarial pass → findings in, process out
  deep-audit/             fan-out audit: effort xhigh (frontmatter) + per-file reviewer + de-dupe re-verify
  quant-thesis/           quant reflexes: show decomposition arithmetic / sized pass-through / numbered bands / two-tier conviction
  judgment/               decisions/design: assess before editing, lead with the call + one tradeoff, blindspot pass
  long-horizon-protocol/  long tasks: consolidate requirements → plan-gate → slice → checkpoint
  memory-discipline/      memory hygiene: what/how to write, verify before recalling
agents/verifier.md        fresh-context adversarial verification subagent (@verifier = guaranteed execution)
config/
  CLAUDE-core.md          persistent behavior core + task router (install into ~/.claude/CLAUDE.md; 5 modes)
  settings-snippets.md    config levers: thinking / effort / hooks / API parameters
hooks/                    deterministic backstops (fire regardless of what the model remembers)
  deep-audit-trigger.py   UserPromptSubmit: multi-file audit intent always triggers the fan-out
  verify-after-edit.py    PostToolUse: runs the project's tests after every code edit (mechanizes verify-before-done)
evals/
  HARDBENCH.md            13 batches of objective three-arm evals (core evidence; includes overturned conclusions)
  RESULTS.md              full blind-eval track record and iteration history (15-2-0; includes every loss, diagnosis, lesson)
  AUDIT-PARALLAX.md        full fan-out audit report on a production repo (1 critical + 8 high, all confirmed real)
install.sh                one-command install / uninstall (idempotent, reversible)
```

---

## ❓ FAQ

<details>
<summary><b>Will it slow down simple tasks?</b></summary>

No. Every skill has a trivial-task escape hatch; generation / judgment / everyday overhead ≈ 1×. Measured: on minute-scale, self-checkable tasks, the suite adds zero accuracy gain and zero drag.
</details>

<details>
<summary><b>Will it touch my existing CLAUDE.md?</b></summary>

No. The behavior core is **appended** inside a block marked `make-opus-fable`; `--uninstall` removes exactly that block, leaving your original content untouched. Verified by testing.
</details>

<details>
<summary><b>Where does it install? Can it be project-scoped?</b></summary>

By default it installs to the user-level `~/.claude/` (global). To scope it to one project, copy `skills/*` into that project's `.claude/skills/` instead.
</details>

<details>
<summary><b>Does this turn Opus into Fable?</b></summary>

No — honestly. It gets Opus "close enough" to Fable on the three axes where a real gap exists (quant 86% / recall 43% / behavioral discipline effective), but it doesn't fully close the gap — perception and raw knowledge are baked into training, and no prompt fixes that. Arguably the most valuable part of this project isn't the skills themselves, but the **rigorous, self-skeptical eval discipline** behind them (held-out validation, isolated variables, objective oracles, spot-checking).
</details>

---

<div align="center">

**Uninstall** · `bash install.sh --uninstall`

Built with honest evals. MIT licensed.

</div>
