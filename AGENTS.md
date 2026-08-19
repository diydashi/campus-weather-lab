# 校园出行天气风险分析工具协作指南

## 项目目标

- 以同一个 Python 项目完成服务单元测试、持续集成测试和程序性能跟踪。
- 优先满足软件测试综合实验的必备要求，保持实现简单、可解释、可复现。
- 对测试和性能结论保留真实证据，不用本地结果冒充云端结果，不编造截图或运行状态。

## 结构与边界

- `src/campus_weather/`：Open-Meteo 客户端和确定性风险规则。
- `tests/`：离线单元测试、真实接口测试、配置检查和性能等价性测试。
- `.github/workflows/ci.yml`：GitHub Actions 测试与构建流水线。
- `benchmarks/`、`data/`：固定输入的 CPU/内存性能工作负载。
- `docs/`：三个实验的简要设计与结果记录。
- `说明文档/`：面向个人学习的中文 LaTeX 说明。
- `课程报告/`：最终课程报告 LaTeX 源稿。
- `reports/`、`dist/`、`.local-packages/` 和 LaTeX 编译产物属于本地证据或生成文件，不提交 Git。

## 开发与测试规范

- 支持 Python 3.11 及以上版本，源码采用 UTF-8 和 `src/` 布局。
- 公共函数写类型标注和简短 docstring；HTTP 请求必须设置超时。
- 真实天气测试只断言协议、结构、范围和不变量，不断言会随时间变化的具体数值。
- 网络测试使用 `network` 标记，离线测试应在无网络环境下通过。
- 性能优化必须先证明功能结果等价；性能数字需注明环境、输入、轮数和测量边界。
- 修改行为时同步更新测试、`docs/`、学习说明和必要的报告内容。

## 常用命令

```powershell
./scripts/setup-local.ps1
./scripts/test.ps1 -Offline
./scripts/run-experiment-1.ps1
./scripts/run-experiment-2.ps1
./scripts/run-experiment-3.ps1
```

## 文档与证据

- 文档按“风险 → 测试设计 → 执行 → 结果 → 分析”组织。
- 大语言模型的 prompt 与回答摘要记录在 `AI_USAGE.md`。
- 课程报告中的 GitHub Actions 状态、提交号和运行链接必须来自真实远程运行。
- 公开仓库不得写入姓名、完整学号、令牌、Cookie 或其它个人凭据。
