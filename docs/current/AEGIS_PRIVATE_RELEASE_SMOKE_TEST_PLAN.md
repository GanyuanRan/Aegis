# Aegis Private Release Smoke Test Plan

状态：`Reviewed`

## 1. 文档定位

本文档定义 `Aegis Method Pack (runtime-ready)` 在公开发布前的 private-first 冒烟验证路径。

本文档回答以下问题：

1. 为什么先建立 private `Aegis` 仓再转 public
2. private 阶段最低要验证什么
3. 哪些结果满足后才允许进入 public cutover

本文档不负责：

- 授予 public release authority
- 替代 `AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- 执行 GitHub 仓库创建或权限配置

---

## 2. 当前结论

当前推荐发布路径调整为：

> **先建立 private `Aegis` release staging 仓，按未来公开仓真实安装方式完成最小冒烟与自举验证；通过后再切换为 public。**

理由：

1. 在公开曝光前验证安装链，避免把首次用户变成安装链测试者
2. 在真实干净机器上验证 `Aegis` 安装标识、文档口径与宿主行为
3. 降低公开后维护压力，把已知问题先收敛进 known limitations
4. 保留 method-pack 边界，不把 private smoke 误写成完整平台验证

---

## 3. 测试范围

### 3.1 必测对象

1. private `Aegis` 仓库可被测试机器访问
2. OpenCode 推荐安装路径可运行
3. Codex 推荐安装路径至少一条可运行
4. 核心 skills 可被宿主发现或调用
5. Aegis 能参与一个小型真实开发任务
6. 输出仍保持 method-pack artifact 边界

### 3.2 不测对象

1. 完整 `Aegis Platform`
2. 所有宿主的 marketplace 上架
3. runtime core authority
4. 企业级部署、SLA 或生产 rollout

---

## 4. 推荐测试环境

至少使用一台非当前开发机的干净机器。

最低记录字段：

1. 操作系统与版本
2. Git 版本
3. Codex 版本与安装方式
4. OpenCode 版本与安装方式
5. private repo 访问方式
6. 测试时间
7. 测试人

不得把个人 token、私有凭据或机器专属敏感信息写入公开候选文档。

---

## 5. 冒烟任务

### Smoke A：仓库安装路径

目标：

- 验证 private `Aegis` 仓按推荐方式可安装

最低验证：

1. OpenCode 可从 private `Aegis` 仓安装插件或等价分发入口
2. Codex 可按 `.codex/INSTALL.md` 或公开候选安装文档完成安装
3. 安装路径不要求用户手动管理源码目录

通过标准：

- 宿主能发现 Aegis skills
- 安装说明不再依赖 `superpowers` 作为最终用户可见标识
- private repo 权限限制被记录为 private-only limitation

### Smoke B：技能触发路径

目标：

- 验证 Aegis 的核心 method-pack workflow 可触发

最低验证：

1. `brainstorming`
2. `systematic-debugging`
3. `verification-before-completion`

通过标准：

- 宿主能加载或触发上述 skills
- 输出包含事实、证据、验证或边界说明
- 没有把 Aegis 声明为完整平台或 runtime core

### Smoke C：小型真实任务

目标：

- 用 Aegis 完成一个低风险真实任务

推荐任务：

1. 审计 README 与安装说明是否适合首次用户
2. 检查 private-first release docs 是否互相一致
3. 对一个小型文档问题执行修复轨 + 退役轨

通过标准：

- 有明确 plan 或 task framing
- 有最小必要改动
- 有验证命令或 readback 证据
- 有 architecture review
- 人工确认后才能进入 public cutover

---

## 6. Stop Conditions

出现以下任一情况，不进入 public cutover：

1. OpenCode 推荐安装路径无法完成
2. Codex 没有任何可执行安装路径
3. 核心 skills 无法被宿主发现或调用
4. README / install docs 仍引用旧安装标识作为目标状态
5. private 测试发现的问题没有写入 known limitations 或 smoke record
6. 当前仓被误写成完整 `Aegis Platform`

---

## 7. 通过条件

满足以下条件后，可进入 public cutover：

1. private `Aegis` 仓内容与公开候选内容一致
2. OpenCode smoke 通过
3. Codex smoke 至少有一条安装路径通过
4. 小型真实任务验证 Aegis 具备可用价值
5. smoke record 已落盘
6. known limitations 已更新
7. release checklist 没有阻塞项

---

## 8. 修复轨

1. 真实根因
   - 直接 public release 会把真实安装风险和维护压力外放给首次用户
2. 唯一 canonical owner
   - 本文档
3. 最小必要改动
   - 增加 private release smoke gate，不改变 method-pack 范围
4. 兼容边界
   - 不破坏公开仓最终必须切到 `Aegis` 的目标状态
   - 不把 private repo 权限路径写成 public 用户安装路径
5. 验证方式
   - 按本文档执行 smoke，并在 `AEGIS_PRIVATE_RELEASE_SMOKE_TEST_RECORD.md` 记录结果

---

## 9. 退役轨

1. 旧对象在哪里
   - 直接从开发仓进入 public release 的路径
2. 是否仍在主链生效
   - 不应作为当前推荐路径继续生效
3. 默认操作
   - 将 direct public release 降级为 private smoke 之后的 cutover 动作
4. 保留理由
   - public release 仍是最终目标，但不再是第一验证动作
5. 验证
   - release plan 与 cutover checklist 均指向 private-first gate

---

## 10. Architecture Review

执行 private smoke 时必须持续检查：

1. 是否仍只验证 `Method Pack`
2. 是否仍保留 plugin-installable 属性
3. 是否把 private repo 权限限制与 public 用户安装路径区分清楚
4. 是否避免让 Aegis 自己给自己授予最终完成权
