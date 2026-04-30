# Aegis Phase 5 Completion Record

状态：`Reviewed`

## 1. 文档定位

本文档记录 `Aegis Phase 5 / Runtime-ready Hardening` 的整体收口结论、fresh verification 证据、修复轨 / 退役轨回望，以及当前仍然存在的边界性风险。

本文档不替代以下 authoritative baseline：

- `docs/current/README.md`
- `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
- `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`

---

## 2. 阶段结论

`Phase 5 / Runtime-ready Hardening` 当前可判定为：

> `Completed within current method-pack scope`

这里的 `current method-pack scope` 明确指：

1. runtime-ready artifacts 稳定性
2. 双轨治理进入可验证交付
3. future adapter / runtime core handoff 所需的 method-pack 输入与宿主兼容性准备

本文档不支持以下更大的结论：

- 完整 `Aegis Platform` 已生产就绪
- 当前仓已拥有 runtime core 级 authority
- future host adapters 或 runtime core 已在当前仓落地

---

## 3. 事实

### 3.1 Artifacts stability

当前已有 fresh evidence 支撑以下事实：

1. `artifact schema fixtures` 在 Layer 1 fast check 中通过
2. Layer 2 / Layer 3 场景检查能稳定识别：
   - `TaskIntentDraft`
   - `BaselineReadSetHint`
   - `ImpactStatementDraft`
   - `EvidenceBundleDraft`
   - `GateInputPack`
3. 当前 artifacts 仍保持 `draft / hint / projection` 定位，没有越权漂移到 authoritative outputs

### 3.2 双轨治理已进入交付

当前已有 fresh evidence 支撑以下事实：

1. 场景 B transcript 分析通过
2. 场景 B 明确要求并实际检查：
   - `root cause`
   - `fix track`
   - `retirement track`
3. with / without Aegis comparison 通过，说明双轨与证据链不是 fixture 文本装饰，而是当前 method-pack 行为差异的一部分

### 3.3 宿主兼容与 handoff 准备

当前已有 fresh evidence 支撑以下事实：

1. `OpenCode` integration suite 当前真实 `3/3 PASS`
2. `Codex` representative natural smoke 当前真实 `PASS`
3. `codex plugin sync regression` 已在 Layer 1 fast check 中通过
4. `OpenCode` 插件技能发现链已对齐宿主当前官方文档支持的全局 skills 目录，而不是继续把 undocumented config-only 路径当成唯一契约

---

## 4. 证据

### 4.1 Fresh verification commands

```bash
bash tests/opencode/run-tests.sh --integration
bash -lc "env SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh brainstorming tests/skill-triggering/prompts/brainstorming.txt"
bash tests/e2e/run-all.sh --full --host-profile fast
```

### 4.2 Fresh verification results

- `bash tests/opencode/run-tests.sh --integration`
  - `test-plugin-loading.sh` → `PASS`
  - `test-tools.sh` → `PASS`
  - `test-priority.sh` → `PASS`
  - aggregate → `STATUS: PASSED`
- Codex targeted natural smoke
  - `PASS`
  - loaded skills: `using-superpowers`, `brainstorming`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
  - `Layer 1 Fast Check` → `PASS`
  - `Layer 2 Behavior Check` → `PASS`
  - `Layer 3 Scenario Check` → `PASS`
  - aggregate → `STATUS: PASSED`

### 4.3 Supporting records

- `docs/current/AEGIS_PHASE5_E2E_BASELINE_RUN.md`
- `docs/current/AEGIS_PHASE5_E2E_COMPLETION_RECORD.md`

---

## 5. 修复轨回望

1. 真实根因
   - OpenCode 侧真实阻断不是 plugin file 不存在，而是当前 integration runtime 没有把 `config.skills.paths` 当成稳定 discovery 主链；skill tool 实际只看到了 `personal-test`，看不到 superpowers skills。
   - Codex 侧真实阻断不是 parser 漂移，而是 `brainstorming` 自然样本文案再次泛化，降低了代表性 smoke 的稳定性。
2. 唯一 canonical owners
   - `.opencode/plugins/superpowers.js`
   - `tests/skill-triggering/prompts/brainstorming.txt`
   - supporting doc owner：`docs/README.opencode.md`
3. 最小必要改动
   - 在 OpenCode plugin 中把 superpowers skills 镜像到宿主官方支持的 `~/.config/opencode/skills/` discovery 路径
   - 将 `config.skills.paths` 保留为兼容 fallback，而不再把它当成唯一 discovery contract
   - 收敛 `brainstorming` 自然样本文案，只保留 design exploration 语义
4. 兼容边界
   - 未引入 runtime core dependency
   - 未新增 authority-upgrading 输出
   - 未破坏 plugin-installable 分发骨架
5. 验证方式
   - OpenCode integration suite fresh pass
   - Codex targeted smoke fresh pass
   - full E2E aggregate fresh pass

---

## 6. 退役轨回望

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - `OpenCode` 的 config-only discovery 假设
   - 漂移后的 `brainstorming` 自然样本文案
2. 是否仍在主链生效
   - config-only 发现链：不再是主链，只保留为兼容 fallback
   - prompt drift：否
3. 保留它的唯一理由
   - `config.skills.paths` fallback 的唯一理由，是当前仍缺少证据证明所有目标宿主版本都已完全不需要该兼容层
4. 删除触发条件
   - 当受支持的 OpenCode 版本经过真实验证，确认 native skills path 已足够稳定且 config fallback 不再贡献兼容价值
5. 删除前验证清单
   - `bash tests/opencode/run-tests.sh --integration`
   - `bash tests/e2e/run-all.sh --full --host-profile fast`
   - `docs/README.opencode.md` 安装说明回读

---

## 7. Reflection 回望

### Goal

`Phase 5` 在当前执行计划中的三个高层目标已被覆盖：

1. artifacts 稳定性 → 已由 schema fixtures + Layer 2 / 3 artifacts evidence 覆盖
2. dual-track 实际进入交付 → 已由场景 B transcript / comparison 覆盖
3. future adapter/core handoff 准备 → 已由 runtime-ready artifacts、宿主兼容性与 boundary 未漂移共同覆盖

### DeeperCause

`No`

理由：

- 当前阻断都收敛在本仓 canonical owners
- 没有证据表明 method-pack boundary、artifact contract 或 dual-track 结构本身存在更深层设计缺陷
- 当前修复不依赖放宽验证口径

### Evidence

- `bash tests/opencode/run-tests.sh --integration`
- `bash -lc "env SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh brainstorming tests/skill-triggering/prompts/brainstorming.txt"`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

### Risk / Unknown

- Layer 2 / Layer 3 当前仍是 fixture-backed validation，不是 live remote multi-host orchestration
- `Claude / Cursor / Gemini` 侧当前没有在本轮做 release-level fresh install verification
- 当前仓仍只是 `Method Pack (runtime-ready)`，不是 full platform

### Decision

`exit`

理由：

- 当前 `Phase 5` 在本仓 method-pack scope 内的定义已经满足
- 剩余项已被明确分类为生产 rollout gap 或 full-platform gap，而不是当前 phase 未闭合

---

## 8. QA 结论

### Remove / Restore

- 已移除 Codex natural smoke 的 prompt drift 阻断
- 已将 OpenCode skills discovery 主链恢复到宿主官方支持路径
- 未引入新的 fallback owner、runtime authority 或 host-specific baseline 漂移

### Confidence

- `A`

理由：

- 有 direct fresh evidence
- 有 host integration coverage
- 有 full aggregate E2E coverage
- 当前 phase 范围内没有 material unknown 阻断

### Authority Note

本文档只提供：

- verified evidence
- phase-level advisory closeout judgment

本文档不提供：

- full-platform production authority
- runtime core completion authority

---

## 9. 后续入口

`Phase 5` 收口后，后续是否继续推进，应先回读：

1. `docs/current/AEGIS_PRODUCTION_READINESS_GAPS.md`
2. `docs/current/AEGIS_TARGET_STATE.md`
3. `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`

当前没有自动激活的新 implementation slice；是否继续，由用户基于 production gap 再决定。
