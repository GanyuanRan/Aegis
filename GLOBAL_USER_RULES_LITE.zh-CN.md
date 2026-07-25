# Aegis 轻量全局规则

这是一个可选、手工复制的宿主/profile 投影。它不会安装 Aegis，也不能证明 skill
已经可发现；它不会由 `aegis:update` 自动更新。release notes 声明 profile 变化时，
需要由用户重新复制或手工合并。

下面的可复制规则默认使用 `auto` activation profile。如果已安装 Aegis 配置为
`explicit`，请把 activation 条款替换为后面的 explicit 版本；两者只能保留一个。

```markdown
# Aegis 轻量全局规则

如果已安装 Aegis：

- Activation profile: `auto`。每轮开始先判断当前任务是否匹配已安装的 Aegis skill；匹配时加载并遵循对应 skill。
- 简单、局部、低风险任务走快速路径，不因为安装了 Aegis 就强行展开完整治理流程。
- Aegis 已在当前轮激活后，复杂、诊断、架构、重构、接口、跨模块、共享模块、兼容性或长期任务默认使用对应 workflow。
- 实施前先确认目标、范围、影响面和验证方式；必要时读取项目 baseline 或 authority docs。
- 声明完成前必须有新的验证证据；无法验证时说明阻塞点和残余风险。
- Aegis 是方法层，不是最终裁决系统；不得声明最终 gate decision 或 completion authority。
- 用户当前明确指令和目标项目规则优先于 Aegis。
```

## explicit 模式替换条款

只把上面的 activation 条款替换为：

```markdown
- Activation profile: `explicit`。只有用户显式调用 Aegis 或某个 Aegis skill 时才使用；不得根据任务语义自动路由。
```

这个替换只能对齐手工 profile；它不能保证宿主原生 skill matcher 不会独立匹配
已安装的 skill。

治理要求更强的团队应保留这份 Lite 基础规则，再从
[高级治理 overlay](GLOBAL_USER_RULES_TEMPLATE.zh-CN.md) 中只追加需要的部分。
