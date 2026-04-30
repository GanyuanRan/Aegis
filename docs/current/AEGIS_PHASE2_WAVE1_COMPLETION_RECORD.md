# Aegis Phase 2 Wave 1 Completion Record

状态：`Reviewed`

## 1. 文档定位

本文档记录 `Aegis Phase 2 / Wave 1` 的实际完成情况、fresh verification 证据、修复轨 / 退役轨回望，以及当前残余风险。

本文档是阶段收口记录，不替代以下 authoritative baseline：

- `docs/current/AEGIS_TARGET_STATE.md`
- `docs/current/AEGIS_PHASE2_WAVE1_ATOMIC_PLAN.md`
- `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`

---

## 2. 阶段结论

`Phase 2 / Wave 1` 当前可判定为：

> `Completed within approved scope`

完成范围严格限定于 `AEGIS_PHASE2_WAVE1_ATOMIC_PLAN.md` 允许的边界：

1. `skills/brainstorming/SKILL.md`
2. `skills/systematic-debugging/SKILL.md`
3. `skills/verification-before-completion/SKILL.md`
4. 与这三个 skill 直接相关的最小 smoke / plugin compatibility 验证链

当前没有证据显示本轮改造越过以下边界：

- `writing-plans`
- `requesting-code-review`
- future runtime core
- host adapter runtime

---

## 3. 事实

### 3.1 Skill 层事实

- `brainstorming` 已显式纳入：
  - authority boundary
  - path-and-scope selection
  - `TaskIntentDraft`
  - `BaselineReadSetHint`
  - `ImpactStatementDraft`
  - compatibility boundary / non-goals 要求
- `systematic-debugging` 已显式纳入：
  - fact / assumption / unknown
  - canonical owner
  - symptom / logic / system / architecture 四层诊断
  - Reflection checklist
  - 修复轨 + 退役轨双轨收口
- `verification-before-completion` 已显式纳入：
  - Required Outputs
  - QA Closure
  - Remove/Restore
  - Confidence Grade
  - authority boundary
  - `verified evidence != authoritative completion`

### 3.2 验证链事实

- Codex Wave 1 自然触发 smoke 已覆盖：
  - `brainstorming`
  - `systematic-debugging`
  - `verification-before-completion`
- Codex Wave 1 显式 skill smoke 已覆盖：
  - `please-use-brainstorming`
  - `use-systematic-debugging`
  - `use-verification-before-completion`
- OpenCode plugin loading regression 通过
- Codex plugin sync regression 通过

### 3.3 分发边界事实

- 当前没有引入宿主专有 runtime 依赖
- 当前仍保留 `superpowers` 原有 plugin-installable 分发骨架
- 当前仍符合 `Aegis Method Pack (runtime-ready)` 边界，没有越权承担 runtime authority

---

## 4. 证据

### 4.1 Fresh verification commands

2026-04-26 本轮 fresh verification 运行命令如下：

```bash
SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh
SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh
bash tests/opencode/run-tests.sh
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

### 4.2 Fresh verification results

- `SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh`
  - `Passed: 3`
  - `Failed: 0`
  - 覆盖：`brainstorming` / `systematic-debugging` / `verification-before-completion`
- `SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh`
  - `Passed: 3`
  - `Failed: 0`
  - `Total: 3`
- `bash tests/opencode/run-tests.sh`
  - `STATUS: PASSED`
- `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
  - `PASS`

### 4.3 验证辅助链修正证据

本轮还修正了 Codex smoke helper 的两个证据链问题：

1. `codex_log_mentions_skill` 旧实现会把 transcript 中的 diff / 文档引用误当作 skill 已加载证据
2. `print_codex_skills_triggered` 旧实现对 transcript 噪音敏感，导致已触发 skill 的展示不稳定

修正后：

- skill 通过判定只认真实 skill load 证据
- skill 展示提取优先基于真实 `Get-Content ... skills/.../SKILL.md` 记录
- `verification-before-completion` 自然样本在收紧判定后曾真实失败一次，证明旧链条存在 false positive 风险
- 调整自然 prompt 后再次 fresh pass，说明当前通过结论来自真实触发，而非日志误判

---

## 5. 实施摘要

### Slice 1：`brainstorming`

已完成：

- authority-first 上下文探索
- path / scope 选择
- 三个 runtime-ready draft artifacts
- compatibility boundary / non-goals / owners 显式化

保留未破坏：

- `HARD-GATE`
- one-question-at-a-time
- design approval before implementation

### Slice 2：`systematic-debugging`

已完成：

- canonical debugging workflow 定位
- fact / assumption / unknown 输出要求
- four diagnostic layers
- Reflection checklist
- dual-track closure
- confidence grading

保留未破坏：

- `NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST`
- 四阶段调试骨架
- `3+` 次失败后升级到架构质疑门

### Slice 3：`verification-before-completion`

已完成：

- Required Outputs
- QA Closure
- Remove/Restore
- Confidence Grade
- authority note

保留未破坏：

- `NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE`
- claim-before-verification 零容忍
- method-pack 不越权授予 authoritative completion

### Slice 4：Codex smoke / helper tightening

已完成：

- Codex Wave 1 smoke matrix 限定到批准范围
- Codex helper 改为以真实 skill load 作为通过证据
- Codex skills triggered 展示更稳定
- `verification-before-completion` 自然样本调优为 completion-gate 语义，而非 review 语义

### Slice 5：plugin-installable compatibility

