# Aegis Fallback Retirement Preparation

状态：`Reviewed`

## 1. 文档定位

本文档记录当前 `Aegis Method Pack` 中仍被保留的 compatibility fallback，以及它们的后续退役准备入口。

本文档只负责回答以下问题：

- 当前有哪些 fallback 仍被保留
- 它们为什么还能保留
- 后续该看什么指标来判断是否可以退役
- 退役前最低需要补哪些验证

本文档不负责：

- 直接宣布某个 fallback 已经可以删除
- 把 method-pack fallback 写成 runtime core 或 host adapter 契约
- 替代 `AEGIS_KNOWN_LIMITATIONS.md` 或 completion records 的证据作用

---

## 2. 当前结论

截至 `2026-04-28`，当前需要进入退役准备管理的主要对象为：

1. `OpenCode config.skills.paths compatibility fallback`
2. `Codex Git Bash representative smoke` 相关的观察性兼容保留

其中：

- `OpenCode config.skills.paths compatibility fallback` 是当前唯一仍处于主线阅读范围内、且明确需要 future retirement validation 的宿主兼容 fallback。
- `Codex Git Bash representative smoke` 更准确地说是环境稳定性观察对象，不是新的 discovery fallback；它仍应留在 `AEGIS_KNOWN_LIMITATIONS.md` 中管理。

---

## 3. Active Retirement Preparation Set

### 3.1 OpenCode config fallback

**保留对象**
- OpenCode `config.skills.paths` compatibility fallback

**当前状态**
- 不是 canonical discovery chain
- 当前 canonical chain 已切到宿主官方支持的全局 skills path
- fallback 仅作为兼容层保留

**保留原因**
- 仍缺少跨版本 fresh evidence，证明目标 OpenCode 版本集合都不再需要该兼容层

**观察指标**
- `bash tests/opencode/run-tests.sh --integration`
- 真实 fresh install 验证
- `AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md` 中的宿主 verdict 是否扩大到多版本 / 更多真实安装样本

**退役触发条件**
- 目标 OpenCode 版本集合完成真实验证，且 native global skills path 在这些版本上稳定提供所需 discovery 行为

**退役前最低验证**

```bash
bash tests/opencode/run-tests.sh --integration
bash tests/e2e/run-all.sh --full --host-profile fast
```

同时回读：

1. `docs/README.opencode.md`
2. `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
3. `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`

---

## 4. Reading Order

如果 fallback 信息同时出现在：

- `AEGIS_PHASE5_COMPLETION_RECORD.md`
- `AEGIS_PRODUCTION_READINESS_GAPS.md`
- `AEGIS_KNOWN_LIMITATIONS.md`
- 本文档

读取顺序为：

1. 本文档：看“后续是否要推进 retirement preparation”
2. `AEGIS_KNOWN_LIMITATIONS.md`：看“当前为什么仍保留”
3. `AEGIS_PHASE5_COMPLETION_RECORD.md`：看“保留结论来自什么 fresh evidence”

---

## 5. Current Architecture Guardrail

处理 fallback retirement preparation 时，必须保持以下边界：

1. 不把 compatibility fallback 当成 canonical product capability
2. 不为了“先删掉 fallback”而牺牲当前 verified host path
3. 不把宿主兼容处理反向抬进 method-pack baseline
4. 不在缺少 fresh evidence 的情况下宣布 retirement 已完成
