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
references:
  - title: "华为LTE基站测试规范"
    url: "https://support.huawei.com/enterprise/doc/DOC1100000001"
    type: documentation
    description: "华为LTE基站测试用例设计规范和模板"
  - title: "华为TestSuite测试框架"
    url: "https://support.huawei.com/enterprise/doc/DOC1100000002"
    type: reference
    description: "华为官方TestSuite自动化测试框架使用指南"
  - title: "华为LTE API参考"
    url: "https://support.huawei.com/enterprise/doc/DOC1100000003"
    type: api
    description: "LTE测试API接口说明和参数定义"
  - title: "lte-test-runner"
    url: "../lte-test-runner/SKILL.md"
    type: skill
    description: "LTE测试自动执行与迭代修复引擎"
  - title: "lte-testcase-debugger"
    url: "../lte-testcase-debugger/SKILL.md"
    type: skill
    description: "LTE测试用例调试器"
  - title: "lte-similar-steps-finder"
    url: "../lte-similar-steps-finder/SKILL.md"
    type: skill
    description: "LTE相似步骤查找器，用于在用例级搜索失败时逐级向上搜索相似步骤"
assets:
  - name: "LTE_Test_Template.py"
    type: code-template
    description: "标准LTE测试用例代码模板"
  - name: "testcase_spec.yaml"
    type: config-template
    description: "测试用例规格YAML模板"
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

### 步骤 2：分层搜索相似用例/步骤

采用**分层搜索策略**，逐级向上查找：

```
┌─────────────────────────────────────────────────────────────┐
│ 第一层：当前项目测试用例库（最高优先级）                      │
│         查找相似【测试用例】                                 │
│         权重：项目内用例 ★★★★★                            │
└────────────────────┬────────────────────────────────────────┘
                     │ 找不到足够相似的用例（<60%相似度）
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 第二层：逐级向上查找相似【测试步骤】                          │
│                                                             │
│   当前文件夹 → 父文件夹 → 祖父文件夹 → ... → 公共库          │
│      ★★★★☆     ★★★☆☆     ★★☆☆☆     ...    ★☆☆☆☆      │
│                                                             │
│   搜索顺序：                                                 │
│   1. 当前文件夹（最高权重）                                  │
│   2. 父文件夹（父文件夹名/common/steps/等）                   │
│   3. 继续向上直到根目录                                       │
│   4. 公共库文件夹（最低权重，所有用户共享）                    │
└─────────────────────────────────────────────────────────────┘

公共文件夹定义：
- `../common/` - 公共步骤库
- `../../common/` - 更上层的公共库
- `/path/to/shared/steps/` - 大家都可以用的公共步骤
- 特点：所有公共文件夹权重相同，谁都可以用
```

### 步骤 3：相似度计算

**第一层搜索（用例级）**：
使用 AI 能力分析用户输入与每个现有用例的相似度：

| 维度 | 权重 | 说明 |
|------|------|------|
| 功能相似度 | 40% | 用例名称和描述的功能相关性 |
| 步骤相似度 | 30% | 测试步骤的流程和操作相似度 |
| 期望相似度 | 20% | 期望结果的结构和类型相似度 |
| 上下文相似度 | 10% | 前置条件和恢复步骤的相似度 |

**第二层搜索（步骤级）**：
当用例级搜索相似度 < 60% 时，触发步骤级搜索：

| 维度 | 权重 | 说明 |
|------|------|------|
| 操作相似度 | 40% | 核心操作是否相同（attach/detach/handoff等） |
| 参数相似度 | 30% | 配置参数是否类似（band/plmn/tac等） |
| 期望相似度 | 20% | 期望结果结构是否一致 |
| 路径权重 | 10% | 当前位置的权重（越近越高） |

**评分算法**：
```
用例相似度 = 功能*0.4 + 步骤*0.3 + 期望*0.2 + 上下文*0.1
步骤相似度 = 操作*0.4 + 参数*0.3 + 期望*0.2 + 路径权重*0.1

最终得分 = 基础相似度 × 位置权重
```

### 步骤 4：生成新测试用例代码

基于最相似的用例或步骤模式，生成新的测试代码：

