# 差距狩猎评测组(设计稿)— 开放/模糊/验证昂贵型 — 2026-07-05

## 核心原理:oracle 经济学

三臂 25 个臂全满分的真正原因不是任务"短",而是**每个臂都有廉价 oracle**——agent 能跑自己写的测试,执行反馈把两个模型都推到 100%。所以差距狩猎的设计法则只有一条:

> **拿走 oracle,或者给 oracle 标价。验证越贵,判断力越稀缺,模型差距越显形。**

"长视野"只是"验证昂贵"的一种形态(错误复利到很晚才暴露)。其他形态本地完全可测:首发正确率(交付前禁止执行)、缺陷召回(bug 无测试可跑,只能靠读)、视觉 grounding(oracle 是像素)、模糊 scoping(oracle 是被埋的决策陷阱)、知识密度(oracle 是查不到的事实)。

## 按 Lewen 的真实工作画像映射五条分离轴

她的项目形态:parallax(金融数据工程,脏数据+双时态语义)/ lewen-garden & owl(视觉审美驱动前端)/ womenx QA & kaggle red-team(审计/找漏洞)/ FDE 目标(从模糊需求到可运行系统的 scoping)。对应官方已证实的 Fable 优势轴:bug-finding recall 更高、vision grounding +16.3、navigating ambiguity、first-shot correctness、知识密度 +13。

| # | 评测 | 基质 | 打分(客观性) | 针对的分离轴 | 可证伪预测 |
|---|---|---|---|---|---|
| B1 | **首发正确率** | 现有 hardbench 任务的新变体,规则:**交付前禁止执行任何代码**(prompt 强制 + 转录抽查) | 隐藏测试(全客观) | 官方"first-shot correctness";执行反馈被拿走后纯能力显形 | C>A 出现分层;B≈A(plan-gate 或有小增益) |
| B2 | **缺陷召回**(最贴她) | parallax 拷贝到隔离目录,由我在 store/triangles/graph 里种 10 个语义级 bug:PIT as-of 边界 >=/>、财季映射 off-by-one、naive/aware 时区混用、**漏 conn.commit(她的真实 bug#4 同类!)**、千/百万单位错位、yoy 分母用了 revised 值而非 PIT 值、dedupe first/last、cron 幂等破坏 | 召回率对照种子清单(客观);误报我人工核 | 官方"bug-finding recall noticeably higher"+她的 QA 品味 | C>A 可测;**B>A 首次可能成立**(verify skill 的系统攻击清单正是为此写的)→ 弥合率首次可算 |
| B3 | **视觉找茬**(正控) | 合成页面种 N 个视觉缺陷(2px 错位、色板外颜色、380px 溢出、字重错、z-index 渗漏),定视口截图,**臂只拿图**+无缺陷 spec | 缺陷召回(客观) | 多模态 grounding 92.4 vs 76.1;她的 garden 截图验证工作流 | **全组最大分离**;skill 弥合≈0(grounding 是能力不是流程)——同时充当 harness 灵敏度的正控 |
| B4 | **模糊 scoping** | FDE 式含糊 stakeholder 需求 + 资料包内埋决策陷阱(已停更的数据源、互斥的两个要求、合规阻断),交付=建设方案 | 陷阱浮出=二元判定(主导)+盲评补余 | 官方"navigating ambiguity"+她的 FDE 方向 | B>A 可测(需求攻击规则的主场);C≥B |
| B5 | **知识密度探针**(负控) | 禁网,冷门但可验证的领域/API 事实(TWSE 规则、pandas/matplotlib 边缘语义) | 答案对错(客观) | AA-Omniscience +13;**skill 原理上补不了的部分** | C>A=B——干净演示"不可弥合分量" |

## 产出形态:差距是向量,不是标量

跑完得到的是**分轴画像**:每轴 (A, B, C) + 弥合率。预期形状(可证伪):B2/B4 上 skill 有真实弥合、B1/B3/B5 上没有——如果成立,就把"skill 补流程、补不了能力"从文献结论变成她自己数据上的一手结论;如果不成立,更有意思。

## 实施注意

- B2 的 parallax 只在本机隔离目录变异,不动原仓库(cp 到 scratchpad,种子清单存 evals/)。
- B3 正控最便宜,先跑——**先证明 harness 测得出差距,再解读其他轴的零差距**。
- Fable 配额:07-07 后计费;B2+B3 的 Fable 臂估计 <30 万 token。
- 美学轴(garden 风格)不进自动评测:唯一有效的 oracle 是她本人盲评 A/B——如果做,3 对即可。
- 每个评分器上场前先过"参考解满分+坏解掉分"自测(hardbench 的既定纪律)。

## 建议跑序

B3(正控,证明灵敏度)→ B2(她的领域,弥合率最可能首次成立)→ B4 → B1 → B5(负控,一轮 6 臂即够)。
