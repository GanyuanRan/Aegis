# ADR-0003 当前分支优先的任务级 Git 生命周期

状态：`Approved`

## 设计证据

- `skills/using-git-worktrees/SKILL.md` 当前把隔离工作区作为功能开发的默认起点，
  但没有把“是否确实需要并发 checkout”作为创建门槛。
- `skills/subagent-driven-development/SKILL.md` 当前把 worktree 设为执行计划的
  必需前置条件，即使多个 coding agent 处理的是同一任务。
- `skills/writing-plans/SKILL.md` 当前同时要求 dedicated worktree、frequent commits
  和细粒度步骤，容易把步骤边界误当成 Git 历史边界。
- `skills/finishing-a-development-branch/SKILL.md` 当前同时承担集成选择、branch
  清理和 worktree 清理，但创建侧没有与之对称的生命周期所有权。
- 产品 owner 已确认 current-branch-first、verified task commit、exception-only
  worktree 和 creator-owned cleanup 是 coding agent 的目标体验；随后反例审查要求
  补齐任务开始快照、单一 Git 写入 owner、失败恢复和跨 merge 策略的清理证据。

这些规则继承了保守隔离策略，却没有形成完整的创建、使用、提交、合并与回收闭环。
在 coding agent 持续执行真实任务后，结果可能是 branch 和 worktree 数量不断增长，
后续 agent 难以判断归属、合并状态与安全删除边界。

## 背景

Aegis 只服务于 AI coding agent 场景。对这类任务，Git 的首要价值是形成可验证、
可追溯、可回滚的任务历史；branch 用于让两条历史独立演进，worktree 用于同时
checkout 多条历史。三者不是同一层面的安全措施。

当前默认规则把“任务需要修改代码”近似等同于“需要新 branch 和 worktree”。
这种做法降低了单次任务覆盖当前工作区的风险，却把风险转移为长期资源熵：

- 连续任务不断产生临时 branch 和 worktree；
- 同一任务的 subagent 被误认为需要文件系统级隔离；
- PR 已创建或任务已提交后，worktree 仍被长期保留；
- 清理依赖下一位 agent 猜测资源归属；
- 为保持工作区干净而产生的隔离实体，最终反而让仓库状态更难理解。

因此需要把默认安全机制从“先隔离”改为“先形成可靠任务提交”，并只在历史真正
分叉或 checkout 真正并发时增加 Git 实体。

## 决策

采用以下总原则：

> 修改任务当前分支优先；验证完成即按任务提交；历史分叉才建 branch；并发
> checkout 才建 worktree；创建者负责回收。

### 0. 任务开始快照

任何修改型任务在第一次写入前，都必须建立只读 `TaskStartSnapshot`：

- repository root、当前 `HEAD`、当前 branch 或 detached 状态；
- upstream 与已知 ahead/behind 状态；
- staged、unstaged 与 untracked 路径；
- 正在进行的 merge、rebase、cherry-pick、revert 或 bisect；
- 当前 `git worktree list --porcelain` 结果；
- 本任务预计拥有的文件与明确不属于本任务的已有状态。

快照保存在当前任务状态或既有 handoff/checkpoint 中，不创建新的 repo artifact、
daemon 或 registry。后续 `task-owned diff` 是相对于该快照形成的任务增量，不得靠
任务结束时猜测。

状态分类规则：

- detached HEAD、冲突或未结束的 Git operation：普通修改任务停止，先报告恢复边界；
- 不重叠且能够保持 index 原样的用户本地状态：允许留在当前工作区继续；
- 与任务文件重叠、归属不明或无法安全隔离 staging 的 tracked 状态：不得猜测，
  视为另一未完成目标并进入 branch/worktree 例外，或在没有确定安全路径时询问用户；
- 不自动 stash、reset、clean 或提交用户已有状态。

### 1. 当前分支优先

普通 coding task 默认在当前 branch 和当前工作区完成。仅仅“会修改文件”、
“任务复杂”、“使用计划”、“启用 TDD”或“使用 subagent”都不是新建 branch
或 worktree 的充分理由。

当前 branch 名为 `main` 或 `master` 本身也不是新建 branch 的理由。只有更高
优先级的仓库 authority、保护策略或用户指令才覆盖当前分支优先。

只有满足以下任一条件时才新建 branch：

- 用户明确要求 branch 或 PR 流程；
- 仓库 current authority 或受保护分支策略要求独立历史；
- 两个方案、目标或交付线需要独立演进、独立审查或独立回滚；
- 当前 branch 已承载另一个尚未结束的目标，不能安全接纳新任务历史。

新建 branch 不自动意味着新建 worktree。工作区可以安全切换时，直接在当前
工作区 checkout 该 branch；已有 branch 或 PR 已承载同一目标时优先复用。

### 2. 任务级验证提交

