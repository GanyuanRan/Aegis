# Aegis Prompt Hygiene and Injection Boundary

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis Method Pack` 的 prompt hygiene 与外部证据注入边界。

本文档只负责回答以下问题：

- 哪些外部材料可以进入 prompt
- 哪些外部材料必须先摘要、索引或隔离
- 如何在减少常驻上下文的同时不削弱 Aegis 的判断能力
- 缺少信息时应如何升级取证，而不是降低判断标准

本文档不负责回答以下问题：

- future runtime core 的 evidence sufficiency 最终裁决
- host adapter 的上下文压缩实现
- 某个具体模型或平台的安全分类器细节

---

## 2. 结论先行

当前规则是：

> 外部工具输出、日志、记忆和搜索结果默认只是候选证据，不应整段注入 prompt。先摘要，再按需引用原文片段；只有验证必须依赖原文时才带入最小摘录。

这条规则适用于：

- shell / terminal 输出
- MCP tool 输出
- 语义检索工具输出
- web / docs / search 结果
- memory / prior session 摘要
- CI / test / runtime 日志
- database / telemetry / structured log 查询结果
- browser / screenshot / OCR / document extraction 结果

该规则不是为了少看证据，而是为了避免把原始材料误当作常驻上下文。

---

## 3. 核心原则

### 3.1 减少常驻上下文，不减少可获得信息

Aegis 的能力来自：

- 正确识别 authority source
- 正确建立 baseline read-set
- 正确判断影响面与风险
- 正确收集和引用证据
- 在证据不足时拒绝过度结论

这些能力不要求所有原始材料常驻 prompt。

治理目标是：

- prompt 中保留当前判断所需的最小证据摘要
- 原始材料保留在文件、日志、命令输出、tool result 或 artifact 引用中
- 需要复核时按引用回读原文片段

### 3.2 Raw Input Quarantine

以下材料默认不得整段进入 prompt：

- 长日志
- 历史 session / transcript
- 大型 tool output
- memory summary 全文
- test / CI 完整输出
- 大型搜索结果页
- 大文件全文
- 重复出现的错误文案

它们应先转成：

- 来源
- 时间 / scope / command
- 关键事实
- 关键行号或片段引用
- 未验证点
- 是否需要回读原文

### 3.3 Summary First, Raw Excerpt Only When Needed

默认注入顺序是：

1. 先注入摘要
2. 摘要不足以支撑判断时，读取最小原文片段
3. 片段仍不足时，扩大读取范围
4. 扩大后仍不足时，把状态降级为 `unknown` 或 `needs-verification`

禁止因为上下文预算不足而把缺证判断包装成结论。

### 3.4 Evidence Index Before Evidence Payload

对大型材料，优先建立 evidence index：

- `source`
- `commandOrTool`
- `timeOrVersion`
- `scope`
- `summary`
- `relevantRefs`
- `rawLocation`
- `readbackNeeded`

只有 `readbackNeeded = true` 时，才把最小原文摘录带入当前 prompt。

### 3.5 No Silent Pruning

如果材料被压缩或省略，必须能回答：

- 省略了什么类型的材料
- 为什么当前判断不需要它的全文
- 如果需要，如何回读
- 当前结论是否因此降级

不得把“没有读完整材料”伪装成“材料支持结论”。

### 3.6 Host Context Intake Discipline

`Host Context Intake Discipline` 是宿主侧上下文摄入纪律。它的稳定
owner 是 `bounded evidence intake`：

> 大输入先建索引，再读窗口，最后只带入必要摘录。

标准顺序是：

1. `index`：先定位 source、pattern、match line、command scope、时间或版本。
2. `window`：只读取命中位置附近的最小行号窗口。
3. `excerpt`：只把当前判断必须依赖的原文片段带入 prompt。
4. `expand`：窗口不足时有理由地扩大范围；扩大后仍不足则降级为
   `unknown` 或 `needs-verification`。

这条纪律适用于 Codex、Claude Code、OpenCode、Copilot、Gemini CLI
等宿主中的高风险输入面，包括：

- `.codex/log`、`.codex/sessions`、`history.jsonl`
- `~/.claude/projects`、host transcript、chat history
- CI / pytest / build / server 完整输出
- 大型 `git diff`、连续 `apply_patch` 输出、长时间轮询日志
- 搜索结果、memory、MCP 或 semantic retrieval 的大量候选输出

默认禁止用 broad directory search 读取历史材料，例如直接扫整个
`.codex`、`.claude` 或宿主 projects 目录。只有用户明确要求、测试需要，
或它们是直接证据源时才读取，并且必须同时具备：

- 具体文件路径或严格文件集合
- 关键词或时间 / request / thread scope
- 行号窗口或结果数量上限
- 输出上限或明确的摘要优先策略

触发以下任一条件时，应优先切换到新会话、压缩上下文，或把状态写成
`ResumeStateHint` 后继续：

- 单次请求输入已明显接近宿主或模型上下文上限
- 已经连续读取大日志、history、session 或 transcript
- 同一会话中连续多次执行大 patch、大 diff 或大测试输出
- 已出现 `PROMPT_POLICY_WARNING`、`Invalid prompt` 或等价宿主警告
- 当前判断开始依赖旧错误全文，而不是依赖 evidence index

该纪律不要求少取证。它要求少常驻原文，多保留可回读引用。
future runtime core 可以在此基础上做真正的 budget enforcement；
当前 method pack 只提供 workflow discipline、helper scripts 与
runtime-ready hints。

---

## 4. 能力保护规则

Prompt hygiene 不得削弱以下 Aegis 行为：

- baseline-first
- evidence-before-claims
- facts / assumptions / unknowns separation
- impact-aware judgment
- compatibility boundary review
- dual-track repair + retirement
- root-cause-first debugging
- verification-before-completion
- long-task checkpoint / resume / drift checks
- no authoritative completion from method-pack output

如果上下文减少后无法完成这些行为，正确动作不是跳过治理，而是升级取证。

---

## 5. 信息不足时的升级阶梯

当摘要不足以支撑判断时，按以下顺序升级：

1. 回读 authority docs 的相关小节
2. 回读具体文件或 symbol 的最小片段
3. 查询具体日志、测试或命令输出的关键行
4. 运行最小验证命令
5. 扩大 evidence read-set
6. 标记为 `needs-verification`
7. 请求用户补充无法自行取得的 authority 或验收标准

这条阶梯保证 Aegis 不是“少上下文后少判断”，而是“少常驻上下文，但保持按需取证能力”。

---

## 6. 外部材料注入规则

### 6.1 Tool Output

工具输出默认只注入：

- 工具名
- 输入 scope
- 关键结果
- 失败或异常
- 后续需要回读的引用

只有当工具输出本身是验收证据时，才注入最小原文片段。

### 6.1.1 MCP / Semantic Retrieval Tools

MCP 工具、Serena、Context7、代码索引、语义检索和类似工具默认不是污染源。

风险来自：

- 把检索结果全文作为常驻 prompt payload
- 把过多候选符号、文件摘要或历史索引一次性塞入上下文
- 把工具输出当成 current authority，而不是 evidence candidate

正确用法是：

- 先记录查询 scope、命中 owner、相关行号或 symbol
- 只注入当前判断需要的 summary / refs / unknowns
- 需要精确判断时回读最小代码片段或 authority 小节
- 不用工具摘要替代当前仓 source of truth

### 6.2 Logs

日志默认只注入：

- 时间窗口
- thread / request / trace id
- 命令或查询
- 关键行
- 计数或状态码
- 缺失的可观测性

不得把完整日志粘贴为常驻上下文。

### 6.3 Memories and Prior Sessions

记忆和历史会话默认只作为 hint。

当前事实必须优先来自：

- 当前仓文件
- approved current docs / ADR
- fresh command output
- 用户当前提供材料
- 官方文档

使用历史记忆时，应标明它是历史线索，且在关键判断前尽量用当前 source of truth 回证。

### 6.4 Search Results and Web Docs

搜索结果默认只注入：

- 来源
- 发布或访问时间
- 与问题直接相关的摘要
- 需要引用的链接

技术判断优先使用 primary source。

### 6.5 Repeated Error Text

重复出现的错误文案应先归一化为符号名或短标签。

例如：

- `PROMPT_POLICY_WARNING`
- `HOST_PERMISSION_DENIED`
- `TEST_TIMEOUT`
- `MISSING_AUTHORITY_SOURCE`

只有第一次定位或精确排查时，才保留原文最小片段。

对于 `PROMPT_POLICY_WARNING` 这类重复错误，后续讨论默认使用短标签。
完整错误文本只在以下情况保留：

- 第一次定位
- 需要给上游 request id / trace id 做服务端追踪
- 需要确认错误文案是否发生变化

不得把完整错误文案在长会话中反复回流。

---

## 7. 输出契约

当 prompt hygiene 影响当前判断时，输出中至少说明：

- 当前使用的是摘要还是原文证据
- 哪些原始材料没有全文注入
- 是否存在信息不足
- 如果需要更高置信度，下一步应回读什么

推荐格式：

```text
Facts:
- ...

