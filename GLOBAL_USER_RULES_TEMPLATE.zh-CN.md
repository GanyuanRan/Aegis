# Aegis 全局路由前缀

将下面的规则块添加到现有全局用户规则的最开头即可，无需改动原有内容。

这是一个可选、手工复制的宿主/profile 前缀。它不会安装 Aegis，也不能证明 skill
已经可发现；它不由 `aegis:update` 自动更新。release notes 声明路由前缀变化
时，需要重新复制或手工合并。

```markdown
# Aegis 全局路由前缀

如果已安装 Aegis：

- 遵循宿主或当前会话提供的 Aegis Activation Mode；未声明时按默认 `auto` 处理。
- `auto`：每轮开始判断当前任务是否匹配已安装的 Aegis skill；匹配时，在回复或行动前加载并遵循最相关的最小必要 skill。
- `explicit`：只有用户明确调用 Aegis 或指定 Aegis skill 时才加载；不得仅根据任务语义自动启用 Aegis。
- 没有匹配的 Aegis skill 时，直接走普通 fast path；已匹配时，按照对应 skill 的规则决定是否使用 fast path，不因安装了 Aegis 而自动展开完整治理流程。
- 在长任务续接、会话恢复、上下文压缩或任务明显切换后，根据当前任务重新检查 Aegis 路由。
- 具体的分析、规划、调试、TDD、验证、治理和输出要求，由当前加载的 Aegis skill 按需决定。
- TDD Mode 独立于 Activation Mode，遵循当前 Aegis 配置（默认 `off`，可选 `auto`）以及用户或项目的明确要求。
```
