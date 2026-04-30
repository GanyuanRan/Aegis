# Aegis Product Requirements

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis` 当前二次开发改造的产品需求。

本文档只负责回答以下问题：

- 本次改造到底要实现什么
- 本次改造明确不做什么
- 成功标准是什么
- 哪些现有 `superpowers` 能力必须保留
- 哪些新增能力必须进入 `Aegis`

本文档不负责回答以下问题：

- 具体 skill 的逐行实现
- future runtime core 的节点执行细节
- adapter 的 API 或 transport 设计

---

## 2. 产品目标

本次 `Aegis` 二次开发改造的目标是：

> 在不破坏 `superpowers` 当前有效方法层与插件分发能力的前提下，将 ADD 思维、TLREF 三层反思执行框架思维，以及“修复轨 + 退役轨”的熵减治理思路融入方法层默认工作流，并为 future `Aegis Runtime Core` 保留清晰 authority boundary。

---

## 3. 核心需求

### 3.1 需求 A：融入 ADD 思维

`Aegis` 必须把以下 ADD 相关能力融入方法层：

- 证据驱动
- 架构优先的影响面分析
- baseline / ADR / contract 的前置读取意识
- 高风险任务的治理输入显式化
- 对 future authoritative core 的 runtime-ready artifact 预留

### 3.2 需求 B：融入 TLREF 三层反思执行框架

`Aegis` 必须把 TLREF 融入方法层默认工作流：

- 第一层：路径选择
- 第二层：DIVE + task-specific loops
- 第三层：QA

并使其可投影到核心 process skills。

### 3.3 需求 C：保留 `superpowers` 未被覆盖的有效能力

本次改造不得损坏 `superpowers` 原本已经有效、且未被 ADD / TLREF 替代的能力，尤其包括：

- skills 分发模型
- workflow 触发骨架
- 多宿主安装与使用说明骨架
- 现有可复用的 planning / review / testing discipline

### 3.4 需求 D：保留插件可安装能力

本次改造完成后，`Aegis` 必须继续保留：

> 像 `superpowers` 一样，可以通过 plugin / marketplace / repo-install 等方式，被安装进所有支持 plugin 的 AI 编程工具中的能力。

这意味着：

- 不得把当前仓改造成只能在单一宿主里生效的私有规则包
- 不得引入会破坏跨宿主分发模型的结构性依赖
- 不得为了治理能力增强而牺牲 plugin-installable 属性

### 3.5 需求 E：引入修复轨 + 退役轨双轨治理

对以下任务类型：

- bug 修复
- 架构重构
- 链路治理
- contract 调整

`Aegis` 必须默认要求同时输出：

- `修复轨`
- `退役轨`

### 3.6 需求 F：分阶段产品化策略

当前产品化策略必须满足：

1. 先把当前仓做成可独立开源、可跨宿主分发的 `Aegis Method Pack`
2. 先完成 method-pack 侧的 baseline 固化、非 live strengthening 与 release/readme 准备
3. 在 method-pack 获得真实反馈之前，不提前承诺完整 `Aegis Platform`
4. 如果后续进入完整平台建设，必须保持 `Method Pack`、`Host Adapters`、`Runtime Core` 三层分离
5. `OpenCode` 可以作为 future host-shell 候选之一，但不能被提前写成当前仓的单宿主绑定前提

---

## 4. 非目标

本次改造明确不以以下目标为交付范围：

- 在当前仓直接实现 authoritative runtime core
- 在当前仓直接实现 `completion authority`
- 在当前仓建设完整 host adapter runtime
- 在当前阶段把所有 existing skills 全部重写
- 为单一宿主做深度定制而破坏跨宿主 plugin 可安装能力

---

## 5. 兼容性要求

本次改造必须满足以下兼容性要求：

- 不破坏现有 plugin / marketplace / repo-install 分发能力
- 不破坏 method-pack 仓作为多宿主安装入口的定位
- 不把 host-specific logic 反向提升为通用 baseline
- 不破坏现有未被替代的有效 workflow discipline

---

## 6. 成功标准

当以下条件全部满足时，可视为本次改造达到阶段性成功：

1. 当前仓形成完整 authority docs
2. TLREF 被正式纳入方法层 baseline
3. 双轨治理规则被正式纳入 current docs
4. runtime-ready artifacts 具备清晰 schema baseline
5. 第一批高杠杆 skills 已完成 process upgrade
6. `Aegis` 仍可作为 plugin-installable method pack 面向多宿主分发
7. 当前仓仍未越权宣称拥有 authoritative runtime core

---

## 7. 当前优先级

当前优先级从高到低为：

1. authority docs 完整化
2. 规则分层
3. 双轨治理固化
4. artifact schema 固化
5. 第一批核心 skills 升级
6. 后续 adapter/core 对接准备
7. method-pack open-source readiness 与 staged productization

---

## 8. 失败信号

出现以下任一现象，应视为本次改造偏离产品需求：

- `Aegis` 失去 plugin-installable 属性
- 新增治理能力只能在单一宿主中工作
- skill 改造破坏原本未被替代的有效 `superpowers` 能力
- 方法层开始越权产出 authoritative `GateDecision` 或 `completion authority`
- 双轨治理只停留在口号，没有形成实际交付约束
