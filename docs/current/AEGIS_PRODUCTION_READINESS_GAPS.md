# Aegis Production Readiness Gaps

状态：`Reviewed`

## 1. 文档定位

本文档回答两个问题：

1. 当前 `Aegis Method Pack (runtime-ready)` 离“可投入日常生产使用”还差什么
2. 如果目标不是 method-pack，而是完整 `Aegis` 体系，仍缺哪些层

本文档不授予 production authority；它只给出基于当前 fresh evidence 的 gap judgment。

---

## 2. 结论先行

### 2.1 如果你的目标是当前仓这个 `Aegis Method Pack`

当前已经满足：

- baseline docs 完整
- Phase 2 / 3 / 4 / 5 fresh closeout
- OpenCode / Codex 当前关键兼容入口通过
- runtime-ready artifacts、dual-track、boundary discipline 已进入可验证交付

所以结论是：

> **当前仓已接近“可投入日常生产使用”的 method-pack 状态。**

但要把“可用”升级成“稳态生产 rollout”，仍建议补齐下面 3 项剩余工作。

### 2.2 如果你的目标是完整 `Aegis`

结论不同：

> **离完整 `Aegis` 投入生产还差两整层：`Host Adapters` 与 `Runtime Core`。**

当前仓并没有也不应该替代它们。

### 2.3 如果你当前目标是“先开源 method-pack，再决定是否做完整平台”

这是当前更稳妥的策略。

原因不是 scope 缩小，而是 owner 边界更清楚：

- `Method Pack` 已具备独立成立的产品形态
- 开源反响与真实使用反馈，可以反向验证 future `Host Adapters + Runtime Core` 是否值得建设
- 可以避免在没有真实需求压力之前，过早把 method-pack、宿主壳与 runtime authority 混回同一层

因此，当前可以接受以下判断：

> **真实环境回归与完整平台建设都可以后置；method-pack 的非 live strengthening work 可以先做。**

---

## 3. Method Pack 仍建议补齐的剩余工作

### 3.1 可以后置到真实 rollout 前的事项

以下事项重要，但如果你当前目标是“先开源 method-pack、后决定是否做平台”，可以先后置：

- 多宿主 release-level fresh install 回归
- 真实团队任务样本验证

它们的正确位置是：

- 在宣布“可投入日常生产 rollout”之前
- 在扩大宿主兼容矩阵之前
- 在决定是否要把 method-pack 升级成 full platform program 之前

### 3.2 多宿主 release-level fresh install 回归

当前已有 fresh evidence 的宿主重点是：

- `Codex`
- `OpenCode`

仍建议补齐：

- `Claude Code`
- `Cursor`
- `Gemini CLI`

不是只跑 fixture 或单条 smoke，而是至少做一轮“从安装到技能可见、到代表性 prompt 可触发”的 release-level fresh verification。

### 3.3 文档与测试同步回归

本轮已经修正：

- OpenCode skills discovery 主链
- OpenCode 安装说明

仍建议补一轮整体回读，确认：

- `docs/testing.md`
- `docs/README.codex.md`
- `docs/README.opencode.md`
- marketplace / repo-install 说明

之间没有旧 wording 残留。

### 3.4 真实团队任务样本验证

当前 Layer 2 / Layer 3 仍以 fixture-backed transcript 为主。

建议补齐至少 3 类 live production-like 样本：

1. 新功能设计到计划
2. 真实 bug 修复
3. 合同/接口或治理收敛任务

目标不是扩 scope，而是确认当前 method-pack 在真实任务里也能稳定产出：

- ImpactStatementDraft
- EvidenceBundleDraft
- GateInputPack
- TodoCheckpointDraft / ResumeStateHint / DriftCheckDraft（当任务存在中断、恢复或长任务风险时）
- fix track / retirement track

### 3.5 已完成的 strengthening owner 固化

本轮已经完成并落盘：

- `AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `AEGIS_METHOD_PACK_ROLLBACK_CHECKLIST.md`
- `AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `AEGIS_KNOWN_LIMITATIONS.md`
- `AEGIS_METHOD_PACK_STRENGTHENING_COMPLETION_RECORD.md`

