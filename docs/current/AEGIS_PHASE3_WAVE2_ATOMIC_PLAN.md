# Aegis Phase 3 Wave 2 Atomic Plan

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis` 当前下一实施切片的原子级任务清单。

本文档只负责回答以下问题：

- `Phase 3 / Wave 2` 具体先改哪些文件
- `writing-plans` 与 `requesting-code-review` 各自的目标、边界与验证方式是什么
- 如何把 `TLREF / DIVE / Reflection / QA / 双轨治理` 继续投影到后续高杠杆 process skills
- 如何在继续增强流程能力时，保持 `superpowers` 的 plugin-installable 分发属性

本文档不负责回答以下问题：

- future runtime core 的实现细节
- `Phase 4` 及之后的完整执行方案
- 本轮之外其他 skills 的全面重写策略

---

## 2. 当前结论

当前仓库已经完成：

- `Phase 1：Authority Completion`
- `Phase 2：Skill Upgrade Wave 1`

当前仓库下一步只做：

- `Phase 3：Skill Upgrade Wave 2`

当前 Wave 2 只允许覆盖以下两个 skills 与其最小必要验证链：

1. `skills/writing-plans/SKILL.md`
2. `skills/requesting-code-review/SKILL.md`

以及与它们直接相关的：

- `tests/skill-triggering/`
- `tests/explicit-skill-requests/`
- `docs/testing.md`

除非有证据证明现有结构已阻断 Wave 2 落地，否则本切片不扩展到：

- future runtime core
- host adapter 实现
- 全量 review / execution workflow 重构
- `subagent-driven-development`
- `executing-plans`

---

## 3. Wave 2 交付目标

Wave 2 完成时，必须同时满足以下目标：

1. `writing-plans` 已吸收 `TLREF / DIVE / Reflection / QA` 的最小计划层骨架
2. `writing-plans` 对 plan 产物显式纳入：
   - impact
   - compatibility boundary
   - verification
   - repair track / retirement track
3. `requesting-code-review` 已显式纳入：
   - evidence sufficiency
   - architecture drift check
   - authority boundary
   - dual-track review lens
4. 两个 skill 改造后仍保持 `superpowers` 原有高价值行为，不破坏既有分发模型
5. 至少一条自然触发验证链覆盖 `writing-plans` 与 `requesting-code-review`
6. 至少一条显式 skill 请求验证链覆盖 `writing-plans` 与 `requesting-code-review`
7. `plugin-installable` 相关测试入口未因本轮改造被破坏

---

## 4. 文件责任图

### 4.1 Method-pack Canonical Owners

- `skills/writing-plans/SKILL.md`
  - spec 转 implementation plan 的唯一 canonical workflow owner
- `skills/requesting-code-review/SKILL.md`
  - review request 之前的证据门、漂移门与反馈处理门

### 4.2 Supporting Verification Owners

- `tests/skill-triggering/run-all.sh`
  - 自然触发回归总入口
- `tests/skill-triggering/prompts/*.txt`
  - 自然语言触发样本
- `tests/explicit-skill-requests/run-all.sh`
  - 显式点名 skill 的触发回归入口
- `tests/explicit-skill-requests/prompts/*.txt`
  - 显式请求样本
- `docs/testing.md`
  - 当前测试矩阵与运行说明

### 4.3 Distribution / Compatibility Verification Owners

- `tests/opencode/run-tests.sh`
  - OpenCode plugin 骨架验证入口
- `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
  - Codex plugin 同步与嵌入式插件骨架回归入口

---

## 5. 原子实施切片

### Slice 1：`writing-plans` 计划治理升级

**目标：**

- 保留原有“从 spec 写到可执行计划”的强约束
- 把 `Define / Investigate / Validate / Evolve`、impact、compatibility、verification、双轨治理收进计划生成主路径

**涉及文件：**

- 修改：`skills/writing-plans/SKILL.md`

**修复轨：**

1. 真实根因
   - 当前 `writing-plans` 对计划细化和 TDD 粒度要求很强，但尚未显式纳入 `Aegis` 的 impact、compatibility、verification、risk/rollback 与 dual-track 收口视角。
2. 唯一 canonical owner
   - `skills/writing-plans/SKILL.md`
3. 最小必要改动
   - 只改 overview、scope check、plan header、task structure、self-review、execution handoff。
4. 兼容边界
   - 必须保留：
     - plan header
     - bite-sized task granularity
     - exact file paths / exact commands discipline
     - TDD / frequent commits / no placeholders
5. 验证方式
   - 自然触发测试
   - 显式 skill 请求测试
   - 人工回读确认计划技能仍然是“plan writer”，而不是 runtime authority

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 任何只强调“把步骤写细”，但未显式包含 impact / compat / verification / rollback 的旧计划分支描述。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 只保留那些直接维持计划粒度与可执行性的最小文字。
4. 删除触发条件
   - 新版 `writing-plans` 已能同时覆盖精细计划、验证意识与双轨治理。
5. 删除前验证清单
   - 不得移除 exact paths / exact commands
   - 不得弱化 TDD
   - 不得把 implementation plan 写成抽象愿景文

---

### Slice 2：`requesting-code-review` 审查治理升级

**目标：**

- 保留原有“请求 code review”主路径
- 显式纳入 evidence sufficiency、architecture drift、authority boundary 与 dual-track review lens

**涉及文件：**

- 修改：`skills/requesting-code-review/SKILL.md`
- 视需要修改：
  - `skills/requesting-code-review/code-reviewer.md`

**修复轨：**

1. 真实根因
   - 当前 `requesting-code-review` 偏重“何时发起 review 与如何处理反馈”，但还未显式要求 reviewer 检查证据充分性、残余风险、架构漂移，以及旧逻辑是否应退役。
2. 唯一 canonical owner
   - `skills/requesting-code-review/SKILL.md`
3. 最小必要改动
   - 先只改主 `SKILL.md`；只有在 reviewer 模板与主文冲突时，才扩展到 `code-reviewer.md`。
4. 兼容边界
   - 必须保留：
     - 何时发起 review 的主路径
     - reviewer subagent dispatch 核心方式
     - Critical / Important / Minor 的处理纪律
5. 验证方式
   - 自然触发测试
   - 显式 skill 请求测试
   - 文本回读确认“review 通过”不等于 authoritative completion

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 任何把“有 reviewer 反馈”直接等价成“工作完成”的旧表述，或未检查架构漂移/旧路径去留的 review 请求模板。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 只保留与 review dispatch、反馈处置直接相关的最小主线文字。
4. 删除触发条件
   - 新版 skill 已能覆盖 review request、evidence sufficiency、dual-track lens 与 authority boundary。
5. 删除前验证清单
   - 不得删除 SHAs / review context 传递要求
   - 不得弱化 Critical / Important 问题处理纪律
   - 不得把 review skill 改写成 completion gate

---

### Slice 3：触发覆盖与最小行为回归

**目标：**

- 给 Wave 2 两个 skill 建立与当前范围相称的最低触发安全网

**涉及文件：**

- 修改：`tests/skill-triggering/run-all.sh`
- 新增或修改：
  - `tests/skill-triggering/prompts/writing-plans.txt`
  - `tests/skill-triggering/prompts/requesting-code-review.txt`
- 修改：`tests/explicit-skill-requests/run-all.sh`
- 新增：
  - `tests/explicit-skill-requests/prompts/use-writing-plans.txt`
  - `tests/explicit-skill-requests/prompts/use-requesting-code-review.txt`
- 视需要修改：
  - `tests/explicit-skill-requests/run-test.sh`
  - `tests/helpers/codex-cli.sh`
  - `docs/testing.md`

**修复轨：**

1. 真实根因
   - 当前 Codex Wave 1 smoke matrix 只覆盖前三个高杠杆 process skills，尚未把 `writing-plans` 与 `requesting-code-review` 纳入当前 host-native smoke 范围。
2. 唯一 canonical owner
   - `tests/skill-triggering/run-all.sh`
   - `tests/explicit-skill-requests/run-all.sh`
3. 最小必要改动
   - 只补两条目标 skill 的 prompt、矩阵项与必要 helper 支撑。
4. 兼容边界
   - 必须保留：
     - Wave 1 既有通过链
     - Codex helper 的“真实 skill load 证据优先”纪律
5. 验证方式
   - Codex natural smoke
   - Codex explicit smoke
   - 必要时定向单测某条 prompt 的稳定性

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 任何仅依赖 diff / 文档引用而非真实 skill load 的旧匹配方式。
2. 是否仍在主链生效
   - 不应继续作为通过依据。
3. 保留它的唯一理由
   - 无。
4. 删除触发条件
   - Wave 2 helper 仍保持真实 load-based 判定即可。
5. 删除前验证清单
   - 回归矩阵必须 fresh pass
   - 不能把通过标准重新放宽到字符串出现级别

---

### Slice 4：兼容性回看

**目标：**

- 确认 Wave 2 skill 增强没有破坏 plugin-installable 分发属性

**涉及文件：**

- 不默认改业务文件
- 运行：
  - `tests/opencode/run-tests.sh`
  - `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`

**修复轨：**

1. 真实根因
   - 任何 method-pack 改造都可能通过测试辅助脚本、安装说明或插件骨架间接污染分发能力。
2. 唯一 canonical owner
   - compatibility regression commands themselves
3. 最小必要改动
   - 默认只跑回归；仅在出现真实失败时再做窄修。
4. 兼容边界
   - 不能为了让某一宿主更好用而破坏跨宿主分发模型。
5. 验证方式
   - OpenCode plugin loading
   - Codex plugin sync regression

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 若出现为单一宿主增加的特殊兼容文本或脚本分支，应在此切片内盘点。
2. 是否仍在主链生效
   - 需视实际发现而定。
3. 保留它的唯一理由
   - 仅保留跨宿主分发所必需的兼容最小面。
4. 删除触发条件
   - 出现统一兼容实现后，退役宿主特例。
5. 删除前验证清单
   - 两条分发回归链 fresh pass

---

## 6. 最低验证矩阵

Wave 2 结束前，至少要 fresh 运行：

```bash
SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh
SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh
bash tests/opencode/run-tests.sh
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

若只做中间切片验证，则至少跑：

- 相关 `SKILL.md` 回读
- 对应自然触发定向测试
- 对应显式 skill 请求定向测试

---

## 7. 完成定义

只有当以下条件全部成立时，Wave 2 才可视为完成：

1. `writing-plans` 已显式对齐 `Aegis` 计划治理要求
2. `requesting-code-review` 已显式对齐 `Aegis` 审查治理要求
3. Codex natural smoke 覆盖两个目标 skill 且 fresh pass
4. Codex explicit smoke 覆盖两个目标 skill 且 fresh pass
5. plugin-installable compatibility regression fresh pass
6. 没有证据表明当前仓开始越权承担 runtime authority

---

## 8. 本轮非目标

为了避免漂移，Wave 2 明确不做：

- 不重写 `subagent-driven-development`
- 不重写 `executing-plans`
- 不把 plan / review skill 改成 runtime gate engine
- 不引入宿主专有 logic 到 method-pack baseline
- 不为单一样本通过而放宽 smoke 判定标准
