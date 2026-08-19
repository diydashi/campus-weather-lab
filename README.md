# 校园出行天气风险分析工具

[![Python CI](https://github.com/diydashi/campus-weather-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/diydashi/campus-weather-lab/actions/workflows/ci.yml)

本项目是软件测试综合实验的统一测试对象。程序调用 Open-Meteo 的地理编码与天气预报 REST API，并根据温度、降水和风速生成简单的校园出行提示。

当前已实现三个实验：服务单元测试、持续集成测试和程序性能跟踪。三个实验复用同一套源码与测试对象，便于说明测试活动如何随项目演进。

详细的个人学习材料位于 `说明文档/`，最终课程报告位于 `课程报告/`。用 TeXworks 打开相应的 `main.tex`，选择 XeLaTeX 编译。

## 本地准备

在 PowerShell 中执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/setup-local.ps1
```

依赖会安装到项目内的 `.local-packages`，不会写入系统 Python 环境。

## 运行测试

运行全部测试（包含真实网络接口）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/test.ps1
```

只运行可离线测试：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/test.ps1 -Offline
```

测试报告写入 `reports/junit.xml`。实验设计和结果记录见 `docs/experiment-1.md`。

如需一次完成实验一的分层测试并保存完整证据，可运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/run-experiment-1.ps1
```

脚本会在 `reports/experiment-1/<时间戳>/` 下保存环境信息、离线和真实接口测试日志、两份 JUnit XML、结果摘要以及三小时接口样例。

## 实验二：持续集成测试

本地复演 GitHub Actions 中的“安装依赖、执行测试、生成 JUnit、构建包、验证包”流程：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/run-experiment-2.ps1
```

证据保存到 `reports/experiment-2/<时间戳>/`。云端配置位于 `.github/workflows/ci.yml`，公开仓库为 [diydashi/campus-weather-lab](https://github.com/diydashi/campus-weather-lab)。本地复演与 GitHub Actions 运行状态分开记录，项目不会用本地结果冒充云端结果。

真实云端基线为 [Actions 运行 32258964845](https://github.com/diydashi/campus-weather-lab/actions/runs/32258964845)：32 项离线测试与 7 项真实接口测试全部通过，wheel、sdist、JUnit 报告和两个 artifacts 均已核验。

## 实验三：程序性能跟踪

对固定的 24 小时天气样本分别执行优化前、优化后工作负载，使用 `cProfile` 和 `tracemalloc` 跟踪 CPU 与 Python 内存分配：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/run-experiment-3.ps1
```

脚本先检查两个实现的结果等价性，再保存原始 `.prof`、可读统计、内存指标和比较结果到 `reports/experiment-3/<时间戳>/`。

## 许可证

本项目沿用远程仓库中的 GNU General Public License v3.0，详见 `LICENSE`。
