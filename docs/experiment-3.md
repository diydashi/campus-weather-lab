# 实验三：程序性能跟踪记录

## 目标与对象

使用 Python 标准库 `cProfile` 和 `tracemalloc` 分析校园天气风险批处理工作负载的 CPU 时间与 Python 对象分配峰值，定位瓶颈并验证改进效果。

固定输入为 `data/sample_weather.json`，包含 24 条逐小时记录。每次性能运行处理 10,000 轮，即 240,000 个事件，避免把真实 API 网络延迟混入本地算法性能。

## 对照实现

- 基线实现：每轮重新解析时间、重新排序，并把全部事件结果保存在大列表中。
- 优化实现：只预处理和排序一次，循环中使用累计值，不保留大中间列表。

优化前后都调用相同的 `assess_hour` 风险规则。比较脚本首先要求 `event_count`、`time_checksum` 和 `risk_score` 完全相同，否则不接受性能结论。

## 实际执行

执行命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/run-experiment-3.ps1
```

结果基线：`reports/experiment-3/20260819-175557/`

| 指标 | 基线 | 优化后 | 解释 |
|---|---:|---:|---|
| `tracemalloc` 同步测量时间 | 0.7499 s | 0.4507 s | 优化后约 1.664 倍 |
| 时间减少比例 | - | 39.90% | 同一固定输入与轮数 |
| Python 分配峰值 | 21,573,080 B | 2,840 B | 减少约 99.987% |
| CPU profiler 总调用数 | 2,875,977 | 1,426,022 | 减少约 50.4% |
| cProfile 内的工作负载累计时间 | 0.478 s | 0.245 s | 独立 CPU 跟踪也支持改进有效 |

两个版本均得到：`event_count=240000`、`time_checksum=165600000`、`risk_score=620000`。

## 瓶颈与解释

基线 CPU 统计中，`baseline_workload` 累计约 0.478 秒；`sum`、`_risk_score`、`sorted`、`assess_hour`、排序 lambda 和 `datetime.fromisoformat` 是主要热点。基线调用 `fromisoformat` 480,000 次，反映时间字符串在每轮被重复解析。优化后准备工作只执行一次，总调用数下降，工作负载累计时间约减半。

内存峰值大幅下降的根本原因不是换了测量工具，而是消除了包含 240,000 个元组的 `events` 列表。优化实现只维护三个整数累计值和 24 条预处理记录。

## 结果边界

- `tracemalloc` 统计 Python 跟踪到的内存分配，不等于操作系统看到的进程 RSS。
- 性能数字会随处理器、Python 版本和系统负载变化，因此应关注相对趋势和热点，不把单次小数位当作绝对结论。
- `cProfile` 和 `tracemalloc` 都会引入额外开销；本实验使用同条件对照，并保留原始 `.prof` 供复查。

## 结论

通过“先保证结果等价，再比较资源开销”，实验定位了重复日期解析、重复排序和大中间列表三类问题。优化后 CPU 跟踪与内存跟踪均显示明显改善，满足课程对 CPU 瓶颈、内存瓶颈和改进方案分析的要求。
