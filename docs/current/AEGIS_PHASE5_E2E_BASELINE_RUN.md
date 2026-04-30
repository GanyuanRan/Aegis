# Aegis Phase 5 E2E Baseline Run

状态：`Recorded`

## 1. 文档定位

本文档记录 `Aegis Phase 5 / Runtime-ready Hardening` 中 `E2E 验收框架` 这一批准切片的 fresh baseline run 结果。

本文档只记录：

- baseline run 的实际命令
- baseline run 的真实结果
- 当前环境中的 blocker 与其分类
- 由 baseline run 反推的最小脚本/样本收敛结论

本文档不授予：

- authoritative completion
- runtime core 级别裁决
- 对后续 Phase 5 切片的自动激活

---

## 2. 运行环境

- 日期：`2026-04-27`
- 工作目录：repo root（本机开发仓路径）
- 宿主：
  - `Codex CLI`
  - `OpenCode CLI`
- 运行模式：
  - `Layer 1 fast host profile`
  - fixture-backed `Layer 2`
  - fixture-backed `Layer 3`

---

## 3. Fresh Verification Commands

本轮 baseline run 实际执行了以下 fresh commands：

```bash
bash -lc "env SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh brainstorming tests/skill-triggering/prompts/brainstorming.txt"
bash tests/e2e/layer1-fast-check.sh --host-profile fast
bash tests/e2e/run-all.sh --full --host-profile fast
```

---

## 4. Fresh Results

### 4.1 Targeted Codex natural smoke

命令：

```bash
bash -lc "env SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh brainstorming tests/skill-triggering/prompts/brainstorming.txt"
```

结果：

- `PASS`
- 触发技能：
  - `using-superpowers`
  - `brainstorming`

结论：

- `brainstorming` 自然样本在当前收敛文案下可再次触发

### 4.2 Layer 1 Fast Check

命令：

```bash
bash tests/e2e/layer1-fast-check.sh --host-profile fast
```

结果：

- `Passed: 6`
- `Failed: 0`

覆盖项：

1. `boundary compliance`
2. `artifact schema fixtures`
3. `codex representative skill-triggering smoke`
4. `codex representative explicit-skill smoke`
5. `opencode base suite`
6. `codex plugin sync regression`

结论：

- Layer 1 host-native fast profile 当前可重复执行

### 4.3 Full E2E Aggregate

命令：

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

结果：

- `Layer 1 Fast Check` → `PASS`
- `Layer 2 Behavior Check` → `PASS`
- `Layer 3 Scenario Check` → `PASS`
- `STATUS: PASSED`

Layer 2 事实：

- 场景 A with-Aegis transcript 分析通过
- 场景 A with/without comparison 通过
- 场景 B with-Aegis transcript 分析通过
- 场景 B with/without comparison 通过

Layer 3 事实：

- 场景 A 验收通过
- 场景 B 验收通过
- 场景 C Codex fixture 通过
- 场景 C Claude fixture 通过
- 场景 C cross-host comparison 通过

---

## 5. Blockers 与分类

本轮 baseline run 没有阻断当前切片 closeout 的 blocker。

### 5.1 已识别并收敛的问题

1. `Layer 1` 中 `brainstorming` Codex natural smoke 存在波动
2. 真实根因不是 parser 宽松度不足，而是自然样本文案漂移

证据：

- 旧的稳定样本与当前失败样本 prompt 文本不同
- 当前 prompt 单次 fresh rerun 可过，但失败日志显示确有未加载 `brainstorming/SKILL.md` 的真实轮次
- 回收到已证据化的稳定语义后，targeted smoke、Layer 1、full E2E 均 fresh pass

分类：

- 类型：`已修复的样本漂移`
- 级别：`非环境 blocker`

---

## 6. 修复轨回望

1. 真实根因
   - `tests/skill-triggering/prompts/brainstorming.txt` 漂移到了更泛化的措辞，降低了 Codex 对 `brainstorming` 的自然触发稳定性。
2. 唯一 canonical owner
   - `tests/skill-triggering/prompts/brainstorming.txt`
3. 最小必要改动
   - 只收敛自然样本文案，未放宽 parser，未降低 Layer 1 判定标准。
4. 兼容边界
   - 保持现有 Codex skill-load transcript 证据口径不变。
5. 验证方式
   - targeted smoke
   - Layer 1 fast check
   - full E2E aggregate

---

## 7. 退役轨回望

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 漂移后的 `brainstorming` 自然样本文案。
2. 是否仍在主链生效
   - 否，已被收敛替换。
3. 保留它的唯一理由
   - 无；该文案没有形成新的 contract 价值。
4. 删除触发条件
   - 已触发并完成收敛。
5. 删除前验证清单
   - 确认回收后的 prompt 仍能支持 targeted smoke、Layer 1 与 full E2E。

---

## 8. 结论

本轮 baseline run 证明：

- `Phase 5 E2E 验收框架` 这一批准切片已具备 fresh、可重复的运行证据
- 当前证据属于 `verified evidence`
- 当前证据不等价于整个 `Phase 5 / Runtime-ready Hardening` 已全部完成

建议后续 authority 口径：

- `Phase 5` 仍为 `in-progress`
- `Phase 5 E2E verification slice` 可进入 completion record 收口
