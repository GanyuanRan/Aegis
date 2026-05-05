# Aegis Public Repo File Disposition

状态：`Reviewed`

## 1. 文档定位

本文档定义 `Aegis Method Pack` 建立独立公开仓时的文件去留策略。

本文档回答以下问题：

1. 哪些文件应直接进入公开仓
2. 哪些文件应迁移到公开仓但需要重写或去本机化
3. 哪些文件应保留在开发仓或归档，而不应进入公开主叙事

本文档不负责：

- 替代 release checklist
- 替代实际 git 操作
- 授予最终开源发布 authority

---

## 2. 使用规则

本文档中的文件处理分为四类：

1. `保留`
   - 直接进入公开仓
2. `迁移后保留`
   - 需要重写、去本机化、去私有化后进入公开仓
3. `归档`
   - 可进入公开仓，但只能作为 historical / migration inputs
4. `仅开发仓保留`
   - 保留在当前开发仓，不进入公开发行主仓

对于“仍需本地保留、但不应进入公开发行主仓”的内容，默认优先使用：

- `.local/`

具体策略见：

- `docs/current/AEGIS_LOCAL_ONLY_OVERLAY_POLICY.md`

---

## 3. 根目录文件去留清单

| 路径 | 处理 | 说明 |
| --- | --- | --- |
| `README.md` | `迁移后保留` | 已完成第一轮独立 `Aegis Method Pack` 公开首页重写；cutover 前仍需最终 readback |
| `README.zh-CN.md` | `保留` | 根目录中文公开首页；需与 `README.md` 保持 scope boundary 一致 |
| `LICENSE` | `保留` | 当前 MIT 许可可继续保留，但公开仓应补充 fork/致谢说明 |
| `CODE_OF_CONDUCT.md` | `保留` | 公开仓 community profile 基础文件 |
| `RELEASE-NOTES.md` | `迁移后保留` | 应改成适配新公开仓首发 release 的对外说明 |
| `.gitignore` | `保留` | 已具备较好的公开噪音屏蔽价值 |
| `package.json` | `保留` | 若仍作为分发骨架 owner，应继续保留 |
| `AGENTS.md` | `迁移后保留` | 可作为 contributor guardrail，但需确认没有只适合私有协作的内容 |
| `CLAUDE.md` | `迁移后保留` | 可保留为 host-specific contributor guidance，但需去掉只对当前 fork/上游流程有意义的局部约束 |
| `AGENTS_RULES.md` | `归档` | 属于 process mother draft，不应作为公开主入口 |
| `GEMINI.md` | `迁移后保留` | 若仍作为宿主贡献文档存在，应检查 wording 与当前 baseline 一致 |
| `gemini-extension.json` | `保留` | 若仍作为分发工件 owner，应继续保留 |

---

## 4. 目录级去留清单

| 路径 | 处理 | 说明 |
| --- | --- | --- |
| `.claude-plugin/` | `保留` | 分发骨架的一部分 |
| `.codex-plugin/` | `保留` | 分发骨架的一部分 |
| `.cursor-plugin/` | `保留` | 分发骨架的一部分 |
| `.opencode/` | `迁移后保留` | 只保留真正需要的 host integration owner；不带本地依赖与缓存 |
| `.github/` | `迁移后保留` | 保留 issue / PR 模板，并补 CI、SECURITY、community profile 相关配置 |
| `skills/` | `保留` | method-pack 核心资产 |
| `agents/` | `保留` | method-pack 组成部分 |
| `commands/` | `保留` | method-pack 组成部分 |
| `hooks/` | `保留` | method-pack 组成部分 |
| `scripts/` | `迁移后保留` | 保留公开发布仍需要的脚本，去掉只适合本机/私有流程的辅助脚本 |
| `tests/` | `迁移后保留` | 保留可复现公开质量的测试 owner；`tests/local/` 仅保留 README，实际本地开发测试默认不进入公开仓 |
| `assets/` | `保留` | 公开品牌/图标资产 |
| `docs/current/` | `保留` | 当前 authority baseline 主体 |
| `docs/adr/` | `保留` | 结构性决策 owner |
| `docs/README.codex.md` | `保留` | 对外 host 安装说明 |
| `docs/README.opencode.md` | `保留` | 对外 host 安装说明 |
| `docs/testing.md` | `保留` | 对外测试入口 |
| `docs/plans/` | `归档` | 历史计划，不应作为公开 baseline |
| upstream-specific historical design/spec subtree | `已移除` | 不作为公开仓用户可见内容，也不作为公开 baseline |
| `Aegis_Fork_Bootstrap_Pack/` | `仅开发仓保留` | 迁移输入价值高，但不适合作为公开发行主仓主内容 |

