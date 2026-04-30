# Aegis Transformation Execution Plan

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis` 当前整体改造的实施顺序。

---

## 2. 执行目标

目标不是一次性重写整个 `superpowers`，而是按 authority-first 路径分阶段收敛：

1. 文档和边界先稳定
2. 高杠杆 skills 先升级
3. runtime-ready artifacts 固定
4. 先完成 method-pack 侧的 release / open-source strengthening
5. 再考虑 adapter / core 对接

---

## 3. Phase Order

### Phase 1：Authority Completion

补齐：

- transformation architecture
- product requirements
- rule layering
- dual-track governance
- artifact schema baseline

### Phase 2：Skill Upgrade Wave 1

优先改：

1. `brainstorming`
2. `systematic-debugging`
3. `verification-before-completion`

### Phase 3：Skill Upgrade Wave 2

继续改：

1. `writing-plans`
2. `requesting-code-review`

### Phase 4：Compatibility Review

检查：

- 原有 `superpowers` 能力是否仍在
- plugin-installable 属性是否仍成立
- 是否出现 host-specific 反向污染 baseline

### Phase 5：Runtime-ready Hardening

检查：

- artifacts 是否稳定
- dual-track 是否实际进入交付
- 是否可进入 future adapter/core 对接准备

---

## 4. 每阶段最低验证

每个阶段至少完成：

- baseline / spec 回看
- 兼容性检查
- 修复轨 + 退役轨回望
- 风险与回滚说明

---

## 5. 当前阶段结论

当前仓处于：

- `Phase 1 complete`
- `Phase 2 complete`
- `Phase 3 complete`
- `Phase 4 complete`
- `Phase 5 complete within current method-pack scope`

也就是说，兼容性回看阶段已完成，`Phase 5 / Runtime-ready Hardening`
中的 `E2E 验收框架` 已完成，且 artifacts stability、dual-track delivery、
adapter/core handoff preparation 已在当前 method-pack scope 内完成收口。

---

## 6. 当前激活计划

当前最新实施切片的正式计划为：

- `docs/current/AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md`

该计划负责：

- 保留 E2E 验收框架的 authority 对齐与 bootstrap skeleton
- 给 `tests/e2e/` 提供 Layer 1 / Layer 2 / Layer 3 owners、host profile 与可运行入口
- 为 Phase 5 后续切片提供可继续扩展的统一验收骨架

当前切片的收口记录为：

- `docs/current/AEGIS_PHASE5_E2E_BASELINE_RUN.md`
- `docs/current/AEGIS_PHASE5_E2E_COMPLETION_RECORD.md`
- `docs/current/AEGIS_PHASE5_COMPLETION_RECORD.md`

前一实施切片的收口记录为：

- `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`

如果后续继续推进，应不再沿用“Phase 5 未完成”的口径，而应从以下两个入口中择一：

1. `docs/current/AEGIS_PRODUCTION_READINESS_GAPS.md` 中定义的 rollout strengthening work
2. future `adapter/core` 方向的新 approved plan

---

## 7. Phase 5 之后的默认推进路线

`Phase 5` 收口后，当前默认路线不是直接进入完整平台实现，而是：

1. 先做 `Aegis Method Pack` 的 release-strengthening 与 open-source readiness
2. 先把不依赖真实环境回归的工作做完
3. 把真实环境回归、真实团队任务样本验证放到“宣布日常生产 rollout”之前
4. 只有当 method-pack 在开源与真实使用中证明有持续价值时，才批准进入完整 `Aegis` 平台建设

当前允许优先推进的工作包括：

- docs / testing / install wording 回读与收敛
- release checklist / rollback checklist
- host compatibility matrix snapshot
- known limitations / compatibility fallback 治理记录
- 非 live 的 representative scenario strengthening

当前不自动激活的工作包括：

- 完整 `Host Adapters` 实现
- 完整 `Runtime Core` 实现
- 把 `OpenCode` 或其他宿主逻辑反向抬进 method-pack baseline

若未来进入完整平台建设，推荐方向仍是：

- 保持 `Aegis Method Pack` 独立分发
- 以已安装 `Aegis Method Pack` 的 `OpenCode` 作为优先宿主壳候选之一
- 在独立 approved plan 中展开 `Host Adapters + Runtime Core`
