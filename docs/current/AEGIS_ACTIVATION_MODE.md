# Aegis Activation Mode

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis Method Pack` 的宿主激活模式。

本文档只负责回答以下问题：

- Aegis 是否默认自动注入启动纪律
- 用户如何关闭自动注入但保留显式调用
- 该开关属于 method-pack / host profile / runtime core 哪一层

本文档不负责回答以下问题：

- future runtime core 的最终 policy enforcement
- 每个宿主内部的 token 预算实现
- 宿主原生 skill matcher 是否会在未注入 bootstrap 时仍自动匹配某个 skill

---

## 2. 结论先行

Aegis 的宿主侧激活模式由用户本地配置和环境变量共同定义：

- `auto`：默认模式。Aegis 可以自动注入 compact bootstrap，并参与 skill
  routing discipline。
- `explicit`：显式模式。Aegis 不自动注入 bootstrap；agent 只有在用户显式
  调用 Aegis 或某个 Aegis skill 时才使用 Aegis。

默认不需要配置文件；没有配置时等同于：

```text
activation_mode = "auto"
```

当前只定义 `auto` 与 `explicit`。`off` 暂不定义，避免把“关闭自动介入”
误解成“卸载或隐藏所有 skills”。

---

## 3. 显式调用语义

推荐配置方式是用户本地配置文件：

```text
~/.config/aegis/config.toml
```

Windows：

```text
%USERPROFILE%\.config\aegis\config.toml
```

安装不会自动创建该文件。需要显式模式时，手动创建目录和文件，并写入：

```toml
activation_mode = "explicit"
```

改回自动模式时，写入：

```toml
activation_mode = "auto"
```

也可以删除该文件，回到默认 `auto`。

高级临时覆盖方式是环境变量 `AEGIS_ACTIVATION_MODE`。它必须在宿主进程启动前
进入该进程的 environment，并且优先级高于用户本地配置文件。

一次性终端启动示例：

```bash
AEGIS_ACTIVATION_MODE=explicit opencode
AEGIS_ACTIVATION_MODE=explicit claude
```

PowerShell 一次性启动示例：

```powershell
$env:AEGIS_ACTIVATION_MODE = "explicit"
opencode
# 或：claude
```

长期生效方式：

- bash/zsh 用户可把 `export AEGIS_ACTIVATION_MODE=explicit` 写入 `~/.zshrc`
  或 `~/.bashrc`
- PowerShell 用户可把 `$env:AEGIS_ACTIVATION_MODE = "explicit"` 写入
  `$PROFILE`，或用 `[Environment]::SetEnvironmentVariable(...)` 设置系统 /
  用户环境变量
- GUI 启动的宿主必须从已经带有该环境变量的 launcher、shell 或系统环境启动
- 修改后需要重启或重新加载宿主，已经运行的 session 通常不会自动继承新值

读取优先级：

1. `AEGIS_ACTIVATION_MODE`
2. `~/.config/aegis/config.toml`
3. 默认 `auto`

在 `explicit` 模式下，以下输入仍应允许 Aegis 被使用：

- `use aegis`
- `用 Aegis`
- `aegis:using-aegis`
- `use aegis:brainstorming`
- `调用 aegis:test-driven-development`
- 宿主支持的其他直接 skill 调用形式

`explicit` 只关闭自动 bootstrap 注入；它不删除 Aegis skills，不卸载插件，
也不禁止用户点名调用。

---

## 4. 分层边界

该开关属于 host / profile rule：

- method-pack 定义模式语义
- host install surface 负责读取变量并调整 bootstrap 注入
- future host adapter 可以把它升级为更正式的 profile 配置
- future runtime core 才能承担 authoritative enforcement

因此，`explicit` 模式不能被写成最终 `GateDecision`、`PolicySnapshot` 或
completion authority。

---

## 5. 宿主行为

支持自动 bootstrap 注入的宿主应遵循：

1. `auto` 或未设置：维持现有自动注入行为。
2. `explicit`：不自动注入 `using-aegis` bootstrap。
3. 未识别值：保守回退到 `auto`，避免静默禁用 Aegis。

仅依赖宿主原生 skill discovery 的宿主，应在安装文档中说明：

- Aegis 可以被显式调用
- 宿主自己的 semantic skill matcher 可能仍由宿主控制
- 如果用户需要强制显式模式，应使用宿主支持的 profile / install 配置隐藏
  或不安装自动入口 skill

---

## 6. 验证边界

最低验证包括：

- `auto` 模式仍注入 bootstrap
- `explicit` 模式不注入 bootstrap
- Aegis skills 仍保持安装和发现路径
- 文档明确说明显式调用仍可用

这些验证只是 method-pack evidence，不授予 authoritative runtime completion。
