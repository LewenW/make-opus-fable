# make-opus-fable

**让 Opus 4.8 在纪律、审计广度和 quant 判断上更像 Fable 5** —— 一套行为/编排 skill,把 Fable 训练出来的习惯翻译成 Opus 可执行的显式流程 + 结构。每条设计都有实证出处(13 批三臂客观评测,见 [`evals/HARDBENCH.md`](evals/HARDBENCH.md)),包括被证伪的结论。

---

## ⚡ 一条命令安装

```bash
git clone https://github.com/LewenW/make-opus-fable.git
cd make-opus-fable && bash install.sh
```

装完**开一个新的 Claude Code 会话**即生效。马上试:

```
/verify-before-done      # 交付前自检,把「看着对但其实错」挡下来
/deep-audit              # 审整个仓库找 bug(扇出 + xhigh,买召回)
/quant-thesis            # 从凌乱的上游信号预测下游数字
```

| 命令 | 作用 |
|---|---|
| `bash install.sh` | 装 6 个 skill + verifier subagent + 行为纪律块 |
| `bash install.sh --with-hooks` | 额外装确定性触发 hook(让 deep-audit 更可靠自动触发) |
| `bash install.sh --uninstall` | 一键卸载(用标记块管理 CLAUDE.md,**绝不动你原有内容**) |

幂等,重装安全。装到用户级 `~/.claude/`(skill、agent),行为纪律以带 `make-opus-fable` 标记的块**追加**进 `~/.claude/CLAUDE.md`。

---

## 🎯 什么时候真用得上(诚实版)

跑了 13 批评测,一手确认能**真正拉开** Opus 和 Fable 的场景**只有三处**,套件都量化了弥合率;其余绝大多数日常任务两模型**没差别**,套件也无从帮起(本就满分)。

| 场景 | Opus vs Fable | 套件补得动吗 |
|---|---|---|
| 分钟级/可自测编码、终端修复、指令遵循、检索、知识问答 | **没差别**(都满分) | 无需补 —— 这类活直接用 Opus,省 Fable 配额 |
| **行为质量**(诚实汇报 / 不编造 / 范围克制) | Fable 训练得更稳 | ✅ **有效**(盲测 15 胜 2 负) |
| **穷举缺陷召回**(审计找全每个 bug) | Fable 召回更高 | ✅ **弥合 ~43%**(`deep-audit`:xhigh + 每文件扇出) |
| **quant 论点/预测**(凌乱数据下形成判断) | Fable 明显更强 | ✅ **弥合 ~86%**(`quant-thesis` 技术反射协议) |
| 视觉读图 / 纯知识密度 | Fable 更强 | ❌ **补不了**(感知/能力,训练进去的) |

**一句话:套件有用于「行为纪律」「审计结构」「quant 反射」三轴,无用于注入「感知/知识」能力。** 差距结构性地活在「难 / 开放 / 长视野」的任务带里 —— 清晰单轮任务上两模型永远打平,所以补起来的地方也只在那几个真会拉开的轴上。

---

## 🧩 六个 skill(各管什么、何时触发)

安装后每个 skill 都可用 `/<名字>` 手动触发,也会按 `description` 自动触发(官方已知 skill 会 under-trigger,重要任务建议手动点名)。

| Skill | 什么时候用 | 干什么 |
|---|---|---|
| **verify-before-done** | 宣称任何实质工作「完成/修好/通过」之前 | 证据审计 → 对抗五连问 → 只把 findings 放进交付物、过程叙述不放。杀「看着对但其实错」 |
| **deep-audit** | 目标是**找全**缺陷:多文件预合并审计、「审这个模块找 bug」、回归/安全排查 | 枚举文件 → 每文件一个 fresh `xhigh` reviewer 并行 → 并集去重复核。用 token 和时间换召回 |
| **quant-thesis** | 从上游信号预测下游数字:「X 对 Y 意味着什么」「营收会不会加速」「read-through」 | 显式亮分解算术、过手率带系数、给数字区间、两档信心(方向 vs 量级)、查基数/stock-flow |
| **judgment** | 交付物是**决策/设计/评估**而非改代码:「该选 X 还是 Y」「这设计合理吗」 | 先评估后动手、先给结论+唯一权衡、跑盲点扫描、没达成一致不实现 |
| **long-horizon-protocol** | 跨多文件/多步/多会话:重构、迁移、整功能、跨模块调试、长研究 | 需求合并 → 计划门 → 切成 ≤1h 单元 → 状态检查点,别丢线头 |
| **memory-discipline** | 读写跨会话记忆:CLAUDE.md、进度笔记、经验账本 | 写什么/怎么写/召回前先验一手,别把假设当事实带进未来会话 |

外加 `agents/verifier.md` —— fresh-context 对抗验证 subagent,大改高危时 `@verifier` 点名保证执行(比自检强)。

