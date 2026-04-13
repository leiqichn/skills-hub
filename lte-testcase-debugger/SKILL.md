---
name: lte-testcase-debugger
description: |
  调试 LTE FDD Python nosetest 测试用例，迭代修复直到测试通过。当测试用例执行失败时自动触发，分析错误信息、定位问题代码、修复缺陷、重新运行，形成循环直到所有断言通过。
  **触发场景**：测试失败、测试报错、用例调试、nosetest 失败、修复测试代码、测试用例跑不通。
triggers:
  - "测试失败"
  - "nosetest.*失败"
  - "测试报错"
  - "用例跑不通"
  - "修复.*测试"
  - "debug.*test"
  - "test.*fail"
  - "LTE.*调试"
---

# LTE FDD 测试用例调试器

本 skill 处理 LTE FDD 测试用例的调试循环。当测试执行失败时，自动分析错误、定位问题、修复代码、重新运行，直到测试通过。

## 调试循环

```
执行测试 → 分析错误 → 定位问题 → 修复代码 → 重新执行 → 循环直到通过
```

## 工作流程

### 步骤 1：执行测试并捕获错误

运行 nosetest 执行测试用例：

```bash
nosetests -v <测试文件>::<测试类>::<测试方法>
```

或执行整个测试类：
```bash
nosetests -v <测试文件>::<测试类>
```

捕获完整的错误输出，包括：
- 堆栈跟踪（Traceback）
- 断言错误信息
- 标准输出和标准错误

### 步骤 2：分析错误类型

根据错误特征分类：

| 错误类型 | 错误模式 | 修复策略 |
|---------|---------|---------|
| **断言失败** | `AssertionError` | 检查期望值、比较逻辑、阈值设置 |
| **导入错误** | `ImportError`, `ModuleNotFoundError` | 添加 import、检查模块路径 |
| **语法错误** | `SyntaxError` | 修复 Python 语法 |
| **属性/方法错误** | `AttributeError`, `NameError` | 检查变量名、方法名、API 调用 |
| **超时错误** | `TimeoutError` | 增加等待时间、检查异步操作 |
| **连接错误** | `ConnectionError`, `NetworkError` | 检查网络配置、设备连接 |
| **资源错误** | `ResourceError`, `EnvironmentError` | 检查测试环境、资源分配 |

### 步骤 3：定位问题代码

根据堆栈跟踪：
1. 定位到具体的失败文件和行号
2. 读取相关代码段
3. 分析上下文依赖

### 步骤 4：生成修复方案

针对不同错误类型：

**断言失败**：
```python
# 错误
self.assertGreaterEqual(result.peak, 100)

# 分析：实际值可能为 None 或低于阈值
# 修复：添加更详细的诊断信息
peak_rate = result.peak if result.peak is not None else 0
self.assertGreaterEqual(peak_rate, 100, f"Peak rate {peak_rate} < 100Mbps")
```

**导入错误**：
```python
# 错误
from lte_api import LTE_API

# 修复：检查正确的导入路径
import sys
sys.path.insert(0, '/path/to/lte/module')
from lte_api import LTE_API
```

**API 调用错误**：
```python
# 错误
self.lte_api.attach_ue()

# 修复：检查 API 签名和参数
# 可能需要传递参数
self.ue = self.lte_api.attach_ue(ue_config={
    'band': 3,
    'plmn': '46001'
})
```

### 步骤 5：应用修复并重新测试

1. 使用 Edit 工具修改代码
2. 重新运行测试
3. 如果仍然失败，回到步骤 2

### 步骤 6：验证通过

当测试通过时：
1. 输出成功信息
2. 总结修复内容
3. 提供后续建议

## 常见 LTE FDD 测试错误处理

### 基站连接问题

```python
# 问题：基站连接超时
# 修复：
def setUp(self):
    self.lte_api = LTE_API()
    self.lte_api.set_timeout(30)  # 增加超时时间
    self.lte_api.connect('192.168.1.100')  # 确保 IP 正确
```

### UE附着失败

```python
# 问题：UE附着网络失败
# 修复：
def test_ue_attach(self):
    max_retries = 3
    for i in range(max_retries):
        try:
            self.ue = self.lte_api.attach_ue()
            break
        except AttachError as e:
            if i == max_retries - 1:
                raise
            time.sleep(5)  # 重试前等待
```

### 吞吐量测量不准确

```python
# 问题：吞吐量测量值为 0 或 None
# 修复：
def test_throughput(self):
    # 确保数据传输真正开始
    self.udp.start()
    time.sleep(2)  # 等待数据传输稳定

    # 确保测量时间足够长
    result = self.udp.measure_throughput(duration=10)

    # 防御性断言
    self.assertIsNotNone(result, "Throughput measurement returned None")
    self.assertGreater(result.peak, 0, "Peak throughput is 0")
```

### 清理失败导致后续测试受影响

```python
# 问题：tearDown 清理不完整
# 修复：
def tearDown(self):
    try:
        if hasattr(self, 'udp'):
            self.udp.stop()
        if hasattr(self, 'ue'):
            self.lte_api.release_ue(self.ue)
    except Exception as e:
        print(f"Cleanup warning: {e}")  # 不要让清理失败影响测试结果
```

## 调试输出格式

### 错误分析报告

```
=== LTE 测试用例调试报告 ===
用例: test_embb_dl_throughput
文件: test_throughput_embb.py
行号: 42

错误类型: AssertionError
错误信息: Peak rate 0 < 100Mbps

可能原因:
1. UDP 数据传输未正常启动
2. 测量持续时间太短
3. 网络配置问题

修复建议:
1. 在测量前添加 delay 确保数据传输稳定
2. 增加测量持续时间到 10 秒
3. 检查基站和 UE 的带宽配置

应用修复: 是
```

### 修复后的测试输出

```
=== 测试执行结果 ===
用例: test_embb_dl_throughput
状态: ✓ 通过
执行时间: 12.3s
峰值速率: 112.5 Mbps
平均速率: 95.2 Mbps

修复历史:
  1. 增加测量前等待时间 (2s → 5s)
  2. 增加测量持续时间 (5s → 10s)
  3. 添加详细的诊断日志
```

## 与 lte-testcase-generator 配合

调试完成后：

1. 如果是新生成的用例调试成功 → 记录修复内容到用例注释中
2. 如果是现有用例的问题修复 → 更新原始用例文件
3. 如果发现通用问题 → 建议更新 generator skill 的代码模板

## 注意事项

1. **保持耐心**：有些测试需要多次调试才能通过
2. **每次只改一个变量**：便于定位真正的问题
3. **记录修复历史**：方便后续回溯
4. **不要跳过断言**：修复不是绕过问题，而是正确解决问题
5. **确保环境干净**：每次调试前确认环境状态
