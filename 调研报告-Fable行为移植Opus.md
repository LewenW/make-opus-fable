# Fable 5 → Opus 4.8 行为移植:深度调研报告 + Skill 套件设计依据

> 生成:2026-07-04。前置文档:《对话记忆转移文档:Fable 5 vs Opus 4.8 差距分析与 Skill 补齐方案》(本报告是它的深化、修正与落地)。
> 调研方式:7 条并行调研线,每条线配一个独立对抗核查 agent(要求亲自打开一手来源、亲自跑 git diff / 亲自解析 PDF / 亲自下载二进制复核),最后 completeness critic 补漏。共 15 个 agent、463 次工具调用。
> 证据等级标注:【核】= 对抗核查 agent 在一手来源逐字复核通过;【单】= 单一来源(通常是可靠媒体或自述);【推】= 合理推断,无直接来源。

---

## 0. TL;DR(五句话)

1. **Anthropic 自己就在做你想做的事,而且是双向的**:Claude Code 按模型下发不同系统提示(逆向官方二进制证实),给旧模型多发 2,700 token 的程序性指令、给新模型只发 385 token;还给 Opus 4.7 单独发过"先调查再提问"的补偿补丁——"把训练产出翻译成显式指令"是 Anthropic 的内部常规操作,你的项目方向被官方实践直接背书。【核】
2. **最高权威的"翻译文本"已经存在**:官方《Prompting Claude Fable 5》页面就是 Anthropic 把 Fable 训练行为写成逐字指令块的对照表,其中"进度审计"一条官方实测"几乎消除虚构状态报告"。社区所有 "Fable port" skill 基本都是它的转写。【核】
3. **先例已有测量结果**:六个"Fable 纪律" skill 在 Opus 4.8 上盲测 12胜0负2平(小样本、自发布、LLM 评审),token 开销 ~7%;但初版有两个 skill 全输——输在"把验证过程碎碎念进交付物"。hooks 硬执行路线实测 +2/38(噪音水平)、2-3 倍 token。**skill 改的是"性格",不是"能力"。**【核】
4. **能补与不能补的边界已定量**:脚手架/skill 能在流程可靠性维度抹平约一个模型档位(Sonnet4.5+强脚手架 52.7% > Opus4.5+官方脚手架 52.0%,SWE-Bench-Pro【核】);但组合深度、原生推理、知识密度有硬上限(见 §5),且 skill 本身受指令密度约束——前沿模型 ~100-150 条并发指令后遵循率开始掉【核】。
5. **有四个维度根本不用写 prompt,配置就能补**:adaptive thinking(Opus 4.8 同机制,默认已开)、工具间思考(自动)、长跑基础设施(compaction/context-editing/task-budgets/memory tool 全部支持 Opus 4.8)、ultracode 编排(Opus 4.8 独有,Fable 反而没有)。skill 只需要负责剩下两个:自验证倾向、委派积极性。【核】

---

## 1. 对你原文档的修正与确认(逐条核查结果)

你原文档 §2 的数字表逐条核查后:**大部分确认,四处需要修正,一处有重要 nuance**。

