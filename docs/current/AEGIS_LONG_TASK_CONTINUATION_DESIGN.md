# Aegis Long Task Continuation Design

状态：`Reviewed`

## 1. 文档定位

本文档定义 `Aegis Method Pack` 中“长任务防跑偏协议”的设计草案。

它只回答以下问题：

- 长任务为什么需要额外的 attention / resume / evidence discipline
- 当前 Method Pack 可以新增哪些 advisory-first artifacts
- 现有 todo 复述如何与 checkpoint、resume、drift check 结合
- 后续 skill 改造应如何避免重复 owner 与 authority drift

它不负责回答以下问题：

- 宿主进程如何后台常驻
- 自动重启、任务队列、watchdog、daemon 或数据库存储如何实现
- authoritative `GateDecision`、evidence sufficiency 或 completion authority 如何裁决

---

## 2. Baseline Constraints

本设计必须遵守以下已批准边界：

1. 当前仓库仍是 `Aegis Method Pack (runtime-ready)`，不是完整平台。
2. 当前仓库可以产出 draft、hint、projection、checklist 与 runtime-ready artifact conventions。
3. 当前仓库不能产出 authoritative `GateDecision`，不能授予 `completion authority`。
4. 当前仓库必须保留 plugin-installable 与 multi-host distribution 属性。
5. 新增长任务能力不得把 host-specific hooks、runner、session recovery 反向写成 method-pack baseline。

相关 authority refs：

- `docs/current/README.md`
- `docs/current/AEGIS_TARGET_STATE.md`
- `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
- `docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
- `docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md`
- `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`

---

## 3. Problem Statement

长任务中的主要风险不是“执行过程一定会暂停”，而是暂停、压缩、失败或恢复后出现以下问题：

1. 任务目标丢失：恢复后无法准确说明原始目标、非目标与成功标准。
2. 执行状态丢失：无法说明上轮完成了什么、证据是什么、下一步是什么。
3. 范围漂移：局部实现细节把 agent 带离 baseline、兼容边界或用户授权范围。
4. 退役遗漏：新增逻辑后没有交代旧 owner、fallback、重复分支或历史补丁去留。
5. 假完成：测试、日志、diff、回读证据不足，却输出完成结论。

因此本设计的目标不是承诺“长任务永不中断”，而是保证：

> 长任务即使中断，也必须可恢复、可审计、可继续、可发现漂移，并且不得无证完成。

---

## 4. Design Summary

本设计引入：

> `Todo-Checkpoint Reflection Loop`

它由四个锚点组成：

1. `TaskIntentDraft`：锚定目标、范围、非目标、风险。
2. `TodoCheckpointDraft`：锚定当前 todo、已完成项、下一步与阻塞。
3. `DriftCheckDraft`：锚定 baseline、兼容边界、退役轨与范围漂移检查。
4. `EvidenceBundleDraft`：锚定验证证据，防止无证完成。

四个锚点分别解决：

- todo 复述负责拉回注意力。
- checkpoint 负责保存执行状态。
- drift check 负责发现架构或范围漂移。
- evidence bundle 负责约束完成声明。

---

## 5. Proposed Runtime-Ready Artifacts

以下 artifacts 仅为 Method Pack 产出的 draft / hint / projection input。

它们不得被写成 authoritative runtime records。

### 5.1 `TodoCheckpointDraft`

最小字段：

- `schemaVersion`
- `taskId`
- `currentTodo`
- `completedTodos`
- `activeSlice`
- `evidenceRefs`
- `blockedOn`
- `nextStep`
- `updatedAt`

当前 owner：

- method pack

用途：

- 让 agent 在每轮执行前复述当前目标与下一步。
- 让恢复会话先读 checkpoint，而不是重新猜测任务状态。
- 让用户和后续 agent 能检查长任务是否仍沿着原 todo 前进。

### 5.2 `ResumeStateHint`

最小字段：

- `schemaVersion`
- `taskId`
- `lastCheckpointRef`
- `resumeInstruction`
- `knownPartialWork`
- `mustReadBeforeContinuing`
- `unsafeToAssume`

当前 owner：

- method pack / host projection

