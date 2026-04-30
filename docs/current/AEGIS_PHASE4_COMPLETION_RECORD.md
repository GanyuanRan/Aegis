# Aegis Phase 4 Compatibility Review Completion Record

状态：`Reviewed`

## 1. 文档定位

本文档记录 `Aegis Phase 4 / Compatibility Review` 的实际完成情况、fresh verification 证据、修复轨 / 退役轨回望，以及当前残余风险。

本文档是阶段收口记录，不替代以下 authoritative baseline：

- `docs/current/AEGIS_TARGET_STATE.md`
- `docs/current/AEGIS_PHASE4_COMPATIBILITY_REVIEW_ATOMIC_PLAN.md`
- `docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`

---

## 2. 阶段结论

`Phase 4 / Compatibility Review` 当前可判定为：

> `Completed within approved scope`

完成范围严格限定于 `AEGIS_PHASE4_COMPATIBILITY_REVIEW_ATOMIC_PLAN.md` 允许的边界：

1. Codex 安装 / smoke / plugin sync 相关 owner 回看
2. OpenCode 安装 / plugin loading / integration smoke 相关 owner 回看
3. 与兼容性回看直接相关的最小 authority / testing supporting docs

当前没有证据显示本轮兼容性回看越过以下边界：

- future runtime core
- host adapter 正式实现
- 新宿主接入
- 与兼容性回看无直接阻断关系的全量 skill 重写

---

## 3. 事实

### 3.1 Compatibility Inventory 事实

当前阶段已把以下六类兼容性能力重新盘点并重新绑定到 canonical owners：

1. `installation`
   - Codex owner：`docs/README.codex.md`
   - OpenCode owner：`docs/README.opencode.md`
2. `skill discovery`
   - Codex owner：`tests/skill-triggering/*`、`tests/explicit-skill-requests/*`
   - OpenCode owner：`tests/opencode/test-tools.sh`
3. `priority`
   - OpenCode owner：`tests/opencode/test-priority.sh`
4. `tool mapping`
   - OpenCode owner：`docs/README.opencode.md`
5. `distribution sync`
   - Codex owner：`scripts/sync-to-codex-plugin.sh`
   - regression owner：`tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
6. `plugin-installable`
   - 当前宿主兼容 owner：`docs/README.codex.md`、`docs/README.opencode.md`、`docs/testing.md`

### 3.2 Codex 兼容性事实

- Codex 当前 lightweight host-native compatibility matrix 仍覆盖：
  - `brainstorming`
  - `systematic-debugging`
  - `verification-before-completion`
  - `writing-plans`
  - `requesting-code-review`
- Codex natural smoke fresh pass：
  - `Passed: 5`
  - `Failed: 0`
- Codex explicit smoke fresh pass：
  - `Passed: 5`
  - `Failed: 0`
  - `Total: 5`
- Codex plugin sync dry-run regression fresh pass
- 本轮还识别并收敛了一个真实自然样本漂移：
  - `brainstorming` 自然样本中的 `implementation plan` 表述会把 Codex 路由到 `writing-plans`
  - 收敛自然样本后，fresh rerun 恢复到 `brainstorming`

### 3.3 OpenCode 兼容性事实

- OpenCode plugin loading regression fresh pass
- OpenCode integration suite 当前已显式区分三种状态：
  - `opencode` 不存在
  - `opencode` 存在但本机不可运行
  - `opencode` 真正可运行
- 后续 fresh re-check 进一步确认：
  - `PowerShell` / `cmd` 下 `opencode --version` 返回 `1.14.26`
  - `opencode run --pure --model opencode/big-pickle --print-logs "hello"` 可返回真实响应
  - Windows CLI 桥接修复后，`bash/WSL` 链路也能稳定走到真实 OpenCode runtime
- OpenCode 兼容性回归在当前机器上已完成真正 integration closeout：
  - `test-plugin-loading.sh` 通过
  - `test-tools.sh` 通过
  - `test-priority.sh` 通过
  - `bash tests/opencode/run-tests.sh --integration` => `Passed: 3`, `Failed: 0`, `Skipped: 0`
- 兼容性语义也已收敛到当前宿主真实契约：
  - 使用 OpenCode 原生 `skill` 工具，而不是旧设计稿里的 `find_skills` / `use_skill` 心智模型
  - 以 skill scope visibility 为断言面，而不是未承诺的 duplicate-name override
  - 参考 OpenCode 官方 skills 文档：skill 名需在不同 location 间保持唯一；project-local skills 由当前工作目录向上走到 git worktree 进行发现

### 3.4 Supporting docs / owner 事实

- `docs/testing.md` 已补齐：
  - Codex lightweight smoke matrix 说明
  - OpenCode base suite / integration suite 的双层验证说明
  - `opencode --version` 作为 runnable probe 的边界说明
- `docs/README.opencode.md` 已补齐：
  - `opencode --version` 作为 integration 前置检查
  - “binary 在 PATH 上但不可运行”时的 troubleshooting 说明
- 本轮 closeout 发布时：
  - `AGENTS.md`、`docs/current/README.md`、`docs/current/AEGIS_TRANSFORMATION_EXECUTION_PLAN.md`
    已被要求对齐到 `Phase 4 complete`
  - 后续 `Phase 5` 是否激活，应以当时的 current authority docs 为准，而不是以本收口记录中的阶段快照为准

### 3.5 分发边界事实

- 当前没有为通过兼容性回看而引入任何宿主专有 runtime 依赖
- 当前仍保留 `superpowers` 原有 plugin-installable 分发骨架
- 当前仍符合 `Aegis Method Pack (runtime-ready)` 边界，没有越权承担 runtime authority

---

## 4. 证据

### 4.1 Fresh verification commands

2026-04-27 本轮 fresh verification 运行命令如下：

```bash
bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh'
bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh'
bash tests/opencode/run-tests.sh
bash tests/opencode/run-tests.sh --integration
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

