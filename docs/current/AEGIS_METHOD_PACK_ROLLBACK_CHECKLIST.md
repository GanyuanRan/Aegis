# Aegis Method Pack Rollback Checklist

状态：`Reviewed`

## 1. 文档定位

本文档定义 `Aegis Method Pack` 当前 release 出现问题时的最小 rollback checklist。

它只处理 method-pack 范围内的回滚，不处理：

- 完整平台运行时回滚
- 远端 host adapter 服务回滚
- runtime core policy rollback

---

## 2. Rollback Triggers

出现以下任一情况时，应启动 rollback 判断：

1. `tests/e2e/run-all.sh --full --host-profile fast` 在 release 后不可复现通过
2. 宿主安装链路出现 regression
3. skill discovery / priority / plugin sync 出现 regression
4. 发布后发现 authority drift 或 boundary drift

---

## 3. Rollback Scope

当前 rollback 默认只回到最近一个：

- 已验证通过的 method-pack 文档与技能状态
- 已验证通过的宿主说明状态
- 已验证通过的测试入口状态

不在当前文档里直接定义 git 操作命令，而是要求先识别：

1. 哪个 canonical owner 出问题
2. 是否只是 supporting doc drift
3. 是否涉及 plugin-installable 主链

---

## 4. Rollback Readback

回滚前先回读：

1. `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`
2. `docs/current/AEGIS_PHASE5_COMPLETION_RECORD.md`
3. `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
4. `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

目标是确认问题属于：

- 已知 limitation
- 新 regression
- 环境 blocker

---

## 5. Rollback Decision Matrix

### 5.1 文档 drift

如果问题只是 README / testing docs wording 漂移：

- 直接回滚对应文档 owner
- 不扩大到技能或测试脚本 owner

### 5.2 测试 / smoke regression

如果问题是：

- Codex representative smoke regression
- OpenCode base suite regression
- plugin sync regression

则先回滚对应 canonical owner：

- `tests/skill-triggering/*`
- `tests/opencode/*`
- `scripts/sync-to-codex-plugin.sh`

### 5.3 Boundary drift

如果问题是 authority drift / boundary drift：

- 优先回滚最近引入越权表述或越权逻辑的 canonical owner
- 同时更新 known limitations 或 release notes，说明阻断原因

---

## 6. Minimum Rollback Verification

每次 rollback 后至少重新跑：

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

如果回滚命中了特定宿主链路，再补：

```bash
bash tests/opencode/run-tests.sh
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

---

## 7. Rollback Record Requirements

每次 rollback 至少要记录：

1. 触发条件
2. 受影响 canonical owner
3. 回滚后的 fresh verification
4. 是否只是恢复旧状态，还是还需后续修复

---

## 8. Architecture Review

回滚后的架构回望要回答：

- 是否恢复了 `Method Pack` 边界
- 是否恢复了 plugin-installable 主链
- 是否把环境 blocker 与产品 regression 重新分开

如果这三点都没有恢复，rollback 不能算完成。
