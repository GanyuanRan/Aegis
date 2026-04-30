# Aegis Rule Layering

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis` 当前规则体系的分层边界。

本文档只负责回答以下问题：

- 哪些规则属于可迁移的方法层核心
- 哪些规则属于宿主 / profile 偏好
- 哪些规则属于当前仓的贡献约束

---

## 2. 三层规则模型

### 2.1 Portable Method Rules

适合进入 `Aegis Method Pack` 核心的规则包括：

- TLREF
- DIVE
- Reflection
- QA
- 证据驱动
- 双轨治理
- 输出契约

### 2.2 Host / Profile Rules

不应直接写入通用 method-pack baseline 的规则包括：

- `sequential-thinking`
- 优先 `serena` / `context7`
- 宿主特有 tool routing
- 某个插件平台独有的装配方式

这些规则应进入：

- host adapter docs
- host-specific profile
- install / usage guide

### 2.3 Repo Contribution Rules

只约束当前仓贡献与本地实现的规则包括：

- 文件长度限制
- 命名约定
- 本仓安全与提交约束
- 文档落点约束

这些规则不应自动提升为跨宿主通用方法论。

---

## 3. 当前母稿的分层结论

根部 `AGENTS_RULES.md` 当前应视为：

> 尚未完全拆层的规则母稿

后续迁移原则：

- 方法论核心迁入 `docs/current/` 与 skills
- 宿主偏好迁入 host-facing docs
- 仓库约束迁入 repo contribution docs

---

## 4. 设计约束

后续任何规则新增，都必须先回答：

1. 它是否可跨宿主迁移
2. 它是否依赖特定工具能力
3. 它是否只服务当前仓贡献

只有第一类，才允许进入 method-pack core。
