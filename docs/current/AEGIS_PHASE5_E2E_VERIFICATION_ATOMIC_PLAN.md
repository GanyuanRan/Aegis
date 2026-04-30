# Aegis Phase 5 E2E Verification Atomic Plan

状态：`Completed within approved scope`

## 1. 文档定位

本文档定义 `Aegis Phase 5 / Runtime-ready Hardening` 的第一个实施切片：**E2E 验收框架**。

本文档只负责回答以下问题：

- 如何最终证明"Aegis Method Pack 优化后达到了预期"
- E2E 验收框架由哪些验证层次组成
- 每层验证使用什么方法、工具与通过标准
- 如何把现有分散的测试资产收敛为一个可重复执行的验收套件
- 验收框架本身如何被验证不会越权（不替代 future runtime core）

本文档不负责回答以下问题：

- future runtime core 的实现细节
- host adapter 的正式开发
- Phase 5 后续切片的完整执行方案（如 artifact contract hardening、dual-track automation）
- 全量 skills 重写

---

## 2. 当前结论

当前仓库已完成：

- `Phase 1：Authority Completion`
- `Phase 2：Skill Upgrade Wave 1`
- `Phase 3：Skill Upgrade Wave 2`
- `Phase 4：Compatibility Review`

经用户批准，当前 `Phase 5` 的第一个激活切片为：

> **E2E 验收框架** — 将分散在 completion records、smoke tests、transcript 分析中的验证手段，收敛为一个可重复执行、有明确通过标准的验收套件。

当前实际收口结论收敛为：

> **Phase 5 E2E verification slice complete within approved scope**

截至当前，以下工作已完成并有 fresh verification 支撑：

1. 本文档已从设计稿收敛为当前 approved plan
2. `tests/e2e/` 的 bootstrap skeleton、fixtures 与入口脚本已建立
3. `Phase 4 -> Phase 5` 的 authority docs 已完成第一轮对齐

当前批准切片的核心目标为：

1. 完成 `layer1-fast-check.sh` 的 host-native fast profile
2. 将边界合规、artifact schema、代表性 Codex smoke、OpenCode base suite、plugin sync 收敛为统一 Layer 1 入口
3. 记录一轮 fresh baseline run，确认 Layer 1 可重复执行，并为 Layer 2 激活提供稳定输入

当前切片只允许覆盖以下范围：

1. 验收框架的设计文档与脚本骨架
2. 第一层（快速烟雾验证）的自动化补充
3. 第二层（行为验证）的 transcript 分析工具与 with/without 对比方法
4. 第三层（E2E 场景）的场景定义与验收标准模板
5. 不与现有 `tests/` 下任何已有测试框架发生结构冲突

除非有证据证明当前切片被现有边界阻断，否则本切片不扩展到：

- future runtime core
- host adapter 正式实现
- 新宿主接入
- 未被 E2E 验收直接阻断的 skill 本文重写

---

## 3. Phase 5 交付目标

当前切片完成时，必须同时满足以下目标：

1. E2E 验收框架已设计为三层结构且已文档化
2. 第一层（快速烟雾）已有的 smoke tests + 新增的边界合规检查 + schema 检查全部可自动化执行
3. 第二层（行为验证）的 transcript 分析脚本可解析 TLREF 路径选择、artifact 产出、边界合规（量化指标待 baseline run 后定稿，不在理论阶段写死）
4. 第三层（E2E 场景）已定义至少 3 个验收场景，覆盖完整工作流 + 双轨治理 + 跨宿主
5. 所有验收脚本放在 `tests/e2e/` 目录下，与现有测试框架不冲突
6. 整个验收套件已在一轮 baseline run 中实际执行过，记录结果
7. 验收框架本身未越权声称拥有 runtime core 级别的权威裁决能力

---

## 4. 文件责任图

### 4.1 新增 canonical owners

- `docs/current/AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md`
  - 当前 atomic plan owner
- `tests/e2e/README.md`
  - E2E bootstrap 与 Layer 1 当前状态说明 owner
- `tests/e2e/run-all.sh` (Slice 5)
  - E2E 验收总入口脚本
- `tests/e2e/layer1-fast-check.sh` (Slice 2)
  - 第一层快速烟雾验证：兼容性 smoke + 边界合规 grep + schema 检查