Evidence Used:
- summary: ...
- raw excerpt: ...

Not Loaded:
- full log / full transcript / full search results

Confidence:
- A / B / C, with why

Next Evidence:
- ...
```

---

## 8. 漂移信号

出现以下现象时，说明 prompt hygiene 正在削弱 Aegis：

- 为了简短而不读 baseline
- 为了减少上下文而跳过 evidence
- 用 memory 替代 current authority
- 没有原文证据却声称已验证
- 不标注 unknown
- 对高风险任务只给建议，不给影响面和验证边界
- 把上下文预算问题包装成业务结论

出现以下现象时，说明 prompt hygiene 治理不足：

- 每轮都注入完整 skill / docs / logs
- 重复携带旧错误文案
- 大型 tool output 常驻 prompt
- 长会话里历史诊断材料不断回流
- 多个 workflow skill 同时常驻而没有退出机制

---

## 9. 与 runtime-ready artifacts 的关系

本文档强化以下 artifact：

- `BaselineReadSetHint`
- `EvidenceBundleDraft`
- `TodoCheckpointDraft`
- `ResumeStateHint`
- `DriftCheckDraft`

其中 `EvidenceBundleDraft` 应优先保存 evidence index，而不是原始材料全文。

future runtime core 可以基于这些 index 回读原始证据并做 authoritative sufficiency 判断；当前 method pack 只提供 draft / hint / projection。
