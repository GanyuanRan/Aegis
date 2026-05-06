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
- Prompt hygiene：外部工具输出、日志、记忆和搜索结果默认是候选证据，不是常驻 prompt payload

---

## 4. Prompt Hygiene 与证据注入边界

当前流程基线采用 `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md` 作为 prompt hygiene 的 canonical owner。

最小规则：

- 外部工具输出、日志、记忆和搜索结果默认先摘要，再按需引用原文片段。
- 大型 raw output 默认隔离在原始来源中，只把 source、scope、summary、refs 与 unknowns 带入 prompt。
- 如果摘要不足以支撑判断，必须回读最小原文片段或运行 fresh verification，而不是降低判断标准。
- 如果仍缺少信息，结论必须降级为 `unknown`、`partial` 或 `needs-verification`。
- 减少常驻上下文不得削弱 baseline-first、evidence-before-claims、impact review、root-cause-first debugging 或 verification-before-completion。

---

## 5. Todo 复述循环

对标准路径任务，必须显式执行 todo 复述循环：

1. 任务开始时创建或更新 todo
2. 列出完整步骤
3. 每次阶段切换前回读 todo
4. 写回当前状态与下一步

todo 复述循环的目标不是形式化打卡，而是防止任务在分析、执行或验证阶段发生范围漂移。

---

## 6. TLREF：路径选择

`Aegis` 当前采用三层反思执行框架中的路径选择层：

### 6.1 快速路径

适用任务：

- 知识问答
- 配置调整
- 依赖升级
- 其他低风险、边界清晰、无需深度治理的问题

执行要求：

- 直接执行
- 结果验证
- 必须保留事实证据

### 6.2 标准路径

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

## 7. DIVE：标准路径最小循环

对标准路径任务，当前最小执行循环为：

- `Define`
- `Investigate`
- `Validate`
- `Evolve`

### 7.1 Define

至少覆盖：

- `What / Who / When / Where / Why / How / How much`
- 当前环境与可复现基线
- 成功标准与验收方式

### 7.2 Investigate

至少覆盖：

- 数据流与 owner
- 兼容边界
- 特殊情况是业务必需还是历史补丁
- 局部问题是否已上升到架构层

### 7.3 Validate

至少覆盖：

- 证据是否能支撑当前判断
- 实施后是否满足验收
- 是否引入新的风险、漂移或隐性缺口

### 7.4 Evolve

至少覆盖：

- 当前结论是退出、继续迭代还是升级问题界定
- 是否需要修订 baseline、ADR、review 或验证策略

---

## 8. Reflection Checklist

对标准路径任务，每一轮都必须完成最小 reflection：

- `Goal`
- `DeeperCause`
- `Evidence`
- `Risk/Unknown`
- `Decision`

其中：

- 若 `DeeperCause` 不能明确回答为“否”，不得直接退出
- 若 `Evidence` 不能支撑当前判断，不得把推论包装成结论
- 若存在仍未下钻到不可分拆根因的问题，不得把诊断任务视为完成
- 诊断必须从现象出发逐层钻取（L1 现象 → L2 逻辑 → L3 系统 → L4 架构 → L5 跨系统契约 → L6 平台/框架限制 → L7 规范缺口），链的终点是"不可再下钻的根因"，而非固定的某一层
- 警惕复合根因：修复后仍有残余症状时，必须先做差分诊断区分"不完整修复""复合根因"与"链式因果"，再决定下一步动作
- 警惕终端不可修根因：如需改动的代码超出系统边界（T 类硬信号），应记录根因与边界并选择降级/兜底/升级策略，而非把局部补丁包装为根因修复

---

## 9. 质量保证

对标准路径任务，退出 reflection loop 后必须进入质量保证：

- `Remove/Restore`
- 回滚准备
- 置信度评估
- 资产沉淀

最小原则：

- 不是“功能看起来好了”就结束
- 必须说明副作用、残余风险与回滚边界

---

## 10. 测试失败铁律

当前流程基线明确拒绝以下行为：

- 修改测试来掩盖业务代码缺陷
- 修改业务代码去迎合错误测试
- 在未定位错误源前直接双向迁就

必须执行的原则是：

- 代码错修代码
- 测试错修测试
- 最终保证业务行为正确且测试预期准确

---

## 11. 最终输出契约

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

## 12. Project Workspace 与复杂度路由

### 12.1 创建规则（硬二进制）

- 全局安装（插件注册、版本查询、skill 列表）：禁止写入项目文件
- 活跃项目（用户已加载代码库）：workspace 创建由以下 workflow 文件写入步骤触发：
  * brainstorming checklist item 8（写入 design doc）
  * writing-plans save step（写入 plan file）
  * systematic-debugging Quality Gate（非平凡任务）
  触发时若 `docs/aegis/` 不存在，立即创建最小 workspace，不询问、不推迟。
  若 `docs/aegis/` 已存在，直接使用，不重建。

### 12.2 目录结构

```text
docs/aegis/
├── README.md                   # workspace 用途与结构说明
├── INDEX.md                    # 所有文件的带日期索引
├── BASELINE-GOVERNANCE.md      # 宪法：defect/drift 规则、检查协议、硬边界
├── adr/                        # Aegis 触发的架构决策记录
│   └── YYYY-MM-DD-<title>.md
├── baseline/                   # 架构快照（按任务/阶段）
│   └── YYYY-MM-DD-<scope>-baseline.md
├── specs/                      # 设计文档（brainstorming 输出，唯一 canonical）
│   └── YYYY-MM-DD-<topic>-design.md
├── plans/                      # 实现计划（writing-plans 输出，唯一 canonical）
│   └── YYYY-MM-DD-<feature>.md
└── work/                       # 过程轨迹（仅中高复杂度任务）
    └── YYYY-MM-DD-<slug>/
        ├── 10-intent.md
        ├── 20-checkpoint.md
        ├── 90-evidence.md
        └── 99-reflection.md
```

