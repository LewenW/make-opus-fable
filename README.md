# make-opus-fable

让 Opus 4.8 在**工作纪律和审计广度**上更像 Fable 5 —— 一套行为/编排 skill,把 Fable 训练出来的习惯翻译成 Opus 可执行的显式流程 + 结构。每条设计都有实证出处(八批评测,见 `evals/`)。

## 一条命令安装

```bash
git clone https://github.com/LewenW/make-opus-fable.git
cd make-opus-fable
bash install.sh
```

装完**开一个新 Claude Code 会话**即生效。试试:`/deep-audit` 审仓库找 bug、`/verify-before-done` 交付前自检。

- `bash install.sh --with-hooks` —— 额外装确定性触发 hook(让 deep-audit 更可靠地自动触发)
- `bash install.sh --uninstall` —— 一键卸载(用清晰标记块管理 CLAUDE.md,绝不动你原有内容)
- 装什么:4 个 skill → `~/.claude/skills/`、verifier subagent → `~/.claude/agents/`、行为纪律块追加进 `~/.claude/CLAUDE.md`(带 `make-opus-fable` 标记,可移除)。幂等,重装安全。

## 它有用在哪(诚实版)

- ✅ **行为纪律**(verify-before-done / 常驻核):盲测 15胜2负——诚实汇报、不瞎说、范围克制、不编造。
- ✅ **审计广度**(deep-audit):`effort=xhigh` + 每文件扇出,缺陷召回从裸 Opus 5.5 提到 7/10(弥合约 43%),依从性 5/5 可自主触发。真实代码上一次挖出 10 个 bug。
- ❌ **不注入能力**:感知(读图)、知识密度、微妙契约违反的召回——这些是训练进去的,skill 补不了。真实代码同协议头对头 Opus 7/9 vs Fable 9/9,拉近但不平。

**一句话:skill 有用于"行为"与"结构"轴,无用于注入"能力"。** 全部证据(含被证伪的结论)在 `evals/HARDBENCH.md`。

---

## 原始说明

✅ **已盲测三轮 + Fable 迭代两版**(2026-07-04):终版战绩 **15胜2负0平**(17 个不同埋雷任务,双臂均为 Opus 4.8,盲评,全过程含败绩见 `evals/RESULTS.md`)。当前版本:verify-before-done **v3**、CLAUDE-core **v2**、其余 v1。
⚠️ 仍未验证的部分:全部测试为**短单轮任务**——长视野多步任务(套件的核心目标场景)需要多轮 harness,尚未测。两场遗留败仗(均为排雷满分后的窄幅 tiebreak)如实保留在战绩里。

## 目录

```
skills/
  long-horizon-protocol/SKILL.md   # 长任务协议:需求合并→计划门→切片执行→状态检查点
  verify-before-done/SKILL.md      # 完成前验证:证据审计→对抗五连问→verdict;findings 进交付物、过程不进
  memory-discipline/SKILL.md       # 记忆纪律:写什么/怎么写/召回前验一手
agents/
  verifier.md                      # fresh-context 对抗验证 subagent(@verifier 点名 = 保证执行)
config/
  CLAUDE-core.md                   # 常驻行为核(拷进 ~/.claude/CLAUDE.md;~40 行,刻意压缩)
  settings-snippets.md             # 配置杠杆:thinking/effort/hooks/API 参数(4 个维度用配置补,不用 prompt)
evals/
  eval-plan.md                     # 12 个种子任务 + 盲测协议(奖励信号=盲测通过率,梯度=改 skill 文本)
  RESULTS.md                       # 三轮盲测完整战绩与迭代史(15-2-0;含全部败绩、诊断、教训、限制)
  HARDBENCH.md                     # 三臂客观评测四批:可自测任务 0 差距;视觉/缺陷召回有差距(文字 skill 补 0-14%);**xhigh+扇出编排把缺陷召回补到 10/10 超过 Fable**——真路径是结构+算力,不是文字
skills/deep-audit/SKILL.md         # 编排型 skill:effort xhigh(frontmatter)+ 每文件扇出 reviewer + 去重复核。实测把缺陷召回 5.5→10/10。RECALL 型审计用
hooks/
  deep-audit-trigger.py            # 确定性兜底:多文件审计意图必触发扇出(skill 描述会 under-fire)。已自测
  settings-hook.json               # 合并进 settings.json 的 hook 配置
  README.md                        # hook 安装说明
reference/
  anthropic-prompt-fragments/      # Anthropic 官方 prompt 碎片原文(Fable 专属 steering + lean 核心)
  iwoszapar-rigor-pack-6-skills.md # 直接先例的 6 个 skill 全文(已盲测 12-0-2;署名 Iwo Szapar,仅作参考)
  iwoszapar-benchmark-report.txt   # 其盲测完整报告(任务、雷点、评分口径、迭代史——含全部败绩)
调研报告-Fable行为移植Opus.md      # 核心交付:证据、修正、天花板、设计依据
```

## 安装(3 步)

```bash
# 1. skills(用户级;也可放进某个项目的 .claude/skills/)
cp -r skills/* ~/.claude/skills/

# 2. verifier subagent
mkdir -p ~/.claude/agents && cp agents/verifier.md ~/.claude/agents/

# 3. 常驻核:把 config/CLAUDE-core.md 的 "## Working discipline" 一节
#    手动合并进 ~/.claude/CLAUDE.md(与你现有四节不冲突,建议追加在最前——primacy 效应)
```

配置项(可选但推荐):按 `config/settings-snippets.md` 检查 `alwaysThinkingEnabled` / `effortLevel`,长任务开 ultracode,高危命令保持 ask 规则。

## 使用要点

- skill 自动触发不可靠(官方已知 under-trigger),重要任务直接 `/long-horizon-protocol`、交付前 `/verify-before-done`、点名 `@verifier` 复核。
- 有可判定验收标准的任务,用 `/goal <标准>` 把"没验证不许收工"变成硬约束。
- 短小任务别上流程——每个 skill 都留了 trivial 逃生口,税感明显时说明触发范围该收窄。
- **三臂实测结论(HARDBENCH.md)**:分钟级、能自测的编码任务,裸 Opus 4.8 = Fable 5 = 100%,套件对正确率零增益——这类活直接用 Opus,省下 Fable 配额;套件价值在行为质量(盲测维度)与长任务(未测,文献支撑)。

## 下一步(建议顺序)

1. ~~盲测~~ ✅ 已完成三轮(见 `evals/RESULTS.md`);~~Fable 迭代~~ ✅ v2/v3 均由 Fable 5 依据败绩诊断改写。
2. **长任务组评测**(eval-plan 种子 7-12:多轮追加需求、中断恢复、计划外惊喜)——套件核心价值场景,需多轮 harness,未测。
3. 头号悬案实验:`CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=0` 灌回 legacy 长提示 vs 本套件 A/B(任务集现成)。
