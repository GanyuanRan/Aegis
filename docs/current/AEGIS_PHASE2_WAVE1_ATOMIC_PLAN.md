# Aegis Phase 2 Wave 1 Atomic Plan

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis` 当前最近实施切片的原子级任务清单。

本文档只负责回答以下问题：

- `Phase 2 / Wave 1` 具体先改哪些文件
- 每个切片的目标、最小改动边界与验证方式是什么
- 如何把 TLREF / ADD / 双轨治理落到第一批高杠杆 skills
- 如何在改造过程中保住 `superpowers` 的 plugin-installable 分发能力

本文档不负责回答以下问题：

- future runtime core 的实现细节
- `Phase 3` 及之后的完整执行方案
- 当前未进入 Wave 1 的其他 skills 如何逐个实现

---

## 2. 当前结论

当前仓库已经完成：

- `Phase 1：Authority Completion`

当前仓库下一步只做：

- `Phase 2：Skill Upgrade Wave 1`

当前 Wave 1 只允许覆盖以下三个 skills 与其最小必要验证链：

1. `skills/brainstorming/SKILL.md`
2. `skills/systematic-debugging/SKILL.md`
3. `skills/verification-before-completion/SKILL.md`

以及与它们直接相关的：

- `tests/skill-triggering/`
- `tests/explicit-skill-requests/`
- `docs/testing.md`

除非有证据证明现有结构已阻断 Wave 1 落地，否则本切片不扩展到：

- `writing-plans`
- `requesting-code-review`
- future runtime core
- host adapter 实现

---

## 3. Wave 1 交付目标

Wave 1 完成时，必须同时满足以下目标：

1. 三个目标 skill 已吸收 `TLREF / DIVE / Reflection / QA` 的最小骨架
2. 对 bug / refactor / contract 类任务，skill 文本已显式接入 `修复轨 + 退役轨`
3. skill 改造后仍保持 `superpowers` 原有高价值行为，不破坏既有分发模型
4. 至少一条自然触发验证链覆盖 `brainstorming` 与 `verification-before-completion`
5. 现有 `systematic-debugging` 触发与显式调用验证链未回退
6. `plugin-installable` 相关测试入口未因本轮改造被破坏

---

## 4. 文件责任图

### 4.1 Method-pack Canonical Owners

- `skills/brainstorming/SKILL.md`
  - 创意/设计类任务的入口分流、范围判断、设计批准门
- `skills/systematic-debugging/SKILL.md`
  - 诊断任务的根因调查、分层分析与最小修复纪律
- `skills/verification-before-completion/SKILL.md`
  - completion claim 之前的验证门、证据门与 QA 门

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
- `docs/README.codex.md`
  - Codex 安装分发说明
- `docs/README.opencode.md`
  - OpenCode 安装分发说明

---

## 5. 原子实施切片

### Slice 1：`brainstorming` 方法层升级

**目标：**

- 保留原有“先设计、后实现、先批准、再动手”的硬门
- 把 `路径选择 + Define 基线意识 + Aegis artifacts 草稿意识` 注入到创意/方案入口

**涉及文件：**

- 修改：`skills/brainstorming/SKILL.md`
- 视需要修改：`skills/brainstorming/visual-companion.md`

**修复轨：**

1. 真实根因
   - 当前 `brainstorming` 强于设计门控，但尚未显式要求读取 baseline / ADR / current docs，也未把 `Aegis` 的 `TaskIntentDraft`、`BaselineReadSetHint`、`ImpactStatementDraft` 投影到产出结构。
2. 唯一 canonical owner
   - `skills/brainstorming/SKILL.md`
3. 最小必要改动
   - 只改入口 checklist、问题界定步骤、设计输出要求与设计文档落点说明。
4. 兼容边界
   - 必须保留：
     - `HARD-GATE`
     - one-question-at-a-time
     - design approval before implementation
5. 验证方式
   - 自然触发测试
   - 显式 skill 请求测试
   - 人工回读确认未破坏原有设计门控

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - `brainstorming` 中任何仅以“idea -> spec”组织、但未显式接入 baseline-first / Aegis artifact framing 的旧分支描述。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 只保留那些直接承载原有 design gate 的最小文字。
4. 删除触发条件
   - 新版 `Aegis` 入口步骤已能同时覆盖设计门控与 baseline-first framing。
5. 删除前验证清单
   - 不得移除 `write design doc`
   - 不得移除 user approval gate
   - 不得引入宿主专有工具绑定

---

### Slice 2：`systematic-debugging` 诊断治理升级

**目标：**

- 保留“先找根因，再修复”的铁律
- 显式纳入 `现象 -> 逻辑 -> 系统 -> 架构` 四层诊断
- 把 `Reflection checklist` 与双轨治理嵌入修复类任务主路径

**涉及文件：**

- 修改：`skills/systematic-debugging/SKILL.md`
- 视需要修改：
  - `skills/systematic-debugging/root-cause-tracing.md`
  - `skills/systematic-debugging/defense-in-depth.md`

**修复轨：**

1. 真实根因
   - 当前 skill 对 root cause discipline 很强，但缺少 `Aegis` 明确要求的四层诊断覆盖、Reflection 结构化收口，以及修复轨/退役轨同时交付约束。
2. 唯一 canonical owner
   - `skills/systematic-debugging/SKILL.md`
3. 最小必要改动
   - 先只改主 `SKILL.md`；只有在支持文档与主文冲突时，才扩展到 leaf references。
4. 兼容边界
   - 必须保留：
     - `NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST`
     - 四阶段调试骨架
     - 3 次失败后质疑架构的升级门
5. 验证方式
   - 现有自然触发测试继续通过
   - 现有显式 skill 请求测试继续通过
   - 文本回读确认不存在越权 `completion authority`

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 主 `SKILL.md` 与各 leaf references 中如果存在重复但说法不一致的调试阶段描述。
2. 是否仍在主链生效
   - 可能仍在主链生效；需要在切片实施时逐个核定。
3. 保留它的唯一理由
   - 只保留对主技能有补充价值的深入技巧文档，不保留与主技能重复却未同步升级的旧文字。
4. 删除触发条件
   - 主 `SKILL.md` 已成为唯一 canonical workflow，且 leaf files 仅承担补充说明角色。
5. 删除前验证清单
   - 不得丢失 root-cause tracing
   - 不得弱化 evidence gathering
   - 不得把架构升级门改成可选建议

---

### Slice 3：`verification-before-completion` QA 门升级

**目标：**

- 保留“无新鲜验证证据，不得宣称完成”的铁律
- 把 `QA`、`Remove/Restore`、`confidence grading`、`EvidenceBundleDraft` 视角纳入 completion gate
- 明确 method pack 只能给出 advisory / verified evidence，不能越权授予 authoritative completion

**涉及文件：**

- 修改：`skills/verification-before-completion/SKILL.md`

**修复轨：**

1. 真实根因
   - 当前 skill 强调 fresh verification，但尚未显式接入 `Aegis` 的 QA 层结构，也没有把验证结果组织成 runtime-ready evidence artifacts。
2. 唯一 canonical owner
   - `skills/verification-before-completion/SKILL.md`
3. 最小必要改动
   - 只改 gate function、成功/失败输出要求、QA 收口与越权边界提醒。
4. 兼容边界
   - 必须保留：
     - `NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE`
     - claim-before-verification 的零容忍
     - 独立验证代理或子代理结果的要求
5. 验证方式
   - 新增自然触发测试
   - 视需要新增显式 skill 请求测试
   - 手工回读验证“verified”不等于“authoritative granted”

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 任何把“tests pass”直接等价成“任务在治理意义上完成”的旧表述。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 仅保留对“先跑命令、再说结论”的强硬约束。
4. 删除触发条件
   - QA 层与 authority boundary 已显式落入主技能。
5. 删除前验证清单
   - 不得降低 fresh verification 要求
   - 不得把 confidence statement 写成 final authority
   - 不得允许 partial verification 直接越门

---

### Slice 4：触发覆盖与最小行为回归

**目标：**

- 给 Wave 1 三个 skill 建立与当前范围相称的最低触发安全网

**涉及文件：**

- 修改：`tests/skill-triggering/run-all.sh`
- 新增：
  - `tests/skill-triggering/prompts/brainstorming.txt`
  - `tests/skill-triggering/prompts/verification-before-completion.txt`
- 视需要新增并修改：
  - `tests/explicit-skill-requests/prompts/use-verification-before-completion.txt`
  - `tests/explicit-skill-requests/run-all.sh`

**修复轨：**

1. 真实根因
   - 当前 `skill-triggering` 只覆盖部分技能，Wave 1 三个目标 skill 中缺少 `brainstorming` 与 `verification-before-completion` 的自然触发覆盖。
2. 唯一 canonical owner
   - `tests/skill-triggering/run-all.sh`
3. 最小必要改动
   - 先补 prompt fixtures 和总 runner，不引入新的重型测试框架。
4. 兼容边界
   - 保持现有测试脚本风格、目录结构与 `claude -p` 运行方式不变。
5. 验证方式
   - `bash tests/skill-triggering/run-all.sh`
   - `bash tests/explicit-skill-requests/run-all.sh`

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 仅靠人工 spot-check 的旧验证方式。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 当自动化触发样本尚不能覆盖复杂语义时，人工 spot-check 仍可作为补充。
4. 删除触发条件
   - 三个 Wave 1 skill 至少各有一条稳定自动触发回归。
5. 删除前验证清单
   - 不得用 fragile prompt 替代真实自然语言触发样本
   - 不得误把显式请求测试当作自然触发测试

---

### Slice 5：插件分发与宿主兼容回望

**目标：**

- 确认 Wave 1 skill 改造没有破坏 plugin-installable 分发能力

**涉及文件：**

- 默认不改代码，先跑回归：
  - `tests/opencode/run-tests.sh`
  - `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
