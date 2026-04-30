# Aegis Runtime-Ready Boundary

状态：`Approved`

## 1. 文档定位

本文档定义当前 `Aegis Method Pack` 与 future `Aegis Runtime Core` 之间的最小边界。

本文档只负责回答以下问题：

- 当前仓可以稳定产出哪些 runtime-ready artifacts
- 当前仓不能裁决哪些 authoritative outputs
- 方法层、宿主投影层与 runtime core 应如何协作

本文档不负责回答以下问题：

- runtime core 的节点级执行实现
- host adapter 的 transport 或 API 细节
- 数据库存储结构

---

## 2. 结论先行

当前仓的目标不是成为 runtime core，而是成为：

> 能稳定产出治理输入与治理投影的 `runtime-ready method pack`

因此：

- 当前仓可以生成草稿、模板、checklists、artifact conventions
- 当前仓可以要求宿主补齐必要信息
- 当前仓可以输出 advisory、warning 风格的 process guidance
- 当前仓不能独立产出 authoritative `GateDecision`
- 当前仓不能独立授予 `completion authority`

---

## 3. 当前仓可产出的 runtime-ready artifacts

当前仓允许并鼓励产出以下 artifacts：

### 3.1 `TaskIntentDraft`

最小字段：

- `requestedOutcome`
- `scope`
- `changeKinds`
- `riskHints`

用途：

- 帮助宿主与未来 runtime core 建立统一任务 framing

### 3.2 `BaselineReadSetHint`

最小字段：

- `candidateDocs`
- `whyRelevant`
- `missingAuthority`

用途：

- 指出当前任务应优先阅读哪些 baseline 文档
- 暴露 authority 缺口

### 3.3 `ImpactStatementDraft`

最小字段：

- `affectedLayers`
- `owners`
- `invariants`
- `compatBoundary`
- `nonGoals`

用途：

- 让高风险任务在执行前显式暴露影响面与兼容边界

### 3.4 `EvidenceBundleDraft`

最小字段：

- `artifactKey`
- `type`
- `source`
- `summary`
- `verifier`

用途：

- 统一证据收集的命名与最小结构

### 3.5 `GateInputPack`

最小字段：

- `baselineRefs`
- `impactStatement`
- `compatPlan`
- `retirementPlan`
- `evidenceBundle`

用途：

- 作为 future runtime core 的最小输入包

### 3.6 `TodoCheckpointDraft`

最小字段：

- `taskId`
- `currentTodo`
- `completedTodos`
- `activeSlice`
- `evidenceRefs`
- `blockedOn`
- `nextStep`
- `updatedAt`

用途：

- 让长任务在每个执行切片前后有可恢复的 todo / checkpoint 状态

### 3.7 `ResumeStateHint`

最小字段：

- `taskId`
- `lastCheckpointRef`
- `resumeInstruction`
- `knownPartialWork`
- `mustReadBeforeContinuing`
- `unsafeToAssume`

用途：

- 在会话恢复、上下文压缩或 agent 交接时提供最小恢复入口

### 3.8 `DriftCheckDraft`

最小字段：

- `taskId`
- `taskIntentRef`
- `baselineRefs`
- `scopeStatus`
- `compatStatus`
- `retirementStatus`
- `newRiskSignals`
- `decision`

用途：

- 在长任务执行过程中显式检查目标、baseline、兼容边界与退役轨是否漂移

---

## 4. 当前仓不能裁决的 authoritative outputs

以下输出只能由 future `Aegis Runtime Core` 负责：

- authoritative `BaselineRef[]`
- authoritative `PolicySnapshot`
- authoritative `ImpactStatement`
- authoritative `GateDecision`
- `architecture_drift / defect / corrosion` 最终分类
- `evidence sufficiency` 最终判定
- `completion authority`

任何 method-pack skill、host prompt、projection template 都不得越权宣称已拥有这些能力。

---

## 5. 三层协作模型

当前推荐的协作模型为：

### 5.1 Method Pack

负责：

- 组织问题界定
- 组织 artifact 生成
- 输出提醒、模板、checklists、review structures

不负责：

- 最终治理裁决

### 5.2 Host Projection / Future Adapter

负责：

- 收集宿主中的原始上下文
- 提取文件、命令、测试、diff、日志等原始证据
- 将 method-pack 产物与宿主事件映射为统一治理输入
- 将 runtime core 输出投影成宿主可消费的提示或阻断

不负责：

- 独立复制一套权威 gate logic

### 5.3 Runtime Core

负责：

- baseline truth
- policy snapshot
- authoritative impact analysis
- gate decision
- evidence sufficiency
- completion authority

---

## 6. 当前运行模式

在 runtime core 尚未独立落地前，当前仓只允许采用：

> `Advisory-first, runtime-ready`

这意味着：

- 当前仓可以让宿主“更像 Aegis 一样工作”
- 当前仓可以让流程更严格、更证据驱动
- 当前仓不能把流程纪律误包装成 system authority

---

## 7. 漂移信号

出现以下现象时，说明当前边界正在被侵蚀：

- skill 文本开始直接输出 `pass / block / granted` 作为最终裁决
- host 侧因为测试通过或流程结束就自称“治理意义上已完成”
- 本仓 docs 把草稿 artifact 称为 authoritative record
- 为了图省事，把 runtime 逻辑直接塞回 method pack 仓

---

## 8. 当前约束

后续一切与 gate、impact、verification、review 相关的 skill 改造，都必须遵守：

- 可以产生 draft
- 可以产生 hint
- 可以产生 projection
- 不可以产生越权 authority
