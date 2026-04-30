# Aegis Host Install Cutover Audit

状态：`Approved`

## 1. 文档定位

本文档记录 `Aegis` 独立公开仓建立前后，host install docs、package manifests、plugin metadata 与宿主推理输出中的 namespace cutover 状态。

本文档回答以下问题：

1. 哪些 active surfaces 已切换到 `Aegis` / `aegis`
2. 哪些 `superpowers` 文本只作为 lineage、历史证据或 compatibility alias 保留
3. 哪些兼容变量需要后续退役
4. 哪些真实宿主 smoke 仍待 private release 阶段补证

本文档不负责：

- 直接执行 manifest rename
- 直接替换安装 URL
- 直接声明 host install cutover 已完成

---

## 2. 当前结论

最终公开发布目标是：所有用户可见的安装标识、display name、repository metadata、安装 URL 与公开文档口径都收敛到 `Aegis`。

宿主推理输出中的主 namespace 也必须收敛到 `aegis` / `Aegis`。正式安装后的目标示例是：

```text
Using aegis:using-aegis
Using aegis:writing-plans
Using aegis:verification-before-completion
```

不应继续以以下形式作为正式主链输出：

```text
Using superpowers:using-superpowers
Using superpowers:writing-plans
```

截至本轮 namespace cutover，active install surfaces 已切到 `Aegis` / `aegis`：

- `package.json`
- `gemini-extension.json`
- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `.cursor-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.opencode/plugins/aegis.js`
- `hooks/session-start`
- `GEMINI.md`
- `.codex/INSTALL.md`
- `.opencode/INSTALL.md`
- `docs/README.codex.md`
- `docs/README.opencode.md`
- `skills/using-aegis/`
- active skill body 中的 `aegis:<skill>` 示例

当前不再把 `superpowers` 作为 active install target。

仍允许出现 `superpowers` 的位置：

1. README / product docs 中的 upstream attribution
2. 历史 completion records 与 release notes
3. `Aegis_Fork_Bootstrap_Pack/` 迁移输入材料
4. 明确标注的兼容变量 fallback，例如 `SUPERPOWERS_TEST_CLI`

---

## 3. 当前 cutover 状态

### 3.1 package / extension manifests

当前状态：`Cut over`

已切换对象：

1. `package.json`
   - `name: "aegis"`
   - `main: ".opencode/plugins/aegis.js"`
2. `gemini-extension.json`
   - `name: "aegis"`
3. `.claude-plugin/plugin.json`
   - `name: "aegis"`
   - `homepage` / `repository` 指向 Aegis 仓
4. `.codex-plugin/plugin.json`
   - `name: "aegis"`
   - `displayName: "Aegis"`
   - `composerIcon: "./assets/aegis-small.svg"`
5. `.cursor-plugin/plugin.json`
   - `name: "aegis"`
   - `displayName: "Aegis"`
6. `.claude-plugin/marketplace.json`
   - `aegis-dev`
   - `aegis`

剩余要求：

- private smoke 时验证各宿主是否接受新标识
- 若 marketplace 对旧标识有平台限制，单独登记为 compatibility alias

### 3.2 host install docs

当前状态：`Cut over`

已切换对象：

1. `.codex/INSTALL.md`
2. `.opencode/INSTALL.md`
3. `docs/README.claude-code.md`
4. `docs/README.codex.md`
5. `docs/README.opencode.md`

当前目标口径：

- Claude Code marketplace name：`aegis-dev`
- Claude Code plugin name：`aegis`
- Codex 安装 namespace：`~/.agents/skills/aegis`
- Codex clone path：`~/.codex/aegis`
- OpenCode plugin identifier：`aegis@git+https://github.com/GanyuanRan/Aegis.git`
- OpenCode plugin file：`aegis.js`

Claude Code 边界：

- 当前有 `.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json`
- 当前有安装引导 owner：`docs/README.claude-code.md`
- 当前尚未形成 Claude Code release-level fresh smoke verdict

### 3.3 OpenCode runtime plugin owner

当前状态：`Cut over`

当前对象：

- `.opencode/plugins/aegis.js`

该对象负责：

- 加载 `skills/using-aegis/SKILL.md`
- 注入 `You have Aegis.`
- 镜像 skills 到 OpenCode native global skills path
- 将 `config.skills.paths` 作为兼容 fallback

### 3.4 agent-visible namespace and bootstrap skill

当前状态：`Cut over`

当前对象：

1. `skills/using-aegis/`
   - frontmatter `name: using-aegis`
2. `hooks/session-start`
   - 注入 `aegis:using-aegis`
