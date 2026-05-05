# Aegis Open-Source Release Plan

状态：`Reviewed`

## 1. 文档定位

本文档定义当前 `Aegis Method Pack (runtime-ready)` 的开源发布实施计划。

本文档回答以下问题：

1. 当前仓若要以 `method-pack` 形态对外开源，推荐采用什么仓库策略
2. 开源发布前应按什么顺序推进
3. 每一步的 owner、验证方式与 stop condition 是什么

本文档不负责：

- 授予 release authority
- 把当前仓升级成完整 `Aegis Platform`
- 直接替代 `AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`

---

## 2. 结论先行

当前最推荐的开源路径是：

> **保留当前 fork 仓作为 upstream 对照与持续开发仓；先建立 private `Aegis` release staging 仓完成真实安装冒烟与小型自举验证；通过后再将 `Aegis` 切换为公开发行主仓。**

理由如下：

1. 当前仓已明显不是单纯 upstream 小改，而是独立的方法包产品形态
2. 独立公开仓更利于品牌、release、issue、roadmap 与社区治理
3. 可以继续保留 fork 与 `superpowers` 的 lineage，而不把对外发行叙事绑死在 fork network 上
4. 更有利于未来把 `Aegis Method Pack` 与 future `Host Adapters + Runtime Core` 分层演进
5. private-first smoke 能在公开曝光前验证安装链和基础可用性，降低首次公开后的维护压力

---

## 3. 发布目标

本轮开源发布的目标是：

1. 对外发布一个独立成立的 `Aegis Method Pack`
2. 保持 plugin-installable 分发骨架
3. 对外明确当前 fresh-evidence 支撑的宿主范围
4. 不误导用户把当前仓理解成完整平台

本轮开源发布的非目标是：

1. 宣布完整 `Aegis Platform` 已可用
2. 覆盖全部宿主的 release-level fresh closeout
3. 引入 runtime core authority
4. 在公开仓中暴露不必要的内部迁移输入与本机环境细节

---

## 4. 推荐仓库策略

### 4.1 首选方案

采用双仓模式：

1. **当前 fork 仓**
   - 角色：持续开发仓 / upstream 对照仓 / 迁移整合仓
   - 作用：保留与 `superpowers` 的 fork lineage，继续承载二开演进
2. **新的公开仓**
   - 名称：`Aegis`
   - 角色：先作为 private release staging 仓，验证通过后转为开源发行主仓
   - 作用：承载对外 README、release、issues、community profile 与版本发布

### 4.2 不推荐方案

直接把当前 fork 仓作为最终公开主仓。

不推荐的原因：

1. 对外品牌会长期受 fork network 叙事干扰
2. 社区容易将其理解为 upstream 变体，而非独立方法包
3. 后续若继续建设 `Aegis Platform`，边界更容易再次混淆

---

## 5. 开源发布实施顺序

### Phase A：公开仓范围裁剪

目标：

- 明确哪些文件进入公开主仓
- 哪些文件仅留在开发仓
- 哪些文件迁移到 archive / historical inputs

owner：

- `docs/current/AEGIS_PUBLIC_REPO_FILE_DISPOSITION.md`

验证：

- 所有对外入口都能回指 current owners
- 不再暴露不必要的本机绝对路径、私有环境前提或临时治理草稿

stop condition：

- 文件边界未收敛前，不进入正式建仓与发布

### Phase B：公开仓治理文件补齐

目标：

- 补齐公开仓 community profile 与基本治理入口

最低交付：

1. `README.md`
2. `README.zh-CN.md`
3. `LICENSE`
4. `CODE_OF_CONDUCT.md`
5. `CONTRIBUTING.md`
6. `SECURITY.md`
7. `SUPPORT.md`
8. `CODEOWNERS`
9. `.github/workflows/ci.yml`

验证：

- GitHub community profile 可达标
- 对外协作者可看懂如何安装、如何贡献、如何反馈问题

stop condition：

- 若公开仓的基础治理文件缺失，不建议发布首个公开版本

### Phase C：对外叙事与入口统一

目标：

- 把公开仓首页叙事与 current baseline 对齐

最低检查：

