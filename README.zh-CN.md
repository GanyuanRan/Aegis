<p align="center">
    <a href="https://linux.do/t/topic/2108966/20" alt="LINUX DO">
        <img
            src="https://img.shields.io/badge/LINUX-DO-FFB003.svg?logo=data:image/svg%2bxml;base64,DQo8c3ZnIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAiIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cGF0aCBkPSJNNjguMi0uMDU1aDYuMjVxMjMuOTY5IDIuMDYyIDM4IDIxLjQyNmM1LjI1OCA3LjY3NiA4LjIxNSAxNi4xNTYgOC44NzUgMjUuNDV2Ni4yNXEtMi4wNjQtMjMuOTY4LTIxLjQzIDM4LTExLjUxMiA3Ljg4NS0yNS40NDUgOC44NzRoLTYuMjVxLTIzLjk3LTIuMDY0LTM4LjAwNC0yMS40M1EuOTcxIDY3LjA1Ni0uMDU0IDUzLjE4di02LjQ3M0MxLjM2MiAzMC43ODEgOC41MDMgMTguMTQ4IDIxLjM3IDguODE3IDI5LjA0NyAzLjU2MiAzNy41MjcuNjA0IDQ2LjgyMS0uMDU2IiBzdHlsZT0ic3Ryb2tlOm5vbmU7ZmlsbC1ydWxlOmV2ZW5vZGQ7ZmlsbDojZWNlY2VjO2ZpbGwtb3BhY2l0eToxIi8+PHBhdGggZD0iTTQ3LjI2NiAyLjk1N3EyMi41My0uNjUgMzcuNzc3IDE1LjczOGE0OS43IDQ5LjcgMCAwIDEgNi44NjcgMTAuMTU3cS00MS45NjQuMjIyLTgzLjkzIDAgOS43NS0xOC42MTYgMzAuMDI0LTI0LjM4N2E2MSA2MSAwIDAgMSA5LjI2Mi0xLjUwOCIgc3R5bGU9InN0cm9rZTpub25lO2ZpbGwtcnVsZTpldmVub2RkO2ZpbGw6IzE5MTkxOTtmaWxsLW9wYWNpdHk6MSIvPjxwYXRoIGQ9Ik03Ljk4IDcwLjkyNmMyNy45NzctLjAzNSA1NS45NTQgMCA4My45My4xMTNRODMuNDI2IDg3LjQ3MyA2Ni4xMyA5NC4wODZxLTE4LjgxIDYuNTQ0LTM2LjgzMi0xLjg5OC0xNC4yMDMtNy4wOS0yMS4zMTctMjEuMjYyIiBzdHlsZT0ic3Ryb2tlOm5vbmU7ZmlsbC1ydWxlOmV2ZW5vZGQ7ZmlsbDojZjlhZjAwO2ZpbGwtb3BhY2l0eToxIi8+PC9zdmc+" /></a>
    <a href="https://dev.to/_879c5a0279451d52e43c3/aegis-a-method-pack-for-more-reliable-ai-coding-agents-1gfm" alt="DEV.to">
        <img src="https://img.shields.io/badge/DEV.to-Article-0A0A0A?logo=devdotto&logoColor=white" /></a>
    <a href="https://github.com/GanyuanRan/Aegis/actions/workflows/ci.yml" alt="CI">
        <img src="https://img.shields.io/github/actions/workflow/status/GanyuanRan/Aegis/ci.yml?branch=main&label=CI" /></a>
    <a href="https://github.com/GanyuanRan/Aegis/releases/latest" alt="Latest Release">
        <img src="https://badgen.net/github/release/GanyuanRan/Aegis?label=Latest%20Release" /></a>
</p>

<p align="center">
    <img src="assets/aegis-hero.png" alt="Aegis 架构驱动 AI 编程 agent 头图" />
</p>

# Aegis

<p align="center">
    <strong>Aegis Method Pack</strong><br/>
    面向 AI 编程 agent 的 baseline-first、evidence-driven 工作流程纪律包。
</p>

<p align="center">
    <a href="README.zh-CN.md"><strong>中文</strong></a>
    ·
    <a href="README.md"><strong>English</strong></a>
    ·
    <a href="docs/current/AEGIS_FAST_TRACK_PLAYBOOK_ZH.md">速通秘籍</a>
    ·
    <a href="docs/current/AEGIS_FAST_TRACK_PLAYBOOK.md">Fast-Track Playbook</a>
</p>

## 为什么需要 Aegis

Aegis 是面向真实软件工作的 **Superpowers 升级版**。它保留 composable
skills 的优点，并进一步加入：