- `tests/e2e/boundary-compliance-check.sh` (Slice 2)
  - 静态边界合规检查
- `tests/e2e/artifact-schema-check.sh` (Slice 2)
  - Artifact schema 字段完整性检查
- `tests/e2e/layer2-behavior-check.sh` (Slice 3)
  - 第二层行为验证：transcript 分析 + with/without 对比 + artifact 产出检查
- `tests/e2e/analyze-transcript.sh` (Slice 3)
  - Transcript 行为模式匹配引擎
- `tests/e2e/layer3-scenario-check.sh` (Slice 4b)
  - 第三层 E2E 场景验收：多场景编排 + 结果汇总
- `tests/e2e/scenarios/` (Slice 4a)
  - E2E 场景定义目录（每个场景一个子目录）
- `tests/e2e/baselines/without-aegis/` (Slice 3)
  - Without Aegis 对照组 transcript 归档
- `tests/e2e/fixtures/artifacts/` (Slice 1)
  - artifact schema bootstrap fixtures

### 4.2 涉及的已有 owners

- `tests/claude-code/test-helpers.sh`
  - 复用 `assert_contains`、`assert_order`、`assert_count`
- `tests/claude-code/analyze-token-usage.py`
  - 复用 transcript 解析与 token 分析
- `tests/skill-triggering/run-all.sh`
  - 第一层的兼容性 smoke 调用目标
- `tests/opencode/run-tests.sh`
  - 第一层的 OpenCode smoke 调用目标
- `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
  - 第一层的分发同步检查目标
- `docs/testing.md`
  - 需要更新以包含 E2E 验收框架说明
- `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
  - 需要回读以确认验收框架不越权
- `docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
  - 作为 artifact 产出检查的 schema 源

### 4.3 Supporting docs

- `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
  - 需要保持当前 Phase 5 / Slice 2 激活状态与 authority docs 一致
- `docs/current/AEGIS_TARGET_STATE.md`
  - 需要回读以确认验收标准与目标状态一致

---

## 5. 原子实施切片

### Slice 1：验收框架设计与 baseline 对齐

**目标：**

- 完成三层验收框架的详细设计
- 对齐 TARGET_STATE、PROCESS_BASELINE、RUNTIME_READY_BOUNDARY、ARTIFACT_SCHEMA_BASELINE 中定义的各项完成标准

**涉及文件：**