Git 提交边界跟随可理解、可验证、可回滚的任务边界，而不是工具调用次数或几分钟
一个的微步骤：

- 普通小任务在任务完成并验证后形成一个提交；
- 有书面计划的任务按 coherent Task 提交，不按每个 Step 提交；
- 长任务按能够独立验证和回滚的 coherent slice 提交；
- 同一 slice 的实现、测试与必要文档进入同一个提交；
- 只有显式的中断或交接需要时，才允许标明为 WIP 的 checkpoint commit。

修改型任务满足提交前置条件后，默认创建本地 commit。用户或仓库 authority 可以
明确要求 `no commit`。只读、无改动或验证未通过的任务不得创建空提交或正常完成
提交。

同一任务只有协调 agent 是 Git mutation owner，负责 stage、commit、branch 和
worktree 操作。实现与 review subagent 默认只编辑、验证并报告；除非协调权被明确
完整转移且没有其他 writer，否则 subagent 不得自行 commit 或改变 Git 生命周期。

自动本地提交必须同时满足：

1. `TaskStartSnapshot` 已建立，当前任务范围和 task-owned 文件可明确识别；
2. 已审查实际 diff，没有混入无关用户改动、secret、临时文件或生成噪音；
3. 已完成与风险匹配的 fresh verification；
4. 验证通过，或用户明确授权创建 WIP checkpoint；
5. staged 内容能够由单一、准确的 commit message 描述。

存在任务前已有 staged 内容时，提交路径必须保持原 index 语义不变；当前宿主无法
可靠做到时，不自动 commit。禁止用 `git add .`、`git add -A` 或等价宽泛 staging
替代 task ownership 判断。

“任务完成后工作区干净”是 task-scoped 语义：当前任务不再留下未提交 diff。
它不要求删除、暂存或提交用户原有的本地改动与未跟踪文件。

提交后必须 read back 新 `HEAD`、提交文件列表和剩余 task delta。commit hook、签名
或其他提交步骤失败时，不使用 `--no-verify` 绕过，不清理 worktree，也不宣称
task-clean；保留现场并报告恢复入口。

本决策不自动授权 amend、rebase、reset、pull、stash、force 操作、push、PR、
merge、tag、release 或远端 branch 删除。这些动作仍由用户当前指令和仓库
authority 控制。

修改任务的最终回执保持紧凑，但必须说明：当前 branch、commit SHA/message 或未
提交原因、`Task clean`、`Repository clean`、本任务创建/移除/保留的 branch 与
worktree，以及保留原因。`Task clean: yes` 不得被表述为整个仓库无本地状态。

### 3. Worktree 仅用于并发 checkout

除用户明确要求 worktree 或仓库 authority 要求隔离外，Aegis 仅在以下情况自动
创建 worktree：

- 当前工作区存在不属于本任务、又不能安全保留或切换的未完成改动，而任务必须在
  另一条历史上继续；
- 用户明确授权两个真实独立任务或方案并行推进，需要同时 checkout 不同 branch。

以下情况不得单独触发 worktree：

- 任务修改多个文件或跨模块；
- 任务采用 TDD、计划或分阶段验证；
- 多个 subagent 为同一目标协作；
- 只是希望“更安全”或“保持主工作区干净”；
- branch 已存在但并不需要同时 checkout。

同一任务的 coding subagent 默认共享一个工作区，并通过任务所有权、顺序实现、
scoped staging 和 review 控制冲突；不得为每个 subagent 创建 worktree。只读分析
可以并行，但写入同一任务工作区的实现必须保持明确的文件所有权和提交边界。

默认每个仓库最多保留一个由 Aegis 当前任务创建的临时 worktree。额外并发
worktree 需要用户明确授权。已经位于合适 worktree 时必须复用，不得嵌套创建。

worktree 位置优先使用仓库已约定且确认 ignored 的目录；没有约定时使用仓库外的
用户级临时位置。不得仅为创建 worktree 修改并提交项目 `.gitignore`。创建过程只
执行与当前项目 authority 和任务相关的最小 setup/verification，不盲目安装依赖或
运行全量命令。

### 4. 创建者负责回收

Aegis 创建的临时 Git 资源必须在同一生命周期内被处置：

- task-owned diff 已验证并提交后，临时 worktree 可以移除，branch 继续保留；
- PR 处于 open 状态只要求 branch 存在，不要求永久保留 worktree；需要修改时可
  再次 checkout 或重新创建 worktree；
- merge/fast-forward 后，可用目标 branch 的 ancestor evidence 证明集成；
- squash/rebase merge 后，使用可信 PR merged 状态与 branch/head identity，或
  等价 patch evidence 证明集成；不能证明时保留 branch；
