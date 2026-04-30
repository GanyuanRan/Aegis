# Aegis Phase 4 Compatibility Review Atomic Plan

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis` 当前下一实施切片的原子级任务清单。

本文档只负责回答以下问题：

- `Phase 4 / Compatibility Review` 具体先核哪些兼容性 owner
- 如何系统盘点 `superpowers` 原有高价值能力是否仍在
- 如何检查 Codex / OpenCode / 分发脚本是否出现 host-specific 反向污染 baseline
- 如何在不进入 future runtime core 的前提下，完成当前阶段的兼容性回看

本文档不负责回答以下问题：

- future runtime core 的实现细节
- `Phase 5` 及之后的完整执行方案
- 新宿主适配器的正式开发
- 当前范围之外的 skill 全量重写

---

## 2. 当前结论

当前仓库已经完成：

- `Phase 1：Authority Completion`
- `Phase 2：Skill Upgrade Wave 1`
- `Phase 3：Skill Upgrade Wave 2`

当前仓库下一步只做：

- `Phase 4：Compatibility Review`

当前 `Phase 4` 只允许覆盖以下三类兼容性 owner 与其最小必要 supporting docs：

1. Codex 安装 / smoke / plugin sync 相关 owner
2. OpenCode 安装 / plugin loading / integration smoke 相关 owner
3. 当前 authority / testing supporting docs 中与兼容性回看直接相关的最小部分

除非有证据证明现有结构已阻断 `Phase 4` 落地，否则本切片不扩展到：

- future runtime core
- host adapter 正式实现
- 新宿主接入
- 未被兼容性回看直接阻断的 skill 本文重写

---

## 3. Phase 4 交付目标

Phase 4 完成时，必须同时满足以下目标：

1. `Aegis` 当前保留的 `superpowers` 原有高价值兼容性能力已形成 inventory
2. Codex 安装说明、最小 smoke、plugin sync 分发链已重新按当前 baseline 回看
3. OpenCode 安装说明、plugin loading、integration smoke 入口已重新按当前 baseline 回看
4. 已明确哪些兼容性链路只是 smoke 级证据，哪些仍缺更深层验证
5. 已盘点并标注所有 host-specific 特例、历史补丁、兼容分支的去留状态
6. `plugin-installable` 相关路径未因当前改造而被单宿主逻辑反向污染
7. 当前阶段收口后，能够为 `Phase 5` 提供一份更干净的 compatibility verdict，而不是零散结论

---

## 4. 文件责任图

### 4.1 Compatibility Canonical Owners

- `docs/README.codex.md`
  - Codex 安装、更新、卸载与故障排查说明 owner
- `docs/README.opencode.md`
  - OpenCode 安装、更新、工具映射与故障排查说明 owner
- `tests/opencode/run-tests.sh`
  - OpenCode plugin compatibility 回归总入口
- `tests/opencode/test-plugin-loading.sh`
  - OpenCode plugin structure / bootstrap / syntax 最小校验 owner
- `tests/opencode/test-tools.sh`
  - OpenCode `find_skills` / `use_skill` 集成校验 owner
- `tests/opencode/test-priority.sh`
  - OpenCode project / personal / superpowers priority 语义校验 owner
- `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
  - Codex plugin 同步与分发脚本回归 owner
- `scripts/sync-to-codex-plugin.sh`
  - Codex plugin sync canonical script owner

### 4.2 Supporting Authority / Testing Owners

- `docs/testing.md`
  - 当前测试矩阵与宿主验证说明
- `docs/current/README.md`
  - authority map 与当前阶段文档组织