- 回读：`docs/current/AEGIS_TARGET_STATE.md`
- 回读：`docs/current/AEGIS_PROCESS_BASELINE.md`
- 回读：`docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
- 回读：`docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
- 回读：`docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md`
- 修改：本文档（定稿验收框架设计）
- 修改：`docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
- 创建：`tests/e2e/` 目录、`README.md` 与 bootstrap fixtures

**修复轨：**

1. 真实根因
   - 当前验证分散在 completion records、smoke tests、transcript 工具中，没有一个统一的、可重复执行的 E2E 验收套件。每个阶段只能凭"证据充分但分散"的结论判断是否完成，缺少一个"一键证明"的机制。
2. 唯一 canonical owner
   - 本文档 + `tests/e2e/` 目录
3. 最小必要改动
   - 只设计框架、对齐 baseline、创建目录结构。不在此切片实现具体验证逻辑。
4. 兼容边界
   - 不得与现有 `tests/` 下任何测试框架发生结构冲突。`tests/e2e/` 应作为编排层调用下层 smoke tests，而不是替代它们。
5. 验证方式
   - 人工回读确认三层设计的定义完整
   - 确认 TARGET_STATE 的 7 条完成标准在验收框架中都有对应验收项

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 各 completion records 中零散记录的"建议下一步"章节，以及 `docs/testing.md` 中只描述集成测试而没有 E2E 框架的部分。
2. 是否仍在主链生效
   - 是，因为它们仍然是当前阶段状态的真实记录。
3. 保留它的唯一理由
   - 作为当前可验证状态的分布式证据输入。
4. 删除触发条件
   - 当 E2E 验收框架形成统一入口、并在第一轮 baseline run 中产出结构化结果后。
5. 删除前验证清单
   - 不得丢失任何已有测试能力的来源和调用入口。

---

### Slice 2：第一层快速烟雾验证自动化

**目标：**

- 补充当前 smoke tests 中缺失的边界合规检查和 artifact schema 检查
- 将这三类检查与现有兼容性 smoke tests 整合为统一的 layer1 入口

**涉及文件：**

- 创建：`tests/e2e/layer1-fast-check.sh`
- 创建：`tests/e2e/boundary-compliance-check.sh`
  - Grep agent-facing prompt assets 中的越权措辞
  - 检查列表：`"granted"`、`"completion authority"`、`"authoritative"`（在 method-pack 上下文中）
- 创建：`tests/e2e/artifact-schema-check.sh`
  - 以 `tests/e2e/fixtures/artifacts/` 下的 canonical sample manifests 为 bootstrap 检查对象
  - 对照 `AEGIS_ARTIFACT_SCHEMA_BASELINE.md` 检查 5 类 artifact 的必填字段完整性
- 修改：`tests/e2e/run-all.sh`

**修复轨：**

1. 真实根因
   - 现有 smoke tests 只验证"技能是否能被触发和加载"，不验证"方法包是否越权"、"artifacts 是否完整"。这两项是 Phase 5 的核心验收项。
2. 唯一 canonical owner
   - `tests/e2e/layer1-fast-check.sh`（编排层）
   - `tests/e2e/boundary-compliance-check.sh`
   - `tests/e2e/artifact-schema-check.sh`
3. 最小必要改动
   - 边界合规检查：grep 模式匹配，不引入 NLP/LLM-based 检查
   - Schema 检查：YAML/json 字段扫描，不引入模板引擎
4. 兼容边界
   - 不得引入新宿主依赖
   - 不得改变现有 smoke tests 的输出格式和通过标准
5. 验证方式
   - `bash tests/e2e/layer1-fast-check.sh` 全部 PASS
   - 故意引入一个越权措辞 → 检查是否被检测到
   - 故意删除一个 artifact 必填字段 → 检查是否被检测到

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 无。这是新增能力。
2. 是否仍在主链生效
   - N/A。
3. 保留它的唯一理由
   - N/A。
4. 删除触发条件
   - N/A。
5. 删除前验证清单
   - N/A。

---

### Slice 3：第二层行为验证工具

**目标：**

- 构建 transcript 行为分析能力
- 建立 with/without Aegis 的对比测试方法
- 实现 artifact 产出率的自动化检查

**涉及文件：**

- 创建：`tests/e2e/analyze-transcript.sh`
  - 解析 JSONL transcript，提取 skill 调用、tool 使用、agent dispatch 等行为模式
- 创建：`tests/e2e/layer2-behavior-check.sh`
  - 编排行为验证流程
- 创建：`tests/e2e/prompts/`
  - 存放 adversarial prompts 和 E2E 场景 prompts
- 可能修改：`tests/claude-code/analyze-token-usage.py`
  - 扩展为除 token 外也能输出行为模式

**修复轨：**

1. 真实根因
   - 当前没有任何工具能自动回答"agent 的行为是否真的因为 Aegis 改变了"。 transcript 文件存在但只能人工翻看，无法规模化验证。
2. 唯一 canonical owner
   - `tests/e2e/analyze-transcript.sh`
   - `tests/e2e/layer2-behavior-check.sh`
3. 最小必要改动
   - transcript 分析基于 JSONL 结构化字段解析（`type`、`message.content`、`toolUseResult`）
   - 行为模式用 key phrase 匹配 + 时序分析（`assert_order`），不引入 ML/NLP
   - with/without 对比：同一 prompt 跑两次（一次无 Aegis 技能，一次有），比较 transcript 差异
4. 兼容边界
   - 不依赖特定宿主的 transcript 格式；默认优先支持 Claude Code JSONL 格式
   - 不对 transcript 内容做运行时 authority 裁决，只产出行为了报告
5. 验证方式
   - 对一个已知有 Aegis 的 transcript 运行分析 → 检测到 TLREF 行为
   - 对一个已知无 Aegis 的 transcript 运行分析 → 检测到无 TLREF 行为
   - with/without 对比脚本输出差异报告

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - `tests/claude-code/analyze-token-usage.py` 当前的 token-only 分析模式。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - Token 分析本身仍有价值，不需要移除。
4. 删除触发条件
   - 不需要删除。
5. 删除前验证清单
   - N/A。

---

### Slice 4a：第三层 E2E 场景定义

**目标：**

- 定义 3 个端到端验收场景的 prompt、预期行为路径、artifact 产出清单、验收标准
- 场景定义本身不依赖 transcript 分析工具，可与 Slice 3 并行推进
- 场景覆盖完整工作流、双轨治理、跨宿主一致性

**涉及文件：**

- 创建：`tests/e2e/scenarios/scenario-A-new-feature/`
  - `README.md`：场景说明、预期行为路径、验收标准
  - `prompt.txt`：启动 prompt
  - `expected-artifacts.json`：预期产出的 artifact 列表与字段
  - `expected-behavior.json`：预期的 transcript 行为模式
- 创建：`tests/e2e/scenarios/scenario-B-bug-fix/`
  - 同上结构，但聚焦 systematic-debugging + 双轨治理
- 创建：`tests/e2e/scenarios/scenario-C-cross-host/`
  - 同上结构，但聚焦同一 prompt 在 Claude Code 和 Codex 上的行为一致性

**修复轨：**

1. 真实根因
   - 没有标准化的 E2E 场景定义格式。每次验证都是临时写 prompt、临时看 transcript、临时写结论。不可重复。
2. 唯一 canonical owner
   - `tests/e2e/scenarios/` 下每个场景目录
3. 最小必要改动
   - 场景定义只用 markdown + JSON，不引入场景描述语言
   - 预期行为路径用线性步骤表达（不引入图匹配引擎）
   - 先定义 3 个场景，不贪多
4. 兼容边界
   - 场景不依赖特定宿主运行（但跨宿主场景需要 2+ 宿主）
   - 预期行为路径只描述"skill 调用顺序"和"artifact 产出"，不做 authority 裁决
5. 验证方式
   - 人工审阅场景定义：确认覆盖了 brainstorming → planning → implementation → review 完整链路
   - 每个场景的预期行为可用自然语言阅读验证

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 无。这是新增能力。
2. 是否仍在主链生效
   - N/A。
3. 保留它的唯一理由
   - N/A。
4. 删除触发条件
   - N/A。
5. 删除前验证清单
   - N/A。

---

### Slice 4b：场景运行编排（依赖 Slice 3）

**目标：**

- 实现场景验收的自动化编排：启动 session → 收集 artifacts + transcript → 对比预期
- 依赖 Slice 3 的 transcript 分析工具就绪后才能运行

**涉及文件：**

- 创建：`tests/e2e/layer3-scenario-check.sh`
  - 编排场景验收流程：启动 session → 收集 artifacts + transcript → 对比预期

**修复轨：**

1. 真实根因
   - 场景定义后如果没有自动化运行脚本，每次验收仍需手动操作，降低可重复性。
2. 唯一 canonical owner
   - `tests/e2e/layer3-scenario-check.sh`
3. 最小必要改动
   - 脚本只编排流程，具体的 transcript 分析委托给 Slice 3 的 `analyze-transcript.sh`
4. 兼容边界
   - 场景不依赖特定宿主运行（但跨宿主场景需要 2+ 宿主）
   - 预期行为路径只描述"skill 调用顺序"和"artifact 产出"，不做 authority 裁决
5. 验证方式
   - 每个场景的 expected-behavior.json 可通过 transcript 分析结果对比
   - 每个场景的 expected-artifacts.json 可通过产出物字段检查对比

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 无。这是新增能力。
2. 是否仍在主链生效
   - N/A。
3. 保留它的唯一理由
   - N/A。
4. 删除触发条件
   - N/A。

---

### Slice 5：Baseline run 与结果记录

**目标：**

- 在当前环境下实际运行一次完整的 E2E 验收套件
- 记录结果、失败项、环境 blocker
- 根据运行结果调整验收标准和脚本

**涉及文件：**

- 修改：`tests/e2e/` 下所有脚本（fix bugs from baseline run）
- 创建：`docs/current/AEGIS_PHASE5_E2E_BASELINE_RUN.md`
  - 记录 baseline run 的环境、命令、结果、失败分析
- 修改：`docs/testing.md`
  - 新增 E2E 验收框架说明

**修复轨：**

1. 真实根因
   - 框架设计完成后如果不跑一次 baseline，无法知道设计是否合理、通过标准是否可达。
2. 唯一 canonical owner
   - 本次 baseline run 的记录文档
3. 最小必要改动
   - 只调整通过标准和脚本 bug，不改变框架设计
   - 环境 blocker 要显式记录，不隐藏
4. 兼容边界
   - baseline run 只依赖当前宿主环境（Claude Code），跨宿主场景可按环境可用性选择跳过或记录 blocker
5. 验证方式
   - `bash tests/e2e/run-all.sh` 完整运行，记录每层结果
   - 所有 blocker 有显式原因说明

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - `docs/testing.md` 中只描述集成测试而不包含 E2E 框架的内容。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 集成测试说明本身是权威的。
4. 删除触发条件
   - 不需要删除，只需补充 E2E 框架说明。
5. 删除前验证清单
   - N/A。

---

### Slice 6：验收标准定稿与 Phase 5 收口准备

**目标：**

- 根据 baseline run 结果定稿验收标准
- 确认验收框架达到 Phase 5 的通过门槛
- 记录残余风险与下一 slice 建议

**涉及文件：**

- 修改：本文档（验收标准定稿）
- 修改：`docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
- 创建：`docs/current/AEGIS_PHASE5_E2E_COMPLETION_RECORD.md`

