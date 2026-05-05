# Aegis Private Release Smoke Test Record

状态：`Draft`

## 1. 文档定位

本文档记录 private `Aegis` release staging 仓的真实安装与基础可用性冒烟结果。

本文档不预设通过结论；只有实际执行后才能填写 `Pass / Fail / Blocked`。

---

## 2. 测试摘要

| 字段 | 结果 |
| --- | --- |
| 测试日期 | `TBD` |
| 测试机器 | `TBD` |
| 操作系统 | `TBD` |
| private repo URL | `private Aegis staging repository` |
| private staging commit | `current staging HEAD at precheck time` |
| 测试人 | `TBD` |
| 总体结论 | `Not run` |

### 2.1 本机预检证据

本节只记录当前开发机上的 pre-release checks，不等价于 private release smoke。

Private staging 发布事实：

- 发布目录：`local release-staging checkout`
- 推送目标：`private Aegis staging repository`
- 推送分支：`main`
- 远端 HEAD：`current staging HEAD at precheck time`
- 发布包排除：`.tmp/`、`.serena/`、`.local/`、`Aegis_Fork_Bootstrap_Pack/`、`docs/plans/`、`AGENTS_RULES.md`

已执行并通过：

1. `git diff --check`
2. `node --check .opencode/plugins/aegis.js`
3. JSON parse:
   - `package.json`
   - `gemini-extension.json`
   - `.codex-plugin/plugin.json`
   - `.claude-plugin/plugin.json`
   - `.cursor-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
4. `bash tests/opencode/run-tests.sh`
5. `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
6. `bash tests/e2e/boundary-compliance-check.sh`
7. `bash tests/e2e/run-all.sh --full --host-profile none`
8. `bash tests/e2e/run-all.sh --full --host-profile fast`
9. `python tests/helpers/test_parse_codex_skills.py`

补充说明：

- `python -m unittest tests.helpers.test_parse_codex_skills` 在当前仓库结构下失败，原因是 `tests/` 未作为 Python package 暴露。
- 同一测试文件通过 `python tests/helpers/test_parse_codex_skills.py` 执行成功，因此当前记录不将其判定为解析逻辑失败。
- 第二机器 private repo 安装、真实 Codex 安装、真实 OpenCode 安装仍未执行。

---

## 3. 环境记录

| 对象 | 版本 / 状态 | 证据 |
| --- | --- | --- |
| Git | `TBD` | `TBD` |
| Codex | `TBD` | `TBD` |
| OpenCode | `TBD` | `TBD` |
| Node / Bun / Shell | `TBD` | `TBD` |
| private repo auth | `TBD` | 不记录 token 或私有凭据 |

---

## 4. Smoke A：仓库安装路径

### 4.1 OpenCode

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| 推荐安装入口可执行 | `Not run` | `TBD` |
| Aegis plugin 可加载 | `Not run` | `TBD` |
| skills 可被发现 | `Not run` | `TBD` |
| 安装标识已使用 Aegis 口径 | `Not run` | `TBD` |

结论：`Not run`

### 4.2 Codex

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| 推荐安装入口可执行 | `Not run` | `TBD` |
| skills 可被发现 | `Not run` | `TBD` |
| `using-aegis` / Aegis bootstrap 可触发 | `Not run` | `TBD` |
| 安装标识已使用 Aegis 口径 | `Not run` | `TBD` |

结论：`Not run`

---

## 5. Smoke B：技能触发路径

| Skill | 结果 | 证据 | 备注 |
| --- | --- | --- | --- |
| `brainstorming` | `Not run` | `TBD` | `TBD` |
| `systematic-debugging` | `Not run` | `TBD` | `TBD` |
| `verification-before-completion` | `Not run` | `TBD` | `TBD` |

结论：`Not run`

---

## 6. Smoke C：小型真实任务

任务描述：

- `TBD`

验收点：

1. 有事实 / 证据 / 边界说明
2. 有最小必要改动或明确不改动理由
3. 有验证命令、readback 或人工检查证据
4. 有 architecture review
5. 人工确认后再进入下一步

结果：`Not run`

证据：

- `TBD`

---

## 7. 发现的问题

| 编号 | 问题 | 严重度 | owner | 处理状态 |
| --- | --- | --- | --- | --- |
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

---

## 8. Known Limitations 回写

| 限制 | 是否已回写 | 文件 |
| --- | --- | --- |
| `TBD` | `No` | `docs/current/AEGIS_KNOWN_LIMITATIONS.md` |

---

## 9. 修复轨

1. 真实根因
   - `TBD`
2. 唯一 canonical owner
   - `TBD`
3. 最小必要改动
   - `TBD`
4. 兼容边界
   - `TBD`
5. 验证方式
   - `TBD`

---

## 10. 退役轨

1. 旧对象在哪里
   - `TBD`
2. 是否仍在主链生效
   - `TBD`
3. 默认操作
   - `TBD`
4. 保留理由
   - `TBD`
5. 退役触发条件
   - `TBD`

---

## 11. Architecture Review

| 检查项 | 结论 | 证据 |
| --- | --- | --- |
| 是否仍只验证 Method Pack | `TBD` | `TBD` |
| 是否保留 plugin-installable 属性 | `TBD` | `TBD` |
| 是否区分 private 权限限制与 public 安装路径 | `TBD` | `TBD` |
| 是否避免 Aegis 自授最终完成权 | `TBD` | `TBD` |

总体决策：

- `Not run`
