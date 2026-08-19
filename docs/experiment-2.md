# 实验二：持续集成测试记录

## 目标与对象

在实验一的 Python 项目上建立持续集成配置，使每次推送和拉取请求都能自动安装依赖、执行离线与真实接口测试、生成 JUnit XML、构建 wheel 与源码包，并保存报告和分发包。

## 风险与设计

- 配置文件语法或步骤缺失：新增离线配置测试，检查工作流包含测试、JUnit、构建和制品上传步骤。
- 网络波动导致错误归因：离线测试与 `network` 测试分别执行并生成不同 JUnit 文件。
- 测试通过但软件包不可用：构建后检查 wheel 与 sdist 是否存在，并检查核心模块是否被打包。
- 证据随终端输出丢失：保存 JUnit、测试日志、构建日志、环境信息和制品摘要。
- 云端结果被误写为本地结果：本地复演与 GitHub Actions 运行状态分开记录。

## 关键配置

- 工作流：`.github/workflows/ci.yml`
- 开发依赖：`requirements-dev.txt`
- 本地复演：`scripts/run-experiment-2.ps1`
- 分发包检查：`scripts/verify_distribution.py`
- 配置自检：`tests/test_project_configuration.py`

GitHub Actions 在 `push`、`pull_request` 和手动触发时运行。测试报告使用 `actions/upload-artifact@v4` 保存，构建使用 PyPA `build` 前端生成 wheel 与 sdist。

## 实际执行

执行命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/run-experiment-2.ps1
```

结果基线：`reports/experiment-2/20260819-175707/`

- Python 3.13.7；pytest 8.4.1；build 1.5.0。
- 共执行 39 项测试，39 passed，0 failed，耗时 8.397 秒。
- 成功生成 `campus_weather_lab-0.1.0-py3-none-any.whl` 和 `campus_weather_lab-0.1.0.tar.gz`。
- wheel 与 sdist 的核心源码检查通过；SHA-256 和大小保存在 `artifacts.txt`。
- GitHub 云端运行：未执行。原因是工作区没有配置远程仓库或 GitHub 账户连接。

## 结论

持续集成所需配置、测试、自动打包和本地可复验证据已经完成。当前结论只证明工作流关键命令能在本地成功执行，不等价于一次 GitHub 托管运行。提交前应把项目推送到个人仓库，在 Actions 页面手动或通过推送触发，并把真实运行页截图补入最终报告。

## 建议截图

1. GitHub 仓库中 `.github/workflows/ci.yml` 文件页面。
2. Actions 中绿色的 `test-and-build` 作业详情，显示测试、构建和上传制品步骤。
3. 作业页面的 Artifacts 区域，显示 `pytest-reports` 与 `python-distributions`。
4. 本地 `summary.txt`，用于与云端结果交叉验证。
