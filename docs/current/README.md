# Aegis Current Authority Map

状态：`Approved`

## 1. 文档定位

本文档定义当前 `Aegis` 仓库的 authority order、文档状态解释与最小基线集合。

本文档只负责回答以下问题：

- 当前仓库哪些文档是 authoritative baseline
- 文档冲突时按什么顺序裁决
- 哪些材料只是迁移输入，不应继续被当作当前权威
- 当前仓库的基线体系最少由哪些文档组成

本文档不负责回答以下问题：

- `Aegis` 的具体技能内容如何实现
- `Aegis Runtime Core` 的节点级运行时契约细节
- 某个宿主的安装或兼容性说明

---

## 2. 当前仓库定位

当前仓库的正式定位为：

> `Aegis Method Pack (runtime-ready)`

也就是说：

- 当前仓库负责方法层、技能分发层、宿主说明层与治理投影层
- 当前仓库不承担 authoritative runtime core
- 当前仓库可以产出 runtime-ready artifacts 与 contracts
- 当前仓库不能独立授予 `completion authority`

---

## 2.1 当前执行状态

截至 `2026-04-28`，当前仓库的阶段状态为：

> `Phase 5 / Runtime-ready Hardening completed within current method-pack scope`

当前已完成并有 fresh verification 支撑的阶段收口包括：

- `Phase 2 / Wave 1`
- `Phase 3 / Wave 2`
- `Phase 4 / Compatibility Review`

当前最新已完成切片为：

> `Phase 5 overall closeout completed within current method-pack scope`

继续判断是否进入下一阶段或 production strengthening work 前，仍应先回读以下材料：