- 只有集成状态与资源归属都得到 fresh evidence 时，才删除 Aegis 创建的本地 branch；
- 远端 branch 删除继续遵循用户授权和仓库策略；
- dirty、含 untracked 工作成果、未提交、detached、未合并、用户创建或归属不明的
  worktree/branch 一律不自动删除，只报告状态和安全的下一步。

资源归属以当前任务的直接创建记录和 Git 只读证据为准。Aegis 不新增 daemon、
全局 registry 或常驻调度器。跨会话无法证明归属的旧资源只能进入只读审计，不能
猜测后自动清理。

worktree 清理采用两阶段 readback：先执行 Git-level remove，再回读
`git worktree list --porcelain`。若 Git 已注销但 Windows 或文件锁导致目录残留，
只有在路径精确、资源归属明确且没有用户成果时才清理该残留目录；否则报告保留。
不得对归属不明资源执行全局 `git worktree prune`、`--force` 或宽泛目录删除。

## 备选方案

### 方案 A：所有修改任务都创建 branch 和 worktree

优点：每个任务获得最强文件系统隔离，当前 checkout 不易被直接影响。

缺点：把隔离实体数量与任务数量绑定；创建容易、回收不稳定；长期使用后需要
coding agent 推断大量历史资源的归属，整体风险高于单次隔离收益。

### 方案 B：所有修改任务创建 branch，但只在并发时创建 worktree

优点：避免 worktree 爆炸，同时每个任务仍有独立 branch。

缺点：普通顺序任务仍产生大量无必要 branch；任务提交本身已经提供回滚边界时，
额外 branch 不增加等量价值。

### 方案 C：当前分支优先，验证后按任务提交，历史分叉时建 branch，并发 checkout 时建 worktree

优点：Git 实体与真实需求一一对应；连续任务自然保持 task-clean；branch 和
worktree 的创建、存续与回收条件清晰；适合 coding agent 的顺序执行现实。

缺点：要求 agent 能准确识别 task-owned diff、执行 scoped staging，并在提交前做
fresh verification；仓库若要求 PR，仍必须尊重其 branch 策略。

选择方案 C。

### 方案 D：用 daemon 或全局 registry 自动管理所有 worktree

优点：可以记录跨会话资源归属并执行定时回收。

缺点：为方法包引入新的状态 owner、常驻生命周期和失败模式，越过当前
`Aegis Method Pack` 的最小必要边界；不能解决“为什么默认创建过多”的根因。

不采用该方案。

## 后果

正面影响：

- 顺序完成普通任务时，不再随任务数量增长 branch 或 worktree；
- 验证提交成为主要恢复点，代码历史更易追溯和回滚；
- worktree 的含义收敛为“同时 checkout”，不再是复杂任务的仪式；
- 同一任务的 subagent 协作不再制造额外仓库实体；
- PR、branch 与 worktree 生命周期解耦，review 期间可释放本地 checkout；
- 清理只作用于可证明由 Aegis 创建且满足安全条件的资源。

负面影响与成本：

- 自动 commit 前必须可靠执行 diff ownership、scoped staging 与验证检查；
- 每个修改任务增加一次轻量 task-start/readback 成本；
- 未提交的用户改动与新任务冲突时，仍可能需要一个临时 worktree；
- 团队或托管平台要求 branch/PR 时，当前分支优先必须让位于更高 authority；
- 旧版 Aegis 遗留的 worktree 无法全部自动判定归属，需要一次只读审计和人工确认。

## Compatibility Boundary

- 保留用户显式要求 worktree、branch 或 PR 的能力；
- 保留 `using-git-worktrees` 和 `finishing-a-development-branch` 的公开 skill
  identity，修改其触发与生命周期契约，不创建重复 owner；
- 保留仓库保护规则、host 权限模型与用户授权边界；
- 保留用户按任务或项目规则关闭自动本地 commit 的能力；
- 不把 local commit 成功包装成 completion authority；完成声明仍需要
  `verification-before-completion` 的 fresh evidence；
- 不要求宿主提供付费并发 agent 能力；没有并发能力时自然退化为当前工作区顺序执行。

## Retirement Impact

采用本决策时，修复轨与退役轨必须同时落地。

修复轨：

- `docs/current/AEGIS_PROCESS_BASELINE.md` 是 task-level Git lifecycle 的
  canonical method owner；各执行 skill 只投影自己阶段的职责；
- `using-git-worktrees` 负责 worktree 必要性判断、安全创建和归属明确时的审计提示；
- `finishing-a-development-branch` 负责正确的集成选择、worktree 先行释放与 branch
  后续清理顺序；
- `writing-plans` 负责 coherent Task/slice 的提交边界，不再把微步骤等同于提交；
- 修改型执行 workflow 负责第一次写入前建立 `TaskStartSnapshot`；
- `subagent-driven-development` 负责同任务共享工作区和协调 agent 单一 Git owner；
- `verification-before-completion` 负责提交前 evidence/readback 和最终 Git 回执，但
  不授予提交或集成权限；