已完成：

- OpenCode isolated plugin setup 增加最小 `package.json` with `"type": "module"`
- 修复 isolated syntax check 下的 ESM 语义漂移

---

## 6. 修复轨回望

### 6.1 根因

- `brainstorming` 原始文本缺少 authority-first / runtime-ready artifact framing
- `systematic-debugging` 原始文本缺少四层诊断、Reflection 和双轨治理显式收口
- `verification-before-completion` 原始文本缺少 QA / confidence / authority boundary 显式结构
- Codex smoke helper 原始实现把“看见 skill 文件名”与“真实 skill 已加载”混为一谈

### 6.2 Canonical owners

- `skills/brainstorming/SKILL.md`
- `skills/systematic-debugging/SKILL.md`
- `skills/verification-before-completion/SKILL.md`
- `tests/helpers/codex-cli.sh`
- `tests/skill-triggering/prompts/verification-before-completion.txt`

### 6.3 最小必要改动

- 只修改 Wave 1 三个 skill 本文
- 只修改与 Wave 1 直接相关的 Codex smoke / explicit smoke / plugin compatibility 辅助脚本
- 不扩散到 Wave 2 skills
- 不引入 runtime core 逻辑

### 6.4 兼容边界

- 保留原有 `superpowers` 分发骨架
- 保留现有 plugin-installable 能力
- 保留三条核心 process skills 的原有强门控，不以治理增强为名削弱原纪律

### 6.5 验证方式

- Codex natural smoke
- Codex explicit smoke
- OpenCode plugin loading
- Codex plugin sync dry-run regression

---

## 7. 退役轨回望

### 7.1 已收敛的旧表述 / 旧判定

- 旧的“只看字符串出现即可算 skill triggered”判定方式已不再作为通过依据
- `verification-before-completion` 自然样本里带 review / verdict 倾向的旧措辞已收敛到 completion-gate 语义

### 7.2 仍保留但已降级为兼容辅助

- explicit smoke 的 premature-action warning 仍保留
  - 当前作用：提示 Codex transcript 中 skill 可见性与动作时序仍有灰区
  - 当前不是阻断条件

### 7.3 暂未删除的旧逻辑 / 原因

- `tests/skill-triggering/run-test.sh` / `tests/explicit-skill-requests/run-test.sh` 仍保留 transcript 摘录与技能展示逻辑
  - 保留原因：便于人类回读 smoke transcript
  - 观察指标：展示与真实 skill load 是否持续一致
  - 退役时机：若未来引入更权威的 transcript parser，可替换当前 grep/sed helper

### 7.4 后续退役触发条件

- 若 Codex 提供结构化 skill invocation transcript，可退役当前基于文本模式的 helper 判定
- 若 future host adapter / runtime core 提供统一 gate evidence format，可退役当前 method-pack 内的轻量 smoke 证据提取

---

## 8. Reflection 回望

### Goal

Wave 1 原定目标已满足：

- 三个目标 skill 已完成 process upgrade
- Codex 最小 smoke 矩阵已建立并通过
- plugin-installable compatibility 仍成立
- 当前仓仍保持 `Method Pack (runtime-ready)` 边界

### DeeperCause

`No`

理由：

- 当前发现的 deepest issue 不在 Wave 1 skill 文本，而在 Codex smoke helper 的证据判定过宽
- 该根因已通过“收紧检测 -> 暴露真实失败 -> 调整 prompt -> fresh rerun”闭环消解
- 暂无证据显示仍存在更深层架构性 owner 错置或 authority 越权

### Evidence

- 见本文第 4 节 fresh verification commands / results
- 见 `.tmp/superpowers-tests/1777194177/`、`.tmp/superpowers-tests/1777194624/`、`.tmp/superpowers-tests/1777194657/`

### Risk / Unknown

- Codex explicit smoke 仍会提示：
  - `Commands were executed before the skill file was loaded`
  - 当前解释：runner warning only，不阻断当前“requested skill became visible”判断
- 当前 Codex smoke 仍是 lightweight host-native smoke，不等价于更深层行为正确性证明
- OpenCode 仅跑了 plugin loading regression，未跑 integration variant

### Decision

`exit`

---

## 9. 置信度

`A`

理由：

- 关键结论均来自 fresh command output
- 中途识别并修复了一个真实 false positive 风险
- 修复后完成了定向复测 + 全矩阵复测 + plugin compatibility 复测
- 当前残余风险已明确收口在 lightweight smoke 能力边界内，而非 Wave 1 目标本身

---

## 10. 架构回望

本轮没有发现新的结构性缺陷，但确认了两条重要架构纪律：

1. `Aegis Method Pack` 不能把“验证提示词增强”误当成“runtime authority”
2. `verification evidence` 的测试链本身也必须接受 `verification-before-completion` 约束，不能允许 false positive smoke 存在

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

- 进入 `Phase 3 / Wave 2`
- 优先升级：
  - `writing-plans`
  - `requesting-code-review`

备选下一步：

- 先把当前 completion record 评审确认
- 再进入下一波改造

---

## 12. 影响面

### 功能

- 仅影响 Wave 1 三个高杠杆 process skills 的方法层文本与其最小验证链

### 数据

- 无业务数据结构变更

### 性能

- 仅增加 smoke helper 判定精度
- 无 runtime path 性能影响

### 安全 / 合规

- 无新增敏感权限
- 无新增外部依赖
- 无新增 authority 越权路径
