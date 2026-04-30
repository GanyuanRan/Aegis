# Aegis Repo Development Guardrails

状态：`Approved`

## 1. 本文件作用

本文档是当前 `Aegis` 仓库的本地开发入口护栏。

它负责统一以下事情：

- 当前仓库是什么，不是什么
- 后续二次开发应先看哪些 authority docs
- 当前阶段到底允许做什么，不允许做什么
- 如何避免把 `ADD / TLREF / 双轨治理` 融合工作做偏

它不替代：

- `docs/current/README.md` 的 authority order
- `docs/current/AEGIS_PROCESS_BASELINE.md` 的方法层流程
- `docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md` 的双轨治理规则
- 已安装 Aegis skills 的任务执行 workflow
- `CLAUDE.md` 的 upstream PR 纪律
- future runtime core 的 authoritative decision

换句话说：本文档只定义本仓边界与入口顺序，不复制 Aegis 通用执行细节。

---

## 2. 首次进入仓库时的阅读顺序

除非任务非常局部，否则进入本仓先按以下顺序对齐：

1. `docs/current/README.md`
2. `docs/current/AEGIS_TARGET_STATE.md`
3. `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
4. 与当前任务直接相关的 `docs/current/*.md`
5. 如果任务属于当前激活切片，再读：
   - `docs/current/AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md`
6. 如果目标涉及 upstream 提交或对外 PR，再读：
   - `CLAUDE.md`

如果这些文档之间出现冲突，按 `docs/current/README.md` 定义的 authority order 裁决。

---

## 3. 当前仓库定位

当前仓库的正式定位是：

> `Aegis Method Pack (runtime-ready)`

这意味着当前仓库负责：

- skills
- initial instructions
- workflow discipline
- runtime-ready artifacts 的 draft / hint / projection
- 多宿主 plugin-installable 分发骨架

这也意味着当前仓库不负责：

- authoritative runtime core
- authoritative `GateDecision`
- `completion authority`
- 把宿主执行结果直接当成治理最终真相

任何把当前仓写成 runtime core 的文档、skill 或实现，都视为偏航。

---

## 4. 当前批准的开发顺序

当前仓库已完成：

- `Phase 1：Authority Completion`
- `Phase 2：Skill Upgrade Wave 1`
- `Phase 3：Skill Upgrade Wave 2`
- `Phase 4：Compatibility Review`

经用户批准，当前已进入：

- `Phase 5：Runtime-ready Hardening`
- `Phase 5：completed within current method-pack scope`

继续推进 production strengthening work 或下一阶段前，先确认并回读：

1. `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`
2. `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
3. `docs/current/AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md`
4. `docs/current/AEGIS_PHASE5_E2E_BASELINE_RUN.md`
5. `docs/current/AEGIS_PHASE5_E2E_COMPLETION_RECORD.md`
6. `docs/current/AEGIS_PHASE5_COMPLETION_RECORD.md`
7. `docs/current/AEGIS_PRODUCTION_READINESS_GAPS.md`

进入任何后续阶段前先读：

- `docs/current/AEGIS_PHASE2_WAVE1_COMPLETION_RECORD.md`
- `docs/current/AEGIS_PHASE3_WAVE2_COMPLETION_RECORD.md`
- `docs/current/AEGIS_PHASE4_COMPATIBILITY_REVIEW_ATOMIC_PLAN.md`
- `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`

在用户批准下一阶段前，不要提前扩到：

- future runtime core
- host adapter 实现
- `subagent-driven-development`
- `executing-plans`
- 全量 skills 重写

`Phase 5` 之后的默认路线也要明确区分：

- 可以先做：method-pack strengthening、开源准备、非 live rollout work
- 可以后置：真实环境回归、真实团队任务样本验证
- 不自动激活：完整 platform、host adapters、runtime core

---

## 5. 不可偏移的融合原则

### 5.1 ADD / TLREF 融合原则

- 把 `TLREF / DIVE / Reflection / QA` 作为 method-pack 主脊柱
- 把 `ADD` 的高价值部分落成 baseline-first、evidence-driven、impact-aware 的 workflow
- 把 runtime-ready artifacts 维持为 `draft / hint / projection`
- 不把方法层纪律误包装成 authoritative runtime power

### 5.2 `aegis` 保留原则

二次开发不能破坏原有高价值能力，尤其包括：

- skills 分发模型
- workflow 触发骨架
- 多宿主安装说明骨架
- plugin / marketplace / repo-install 的可分发能力

### 5.3 分层原则

- portable method rules -> `docs/current/` 与 skills
- host / profile rules -> host docs 或 host-specific profile
- repo contribution rules -> 本仓入口文档与贡献文档

不要把这三层重新混成一个大 prompt。

---

## 6. 当前开发硬约束

### 6.1 Baseline First

先读 baseline，再改 skill；先收敛边界，再增强能力。
创建 ADR 前需通过 `docs/adr/ADR-CREATION-GATE.md` 三条件核验。

### 6.2 Minimal Change

优先最小必要改动。当前切片只改 canonical owner 文件；只有出现证据化冲突时，才扩到 supporting docs。

### 6.3 Dual-Track by Default

对以下任务默认触发 Aegis 双轨治理 workflow，执行细节以 `docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md`
与相关 Aegis skill 为准：

- bug 修复
- 架构重构
- 链路治理
- contract 调整

本文件只保留触发边界：严禁只加新文字、新分支、新 fallback，而不交代旧逻辑去留。

### 6.4 No Authority Drift

当前仓可以输出：

- draft
- hint
- advisory
- verification evidence

当前仓不可以输出：

- authoritative `GateDecision`
- authoritative `completion granted`
- authoritative `PolicySnapshot`

### 6.5 Plugin-Installable Is a Hard Requirement

任何改造都不得破坏：

- `docs/README.codex.md`
- `docs/README.opencode.md`
- `tests/opencode/`
- `tests/codex-plugin-sync/`

所代表的多宿主安装与分发能力。

---

## 7. 当前阶段实施要求

如果当前任务属于 `Phase 5` 之后的 production strengthening work，默认按以下方式执行：

1. 先读 `AEGIS_PHASE4_COMPLETION_RECORD.md`
2. 以 `Phase 5 completion records + production readiness gaps` 为输入基线
3. 先读 `AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md`
4. 默认先复用已完成的 E2E 验收骨架，再扩展新的 rollout-strengthening 验证
5. 每完成一个切片，就做一次：
   - baseline / skill 回读
   - fresh bootstrap 验证
   - 修复轨回望
   - 退役轨回望

如果当前目标不是“立刻投入日常生产 rollout”，而是“先把 method-pack 做成可开源、可验证、可继续扩展的稳定方法包”，则默认优先顺序改为：

1. 文档与安装说明回读
2. release / rollback 手册补齐
3. host compatibility matrix snapshot
4. fallback 治理记录
5. 非 live representative scenario strengthening

只有当用户明确要求进入真实生产 rollout 准备时，才把以下事项提升为当前切片主目标：

- 多宿主 release-level fresh install 回归
- 真实团队任务样本验证

如果未来进入完整 `Aegis` 平台建设，仍需保持当前仓边界不变：

- 当前仓继续作为 `Aegis Method Pack`
- `OpenCode + installed Aegis Method Pack` 可以作为优先宿主壳候选之一
- `Host Adapters + Runtime Core` 必须在新的 approved plan 中独立展开

如果某个想法需要新增结构、跨越当前激活的 bootstrap 边界、或影响 runtime boundary，
先回写 baseline docs，再等待用户确认是否进入后续切片。

---

## 8. 对外提交说明

本文件约束的是当前 fork 的开发方向。

如果后续要把某部分能力向 upstream 提交：

1. 先确认该改动不是 fork-specific
2. 先确认没有破坏 upstream 的 zero-dependency / plugin philosophy
3. 先完整阅读 `CLAUDE.md`
4. 按 `CLAUDE.md` 的标准补齐证据、PR 模板与人工审阅

换句话说：

- `AGENTS.md` 管当前 fork 的改造不跑偏
- `CLAUDE.md` 管对 upstream 提交时不翻车
