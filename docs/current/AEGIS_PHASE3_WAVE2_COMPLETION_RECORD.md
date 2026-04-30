# Aegis Phase 3 Wave 2 Completion Record

状态：`Reviewed`

## 1. 文档定位

本文档记录 `Aegis Phase 3 / Wave 2` 的实际完成情况、fresh verification 证据、修复轨 / 退役轨回望，以及当前残余风险。

本文档是阶段收口记录，不替代以下 authoritative baseline：

- `docs/current/AEGIS_TARGET_STATE.md`
- `docs/current/AEGIS_PHASE3_WAVE2_ATOMIC_PLAN.md`
- `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`

---

## 2. 阶段结论

`Phase 3 / Wave 2` 当前可判定为：

> `Completed within approved scope`

完成范围严格限定于 `AEGIS_PHASE3_WAVE2_ATOMIC_PLAN.md` 允许的边界：

1. `skills/writing-plans/SKILL.md`
2. `skills/requesting-code-review/SKILL.md`
3. `skills/requesting-code-review/code-reviewer.md`
4. 与这两个 skill 直接相关的最小 smoke / plugin compatibility 验证链
5. 与当前切片直接相关的 authority / testing supporting docs

当前没有证据显示本轮改造越过以下边界：

- future runtime core
- host adapter runtime
- `executing-plans`
- `subagent-driven-development`
- 全量 skills 重写

---

## 3. 事实

### 3.1 Skill 层事实

- `writing-plans` 已显式纳入：
  - fact / assumption / unknown pre-check
  - baseline / authority refs
  - compatibility boundary
  - verification expectations
  - repair track / retirement track
  - plan 不能越权授予 authoritative completion
- `requesting-code-review` 已显式纳入：
  - reviewed scope / plan / evidence / compatibility boundary
  - evidence sufficiency 检查
  - architecture drift / duplicate owner / stale fallback 检查
  - retirement notes / dual-track review lens
  - review 不能越权等价为 authoritative completion
- `requesting-code-review/code-reviewer.md` 已与主 skill 对齐：
  - reviewer 输入模板补齐 evidence / compatibility / retirement placeholders
  - 输出模板补齐 evidence review 与 authority note

### 3.2 验证链事实

- Codex Wave 1 + Wave 2 自然触发 smoke 已覆盖：
  - `brainstorming`
  - `systematic-debugging`
  - `verification-before-completion`
  - `writing-plans`
  - `requesting-code-review`
- Codex Wave 1 + Wave 2 显式 skill smoke 已覆盖：
  - `please-use-brainstorming`
  - `use-systematic-debugging`
  - `use-verification-before-completion`
  - `use-writing-plans`
  - `use-requesting-code-review`
- OpenCode plugin loading regression 通过
- Codex plugin sync regression 通过

### 3.3 Supporting docs / fixture 事实

- `AGENTS.md` 当前激活切片阅读顺序已对齐到 `AEGIS_PHASE3_WAVE2_ATOMIC_PLAN.md`
- `tests/explicit-skill-requests/run-test.sh` 在 Codex 最小项目夹具中已补齐 `AEGIS_PHASE3_WAVE2_ATOMIC_PLAN.md`
- `docs/testing.md` 已补齐 Wave 1 + Wave 2 的 Codex smoke 说明
- `tests/skill-triggering/prompts/writing-plans.txt` 已收敛为当前批准 Wave 2 scope，避免自然样本与仓库护栏冲突

### 3.4 分发边界事实

- 当前没有引入宿主专有 runtime 依赖
- 当前仍保留 `superpowers` 原有 plugin-installable 分发骨架
- 当前仍符合 `Aegis Method Pack (runtime-ready)` 边界，没有越权承担 runtime authority

---

## 4. 证据

### 4.1 Fresh verification commands

2026-04-26 本轮 fresh verification 运行命令如下：

```bash
bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh'
bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh'
bash tests/opencode/run-tests.sh
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

### 4.2 Fresh verification results

- `bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh'`
  - `Passed: 5`
  - `Failed: 0`
  - 覆盖：`brainstorming` / `systematic-debugging` / `verification-before-completion` / `writing-plans` / `requesting-code-review`
- `bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh'`
  - `Passed: 5`
  - `Failed: 0`
  - `Total: 5`
- `bash tests/opencode/run-tests.sh`
  - `STATUS: PASSED`