---

## 5. 需要优先去本机化的内容

以下内容在进入公开仓前应优先处理：

1. 本机绝对路径
   - 例如当前开发机上的 repo root 绝对路径
   - 例如当前开发机上的宿主工具 checkout 绝对路径
2. 只适合当前私有环境的 runner 描述
3. 仅用于本机排障的临时说明
4. 只对开发仓 lineage 有意义、但对公开用户无价值的细节

当前已知需要处理的典型位置包括：

1. `docs/current/AEGIS_PHASE5_E2E_BASELINE_RUN.md`
2. `Aegis_Fork_Bootstrap_Pack/README.md`
3. `tests/helpers/test_parse_codex_skills.py`
4. `tests/local/` 下除 README 之外的开发期测试输入与临时 case

这些位置不一定都要从公开仓删除，但至少需要：

- 去本机化
- 或转归档
- 或仅留在开发仓

---

## 6. 公开仓发布前必须核对的治理文件

以下文件当前开发仓已补齐第一轮版本。进入公开仓前仍需最终 readback，并在公开仓环境中验证 CI 可运行：

1. `CONTRIBUTING.md`
2. `SECURITY.md`
3. `SUPPORT.md`
4. `CODEOWNERS`
5. `.github/workflows/ci.yml`

这些文件的角色分别是：

- `CONTRIBUTING.md`：说明协作流程与 PR 入口
- `SECURITY.md`：说明安全问题上报路径
- `SUPPORT.md`：说明获取帮助与 issue 分流方式
- `CODEOWNERS`：明确代码审阅 owner
- `ci.yml`：建立基础公开可见验证链

stop condition：

- 若公开仓 CI 尚未实跑，不得把 `.github/workflows/ci.yml` 声明为 release-level 已验证

---

## 7. 当前推荐的公开仓最小文件包

### 7.1 必须进入公开仓

1. `README.md`
2. `README.zh-CN.md`
3. `LICENSE`
4. `CODE_OF_CONDUCT.md`
5. `CONTRIBUTING.md`
6. `SECURITY.md`
7. `SUPPORT.md`
8. `CODEOWNERS`
9. `.github/`
10. `skills/`
11. `agents/`
12. `commands/`
13. `hooks/`
14. `scripts/`
15. `tests/`
16. `assets/`
17. `docs/current/`
18. `docs/adr/`
19. `docs/README.codex.md`
20. `docs/README.opencode.md`
21. `docs/testing.md`

### 7.2 默认不进入公开发行主仓

1. `Aegis_Fork_Bootstrap_Pack/`
2. `docs/plans/`
3. upstream-specific historical design/spec subtree
4. 任何 `.tmp/`、`.serena/`、`node_modules/`、平台缓存与本机依赖产物
5. `tests/local/` 下除 `tests/local/README.md` 之外的本地开发测试 case

---

## 8. 双轨治理视角

### 8.1 修复轨

本次公开仓整理的真实目标是：

- 收敛“公开发行主仓”的最小必要文件集合

canonical owner：

- 本文档

最小必要改动：

- 只定义去留、迁移、归档规则
- 不在本文档中直接承诺具体 git 操作已执行

验证方式：

- 公开仓建仓前按本表逐项对照

### 8.2 退役轨

默认需要从公开主叙事中退役的对象包括：

1. process mother draft
2. historical plans
3. migration inputs
4. 本机路径证据
5. 临时缓存与本地依赖产物

若某对象暂时不能删除公开暴露，必须说明：

1. 为什么仍要保留
2. 是否仅作为 archive
3. 它不属于 current authority 的证据在哪里

---

## 9. Architecture Review

执行公开仓文件裁剪时必须持续检查：

1. 是否把 `Method Pack` 与 future platform 再次混回同一仓叙事
2. 是否把 migration inputs 误抬成 current authority
3. 是否保住多宿主 plugin-installable 分发骨架
4. 是否把本机验证证据错误地当成面向外部用户的稳定安装说明
