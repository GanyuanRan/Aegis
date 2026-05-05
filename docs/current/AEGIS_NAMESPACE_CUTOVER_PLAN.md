# Aegis Namespace Cutover Plan

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis` 从 upstream `superpowers` 用户可见标识切换到 `Aegis` / `aegis` 的执行边界。

本文档回答以下问题：

1. 安装后宿主输出中应显示什么 namespace
2. 哪些 package / plugin / skill / hook / host install surface 必须切换
3. 哪些 `superpowers` 文本只作为 lineage、致谢或历史归档保留
4. 如何避免在改名过程中破坏 plugin-installable 能力

本文档不负责：

- 改写历史 release notes
- 删除 upstream 致谢
- 声明所有 marketplace 已完成上架
- 声明真实第二机器 private smoke 已完成

---

## 2. 目标状态

正式 `Aegis Method Pack` 安装后，用户可见主标识必须收敛为：

- package / plugin name：`aegis`
- display name：`Aegis`
- OpenCode plugin entry：`.opencode/plugins/aegis.js`
- Codex skill install namespace：`~/.agents/skills/aegis`
- OpenCode plugin install identifier：`aegis@git+<Aegis repo URL>`
- bootstrap skill：`using-aegis`
- agent-visible skill namespace examples：`aegis:<skill-name>`

允许保留 `superpowers` 的场景仅限：

1. upstream attribution / thanks
2. historical release notes or archived upstream plans
3. explicitly documented compatibility alias with a retirement trigger

`superpowers` 不应继续作为正式安装、正式插件名、正式 display name 或推理输出主前缀。

---

## 3. 当前真实问题

当前仓库仍有 active surfaces 使用 upstream 标识：

- `package.json`
- `gemini-extension.json`
- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `.cursor-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.opencode/plugins/superpowers.js`
- `hooks/session-start`
- `GEMINI.md`
- `.codex/INSTALL.md`
- `.opencode/INSTALL.md`
- `docs/README.codex.md`
- `docs/README.opencode.md`
- `skills/using-superpowers/`
- 多个 skill body 中的 `superpowers:<skill>` 示例

这会导致安装后宿主仍可能显示：

```text
Using superpowers:using-superpowers
Using superpowers:writing-plans
```

这与公开仓 `Aegis` 的目标状态冲突。

---

## 4. 执行顺序

### 4.1 Phase A：active install surfaces

必须优先切换：

1. package / plugin manifests
2. OpenCode runtime plugin entry
3. session-start hook bootstrap text
4. host install docs
5. `GEMINI.md` imports
6. OpenCode setup and plugin-loading tests

验证：

- `node --check .opencode/plugins/aegis.js`
- `bash tests/opencode/run-tests.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile none`

### 4.2 Phase B：bootstrap skill rename

目标：

- `skills/using-superpowers/` 收敛为 `skills/using-aegis/`
- frontmatter `name` 收敛为 `using-aegis`
- host bootstrap text 不再要求加载 `using-superpowers`

兼容边界：

- 不改变 “收到任务先检查可用 skills” 的行为
- 不改变各宿主工具映射说明
- 不把 method-pack 误写成 runtime core

验证：

- OpenCode base plugin-loading test 能找到 `using-aegis`
- e2e transcript parser tests 可解析 `using-aegis`
- boundary compliance check 不新增 authority drift

### 4.3 Phase C：agent-facing skill references

目标：

- skill body 中当前执行路径、sub-skill 提示、计划保存路径默认切到 `aegis`
- 新文档默认写入 `docs/aegis/...`
- 新本地视觉/brainstorm 产物默认写入 `.aegis/...`

兼容边界：

- 旧 upstream-specific historical docs subtree 已从公开用户可见内容移除
- 已存在 completion records 中的历史 evidence 不改写
- upstream thanks 不删除

### 4.4 Phase D：marketplace and external sync surfaces

目标：

- marketplace / plugin registry 相关名称切到 `Aegis`
- 若某平台仍要求旧标识，记录为 compatibility alias
- Codex plugin sync destination 收敛到 `plugins/aegis`
- Codex plugin sync fixture 不再以 `plugins/superpowers` 作为 active expectation

当前边界：

- 本阶段不声明 marketplace 上架完成
- 真实 marketplace 行为留到 private smoke / public cutover 阶段验证

当前验证：

- `scripts/sync-to-codex-plugin.sh` canonical destination：`plugins/aegis`
- `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh` 已迁移到 `aegis` fixture
- `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh` 通过
- `bash tests/e2e/run-all.sh --full --host-profile fast` 通过

---

## 5. 修复轨

1. 真实根因
   - fork 后方法层内容已演进为 `Aegis`，但 active install surfaces 仍沿用 upstream `superpowers` 标识
2. 唯一 canonical owner
   - 本文档负责 namespace cutover owner
   - `docs/current/AEGIS_HOST_INSTALL_CUTOVER_AUDIT.md` 负责 host install audit owner
3. 最小必要改动
   - 先切用户可见和宿主读取的 active surfaces
   - 历史归档、completion records、upstream lineage 文案不做无意义改写
4. 兼容边界
   - plugin-installable 能力必须保留
   - `superpowers` 只能作为 lineage 或明确兼容层保留
   - 不把当前 method pack 写成 runtime core
5. 验证方式
   - static manifest / plugin syntax check
   - OpenCode base install test
   - e2e boundary and artifact checks
   - private release smoke 时补真实宿主安装 evidence

---

## 6. 退役轨

1. 旧对象在哪里
   - upstream package/plugin names
   - `.opencode/plugins/superpowers.js`
   - `skills/using-superpowers/`
   - install docs 中的 `~/.codex/superpowers`、`~/.agents/skills/superpowers`
   - agent-facing `superpowers:<skill>` examples
   - Codex plugin sync test fixture 中的 `plugins/superpowers`
2. 是否仍在主链生效
   - active install surfaces 与 Codex sync fixture 已切换；旧测试变量 fallback 仍保留
3. 默认操作
   - active surfaces 改为 `aegis` / `Aegis`
4. 例外保留
   - upstream attribution / historical records
   - 经验证的平台限制导致暂时无法改名的 marketplace alias
5. 删除触发条件
   - private release smoke 确认 `aegis` 安装主链可用
   - public cutover 前清点剩余 active `superpowers` 标识
6. 删除前验证清单
   - 搜索 active surface 不再依赖旧路径
   - OpenCode base test 通过
   - Codex install docs 使用 `aegis` namespace
   - README 仍保留 upstream credit

---

## 7. 架构回望

本次 cutover 不改变 `Aegis Method Pack (runtime-ready)` 的边界。

本次 cutover 只改变：

- 用户可见品牌
- plugin/install namespace
- bootstrap skill identity
- 新文档与新本地产物默认路径

本次 cutover 不新增：

- runtime core
- host adapter
- authoritative `GateDecision`
- final completion authority

若后续发现某宿主只能以旧 `superpowers` 标识加载，应将该旧标识记录为 compatibility alias，并在 `AEGIS_PRIVATE_RELEASE_SMOKE_TEST_RECORD.md` 中记录阻塞原因、观察指标与退役时机。