因此，这一组工作不再属于当前 gap，而是 production rollout 前的已完成前置资产。

### 3.6 兼容 fallback 的后续退役验证

当前 repo 已有：

- fallback 保留原因
- 观察指标
- 退役时机

当前已完成：

- fallback 保留对象的独立准备入口
  - `docs/current/AEGIS_FALLBACK_RETIREMENT_PREPARATION.md`

仍建议补的是：

- 基于真实多版本 / 多宿主验证，判断哪些 compatibility fallback 可以继续收敛或删除

### 3.7 当前可先做、且不依赖真实环境回归的工作

如果当前优先目标是 method-pack 开源与方法层稳定性增强，建议先做：

1. 文档与测试说明整体回读
2. 非 live representative scenarios 的补强
3. 已落盘 strengthening owner 的 wording 与入口一致性回归
4. fallback 保留对象的后续退役验证

当前 OpenCode plugin 仍保留：

- native global skills path 作为主链
- `config.skills.paths` 作为兼容 fallback

它是合理的，但仍是一个待观察对象。

建议补一条轻量治理记录：

- `保留对象`：OpenCode `config.skills.paths` fallback
- `保留原因`：宿主 discovery 契约仍可能跨版本波动
- `观察指标`：OpenCode integration suite, real install smoke
- `退役时机`：当多版本验证显示 fallback 不再提供兼容价值

当前这类记录的独立入口为：

- `docs/current/AEGIS_FALLBACK_RETIREMENT_PREPARATION.md`

---

## 4. 如果目标是完整 Aegis，仍缺哪些层

### 4.1 Host Adapters

当前还没有正式的：

- host event normalization
- transcript / tool / diff / test evidence ingestion contract
- host-facing projection output contract

换句话说，当前仓能让宿主“像 Aegis 一样工作”，但还没有把宿主事件收敛成统一治理输入的正式适配层。

### 4.2 Runtime Core

当前还没有正式的：

- authoritative baseline truth
- policy snapshot
- authoritative impact analysis
- evidence sufficiency judgment
- gate decision
- completion authority

这整层必须独立建设，不能继续往 method-pack 仓里塞。

---

## 5. 建议优先级

如果你下一步是“把当前仓投入实际生产使用”，推荐顺序是：

1. 多宿主 release-level fresh install 回归
2. 真实团队任务样本验证
3. release / rollback 手册
4. fallback 观察与退役计划

如果你下一步是“先把当前仓做成可开源的 method-pack”，推荐顺序是：

1. 文档与测试同步回归
2. release / rollback 手册
3. host compatibility matrix snapshot
4. fallback 观察与退役计划
5. 非 live representative scenario strengthening

对应的开源发布 gap 入口为：

- `docs/current/AEGIS_OPEN_SOURCE_READINESS_GAPS.md`

如果你下一步是“继续做完整 Aegis”，推荐顺序是：

1. 先写 `adapter-facing contracts`
2. 再拆 `Host Adapters`
3. 最后独立建设 `Runtime Core`

---

## 6. 风险提示

### 6.1 不要把当前可用 method-pack 误判成 full platform

这是当前最大的认知风险。

### 6.2 不要为了追求“生产感”把 host logic 反向抬进 baseline

宿主兼容问题只能在 host docs / plugin owners / adapter contracts 解决，不能把 method baseline 写脏。

### 6.3 不要跳过 live 样本验证

fixture 证明结构成立，live 样本才证明日常生产使用的摩擦点已经暴露。

---

## 7. 当前 verdict

基于 `2026-04-28` 的 fresh evidence，当前 verdict 为：

- **Aegis Method Pack**：可以开始进入受控生产使用准备，但还建议补 3 项 rollout / live-validation work
- **Aegis Method Pack / open-source-first path**：可以先进入 method-pack strengthening 与开源准备，真实环境回归可后置到 production rollout 前
- **完整 Aegis**：尚未进入生产阶段，仍缺 `Host Adapters + Runtime Core`