**代码模板（nosetest TestClass 风格）**：
```python
# -*- coding: utf-8 -*-
"""
LTE FDD [用例所属类别] 测试用例
自动生成用例: [用例名称]
生成时间: [当前时间]

用例规格:
  - 前置: [前置步骤摘要]
  - 步骤: [测试步骤摘要]
  - 期望: [期望结果摘要]
"""

import unittest
import time
import logging
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Test[用例类别](unittest.TestCase):
    """
    [用例描述]

    用例ID: TEST_[年份]_[模块]_[序号]
    优先级: P[1-3] (1=最高)
    预计耗时: Xs
    """

    @classmethod
    def setUpClass(cls):
        """类级别的初始化，只执行一次"""
        cls._shared_resources = []
        logger.info("TestClass 初始化")

    def setUp(self):
        """前置步骤 - 每个测试方法前执行"""
        self._setup_complete = False
        self._ue_context: Optional[Dict[str, Any]] = None
        self._test_data: Dict[str, Any] = {}

        try:
            # 初始化 LTE API
            self._init_lte_api()
            # 配置测试环境
            self._configure_test_environment()
            # 等待设备就绪
            self._wait_for_device_ready()
            self._setup_complete = True
            logger.info(f"setUp 完成: {self._test_data}")
        except Exception as e:
            logger.error(f"setUp 失败: {e}")
            self.fail(f"前置条件设置失败: {e}")

    def _init_lte_api(self):
        """初始化 LTE API 连接"""
        from lte_api import LTE_API

        self.lte_api = LTE_API()
        self.lte_api.set_timeout(30)
        self.lte_api.set_log_level(logging.INFO)
        logger.debug("LTE API 初始化完成")

    def _configure_test_environment(self):
        """配置测试环境参数"""
        # 默认配置
        self._default_config = {
            'band': 3,
            'plmn': '46001',
            'bandwidth': '20MHz',
            'tx_power': 23,
            'duration': 10
        }
        # 合并用户自定义配置
        config = {**self._default_config}
        self._test_data['config'] = config
        logger.debug(f"测试配置: {config}")

    def _wait_for_device_ready(self, timeout: int = 30):
        """等待设备就绪"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.lte_api.is_device_ready():
                logger.info("设备就绪")
                return
            time.sleep(1)
        raise TimeoutError(f"设备未能在 {timeout}s 内就绪")

    def test_[用例标识](self):
        """
        测试步骤: [步骤摘要]
        期望结果: [期望结果]

        测试数据:
          {test_data}
        """
        test_start = time.time()
        logger.info(f"开始执行测试: {self._testMethodName}")

        try:
            # 执行核心测试逻辑
            result = self._execute_test_steps()

            # 验证结果
            self._verify_expectations(result)

            # 记录测试通过
            elapsed = time.time() - test_start
            logger.info(f"测试通过，耗时: {elapsed:.2f}s")

        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"测试执行异常: {e}")
            raise

    def _execute_test_steps(self) -> Dict[str, Any]:
        """
        执行测试步骤 - 子类可重写实现具体测试逻辑

        Returns:
            测试结果字典
        """
        # TODO: 根据具体测试用例实现
        raise NotImplementedError("子类必须实现 _execute_test_steps")

    def _verify_expectations(self, result: Dict[str, Any]):
        """
        验证期望结果 - 子类可重写实现具体断言逻辑

        Args:
            result: 测试结果
        """
        # TODO: 根据具体期望实现断言
        pass

    def tearDown(self):
        """恢复步骤 - 每个测试方法后执行"""
        cleanup_errors = []

        try:
            # 清理测试数据
            if hasattr(self, '_test_data'):
                self._test_data.clear()

            # 释放 UE 连接
            if hasattr(self, '_ue_context') and self._ue_context:
                try:
                    self._release_ue()
                except Exception as e:
                    cleanup_errors.append(f"UE释放失败: {e}")

            # 停止数据传输
            if hasattr(self, '_udp_transfer'):
                try:
                    self._udp_transfer.stop()
                    logger.debug("UDP 传输已停止")
                except Exception as e:
                    cleanup_errors.append(f"UDP停止失败: {e}")

            # 断开连接
            if hasattr(self, 'lte_api'):
                try:
                    self.lte_api.disconnect()
                    logger.debug("LTE API 已断开")
                except Exception as e:
                    cleanup_errors.append(f"断开连接失败: {e}")

        except Exception as e:
            cleanup_errors.append(f"清理异常: {e}")
            logger.warning(f"tearDown 警告: {e}")

        finally:
            # 即使清理失败也不让测试报告失败
            if cleanup_errors:
                logger.warning(f"部分清理操作失败: {cleanup_errors}")

    @classmethod
    def tearDownClass(cls):
        """类级别的清理，所有测试执行完后执行一次"""
        try:
            # 清理共享资源
            for resource in cls._shared_resources:
                try:
                    resource.release()
                except Exception as e:
                    logger.warning(f"释放共享资源失败: {e}")
            cls._shared_resources.clear()
            logger.info("TestClass 清理完成")
        except Exception as e:
            logger.error(f"tearDownClass 异常: {e}")

    def _release_ue(self):
        """释放 UE 资源"""
        if self._ue_context:
            self.lte_api.release_ue(self._ue_context.get('ue_id'))
            logger.debug(f"UE {self._ue_context.get('ue_id')} 已释放")
            self._ue_context = None

    def _create_retry_decorator(self, max_retries: int = 3, delay: int = 5):
        """
        创建重试装饰器

        Args:
            max_retries: 最大重试次数
            delay: 重试间隔(秒)
        """
        import functools

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        logger.warning(f"尝试 {attempt + 1}/{max_retries} 失败: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(delay)
                raise last_exception
            return wrapper
        return decorator


# ============================================================================
# 辅助函数库
# ============================================================================

def create_throughput_test_case(case_name: str, config: Dict[str, Any],
                                expected_peak: float, expected_avg: float):
    """
    创建吞吐量测试用例的辅助函数

    Args:
        case_name: 用例名称
        config: 测试配置 {'band': int, 'bw': str, 'direction': str}
        expected_peak: 期望峰值(Mbps)
        expected_avg: 期望平均值(Mbps)
    """
    class ThroughputTestCase(unittest.TestCase):
        """吞吐量测试用例"""

        def setUp(self):
            self.lte_api = LTE_API()
            self.config = config

        def test_throughput(self):
            """执行吞吐量测试"""
            udp = self.lte_api.start_udp_transfer(
                direction=self.config.get('direction', 'dl'),
                bandwidth=self.config.get('bw', '20MHz')
            )
            time.sleep(self.config.get('duration', 10))
            result = udp.measure_throughput()

            self.assertGreaterEqual(result.peak, expected_peak)
            self.assertGreaterEqual(result.average, expected_avg)

        def tearDown(self):
            if hasattr(self, 'udp'):
                self.udp.stop()
            self.lte_api.release_all_ues()

    return ThroughputTestCase


def validate_test_result(result: Dict[str, Any], thresholds: Dict[str, float]) -> bool:
    """
    验证测试结果是否满足阈值

    Args:
        result: 测试结果
        thresholds: 阈值字典 {'metric_name': threshold}

    Returns:
        是否通过
    """
    for metric, threshold in thresholds.items():
        value = result.get(metric)
        if value is None:
            logger.error(f"指标 {metric} 值为 None")
            return False
        if value < threshold:
            logger.warning(f"指标 {metric}: {value} < {threshold} (阈值)")
            return False
    return True
```