**修复轨：**

1. 真实根因
   - 验收标准必须在实际运行后才能定稿。理论标准不经实践检验就是猜测。
2. 唯一 canonical owner
   - 本文档 + Phase 5 收口记录
3. 最小必要改动
   - 只调整通过数值、环境 blocker 处理方式、跨宿主回退策略
   - 不改变框架结构
4. 兼容边界
   - 验收标准不得要求"全环境全场景通过才准入"——需要区分"硬性门槛"和"环境依赖门槛"
5. 验证方式
   - 对照 TARGET_STATE 的 7 条完成标准逐一确认
   - 每项给出置信度评级（A/B/C）

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 各 Phase completion records 中的"建议下一步"章节将随 Phase 5 推进而逐步退役。
2. 是否仍在主链生效
   - 当前是。
3. 保留它的唯一理由
   - 作为历史轨迹。
4. 删除触发条件
   - 当 Phase 5 收口记录发布了更完整的后续建议后。
5. 删除前验证清单
   - 不丢失任何有价值的观察和风险评估。

---

## 6. 三层验收框架设计

### 6.1 第一层：快速烟雾验证（Layer 1 — Fast Check）

**目标：** 每次变更后快速验证方法包没有结构性问题

| 检查项 | 方法 | 工具 | 通过标准 | 预计耗时 |
|--------|------|------|----------|----------|
| 兼容性 smoke | 调用现有 `tests/skill-triggering/` + `tests/opencode/` | 现有 shell 脚本 | 全部 PASS | 2-3 min |
| 边界合规 | Grep SKILL.md + docs 中越权措辞 | `tests/e2e/boundary-compliance-check.sh` | 零匹配 | < 1 min |
| Artifact schema | 检查 artifact 模板字段完整性 | `tests/e2e/artifact-schema-check.sh` | 零字段缺失 | < 1 min |
| 分发同步 | 调用 `tests/codex-plugin-sync/` | 现有 shell 脚本 | PASS | < 1 min |

