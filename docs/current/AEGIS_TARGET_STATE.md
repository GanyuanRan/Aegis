# Aegis Target State

状态：`Approved`

## 1. 本文档作用

本文档是 `Aegis` 当前目标状态的一页式摘要。

它只回答三个问题：

- 当前仓库最终要做成什么
- 整体 `Aegis` 长期会演进成什么
- 当前阶段明确不做什么

如果需要细节，回到对应 authoritative docs：

- 产品定位：`docs/current/AEGIS_PRODUCT_BASELINE.md`
- 方法流程：`docs/current/AEGIS_PROCESS_BASELINE.md`
- 边界约束：`docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`

---

## 2. 一句话结论

当前仓库的目标状态不是完整平台，而是：

> `Aegis Method Pack (runtime-ready)`

也就是说，本仓最终要成为一个：

- 融合 `ADD + TLREF + 双轨治理`
- 保留 `superpowers` 分发骨架与 plugin-installable 能力
- 能跨宿主安装与工作
- 能稳定产出 runtime-ready drafts / hints / projections
- 但不越权承担 runtime authority

的方法层产品。

---

## 3. 本仓最终目标状态

当本仓达到目标状态时，应同时满足以下条件：

1. 它是一个清晰定义的 `Aegis Method Pack`
2. 它保留 `superpowers` 的：
   - skills 分发模型
   - workflow 触发骨架
   - 多宿主安装骨架
   - plugin / marketplace / repo-install 分发能力
3. 它内建 `Aegis` 的：
   - evidence-driven 工作方式
   - architecture-first 影响面分析
   - TLREF / DIVE / Reflection / QA
   - 修复轨 + 退役轨双轨治理
4. 它能稳定产出：
   - `TaskIntentDraft`
   - `BaselineReadSetHint`
   - `ImpactStatementDraft`
   - `EvidenceBundleDraft`
   - `GateInputPack`
   - `TodoCheckpointDraft`
   - `ResumeStateHint`
   - `DriftCheckDraft`
5. 它仍然只是：
   - `runtime-ready`
   - `advisory-first`
   - `authority-constrained`

---

## 4. 整体 Aegis 长期目标状态

整体 `Aegis` 的长期形态不是单仓，而是三层体系：

1. `Aegis Method Pack`
2. `Aegis Host Adapters`
3. `Aegis Runtime Core`

三层分工如下：

- `Method Pack`
  - 负责 skills、workflow discipline、runtime-ready artifacts
- `Host Adapters`
  - 负责把宿主上下文映射成统一治理输入，再把结果投影回宿主
- `Runtime Core`
  - 负责 baseline truth、policy snapshot、authoritative impact analysis、gate decision、evidence sufficiency、completion authority

当前仓库只对应第一层，不对应后两层。

---

## 5. 当前阶段的完成标准

对当前仓来说，“目标状态已达成”不是一句空话，而是至少要看到：

1. authority docs 完整
2. TLREF 已正式进入方法层 baseline
3. 双轨治理已进入 current docs 与 workflow
4. runtime-ready artifact schema 已固定
5. 第一批高杠杆 skills 已完成 process upgrade
6. plugin-installable 能力仍然成立
7. 当前仓仍未越权宣称自己是 runtime core

---

## 6. 当前阶段明确不做的事

为了避免跑偏，当前阶段明确不做：

- 不把本仓写成完整 `Aegis Platform`
- 不在本仓实现 authoritative `GateDecision`
- 不在本仓授予 `completion authority`
- 不为了治理增强破坏 plugin-installable 能力
- 不把 host-specific logic 反向抬升成 method-pack baseline
- 不把 method pack、adapters、runtime core 重新揉回单仓同层结构

---

## 7. 当前开发方向与产品化顺序

当前正确开发方向是：

1. 先把本仓做强为 `Method Pack (runtime-ready)`
2. 先把 baseline、process、artifact contract 固定下来
3. 再逐步升级高杠杆 skills
4. 先完成 method-pack 的开源发布基线与非 live rollout strengthening work
5. 之后才进入 adapter-facing contracts
6. 最后才进入 runtime core / adapters 的独立建设

当前推荐的产品化顺序是：

1. 先把 `Aegis Method Pack` 做成可开源、可分发、可跨宿主安装的稳定方法包
2. 先用真实用户反馈、真实任务样本与开源反响，验证它是否值得继续长成完整平台
3. 如果 method-pack 在真实使用中证明有持续价值，再进入完整 `Aegis` 的独立建设
4. 到那一步时，`OpenCode + installed Aegis Method Pack` 可以作为优先宿主壳候选之一，用来承载 future host-side 二开优化

这里的关键边界是：

- `OpenCode` 在未来可以是宿主壳候选，但不是当前仓的 authority 来源
- `Aegis Method Pack` 可以先独立成立，不以 runtime core 落地为前提
- 完整平台建设必须发生在 method-pack 价值被验证之后，而不是反过来提前透支实现

一句话说：

> 先让不同宿主“像 Aegis 一样工作”，再让未来独立 runtime core 成为真正 authority。
