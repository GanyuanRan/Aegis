# Aegis Local-Only Overlay Policy

状态：`Reviewed`

## 1. 文档定位

本文档定义当前仓库对“本机化但仍需保留的开发内容”的统一处理策略。

本文档回答以下问题：

1. 哪些内容不应该进入公开仓，但仍应该在本地保留
2. 这些内容应该放在哪里
3. 如何避免本地 overlay 反向污染公开仓 baseline、CI 与安装说明

本文档不负责：

- 替代公开仓文件去留策略
- 替代去本机化审计清单
- 把 local-only 内容提升成 current authority

---

## 2. 当前结论

当前仓对本机化开发内容的 canonical 策略是：

> **把仍需本地保留、但不应进入公开发行主仓的内容，统一放入 repo root 下的 `.local/` 目录，并通过 git ignore 默认不上传。**

这意味着：

1. 本地开发仍可保留必要的 machine-specific 内容
2. 公开仓不必承载这些内容
3. local-only 内容不再分散在多个不透明位置

---

## 3. 适合放入 `.local/` 的内容

默认适合进入 `.local/` 的内容包括：

1. 本机运行备忘
2. 私有调试记录
3. 机器专属 helper scripts
4. 只适合当前开发环境的临时测试输入
5. 不适合作为公开仓安装说明的环境特化 runbook

默认不应放入 `.local/` 的内容包括：

1. current authority docs
2. 对外 README 与 host install docs
3. 公开 CI 依赖的脚本
4. 公开 release 所需的正式工件

---

## 4. 目录约定

当前 canonical local-only overlay 路径为：

- `.local/`

建议子目录：

- `.local/docs/`
- `.local/scripts/`
- `.local/tests/`
- `.local/notes/`

规则：

1. `.local/README.md` 可以被跟踪，用于说明约定
2. `.local/` 其他内容默认不应被跟踪
3. 若某内容被证明具有公开复用价值，应迁出 `.local/`，放入正式 owner 路径

---

## 5. 与公开仓 cutover 的关系

当某项内容满足以下条件时，优先考虑迁入 `.local/`，而不是直接删除：

1. 它对当前机器仍有开发价值
2. 它不适合公开发行主仓
3. 它不应继续污染对外叙事、安装文档或测试门禁

这类内容的典型处理顺序是：

1. 先判断是否应公开
2. 若不应公开，再判断是否仍有本地开发价值
3. 若仍有本地价值，则迁入 `.local/`
4. 若无本地价值，则删除或归档

---

## 6. 与去本机化审计的关系

`AEGIS_PUBLIC_REPO_DELOCALIZATION_CHECKLIST.md` 回答的是：

- 哪些对象需要去本机化审计

本文档回答的是：

- 审计之后，那些仍需本地保留的内容应该放哪里

因此，去本机化后的处理动作现在变成五类：

1. `泛化`
2. `删除`
3. `归档`
4. `仅开发仓保留`
5. `迁入 .local/`

---

## 7. 修复轨

1. 真实根因
   - 当前仓缺少统一的 local-only overlay owner，导致本机化内容容易散落并反向污染公开仓整理
2. 唯一 canonical owner
   - 本文档
3. 最小必要改动
   - 新增 `.local/` 约定与 ignore 规则
4. 兼容边界
   - 不删除当前仍需要的本地化开发内容
   - 不让 local-only 内容进入公开 baseline
5. 验证方式
   - `.local/README.md` 可见
   - `.local/` 其他内容默认被 git ignore

---

## 8. 退役轨

1. 当前旧 owner / 旧做法在哪里
   - 本机化内容目前零散分布在文档、测试、临时目录和个人开发习惯中
2. 是否仍在主链生效
   - 是，且容易造成公开仓整理噪音
3. 默认操作
   - 收敛到 `.local/` 这一单一 local-only overlay
4. 暂不删除的唯一理由
   - 某些内容仍对当前机器上的持续开发有价值
5. 验证
   - 未来本地化新增内容优先进入 `.local/`，而不是继续散落到公开候选路径

---

## 9. Architecture Review

执行本策略时必须持续检查：

1. `.local/` 是否仍只是 local-only overlay，而不是新 baseline
2. 是否有公开 CI、README、install docs 反向依赖 `.local/`
3. 是否把真正应公开的 owner 错误藏进 `.local/`
4. 是否同时满足“本地继续高效开发”和“公开仓保持干净”这两个目标
