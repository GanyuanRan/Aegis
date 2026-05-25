# Aegis 轻量全局规则

当你希望提升 Aegis 路由和 skill 触发稳定性，但不想复制完整高级模板时，
可以把下面这段放进 AI 编程工具的全局用户规则。

```markdown
# Aegis 轻量全局规则

如果已安装 Aegis：

- 每轮开始先判断当前任务是否匹配已安装的 Aegis skill；匹配时加载并遵循对应 skill。
- 简单、局部、低风险任务走快速路径，不因为安装了 Aegis 就强行展开完整治理流程。
- 复杂、诊断、架构、重构、接口、跨模块、共享模块、兼容性或长期任务，默认使用对应的 Aegis workflow。
- 实施前先确认目标、范围、影响面和验证方式；必要时读取项目 baseline 或 authority docs。
- 声明完成前必须有新的验证证据；无法验证时说明阻塞点和残余风险。
- Aegis 是方法层，不是最终裁决系统；不得声明最终 gate decision 或 completion authority。
- 用户当前明确指令和目标项目规则优先于 Aegis。
```

如果团队治理要求更强，可以从
[GLOBAL_USER_RULES_TEMPLATE.zh-CN.md](GLOBAL_USER_RULES_TEMPLATE.zh-CN.md)
开始，只合并需要的部分。
