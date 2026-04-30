# Aegis Product Baseline

状态：`Approved`

## 1. 文档定位

本文档定义当前 `Aegis` 仓库的产品基线。

本文档只负责回答以下问题：

- 当前仓库是什么产品
- 当前仓库在整体 `Aegis` 路线中承担什么角色
- 当前仓库不承担什么角色
- 当前仓库后续应如何演进而不发生边界漂移

本文档不负责回答以下问题：

- 单个 skill 的具体写法
- runtime core 的节点级 contract
- adapter 的 host-specific 细节

---

## 2. 结论先行

当前仓库的正式产品定义为：

> `Aegis Method Pack (runtime-ready)`

当前仓库继承自 `superpowers` 的强项是：

- skills 分发模型
- 多宿主安装与说明骨架
- workflow 触发机制
- 方法论可组合性
- plugin / marketplace / repo-install 方式的可分发能力

当前仓库新增的核心方向是：

- 将 `Aegis` 的治理型流程沉淀为可安装的方法层
- 将 ADD 的高价值理念收敛为 runtime-ready artifacts 与边界契约
- 让不同宿主先“像 Aegis 一样工作”，再在未来接入独立 runtime core

---

## 3. 当前仓库负责的内容

当前仓库负责以下四类内容：

### 3.1 Method Pack

- skills
- initial instructions
- workflow packs
- review / verification / planning discipline
- evidence capture conventions

### 3.2 Distribution Layer

- Codex / OpenCode / 其他宿主的安装说明
- plugin / marketplace / symlink or junction 说明
- 与宿主发现机制兼容的文件组织
- 面向所有支持 plugin 的 AI 编程工具保留可安装属性

### 3.3 Governance Projection Layer

- `TaskIntent` 草稿模板
- `ImpactStatement` 草稿模板
- `EvidenceBundle` 清单与命名规范
- `Gate input` 的最小结构化提示
- 面向宿主输出的风险摘要与下一步建议

### 3.4 Baseline Docs for Method Layer

- 当前仓库自己的 authority docs
- 方法层基线
- 与 future runtime core 的边界文档

---

## 4. 当前仓库不负责的内容

当前仓库不得承担以下 authoritative responsibilities：

- `Baseline Registry`
- `ADR / policy snapshot` 的最终解析
- `GateDecision` 的权威裁决
- `evidence sufficiency` 的最终判定
- `completion authority` 的授予或保留
- defect / drift / corrosion 的最终分类
- cross-session governance archive / fact chain

这些能力只允许存在于未来独立的 `Aegis Runtime Core`。

---

## 5. 当前仓库与整体 Aegis 路线的关系

当前推荐的整体产品形态为：

- `Aegis Method Pack`
- `Aegis Runtime Core`
- `Aegis Host Adapters`

其中当前仓库只对应第一项。

这意味着：

- 当前仓库可以先快速扩散到多个宿主
- 当前仓库可以先收敛流程 discipline
- 当前仓库可以为 future runtime core 预留 contracts
- 当前仓库不能因为文档更多、skill 更强，就自称已经具备完整 governance authority

---

## 6. 与 upstream superpowers 的关系

当前仓库与 upstream 的关系定义如下：

- 继承：skills 分发模型、workflow skeleton、多宿主使用骨架
- 继承：plugin-installable 的方法层分发能力
- 差异化：治理型流程、证据驱动约束、runtime-ready boundary、Aegis branding
- 不追求：向 upstream 回灌 fork-specific 产品定位与 runtime-ready 边界

当前仓库应被视为独立产品线，而不是“带一点规则改造的 superpowers 镜像”。

---

## 7. 当前阶段的演进策略

当前阶段采用以下收敛顺序：

### Phase 1：Baseline First

- 先建立 authority map
- 先建立产品基线、流程基线、边界基线
- 后续所有 skill 改造都以这些文档为准

### Phase 2：Process Upgrade

- 在不打散现有分发骨架的前提下，增强关键 skills
- 重点增强 framing、debugging、verification、planning、review

### Phase 3：Runtime-ready Projection

- 为 future runtime core 固定 artifact shapes
- 形成稳定的 method-pack 输出契约

### Phase 4：Repo Split

- 在单仓方法层稳定后，再拆独立 runtime core 与 adapters

---

## 8. 漂移信号

出现以下任一现象时，应视为产品边界正在漂移：

- 当前仓库开始在 docs 或 skills 中直接宣称拥有 `completion authority`
- `GateDecision` 被写成当前仓的本地最终裁决逻辑
- 宿主侧输出被误写成 authoritative truth
- 当前仓为了容纳 runtime core，开始把 method pack、adapter、authority core 再次揉成大一统结构
- 当前仓失去 plugin-installable 属性，或只能在单一宿主中安装使用

---

## 9. 当前约束

当前仓库的一切后续文档与实现，都应满足以下约束：

- 先做方法层，不伪装成权威层
- 先固定 baseline，再改流程实现
- 先收敛 artifact contract，再接 runtime core
- 所有“更厉害”的增强，都必须在边界清晰的前提下进行
