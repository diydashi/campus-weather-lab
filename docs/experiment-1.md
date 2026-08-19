# 实验一：REST 服务单元测试

## 1. 测试对象

项目测试 Open-Meteo 的两个公开 REST API：

1. 地理编码接口：输入城市名称，返回候选城市及经纬度。
2. 天气预报接口：输入经纬度和预测天数，返回逐小时温度、降水概率与风速。

选择它们是因为校园天气提示依赖“城市解析 → 天气查询”这条连续链路；任一接口发生错误都会导致出行建议错误或不可用。

## 2. 缺陷风险与测试设计

| 编号 | 缺陷风险 | 影响 | 对应测试 |
|---|---|---|---|
| R1 | 城市名无结果或返回错误国家 | 查询到错误位置 | 参数化测试南京、北京、上海，并检查国家代码 |
| R2 | 经纬度或预测天数越界 | 无效请求、错误数据 | 参数化覆盖非法纬度、经度和天数 |
| R3 | JSON 字段缺失或类型改变 | 程序解析崩溃 | 用伪响应注入缺失字段、错误类型 |
| R4 | 各小时数组长度不一致 | 天气指标错位 | 检查时间、温度、降水、风速数组均为 24×天数 |
| R5 | 天气数据超出合理范围 | 风险判断失真 | 检查温度、降水概率、风速不变量 |
| R6 | 网络超时或 HTTP 错误 | 功能不可用 | 设置超时，将底层错误转换为 `ServiceError` |
| R7 | 实时数据每天变化 | 测试偶发失败 | 不断言某日具体温度，只断言结构、范围和关系 |

## 3. 测试分层

- `tests/test_client_unit.py`：注入伪 HTTP 传输，离线验证参数、解析和错误处理。
- `tests/test_risk.py`：离线验证本地出行风险规则。
- `tests/test_open_meteo_api.py`：访问真实服务，验证当前接口契约和基本数据合理性，标记为 `network`。

## 4. 参数化

- 城市参数：南京、北京、上海。
- 预测天数：1 天、2 天。
- 非法输入：超界纬度、经度以及 0 天、17 天。
- 风险规则：正常、高温、低温降雨、降雨大风等组合。

## 5. 执行方法

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/setup-local.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/test.ps1 -Offline
```

JUnit XML 报告生成在 `reports/junit.xml`。

## 6. 建议保留的截图

1. 全部测试通过且显示用例数量的终端结果。
2. 参数化测试源码与对应测试名称。
3. `reports/junit.xml` 或测试结果摘要。

## 7. REST 接口测试与函数级单元测试比较

共性：都需要从风险出发设计输入、执行被测对象、断言实际结果，并保证测试可重复和能够定位缺陷。

差别：REST 测试还覆盖 HTTP、序列化、远程部署和网络环境，真实数据会变化，执行较慢且失败原因可能在外部；函数级单元测试隔离本地代码，数据固定、速度快、缺陷定位更直接。因此本项目同时保留网络测试和注入伪响应的离线测试。

## 8. 实际执行结果

最新完整执行时间：2026-08-19 11:48:35（Asia/Shanghai）。执行环境为 Windows 10.0.19045、Python 3.13.7、pytest 8.4.1。

- 离线测试：24 个通过，7 个网络用例按标记排除，用时 0.15 秒。
- 真实接口测试：7 个通过，24 个离线用例按标记排除，用时 8.43 秒。
- 合计：31 个测试全部通过，失败数和错误数均为 0。

原始证据保存在 `reports/experiment-1/20260819-114835/`：

- `environment.txt`：操作系统、Python、pytest 和项目目录；
- `offline-test.log`、`network-test.log`：两层测试的完整终端输出；
- `junit-offline.xml`、`junit-network.xml`：可供工具读取的结构化测试结果；
- `api-sample.json`：南京位置与天气接口的三小时响应样例；
- `summary.txt`：三个执行阶段的退出码及总体判定。

### 执行中遇到的问题

1. 系统 PowerShell 执行策略默认禁止直接运行 `.ps1`，因此改用 `powershell -NoProfile -ExecutionPolicy Bypass -File ...` 进行单次调用，没有修改系统全局策略。
2. Windows PowerShell 5 会错误解释不带 BOM 的 UTF-8 脚本中的中文字符串，因此自动化脚本改用 ASCII 文本，中文保留在 LaTeX、Markdown 和 Python 源码中。
3. `--junitxml=(Join-Path ...)` 会被 PowerShell 拆成错误参数，改为先计算路径，再传入单个 `"--junitxml=$path"` 参数。
4. 为避免网络波动掩盖代码缺陷，先运行 24 个离线测试，再单独执行 7 个真实服务测试。
