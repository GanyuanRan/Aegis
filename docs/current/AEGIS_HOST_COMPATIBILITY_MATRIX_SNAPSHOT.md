# Aegis Host Compatibility Matrix Snapshot

状态：`Reviewed`

## 1. 文档定位

本文档记录当前 `Aegis Method Pack` 的宿主兼容性快照。

它回答的是：

- 哪些宿主已有 fresh evidence
- 哪些宿主只有结构性目标，没有当前 fresh verification
- 当前 compatibility verdict 的读取顺序是什么

它不回答：

- 所有宿主的永久支持承诺
- 完整平台级别的运行时兼容性

---

## 2. Snapshot Date

当前快照基于 `2026-04-30` 已落盘的 fresh evidence 与 current docs。

---

## 3. Current Verdict

### 3.1 已有 fresh evidence 的宿主

| Host | Current Verdict | Evidence Owner |
| --- | --- | --- |
| `Codex` | representative smoke 主链可用；Git Bash 下 naive smoke 仍需观察 | `docs/testing.md`, `tests/skill-triggering/*`, `tests/explicit-skill-requests/*`, `docs/current/AEGIS_KNOWN_LIMITATIONS.md` |
| `OpenCode` | base suite 与 integration closeout 已通过 | `docs/testing.md`, `tests/opencode/*`, `docs/README.opencode.md` |

### 3.2 仍未形成当前 fresh release verdict 的宿主

| Host | Current Status | Why Not Yet |
| --- | --- | --- |
| `Claude Code` | 已有安装引导与 plugin skeleton；尚无当前 release-level fresh smoke verdict | `docs/README.claude-code.md` 已建立，但真实宿主回归仍后置 |
| `Cursor` | 尚无当前 fresh release-level verdict | 未进入当前切片 |
| `Gemini CLI` | 尚无当前 fresh release-level verdict | 未进入当前切片 |

---

## 4. What This Snapshot Means

当前快照只说明：

1. `Codex` 与 `OpenCode` 是当前最有 fresh evidence 的两条主链
2. 当前 method-pack 仍保留跨宿主安装目标
3. “支持所有 plugin host” 仍是产品目标，不等于“所有宿主都已有当前 fresh closeout”

---

## 5. Evidence Sources

读取当前宿主 verdict 时，按以下顺序：

1. `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`
2. `docs/current/AEGIS_PHASE5_COMPLETION_RECORD.md`
3. `docs/testing.md`
4. `docs/README.claude-code.md`
5. `docs/README.codex.md`
6. `docs/README.opencode.md`

---

## 6. Compatibility Boundary

当前 snapshot 只覆盖：

- method-pack 安装与分发
- skill discovery / representative triggering
- plugin loading / priority / distribution sync

当前 snapshot 不覆盖：

- runtime core integration
- host adapter event normalization
- 完整 live production workflow orchestration

---

## 7. Architecture Review

阅读本快照时必须避免三种误判：

1. 把 `Codex + OpenCode` 的当前通过，误判成“全宿主都已正式 closeout”
2. 把 current smoke / integration verdict，误判成 full-platform readiness
3. 把宿主兼容性工作反向提升成 method-pack authority
