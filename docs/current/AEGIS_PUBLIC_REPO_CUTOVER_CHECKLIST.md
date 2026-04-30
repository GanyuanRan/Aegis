# Aegis Public Repo Cutover Checklist

状态：`Reviewed`

## 1. 文档定位

本文档定义把当前开发仓内容整理到独立 `Aegis` release staging 仓，并在 private smoke 通过后切换为公开仓时的执行清单。

本文档回答以下问题：

1. 建立 private staging 仓与公开 cutover 时，实际执行顺序是什么
2. 每一步最低应核对哪些对象
3. 哪些条件满足前，不应进入下一步

本文档不负责：

- 代替文件去留策略本身
- 代替 release checklist
- 直接声明 cutover 已完成

---

## 2. 适用范围

本文档只适用于：

- `Aegis Method Pack (runtime-ready)` 的独立公开仓整理

本文档不适用于：

- 完整 `Aegis Platform`
- host adapter 仓
- runtime core 仓

---

## 3. 执行顺序

### Step 1：创建 private release staging 仓骨架

目标：

- 创建新的独立 private 仓 `Aegis`
- 明确它是 release staging 仓，通过冒烟后才切换为公开发行主仓

最低要求：

1. 新仓名称已确定为 `Aegis`
2. 默认分支确定
3. `LICENSE`、README、issue/PR、security/community 基础能力已准备迁入

stop condition：

- private staging 仓未建立前，不进入文件迁移

### Step 2：按文件去留策略筛选内容

owner：

- `docs/current/AEGIS_PUBLIC_REPO_FILE_DISPOSITION.md`

最低核对：

1. `保留` 内容进入公开仓候选集合
2. `迁移后保留` 内容进入“待改写/待清洗”集合
3. `归档` 内容不进入公开主叙事
4. `仅开发仓保留` 内容不进入公开发行主仓

stop condition：

- 若 `Aegis_Fork_Bootstrap_Pack/`、`docs/plans/`、`docs/superpowers/plans/` 仍被当作公开主内容，不进入下一步

### Step 3：执行去本机化清理

owner：

- `docs/current/AEGIS_PUBLIC_REPO_DELOCALIZATION_CHECKLIST.md`

最低核对：

1. 清理本机绝对路径
2. 清理只适合当前私有环境的 runner 描述
3. 清理只用于本机排障的临时说明
4. 清理临时缓存与本地依赖产物
5. 将仍需本地保留、但不应公开的内容迁入 `.local/`

stop condition：

- 若仍存在高显著度本机路径或私有环境假设，不进入公开 README 定稿

### Step 4：对外入口统一

最低核对：

1. `README.md` 已按独立公开仓完成第一轮重写
2. `README.zh-CN.md` 已准备根目录中文版本
3. `docs/README.codex.md`
4. `docs/README.opencode.md`
5. `docs/testing.md`
6. `docs/current/README.md`

必须确认：

1. 当前仓只被写成 `Aegis Method Pack (runtime-ready)`
2. 已验证宿主与目标宿主被清楚区分
3. 已知限制已明确暴露

### Step 5：治理文件与 CI 验证

最低核对：

1. `CONTRIBUTING.md`
2. `SECURITY.md`
3. `SUPPORT.md`
4. `CODEOWNERS`
5. `.github/workflows/ci.yml`

必须确认：

1. 公开协作入口完整
2. 基础 CI 可运行
3. 不依赖本机私有状态才能完成最小验证

### Step 6：Private release smoke

owner：

- `docs/current/AEGIS_PRIVATE_RELEASE_SMOKE_TEST_PLAN.md`
- `docs/current/AEGIS_PRIVATE_RELEASE_SMOKE_TEST_RECORD.md`

最低核对：

1. OpenCode 推荐安装路径可运行
2. Codex 推荐安装路径至少一条可运行
3. 核心 skills 可被宿主发现或调用
4. 小型真实任务已完成并记录 evidence
5. private 权限限制没有被写成 public 用户安装路径

stop condition：

- private smoke 未通过前，不进入 public cutover

### Step 7：发布前最终收口

owner：

- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`

最低验证：

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

按需补充：

```bash
bash tests/opencode/run-tests.sh --integration
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

### Step 8：Public cutover 与首个公开 release

最低交付：

1. tag / version
2. release notes
3. known limitations 摘要
4. host compatibility snapshot 摘要

---

## 4. 最小执行清单

- [ ] private `Aegis` release staging 仓已创建
- [ ] 文件去留已按 disposition 文档筛选
- [ ] 去本机化清理已完成
- [x] 公开入口文档已完成第一轮统一
- [x] 治理文件与 CI 候选配置已到位
- [ ] private staging 仓环境 CI 已实跑并完成 readback
- [ ] private release smoke 已通过并写入 record
- [ ] release checklist 已跑通
- [ ] private staging 仓已切换为 public
- [ ] 首个 release 资料已准备

---

## 5. 修复轨

1. 真实根因
   - 当前开发仓、private staging 仓与未来公开发行主仓的内容边界尚未被执行层面固化
2. 唯一 canonical owner
   - 本文档
3. 最小必要改动
   - 只新增 cutover 执行顺序与 stop conditions
4. 兼容边界
   - 不改变当前 method-pack baseline
   - 不直接触发 public cutover
5. 验证方式
   - 后续公开仓整理时按本表逐项对照

---

## 6. 退役轨

1. 当前旧 owner / 旧 fallback / 历史补丁在哪里
   - 分散在会话结论、release 讨论与文件去留策略说明中
2. 是否仍在主链生效
   - 不应继续只停留在会话级
3. 默认操作
   - 收敛为单一 cutover checklist owner
4. 暂不删除的唯一理由
   - 其它文档仍承载范围与策略信息，但不承载执行顺序
5. 验证
   - cutover 执行时，以本文档为动作顺序 owner，不再依赖零散会话说明

---

## 7. Architecture Review

执行公开仓 cutover 时必须持续检查：

1. 是否仍保持 `Method Pack` 边界
2. 是否仍保持 plugin-installable 属性
3. 是否避免把开发仓迁移输入误抬成公开仓 current authority
4. 是否把“已验证主链”与“未来目标宿主”区分清楚
5. 是否把 private staging 权限路径与 public 用户安装路径区分清楚