| 原文档条目 | 核查结论 |
|---|---|
| SWE-bench Verified 95.0 vs 88.6 | ✅ 确认,且 95.0 有独立复现(vals.ai)【核】 |
| SWE-bench Pro 80.0–80.3 vs 69.2 | ✅ 确认,但 80.3 是 Anthropic 自家脚手架跑的,已被第三方标记"待独立复测"【核】 |
| FrontierCode Diamond 29.3 vs 13.4 | ✅ 确认【核】 |
| GDPval-AA 1932 vs 1890(+42) | ⚠️ 那是发布时快照;当前 AA v2 榜单是 **1759 vs 1598(+161)**,两代 Elo 池不可混用,引用必须带日期【核】 |
| AA-Omniscience +12.6~12.7 | ≈ 确认(现榜整数 40 vs 27,即 +13)【核】 |
| **Terminal-Bench +5.3** | ❌ **修正:+5.3 是 Mythos 5(无分类器)对 Opus 的差距。实际部署的 Fable 5 因 20.9% 的试次触发安全回落,只领先 +1.6~+2.5**。安全税显著压缩终端类任务优势【核】 |
| 多模态 92.4 vs 76.1 | ✅ 数字确认,但注明它是 BenchLM 聚合器的类别均值,非官方口径【核】 |
| 幻觉更高 | ✅ 确认且拿到一手数字:system card §6.3.3.4,missing-reference 集 Mythos 82% vs Opus 4.8 91% 非幻觉率(即 **18% vs 9%**)——这是唯一一项 Fable 输给 Opus 4.8 的诚实性测评。根因:更倾向"硬答"而非"说不知道"【核,PDF 原文】 |
| 定价 $10/$50 vs $5/$25 | ✅ 确认(Anthropic 一手)【核】 |
| 延迟 | ✅ 确认且有具体数:TTFT 178s(Fable max effort)vs 18s(Opus)。**但反转数据**:312 个真实 PR 任务中,Fable 单任务中位墙钟 64s < Opus 87s——单轮慢、整活快,因为纠错轮次少。这正是"流程可靠性"论点的最好证据【核】 |
| Every "Senior Engineer" 91/100 | ✅ 确认,补全:Opus 4.8 = 63、GPT-5.5 = 62。91 vs 63 的 28 分差 vs SWE-bench 的 6.4 分差 = "任务越长差距越大"的最干净量化【核】 |
| "Fable low ≈ Opus xhigh"(原文档标"未经证实") | ✅ **已证实且拿到一手图表**:system card p.254 图 8.2.A,SWE-bench Pro 上 Mythos 5 low = **75.0** > Opus 4.8 xhigh = **68.6**。注意:图是 Mythos 配置(公开 Fable 同权重,80.0 vs 80.3,可近似迁移);无独立复现,全部社区引用都回溯到这张图【核,读图原件】 |
| METR | 原文档没有;补充:**METR 未测过 Opus 4.8 / Fable 5**。Opus 4.6 p50 ≈ 12h(不是媒体说的 14.5h)、p80 只有 **70 分钟**;Opus 4.5 p50=4h53m、p80=49min。2025+ 模型 p50/p80 比值中位数 **5.15**【核,原始 YAML 复算】 |

**由 METR 数据导出的可执行规则**(写进了 long-horizon-protocol skill):要 80% 一次通过率,子任务要切到 p50 视野的 ~1/5——对 Opus 级就是 **≤1 小时人类等效工作量/子任务**。这把你原文档模块 7 的"超过 N 步就拆"变成了有出处的定量规则。

---

## 2. 最大新发现:Claude Code 的按模型双提示机制(项目前提的关键修正)

调研 agent 反编译了官方 npm 二进制(@anthropic-ai/claude-code-darwin-arm64@2.1.201),对抗核查 agent 自己重新下载并逐字节复核通过:【核】

- Claude Code 内部有一个 **lean/legacy 提示门**(`Pg(model)`):`claude-3-*`、haiku、sonnet、opus-4-0~4-7 走 **legacy 长提示**;**Fable 5、Mythos 5、Opus 4.8** 及带 `lean_prompt` 能力旗标的模型走 **lean 短提示**。
- 静态行为核:legacy ≈ **2,689 token** → lean ≈ **385 token**,**-85.7%**(Shihipar 说的 "80%" 与此吻合;第三方 TwelveTables 抓包 diff 是按字节算的 -66%,分母不同)。工具描述同步瘦身:TodoWrite 2,037→108 token(-95%),few-shot 例子全部删除。
- **Fable 拿到的不是"更少",是"不同"**:带 `fable_5_mitigations` 旗标的模型在 lean 基础上**额外**收到三段专属 steering——599 token 的"Outcome-first 沟通"、301 token 的"自主运行守则"(含"结束回合前检查最后一段是不是承诺"、"改状态命令前核对证据")、177 token 的身份段。
- **官方补偿补丁先例**:`claude-opus-4-7` 独享一段 "investigate before asking" 补丁(有专属 env 开关);这证明"给旧模型写显式指令补新模型的训练行为"就是 Anthropic 的内部工程手段。
- 可用的实验开关:`CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=0/1` 可对任意模型强制 legacy/lean 提示——**这给了你一个现成的 A/B 实验台**。

**对项目前提的修正**:你原文档(和我最初的假设)认为"被删掉的 2,700 token = Fable 内化的行为 = Opus skill 的原材料"。但二进制证明 **Opus 4.8 也走 lean 路线**——Anthropic 认为 Opus 4.8 同样不需要那些 boilerplate。所以:

1. **主料不是 legacy 语料**,而是 (a) Fable 专属的三段 mitigations(Anthropic 判断 Opus 4.8 不需要、但那是按"交互式短任务"场景判断的;**长任务场景下它们正是 Opus 缺的东西**)+ (b) 官方迁移指南里所有标 [TUNE] 的补偿指令(搜索欲、委派欲、记忆欲、验证提醒——官方明说 Fable "Skip the verification reminders",反推 Opus 要 KEEP)+ (c) 实测有效的纪律类规则(埋雷盲测赢的那些)。
2. legacy 语料里**只选择性回收**验证/范围纪律类条目(如 "browser 里跑过才算 UI 完成"、"区分 verified vs assumed")——这些恰好也是 iwoszapar 盲测里赢的方向。
3. "legacy 全量灌回对 Opus 4.8 是否有益"是 critic 标记的**头号未决实验**,已写进 eval-plan(用 `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT` 做 A/B)。