- 如测试说明需补充，再修改：`docs/testing.md`

**修复轨：**

1. 真实根因
   - skill 文本调整虽然不直接改安装骨架，但如果不做分发回望，可能静默引入 host-specific 漂移或验证遗漏。
2. 唯一 canonical owner
   - 本切片以验证脚本为 owner，不新增实现 owner。
3. 最小必要改动
   - 先验证，不预设要修改分发文档或脚本。
4. 兼容边界
   - 不得为了 `Aegis` 治理增强而破坏 Codex / OpenCode 的安装入口。
5. 验证方式
   - `bash tests/opencode/run-tests.sh`
   - `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 如果 Wave 1 期间新增宿主专有提示或分发说明副本，应视为待退役对象。
2. 是否仍在主链生效
   - 当前不应新增；若新增则视为偏航。
3. 保留它的唯一理由
   - 无；除非存在跨宿主兼容阻断证据。
4. 删除触发条件
   - 一旦证实只是为本轮调试临时添加，必须在同切片删除。
5. 删除前验证清单
   - 删除后重新跑两类插件分发回归

---

## 6. 执行顺序

当前只允许按以下顺序推进：

1. `Slice 1：brainstorming`
2. `Slice 4` 中与 `brainstorming` 直接相关的触发覆盖
3. `Slice 2：systematic-debugging`
4. `Slice 3：verification-before-completion`
5. `Slice 4` 剩余触发覆盖
6. `Slice 5：插件分发与宿主兼容回望`

顺序理由：

- `brainstorming` 是最上游的 process entry
- `systematic-debugging` 与 `verification-before-completion` 分别对应诊断门与收口门
- 触发覆盖必须跟着 skill 落地同步建立
- 分发回望必须放在 Wave 1 实现结束后统一做一次

---

## 7. 最低验证矩阵

每次合并一个切片前，至少完成：

1. 相关 `SKILL.md` 回读
2. 相关触发测试
3. `docs/current/README.md` 与本计划回看
4. 修复轨回望
5. 退役轨回望

Wave 1 全部完成前，至少完成一次：

1. `bash tests/skill-triggering/run-all.sh`
2. `bash tests/explicit-skill-requests/run-all.sh`
3. `bash tests/opencode/run-tests.sh`
4. `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`

如环境不允许执行某条验证，必须显式记录：

- 未执行原因
- 替代证据
- 残余风险

---

## 8. 完成判定

只有当以下条件全部满足时，`Phase 2 / Wave 1` 才允许宣称完成：

1. 三个目标 skill 已完成文本升级
2. Wave 1 相关触发覆盖已补齐
3. 未引入 method pack 越权 authority 表述
4. 未破坏 plugin-installable 分发能力
5. 每个切片都已有修复轨 + 退役轨回望记录

如果只完成 skill 文本修改，但没有完成：

- 触发回归
- 分发回归
- 退役计划说明

则一律视为：

> `Wave 1 not complete`
