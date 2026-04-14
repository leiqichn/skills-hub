---
name: lte-report-generator
description: |
  LTE FDD 测试报告生成器。将测试执行结果解析、汇总、生成为可视化报告。支持 JSON、Markdown、HTML 三种格式输出，可用于测试结果存档、CI/CD集成、邮件通知等场景。
  **触发场景**：生成测试报告、查看测试汇总、导出测试结果、CI/CD报告集成、邮件报告发送。
triggers:
  - "生成.*报告"
  - "测试报告"
  - "导出.*结果"
  - "test.*report"
  - "generate.*report"
  - "test.*summary"
  - "测试.*汇总"
  - "测试.*统计"
references:
  - title: "lte-test-runner"
    url: "../lte-test-runner/SKILL.md"
    type: skill
    description: "LTE测试执行引擎，提供测试结果数据"
  - title: "lte-testcase-debugger"
    url: "../lte-testcase-debugger/SKILL.md"
    type: skill
    description: "LTE测试用例调试器"
assets:
  - name: "report_generator.py"
    type: script
    description: "报告生成核心脚本"
---


# LTE 测试报告生成器

本 skill 将测试执行结果解析、汇总、生成为可视化报告。

## 功能特性

- **多格式支持**: JSON / Markdown / HTML
- **统计汇总**: 通过率、失败率、耗时统计
- **用例级详情**: 每个测试用例的状态、耗时、错误信息
- **可视化图表**: 文本饼图、状态分布
- **CI/CD 集成**: 支持 JUnit XML 风格输出

## 快速开始

### 基本使用

```bash
# 生成 Markdown 报告
python report_generator.py -i test_result.json -o report.md -f md

# 生成 HTML 报告
python report_generator.py -i test_result.json -o report.html -f html

# 生成 JSON 报告
python report_generator.py -i test_result.json -o report.json -f json
```

### Python API

```python
from report_generator import ReportGenerator, TestStatus

# 创建报告生成器
gen = ReportGenerator(
    project_name="LTE 测试项目",
    environment="真实基站"
)

# 添加测试结果
gen.add_test_result(
    name='test_ue_attach',
    class_name='TestUEAttach',
    file_path='test_attach.py',
    status=TestStatus.PASSED,
    duration=1.23
)

gen.add_test_result(
    name='test_throughput',
    class_name='TestThroughput',
    file_path='test_throughput.py',
    status=TestStatus.FAILED,
    duration=5.67,
    error_type='AssertionError',
    error_message='Expected RSRP > -100, got -120'
)

# 生成报告
json_report = gen.generate_json()
md_report = gen.generate_markdown()
html_report = gen.generate_html()
```

## 数据结构

### TestReport

```python
@dataclass
class TestReport:
    project_name: str        # 项目名称
    environment: str        # 测试环境
    test_suites: List[...]  # 测试套件列表
    start_time: float       # 开始时间戳
    end_time: float         # 结束时间戳
    metadata: Dict           # 额外元数据
```

### TestSuiteResult

```python
@dataclass
class TestSuiteResult:
    name: str               # 套件名称（通常是文件名）
    total: int             # 总测试数
    passed: int            # 通过数
    failed: int            # 失败数
    errors: int            # 错误数
    skipped: int           # 跳过数
    duration: float        # 总耗时
    test_cases: List[...]  # 测试用例列表
```

### TestCaseResult

```python
@dataclass
class TestCaseResult:
    name: str              # 用例名称
    class_name: str        # 测试类名
    file_path: str         # 文件路径
    status: TestStatus     # 状态
    duration: float        # 耗时
    error_type: str        # 错误类型
    error_message: str     # 错误信息
    timestamp: float       # 时间戳
```

### TestStatus 枚举

```python
class TestStatus(Enum):
    PASSED = "PASSED"    # 通过
    FAILED = "FAILED"    # 失败（断言不通过）
    ERROR = "ERROR"      # 错误（异常）
    TIMEOUT = "TIMEOUT"  # 超时
    SKIPPED = "SKIPPED"  # 跳过
    UNKNOWN = "UNKNOWN"  # 未知
```

## 输出格式

### JSON 格式

```json
{
  "project_name": "LTE 测试项目",
  "environment": "真实基站",
  "total_tests": 10,
  "total_passed": 8,
  "total_failed": 1,
  "total_errors": 1,
  "overall_pass_rate": 80.0,
  "duration": 45.67,
  "test_suites": [...]
}
```

### Markdown 格式

包含：概览、统计图表、用例详情、失败用例分析

### HTML 格式

包含：响应式设计、渐变色统计卡片、语法高亮代码块

## CLI 用法

```bash
python report_generator.py --project "LTE项目" --env "真实基站" -i input.json -o output.md -f md
```

## 相关 Skill

- `lte-test-runner` - 测试执行引擎
- `lte-testcase-debugger` - 测试用例调试器

---