1. `docs/current/AEGIS_TARGET_STATE.md`
2. `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
3. `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`
4. `docs/current/AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md`
5. `docs/current/AEGIS_PHASE5_E2E_BASELINE_RUN.md`
6. `docs/current/AEGIS_PHASE5_E2E_COMPLETION_RECORD.md`
7. `docs/current/AEGIS_PHASE5_COMPLETION_RECORD.md`
8. `docs/current/AEGIS_METHOD_PACK_STRENGTHENING_ATOMIC_PLAN.md`
9. `docs/current/AEGIS_METHOD_PACK_STRENGTHENING_COMPLETION_RECORD.md`
10. `docs/current/AEGIS_PRODUCTION_READINESS_GAPS.md`

如果后续开发与以上阶段状态冲突，以 completion record 中已验证的事实和当前 approved baseline 为准，不以会话记忆或零散 shell 输出为准。

---

## 3. Authority Order

除非后续有更新且已批准的文档明确替代，当前 authority order 固定如下：

1. `docs/current/README.md`
2. 相关 `Approved` ADR，位于 `docs/adr/`
3. 相关 `Approved` current baseline 文档，位于 `docs/current/`
4. 宿主安装与测试文档，例如 `docs/README.codex.md`、`docs/README.opencode.md`、`docs/testing.md`
5. 迁移输入材料与草稿，包括：
   - 根目录 `AGENTS_RULES.md`
   - `Aegis_Fork_Bootstrap_Pack/`
   - 旧 `docs/plans/` 下的历史设计文档
   - 已从用户可见仓库内容中移除的 upstream-specific 历史设计文档

解释规则：

- `docs/current/README.md` 负责定义当前 authority map，本身优先级最高。
- ADR 用于钉死结构性决策；当 ADR 与一般说明性文字冲突时，以 ADR 为准。
- `docs/current/` 下的文档定义当前仓库的 active baseline。
- 根目录 `AGENTS_RULES.md` 当前仍可视为 process mother draft，但不是当前仓库的最终 authority target。
- `Aegis_Fork_Bootstrap_Pack/` 是高价值迁移输入，但不是当前仓库的永久 source of truth。

---

## 4. Current Authoritative Documents

当前最小 authoritative document set 为：

- `docs/current/README.md`
- `docs/current/AEGIS_TARGET_STATE.md`
- `docs/current/AEGIS_TRANSFORMATION_ARCHITECTURE.md`
- `docs/current/AEGIS_PRODUCT_REQUIREMENTS.md`
- `docs/current/AEGIS_PRODUCT_BASELINE.md`
- `docs/current/AEGIS_PROCESS_BASELINE.md`
- `docs/current/AEGIS_ACTIVATION_MODE.md`
- `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md`
- `docs/current/AEGIS_RULE_LAYERING.md`
- `docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md`
- `docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
- `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
- `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
- `docs/current/AEGIS_PHASE2_WAVE1_ATOMIC_PLAN.md`
- `docs/current/AEGIS_PHASE3_WAVE2_ATOMIC_PLAN.md`
- `docs/current/AEGIS_PHASE4_COMPATIBILITY_REVIEW_ATOMIC_PLAN.md`
- `docs/current/AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md`
- `docs/current/AEGIS_METHOD_PACK_STRENGTHENING_ATOMIC_PLAN.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_METHOD_PACK_ROLLBACK_CHECKLIST.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
- `docs/current/AEGIS_FALLBACK_RETIREMENT_PREPARATION.md`
- `docs/current/AEGIS_OPEN_SOURCE_READINESS_GAPS.md`
- `docs/current/AEGIS_OPEN_SOURCE_RELEASE_PLAN.md`
- `docs/current/AEGIS_PRIVATE_RELEASE_SMOKE_TEST_PLAN.md`
- `docs/current/AEGIS_PRIVATE_RELEASE_SMOKE_TEST_RECORD.md`
- `docs/current/AEGIS_PUBLIC_REPO_FILE_DISPOSITION.md`
- `docs/current/AEGIS_PUBLIC_REPO_CUTOVER_CHECKLIST.md`
- `docs/current/AEGIS_PUBLIC_REPO_DELOCALIZATION_CHECKLIST.md`
- `docs/current/AEGIS_LOCAL_ONLY_OVERLAY_POLICY.md`
- `docs/current/AEGIS_HOST_INSTALL_CUTOVER_AUDIT.md`
- `docs/current/AEGIS_NAMESPACE_CUTOVER_PLAN.md`
- `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`

当前阶段收口记录包括：

- `docs/current/AEGIS_PHASE2_WAVE1_COMPLETION_RECORD.md`
- `docs/current/AEGIS_PHASE3_WAVE2_COMPLETION_RECORD.md`
- `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`
- `docs/current/AEGIS_PHASE5_E2E_COMPLETION_RECORD.md`
- `docs/current/AEGIS_PHASE5_COMPLETION_RECORD.md`
- `docs/current/AEGIS_METHOD_PACK_STRENGTHENING_COMPLETION_RECORD.md`

当前尚未进入 authoritative set 的内容包括：

- 任意未落盘的 IDE 草稿
- `docs/plans/` 下的实施计划
- 已从用户可见仓库内容中移除的 upstream-specific 旧 design/spec 文档
- `Aegis_Fork_Bootstrap_Pack/` 中尚未迁入当前体系的内容
- `docs/current/AEGIS_LONG_TASK_CONTINUATION_DESIGN.md`，当前为长任务协议 reviewed design input，尚未批准为 authoritative baseline

---

## 5. Scope Boundaries

`docs/current/AEGIS_PRODUCT_BASELINE.md` 负责：

- 当前仓库的产品定位
- 当前仓库承担什么，不承担什么
- 当前仓库与 upstream、未来 runtime core、未来 adapters 的关系

`docs/current/AEGIS_TARGET_STATE.md` 负责：

- 当前仓库目标状态的一页式摘要
- 整体 `Aegis` 长期目标形态的最小总览
- 当前阶段明确做什么与不做什么

`docs/current/AEGIS_PRODUCT_REQUIREMENTS.md` 负责：

- 本次改造的目标、非目标与成功标准
- 哪些 `superpowers` 能力必须保留
- plugin-installable 属性必须保留的产品要求

`docs/current/AEGIS_TRANSFORMATION_ARCHITECTURE.md` 负责：

- 当前整体改造的总设计
- 为什么当前阶段先收敛为 `Method Pack (runtime-ready)`
- TLREF 在整体改造中的系统位置
- 分阶段演进路径与当前刻意不做的事

`docs/current/AEGIS_RULE_LAYERING.md` 负责：

- method rules、host rules、repo rules 的分层边界

`docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md` 负责：

- 修复轨 + 退役轨双轨治理规则
- 当前切片在熵减方向上的最小交付约束

`docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md` 负责：

- runtime-ready artifacts 的最小 schema baseline
- artifact 的 method-pack / host / future-runtime owner 边界

`docs/current/AEGIS_PROCESS_BASELINE.md` 负责：

- `Aegis` 对外分发的方法层总流程
- TLREF / DIVE / Reflection / QA 的最小约束
- 输出契约与证据要求

`docs/current/AEGIS_ACTIVATION_MODE.md` 负责：

- `AEGIS_ACTIVATION_MODE=auto|explicit` 的模式语义
- 自动 bootstrap 注入与显式 skill 调用的边界
- method-pack、host profile 与 future runtime core 的 owner 切分

`docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md` 负责：

- 外部工具输出、日志、记忆与搜索结果如何进入 prompt
- raw evidence、summary、index 与 readback 的边界
- 在减少常驻上下文时如何保持 baseline-first 与 evidence-before-claims 能力

`docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md` 负责：

- 当前方法层可产出的 runtime-ready artifacts
- 方法层、宿主投影层与未来 runtime core 的边界
- 哪些能力只能留在未来 runtime core

`docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md` 负责：

- 整体改造的阶段化实施顺序
- 每一阶段的最低验证要求

`docs/current/AEGIS_PHASE2_WAVE1_ATOMIC_PLAN.md` 负责：

- 当前最近实施切片的原子级任务清单
- `Phase 2 / Wave 1` 的文件落点、最小改动边界与验证矩阵
- Wave 1 各切片的修复轨 + 退役轨收敛方式

`docs/current/AEGIS_PHASE3_WAVE2_ATOMIC_PLAN.md` 负责：

- 当前下一实施切片的原子级任务清单
- `Phase 3 / Wave 2` 的文件落点、最小改动边界与验证矩阵
- Wave 2 各切片的修复轨 + 退役轨收敛方式

`docs/current/AEGIS_PHASE4_COMPATIBILITY_REVIEW_ATOMIC_PLAN.md` 负责：

- 当前激活切片的原子级任务清单
- `Phase 4 / Compatibility Review` 的兼容性 owner、最小改动边界与验证矩阵
- Phase 4 各切片的修复轨 + 退役轨收敛方式

`docs/current/AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md` 负责：

- 当前激活切片的 E2E bootstrap 计划
- `tests/e2e/` 的最小 owner、bootstrap 边界与后续切片顺序
- Phase 5 中哪些验证能力已激活、哪些仍处于 planned 状态

`docs/current/AEGIS_METHOD_PACK_STRENGTHENING_ATOMIC_PLAN.md` 负责：

- Phase 5 收口之后、真实环境回归之前的 strengthening 切片边界
- release / rollback / compatibility / limitation owners 的最小落点
- 当前非 live strengthening work 的验证矩阵与收口标准

`docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md` 负责：

- method-pack release gate
- 最低 fresh verification
- 发布前必须回读的 owner 与 boundary checks

`docs/current/AEGIS_METHOD_PACK_ROLLBACK_CHECKLIST.md` 负责：

- method-pack rollback 触发条件
- rollback decision matrix
- rollback 后最小验证要求

`docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md` 负责：

- 当前有 fresh evidence 的宿主 verdict
- 当前未进入 release-level verdict 的宿主范围
- compatibility snapshot 的阅读顺序与边界

`docs/current/AEGIS_KNOWN_LIMITATIONS.md` 负责：

- 当前已知限制
- compatibility fallback 的保留原因与退役时机
- limitation 的统一阅读入口

`docs/current/AEGIS_FALLBACK_RETIREMENT_PREPARATION.md` 负责：

- 当前仍保留的 compatibility fallback 的后续退役准备入口
- 退役前最低验证与观察指标
- fallback retirement work 的当前阅读顺序

`docs/current/AEGIS_OPEN_SOURCE_READINESS_GAPS.md` 负责：

- 距离 method-pack 开源发布还差什么
- 哪些事项是开源前建议补齐的
- 哪些事项仍可后置到 production rollout 前

`docs/current/AEGIS_OPEN_SOURCE_RELEASE_PLAN.md` 负责：

- 当前 method-pack 的开源发布实施顺序
- 推荐的仓库策略
- 开源发布前每一步的 owner、验证与 stop condition

`docs/current/AEGIS_PRIVATE_RELEASE_SMOKE_TEST_PLAN.md` 负责：

- private `Aegis` release staging 仓的真实安装冒烟计划
- private-first gate 的最低验证范围与 stop condition
- public cutover 前必须完成哪些基础可用性验证

`docs/current/AEGIS_PRIVATE_RELEASE_SMOKE_TEST_RECORD.md` 负责：

- private smoke 的实际执行记录
- 真实安装与小型自举任务的 evidence
- 是否允许进入 public cutover 的输入材料

`docs/current/AEGIS_PUBLIC_REPO_FILE_DISPOSITION.md` 负责：

- 建立独立公开仓时的文件保留/迁移/归档规则
- 哪些内容应进入公开主仓
- 哪些内容只应保留在开发仓或 archive

`docs/current/AEGIS_PUBLIC_REPO_CUTOVER_CHECKLIST.md` 负责：

- 把当前开发仓整理进独立公开仓时的执行顺序
- 每一步的最低核对项与 stop condition
- cutover 执行层的动作 owner

`docs/current/AEGIS_PUBLIC_REPO_DELOCALIZATION_CHECKLIST.md` 负责：

- 进入公开仓前的去本机化审计规则
- 当前高优先级本机化对象
- 每类命中项的处理动作

`docs/current/AEGIS_LOCAL_ONLY_OVERLAY_POLICY.md` 负责：

- 当前仓对 local-only 内容的统一放置策略
- `.local/` overlay 的边界
- 如何同时满足本地持续开发与公开仓清洁

`docs/current/AEGIS_HOST_INSTALL_CUTOVER_AUDIT.md` 负责：

- host install docs、package manifests 与 plugin metadata 的 cutover 审计
- 哪些 upstream / `superpowers` 标识暂时保留
- 何时可以逐宿主切到 `Aegis` 公开仓语义

`docs/README.claude-code.md` 负责：

- Claude Code host 的安装入口说明
- private 仓阶段的 GitHub 鉴权前置检查
- Claude Code plugin skeleton 与 release-level fresh smoke verdict 的边界说明

`docs/current/AEGIS_NAMESPACE_CUTOVER_PLAN.md` 负责：

- 用户可见 namespace、display name 与 bootstrap skill 的 cutover 边界
- 哪些 active surfaces 必须切到 `aegis` / `Aegis`
- 哪些 `superpowers` 文本只作为 lineage、致谢、历史归档或临时 compatibility alias 保留

`docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md` 负责：

- 钉死“当前仓不是 runtime core”的正式决策
- 防止后续在单仓里重新揉回 authoritative core

---

## 6. Document Status Model

当前仓库统一使用以下状态语义：

- `Draft`
  - 可参考，但不具 authoritative effect
- `Reviewed`
  - 已完成结构与方向审阅，但尚未成为 active baseline
- `Approved`
  - 当前生效的基线文档
- `Superseded`
  - 曾生效，但已被更新文档替代
- `Deprecated`
  - 仅保留历史参考价值，不可再作为新决策基线

---

## 7. Migration Note

当前仓库的基线来源主要有两组：

1. `superpowers` 现有方法层与多宿主分发骨架
2. `AGENTS_RULES.md` 与 `Aegis_Fork_Bootstrap_Pack/` 中整理出的治理理念与 ADD 边界

迁移原则如下：

- 可以迁移原则、流程、输出契约与 artifact shapes
- 不可把 bootstrap pack 里的 runtime authority 直接假装为当前仓已具备的能力
- 不可把根部规则文档长期停留在“会话级”或“草稿级”，后续应继续迁入 `docs/current/`

---

## 8. Update Rule

当后续变更影响以下任一维度时，必须先更新当前 authority docs：

- 当前仓库的产品定位
- 方法层流程与输出契约
- 方法层与 runtime core 的边界
- 结构性 ADR
- 当前 active atomic plan

如果发现文档冲突：

1. 先按本文件定义的 authority order 裁决
2. 再修复优先级较低的文档，避免冲突持续存在
