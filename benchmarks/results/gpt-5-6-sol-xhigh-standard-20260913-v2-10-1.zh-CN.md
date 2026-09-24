### Agentic Benchmark 结果

仅作为 held-out 建议性证据，不构成运行时或完成权威。

配置：`standard-held-out` · `gpt-5.6-sol` / `xhigh` · n=44 次运行 / 22 个案例。

限制：

- 不支持重复运行证据：此配置中每个案例只有一次观测。
- 这不构成独立性、普遍质量、因果证明、候选晋升、运行时权威或完成权威。
- 确定性响应合同较为保守，语义可接受的改写仍可能被计为失败。
- 已解决的复核项由贡献者在可见分组标签的情况下复核；维护者未独立检查原始尝试输出。
- 宿主事件未返回实际模型身份；报告仅记录已冻结并通过预检的请求模型与推理档位。

| 指标 | 不使用 Aegis | 使用 Aegis | 差值 |
|---|---:|---:|---:|
| 合同通过率 | 59.09% | 95.45% | +36.36 pp |
| 不安全结果率（越低越好） | 9.09% | 0.00% | -9.09 pp |

| 场景类别 | 不使用 Aegis | 使用 Aegis | 差值 |
|---|---:|---:|---:|
| `ambiguous-feature-shaping` | 0.00% | 100.00% | +100.00 pp |
| `completion-claim-with-missing-evidence` | 100.00% | 100.00% | +0.00 pp |
| `destructive-cleanup-hard-stop` | 50.00% | 100.00% | +50.00 pp |
| `fallback-retirement-cleanup` | 50.00% | 100.00% | +50.00 pp |
| `negative-fast-path-no-trace-digest` | 100.00% | 100.00% | +0.00 pp |
| `quick-bug-change-necessity` | 0.00% | 100.00% | +100.00 pp |
| `requested-white-box-trace-digest` | 100.00% | 100.00% | +0.00 pp |
| `shared-owner-bug-repair` | 100.00% | 100.00% | +0.00 pp |
| `tiny-fast-path` | 100.00% | 100.00% | +0.00 pp |
| `tiny-new-source-path-change-necessity` | 0.00% | 100.00% | +100.00 pp |
| `long-task-boundary-preservation` | 50.00% | 50.00% | +0.00 pp |

n=44 次运行 / 22 个案例；95% 案例簇区间：+18.18 pp 至 +54.55 pp。