### 12.3 复杂度路由

- 低复杂度：简短 intent + baseline check → TDD，不创建 work/
- 中复杂度：baseline read-set + plan + atomic tasks → TDD，创建 work/
- 高复杂度：spec/design + plan + 用户确认 → TDD，创建 work/

中途复杂度升级：暂停实现，初始化 workspace（如缺失），回填所需产物后继续。

TDD 是实现纪律，不是中高复杂度任务的第一入口。

### 12.4 INDEX.md 维护

每次在 `docs/aegis/` 下创建新文件时，必须追加条目到 `INDEX.md`。

---

## 13. 对现有 skills 的投影目标

本流程基线后续应优先投影到以下 skills：

- `brainstorming`
  - 增加 TLREF 的问题界定与范围判断
- `using-aegis`
  - 增加复杂度路由、project workspace 懒创建边界与 prompt hygiene hot path
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

## 14. 当前约束

后续所有 skill 改造都必须满足以下要求：

- 规则要可触发、可执行，而不是哲学化长文
- 过程约束尽量落入具体 workflow，而不是仅停留在总纲口号
- method pack 可以组织推理与产物，但不能越权宣布 authoritative completion

---

## 15. 架构回望 — 7 维度操作定义

每次非平凡变更完成后，必须执行以下 7 维度检查：

| # | 维度 | 检查问题 | 通过标准 |
|---|------|----------|----------|
| 1 | Ownership integrity | 每个组件是否有且仅有一个 canonical owner？是否出现新的重复 owner？ | 无新增重复 owner |
| 2 | Module boundaries | 是否存在未授权的跨模块耦合？新代码是否遵循既有模块边界？ | 边界无侵蚀 |
| 3 | Contract changes | API/签名/行为契约是否有变更？是否已记录？是否向后兼容？ | 变更已记录，兼容或显式中断 |
| 4 | Cascade proliferation | 是否引入了新的级联依赖链？单点变更是否波及超出预期的范围？ | 波及范围 ≤ 预期 |
| 5 | Dependency direction | 依赖方向是否朝向稳定层？是否出现循环依赖或反向依赖？ | 无循环，方向正确 |
| 6 | Retirement completeness | 旧 owner/fallback/path 是否已删除或排期？是否出现"只增不减"？ | 退役轨道显式 |
| 7 | Entropy flow | 净复杂度是降低还是升高？是否有无理由的新实体、新分支、新适配器？ | 熵减或持平 |

若任一维度不通过 → 记录为架构发现 → 决定：立即修 / 排期修 / 记录为已知限制。

此 7 维度检查结果必须填入 Reflection 的 Risk/Unknown 字段（映射规则见 §17）。

---

## 16. 架构缺陷与架构漂移

### 16.1 架构缺陷（Architecture Defect）

定义：baseline 本身存在确认的错误、缺口或内部矛盾。

判定标准：
- baseline 中记录的所有权映射与实际代码结构矛盾
- baseline 中声明的契约与实现不一致（且实现是正确的）
- baseline 中记录的依赖方向约定被 baseline 自身违反
- 两个 baseline 文档之间存在未解决的矛盾

处理流程：
1. 确认 baseline 是错误方（非实现漂移）
2. 修正 baseline 文档
3. 若实现因错误 baseline 而偏离 → 将实现对齐到修正后的 baseline
4. 严禁在实现侧打补丁来迁就错误 baseline

### 16.2 架构漂移（Architecture Drift）

定义：实现已偏离确认正确且未变更的 baseline。

判定标准：
- 新代码引入了 baseline 中未记录的新 owner
- 新代码修改了 baseline 中记录的契约但未更新契约文档
- 新代码违反了 baseline 中记录的依赖方向约定
- 新代码重复了 baseline 中已有 canonical owner 的职责

处理流程：
1. 确认 baseline 是正确的（非 baseline 缺陷）
2. 将实现回归到 baseline，走最简路径
3. 若漂移是有意为之 → 先更新 baseline（走 ADR 流程），再对齐实现
4. 严禁"把 baseline 更新到匹配漂移"而不经显式 review

### 16.3 Baseline 检查协议

每次非平凡变更前：
1. 读取 `baseline/` 中最新快照
2. 对比当前代码结构与 ownership mapping
3. 对比当前契约与 contract inventory
4. 检查 known anti-patterns 是否出现新实例
5. 报告：aligned / minor drift (self-correctable) / material drift (needs review)

---

## 17. 架构回望 → Reflection Risk/Unknown 映射

7 维度检查结果到 Reflection checklist 的显式映射：

| 架构维度 | Reflection 字段 | 映射规则 |
|----------|----------------|---------|
| Ownership integrity | Risk/Unknown | 新重复 owner → 记录为 Risk |
| Module boundaries | Risk/Unknown | 边界侵蚀 → 记录为 Risk |
| Contract changes | Evidence | 契约变更 → 作为 Evidence 引用 |
| Cascade proliferation | Risk/Unknown | 超出预期的波及 → 记录为 Unknown |
| Dependency direction | Risk/Unknown | 循环/反向 → 记录为 Risk |
| Retirement completeness | Risk/Unknown | 未退役 → 记录为 Risk，标注排期 |
| Entropy flow | DeeperCause | 熵增 → 检查是否存在未分析的深层诱因 |

此映射确保架构回望的发现不会在 Reflection 阶段被遗漏。
