# parallax 全量深度审计报告 — 2026-07-05

由 `deep-audit` 编排(effort=xhigh,52 个源文件各派一个全新上下文 reviewer 并行审,再逐条人工核对代码验证)对 `LewenW/parallax` 的一次真实运行。**只读快照**审计,`main` HEAD `69c9e04` 全程未改动一字节。

- 52 文件全审,20 个命中,共 29 条发现(1 critical / 8 high / 7 medium / 13 low)
- 本报告只收录**逐条亲自核实**(读你 main 的真实代码 + 必要时跑 Python 验证数学断言)的 1 条 critical + 8 条 high;medium/low 見下方"未逐条复核"说明
- 用时约 18.5 分钟,52 agent、615 次工具调用

## Critical(1)— 建议优先修

**`sources/trendforce.py::_pub_iso`(第 16-18 行)** — 时区标签造假,与 `base.py::rfc822_to_iso` 是**同一家族、不同变体**的 bug(那个已在你的 Codex 审计流程里标注"P1"并部分修复,这个是同一根因在另一个 source 文件里的独立实例,从未被碰过):
```python
def _pub_iso(rfc822: str) -> str:
    dt = parsedate_to_datetime(rfc822)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")   # 没有 .astimezone(UTC)!
```
带非 UTC 偏移(如 `+0800`)的 pubDate 会被原样贴上 `Z`。实测:`"Mon, 05 Jul 2026 02:30:00 -0500"` → 输出 `"2026-07-05T02:30:00Z"`,真实 UTC 应为 `07:30:00Z`,偏了整整 5 小时。**修法与 base.py 一致**(见下条),但要小心 — 那个修法本身还有残留漏洞。

## High(8)— 全部亲自核实为真

1. **`sources/base.py::rfc822_to_iso`(第 46 行)—「已修复」留了个坑**:当前代码已是 `.astimezone(UTC)`(你的 Codex 审计已修过一版)。但我亲自跑了验证:`email.utils.parsedate_to_datetime` 遇到 RFC2822 的 `-0000`("时区未知"标记,RSS feed 常见)或缺失偏移量时,返回的是 **naive datetime**(无 tzinfo)。Python 对 naive datetime 调用 `.astimezone(UTC)` 的语义是"假定为**本机时区**再转换",不是"当作已是 UTC"。实测:在你的 EDT 机器上,`-0000` 输入被再偏移了 4-5 小时——**docstring 想防的"提前泄漏"用这条边路又溜回来了**。修法:先判断 `dt.tzinfo is None`,若是则 `dt.replace(tzinfo=UTC)`(不是 astimezone),再统一转换。

2. **`store.py::observations_as_of`(第 230-231 行)— PIT 校验形同虚设**:`as_of` 的校验只检查 `"T" in as_of`,不要求 `Z`/`+00:00` 后缀,而整个系统的 PIT 排序不变量(`models/core.py` 头部声明)是"字符串字典序==时间序,全靠时间戳统一格式撑着"。我实测:一个不带后缀的 `as_of="2026-07-04T12:00:00"` 能通过校验,但存储的 `published_at` 都带 `Z`;字符串比较 `"...12:00:00Z" <= "...12:00:00"` 为 **False**——一条恰好发生在 as_of 那一刻的观测会被 PIT 查询错误排除。

3. **`models/core.py::_TS_RE`(第 14 行)— 时间戳格式本身允许两种会打破排序不变量的写法**:正则同时允许可选小数秒和两种 UTC 后缀(`Z`/`+00:00`)。我实测两个反例:①`"...:00.5Z"`(真实更晚)字符串比较却**小于**`"...:00Z"`(真实更早)——小数点 `.`(0x2E)的 ASCII 值小于 `Z`(0x5A);②同一时刻的 `"...Z"` 和 `"...+00:00"` 字符串不相等且比较结果任意。这条是根源,上面两条(observations_as_of 的弱校验、PIT 排序)某种程度都是它的下游症状。

4. **`graph/resolver.py::_norm`(第 46-48 行)— 公司后缀截断正则漏了单词边界,会腰斩正常公司名**:我实测:`'Cisco'` → `'cis'`、`'Costco'` → `'cost'`、`'Petco'` → `'pet'`、`'Sysco'` → `'sys'`。正则本意是"去掉末尾的 `Inc/Corp/Co/Ltd` 等噪声后缀",但因为分隔符 `[,\.]?\s*` 允许零字符,任何**恰好以 co/inc/corp 等结尾的完整单词**都被腰斩。这会让这些公司名在你的实体解析里精确匹配层全部失效,只能靠子串兜底(而子串层还有你已知的 `ASM`→`ASML` 类误链风险)。**这条建议优先级仅次于 critical**——如果你的公司清单里有任何名字用词碰巧以这几个音节结尾,现在就在悄悄误判。

