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

    # 验证连接状态
    if not self.lte_api.is_connected():
        raise ConnectionError("基站连接失败")

    # 等待小区就绪
    self._wait_for_cell_ready()
```

### UE附着失败

```python
# 问题：UE附着网络失败
# 修复：
def test_ue_attach(self):
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            self.ue = self.lte_api.attach_ue()
            # 验证附着成功
            if not self._verify_attach(self.ue):
                raise AttachError("UE附着验证失败")
            logger.info(f"UE {self.ue.imsi} 附着成功")
            return
        except AttachError as e:
            logger.warning(f"附着尝试 {attempt + 1} 失败: {e}")
            if attempt < max_retries - 1:
                logger.info(f"等待 {retry_delay}s 后重试...")
                time.sleep(retry_delay)
            else:
                raise AttachError(f"UE附着失败，已重试 {max_retries} 次")

def _verify_attach(self, ue):
    """验证UE附着状态"""
    try:
        status = self.lte_api.get_ue_status(ue.id)
        return status.state == 'attached'
    except:
        return False
```

### 吞吐量测量不准确

```python
# 问题：吞吐量测量值为 0 或 None
# 修复：
def test_throughput(self):
    # 确保数据传输真正开始
    self.udp.start()

    # 等待数据传输稳定
    time.sleep(self._get_stabilization_time())

    # 确保测量时间足够长
    measurement_duration = self._get_measurement_duration()
    result = self.udp.measure_throughput(duration=measurement_duration)

    # 防御性断言
    self.assertIsNotNone(result, "Throughput measurement returned None")
    self.assertIsNotNone(result.peak, "Peak throughput is None")
    self.assertGreater(result.peak, 0, "Peak throughput is 0")

    # 记录详细诊断信息
    logger.info(f"吞吐量测量: peak={result.peak}, avg={result.average}")

def _get_stabilization_time(self):
    """获取传输稳定等待时间"""
    # 可配置的等待时间
    return self._test_config.get('stabilization_time', 5)

def _get_measurement_duration(self):
    """获取测量持续时间"""
    return self._test_config.get('measurement_duration', 10)
```

### 清理失败导致后续测试受影响

```python
# 问题：tearDown 清理不完整
# 修复：
def tearDown(self):
    # 使用 try-finally 确保清理总是执行
    cleanup_warnings = []

    try:
        # 停止 UDP 传输
        if hasattr(self, 'udp') and self.udp:
            try:
                self.udp.stop()
                logger.debug("UDP 传输已停止")
            except Exception as e:
                cleanup_warnings.append(f"UDP停止: {e}")

        # 释放 UE
        if hasattr(self, 'ue') and self.ue:
            try:
                self.lte_api.release_ue(self.ue)
                logger.debug(f"UE {self.ue.id} 已释放")
            except Exception as e:
                cleanup_warnings.append(f"UE释放: {e}")

        # 断开连接
        if hasattr(self, 'lte_api') and self.lte_api:
            try:
                self.lte_api.disconnect()
                logger.debug("LTE API 已断开")
            except Exception as e:
                cleanup_warnings.append(f"断开连接: {e}")

    finally:
        # 即使清理失败也记录警告
        if cleanup_warnings:
            logger.warning(f"tearDown 清理警告: {cleanup_warnings}")
            # 不要让清理失败影响测试结果报告
```

## LTE 特定错误深度分析

### 1. SNR/信号质量问题

```
错误: AssertionError: SNR 3.2dB < 10dB
可能原因:
  - 天线连接问题
  - 频偏配置错误
  - 干扰源
修复:
  1. 检查天线连接器
  2. 验证频点配置
  3. 扫描干扰信号
```

### 2. HARQ重传率过高

```
错误: AssertionError: HARQ retransmission rate 35% > 20%
可能原因:
  - CQI反馈不及时
  - 下行干扰
  - 信道条件差
修复:
  1. 检查 PDCCH 配置
  2. 验证信道条件
  3. 调整目标 BLER
```

### 3. 调度算法问题

```
错误: 预期调度 50 PRB，实际 30 PRB
可能原因:
  - 调度器配置问题
  - PMI/CQI 反馈异常
  - 优先级配置错误
修复:
  1. 检查调度器参数
  2. 验证 CQI 报告
  3. 检查优先级设置
```

### 4. 功率控制问题

```
错误: UE TX power -10dBm > 0dBm
可能原因:
  - 功率控制配置错误
  - 开环功率控制参数
修复:
  1. 检查 P0_PUSCH 配置
  2. 验证路径损耗估算
  3. 检查 alpha 参数
```

## 调试输出格式

### 错误分析报告

```
╔══════════════════════════════════════════════════════════════════╗
║                   LTE 测试用例调试报告                           ║
╠══════════════════════════════════════════════════════════════════╣
║ 用例: test_embb_dl_throughput                                   ║
║ 文件: test_throughput_embb.py                                    ║
║ 行号: 42                                                        ║
╠══════════════════════════════════════════════════════════════════╣
║ 错误类型: AssertionError                                         ║
║ 错误信息: Peak rate 0 < 100Mbps                                  ║
╠══════════════════════════════════════════════════════════════════╣
║ 可能原因:                                                       ║
║   1. UDP 数据传输未正常启动                                      ║
║   2. 测量持续时间太短                                            ║
║   3. 网络配置问题                                                ║
╠══════════════════════════════════════════════════════════════════╣
║ 修复建议:                                                       ║
║   1. 在测量前添加 delay 确保数据传输稳定                         ║
║   2. 增加测量持续时间到 10 秒                                    ║
║   3. 检查基站和 UE 的带宽配置                                    ║
╠══════════════════════════════════════════════════════════════════╣
║ 调试历史:                                                       ║
║   尝试 1: 增加测量前等待时间 (2s → 5s) - 失败                  ║
║   尝试 2: 增加测量持续时间 (5s → 10s) - 失败                    ║
║   尝试 3: 检查 UDP 配置 - 成功 ✓                                ║
╚══════════════════════════════════════════════════════════════════╝
```

### 修复后的测试输出

```
============================================================
 测试执行结果
============================================================
用例: test_embb_dl_throughput
状态: ✓ 通过
执行时间: 12.3s
峰值速率: 112.5 Mbps
平均速率: 95.2 Mbps

修复历史:
  1. 增加测量前等待时间 (2s → 5s)
  2. 增加测量持续时间 (5s → 10s)
  3. 添加详细的诊断日志
============================================================
```

## 调试策略建议

### 1. 二分法调试

当测试失败原因不明确时：
```
1. 简化测试条件（最小配置）
2. 如果仍然失败 → 问题在环境/Setup
3. 如果通过 → 逐步增加复杂度
```

### 2. 对比法调试

当有多个相似测试时：
```
1. 找一个必定通过的用例
2. 对比两个用例的差异
3. 差异点即为问题所在
```

### 3. 隔离法调试

当测试相互影响时：
```
1. 只运行失败的测试
2. 如果通过 → 之前测试遗留状态
3. 如果失败 → 问题在当前测试
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
6. **保存堆栈信息**：便于后续分析
7. **检查资源释放**：确保测试间无资源泄露