- baseline first：高风险改动前先读当前项目事实
- evidence before completion：没有 fresh verification evidence，不声明完成
- repair track + retirement track：修复问题时同步说明旧路径保留或退役
- 工作流质量（Workflow Quality）护栏：简单任务保持轻量，风险升高才展开
- 多宿主可移植 method-pack skills

当 agent 容易在目标、owner、架构边界或验证路径不清楚时就开始写代码，Aegis
能把工作拉回更稳的工程节奏。

## 极简安装

把下面这段话交给你的 AI 编程 Agent：

```text
请阅读 https://github.com/GanyuanRan/Aegis，识别我当前使用的 AI 编程宿主，并按对应宿主说明全局安装 Aegis。如果需要重启或重新加载宿主，请明确告诉我；然后从已安装的 Aegis method-pack 根目录运行完整安装验证。不要在目标项目目录中运行 doctor 命令。先定位 `<aegis-method-pack-root>`，再运行 `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --write-config --json`。只有当 JSON 输出包含 `"ok": true`、`"workspaceSupport": "available"` 和 `"configStatus": "configured"` 时，才把安装视为完成；如果宿主有单独的 skill discovery 目录，也要额外用 `--discovery-root <path>` 验证它指向当前版本；如果宿主说明声明了 skill 目录名前缀，也同时传 `--discovery-name-prefix <prefix>`。
```

## 更新 Aegis

完成安装并登记当前宿主之后，后续更新可以用自然语言直接让 agent `更新 Aegis`，
也可以显式说 `aegis:update`。agent 可以把这两种方式路由到本地更新路径：先定位
已安装的 method-pack 根目录，读取本机 host-scoped registry，再调用
`scripts/aegis-update.py` 默认更新当前宿主。只有用户明确要求 `--all` 时才更新所有
已登记宿主。Aegis 默认不做后台自动更新。

## 使用前必须知道

Aegis 当前发布形态是：

> `Aegis Method Pack (runtime-ready)`

它不是完整的 Aegis Platform，不是 daemon，不是后台 runner，不是 runtime core，
不提供 authoritative `GateDecision`，不提供 authoritative `PolicySnapshot`，
也不授予 final completion authority。用户当前指令和目标项目规则优先于 Aegis。

为了让宿主级行为更顺滑，可以使用：

- [轻量全局规则](GLOBAL_USER_RULES_LITE.zh-CN.md)
- [高级全局规则模板](GLOBAL_USER_RULES_TEMPLATE.zh-CN.md)

Aegis 默认自动模式。要切换到显式模式，在已安装的 method-pack 根目录运行：

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

修改后需要重启宿主。长期设置方式和宿主注意事项见
[docs/current/AEGIS_ACTIVATION_MODE.md](docs/current/AEGIS_ACTIVATION_MODE.md)。

