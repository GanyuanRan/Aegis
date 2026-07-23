# ADR-0002 Kimi 原生 Plugin 是 Aegis 自动入口

状态：`recorded-from-work`

## Source Evidence

- `b7cee13`：记录 Kimi 自动路由设计与候选方案
- `88b8ec9`：修复 Kimi 可见 skill metadata 的解析边界
- `6b90319`：加入根 `kimi.plugin.json` 与 `sessionStart.skill`
- `5f1ab62`：加入 `kimi-code-auto` / `kimi-code-explicit` doctor profile
- `2730a58`：加入 Kimi 确定性、集成与 live routing 测试通道
- `7123079`：同步安装、更新、activation、trigger-health 与兼容性基线

## 背景

Kimi Code CLI 能从 `$KIMI_CODE_HOME/skills/`、`~/.agents/skills/` 以及项目
skill 根发现独立 Aegis skills。原有 Aegis 安装因此能够支持显式调用，但用户反馈
表明自然语言任务很少稳定进入 `using-aegis`，表现为“安装成功，但通常只能手动
触发”。

根因不在单个 skill body：plain Agent Skills discovery 只让 Kimi 看见候选 skill，
并不保证每个新会话或恢复会话先进入 Aegis router。继续扩写 description 可以改善
匹配概率，但不能建立稳定的 session bootstrap owner。

## 决策

Kimi Code CLI 的 Aegis 默认自动安装采用 Kimi 原生 plugin：

- 根 `kimi.plugin.json` 是 Kimi host adapter manifest
- manifest 直接引用 canonical `./skills/`，不复制 Kimi-only skill bodies
- `sessionStart.skill = using-aegis` 建立新会话与恢复会话的稳定 router entry
- Kimi plugin manager 负责安装、managed copy、enablement、update 与 reload
- Aegis doctor 只读验证 managed root、版本、session-start entry 与重复 exposure
- updater-managed direct-child skill discovery 保留为 explicit compatibility mode
- plugin 与 direct-child exposure 不得同时启用

这一入口只加载方法层 routing discipline。它不授予 authoritative
`GateDecision`、`PolicySnapshot`、evidence sufficiency 或 completion authority。

## 备选方案

### 方案 A：只保留 direct-child skills，并继续优化 metadata

优点：分发简单，沿用现有 updater。

缺点：metadata 只能影响 Kimi 的候选匹配，不能保证 `using-aegis` 在 session start
进入决策路径，无法从结构上解决“多数时候需要手动触发”。

### 方案 B：把 bootstrap 规则写入用户全局 `AGENTS.md`

优点：能够提高全局入口可见度。

缺点：会修改用户拥有的跨项目规则面，并制造第二个 bootstrap owner；更新、冲突
和卸载边界不清晰。

### 方案 C：薄 Kimi plugin 复用 canonical skills tree

优点：使用宿主原生 session-start contract，不复制 router 或 skill bodies，且安装、
更新、enablement 与 reload owner 清晰。

缺点：需要用户确认第三方 plugin 信任；managed copy 更新必须走 Kimi plugin
manager；真实模型路由仍受 Kimi CLI、账号、provider 和宿主版本影响。

选择方案 C。

## 后果

正面影响：

- 自动入口从概率性 skill matching 提升为显式 session-start contract
- `using-aegis` 继续作为唯一 portable router owner
- Kimi-specific adapter 保持薄层，不引入 daemon、MCP 或 runtime core
- doctor 可以拒绝 plugin/direct-child 重复 owner，而不是静默选择

负面影响与成本：

- 既有 direct-child 用户迁移前必须识别并安全退役旧 exposure
- 自动安装的更新不再由 `aegis-update.py` 拥有，而由 Kimi plugin manager 拥有
- 通用安装提示词必须验证 host-native activation 与 automatic entry，不能只看文件
  discovery 或通用 doctor
- 当前环境缺少 Kimi CLI，尚无当前 release-level live routing closeout

## Compatibility Boundary

`$KIMI_CODE_HOME/skills/<skill-name>/SKILL.md` direct-child exposure 继续作为
explicit compatibility installation，适用于 plugin 不可用、组织策略禁止 plugin 或
用户明确要求显式模式的情况。`~/.agents/skills/` 只作为共享 fallback。

兼容模式的保留不允许形成两个同时激活的 Aegis owner。`kimi-code-auto` 与
`kimi-code-explicit` doctor profiles 分别验证这两个互斥状态。

## Retirement Impact

- 退役：direct-child 作为 Kimi 默认自动安装路径的定位
- 保留：direct-child 的 explicit compatibility 功能与 updater 支持
- 禁止：把 Codex umbrella symlink 当作 Kimi canonical 自动入口
- 重审条件：Kimi 官方 plugin/session-start contract 发生破坏性变化，或 fresh live
  evidence 表明 session-start entry 不能改善自然语言 routing reliability

## Baseline Sync

以下 current authority surfaces 已同步：

- `docs/README.kimi-code.md`
- `docs/current/AEGIS_ACTIVATION_MODE.md`
- `docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_FAST_TRACK_PLAYBOOK.md`
- `docs/current/AEGIS_FAST_TRACK_PLAYBOOK_ZH.md`

## 验证边界

确定性证据覆盖 manifest、版本同步、skill metadata、doctor profiles、重复 exposure
拒绝、安装文档契约以及 live smoke evaluator。真实 Kimi plugin install、reload/new、
resume 与自然语言模型 routing 因当前机器缺少 `kimi` 而仍是 environment-bound
unknown。