5. **`evals/earnings_scoring.py::_magnitude_veto`(第 63-66 行)— 除零 + 负值绕过,而这是你"零容忍"的主评分门**:`if p <= 0: continue` 只护住了被除数 `p`,分母 `n`(gold 期望值)完全没护。gold 值恰好为 `0.0`(如"税率约 0%")会直接 `ZeroDivisionError` 炸穿整场评分;gold 为负值则比值恒小于 1000,永远不会触发本该触发的量级否决。

6. **`graph/status.py::compute_status`(第 33/36 行)— 证据状态机的核心不对称,L3 能"立事实"但不能"推翻事实"的契约被破坏**:docstring 明写"L3 不能立事实也不能推翻事实"。`contra_l2plus` 正确地把 L3 从"反对票"里剔除(注释"L3 不计"),但 `support_disclosers` 统计"支持票"时**没有同样过滤 L3**——两个 L3 独立 discloser 就能把状态推到 `corroborated`,一个 L1+一个 L3 就能推到 `confirmed`。这正是 docstring 禁止的"L3 立事实"。

7. **`extract/earnings.py::_guidance_ok`(第 66-73 行)— 反捏造数字校验用子串匹配,没有数字边界**:整个模块存在的意义是"guidance 数字必须真实出现在原文引用里,不能是 LLM 编的"。但检查用的是 `v in q`(纯子串),我实测:引用里有真实的 `"30.9 billion"`,LLM 编造一个 `value=9`,校验会通过——因为 `"9"` 就是 `"30.9"` 的子串。这条防幻觉的门可以被任何"恰好是已有数字子串"的编造值绕过。

8. **`jobs/fix_gnews_published_at.py::_pubdates_from_raw`(第 30 行)— 一次性矫正脚本按 link 去重,但你的文档唯一键是 `(url, content_sha256)`**:`gnews.py` 里 `content_sha256 = sha256(link|raw_title)`,同一 link、不同 title 是两份不同 document(真实场景:同一篇文章被聚合器用不同标题抓两次)。矫正脚本 `out[link] = pub` 只按 link 存,撞了就后者覆盖前者;`main()` 里查询也只按 `url` 取值(第 41-42 行连 `title` 都没 SELECT)。后果:如果一次 raw 归档里恰好有两条同 link 不同 title 的 item,其中一份文档会被矫正成**另一份**item 的 pubDate。发生概率较低,但这个脚本本身就是"修时区 bug"用的,它自己带着同类精度问题。

## 未逐条复核(medium 7 + low 13)

以下按严重度列出定位,供你或后续 audit 参考,**我没有逐条读代码验证**,不排除误报(遵循"精度不能只靠信任"原则,不逐条确认就不list 进 high/critical):

**medium**:`jobs/add_manual_observation.py::main`、`jobs/register_prediction.py::main`、`jobs/watch_semi_billings.py::main`、`reports/earnings_diff.py::build_markdown`、`sources/sec.py::_derive_discrete_quarters`、`sources/trendforce.py::pull`、`evals/earnings_scoring.py::_magnitude_veto`(第二条,同函数的单位盲区,与上面第5条不同角度)

**low**:`audit.py::sample_tips`(采样量 n 参数名不副实,只能增不能减)、`extract/earnings.py::latest_extraction`(取"最近一次财报"时同 published_at 无 tiebreak)、`llm_cli.py::_default_runner`、`predictions.py::_compare`、`sources/gnews.py::pull_query`、`sources/sec_filings.py`(两处)、`triangles/series.py`(两处)

## 建议的修复顺序

1. `models/core.py::_TS_RE` 收紧到只认一种格式(建议只认整秒 + `Z`,砍掉小数秒和 `+00:00` 分支)——这是根,修了它,#2 #3 的下游症状自然缓解一部分,但 #2 的弱校验仍要单独补上 `Z`/`+00:00` 后缀要求。
2. `sources/trendforce.py::_pub_iso` 和 `sources/base.py::rfc822_to_iso` 一起修(naive-datetime 补丁),这两个是同一家族。
3. `graph/resolver.py::_norm` 加词边界——这条影响你实体解析的日常正确率,且修法简单(加 `\b` 或改用 `(?:^|(?<=\s))` 前瞻)。
4. `evals/earnings_scoring.py::_magnitude_veto` 和 `extract/earnings.py::_guidance_ok` 都是"反幻觉/反单位错误"防线上的漏洞,建议一起过一遍你的 eval 金标准看有没有已经被这两个漏洞放过的历史案例。
5. `graph/status.py::compute_status` 和 `jobs/fix_gnews_published_at.py` 影响面较窄,按你实际用量排期。

## 方法论说明

这份报告本身就是"编排能补能力轴"结论的实战验证(见 HARDBENCH.md 第四批):同一套 xhigh+扇出协议,在人工种的 10 个变异上测出 10/10(超过 Fable 的 9/10),这次在你的真实代码上跑,一次性挖出你此前两轮 B2/B2b 缺陷召回测试都没碰到过的 7 个全新真 bug(前两轮只覆盖了 store.py/series.py/engine.py/predictions.py/resolver.py 五个文件的一部分函数;这次是全部 52 个源文件)。