### 步骤 5：输出和保存

1. **文件输出**：将生成的代码写入新文件
   - 文件名格式：`test_[模块]_[用例标识].py`
   - 保存到测试用例库目录

2. **终端输出**：同时在终端显示完整代码

3. **相似用例信息**：显示找到的相似用例及其相似度分数

## 完整闭环流程

本 skill 是 LTE 测试闭环的核心环节之一，与其他 skill 形成完整测试流程：

```
┌─────────────────────────────────────────────────────┐
│              LTE 测试 Skill 生态                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────────┐                            │
│  │ lte-testcase-       │  ← 生成测试用例            │
│  │ generator           │                            │
│  └──────────┬──────────┘                            │
│             │                                       │
│             ▼                                       │
│  ┌─────────────────────┐                            │
│  │ lte-test-runner     │  ← 执行 + 自动调试         │
│  └──────────┬──────────┘                            │
│             │                                       │
│             ▼                                       │
│  ┌─────────────────────┐                            │
│  │ lte-testcase-       │  ← 分析 + 修复             │
│  │ debugger            │                            │
│  └─────────────────────┘                            │
│                                                      │
│  ┌─────────────────────┐                            │
│  │ lte-similar-steps-  │  ← 找不到相似用例时触发    │
│  │ finder              │    逐级向上搜索相似步骤     │
│  └─────────────────────┘                            │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 分层搜索机制

### 第一层：当前项目用例库
在当前项目的测试用例库中查找相似【测试用例】。

### 第二层：逐级向上搜索相似【步骤】
当用例相似度 < 60% 时，调用 **lte-similar-steps-finder** 逐级向上搜索：

```
当前文件夹 (★★★权重)
    ↓
父文件夹 (★★权重)
    ↓
公共库文件夹 (★权重，所有公共文件夹权重相同)
    - ../common/
    - ../../shared/steps/
    - /path/to/shared/library/
```

## 与 lte-test-runner 配合（推荐）

生成代码后，推荐使用 **lte-test-runner** 进行自动执行和调试：

```python
from test_runner import LTETestRunner

runner = LTETestRunner()
result = runner.generate_and_run(spec, output_dir='./test_cases')
```

runner 会自动：
1. 调用本 skill 生成测试代码
2. 执行测试
3. 如果失败，自动调用 debugger 进行迭代修复
4. 如果相似用例不足，触发 lte-similar-steps-finder 搜索
5. 循环直到测试通过或达到最大迭代次数

## 与 lte-similar-steps-finder 配合

当第一层搜索找不到足够相似的用例（相似度 < 60%）时：

```
Generator → 调用 similar-steps-finder → 逐级向上搜索相似步骤
                                        ↓
                              当前文件夹 → 父文件夹 → 公共库
```

similar-steps-finder 会返回：
- 相似步骤列表
- AW天线映射（如需要）
- 推荐的新用例结构

## 与 lte-testcase-debugger 配合（手动模式）

如果不想使用自动 runner，可以手动调用 debugger：

```
生成代码 → nosetests 执行 → 失败 → 调用 lte-testcase-debugger → 修复 → 重新执行 → 循环
```

当测试失败时：
1. **调用 lte-testcase-debugger skill**：分析错误并生成修复方案
2. **应用修复**：根据 debugger 建议修改代码
3. **重新执行**：再次运行 nosetests
4. **迭代优化**：不断修复直到所有断言通过