用途：

- 在上下文压缩、会话恢复或 agent 交接后，提供最小恢复入口。
- 明确哪些事实必须重读，哪些结论不能凭记忆沿用。

### 5.3 `DriftCheckDraft`

最小字段：

- `schemaVersion`
- `taskId`
- `taskIntentRef`
- `baselineRefs`
- `scopeStatus`
- `compatStatus`
- `retirementStatus`
- `newRiskSignals`
- `decision`

当前 owner：

- method pack

允许的 `decision`：

- `continue`
- `pause-for-user`
- `needs-baseline-readback`
- `needs-verification`
- `blocked`

禁止的 `decision`：

- `gate-passed`
- `completion-granted`
- `authoritatively-safe`

用途：

- 让长任务每轮显式检查是否偏离目标、baseline、兼容边界或退役轨。
- 防止 workflow discipline 被误包装成 runtime authority。

---

## 6. Loop Protocol

### 6.1 Start

长任务开始前，agent 必须生成或刷新：

1. `TaskIntentDraft`
2. `BaselineReadSetHint`
3. `ImpactStatementDraft`
4. 初始 todo map
5. 第一份 `TodoCheckpointDraft`

如果 baseline refs 不足，任务状态必须保持为 `needs-baseline-readback`，不得直接进入实现。

### 6.2 Before Each Work Slice

每个执行切片开始前，agent 必须复述：

1. 当前目标
2. 当前 todo
3. 本切片要改什么
4. 本切片不改什么
5. 完成后如何验证

复述必须来自 latest checkpoint 与 baseline refs，不能只来自会话记忆。

### 6.3 After Each Work Slice

每个执行切片结束后，agent 必须更新：

1. `completedTodos`
2. `evidenceRefs`
3. `blockedOn`
4. `nextStep`
5. `DriftCheckDraft`

如果没有新增可验证证据，状态只能是 `partial` 或 `needs-verification`。

### 6.4 Resume

恢复长任务时，agent 必须先读取：

1. latest `TodoCheckpointDraft`
2. latest `ResumeStateHint`
3. original `TaskIntentDraft`
4. required baseline refs

如果恢复信息互相矛盾，agent 必须暂停并请求用户或 baseline readback，而不是继续执行。

### 6.5 Completion Candidate

长任务只能进入“完成候选”状态，不能由 Method Pack 自行授予完成权威。

完成候选必须具备：

1. 所有 todo 有明确状态。
2. 所有阻塞项已解决或明确外部化。
3. `EvidenceBundleDraft` 覆盖主要验收点。
4. `DriftCheckDraft.decision` 没有处于 `blocked`、`pause-for-user`、`needs-baseline-readback` 或 `needs-verification`。
5. `GateInputPack` 已组装为 future runtime core 或用户审阅输入。

---

## 7. Skill Ownership

当前落地后的 owner 分工如下：

| Owner | Responsibility |
| --- | --- |
| `executing-plans` | 按计划执行 task，并在每个切片前后消费 checkpoint protocol |
| `subagent-driven-development` | 将 checkpoint / resume state 传递给 fresh subagent，避免跨 agent 丢状态 |
| `verification-before-completion` | 检查 evidence bundle 与完成候选输入，不授予 completion authority |
| `long-task-continuation` | 只定义长任务 continuation protocol，不接管计划执行 |

`long-task-continuation` skill 已按协议 skill 落地。

它不是新的 execution owner，也不复制 `executing-plans` 或 `subagent-driven-development` 的职责。

---

## 8. Reference Input Boundary

外部项目只作为内部设计参考输入：

- 长任务 loop 思想可以吸收为 continuation discipline。
- lifecycle / phase / UAT 思想可以吸收为 Method Pack workflow strengthening。
- host hooks、context recovery、MCP、LSP、session ergonomics 可以留给 future host profile 或 adapter-facing docs。

主 README 不应因为本设计而新增外部项目依赖说明。

只有在直接复制代码、脚本、配置或文档片段，或引入运行时依赖时，才需要在 README、NOTICE 或 license 文件中补充 attribution / dependency 说明。

---

## 9. Repair Track

真实根因：

