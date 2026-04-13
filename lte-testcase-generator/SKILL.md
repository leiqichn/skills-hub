---
name: lte-testcase-generator
description: |
  在 LTE FDD Python 测试用例工程中查找相似测试用例并生成新的测试代码。当用户提供测试用例名称、前置步骤(preconditions)、测试步骤(test steps)、恢复步骤(recovery steps)和期望结果(expected results)时，自动找到最相似的现有用例并基于该用例生成新的测试代码。适用于 nosetest 测试框架的 TestClass 风格用例。
  **触发场景**：用户说"帮我找相似的 LTE 测试用例"、"生成新的测试用例"、"基于现有用例创建新用例"、"LTE FDD 测试"等。
triggers:
  - "查找相似测试用例"
  - "生成 LTE 测试用例"
  - "基于.*创建.*测试用例"
  - "LTE FDD.*测试用例"
  - "nosetest.*测试"
  - "无线.*测试用例"
  - "test case.*similar"
  - "find similar.*test"
  - "generate.*test case"
---

# LTE FDD 测试用例生成器

本 skill 帮助你在现有的 LTE FDD Python 测试用例工程中，通过输入新用例的规格（名称、前置、步骤、恢复、期望），找到最相似的现有用例，并基于相似用例生成新的测试代码。

## 工作流程

### 步骤 1：理解测试用例规格

用户会提供以下信息：
- **用例名称** (case_name): 简短描述性名称
- **前置步骤** (preconditions): 测试开始前的准备步骤
- **测试步骤** (test_steps): 核心测试操作步骤
- **恢复步骤** (recovery_steps): 测试完成后的清理步骤
- **期望结果** (expected_results): 测试成功的判定标准

### 步骤 2：定位测试用例库

首先确认测试用例库的位置：

1. **用户指定路径**：如果用户明确提供了测试用例目录，直接使用
2. **常见位置**：依次检查以下目录：
   - `./test_cases/` 或 `./tests/`
   - `./testcases/` 或 `./testcase/`
   - `./lte/` 或 `./LTE/`
   - `./` 当前目录下的 `.py` 文件

找到测试用例后，读取所有测试文件内容。

### 步骤 3：语义相似度计算

使用 AI 能力分析用户输入与每个现有用例的相似度：

**相似度评分维度**：
1. **功能相似度**：用例名称和描述的功能相关性 (0-40%)
2. **步骤相似度**：测试步骤的流程和操作相似度 (0-30%)
3. **期望相似度**：期望结果的结构和类型相似度 (0-20%)
4. **上下文相似度**：前置条件和恢复步骤的相似度 (0-10%)

**评分算法**：
```
最终相似度 = 功能*0.4 + 步骤*0.3 + 期望*0.2 + 上下文*0.1
```

选取**相似度最高的前 3 个用例**作为候选。

### 步骤 4：生成新测试用例代码

基于最相似的用例，生成新的测试代码：

**代码模板（nosetest TestClass 风格）**：
```python
# -*- coding: utf-8 -*-
"""
LTE FDD [用例所属类别] 测试用例
自动生成用例: [用例名称]
生成时间: [当前时间]
"""

import unittest
import time


class Test[用例类别](unittest.TestCase):
    """
    [用例描述]
    """

    def setUp(self):
        """前置步骤"""
        [前置步骤代码]

    def test_[用例标识](self):
        """
        测试步骤: [步骤摘要]
        期望结果: [期望结果]
        """
        [测试步骤代码]

    def tearDown(self):
        """恢复步骤"""
        [恢复步骤代码]
```

### 步骤 5：输出和保存

1. **文件输出**：将生成的代码写入新文件
   - 文件名格式：`test_[模块]_[用例标识].py`
   - 保存到测试用例库目录

2. **终端输出**：同时在终端显示完整代码

3. **相似用例信息**：显示找到的相似用例及其相似度分数

## 调试循环

生成的测试用例可能需要调试。如果测试执行失败，使用 **lte-testcase-debugger skill** 进行迭代修复：

```
当测试失败时 → 调用 lte-testcase-debugger → 修复代码 → 重新执行 → 循环直到通过
```

## 代码生成策略

### 基于相似用例的模式提取

从相似用例中提取以下模式：

1. **setup 模式**：如何初始化测试环境
2. **API 调用模式**：如何调用 LTE 测试 API
3. **断言模式**：如何验证期望结果
4. **清理模式**：如何进行恢复操作

### 必要元素保留

从相似用例继承：
- 继承测试类结构
- 保留通用的 setup/teardown 逻辑
- 保持相同的断言辅助函数调用

### 必要元素替换

根据新用例规格替换：
- 用例名称和描述
- 特定的测试参数值
- 特定的期望结果

## 示例

### 输入示例

用户输入：
```
用例名称: eMBB下行吞吐量测试
前置步骤:
  - 基站配置为 FDD 模式
  - UE attach 到网络
  - 配置 20MHz 带宽
测试步骤:
  - 启动 UDP 数据传输
  - 测量下行吞吐量
  - 记录峰值速率
恢复步骤:
  - 停止数据传输
  - 释放 UE 连接
期望结果:
  - 下行峰值速率 >= 100Mbps
  - 平均吞吐量 >= 80Mbps
```

### 输出示例

找到最相似用例：`test_lte_throughput_dl_10m.py`（相似度 85%）

生成代码：
```python
# -*- coding: utf-8 -*-
"""
LTE FDD 吞吐量测试用例
自动生成用例: eMBB下行吞吐量测试
生成时间: 2026-04-13
"""

import unittest
import time


class TestThroughput(unittest.TestCase):
    """eMBB 下行吞吐量测试"""

    def setUp(self):
        """前置步骤"""
        self.lte_api = LTE_API()
        self.lte_api.set_bandwidth('20MHz')
        self.ue = self.lte_api.attach_ue()
        print(f"UE {self.ue.imsi} attached")

    def test_embb_dl_throughput(self):
        """
        测试步骤: eMBB下行吞吐量测试
        期望结果: 下行峰值>=100Mbps, 平均>=80Mbps
        """
        self.udp = self.lte_api.start_udp_transfer(direction='dl')
        time.sleep(10)
        result = self.udp.measure_throughput()

        self.assertGreaterEqual(result.peak, 100, "Peak rate below 100Mbps")
        self.assertGreaterEqual(result.average, 80, "Average rate below 80Mbps")

    def tearDown(self):
        """恢复步骤"""
        if hasattr(self, 'udp'):
            self.udp.stop()
        self.lte_api.release_ue(self.ue)
```

## 注意事项

1. **中文注释**：生成的代码包含中文注释，便于理解
2. **参数化**：敏感参数（如 IP、端口号）用变量代替
3. **错误处理**：包含必要的异常捕获
4. **日志记录**：关键步骤有日志输出
5. **可读性**：代码格式整洁，符合 PEP 8

## 与 lte-testcase-debugger 配合

生成代码后：
1. **立即尝试运行**：使用 nosetests 执行测试
2. **失败时调用 debugger**：当测试失败时，调用 `lte-testcase-debugger` skill 进行诊断和修复
3. **迭代优化**：不断修复直到所有断言通过