- `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
  - `PASS`

### 4.3 中途诊断证据

本轮还识别并收敛了两个验证链问题：

1. 首次 fresh verification 使用 PowerShell 环境变量写法，变量未实际透传进 `bash`
   - 现象：脚本错误落入 Claude 分支
   - 结论：属于命令调用方式问题，不是仓库脚本逻辑缺陷
2. `writing-plans` 自然样本曾真实失败一次
   - 现象：skill 未加载，Codex 先被仓库护栏拦在 scope clarification
   - 根因：样本请求“新认证系统 implementation plan”，与当前仓只允许推进 Wave 2 的 scope 冲突
   - 处理：把自然样本收敛为当前批准 Wave 2 scope 后 fresh rerun 通过

### 4.4 Fresh artifact paths

- 自然触发总矩阵：`.tmp/superpowers-tests/1777209627/`、`.tmp/superpowers-tests/1777209768/`、`.tmp/superpowers-tests/1777210070/`、`.tmp/superpowers-tests/1777210372/`、`.tmp/superpowers-tests/1777210674/`
- 显式 skill 总矩阵：`.tmp/superpowers-tests/1777206732/`、`.tmp/superpowers-tests/1777207033/`、`.tmp/superpowers-tests/1777207161/`、`.tmp/superpowers-tests/1777207238/`、`.tmp/superpowers-tests/1777207458/`
- `writing-plans` 定向复测：`.tmp/superpowers-tests/1777208407/`

---

## 5. 实施摘要

### Slice 1：`writing-plans`

已完成：

- canonical planning workflow framing
- authority / baseline / compatibility pre-check
- required planning outputs
- impact / verification / dual-track planning structure
- planning boundary 说明

保留未破坏：

- exact file paths / exact commands discipline
- bite-sized task granularity
- TDD / DRY / YAGNI / frequent commits
- execution handoff 主路径

### Slice 2：`requesting-code-review`

已完成：

- canonical review-request workflow framing
- required review inputs / outputs
- evidence sufficiency 与 architecture drift 检查
- compatibility / retirement review lens
- advisory-only boundary

保留未破坏：

- 何时发起 review 的主路径
- reviewer dispatch 核心方式
- Critical / Important / Minor 处置纪律

### Slice 3：Codex smoke / explicit smoke 扩面

已完成：

- Codex Wave 2 natural smoke matrix
- Codex Wave 2 explicit smoke matrix
- Codex explicit 最小项目夹具 authority docs 对齐
- `writing-plans` 自然样本从越界需求收敛回当前批准 scope

### Slice 4：plugin-installable compatibility

已完成：

- OpenCode plugin loading regression
- Codex plugin sync dry-run regression

---

## 6. 修复轨回望

### 6.1 根因

- `writing-plans` 原始文本对计划粒度要求很强，但未显式纳入 impact、compatibility、verification、dual-track 与 authority boundary
- `requesting-code-review` 原始文本偏重“何时发起 review”，未显式要求 reviewer 检查 evidence sufficiency、architecture drift 和旧路径去留
- Codex Wave 2 测试夹具仍偏向 Wave 1 authority context
- `writing-plans` 自然样本原始语义与当前批准 slice scope 冲突

### 6.2 Canonical owners

- `skills/writing-plans/SKILL.md`
- `skills/requesting-code-review/SKILL.md`
- `skills/requesting-code-review/code-reviewer.md`
- `tests/skill-triggering/prompts/writing-plans.txt`
- `tests/skill-triggering/prompts/requesting-code-review.txt`
- `tests/skill-triggering/run-all.sh`
- `tests/explicit-skill-requests/run-all.sh`
- `tests/explicit-skill-requests/run-test.sh`
- `AGENTS.md`
- `docs/testing.md`

### 6.3 最小必要改动

- 只修改 Wave 2 两个 skill 本文与 reviewer 模板
- 只修改与 Wave 2 直接相关的 Codex smoke / explicit smoke / authority / testing supporting docs
- 不扩散到 future runtime core
- 不扩散到未批准的 execution / subagent workflow 大改

### 6.4 兼容边界

- 保留原有 `superpowers` 分发骨架
- 保留现有 plugin-installable 能力
- 保留原有 planning / review workflow 的核心强约束
- 不以治理增强为名把方法层抬升成 runtime authority

### 6.5 验证方式

- Codex natural smoke
- Codex explicit smoke
- OpenCode plugin loading
- Codex plugin sync dry-run regression

---

## 7. 退役轨回望

### 7.1 已收敛的旧表述 / 旧判定

- `AGENTS.md` 中旧的“当前激活切片 -> Wave 1”引用已不再作为当前入口护栏
- explicit smoke Codex 最小夹具中旧的“只有 Wave 1 plan”上下文已收敛
- `docs/testing.md` 中旧的 “Wave 1 only” Codex smoke 说明已收敛为 Wave 1 + Wave 2
- `writing-plans` 自然样本里旧的越界认证系统需求已不再作为当前 slice 的自然触发表述

### 7.2 仍保留但已降级为兼容辅助

- explicit smoke 的 premature-action warning 仍保留
  - 当前作用：提示 Codex transcript 中 skill 可见性与动作时序仍有灰区
  - 当前不是阻断条件
- `Phase 2 / Wave 1` 原子计划仍保留在 authoritative set
  - 当前作用：作为已完成阶段的基线历史与回读依据
  - 当前不是 active slice owner

### 7.3 暂未删除的旧逻辑 / 原因

- `tests/skill-triggering/run-test.sh` / `tests/explicit-skill-requests/run-test.sh` 仍保留 transcript 摘录与技能展示逻辑
  - 保留原因：便于人类回读 smoke transcript
  - 观察指标：展示与真实 skill load 是否持续一致
  - 退役时机：若未来引入更权威的 transcript parser，可替换当前 grep/sed helper

### 7.4 后续退役触发条件

- 若 Codex 提供结构化 skill invocation transcript，可退役当前基于文本模式的 helper 判定
- 若 `Phase 4` 形成更统一的 compatibility review 入口，可收敛当前分散在阶段记录与 testing 文档中的阶段性说明

---

## 8. Reflection 回望

### Goal

Wave 2 原定目标已满足：

- 两个目标 skill 已完成 process upgrade
- Codex Wave 2 最小 smoke 矩阵已建立并通过
- plugin-installable compatibility 仍成立
- 当前仓仍保持 `Method Pack (runtime-ready)` 边界

### DeeperCause

`No`

理由：

- 当前发现的 deeper issue 不在 skill 改造方向本身，而在 supporting verification context 是否与 active scope 保持一致
- 该问题已通过“authority 对齐 -> 夹具补齐 -> 样本收敛 -> fresh rerun”闭环消解
- 暂无证据显示仍存在更深层架构性 owner 错置或 authority 越权

### Evidence

- 见本文第 4 节 fresh verification commands / results
- 见 `.tmp/superpowers-tests/1777206732/`、`.tmp/superpowers-tests/1777207238/`、`.tmp/superpowers-tests/1777208407/`、`.tmp/superpowers-tests/1777209627/`

### Risk / Unknown

- Codex explicit smoke 仍会提示：
  - `Commands were executed before the skill file was loaded`
  - 当前解释：runner warning only，不阻断当前“requested skill became visible”判断
- 当前 Codex smoke 仍是 lightweight host-native smoke，不等价于更深层行为正确性证明
- `Phase 4` 尚未形成独立 atomic plan；当前只完成了 Wave 2 范围内要求的最小 plugin compatibility 回看

### Decision

`exit`

---

## 9. 置信度

`A`

理由：

- 关键结论均来自 fresh command output
- 中途识别并收敛了一个真实样本越界问题
- 修复后完成了定向复测 + 全矩阵复测 + plugin compatibility 复测
- 当前残余风险已明确收口在 lightweight smoke 能力边界与下一阶段规划缺口，而非 Wave 2 目标本身

---

## 10. 架构回望

本轮没有发现新的结构性缺陷，但确认了三条重要架构纪律：

1. `Aegis Method Pack` 的自然触发样本也必须服从当前 active authority scope，不能拿越界需求去验证规划 skill
2. supporting fixture 与 authority docs 的漂移会直接污染对 skill 是否真正触发的判断，必须和 active slice 同步升级
3. 方法层的 planning / review 增强可以继续下沉为 workflow discipline，但不能借此越权成 runtime completion authority

当前架构仍符合以下方向：

- 方法层增强
- authority boundary 清晰
- 插件可安装能力保留
- 宿主无关分发模型保留

未观察到以下漂移：

- method-pack 向 runtime core 越权
- host-specific logic 反向抬升为 baseline
- 为治理增强而破坏 plugin-installable 属性

---

## 11. 建议

首选下一步：

- 进入 `Phase 4：Compatibility Review`
- 先补一份 Phase 4 atomic plan，明确：
  - 还要验证哪些原有 `superpowers` 能力
  - 哪些 host-specific 文档或脚本可能存在反向污染风险
  - 当前最小 plugin compatibility 已通过后，下一轮应该扩到哪些非 smoke 层检查

备选下一步：

- 先对 Wave 2 completion record 进行人工审阅确认
- 再切到 `Phase 4` 的基线文档与实施计划补齐

---

## 12. 影响面

### 功能

- 仅影响 Wave 2 两个高杠杆 process skills 的方法层文本与其最小验证链

### 数据

- 无业务数据结构变更

### 性能

- 仅增加 smoke / review / planning 文本约束与夹具上下文对齐
- 无 runtime path 性能影响

### 安全 / 合规

- 无新增敏感权限
- 无新增外部依赖
- 无新增 authority 越权路径