3. `.opencode/plugins/aegis.js`
   - 注入 `You have Aegis.`
   - 加载 `using-aegis`
4. `GEMINI.md`
   - `@./skills/using-aegis/SKILL.md`
5. active skill body 中的 `aegis:<skill>` 示例

### 3.5 compatibility variables

当前状态：`Compatibility alias retained`

保留对象：

1. `SUPERPOWERS_TEST_CLI`
   - 新主变量为 `AEGIS_TEST_CLI`
   - 旧变量作为测试脚本 fallback
2. `SUPERPOWERS_ROOT`
   - 新主变量为 `AEGIS_ROOT`
   - 旧变量作为 brainstorm server 测试 fallback
3. `SUPERPOWERS_DIR` / `SUPERPOWERS_SKILLS_DIR` / `SUPERPOWERS_PLUGIN_FILE`
   - 新主变量为 `AEGIS_DIR` / `AEGIS_SKILLS_DIR` / `AEGIS_PLUGIN_FILE`
   - 旧变量作为 OpenCode test helper fallback export

保留理由：

- 避免已有本地测试命令立即失效
- 不影响正式安装标识或宿主推理输出

退役触发条件：

- public cutover 前最后一轮测试文档已全部切到 `AEGIS_*`
- private smoke 未发现仍依赖旧变量的执行路径
- 删除旧变量 fallback 后 `bash tests/opencode/run-tests.sh` 与 `bash tests/e2e/run-all.sh --full --host-profile none` 通过

### 3.6 Codex plugin sync path

当前状态：`Cut over`

当前对象：

- `scripts/sync-to-codex-plugin.sh`
- `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`

当前目标口径：

- Codex marketplace embedded plugin path：`plugins/aegis`
- sync branch prefix：`sync/aegis-`
- bootstrap branch prefix：`bootstrap/aegis-`
- Codex composer icon asset：`assets/aegis-small.svg`

本轮修复：

- `scripts/sync-to-codex-plugin.sh` 已经以 `plugins/aegis` 为 canonical destination
- `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh` 的旧 `plugins/superpowers` fixture 已迁移为 `plugins/aegis`

验证：

- `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh` 通过
- `bash tests/e2e/run-all.sh --full --host-profile fast` 通过，并覆盖 codex plugin sync regression

---

## 4. Remaining stop condition

在以下条件满足前，不应声明 namespace cutover 具备 release-level host evidence：

1. private `Aegis` release staging 仓已建立
2. 真实 Codex 安装可发现 `using-aegis`
3. 真实 OpenCode 安装可加载 `aegis` 插件
4. 宿主输出不再以 `superpowers:` 作为正式主前缀
5. 若某宿主仍显示旧前缀，已记录为 compatibility alias 与退役计划

---

## 5. 修复轨

1. 真实根因
   - 当前仓从 `superpowers` fork 演进为 `Aegis`，但 host install、manifests 与 bootstrap skill 曾仍承载 upstream 标识
2. 唯一 canonical owner
   - 本文档
3. 最小必要改动
   - active install surfaces、bootstrap skill、OpenCode plugin、host docs、test owners 切到 `Aegis` / `aegis`
4. 兼容边界
   - 保留 upstream attribution
   - 保留旧测试环境变量 fallback
   - 不把 private smoke 尚未执行包装成 release-level host evidence
5. 验证方式
   - static JSON parse
   - `node --check .opencode/plugins/aegis.js`
   - OpenCode base suite
   - Codex plugin sync regression
   - e2e boundary, no-host aggregate checks, and fast host-profile aggregate checks
   - private smoke 阶段补真实宿主安装 evidence

---

## 6. 退役轨

1. 旧对象在哪里
   - package manifests、plugin manifests、host install docs、OpenCode plugin filename、bootstrap skill、Codex sync fixture、测试变量
2. 是否仍在主链生效
   - active install surfaces 与 Codex sync fixture 已切换；旧测试变量仍作为 fallback 生效
3. 默认操作
   - 退役旧 `superpowers` 用户可见标识
4. 保留理由
   - 只保留不影响正式安装标识的测试变量 fallback 与历史/致谢文本
5. 退役触发条件
   - private smoke 通过后，删除旧测试变量 fallback 并复跑 focused verification

---

## 7. Architecture Review

执行 host install cutover 时必须持续检查：

1. 是否把临时 compatibility alias 误写成最终目标状态
2. 是否在没有 host evidence 的情况下重命名 plugin/package
3. 是否破坏 plugin-installable 这个硬要求
4. 是否把 upstream credit 删除到不可追溯