### 4.2 Fresh verification results

- `bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh'`
  - `Passed: 5`
  - `Failed: 0`
- `bash -lc 'SUPERPOWERS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh'`
  - `Passed: 5`
  - `Failed: 0`
  - `Total: 5`
- `bash tests/opencode/run-tests.sh`
  - `STATUS: PASSED`
- `bash tests/opencode/run-tests.sh --integration`
  - `Passed: 3`
  - `Failed: 0`
  - `Skipped: 0`
  - `STATUS: PASSED`
- `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
  - `PASS`

### 4.3 中途诊断证据

本轮兼容性回看还识别并收敛了两个真实问题：

1. OpenCode integration tests 原先只检查 `command -v opencode`
   - 现象：CLI 在 PATH 上，但 `opencode --version` 直接报平台包错误
   - 结论：原 tests 把环境 blocker 误判成产品失败
   - 处理：新增 runnable probe，并把 blocker 改为显式 `skip`
2. 后续 fresh re-check 发现 Windows shell 下 `opencode --version` 与真实 `run` 已恢复正常
   - 现象：`PowerShell` / `cmd` 下版本检查通过，`opencode/big-pickle` 可返回真实响应
   - 结论：OpenCode runtime blocker 已关闭，可进入真正 integration closeout
   - 处理：为 `tests/opencode` 增加 Windows CLI bridge、runtime readiness probe，并把默认模型切换为当前机器可用的 `opencode/big-pickle`
3. OpenCode tools / priority tests 仍沿用旧设计稿里的 `find_skills` / `use_skill` 与 duplicate-name override 假设
   - 现象：当前 OpenCode 宿主真实暴露的是原生 `skill` 工具；重复 skill 名跨 scope 行为不稳定
   - 根因：测试 owner 仍绑在早期设计稿，而不是当前宿主正式文档与真实 runtime 行为
   - 处理：把 `tests/opencode/test-tools.sh` 收敛到 native `skill` discovery / load，把 `tests/opencode/test-priority.sh` 收敛到 scope visibility；同时在 `docs/README.opencode.md` / `docs/testing.md` 写明“skill names must be unique across locations”
4. `brainstorming` Codex 自然样本在最新 fresh run 中真实失败一次
   - 现象：Codex 读取 `using-superpowers` 后转向 `writing-plans`
   - 根因：提示词把“设计讨论”和“implementation plan”放在同一自然请求里
   - 处理：收窄自然样本，只保留 design discussion + recommendation，fresh rerun 通过

### 4.4 Fresh artifact paths

- Codex natural smoke artifacts：
  - `.tmp/superpowers-tests/1777222201/skill-triggering/brainstorming/`
  - `.tmp/superpowers-tests/1777222339/skill-triggering/systematic-debugging/`
  - `.tmp/superpowers-tests/1777222647/skill-triggering/verification-before-completion/`
  - `.tmp/superpowers-tests/1777222954/skill-triggering/writing-plans/`
  - `.tmp/superpowers-tests/1777223063/skill-triggering/requesting-code-review/`
- Codex explicit smoke artifacts：
  - `.tmp/superpowers-tests/1777222201/explicit-skill-requests/systematic-debugging/`
  - `.tmp/superpowers-tests/1777222500/explicit-skill-requests/brainstorming/`
  - `.tmp/superpowers-tests/1777222648/explicit-skill-requests/verification-before-completion/`
  - `.tmp/superpowers-tests/1777222710/explicit-skill-requests/writing-plans/`
  - `.tmp/superpowers-tests/1777223017/explicit-skill-requests/requesting-code-review/`

---

## 5. 实施摘要

### Slice 1：Compatibility Inventory 与 baseline readback

已完成：

- 兼容能力六类 inventory 盘点
- baseline / requirement / target-state 回读
- 当前兼容性 owner 收敛

### Slice 2：Codex compatibility 回看

已完成：

- Codex natural smoke matrix fresh rerun
- Codex explicit smoke matrix fresh rerun
- Codex natural `brainstorming` 样本收敛
- Codex plugin sync dry-run regression fresh rerun

### Slice 3：OpenCode compatibility 回看

已完成：

- OpenCode plugin loading regression fresh rerun
- OpenCode integration preflight 由“binary 存在”收敛到“CLI 可运行 + runtime 可回答”
- OpenCode native `skill` discovery / load 行为回归 fresh pass
- OpenCode skill scope visibility 回归 fresh pass

### Slice 4：Authority / docs / test matrix 收口

已完成：

- `docs/testing.md` compatibility matrix 收口
- `docs/README.opencode.md` runnable probe / blocker 说明收口
- `Phase 4` 完成记录与阶段状态更新

---

## 6. 修复轨回望

### 6.1 根因

- `Phase 4` 启动前，兼容性结论仍分散在 completion records、host README 与 shell 输出中
- OpenCode integration owner 把“命令存在”误当作“CLI 可运行”
- Codex `brainstorming` 自然样本把 design discussion 与 implementation plan 语义混在一起，触发了错误 skill 路由

### 6.2 Canonical owners

- `tests/opencode/setup.sh`
- `tests/opencode/run-tests.sh`
- `tests/opencode/test-tools.sh`
- `tests/opencode/test-priority.sh`
- `docs/testing.md`
- `docs/README.opencode.md`
- `tests/skill-triggering/prompts/brainstorming.txt`
- `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`

### 6.3 最小必要改动

- 只修改 OpenCode integration preflight / skip 语义
- 只修改与当前回归直接相关的 `brainstorming` 自然样本
- 只把已证据化的兼容性结论回写到最小 supporting docs 和 completion record

### 6.4 兼容边界

- 保留 `superpowers` 原有多宿主分发骨架
- 不为了某个宿主的本机体验去重写 method-pack baseline
- 不把环境 blocker 伪装成产品能力通过
- 不把 lightweight smoke 误表述为 authoritative completion

### 6.5 验证方式

- Codex natural smoke
- Codex explicit smoke
- OpenCode plugin loading
- OpenCode integration preflight + blocker skip
- Codex plugin sync dry-run regression

---

## 7. 退役轨回望

### 7.1 已收敛的旧逻辑 / 旧表述

- OpenCode integration tests 中“只检查 `command -v opencode`”的旧判定已不再作为通过前提
- OpenCode 早期设计稿中的 `find_skills` / `use_skill` 自定义工具假设已不再作为当前兼容性基线
- OpenCode duplicate-name override 期待已从 hard assertion 退役为显式非契约说明
- `brainstorming` 自然样本中把设计讨论直接推向 implementation plan 的旧措辞已不再作为当前 compatibility review 触发表述

### 7.2 仍保留但已降级为兼容辅助

- Codex explicit smoke 的 `premature action` warning 仍保留
  - 当前作用：提示 transcript 中 skill 可见性与动作时序仍有灰区
  - 当前不是阻断条件
- OpenCode integration tests 在 CLI 不可运行时仍会执行 fixture setup
  - 当前作用：保留本地结构性前置检查
  - 当前不是产品失败信号

### 7.3 暂未删除的旧逻辑 / 原因

- Codex smoke transcript parser 仍基于文本模式提取 skill load
  - 保留原因：当前 Codex CLI 没有更权威的结构化 skill invocation transcript
  - 观察指标：文本 transcript 形态是否继续稳定
  - 退役时机：若 Codex 提供结构化 skill load 证据，可替换现有 grep/parser helper

### 7.4 后续退役触发条件

- OpenCode runtime blocker 已在本轮退役为“已验证通过”
- 若未来进入 `Phase 5` 并形成更统一的 host compatibility reporting，可收敛当前 completion record 与 testing docs 中的阶段性说明

---

## 8. Reflection 回望

### Goal

Phase 4 原定目标已满足：

- compatibility inventory 已形成
- Codex 安装 / smoke / plugin sync 结论已统一
- OpenCode 安装 / plugin loading / integration 入口结论已统一
- integration 未通过之处已被收敛为可验证的环境 blocker，而不是漂浮结论
- authority docs 与 testing docs 不再对当前兼容性状态给出冲突表述

### DeeperCause

`No`

理由：

- 本轮 deepest issue 不在 method-pack baseline，而在 host compatibility evidence 的判定边界
- OpenCode 侧 deeper issue 已收敛到本机 CLI 平台包错误，不是仓库逻辑 owner 错置
- Codex 侧 deeper issue 已收敛到自然样本路由语义，不是 method-pack 架构越权

### Evidence

- 见本文第 4 节 fresh verification commands / results
- 见 `tests/opencode/*`、`docs/testing.md`、`docs/README.opencode.md` 的本轮最小改动
- 见 `.tmp/superpowers-tests/1777222201/`、`.tmp/superpowers-tests/1777222500/`、`.tmp/superpowers-tests/1777223063/`

### Risk / Unknown

- OpenCode duplicate-name override 仍不应被当作稳定契约；当前只验证官方文档与真实 runtime 共同支持的 scope visibility 语义
- Codex explicit smoke 仍会提示 `premature action` warning
- 当前 Codex / OpenCode 证据仍属于 lightweight host-native compatibility matrix，不等价于未来 runtime core 级别验证

### Decision

`exit`

---

## 9. 置信度

`A-`

理由：

- Codex matrix、OpenCode plugin loading、Codex plugin sync 均来自 fresh command output
- OpenCode integration 已在当前机器上完成真实 3/3 pass，而不是 blocker skip
- 剩余风险已从“runtime 是否可用”收敛为“哪些宿主语义属于正式契约、哪些只是 host-defined”

---

## 10. 架构回望

本轮没有发现新的结构性缺陷，但确认了三条重要架构纪律：

1. host compatibility tests 必须区分“宿主安装存在”与“宿主 runtime 可用”
2. 自然触发样本必须服从当前 active slice 边界，不能把 design / planning 两条 workflow 混成一个 prompt
3. compatibility review 的结论必须回写到 authority / testing owners，不能长期漂在 completion record 和 shell 输出之外

当前架构仍符合以下方向：

- 方法层增强
- authority boundary 清晰
- 插件可安装能力保留
- 宿主无关分发模型保留

未观察到以下漂移：

- method-pack 向 runtime core 越权
- host-specific logic 反向抬升为 baseline
- 为治理增强而破坏 plugin-installable 属性

---

## 11. 进入 Phase 5 的证据基线

Phase 4 当前结论为 `Completed within approved scope`，置信度保持为 `A-`。

如果用户考虑进入 `Phase 5 / Runtime-ready Hardening`，本收口记录可直接作为进入下一阶段的证据基线。

### 11.1 硬性条件（当前均已满足）

1. Phase 4 已按 approved scope 完成收口，不存在未完成的承诺任务
2. Codex natural smoke + explicit smoke + plugin sync 三轮验证均 fresh pass
3. OpenCode plugin loading + base suite + integration suite 已在当前机器上完成真实 fresh pass
4. 当前没有 evidence 显示 Phase 4 改造出现 authority drift 或 host-specific 反向污染
5. OpenCode 兼容性断言面已收敛到当前宿主真实契约，而不是早期设计稿假设

### 11.2 仍需带入 Phase 5 的残余风险

- OpenCode duplicate-name override 不应被当作稳定契约；当前只验证官方文档与真实 runtime 共同支持的 scope visibility 语义
- Codex explicit smoke 仍存在 `premature action` warning，不阻断但需关注
- 当前 Codex / OpenCode 证据仍属于 lightweight host-native compatibility matrix，不等价于 future runtime core 级别验证

### 11.3 建议

当前更合理的做法不是重复回到 `Phase 4`，而是把本收口记录作为 Phase 5 的输入基线，优先建设统一的 E2E 验收框架与分层验证入口。

---

## 12. 影响面

### 功能

- 仅影响 host compatibility smoke / integration 判定与对应说明文档

### 数据

- 无业务数据结构变更

### 性能

- 无 runtime path 性能影响
- 仅增加更精确的 integration preflight 和更稳定的自然样本触发

### 安全 / 合规

- 无新增敏感权限
- 无新增外部依赖
- 无新增 authority 越权路径