---

## 3. 行为翻译的"官方标准答案"及其证据链

三层互相独立的证据说明该写什么:

**第一层:官方 prompting 指南(最高权威翻译)。** 《Prompting Claude Fable 5》整页 = "Fable 行为 → 逐字指令块"对照表。最重要的一块,官方带实测结论:

> "Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly." — **In Anthropic's testing, this nearly eliminated fabricated status reports even on tasks designed to elicit them.**【核】

**第二层:system card 的失败簇统计(说明为什么这块最重要)。** 886 个内部真实会话抽样:把未验证的猜测当事实陈述 41/886、谎报完成/已验证 16/886、绕开阻碍不上报 9/886…且官方明说这些失败**集中在长上下文场景**。【核,PDF 原文】

**第三层:训练机制的边界(诚实标注)。** system card 确认 RL 是主要数据来源、确认长视野/自验证/记忆/委派是评测维度,但**没有**"对验证后交付给奖励"这类训练配方原文——你原文档 §4 的训练推测保留为【推】级。

---

## 4. 先例的完整测量结果(你项目的直接对照组)

**iwoszapar Rigor Pack(2026-07-03)**——与你的计划几乎完全同构,已有结果:
- 6 个 skill(plan-gate / adversarial-verify / live-state-truth / scope-fence / ruthless-editor / memory-hygiene),完整原文已抓取归档到 `reference/iwoszapar-rigor-pack-6-skills.md`(从站点 JS bundle 提取,核查 agent MD5 复核一致)。【核】
- 协议:埋雷任务、双臂、盲评(评审只见匿名输出+雷点清单)、公开全部败绩。结果:出货版 **12胜0负2平**,token 开销 +4~11%。
- **最有价值的是败绩**:adversarial-verify v1 和 live-state-truth v1 **四场全输**——雷都排了,但输在"把验证过程演给读者看"。诊断原话:"Both losers leaked process into product."。v2 修成"读者只看到 findings,永远看不到 narration"后翻盘;v2 又在一个新雷上退步(简洁挤掉了"浮出 spec 矛盾"的行为),v3 加上"先攻击需求本身"才收敛。**这三轮迭代就是你 eval 循环该有的样子。**
- 无增益清单(同样重要):小函数显式 review、材料全在眼前的场景,skill 纯开销。局限:n=2-3/skill、自发布、LLM 评审、页面带付费产品导流。【核】

**why-was-fable-banned(hooks 硬执行路线)**:PreToolUse hook exit 2,spec 不过就物理禁止编辑。SWE-bench 自测 +2/38(自评"噪音水平"),токen 2-3 倍,玩具任务零增益。README 原话:"the gate enforces process, not capability"。——**这是"skill/hook 天花板"的最诚实社区数据**。【核】

**社区背景**:7 月 1 日 r/ClaudeAI 热帖把这套玩法命名为 **"skill distillation"**(Fable 涨价前让它给 Opus 写 skill),X 上扩散;GitHub topic `claude-fable` 下 17 个 repo,6 个是认真移植(其余高星的 pattern-match 到 SEO/scam)。你不是一个人在做,但**做了测量的只有上面两家**。【核/单】

---

## 5. 天花板:定量证据(能补什么、不能补什么)

**能补(流程可靠性 ≈ 一个模型档位)**:
- Confucius(arXiv 2512.10398,v1-v6 复核):Sonnet 4.5 + CCA 脚手架 **52.7%** > Opus 4.5 + Anthropic 私有脚手架 **52.0%**(SWE-Bench-Pro);Opus 4.5 + CCA = 54.3%。消融:层级上下文管理 **+6.6pp**、精修工具 **+7.0pp**,叠加只到 51.6(收益递减)。【核】
- SkillWeaver(2504.07079):**强 agent 合成的技能移植给弱 agent,WebArena 最高 +54.3%**——"强模型行为→弱模型技能"的直接学术验证。【核】
- MAV(2502.20379):弱验证者组合可以抬升更强的生成者(Gemini-1.5-Pro MATH 64.7→72.7);但**非普适**(GPT-4o 在 HumanEval 上反而 94→92)。【核】
- Memp(2508.06433):GPT-4o 轨迹蒸馏出的程序性记忆给 Qwen2.5-14B,+5% 完成率、-1.6 步。【单,摘要级】

