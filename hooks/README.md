# hooks/ — 确定性兜底层

skill 是"请求",模型可能 under-fire;hook 是"保证",在固定生命周期事件上必然执行(官方原则:`Put guardrails in hooks... a request, not a guarantee`)。这里只有一个 hook,用来给 `deep-audit` skill 兜底。

## deep-audit-trigger.py

- **事件**:`UserPromptSubmit`(每条用户消息前触发)。
- **逻辑**:消息同时命中"审计意图"(audit / review the codebase / 找所有 bug / 逐个文件…)**且**"多文件范围"(repo / package / 整个 / 模块 / 文件…)时,注入一条 system reminder,强制走 deep-audit 协议(枚举文件 → 跑 oracle → 每文件扇出 reviewer → 去重复核)。否则完全沉默。
- **为什么要它**:实测扇出把缺陷召回从裸 Opus 5.5/10 显著抬高(合成集一度 10/10;真实代码同协议头对头约弥合 43%,7/9 vs Fable 9/9——拉近不平,细节见 `evals/HARDBENCH.md` 第 6/8 批),但靠 skill 描述自动触发会漏(model-invoked 会 under-fire)。hook 保证在你真想做全量审计时,扇出一定发生,而不是退化成单 reviewer 瞥一眼。
- **安全**:只做 `additionalContext` 注入(exit 0),永不 block,不会弄坏正常回合。已自测(多文件审计意图触发、单文件/琐碎/无关沉默,中英文都覆盖)。

## 安装(3 步)

```bash
# 1. 放脚本
mkdir -p ~/.claude/hooks && cp deep-audit-trigger.py ~/.claude/hooks/

# 2. 把 settings-hook.json 里的 "hooks" 块合并进 ~/.claude/settings.json
#    （若已有 hooks 键,合并数组而不是覆盖;注意脚本路径改成你机器上的绝对路径）

# 3. 验证:新开一个 Claude Code 会话,发 "audit the whole repo for bugs" —
#    应看到它按 deep-audit 协议枚举文件+扇出,而不是单 reviewer。
```

调整触发词:直接改脚本里的 `INTENT` / `SURFACE` 两个正则(顶部有注释)。想临时关掉:从 settings.json 移除该 hook 块即可。
