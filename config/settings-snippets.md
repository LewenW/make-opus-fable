# 配置杠杆：能用配置补的,不要用 prompt 补

> 结论先行:Fable 的六个原生优势维度里,**四个可以直接用 Opus 4.8 的配置补**(思考深度、工具间思考、长跑持久性、记忆基础设施),只有"自验证倾向"和"委派积极性"必须靠 prompt/skill(即本套件)。
> 以下全部经 2026-07-04 官方文档逐条核verified;版本相关项标注了 as-of。

## 1. Claude Code 侧(她的主要环境)

```jsonc
// ~/.claude/settings.json 相关键
{
  // 思考:Opus 4.8 是 adaptive thinking(与 Fable 同机制,唯一区别是 Fable 不可关闭)。
  // 当前版本默认已开启(二进制确认: alwaysThinkingEnabled===false 才关闭,否则 true)。
  // 显式写上保险:
  "alwaysThinkingEnabled": true,

  // effort:官方对 Opus 4.8 的建议是 coding/agentic 任务从 xhigh 起步(Fable 才是从 high 起步)。
  // 注意 effort 刻度是按模型校准的——Opus 的 xhigh ≠ Fable 的 xhigh。
  "effortLevel": "xhigh"
}
```

- 单轮加深:prompt 里加 `ultrathink`(唯一仍生效的关键词;"think hard" 等已失效)。
- `ultracode`(/effort 菜单):xhigh + 常驻多 agent 编排许可——这是 Opus 4.8 独有的编排增强,Fable 反而没有。长任务建议开。
- 守护性 hooks(确定性执行,比 prompt 强):
```jsonc
{
  "permissions": {
    // 你已有的"删除本地文件必须确认"就是这一层;ask 在任何模式下都会弹确认
    "ask": ["Bash(rm *)", "Bash(rmdir *)", "Bash(git push *)"]
  }
}
```
- 强制验证闭环(可选,最强执行档):会话内 `/goal <验收标准>` = 内置的 Stop-hook,模型没达标就不允许结束回合(上限连续 block 8 次)。
- verifier subagent 安装后,用 `@verifier` 点名调用 = 保证执行;靠 description 自动触发 = 概率执行。

## 2. API 侧(她的 parallax / agent 项目用)

| Fable 原生行为 | Opus 4.8 等价配置 | 具体参数 |
|---|---|---|
| 自适应思考(不可关) | 同机制,需显式开 | `thinking: {"type": "adaptive"}`(省略=关!manual budget_tokens 会 400) |
| 工具调用间思考 | adaptive 自带,无需 beta header | 同上(`interleaved-thinking-2025-05-14` header 对 4.8 已废弃、发了也无害) |
| 深思考 | effort 参数(GA,无 header) | `output_config: {"effort": "xhigh"}`,xhigh/max 时 `max_tokens ≥ 64k` |
| 长跑不丢线索 | 上下文编辑 + 压缩 | header `context-management-2025-06-27`(清工具结果,默认 100k 触发)+ header `compact-2026-01-12`(默认 150k 触发,压缩块必须回传) |
| 自我节奏 | 任务预算(模型可见的倒计时) | header `task-budgets-2026-03-13`,`output_config.task_budget: {"type":"tokens","total":N}`,N≥20000 |
| 跨会话记忆 | memory tool(GA) | tools 加 `{"type":"memory_20250818","name":"memory"}`——API 会自动注入"先看记忆目录再干活/假设随时会被打断"的协议提示,免费的行为矫正 |

## 3. 实验开关(A/B 用,来自二进制逆向,as-of v2.1.201,标识符每版会变)

- `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1/0` — 强制 lean/legacy 系统提示(可以给 Opus 4.8 灌回旧版 2700-token 详细提示做对照实验;见调研报告 §3)
- `CLAUDE_CODE_INVESTIGATE_FIRST=additive` — Anthropic 给 Opus 4.7 的官方补偿补丁(先调查再提问)
- `ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES` — 自定义模型能力旗标(含 `lean_prompt`)

## 4. 不要做的配置

- 不要给模型看剩余 token 倒计时(诱发提前收尾;Fable 的"context 焦虑" quirk 对 Opus 同样适用)。
- 不要在 skill 里写"把你的推理过程复述出来"——若这套 skill 未来跑在 Fable 上会触发 `reasoning_extraction` 拒答回落。
- 温度/top_p 不用调——Opus 4.8 和 Fable 5 都拒绝非默认采样参数(400)。