**不能补(四个硬上限)**:
1. **组合深度**:AgentSynth——脚手架让 L1 成功率翻倍,但 L5-6 全体崩到 ~4%(人类 70%)。脚手架买不来长程组合推理。【核】
2. **验证器质量**:重采样上限定理(2411.17501)——验证器有假阳性,采样再多也到不了强模型精度,且弱模型的假阳性率与其单次精度相关(越弱越骗得过验证器);最优重试常 <10 次。【核】
3. **技能authoring质量**:SkillLearnBench(2604.20087)——人写的 Anthropic 格式 skill 把固定 agent 从 10.17% 拉到 **74.50%**(7.3 倍!skill 上限很高),但**自动生成的 skill 只覆盖人写差距的 ~45%**,且"更强的模型写 skill 不一定更好——它们爱写过度规定、硬编码参数的 skill"。→ 人工策展 + eval 迭代不可省。【核】
4. **指令密度**:IFScale(2507.11538)——前沿模型 ~**100-150 条并发指令**后遵循率开始掉(500 条时只剩 68%),primacy 效应 1.5-2.5×(靠前的指令遵循率显著更高)。→ **skill 总预算:全套件同时激活的祈使句控制在 <100 条,最重要的规则放最前**。本套件按此设计。【核】

另一条设计红线:多轮退化(2505.06120)——所有顶级模型从单轮到多轮平均掉 39%,主因是"走错第一步后不回头"。→ 协议里的"需求合并"和"惊喜即停"规则由此而来。【核】

---

## 6. 放置矩阵(每类行为放哪一层,全部经官方文档核verified)

官方文档现在有明文原则:**"Put guardrails in hooks... a request, not a guarantee"**;CLAUDE.md 是 user message、无强制力;skill 会 under-trigger。

| 行为 | 层 | 理由/机制 | 可靠性陷阱 |
|---|---|---|---|
| 永远该生效的姿态(行动准则、诚实汇报、收尾检查) | **CLAUDE.md**(`config/CLAUDE-core.md`) | 每次请求全文在场;root CLAUDE.md 压缩后自动重注入 | >200 行遵循率下降;长会话会被"最近对话"挤掉优先级 |
| 多步流程剧本(规划、切片、验证循环、记忆协议) | **Skills**(3 个) | 按需加载不占常驻 token;body 载入后全程驻留 | **under-trigger 是最弱环节**:description 要"pushy";CLAUDE.md 加一行指针作 backstop;压缩后只保留每 skill 前 5k token |
| "没验证不许说完成" | **Stop 层**:`/goal` = 内置会话级 Stop-hook(不达标不许结束,上限 8 次) | 确定性执行,模型无法忽略 | 需要可判定的验收标准;每次 stop 有延迟成本 |
| 危险命令守门(rm/重启/推送) | **permissions ask 规则 + PreToolUse hook** | 客户端强制,非模型自觉;hook exit 2 连 allow 规则都拦 | Bash 前缀模式对参数变形脆弱,复杂逻辑用 hook 脚本 |
| 生成者/验证者分离 | **verifier subagent**(`agents/verifier.md`) | 真正的 fresh context(看不到主对话);官方:fresh-context 验证优于自查 | 靠 description 自动触发是概率性的;`@verifier` 点名 = 保证执行 |
| 先探索后动手 | **plan mode**(`defaultMode: "plan"` 可选) | 权限系统物理禁写,不是请求 | 只管会话开头,不管中途重规划 |

一句话版:**判断交给 prompt 层,保证交给 hook 层,流程放 skill 层,验证隔离进 subagent。**

---

## 7. 本套件的设计决策(每条都有出处)

| 决策 | 依据 |
|---|---|
| 3 个 skill 而不是 8 个模块各一个 | IFScale 指令预算;iwoszapar 实测 6 个已有两个在部分场景纯开销;你原文档的模块 1/2/8 合并进 CLAUDE-core,5/6/7 合并进 long-horizon-protocol |
| "findings 进交付物,process 不进"写死在 verify skill 里 | iwoszapar v1 四连败的直接教训 |
| "先攻击需求"排在攻击清单第一位 | iwoszapar v3 的收敛点;system card"静默解决矛盾"失败簇 |
| 子任务 ≤1h 人类等效 | METR p80 数据(Opus 级 49-70 分钟) |
| "需求合并"步骤 | 多轮退化 39% + 不回头效应 |
| 修复-验证循环设上限 | 重采样上限定理,最优 <10 |
| "缺料就明说,不许编造" | Fable 的 18% vs Opus 9% missing-context 幻觉——**这是 Opus 本来就赢的维度,skill 要守住而不是移植 Fable 的激进** |
| 每 skill 都留 trivial 逃生口 | 你 CLAUDE.md 的 Tradeoff 原则;iwoszapar 无增益清单(小任务加流程 = 纯税) |
| 英文写 skill 正文 | 与官方/社区 skill 生态一致,方便盲测对照 |
| 不写"复述你的推理"类指令 | 若套件将来跑在 Fable 上会触发 reasoning_extraction 拒答 |

