# hooks/ — 确定性兜底层

skill 是"请求",模型可能 under-fire;hook 是"保证",在固定生命周期事件上必然执行(官方原则:`Put guardrails in hooks... a request, not a guarantee`)。这里有两个 hook,各给一个 skill 兜底:`deep-audit-trigger.py` 兜底 `deep-audit`(该不该扇出审计),`verify-after-edit.py` 兜底 `verify-before-done`(编辑后该不该跑测试)。这一层是**通用**的——它不挑任务模式,对每一次代码编辑都生效。

## deep-audit-trigger.py

- **事件**:`UserPromptSubmit`(每条用户消息前触发)。
- **逻辑**:消息同时命中"审计意图"(audit / review the codebase / 找所有 bug / 逐个文件…)**且**"多文件范围"(repo / package / 整个 / 模块 / 文件…)时,注入一条 system reminder,强制走 deep-audit 协议(枚举文件 → 跑 oracle → 每文件扇出 reviewer → 去重复核)。否则完全沉默。
- **为什么要它**:实测扇出把缺陷召回从裸 Opus 5.5/10 显著抬高(合成集一度 10/10;真实代码同协议头对头约弥合 43%,7/9 vs Fable 9/9——拉近不平,细节见 `evals/HARDBENCH.md` 第 6/8 批),但靠 skill 描述自动触发会漏(model-invoked 会 under-fire)。hook 保证在你真想做全量审计时,扇出一定发生,而不是退化成单 reviewer 瞥一眼。
- **安全**:只做 `additionalContext` 注入(exit 0),永不 block,不会弄坏正常回合。已自测(多文件审计意图触发、单文件/琐碎/无关沉默,中英文都覆盖)。

## verify-after-edit.py

- **事件**:`PostToolUse`,matcher `Edit|Write|MultiEdit`(每次代码编辑后触发)。
- **逻辑**:从被编辑文件向上找项目根,自动识别测试命令(npm/pnpm/yarn/bun test、pytest、`uv run pytest`、`cargo test`、`go test`、`make test`),跑一遍,把 ✓/✗ 结果(失败时附最后 25 行)作为 `additionalContext` 塞回上下文,逼模型对结果做反应。**非阻塞**——它从不 block 编辑,只是提醒"没验证过的编辑还不算 done"。
- **为什么要它**:verify-after-edit 是工程里最被偷懒的一步,实测强模型也只有 ~60–83% 的编辑跑了真测试,从来到不了 100%,而且数据证明这**不是靠自觉能修的**——所以用 hook 强制,不靠模型记性。它是 `verify-before-done` skill 的机械兜底:skill 是"请记得验证",hook 是"每次编辑后一定验证"。
- **通用性**:不挑 router 模式(generation / audit / long-horizon 都吃这一层),对任意语言的任意代码编辑都生效——这是"通用工具"而非"补三条能力轴"的部分。
- **不打扰**:文档/数据/配置类扩展名(`.md`/`.json`/`.yaml`/图片…)不触发;每个项目根 45s 去抖(`MOF_VERIFY_DEBOUNCE`);单次超时 90s(`MOF_VERIFY_TIMEOUT`,settings 里 hook 级 timeout 设 120s 兜底);没有测试命令 / runner 没装 → 静默。想整个关掉:`MOF_NO_VERIFY_HOOK=1`。
- **安全**:永远 exit 0,任何异常都不抛进会话。已自测:真 pytest 项目跑通并回报 ✓、失败项目回报 ✗+失败尾巴、文档编辑/非编辑工具/去抖/kill-switch/无测试命令全部静默。

## 安装(3 步)

最省事的方式是 `bash install.sh --with-hooks`,它会把两个脚本拷进 `~/.claude/hooks/` 并把绝对路径写进 `settings.json`(带备份、幂等、可 `--uninstall`)。手动装:

```bash
# 1. 放脚本
mkdir -p ~/.claude/hooks && cp deep-audit-trigger.py verify-after-edit.py ~/.claude/hooks/

# 2. 把 settings-hook.json 里的 "hooks" 块合并进 ~/.claude/settings.json
#    （若已有 hooks 键,按事件合并数组而不是覆盖;注意脚本路径改成你机器上的绝对路径）

# 3. 验证:新开一个 Claude Code 会话:
#    - 发 "audit the whole repo for bugs" → 应按 deep-audit 协议枚举文件+扇出,而不是单 reviewer;
#    - 在有测试的项目里改一个代码文件 → 应看到 verify-after-edit 的 ✓/✗ 回报。
```

调整审计触发词:改 `deep-audit-trigger.py` 里的 `INTENT` / `SURFACE` 两个正则(顶部有注释)。调 verify-after-edit 的行为:用上面那几个 `MOF_*` 环境变量。想临时关掉某个 hook:从 settings.json 移除对应的 hook 块即可。