TDD mode 默认是 `off`：Aegis 不会自动要求 TDD，但完成前验证仍然适用。若希望
Aegis 按任务风险自动选择严格、轻量或跳过 TDD，可以手动开启：

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py tdd-mode auto
```

也可以在 query 中用 `TDD Route: strict`、`strict TDD`、`test-first` 或
`RED / GREEN / REFACTOR` 显式要求严格 TDD。

详细语义见 [docs/current/AEGIS_TDD_MODE.md](docs/current/AEGIS_TDD_MODE.md)。

## 宿主兼容性

Aegis 保留多宿主、plugin-installable 的分发目标。

| 宿主组 | 当前状态 | 从这里开始 |
| --- | --- | --- |
| `Codex`, `OpenCode` | 当前 method-pack 范围内已有 fresh evidence | [Codex](docs/README.codex.md), [OpenCode](docs/README.opencode.md) |
| `Claude Code`, `CodeBuddy`, `DeepSeek-TUI`, `Trae`, `GitHub Copilot`, `Qoder`, `Kimi Code CLI`, `ZCode`, `Grok Build` | 已有安装说明；release-level fresh host smoke 仍待补证 | [Claude Code](docs/README.claude-code.md), [CodeBuddy](docs/README.codebuddy.md), [DeepSeek-TUI](docs/README.deepseek-tui.md), [Trae](docs/README.trae.md), [GitHub Copilot](docs/README.copilot.md), [Qoder](docs/README.qoder.md), [Kimi Code CLI](docs/README.kimi-code.md), [ZCode](docs/README.zcode.md), [Grok Build](docs/README.grok-build.md) |
| `CC GUI (JetBrains IDEA)` | Claude Code / OpenAI-GPT 通道的 IDE 插件层结构性支持；release-level fresh host smoke 仍待补证 | [CC GUI](docs/README.cc-gui.md) |
| `Antigravity CLI`, `Antigravity IDE`, `Antigravity App` | `Antigravity CLI` 是当前主动 closeout 目标；`IDE/App` 仍是结构性目标，release-level fresh host smoke 仍待补证 | [Antigravity](docs/README.antigravity.md) |
| `Pi CLI`, `OpenClaw`, `Hermes Agent` | 结构性 Agent Skills / `SKILL.md` skill-host 适配；release-level fresh host smoke 仍待补证 | [Pi CLI](docs/README.pi.md), [OpenClaw](docs/README.openclaw.md), [Hermes Agent](docs/README.hermes-agent.md) |
| `Gemini CLI` | Antigravity 支持成熟前的过渡兼容面 | [兼容性矩阵](docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md) |

对外声明支持状态前，先读：

- [宿主兼容性矩阵](docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md)
- [已知限制](docs/current/AEGIS_KNOWN_LIMITATIONS.md)

## 快速上手 Aegis

安装并重启宿主后，直接用自然语言描述工作即可。Aegis 会按任务匹配方法；需要
更确定的行为时，再直接点名模式。

```text
这个登录失败的根因是什么？先诊断，不要立刻改代码。
审问我：我们是否应该先发布托管版？
Aegis goal: 修复登录后偶发跳回登录页，不重写 auth 系统。
在我合并前，独立审查这个 diff。
```

先阅读 [Aegis 速通秘籍](docs/current/AEGIS_FAST_TRACK_PLAYBOOK_ZH.md)：其中说明
Aegis 为什么轻量、它与独立 skill pack 的区别、五道工程护城河、项目工作区生命周期、
自然触发语句、activation/TDD 控制和常见排障。英文版见
[Fast-Track Playbook](docs/current/AEGIS_FAST_TRACK_PLAYBOOK.md)。

当你需要更强控制时，可以这样说：

- `Aegis goal: ...`：框定范围、成功证据与边界。
- `Grill me ...`、`审问我 ...`：进入决策访谈；每轮只问一个决策问题，不写计划、
  不实施。
- `TDD Route: strict`、`strict TDD` 或 `test-first`：显式要求严格 test-first；
  TDD 默认保持 `off`。
- `aegis:first-principles-review` 或“用第一性原理审查”：在实施前挑战复杂方向。
- `aegis:update`：按当前宿主的本地路径更新已安装的 method pack。

Aegis 用 Workflow Quality 让简单任务保持轻量，只在风险需要时展开。想深入了解
方法时，阅读 [工作流程说明](docs/current/AEGIS_WORKFLOW_GUIDE_ZH.md)、
[工作流质量基线](docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md)、
[复杂度治理基线](docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md) 和
[TDD 模式](docs/current/AEGIS_TDD_MODE.md)。

如果预期能力没有触发，不要先当成措辞问题。按触发链路诊断：安装/版本可见性、
宿主 skill discovery、activation mode、`using-aegis` 路由、任务到 skill 的匹配和
上下文压力。阅读
[触发健康基线](docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md)。

## 维护者入口

主要验证入口：

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

聚焦文档 / method-pack 检查：

```bash
bash tests/e2e/boundary-compliance-check.sh
bash tests/e2e/workflow-quality-check.sh
bash tests/e2e/install-verification-policy-check.sh
bash tests/e2e/layer1-fast-check.sh --host-profile none
```

阅读：

- [docs/testing.md](docs/testing.md)
- [发布检查清单](docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md)
- [当前 authority map](docs/current/README.md)
- [贡献说明](CONTRIBUTING.md)

## 与 Superpowers 的关系

Aegis 派生自 **[Superpowers](https://github.com/obra/superpowers)**，由
[Jesse Vincent](https://github.com/obra) 创建。Superpowers 开创了 composable、
multi-harness agent skills 的基础；Aegis 在此基础上加入面向真实软件项目的
architecture- and evidence-focused method layer。

项目还借鉴了 [mattpocock/skills](https://github.com/mattpocock/skills)
中关于极简沟通、共享语言和严谨调试的思路。这些思路均在 Aegis 自有格式中
重新实现，而不是原样复制。

## 许可证

MIT License。见 [LICENSE](LICENSE)。

## AI编程工具Aegis_QQ交流群：694329785

<p align="center">
    <img src="assets/aegis-qrcode.jpg" alt="Aegis QQ交流群二维码" width="320" />
</p>
