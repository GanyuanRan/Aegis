# ADR-0001 `Aegis Method Pack` 不是 `Aegis Runtime Core`

状态：`Approved`

## 背景

当前仓库起步于 `superpowers` fork，天然适合承载：

- skills
- initial instructions
- workflow packs
- 多宿主安装与分发骨架

与此同时，`Aegis` 目标又明显强于普通方法包，包含：

- evidence-driven governance
- runtime-ready artifacts
- ADD-style authority boundary

因此，当前路线最容易出现的结构性误判是：

> 因为方法层变强了，就把当前仓误当成已具备 authoritative runtime core 的系统。

如果放任这种误判继续演化，会产生以下风险：

- completion authority 滑落到方法层或宿主层
- `GateDecision` 被写成 prompt 或 skill 文本里的本地逻辑
- future runtime core 无法保持独立 canonical owner
- 当前仓再次退化为“大一统二开仓”

---

## 决策

正式决策如下：

> 当前仓库只承担 `Aegis Method Pack (runtime-ready)`，不承担 `Aegis Runtime Core`。

具体约束如下：

- 当前仓可以产出 runtime-ready artifacts、drafts、hints 与 projections
- 当前仓不能独立授予 `completion authority`
- 当前仓不能独立形成 authoritative `GateDecision`
- 当前仓不能把 `Baseline Registry`、`PolicySnapshot`、`evidence sufficiency` 写成仓内最终 truth
- future runtime core 必须以独立边界存在

---

## 备选方案

### 方案 A：当前仓同时承载 method pack 与 runtime core

优点：

- 短期看起来路径更短
- 单仓工作流更直接

缺点：

- 方法层与权威层边界混乱
- upstream 继承区与自研核心区难以稳定切分
- completion authority 容易被流程文本或宿主执行状态偷走

### 方案 B：当前仓固定为 method pack，runtime core 独立

优点：

- authority 边界清晰
- 先把方法层做强，再接 runtime core
- 更符合多宿主复用与长期演进

缺点：

- 前期需要忍受“能力更强，但尚非完整 core”的阶段性不完整
- 后续仍需要建设独立 runtime core

---

## 取舍理由

`Aegis` 的差异化价值不只在 skill 写得更细，而在于：

- 方法层可扩散
- 权威层不可漂移

如果当前仓直接兼任 runtime core，看似省一步，实际会把这两个价值重新揉回一起，最终同时损伤二者。

因此，必须先钉死：

- 当前仓先做强方法层
- runtime authority 留给未来独立 core

---

## 影响与后果

正面影响：

- 后续基线文档、skills 与 contracts 都有明确边界
- 可以放心增强流程 discipline，而不担心越权
- future runtime core 拆分时不会再重做一遍边界澄清

负面影响：

- 当前仓短期内不能自称“完整 Aegis 平台”
- 某些看起来像 gate 的流程，只能先以 advisory/projection 形式存在

---

## 漂移信号

以下现象表明本 ADR 正在被侵蚀：

- skill 或 docs 直接宣称当前仓拥有最终 gate authority
- host projection 文本被误写成 final decision
- baseline truth 只存在于会话输出、注释或 prompt 中
- 为了方便实现，把 runtime core 的 canonical owner 回填到当前仓

---

## 重审触发条件

出现以下任一情况时，应重审本 ADR：

- 独立 `Aegis Runtime Core` 已落地，且当前仓需要重新定义与其关系
- 当前方法层与未来 core 的边界文档已无法覆盖真实需求
- 产品目标从 method pack 演进为新的多仓或多进程形态，需要新的边界 ADR
