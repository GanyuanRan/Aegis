# Aegis Open-Source Readiness Gaps

状态：`Reviewed`

## 1. 文档定位

本文档回答以下问题：

1. 如果目标是“先开源 `Aegis Method Pack`”，当前还差哪些工作
2. 哪些事项是开源发布前建议补齐的
3. 哪些事项可以继续后置到真实 production rollout 前

本文档不授予 release authority；它只提供当前 open-source-first 路径下的 gap judgment。

---

## 2. 结论先行

基于 `2026-04-29` 当前 fresh evidence，结论是：

> **当前仓已经具备 method-pack 开源准备的主体基线。经过本轮入口同步、readback 与完整 fresh verification 后，当前仓已进入 `method-pack open-source release preparation ready for user-governed final decision` 状态。**

以下事项目前可以继续后置，不阻断开源优先路径：

- 多宿主 release-level fresh install 回归
- 真实团队 live 样本验证
- 完整 `Aegis Platform` 的 `Host Adapters + Runtime Core`

---

## 3. 已满足的开源基线

当前已经满足：

1. `Method Pack (runtime-ready)` 定位清晰
2. authority docs、ADR、baseline docs 已落盘
3. `Phase 2 / 3 / 4 / 5` 与 strengthening closeout 已有 fresh verification 支撑
4. plugin-installable 分发骨架仍然成立
5. release / rollback / compatibility / known limitations owners 已建立
6. fallback retirement preparation owner 已建立
7. 根部 README、宿主 README、testing docs 已开始回挂 current owners
8. `bash tests/e2e/run-all.sh --full --host-profile fast` 已在本轮正式 release readback 后 fresh pass

---

## 4. 开源发布前仍建议补齐的工作

### 4.1 文档与入口最终同步回读

建议确认以下入口之间没有旧 wording 残留：

- `README.md`
- `docs/README.codex.md`
- `docs/README.opencode.md`
- `docs/testing.md`
- `docs/current/README.md`

最关键的检查点是：

1. 没有把当前仓误写成 full platform
2. 没有把 host-specific fallback 写成 canonical chain
3. 没有把“支持的安装目标”误写成“所有宿主都已 fresh closeout”

### 4.2 Release checklist readback

当前最适合作为正式开源发布前最后一轮 readback 的 owner 是：

- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`

本轮已完成轻量 readback，确认了：

1. release gate 与当前 scope 一致
2. baseline readback 没有遗漏
3. supporting docs 与 current owners 没有新的 wording drift
4. release checklist 要求的最低 fresh verification 已完成

---

## 5. 可后置事项

如果当前目标是“先开源 method-pack，再决定是否继续做平台”，以下事项可以继续后置：

1. 多宿主 release-level fresh install 回归
2. 真实团队任务 live 样本验证
3. 更广宿主矩阵的真实 closeout

它们仍然重要，但更适合作为：

- production rollout 前工作
- 开源后的真实反馈吸收工作
- future platform investment 的决策输入

---

## 6. 当前距离正式开源发布的剩余工作清单

如果以“最小可发布 method-pack”作为目标，当前已经没有新的 formal pre-release verification blocker。

当前进入的是：

> `method-pack open-source release preparation ready for user-governed final decision`

仍然建议在正式发布说明中明确以下后置项，但它们不阻断当前开源优先路径：

1. 多宿主 release-level fresh install 回归
2. 真实团队任务 live 样本验证
3. 更广宿主矩阵的真实 closeout

---

## 7. 与 Production Gaps 的关系

`AEGIS_PRODUCTION_READINESS_GAPS.md` 回答的是：

- 距离日常生产 rollout 还差什么

本文档回答的是：

- 距离开源发布还差什么

如果用户当前明确目标是“先开源 method-pack”，优先读本文件；如果目标切回“稳态生产 rollout”，优先读 `AEGIS_PRODUCTION_READINESS_GAPS.md`。

---

## 8. Architecture Review

当前 open-source readiness 判断必须坚持：

1. 开源 readiness 不等于 production rollout readiness
2. 开源 method-pack 不等于完整 Aegis platform
3. 当前 repo 的价值在于方法层、artifact、治理与分发骨架，而不是提前承担 runtime authority
