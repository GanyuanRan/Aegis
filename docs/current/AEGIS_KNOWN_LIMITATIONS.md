# Aegis Known Limitations

状态：`Reviewed`

## 1. 文档定位

本文档记录当前 `Aegis Method Pack` 的已知限制、兼容 fallback、保留原因与退役触发条件。

它只记录当前 fresh evidence 支撑的限制项，不做未来推测。

---

## 2. 当前已知限制

### 2.1 当前仓不是完整平台

**保留对象**
- `Method Pack` 与 future `Host Adapters + Runtime Core` 的分层边界

**保留原因**
- 当前仓的正式定位就是 `Aegis Method Pack (runtime-ready)`，不是 full platform

**观察指标**
- current docs 是否仍把 outputs 限定为 `draft / hint / projection`

**退役时机**
- 只有未来完整平台在新的 approved plan 中独立展开后，才进入下一层，不是“删除此限制”

---

### 2.2 真实环境回归已后置

**保留对象**
- 多宿主 release-level fresh install 回归
- 真实团队任务 live 样本验证

**保留原因**
- 当前优先目标是 method-pack strengthening 与开源准备，不是立即宣布日常生产 rollout

**观察指标**
- `AEGIS_PRODUCTION_READINESS_GAPS.md` 中的后置项是否仍明确

**退役时机**
- 当用户明确要求进入 production rollout 准备时

---

### 2.3 OpenCode config fallback 仍保留

**保留对象**
- OpenCode `config.skills.paths` compatibility fallback

**保留原因**
- 当前 canonical chain 已切到宿主官方支持的全局 skills path，但仍缺跨版本证据证明 fallback 完全没有兼容价值

**观察指标**
- `bash tests/opencode/run-tests.sh --integration`
- 真实 fresh install 验证

**退役时机**
- 当目标 OpenCode 版本集合已证明 native global skills path 足够稳定时

---

### 2.4 当前 host snapshot 不是全宿主 release verdict

**保留对象**
- 当前只对 `Codex` 与 `OpenCode` 给出 fresh-evidence 驱动的主链 verdict

**保留原因**
- 其它宿主当前不在本切片验证范围内

**观察指标**
- `AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md` 是否仍明确区分“有 fresh evidence”与“尚未形成 current verdict”

**退役时机**
- 当其它宿主进入单独 approved slice 并完成 fresh closeout 时

---

### 2.5 Git Bash 下的 Codex smoke 时延与稳定性仍需单独观察

**保留对象**
- Git Bash / MSYS2 环境下的 Codex representative smoke

**保留原因**
- 当前已确认 Git Bash 下的 working-dir / cmd bridge 问题可以被收敛，但 representative Codex smoke 仍可能表现为：
  - explicit skill request 可通过，但耗时偏长
  - naive prompt smoke 在当前超时窗口内不稳定

**观察指标**
- `env SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh brainstorming ...`
- `env SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh brainstorming ...`
- `tests/helpers/codex-cli.sh` 的桥接与 parser 行为

**退役时机**
- 当 Git Bash 下 representative Codex smoke 在当前 runner 超时窗口内稳定通过时

---

## 3. Default Reading Rule

如果某个 limitation 同时出现在：

- completion record
- production gaps
- 本文档

以本文件作为“当前阅读入口”，以 completion record 作为“证据来源”。

---

## 4. Architecture Review

当前 limitation 管理的核心要求是：

1. 不隐瞒限制
2. 不把 limitation 写成永久缺陷
3. 不为了掩盖 limitation 而新增无退役计划的 fallback