---

## 🛠 怎么用

- **自动触发不完全可靠**(官方已知)。重要任务直接手动:`/long-horizon-protocol`、交付前 `/verify-before-done`、点名 `@verifier` 复核。
- **短小任务别上流程** —— 每个 skill 都留了 trivial 逃生口;税感明显时说明触发范围该收窄。
- **token 档位**(实测量级):generation / judgment / 日常 ≈ **1×**;long-horizon ≈ 1.2–1.5×;**deep-audit 扇出 ≈ 4–5×**(唯一大头,只在主动要审计级召回时才付)。
- **quant / 审计要发挥,配 `effort=xhigh`**(deep-audit 的 frontmatter 已内置)。

---

## 📊 证据

全部结论(含被 held-out 打回的错误结论)在 [`evals/HARDBENCH.md`](evals/HARDBENCH.md),13 批三臂客观评测(裸 Opus / Opus+套件 / Fable),隐藏测试/磁盘/Python/盲配对面板打分。要点:

- **可自测编码 6 任务**:三臂全 100%,0 差距 —— 清晰单轮任务两模型不分。
- **缺陷召回**:裸 Opus 5.5/10 → xhigh+扇出补到超 Fable;真实代码同协议头对头 Opus 7/9 vs Fable 9/9(拉近不平)。
- **quant 论点**(n=11 盲配对面板):裸 Opus 票级输 Fable 6:27 → `quant-thesis` 补到 15:18 近平手(**弥合 86%**)。
- **四能力轴补测**(终端 agentic / 超量指令遵循@85约束 / 长上下文多跳 / 知识密度):四轴全部三臂零分离,全天花板。
- **真实世界**:对一个生产仓库全量扇出审计,一次挖出 1 critical + 8 high 全为真([`evals/AUDIT-PARALLAX.md`](evals/AUDIT-PARALLAX.md))。

---

## 📁 目录

```
skills/
  verify-before-done/SKILL.md      # 完成前验证:证据审计→对抗五连问→findings进交付物、过程不进
  deep-audit/SKILL.md              # 扇出审计:effort xhigh(frontmatter)+每文件reviewer+去重复核。RECALL型
  quant-thesis/SKILL.md            # quant 反射:分解亮算术/过手率带系数/数字区间/两档信心
  judgment/SKILL.md                # 决策/设计:先评估后动手、先给结论+唯一权衡、盲点扫描
  long-horizon-protocol/SKILL.md   # 长任务:需求合并→计划门→切片→检查点
  memory-discipline/SKILL.md       # 记忆纪律:写什么/怎么写/召回前验一手
agents/
  verifier.md                      # fresh-context 对抗验证 subagent(@verifier 点名=保证执行)
config/
  CLAUDE-core.md                   # 常驻行为核 + 任务路由器(装进 ~/.claude/CLAUDE.md;含 5 种 mode 分类)
  settings-snippets.md             # 配置杠杆:thinking/effort/hooks/API 参数
hooks/
  deep-audit-trigger.py            # 确定性兜底:多文件审计意图必触发扇出(skill 会 under-fire)
  settings-hook.json               # 合并进 settings.json 的 hook 配置
  README.md                        # hook 安装说明
evals/
  HARDBENCH.md                     # 13 批三臂客观评测(核心证据;含被证伪结论)
  RESULTS.md                       # 三轮盲测完整战绩与迭代史(15-2-0;含全部败绩、诊断、教训)
  AUDIT-PARALLAX.md                # 对生产仓库全量扇出审计报告(1 critical + 8 high 全为真)
  eval-plan.md / NEXT-BATTERY.md   # 评测协议与未跑批次
reference/                         # Anthropic 官方 prompt 碎片 + 先例 skill 包(第三方,仅参考)
调研报告-Fable行为移植Opus.md       # 核心调研:证据、修正、天花板、设计依据
```

---

## ❓ FAQ

**会拖累简单任务吗?** 不会。每个 skill 有 trivial 逃生口,generation/judgment/日常开销 ≈ 1×。实测:分钟级可自测任务上套件对正确率零增益也零拖累。

**会动我现有的 CLAUDE.md 吗?** 不会。行为纪律以带 `make-opus-fable` 标记的块**追加**,`--uninstall` 精确移除该块,你原有内容分毫不动。

**装在哪?** 用户级 `~/.claude/`(skill/agent)。也可把 `skills/*` 拷进某个项目的 `.claude/skills/` 只对该项目生效。

**这能让 Opus 变成 Fable 吗?** 不能,诚实讲。它让 Opus 在三个真会拉开的轴上「够用地逼近」Fable(quant 86% / 召回 43% / 行为纪律有效),但拉不平 —— 感知和纯知识是训练进去的,任何 prompt 都补不了。

---

## 卸载

```bash
bash install.sh --uninstall
```