1. 只把当前仓描述为 `Aegis Method Pack (runtime-ready)`
2. 明确当前有 fresh evidence 的宿主范围
3. 把 known limitations 明确暴露
4. 不把 production rollout 后置项写成已完成

安装标识目标：

1. 公开发布的最终用户可见安装标识必须收敛到 `Aegis`
2. `superpowers` 标识只允许在 cutover 前或宿主限制下作为临时 compatibility alias
3. 每个 compatibility alias 都必须记录退役触发条件，并在宿主验证通过后退役

验证：

- 回读 `README.md`
- 回读 `README.zh-CN.md`
- 回读 `docs/README.codex.md`
- 回读 `docs/README.opencode.md`
- 回读 `docs/testing.md`

### Phase D：公开发布前最终验证

目标：

- 用当前 method-pack release gate 做正式发布前收口

最低 fresh verification：

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

按需补充：

```bash
bash tests/opencode/run-tests.sh --integration
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

owner：

- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`

### Phase D0：Private Release Smoke

目标：

- 在 private `Aegis` release staging 仓中按未来公开安装路径完成真实环境冒烟

owner：

- `docs/current/AEGIS_PRIVATE_RELEASE_SMOKE_TEST_PLAN.md`
- `docs/current/AEGIS_PRIVATE_RELEASE_SMOKE_TEST_RECORD.md`

最低验证：

1. OpenCode 推荐安装路径可运行
2. Codex 推荐安装路径至少一条可运行
3. 核心 skills 可被宿主发现或调用
4. Aegis 能参与一个小型真实开发任务
5. 发现的问题已写入 smoke record 或 known limitations

stop condition：

- private smoke 未通过前，不进入 public cutover
- private repo 权限路径不得被写成 public 用户安装路径

### Phase E：Public Cutover 与首个公开 release

目标：

- 将 private `Aegis` release staging 仓切换为 public，并发布首个公开可安装版本

最低交付：

1. tag / version
2. release notes
3. known limitations 摘要
4. 当前宿主兼容快照摘要

---

## 6. 当前建议保留在开发仓、而不是直接暴露为公开主叙事的内容

以下内容默认不应成为公开仓首页的主叙事：

1. `AGENTS_RULES.md`
2. `Aegis_Fork_Bootstrap_Pack/`
3. `docs/plans/`
4. upstream-specific historical design/spec subtree

处理方式：

- 可保留在开发仓
- 若公开仓仍需保存，应显式标注为 historical / migration inputs
- 不应与当前 authoritative docs 并列呈现

---

## 7. 双轨治理要求

### 7.1 修复轨

如果开源整理过程中发现问题，必须回答：

1. 真实根因
2. 唯一 canonical owner
3. 最小必要改动
4. 兼容边界
5. 验证方式

### 7.2 退役轨

如果开源整理过程中发现历史目录、旧说明、旧 fallback 或重复 owner，默认回答：

1. 旧对象在哪里
2. 是否仍在公开主链生效
3. 能否直接从公开主仓删除
4. 若暂不能删，保留理由是什么
5. 删除或迁移后的验证方式是什么

---

## 8. 当前最小执行清单

如果按推荐路径继续推进，下一轮最小工作应为：

1. 建立新的 private `Aegis` release staging 仓
2. 根据 `AEGIS_PUBLIC_REPO_FILE_DISPOSITION.md` 做文件保留/迁移/归档决策
3. 回读 `CONTRIBUTING.md`、`SECURITY.md`、`SUPPORT.md`、`CODEOWNERS`、`.github/workflows/ci.yml`
4. 按 `AEGIS_PRIVATE_RELEASE_SMOKE_TEST_PLAN.md` 在干净机器上做 private smoke
5. 将结果写入 `AEGIS_PRIVATE_RELEASE_SMOKE_TEST_RECORD.md`
6. private smoke 通过后，再执行 public cutover 与首个 method-pack release

---

## 9. Architecture Review

执行本计划时必须持续检查：

1. 当前公开对象是否仍只是 `Method Pack`
2. 当前公开仓是否仍保留 plugin-installable 属性
3. 当前公开叙事是否把 verified host path 与 target host path 清楚区分
4. 当前是否避免把开发仓里的迁移输入误抬成公开 baseline
5. 当前是否把 private staging 限制与 public 安装路径清楚区分