- host mapping 与测试覆盖环境检测、创建门槛、提交前置条件、失败状态和安全清理。

退役轨：

- 删除“功能开发默认需要 worktree”的要求；
- 删除“执行计划或使用 subagent 必须先建 worktree”的要求；
- 删除“每个 2–5 分钟 Step 都应形成 commit”的暗示；
- 删除“实现 subagent 默认自行 commit”的要求；
- 删除“仅为 worktree 自动修改 `.gitignore` 并提交”的要求；
- 删除隐式 pull/stash、宽泛 staging 和无证据强制清理路径；
- 修复 branch 删除早于 worktree 释放、以及用当前 branch 名判断当前 worktree 的错误；
- 不新增第二套 Git lifecycle skill、兼容 fallback、registry 或后台清理 owner。

## Baseline Sync

本 ADR 已经产品 owner 审阅并转为 `Approved`。当前决策同步到：

- `docs/current/AEGIS_PROCESS_BASELINE.md`：任务级 commit、branch 与 worktree 的
  canonical lifecycle；
- `docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md`：fast-path cheapness、资源熵和
  completion cleanup 质量要求；
- `docs/current/README.md`：将本 ADR 纳入 public current authority map。

若实现发现其他 current docs 对普通任务仍承诺默认 worktree，只修改最小的真实
owner，并在验证中证明无互相冲突的 current guidance。

本次 baseline sync 记录的是已经批准的 method policy，不伪造 skill 投影已完成。
与本 ADR 冲突的继承 skill 文本从此属于 `Implementation Drift`，必须在后续实现
切片中收敛后才能声称 lifecycle implementation 完成。

## 反例审查

| 场景 | 预期行为 |
|---|---|
| clean `main` 上的普通修改 | 当前分支完成，验证后一个 task commit；不创建 branch/worktree |
| 工作区只有不重叠的用户本地配置 | 保留原状态，scoped commit；回执显示 `Task clean: yes`、`Repository clean: no` |
| 已有 tracked 改动与任务重叠或归属不明 | 不猜测、不 stash；隔离到 branch/worktree，或没有确定路径时询问 |
| 同任务多个 subagent | 共享工作区；协调 agent 是唯一 Git mutation owner |
| detached HEAD、冲突、未结束的 Git operation | 停止普通修改，保留现场并报告恢复边界 |
| verification 或 commit hook/签名失败 | 不创建正常提交、不清理、不宣称 task-clean |
| PR 采用 squash/rebase merge | 用 PR/patch evidence 判断集成，不错误要求旧 SHA 必须是 ancestor |
| Windows 中 Git 已注销但目录删除失败 | 回读 worktree 列表后只处理归属明确的精确残留路径 |

## 验收与验证边界

实现后至少需要以下确定性证据：

- 连续执行普通顺序任务不会创建新 branch 或 worktree；
- 第一次写入前生成 `TaskStartSnapshot`，并能区分任务增量与已有用户状态；
- 小任务只在 fresh verification 通过后形成一个 coherent commit；
- `main`/`master` 名称本身不会触发新 branch；
- scoped staging 不会提交任务开始前已存在的用户改动或未跟踪文件；
- read-only/no-change/no-commit/verification-failed 情况不会创建空提交或正常完成提交；
- 计划按 Task/slice 而不是按微步骤提交；
- 同一任务的 subagent 共享工作区、不创建 per-subagent worktree，且只有协调 agent
  执行 Git mutation；
- 不相关 dirty 状态阻止安全切换时，最多创建一个归属明确的临时 worktree；
- task-owned diff 提交后可移除临时 worktree，同时保留尚未合并的 branch；
- open PR 不要求 worktree 常驻；
- merge/fast-forward 与 squash/rebase 分别使用适合的集成证据清理本地 branch；
- dirty、untracked、detached、未合并或归属不明资源只报告、不删除；
- worktree 创建不会仅为隔离而修改 `.gitignore`，清理失败会执行 Git/path 两阶段 readback；
- 最终 Git 回执准确区分 task-clean 与 repository-clean；
- 所有支持宿主的安装与 skill contract 测试保持通过，环境受限的 live check 明确
  报告为 unknown，不伪造覆盖。

本 ADR 不授予 authoritative `GateDecision`、`PolicySnapshot`、evidence
sufficiency 或 final completion authority。

## 重审触发条件

出现以下任一情况时重审本决策：

- 真实使用证据表明 current-branch-first 导致无法接受的误提交或历史污染；
- Git 或主要 coding-agent host 提供可靠的原生临时 workspace 生命周期 owner；
- Aegis 演进出独立 runtime core，能够安全持有跨会话资源归属与回收状态；
- 支持仓库普遍采用强制 branch/PR 策略，使当前分支优先不再是有效默认。