- 现有 todo 复述能拉回注意力，但缺少统一的 durable checkpoint / resume / drift artifact 约定。

唯一 canonical owner：

- 本设计文档负责定义 long-task continuation protocol。
- 具体执行仍由 execution skills 负责。

最小必要改动：

- 固定 Method Pack 内的 protocol 与 artifacts。
- 让 execution / subagent / verification skills 消费该协议，而不是复制该协议。

兼容边界：

- 不删除现有 todo 复述。
- 不改变现有 plugin install surfaces。
- 不引入 runtime core、daemon、watchdog 或 host-specific dependency。

验证方式：

- 文档回读确认无越权 completion authority。
- representative interrupted-task scenario 验证 resume / drift / evidence 行为。

---

## 10. Retirement Track

当前重复或旧 owner：

- 现阶段没有可直接删除的 runtime owner。
- 潜在重复风险来自后续继续扩写 execution skills 时，与 `long-task-continuation` 抢 protocol 职责。

默认操作：

- 不新增 execution owner。
- 不新增 host-specific fallback。
- 不把外部 runner 或 host hook 迁入 Method Pack baseline。

保留对象与原因：

- 保留现有 todo 复述，因为它仍是 attention anchor。
- 保留现有 execution skills，因为它们仍是执行 owner。

退役触发：

- 如果后续发现某个 skill 中已有重复的 resume / checkpoint 文本，应收敛到本协议并删除重复描述。

验证：

- 用 `rg` 检查是否出现多个自称 canonical continuation owner 的文件。

---

## 11. Verification Plan

本设计落地后，至少需要以下验证：

1. 静态边界检查：
   - 文档不得声明 authoritative `GateDecision`
   - 文档不得声明 `completion authority`
   - 文档不得把 host-specific hook 写成 Method Pack baseline
2. Skill parse / packaging 检查：
   - 现有 skill metadata 仍可解析
   - plugin sync 与 host install docs 不受影响
3. Representative scenario：
   - 创建一个长任务样本
   - 执行到中段后暂停
   - 从 checkpoint 恢复
   - 验证 agent 能说明已完成、证据、下一步、漂移状态
   - 验证证据不足时不能输出完成结论

---

## 12. Risks And Non-Goals

风险：

1. 协议过重，导致普通短任务也被迫执行长任务流程。
2. 新增 skill 后出现重复 owner。
3. 文档措辞不慎，把 draft / hint 写成 authoritative output。
4. README 过早暴露外部研究来源，制造依赖错觉。

非目标：

1. 不承诺 AI 工具长任务永不中断。
2. 不实现后台 runner。
3. 不实现 automatic retry / watchdog。
4. 不实现 runtime core。
5. 不在主 README 中新增外部参考项目说明。

---

## 13. Acceptance Criteria

本设计可以进入实施计划的条件：

1. 用户确认本协议方向。
2. 文档没有越过 Method Pack 边界。
3. 新 artifacts 均明确标记为 draft / hint / projection input。
4. skill owner 分工清晰，没有新增重复 execution owner。
5. 后续实施计划能为 interrupted-task scenario 给出可运行验证。

---

## 14. Self-Review

### Goal

目标满足：本文档将长任务防跑偏能力收敛为 Method Pack 内的 protocol，而不是 runtime implementation。

### DeeperCause

没有发现需要推翻现有 Method Pack 边界的更深层原因。

当前问题的更深层诱因是：

- todo 复述只有 attention anchor
- 长任务还需要 state anchor、drift anchor 与 evidence anchor

本设计已分别覆盖。

### Evidence

设计依据来自当前 approved baseline：

- `docs/current/README.md`
- `docs/current/AEGIS_TARGET_STATE.md`
- `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
- `docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
- `docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md`

### Risk / Unknown

当前 residual risk：

- 真实 host 恢复链仍取决于具体宿主的 session / plugin 能力。
- 本设计只验证 Method Pack protocol 与 fixture-backed scenario，不验证后台 runner。

### Decision

`continue`

本设计可作为 reviewed design input 保留，并继续由 current authoritative docs 控制最终 baseline；它不能直接视为 runtime authority。