**总预计耗时：** < 5 分钟

**运行条件：** 无需真实 Claude 会话，纯静态检查 + smoke tests

**边界合规策略说明：**

边界合规检查采用两层防线，不是单一 grep：

- **L1（静态）**：`boundary-compliance-check.sh` 用 grep 匹配已知越权关键词（"granted"、"completion authority"、"authoritative" 等）。速度快、无歧义，但只能检测措辞层面的越权。
- **L2（动态）**：`analyze-transcript.sh` 在 transcript 中检查 agent 的行为表述是否出现 authority drift，例如 agent 自称"已做出最终判定"、"本次决策为最终结果"等不包含关键词但语义越权的表述。检出即 fail，不通过 NLP 而是基于行为上下文模式匹配。

L1 作为变更预提交检查（每次改动必跑），L2 作为行为验收的一部分（每个 E2E 场景必检）。

### 6.2 第二层：行为验证（Layer 2 — Behavior Check）

**目标：** 证明 agent 行为确实因为 Aegis 而改变，而非只是文档变了

| 检查项 | 方法 | 工具 | 量化指标 | 预计耗时 |
|--------|------|------|----------|----------|
| TLREF 采纳率 | with/without 对比 + transcript 分析 | `tests/e2e/analyze-transcript.sh` | TBD (待 baseline run 后定稿) | 10-20 min |
| Artifact 产出率 | 检查每个 E2E 场景的 artifact 完整性 | `tests/e2e/layer2-behavior-check.sh` | TBD (待 baseline run 后定稿) | 5-10 min |
| 双轨执行率 | 修复类任务 transcript 中修复轨+退役轨存在 | transcript 分析 | 100%（限于适用双轨治理的任务） | 5 min |
| 技能压力测试 | adversarial prompts + transcript 检查 | `tests/skill-triggering/` 扩展 | TBD (待 baseline run 后定稿) | 15-20 min |
| 边界合规（动态） | transcript 中是否出现越权措辞 | transcript 分析 | 零越权 claim | 5 min |

