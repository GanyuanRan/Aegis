# Aegis Method Pack Strengthening Atomic Plan

状态：`Completed`

## 1. 文档定位

本文档定义 `Phase 5` 收口之后、完整平台建设之前的当前激活切片：

> `Aegis Method Pack Strengthening`

本文档只负责回答以下问题：

- 在不进入真实环境回归的前提下，当前还能先做哪些高价值 strengthening work
- 哪些 release / rollback / compatibility / limitation 资产需要成为正式 owner
- 如何在不越过 `Method Pack` 边界的情况下，为后续开源与受控 rollout 做准备
- 这一切片如何验证与如何做架构回望

本文档不负责回答以下问题：

- 真实团队 live 样本验证的具体执行记录
- 多宿主 release-level fresh install 回归的最终 closeout
- `Host Adapters` 的正式实现
- `Runtime Core` 的正式实现

---

## 2. 当前结论

当前仓库已完成：

- `Phase 1：Authority Completion`
- `Phase 2：Skill Upgrade Wave 1`
- `Phase 3：Skill Upgrade Wave 2`
- `Phase 4：Compatibility Review`
- `Phase 5：Runtime-ready Hardening completed within current method-pack scope`

经用户批准，当前激活切片为：

> **先做不依赖真实环境回归的 method-pack strengthening work；真实环境回归后置。**

因此，本切片当前只允许覆盖：

1. method-pack 开源与受控 rollout 所需的治理文档 owner
2. release / rollback / compatibility / limitations 资产补齐
3. 非 live 验证入口与现有文档 wording 的收敛

当前明确不自动激活：

- 真实团队任务 live 样本
- 多宿主 fresh install release closeout
- 完整平台 implementation
- `OpenCode` 宿主侧深度二开

---

## 3. 切片交付目标

本切片完成时，必须同时满足以下目标：

1. 当前仓拥有正式的 method-pack release checklist owner
2. 当前仓拥有正式的 rollback checklist owner
3. 当前仓拥有正式的 host compatibility matrix snapshot owner
4. 当前仓拥有正式的 known limitations / fallback governance owner
5. `docs/testing.md`、`docs/README.codex.md`、`docs/README.opencode.md` 与上述 owner 没有明显 wording 冲突
6. 有一轮 fresh 非 live aggregate verification 证明：
   - Layer 1 / 2 / 3 fast-profile 通过
   - boundary compliance 通过
   - artifact schema 通过
   - representative host-native smoke 没有退化
7. 本切片收口后，当前仓仍严格停留在 `Aegis Method Pack (runtime-ready)` 边界内

---

## 4. Canonical Owners

### 4.1 新增 canonical owners

- `docs/current/AEGIS_METHOD_PACK_STRENGTHENING_ATOMIC_PLAN.md`
  - 当前切片计划 owner
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
  - method-pack 发布检查清单 owner
- `docs/current/AEGIS_METHOD_PACK_ROLLBACK_CHECKLIST.md`
  - method-pack 回滚检查清单 owner
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
  - 当前宿主兼容矩阵快照 owner
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
  - 当前已知限制、fallback 保留原因与退役触发条件 owner

### 4.2 Supporting owners

- `docs/testing.md`
  - 当前测试矩阵与非 live 验证入口说明
- `docs/README.codex.md`
  - Codex 宿主安装、分发与故障排查说明
- `docs/README.opencode.md`
  - OpenCode 宿主安装、分发与故障排查说明
- `docs/current/AEGIS_PRODUCTION_READINESS_GAPS.md`
  - 当前 gap judgment 与后置项说明
- `AGENTS.md`
  - 当前 fork 的开发方向护栏

---

## 5. 原子实施切片

### Slice 1：Method-pack strengthening baseline 固化

**目标：**

- 把“先做 method-pack、后置真实环境回归”的当前策略落成正式执行计划

**涉及文件：**

- 创建：`docs/current/AEGIS_METHOD_PACK_STRENGTHENING_ATOMIC_PLAN.md`
- 回读：`docs/current/AEGIS_TARGET_STATE.md`
- 回读：`docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
- 回读：`docs/current/AEGIS_PRODUCTION_READINESS_GAPS.md`
- 视需要修改：`docs/current/README.md`

**修复轨：**

1. 真实根因
   - 当前策略已被认可，但尚未有一个专门针对 method-pack strengthening 的 atomic owner。
2. 唯一 canonical owner
   - `docs/current/AEGIS_METHOD_PACK_STRENGTHENING_ATOMIC_PLAN.md`
3. 最小必要改动
   - 只新增本计划并回挂现有 authority docs，不改变既有 phase closeout verdict。
4. 兼容边界
   - 不得把 strengthening 文档写成 full-platform 实施计划。
5. 验证方式
   - current docs 回读后，当前切片 owner 清晰可追踪。

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 零散分布在 `AEGIS_PRODUCTION_READINESS_GAPS.md`、`AGENTS.md`、会话结论中的 strengthening 描述。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 作为当前阶段真实判断来源。
4. 删除触发条件
   - 当本计划成为当前切片的统一 owner 后。
5. 删除前验证清单
   - 不得丢失后置项与当前优先项的边界结论。

---

### Slice 2：Release / rollback 资产补齐

**目标：**

- 给 method-pack 开源与受控 rollout 建立最小发布 / 回滚手册

**涉及文件：**

- 创建：`docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- 创建：`docs/current/AEGIS_METHOD_PACK_ROLLBACK_CHECKLIST.md`
- 回读：`docs/README.codex.md`
- 回读：`docs/README.opencode.md`
- 回读：`docs/testing.md`