- `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
  - 当前阶段状态与实施顺序
- `AGENTS.md`
  - fork 内当前阶段 guardrails

---

## 5. 原子实施切片

### Slice 1：Compatibility Inventory 与 baseline readback

**目标：**

- 先把当前需要保住的兼容性能力盘点成明确 inventory，而不是边跑边猜

**涉及文件：**

- 回读：`docs/current/AEGIS_TARGET_STATE.md`
- 回读：`docs/current/AEGIS_PRODUCT_REQUIREMENTS.md`
- 回读：`docs/current/AEGIS_PRODUCT_BASELINE.md`
- 回读：`docs/current/AEGIS_PHASE2_WAVE1_COMPLETION_RECORD.md`
- 回读：`docs/current/AEGIS_PHASE3_WAVE2_COMPLETION_RECORD.md`
- 视需要修改：`docs/current/AEGIS_TARGET_STATE.md`
- 视需要修改：`docs/current/AEGIS_PRODUCT_REQUIREMENTS.md`

**修复轨：**

1. 真实根因
   - 目前兼容性结论分散在 Wave 1 / Wave 2 completion record、宿主说明与测试脚本中，尚未被显式盘点为当前阶段 inventory。
2. 唯一 canonical owner
   - 当前阶段 inventory 结论本身
3. 最小必要改动
   - 先只做回读与 inventory 盘点；只有发现 baseline 文档中的兼容性要求不一致时，才窄改 baseline。
4. 兼容边界
   - 不得在盘点阶段引入新宿主、新工具或新运行时承诺。
5. 验证方式
   - 人工回读确认 inventory 至少覆盖：安装、skill discovery、priority、tool mapping、distribution sync、plugin-installable。

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 分散在 completion record、README、tests 注释中的零散兼容性描述。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 作为当前真实状态的分布式证据输入。
4. 删除触发条件
   - 当 `Phase 4` 形成统一 inventory 与 verdict 文档后。
5. 删除前验证清单
   - 不得丢失任何当前宿主能力结论来源。

---

### Slice 2：Codex compatibility 回看

**目标：**

- 重新核对 Codex 安装分发说明、最小 smoke、plugin sync 脚本是否仍与当前 baseline 一致

**涉及文件：**

- 回读 / 视需要修改：`docs/README.codex.md`
- 回读 / 视需要修改：`docs/testing.md`
- 回读 / 视需要修改：`tests/skill-triggering/run-all.sh`
- 回读 / 视需要修改：`tests/explicit-skill-requests/run-all.sh`
- 回读 / 视需要修改：`tests/helpers/codex-cli.sh`
- 回读 / 视需要修改：`scripts/sync-to-codex-plugin.sh`
- 回读 / 视需要修改：`tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`

**修复轨：**

1. 真实根因
   - Wave 1 / Wave 2 已证明 Codex 侧 smoke 与 plugin sync 可通过，但还没有一次以“Compatibility Review”为目标的系统性复盘。
2. 唯一 canonical owner
   - `docs/README.codex.md`
   - `scripts/sync-to-codex-plugin.sh`
   - `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
3. 最小必要改动
   - 默认先只跑回读与回归；仅在 README、helper、sync script 与测试结论发生证据化冲突时才窄改对应 owner。
4. 兼容边界
   - 不得为了某条 Codex 路径更顺手而破坏 cross-host plugin-installable 模型。
5. 验证方式
   - `bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh'`
   - `bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh'`
   - `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 任何仅服务某次 smoke 或旧安装方式、但已与当前 baseline 不符的 Codex 特例说明、helper 分支或 sync 文案。
2. 是否仍在主链生效
   - 需视实际回读结果而定。
3. 保留它的唯一理由
   - 仅保留跨宿主分发所必需的兼容最小面。
4. 删除触发条件
   - 当前 baseline 已有统一表述或统一脚本路径时。
5. 删除前验证清单
   - Codex smoke 与 plugin sync regression fresh pass。

---

### Slice 3：OpenCode compatibility 回看

**目标：**

- 重新核对 OpenCode 安装说明、plugin loading、tools / priority integration 入口是否仍与当前 baseline 一致

**涉及文件：**

- 回读 / 视需要修改：`docs/README.opencode.md`
- 回读 / 视需要修改：`docs/testing.md`
- 回读 / 视需要修改：`tests/opencode/run-tests.sh`
- 回读 / 视需要修改：`tests/opencode/test-plugin-loading.sh`
- 回读 / 视需要修改：`tests/opencode/test-tools.sh`
- 回读 / 视需要修改：`tests/opencode/test-priority.sh`
- 回读 / 视需要修改：`tests/opencode/setup.sh`

**修复轨：**

1. 真实根因
   - 当前只确认过 OpenCode plugin loading regression fresh pass，而 integration tests 多数仍属于条件性入口，尚未以 compatibility owner 视角统一盘点。
2. 唯一 canonical owner
   - `docs/README.opencode.md`
   - `tests/opencode/run-tests.sh`
3. 最小必要改动
   - 默认只核现有 tests / docs / setup 之间的一致性；只在证据证明三者矛盾时窄改对应 owner。
4. 兼容边界
   - 不得为了 OpenCode 集成便利去削弱宿主无关的 method-pack 边界。
5. 验证方式
   - `bash tests/opencode/run-tests.sh`
   - 如本机具备 OpenCode，则再跑：
     - `bash tests/opencode/run-tests.sh --integration`

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - 任何只为旧 symlink 迁移、旧工具命名或单次调试保留的 OpenCode 文案 / setup 特例。
2. 是否仍在主链生效
   - 需视实际回读结果而定。
3. 保留它的唯一理由
   - 仅保留 OpenCode 当前正式安装与技能发现所必需的最小兼容说明。
4. 删除触发条件
   - 当前 README、setup 与 tests 可以由统一逻辑覆盖时。
5. 删除前验证清单
   - plugin loading regression fresh pass
   - integration tests 若环境允许则 fresh pass，若不允许则阻断点明确记录

---

### Slice 4：Authority / docs / test matrix 收口

**目标：**

- 把本轮兼容性回看得到的结论，回写进 authority docs 与 testing docs，避免结论继续漂在 completion record 或 shell 输出里

**涉及文件：**

- 修改：`docs/testing.md`
- 视需要修改：
  - `docs/current/README.md`
  - `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
  - `AGENTS.md`
  - `docs/current/AEGIS_TARGET_STATE.md`
  - `docs/current/AEGIS_PRODUCT_REQUIREMENTS.md`

