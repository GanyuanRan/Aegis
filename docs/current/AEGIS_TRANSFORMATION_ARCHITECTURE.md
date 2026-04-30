# Aegis Transformation Architecture

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis` 当前整体改造的总设计方案。

本文档只负责回答以下问题：

- `Aegis` 整体改造的目标形态是什么
- 为什么当前仓不应只停留在 `superpowers` 的改名分支
- 为什么当前阶段先收敛为 `Aegis Method Pack (runtime-ready)`
- 方法层、宿主投影层、future runtime core 的总体关系是什么
- TLREF / DIVE / Reflection / QA 在整体改造中的系统位置是什么
- 当前阶段的分步演进路径是什么

本文档不负责回答以下问题：

- 某个具体 skill 的逐行实现
- future runtime core 的节点级执行细节
- host adapter 的 API / transport / process topology

---

## 2. 结论先行

`Aegis` 的整体改造目标不是：

- 做一个更名版 `superpowers`
- 做一个把 rules 写得更多的 prompt pack
- 做一个把 method pack、adapter、authority core 全部揉在一起的大一统单仓

`Aegis` 的整体改造目标应为：

> 在继承 `superpowers` 方法层分发能力与 plugin-installable 属性的基础上，收敛出一个具备治理型流程、runtime-ready artifact、清晰 authority boundary 的方法层产品，并为未来独立的 `Aegis Runtime Core` 与 `Aegis Host Adapters` 预留稳定接口。

因此，当前仓库的正确目标形态是：

> `Aegis Method Pack (runtime-ready)`

而不是完整 `Aegis Platform`。

---

## 3. 为什么需要这次改造

单纯的 `superpowers` 继承路线，优势在于：

- skills 分发模型成熟
- 多宿主安装骨架成熟
- workflow 触发机制成熟
- 面向支持 plugin 的 AI 编程工具具备可安装能力

但它的天然边界也很清楚：

- 更偏 methodology / skills / process layer
- 不天然拥有 baseline truth
- 不天然拥有 authoritative gate
- 不天然拥有 `completion authority`

而 `Aegis` 要解决的问题，不只是“让 agent 更会做事”，还包括：

- 让 agent 的过程更证据驱动
- 让架构分析进入默认工作流
- 让高风险任务的治理输入提前显式化
- 为 future runtime core 留下稳定治理输入和可审计 artifact

所以，`Aegis` 不是用 `superpowers` 替代 ADD，而是：

- 用 `superpowers` 的分发模型承载 `Aegis Method Pack`
- 用 `Aegis` 的治理理念增强方法层
- 用清晰边界把 authoritative core 留到 future 独立 runtime

---

## 4. 总体目标形态

`Aegis` 的长期目标形态应分为三层：

### 4.1 Aegis Method Pack

负责：

- skills
- initial instructions
- workflow discipline
- review / verification / planning patterns
- evidence capture conventions
- runtime-ready artifact drafts

### 4.2 Aegis Host Adapters

负责：

- 收集宿主中的上下文、文件、命令、日志、测试、diff
- 将宿主事件映射为统一治理输入
- 将 runtime core 输出投影回宿主侧提示、阻断或摘要

### 4.3 Aegis Runtime Core

负责：

- baseline truth
- policy snapshot
- authoritative impact analysis
- gate decision
- evidence sufficiency
- completion authority
- governance archive / fact chain

---

## 5. 当前仓库在总体系中的位置

当前仓库只对应：

- `Aegis Method Pack`

并且是：

- `runtime-ready`
- `advisory-first`
- `authority-constrained`

这意味着当前仓可以做的事包括：

- 把治理型流程变成方法层默认工作流
- 产出 `TaskIntentDraft`、`ImpactStatementDraft`、`EvidenceBundleDraft`、`TodoCheckpointDraft` 等 artifacts
- 让不同宿主先“像 Aegis 一样工作”

这也意味着当前仓不能做的事包括：

- 自己成为 `system of record`
- 自己产出 authoritative `GateDecision`
- 自己授予 `completion authority`

---

## 6. TLREF 在整体设计中的位置

`AGENTS_RULES.md` 中的三层反思执行框架不是附属细节，而是 `Aegis` 方法层的主脊柱。

### 6.1 第一层：路径选择

系统位置：

- method pack 的统一任务分流入口

负责：

- 区分真实问题与伪需求
- 区分快速路径与标准路径
- 决定是否需要进入更完整的治理型流程

### 6.2 第二层：DIVE + task-specific loops

系统位置：

- `brainstorming`
- `systematic-debugging`
- `writing-plans`
- `requesting-code-review`
- `verification-before-completion`

负责：

- 问题界定
- 分析决策
- 执行验证
- 证据与风险回看

### 6.3 第三层：QA

系统位置：

- completion 前的最终 review / verification discipline

负责：

- `Remove/Restore`
- 置信度评估
- 资产沉淀
- 风险与回滚说明

边界约束：

- TLREF 可以组织 method-pack 侧流程
- TLREF 不能越权变成 runtime authority

---

## 7. 当前基线与总设计的关系

当前总设计文档不是替代已有 baseline，而是对它们做总装配：

- `README.md`
  - 定义 authority order 与最小 authoritative set
- `AEGIS_PRODUCT_BASELINE.md`
  - 定义当前仓是什么与不是什么
- `AEGIS_PROCESS_BASELINE.md`
  - 定义 TLREF/DIVE/Reflection/QA 的当前方法层基线
- `AEGIS_RUNTIME_READY_BOUNDARY.md`
  - 定义 method pack 与 future runtime core 的边界
- `ADR-0001`
  - 定义当前仓不是 runtime core

本文档负责把这些文档收束成一个整体改造图景。

---

## 8. 长周期演进阶段（概念轴）

以下 `Stage A-E` 是长期概念演进轴，用来说明 `Aegis` 从方法层到未来 runtime core 的长期形态。
它不与 `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md` 中当前实施切片的 `Phase 1-5` 编号一一对应。

### Stage A：Baseline First

目标：

- 先建立 authority docs
- 先明确产品定位、流程基线、runtime-ready boundary

结果：

- 后续 skill 改造不再无锚推进

### Stage B：Process Upgrade

目标：

- 把 TLREF / DIVE / Reflection / QA 投影到高杠杆 skills

优先顺序：

- `brainstorming`
- `systematic-debugging`
- `verification-before-completion`
- `writing-plans`
- `requesting-code-review`

### Stage C：Runtime-ready Artifacts

目标：

- 固定 method-pack 产物形态

最小集合：

- `TaskIntentDraft`
- `BaselineReadSetHint`
- `ImpactStatementDraft`
- `EvidenceBundleDraft`
- `GateInputPack`
- `TodoCheckpointDraft`
- `ResumeStateHint`
- `DriftCheckDraft`

### Stage D：Adapter-facing Contracts

目标：

- 把宿主投影与 future runtime core 对接的边界固定下来

### Stage E：Repo Split / Core Extraction

目标：

- 在 method-pack 稳定后，单独建设 `Aegis Runtime Core` 与 adapters

---

## 9. 当前刻意不做的事

为了避免边界漂移，当前阶段明确不做以下事情：

- 不把 method pack 宣称为完整 platform
- 不在当前仓实现 authoritative gate engine
- 不在当前仓实现 `completion authority`
- 不把 host-specific logic 反向写成 method-pack 基线
- 不把未分层的 `AGENTS_RULES.md` 原样升格为 current authority
- 不以治理增强为代价牺牲 plugin-installable 属性

---

## 10. 漂移信号

出现以下现象时，应视为整体改造开始偏航：

- 当前仓重新把 method pack、adapter、runtime core 混写为单仓同层结构
- skill 文本开始直接输出 `pass / block / granted` 作为最终裁决
- 宿主侧因为工具跑完或测试通过就宣布“治理意义上已完成”
- 规则母稿长期不拆层，method rules、host rules、repo rules 持续混在一起
- runtime-ready artifacts 长期没有固定 schema，导致不同 skills 各自产生不同形态
- `Aegis` 无法继续以 plugin / marketplace / repo-install 方式被支持 plugin 的 AI 工具安装

---

## 11. 当前设计约束

后续所有改造都必须满足以下设计约束：

- 先方法层，再 runtime core
- 先 baseline，再实现
- 先分层，再扩展
- 先 artifact contract，再 adapter / core 对接
- 任何“更强”的能力都不能以越权为代价

---

## 12. 下一步建议

在本总设计生效后，最合理的下一步顺序为：

1. 补齐规则分层文档
2. 补齐 artifact schema baseline
3. 从 `brainstorming` 开始做第一轮 process upgrade
4. 再推进 `systematic-debugging` 与 `verification-before-completion`

这样推进，能最大程度避免后续 skill 改造失去 authority 锚点。