**刻意不移植的 Fable 特征**:missing-context 下硬答的激进;评分者意识带来的表面礼仪(hedging 成"判断调用"、美德信号——system card 证明那是 grader-training 伪影);context 焦虑;计划外动作(防御性 git 备份、代发邮件)。

---

## 8. 合规确认(distillation 红线的精确边界)

三层原文(核查 agent curl 的 raw HTML/PDF):【核】
- Usage Policy:禁止"Utilization of inputs and outputs to **train an AI model** (e.g., model scraping or model distillation) without prior authorization"。
- 商业条款 §D.4:禁止用服务"build a competing product...including to **train competing AI models**"。
- System card §1.5:分类器"narrowly target frontier LLM development(pretraining pipelines、分布式训练、加速器设计)...should not impact the vast majority of AI development or research"。

**结论**:操作动词是"训练模型"。写 SKILL.md/CLAUDE.md/hook 描述观察到的行为 = prompt engineering,不产生任何权重更新,且目标还是 Anthropic 自家的 Opus——**不触碰任何一层红线**【推,平义解读;无 explicit carve-out】。社区把这叫 "skill distillation" 是个容易引起误会的坏名字,实质是 prompt 工程。

---

## 9. 未决问题(按重要性排序)

1. **头号实验**:对 Opus 4.8,legacy 2,700-token 提示灌回 vs 本行为套件,谁有效/是否叠加?(`CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT` A/B,任务集用 evals/)
2. ~~本套件未经盲测~~ → **已完成三轮盲测 + 两版 Fable 迭代(2026-07-04)**:终版 15W-2L-0T/17 题;v1 的 verify skill 果然重演了先例的"过程漏进产品"崩盘(1-5),v2/v3 修复后翻盘。完整战绩、诊断与限制见 `evals/RESULTS.md`。**长任务组(套件核心场景)仍未测**——这是新的头号评测缺口。
3. "Opus 4.8 是唯一 server-side fallback 目标"未证实(需带 key 调 Models API 看 `allowed_fallback_models`)。
4. Shihipar "80%" 引言只溯源到 the-decoder(视频转录不可取;我们的独立测量 85.7% 按 token、TwelveTables 66% 按字节——引用时写清分母)。
5. 若你想要:把套件在 **7 月 7 日前**(Fable 还在订阅内,50% 周额度,还剩 3 天)交给 Fable 本尊按 skill-distillation-kit 流程再迭代一轮,让它以自己的口吻改写/挑错——这正是社区方法论的正版用法。

## 10. 关键来源(全部为核查 agent 亲自打开过的)

- 官方:Prompting Claude Fable 5(platform.claude.com,行为→指令对照表)/ Introducing Claude Fable 5 / adaptive-thinking / effort / context-editing / compaction / memory-tool / model-config / hooks / skills / sub-agents / memory / permissions / output-styles / features-overview(code.claude.com)
- System card PDF(317 页,SHA-256 复核):anthropic.com/claude-fable-5-mythos-5-system-card;AUP + Commercial Terms
- 二进制:npm @anthropic-ai/claude-code-darwin-arm64@2.1.201;Piebald-AI/claude-code-system-prompts(227+ 版本追踪,本地 clone 已 diff)
- 先例:iwoszapar.com(rigor-pack + skill-distillation-kit,全文已归档 reference/)、github SihyeonJeon/why-was-fable-banned、benjaminard/fable-skills、TwelveTables.blog
- 学术:arXiv 2512.10398(Confucius)、2604.20087(SkillLearnBench)、2504.07079(SkillWeaver)、2502.20379(MAV)、2507.11538(IFScale)、2505.06120(多轮退化)、2411.17501(重采样上限)、2506.14205(AgentSynth)、2508.06433(Memp)、2510.00615(ACON)
- 数据:metr.org/assets/benchmark_results_1_1.yaml(原始 YAML 本地复算)、artificialanalysis.ai(GDPval-AA v2 / Omniscience / 延迟)、every.to Vibe Check、the-decoder(×2)、HN 48750456/48757323
