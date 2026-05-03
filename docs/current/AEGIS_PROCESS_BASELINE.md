# Aegis Process Baseline

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis Method Pack` 当前生效的流程基线。

本文档只负责回答以下问题：

- `Aegis` 方法层采用什么执行框架
- 标准任务与快速任务分别如何处理
- 证据、反思、质量保证与输出契约如何收敛
- 这些规则将来应该投影到哪些 skills 中

本文档不负责回答以下问题：

- 某个具体任务的结论是否正确
- future runtime core 的权威裁决细节
- host adapter 的实现方式

---

## 2. 语言与表达约定

`Aegis` 当前默认采用以下表达约定：

- 思考过程与标识符使用英文
- 面向用户的表达与说明使用中文
- 优先给出直接 verdict，再展开证据与理由
- 输出遵循“事实 -> 推论 -> 结论”的顺序

---

## 3. 核心原则

当前流程基线遵循以下核心原则：

- 证据驱动：事实、假设、未知分离
- 系统性思维：从架构层理解影响面与依赖关系
- 最小必要改动：优先局部、最短路径、避免无必要实体增长
- 向后兼容优先：变更默认保留既有行为
- 阶段验证：每次重要变更后必须做回归验证与架构回望

---

## 4. Todo 复述循环

对标准路径任务，必须显式执行 todo 复述循环：

1. 任务开始时创建或更新 todo
2. 列出完整步骤
3. 每次阶段切换前回读 todo
4. 写回当前状态与下一步

todo 复述循环的目标不是形式化打卡，而是防止任务在分析、执行或验证阶段发生范围漂移。

---

## 5. TLREF：路径选择

`Aegis` 当前采用三层反思执行框架中的路径选择层：

### 5.1 快速路径

适用任务：

- 知识问答
- 配置调整
- 依赖升级
- 其他低风险、边界清晰、无需深度治理的问题

执行要求：

- 直接执行
- 结果验证
- 必须保留事实证据

### 5.2 标准路径

适用任务：

- 诊断
- 功能
- 架构
- 重构
- 性能

执行要求：

- 问题界定
- 分析决策
- 执行验证
- 质量保证

todo 复述循环必须贯穿标准路径。

---

## 6. DIVE：标准路径最小循环

对标准路径任务，当前最小执行循环为：

- `Define`
- `Investigate`
- `Validate`
- `Evolve`

### 6.1 Define

至少覆盖：

- `What / Who / When / Where / Why / How / How much`
- 当前环境与可复现基线
- 成功标准与验收方式

### 6.2 Investigate

至少覆盖：

- 数据流与 owner
- 兼容边界
- 特殊情况是业务必需还是历史补丁
- 局部问题是否已上升到架构层

### 6.3 Validate

至少覆盖：

- 证据是否能支撑当前判断
- 实施后是否满足验收
- 是否引入新的风险、漂移或隐性缺口

### 6.4 Evolve

至少覆盖：

- 当前结论是退出、继续迭代还是升级问题界定
- 是否需要修订 baseline、ADR、review 或验证策略

---

## 7. Reflection Checklist

对标准路径任务，每一轮都必须完成最小 reflection：

- `Goal`
- `DeeperCause`
- `Evidence`
- `Risk/Unknown`
- `Decision`

其中：

- 若 `DeeperCause` 不能明确回答为“否”，不得直接退出
- 若 `Evidence` 不能支撑当前判断，不得把推论包装成结论
- 若存在架构层未触及的问题，不得把诊断任务视为完成

---

## 8. 质量保证

对标准路径任务，退出 reflection loop 后必须进入质量保证：

- `Remove/Restore`
- 回滚准备
- 置信度评估
- 资产沉淀

最小原则：

- 不是“功能看起来好了”就结束
- 必须说明副作用、残余风险与回滚边界

---

## 9. 测试失败铁律

当前流程基线明确拒绝以下行为：

- 修改测试来掩盖业务代码缺陷
- 修改业务代码去迎合错误测试
- 在未定位错误源前直接双向迁就

必须执行的原则是：

- 代码错修代码
- 测试错修测试
- 最终保证业务行为正确且测试预期准确

---

## 10. 最终输出契约

当前 `Aegis` 对外输出最少必须包含：

- `事实`
- `证据`
- `建议/方案`
- `影响面`

按任务类型扩展：

- 诊断任务：复现步骤、根因、阻断点
- 功能任务：验收标准、接口或数据契约变更
- 架构任务：选项对比、权衡、ADR 引用
- 重构任务：热点、测试安全网、复杂度变化
- 性能任务：基线、瓶颈、收益
- 风险与回滚：触发条件、回滚步骤、特性开关

---

## 11. Project Workspace 与复杂度路由

`Aegis` 可以在具体项目中维护轻量 project workspace，但必须遵循：

- 懒创建：全局安装不写入用户项目；只有项目内 workflow 需要落盘产物时才创建。
- 先沿用：已有 `docs/`、ADR、architecture docs、README、AGENTS 或 baseline owner 时，优先引用现有 authority，不复制一套权威。
- 按任务生成：中高复杂度任务的过程记录默认进入 `docs/aegis/work/YYYY-MM-DD-<task-slug>/`。
- 按价值提升：只有可复用的项目事实、长期决策、设计或计划，才提升到 `baseline/`、`adr/`、`specs/` 或 `plans/`。

默认最小结构是：

```text
docs/aegis/
  README.md
  INDEX.md
```

中复杂度任务的默认过程包是：

```text
docs/aegis/work/YYYY-MM-DD-<task-slug>/
  00-intent.md
  10-baseline-readset.md
  30-plan.md
  40-atomic-tasks.md
  50-evidence.md
```

复杂度路由约束：

- 低复杂度任务可以在简短 intent 与 baseline check 后进入 TDD。
- 中复杂度任务必须先有 baseline read-set、plan 与 atomic tasks，再进入 TDD。
- 高复杂度任务必须先有 spec/design 与 plan；需要用户确认时不得跳过确认。

`TDD` 是实现纪律，不是中高复杂度任务的第一入口。

---

## 12. 对现有 skills 的投影目标

本流程基线后续应优先投影到以下 skills：

- `brainstorming`
  - 增加 TLREF 的问题界定与范围判断
- `using-aegis`
  - 增加复杂度路由与 project workspace 懒创建边界
- `systematic-debugging`
  - 显式覆盖“现象 -> 逻辑 -> 系统 -> 架构”四层诊断
- `writing-plans`
  - 引入 impact、compat、retirement 与 verification 视角
- `test-driven-development`
  - 将 TDD 定位为 approved atomic task 的实现纪律，避免中高复杂度任务绕过计划
- `requesting-code-review`
  - 增加证据充分性与架构漂移检查
- `verification-before-completion`
  - 与 reflection、QA 和最终输出契约对齐

---

## 13. 当前约束

后续所有 skill 改造都必须满足以下要求：

- 规则要可触发、可执行，而不是哲学化长文
- 过程约束尽量落入具体 workflow，而不是仅停留在总纲口号
- method pack 可以组织推理与产物，但不能越权宣布 authoritative completion