**TLREF 采纳率测量范围说明：**

第一版 TLREF 采纳率只测量以下两层（在 transcript 中最容易识别）：

1. **路径选择**：任务开始时是否在快速路径和标准路径之间做出显式选择
2. **Reflection Checklist**：每轮完成时是否输出了 Goal / Evidence / Risk / Decision 四项

不要求完整的三层 DIVE 循环（Define → Investigate → Validate → Evolve）才算"采纳"。这一点将在 baseline run 后根据实际数据决定是否需要收紧标准。

**关键方法：with/without 对比**

```
同一 prompt 跑两次：
  Without Aegis → 使用原始系统 prompt，无技能加载
  With Aegis    → 正常加载技能

对比维度：
  1. 是否主动询问需求？（brainstorming 触发）
  2. 是否先写测试？（TDD 触发）
  3. 是否进行根因分析？（debugging 触发）
  4. 是否产出了 artifact？（draft 产出）
  5. 是否进行了双轨分析？（修复轨+退役轨）
```

**总预计耗时：** 30-60 分钟（依赖真实 Claude 会话）

**约束：without 基线可重复性**

Without 基线必须在以下固定条件下运行以确保可重复性：

- 同一宿主（如 Claude Code 版本固定）
- 同一模型版本
- 同一会话配置（无额外 skill 注入）
- 对照组 transcript 应归档至 `tests/e2e/baselines/without-aegis/` 作为 reference

任何改变以上条件之一的对比结果，均不能直接与当前 with/without 差值做比较。

### 6.3 第三层：E2E 场景验收（Layer 3 — Scenario Check）

**目标：** 通过完整工作流验证方法包的端到端行为一致性

**场景定义：**

| 场景 | 覆盖路径 | 核心验证点 | 跨宿主 |
|------|----------|------------|--------|
| **A：新功能开发** | brainstorming → ImpactStatementDraft → writing-plans → TDD → review → finishing-branch | 完整 artifact 链 + GateInputPack 产出 | 1+ 宿主 |
| **B：Bug 修复** | systematic-debugging → ImpactStatementDraft(双轨) → verification-before-completion → EvidenceBundleDraft | 根因分析深度 + 双轨治理证据化 | 1+ 宿主 |
| **C：跨宿主迁移** | 同一 plan 在 Claude Code + Codex 上执行 | 行为路径偏差 ≤ 2 步（"步" = 一次 skill 调用或 artifact 产出事件） | 2+ 宿主（环境依赖） |

**场景依赖说明：**

- 场景 A 和 B 为**硬性门槛**：所有宿主必须通过（至少 1 个宿主覆盖）
- 场景 C 为**弹性门槛**：仅在 2+ 宿主同时可用时执行；若当前环境仅 1 个宿主可用，场景 C 记录为 "skipped (环境限制)"，不阻断整体验收
- 跨宿主场景的硬性要求缩窄为：skill 调用链和 artifact 产出链在两个宿主上必须一致，即核心行为路径无偏差

**每个场景的验收标准模板：**

