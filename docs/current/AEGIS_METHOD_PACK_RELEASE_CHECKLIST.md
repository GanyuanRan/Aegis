# Aegis Method Pack Release Checklist

状态：`Reviewed`

## 1. 文档定位

本文档定义当前 `Aegis Method Pack` 在开源发布或受控发布前的最小 release checklist。

本文档只适用于：

- `Aegis Method Pack (runtime-ready)`
- 多宿主 plugin-installable 分发骨架

本文档不适用于：

- 完整 `Aegis Platform`
- `Host Adapters`
- `Runtime Core`

---

## 2. Release Gate

在执行任何正式 release 前，必须逐项确认：

1. 当前 release 目标仍是 `Aegis Method Pack`
2. 当前 authority docs 没有把本仓误写成 full platform
3. 当前宿主安装说明与测试说明可回指到真实 owner
4. 当前 known limitations 已回写，而不是藏在会话结论里

---

## 3. Baseline Readback

发布前必须回读：

1. `docs/current/README.md`
2. `docs/current/AEGIS_TARGET_STATE.md`
3. `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
4. `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
5. `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
6. `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md`

如果这些文档之间有冲突，以 `docs/current/README.md` 的 authority order 裁决。

---

## 4. Required Verification

当前 method-pack release 的最低 fresh verification：

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

如果本次发布明确包含 OpenCode runtime 侧变更，建议补：

```bash
bash tests/opencode/run-tests.sh --integration
```

如果本次发布明确包含 Codex 分发链变更，建议补：

```bash
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

如果当前机器默认 `bash` 指向 WSL launcher 而不是可用的 Git Bash，或 Git Bash 下已知 smoke 时延仍存在，
应把它记录进 `AEGIS_KNOWN_LIMITATIONS.md`，不要把环境与时延 blocker 误判成 method-pack 边界退化。

---

## 5. Required Doc Checks

发布前必须回读以下宿主文档：

1. `docs/README.codex.md`
2. `docs/README.opencode.md`
3. `docs/testing.md`

确认：

- 安装方式没有引用过时路径
- host-specific fallback 没有被误写成 canonical chain
- testing docs 与 current owners 的命名一致

---

## 6. Artifact / Boundary Checks

发布前必须确认：

1. `Aegis` 产出的仍是 `draft / hint / projection`
2. 没有新增 authoritative `GateDecision`
3. 没有新增 authoritative `completion authority`
4. 没有把单宿主实现逻辑抬成 baseline

可直接依赖以下检查：

```bash
bash tests/e2e/boundary-compliance-check.sh
bash tests/e2e/artifact-schema-check.sh
```

---

## 7. Release Output Package

一次 method-pack release 至少要同时包含：

1. 可安装仓库状态
2. 宿主安装说明
3. testing docs
4. compatibility snapshot
5. known limitations
6. release notes or tag notes

---

## 8. Stop Conditions

出现以下任一情况时，本次 release 应停止：

1. `tests/e2e/run-all.sh --full --host-profile fast` 失败
2. 权威文档对当前仓定位出现冲突
3. README 与 testing docs 明显背离当前 canonical owners
4. 当前 release 想要承诺完整平台能力

---

## 9. Architecture Review

发布前最后一次架构回望要回答：

- 当前 release 是否仍只发布 `Method Pack`
- 当前 release 是否维持了 plugin-installable 属性
- 当前 release 是否把真实环境回归后置项误包装成“已完成”

只有这三个问题都能得到明确的 `yes / no` 结论，并且没有 authority drift，才允许继续。
