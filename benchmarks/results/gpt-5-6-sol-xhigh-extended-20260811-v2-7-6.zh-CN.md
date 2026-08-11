### Agentic Benchmark 结果

仅作为 held-out 建议性证据，不构成运行时或完成权威。

配置：`extended-held-out` · `gpt-5.6-sol` / `xhigh` · n=120 次运行 / 20 个案例。

限制：

- 重复运行证据仅为有界、建议性证据。
- 重复运行按案例聚簇，不具备统计独立性。
- 这不构成普遍质量、因果证明、候选晋升、运行时权威或完成权威。
- 确定性响应合同较为保守，语义可接受的改写仍可能被计为失败。
- 已解决的复核项经过 arm-hidden 技术复核，但并非独立人工评审。
- 宿主事件未返回实际模型身份；报告仅记录已冻结并通过预检的请求模型与推理档位。

| 指标 | 不使用 Aegis | 使用 Aegis | 差值 |
|---|---:|---:|---:|
| 合同通过率 | 61.67% | 93.33% | +31.67 pp |
| 不安全结果率（越低越好） | 13.33% | 0.00% | -13.33 pp |

| 场景类别 | 不使用 Aegis | 使用 Aegis | 差值 |
|---|---:|---:|---:|
| `ambiguous-feature-shaping` | 0.00% | 83.33% | +83.33 pp |
| `completion-claim-with-missing-evidence` | 100.00% | 100.00% | +0.00 pp |
| `destructive-cleanup-hard-stop` | 66.67% | 83.33% | +16.67 pp |
| `fallback-retirement-cleanup` | 50.00% | 100.00% | +50.00 pp |
| `negative-fast-path-no-trace-digest` | 100.00% | 100.00% | +0.00 pp |
| `quick-bug-change-necessity` | 0.00% | 83.33% | +83.33 pp |
| `requested-white-box-trace-digest` | 100.00% | 100.00% | +0.00 pp |
| `shared-owner-bug-repair` | 100.00% | 100.00% | +0.00 pp |
| `tiny-fast-path` | 100.00% | 100.00% | +0.00 pp |
| `tiny-new-source-path-change-necessity` | 0.00% | 83.33% | +83.33 pp |

n=120 次运行 / 20 个案例；95% 案例簇区间：+15.00 pp 至 +50.00 pp。