```json
{
  "scenarioId": "A",
  "requiredArtifacts": ["TaskIntentDraft", "ImpactStatementDraft", "EvidenceBundleDraft", "GateInputPack"],
  "requiredBehavior": {
    "skillSequence": ["brainstorming", "writing-plans", "test-driven-development", "requesting-code-review"],
    "mustContain": ["证据", "影响面", "影响范围"],
    "mustNotContain": ["granted", "completion authority"]
  },
  "passCriteria": {
    "artifactsComplete": true,
    "behaviorMatch": true,
    "boundaryCompliant": true,
    "gitHistoryExists": true
  }
}
```

**总预计耗时：** 2-4 小时（3 个场景，含真实会话时间）

---

## 7. 最低验证矩阵

当前切片结束前，至少要 fresh 运行：

```bash
# Layer 1: Fast checks
bash tests/e2e/layer1-fast-check.sh

# Layer 2: Behavior check (requires Claude CLI)
bash tests/e2e/layer2-behavior-check.sh

# Layer 3: E2E scenarios (requires Claude CLI, ~2-4 hours)
bash tests/e2e/layer3-scenario-check.sh

# Full suite
bash tests/e2e/run-all.sh
```

若当前环境不具备 Claude CLI 或跨宿主条件，则至少跑：

- `tests/e2e/layer1-fast-check.sh`（静态检查 + smoke，无需 Claude）
- 场景 A（新功能开发，单宿主）
- 切片对应的修复轨回望 + 退役轨回望

---

## 8. 验收框架的边界约束

E2E 验收框架本身必须遵守 `AEGIS_RUNTIME_READY_BOUNDARY.md`：

- 验收框架可以：
  - 输出行为报告
  - 输出 artifact 完整性检查
  - 输出边界合规检查
  - 输出 with/without 对比差异
  - 给出 advisory-level 结论（"建议继续"、"建议修复"）
- 验收框架不可以：
  - 输出 authoritative "PASS/BLOCK/GRANTED" 作为最终裁决
  - 声称拥有 completion authority
  - 把一次 baseline run 的结果写成永久性权威 truth
  - 依赖未来 runtime core 的能力才能工作

---

## 9. 完成判据

只有同时满足以下条件，当前切片才算完成：

1. 三层验收框架设计已定稿并文档化
2. `tests/e2e/` 目录存在且包含 layer1/layer2/layer3 入口脚本骨架
3. 边界合规检查脚本可运行并正确检测越权措辞
4. Artifact schema 检查脚本可运行并正确检测字段缺失
5. Transcript 分析脚本可解析 JSONL 并提取行为模式
6. 至少 3 个 E2E 场景已定义（含 prompt、预期行为、验收标准）；其中场景 C（跨宿主）标记为环境依赖，非阻断条件
7. 至少完成一轮 baseline run，结果已记录；环境 blocker 已显式分类（硬性门槛 vs 弹性门槛）
8. 所有通过标准区分了"硬性门槛"和"环境依赖门槛"
9. 验收框架本身未越权声称拥有权威裁决能力
10. `docs/testing.md` 已更新包含 E2E 验收框架说明

当前收口状态：

- 上述条件已满足
- baseline run 记录见 `docs/current/AEGIS_PHASE5_E2E_BASELINE_RUN.md`
- completion record 见 `docs/current/AEGIS_PHASE5_E2E_COMPLETION_RECORD.md`

---

## 10. 当前建议的实施顺序

1. **Slice 1：验收框架设计** — 先设计再实现，确保与 TARGET_STATE 等 baseline 对齐
2. **Slice 2：第一层自动化** — 静态检查最容易实现，快速见效
3. **Slice 3：行为验证工具** — transcript 分析是第二层和第三层的共同依赖
4. **Slice 4a：E2E 场景定义** — 与 Slice 3 并行推进，因为场景定义不依赖分析工具
5. **Slice 4b：场景运行编排** — 依赖 Slice 3 的转录分析工具就绪
6. **Slice 5：Baseline run** — 所有工具就位后跑一次完整验收
7. **Slice 6：验收标准定稿** — 根据实际运行结果调整标准

理由：

- 设计先行 → 避免实现过程中反复修正方向
- 静态检查先行 → 快速获得自动化保护，建立信心
- 场景定义（4a）与分析工具（3）无依赖，可并行 → 减少总工期
- 场景运行（4b）与分析工具（3）有依赖 → 必须等分析工具就绪
- Baseline run 后定稿标准 → 避免理论标准脱离实际