**修复轨：**

1. 真实根因
   - 如果兼容性 verdict 只留在 shell 结果和阶段记录里，后续会再次出现 authority drift。
2. 唯一 canonical owner
   - `docs/testing.md`
   - 当前 active authority docs
3. 最小必要改动
   - 只把已经有证据支撑的兼容性结论回写到对应 owner 文档。
4. 兼容边界
   - 不得把 completion record 中的临时观察上升成未获证据支持的长期 baseline。
5. 验证方式
   - 回读所有被改文档，确认它们之间没有对同一宿主能力给出冲突结论。

**退役轨：**

1. 当前重复 owner / 旧 fallback / 历史补丁在哪里
   - completion record、测试脚本注释、README 之间可能重复叙述同一兼容性事实。
2. 是否仍在主链生效
   - 是。
3. 保留它的唯一理由
   - 只保留“哪个文档负责什么”的最小分工。
4. 删除触发条件
   - authority docs 中已有统一且无冲突的最终表述时。
5. 删除前验证清单
   - 回读确认每类结论有且只有一个 canonical owner。

---

## 6. 最低验证矩阵

Phase 4 结束前，至少要 fresh 运行：

```bash
bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh'
bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh'
bash tests/opencode/run-tests.sh
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

若当前环境具备 OpenCode，可追加：

```bash
bash tests/opencode/run-tests.sh --integration
```

若只做中间切片验证，则至少跑：

- 当前切片相关 README / script / test owner 回读
- 当前切片的目标验证命令
- 修复轨回望
- 退役轨回望

---

## 7. 完成判据

只有同时满足以下条件，`Phase 4` 才算完成：

1. Codex 安装 / smoke / plugin sync 三层结论已统一
2. OpenCode 安装 / plugin loading / integration 入口结论已统一
3. 至少完成一轮 fresh host-native compatibility matrix
4. 若 integration tests 未跑，阻断点与影响面已显式记录
5. 当前 authority docs 与 testing docs 不再对兼容性状态给出冲突表述
6. 没有为了兼容性回看而越权进入 runtime core 或新宿主开发

---

## 8. 当前建议的实施顺序

1. 先做 Slice 1：盘清 inventory 与 baseline 结论
2. 再做 Slice 2：Codex compatibility 回看
3. 再做 Slice 3：OpenCode compatibility 回看
4. 最后做 Slice 4：authority / docs / matrix 收口

理由：

- 先盘点再验证，能避免把 compatibility review 做成零散修补
- 先 Codex 后 OpenCode，符合当前已有 smoke / plugin sync 证据最完整的顺序
- 最后再改 authority docs，可以保证写进去的是 fresh verdict，而不是猜测