**修复轨：**

1. 真实根因
   - 当前已有验证与安装骨架，但没有明确的 release / rollback canonical owner。
2. 唯一 canonical owner
   - `AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
   - `AEGIS_METHOD_PACK_ROLLBACK_CHECKLIST.md`
3. 最小必要改动
   - 只写 method-pack 范围内 checklist，不扩展到 runtime core 或 host adapter rollout。
4. 兼容边界
   - 不得把 “开源准备” 写成 “完整平台发布”。
5. 验证方式
   - checklist 中的命令、owner、阻断点与现有文档一致。

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 散落在 README、testing docs 和 completion records 的操作说明。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 作为细节来源与证据来源。
4. 删除触发条件
   - 当 release / rollback owner 完整收敛后。
5. 删除前验证清单
   - README / testing docs 不丢失必要入口。

---

### Slice 3：Compatibility snapshot 与 known limitations

**目标：**

- 把当前 method-pack 宿主兼容状态和已知限制写成权威快照

**涉及文件：**

- 创建：`docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- 创建：`docs/current/AEGIS_KNOWN_LIMITATIONS.md`
- 回读：`docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`
- 回读：`docs/current/AEGIS_PHASE5_COMPLETION_RECORD.md`
- 回读：`docs/current/AEGIS_PRODUCTION_READINESS_GAPS.md`

**修复轨：**

1. 真实根因
   - 当前兼容性状态与限制结论大多还在 completion records / gap docs 中，没有一个专门的 snapshot owner。
2. 唯一 canonical owner
   - `AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
   - `AEGIS_KNOWN_LIMITATIONS.md`
3. 最小必要改动
   - 只沉淀当前 fresh-evidence 支撑的 host verdict 与 limitations，不推断未验证宿主。
4. 兼容边界
   - 不得把 snapshot 写成“所有支持 plugin 的宿主都已正式通过”。
5. 验证方式
   - snapshot 中每条结论都能回指到 owner doc 或 fresh verification path。

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - `Phase 4`、`Phase 5` completion records 与 `AEGIS_PRODUCTION_READINESS_GAPS.md`。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 它们仍是证据记录。
4. 删除触发条件
   - 当 snapshot / known limitations 成为统一阅读入口后。
5. 删除前验证清单
   - 不得丢失具体命令、通过状态、fallback 保留原因。

---

### Slice 4：Docs wording 收敛与非 live 验证

**目标：**

- 确认宿主 README、testing docs 与新增 owners 一致，并完成一轮 aggregate fast verification

**涉及文件：**

- 视需要修改：`docs/testing.md`
- 视需要修改：`docs/README.codex.md`
- 视需要修改：`docs/README.opencode.md`
- 回读：`tests/e2e/run-all.sh`
- 回读：`tests/e2e/layer1-fast-check.sh`

**修复轨：**

1. 真实根因
   - 当前 wording 与验证入口已经大体一致，但新增 owner 文档后仍需做一次显式收敛。
2. 唯一 canonical owner
   - `docs/testing.md`
3. 最小必要改动
   - 只有在 wording 与当前 owner 冲突时才窄改 supporting docs。
4. 兼容边界
   - 不新增新的宿主承诺，不修改 host runtime behavior。
5. 验证方式
   - `bash tests/e2e/run-all.sh --full --host-profile fast`

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - README 与 testing docs 中可能仍有尚未显式指向新 owner 的零散表述。
2. 是否仍在主链生效
   - 需视回读结果而定。
3. 保留它的唯一理由
   - 仅在不与新 owner 冲突时保留。
4. 删除触发条件
   - 新 owner 已能完整覆盖该信息。
5. 删除前验证清单
   - aggregate fast verification 通过。

---

## 6. 验证矩阵

本切片的最低 fresh verification 为：

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

必要时补充回读验证：

```bash
rg -n "release checklist|rollback checklist|compatibility matrix|known limitations" docs/current
```

---

## 7. 风险与边界

### 7.1 当前刻意后置的事项

- 多宿主 release-level fresh install 回归
- 真实团队任务 live 样本验证
- 完整平台实现与宿主深度二开

### 7.2 当前最大风险

- 把“开源 readiness”误解成“完整生产 readiness”
- 把 snapshot 写成未验证宿主的正式通过结论
- 为了补文档 owner 而反向污染 method-pack 边界

---

## 8. 当前完成标准

当以下条件都满足时，本切片可收口：

1. 新增 4 类 strengthening owner 文档已落盘
2. supporting docs 与新 owner 没有明显冲突
3. 至少一轮 `tests/e2e/run-all.sh --full --host-profile fast` fresh pass
4. 架构回望确认当前仓仍然只是 `Aegis Method Pack (runtime-ready)`

---

## 9. 收口记录

本切片的当前收口记录位于：

- `docs/current/AEGIS_METHOD_PACK_STRENGTHENING_COMPLETION_RECORD.md`

如果后续需要继续推进 production rollout 准备或新的 strengthening work，应先回读该收口记录，再决定是否激活新切片。
