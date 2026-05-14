# Aegis 工作流程说明

Status: `Approved`

## 1. 文档定位

本文面向需要理解和使用 `Aegis Method Pack` 的中文读者，说明 Aegis
在一次工程任务中如何触发、路由、执行、验证和收口。

本文是说明性指南，权威来源仍按以下顺序读取：

1. `AGENTS.md`
2. `docs/current/README.md`
3. `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
4. 任务相关的 `docs/current/*.md`
5. 宿主安装与使用文档

本文不新增 runtime 权威，不授予 `GateDecision`，也不授予
`completion authority`。

---

## 2. 一句话理解 Aegis

Aegis 当前是：

> `Aegis Method Pack (runtime-ready)`

它的职责是把 AI coding agent 的工作过程变得更稳定、更证据驱动、更可恢复：

- 先判断任务类型和风险，而不是直接改代码
- 先读项目基线和 authority source，而不是凭会话印象行动
- 把复杂任务拆成可验证的小步骤
- 让修复、兼容、退休旧逻辑和验证证据同时可见
- 产出 runtime-ready 的 draft、hint、projection，供未来 runtime core 消费

它当前不负责：

- 最终治理裁决
- authoritative `PolicySnapshot`
- authoritative `GateDecision`
- 最终 `completion authority`

---

## 3. 总体流程

Aegis 的一次标准工作流可以概括为：

```text
启动路由
  -> 任务分级
  -> 基线读取
  -> 问题定义
  -> 调查与方案判断
  -> 计划与最小切片
  -> TDD / 实施
  -> 验证与回归
  -> 反思与质量收口
  -> 输出事实、证据、影响面和剩余风险
```

不同任务不会强行走同一套重流程。简单任务走 fast path，复杂任务才进入
standard path。

---

## 4. 启动路由

每轮任务开始时，Aegis 先判断是否有相关 skill 需要加载。

典型入口是 `using-aegis`：

- 它只负责轻量路由
- 它不承载完整 workflow
- 它不替代具体任务 skill
- 它不把所有触发规则塞进一个入口文件

如果用户明确调用某个 skill，例如 `aegis:systematic-debugging` 或
`aegis:writing-plans`，则优先进入对应 skill。

如果用户以 `/aegis-goal <任务>` 或 `Aegis goal: <任务>` 开始，则先加载
`goal-framing`。它只生成轻量 `TaskIntentDraft` 边界：目标、成功证据、停止条件
和非目标，然后再继续路由。Goal framing 默认不创建项目文件，也不授予
completion authority。

示例：

```text
Aegis goal: 修复登录后偶发跳回登录页，不重写 auth 系统。
```

按 goal frame 的信号路由：

| Goal signal | Route |
| --- | --- |
| 单 owner、低风险、验证路径清楚 | fast path 或 `test-driven-development` |
| bug、失败、回归、异常行为 | `systematic-debugging` |
| 产品、架构、contract、跨模块行为不清 | `brainstorming` |
| spec 已批准、需求稳定、需要切任务 | `writing-plans` |
| 多步骤、handoff、容易压缩上下文 | `long-task-continuation` |
| 完成、发布、交付、"是否已完成" | `verification-before-completion` |

如果任务很小，例如事实问答、版本状态、极小文案调整，可以只做快速判断并继续，
不创建项目工作区记录。

---

## 5. 任务分级

Aegis 按复杂度选择执行路径。

### 5.1 Fast Path

适用场景：

- 简单问答
- 明确的小配置调整
- 低风险单文件微改
- 不涉及 contract、架构、跨模块或共享逻辑的任务

执行要求：

- 简要确认意图
- 读取必要证据
- 直接处理
- 做与风险匹配的验证
- 输出结果、证据和剩余未知

### 5.2 Standard Path

适用场景：

- bug 诊断
- 新功能
- 重构
- 架构调整
- 性能问题
- contract、schema、共享模块或跨模块行为变更

执行要求：

- 先定义问题和验收标准
- 读取相关 baseline / authority docs
- 明确 owner、影响面、兼容边界和非目标
- 做计划和最小切片
- 实施后进行验证、回归和质量收口

### 5.3 High-Complexity Path

适用场景：

- 目标不清或方案空间较大
- 架构边界可能改变
- 涉及多个 producer / consumer
- 会影响公共 API、schema、持久化、缓存、导出或 source-of-truth
- 需要用户确认设计方向

执行要求：

- 先写 Spec Brief 或 Design Spec
- 先做计划，再执行
- 需要时创建 `docs/aegis/work/` 任务记录
- 在用户确认或 authority source 明确前，不把推论当结论

---

## 6. 基线优先

非简单任务进入执行前，需要先读取最小相关基线。

在 Aegis 仓库内，常见起点是：

- `docs/current/README.md`
- `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
- 任务相关的 `docs/current/*.md`

在普通项目中，候选基线包括：

- 项目 `AGENTS.md`
- README
- ADR
- `docs/current/`
- `docs/aegis/baseline/`
- 架构、contract、测试或运行文档

如果没有可用基线，Aegis 会先做有界扫描：从文件索引、README、manifest、入口文件、
关键模块和测试推断最小上下文。只有在证据足够时，才初始化项目 baseline。

---

## 7. 标准执行循环：DIVE

Standard path 的最小循环是 `DIVE`。

### 7.1 Define

目标是把任务说清楚：

- 要解决什么
- 谁受影响
- 当前环境是什么
- 问题在哪里复现
- 为什么现在要做
- 计划怎么做
- 验收标准是什么

### 7.2 Investigate

目标是找到真实 owner 和原因：

- 数据流从哪里来，到哪里去
- 谁是 canonical owner
- 是否涉及兼容边界
- 是否存在 fallback、adapter、重复 owner 或历史补丁
- 是否需要从局部 bug 上钻到架构或 contract 层

### 7.3 Validate

目标是确认判断和实现都有证据：

- 证据是否支持当前结论
- 变更是否满足验收标准
- 是否新增风险、漂移或隐藏依赖
- 测试是否覆盖真实用户路径和关键边界

### 7.4 Evolve

目标是决定是否可以收口：

- 当前任务是否可以结束
- 是否需要继续迭代
- 是否需要升级问题定义
- 是否需要更新 baseline、ADR、计划或验证策略

---

## 8. 反思与质量门

标准任务每一轮都要完成最小反思：

```text
Goal:
DeeperCause:
Evidence:
Risk/Unknown:
Decision:
```

质量收口不等于“看起来能跑”。收口前至少要说明：

- 做了什么验证
- 哪些行为已被证据覆盖
- 哪些风险仍然存在
- 回滚边界是什么
- 是否有旧 owner、fallback、adapter 或兼容路径需要删除或记录

---

## 9. 双轨治理

对 bug 修复、架构重构、contract 调整和治理清理，Aegis 默认使用双轨治理。

### 9.1 Repair Track

必须回答：

- 真实根因是什么
- 唯一 canonical owner 是谁
- 最小必要改动是什么
- 兼容边界在哪里
- 如何验证

### 9.2 Retirement Track

必须回答：

- 旧逻辑、重复 owner、fallback 或历史补丁在哪里
- 是否仍在主链路生效
- 能否在当前切片删除
- 如果不能删除，保留理由、观测指标和退休时机是什么
- 删除或保留后如何验证没有残留引用或误伤

默认原则是：新增修复时同时处理旧逻辑。不能只加新分支，而不交代旧分支。

---

## 10. TDD 与测试铁律

TDD 是实施阶段的纪律，不是所有复杂任务的第一入口。

进入实现前，需要先确认：

- 需求或问题已定义清楚
- owner 和影响面已识别
- 该读的 baseline 已读
- 任务可拆成可验证的小切片

测试铁律：

- 代码错，修代码
- 测试错，修测试
- 不能用改测试掩盖业务缺陷
- 不能用改业务代码迁就错误测试
- 最终目标是业务行为正确，测试预期也正确

---

## 11. 触发健康诊断

如果 Aegis 已安装，但预期 skill 没有可靠触发，不要第一反应就给 description
堆更多关键词。

应按触发链路诊断：

1. install and version visibility
2. host skill discovery
3. activation mode and bootstrap entry
4. `using-aegis` router entry
5. task-to-skill routing
6. skill execution depth
7. context pressure and re-entry
8. false positive over-triggering

常见处理方式：

- 先确认安装根目录和版本
- 再确认宿主能发现当前 `skills/`
- 再确认是否需要重启或 reload
- 再确认 activation mode 是 `auto` 还是 `explicit`
- 再显式调用 `aegis:using-aegis` 或目标 skill 做对照

详细诊断层见 `docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md`。

---

## 12. 长任务与工作区记录

Aegis 支持惰性项目工作区。

默认不创建 `docs/aegis/` 的情况：

- 全局安装或版本查询
- 简单问答
- 小文案调整
- 低风险快速任务

需要创建或使用 `docs/aegis/` 的情况：

- baseline bootstrap
- Spec Brief / Design Spec
- 中高复杂度计划
- ripple triage
- 长任务续跑
- 需要可恢复证据链的工作
- 完成态从长期架构决策中自动回写 ADR

典型结构：

```text
docs/aegis/
├── README.md
├── INDEX.md
├── BASELINE-GOVERNANCE.md
├── adr/
├── baseline/
├── specs/
├── plans/
└── work/
```

这些记录是方法层证据和交接材料，不是最终 runtime 裁决。

### 12.1 ADR 自动回写

ADR 自动回写发生在任务接近完成时，而不是执行前。

当已完成工作改变了长期架构面，Aegis 应检查是否需要创建、修订、替代或跳过 ADR。
读取证据时使用最强可用来源：

```text
work -> plan -> spec -> git / verification evidence
```

长期架构面包括 owner、公共 contract、依赖方向、source-of-truth owner、宿主兼容策略、
runtime-ready artifact 边界，以及被保留或退役的 fallback / adapter / 兼容路径。

ADR 与 baseline 是联动的：

```text
ADR 记录为什么这样决策。
baseline 记录当前架构状态。
```

当 ADR 改变或确认了当前架构状态，Aegis 必须执行 baseline sync check。
如果 baseline 不更新，ADR 或反思记录中应说明现有 baseline 为什么仍然成立。

详见 `docs/current/AEGIS_ADR_AUTO_BACKFILL.md`。

---

## 13. 常见 skill 如何分工

`using-aegis`
: 判断是否需要进入 Aegis workflow，并选择合适 skill。

`brainstorming`
: 用于新功能、产品行为、UI、架构、contract 或中高复杂度方向澄清。

`writing-plans`
: 在已有 spec 或需求后，把工作拆成可验证、可执行的小任务。

`executing-plans`
: 执行已写好的计划，并在阶段间保留检查点。

`systematic-debugging`
: 面对 bug、测试失败或异常行为时，从症状追到真实根因。

`test-driven-development`
: 在实施 feature 或 bugfix 前，用测试驱动最小实现和回归验证。

`first-principles-review`
: 当方向复杂、反复修补、fallback 膨胀、owner 重复或用户明确要求第一性原理时使用。若方案选择或任务拆解会固化 owner、retirement、fallback、adapter 或长期稳定性判断，可升级为 decision hygiene review，检查第一性原则不变量、owner / retirement 和反证场景。

`requesting-code-review`
: 完成重要实现后，检查行为风险、回归和测试缺口。

`verification-before-completion`
: 在声称完成、修复、通过、可发布或可交付前，确认有新鲜验证证据。对触及长期架构面的中高复杂度工作，还要执行 ADR 自动回写检查。如果存在 goal framing，还要补 Goal Closure：goal status、success evidence、stop state，以及 non-goals 是否被遵守。

`long-task-continuation`
: 长任务、跨上下文、跨会话或需要交接时，维护 checkpoint、resume hint 和 drift check。

---

## 14. 最终输出形态

Aegis 面向用户的输出优先使用中文，并遵循：

```text
事实 -> 推论 -> 结论
```

最小输出应包含：

- Facts
- Evidence
- Recommendation / Approach
- Impact Scope

按任务类型补充：

- 诊断：复现、根因、阻塞点
- 功能：验收标准、接口或数据 contract 变化
- 架构：方案比较、取舍、ADR 引用
- 重构：热点、测试安全网、复杂度变化
- 性能：基线、瓶颈、收益
- 风险与回滚：触发条件、回滚步骤、feature flag

---

## 15. 边界提醒

Aegis 可以让宿主工作得更像一个治理严谨的工程代理，但当前仓库仍然只是
`Method Pack`。

因此，Aegis 当前可以产出：

- `TaskIntentDraft`
- `BaselineReadSetHint`
- `ImpactStatementDraft`
- `EvidenceBundleDraft`
- `GateInputPack`
- `SubagentContextPacket`
- `TodoCheckpointDraft`
- `ResumeStateHint`
- `DriftCheckDraft`

这些都是 draft、hint 或 projection input。它们可以帮助未来 runtime core
做判断，但不能被写成当前仓库已经拥有的最终权威。
