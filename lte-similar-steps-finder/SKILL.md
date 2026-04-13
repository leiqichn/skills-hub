---
name: lte-similar-steps-finder
description: |
  在 LTE FDD 测试用例工程中查找相似测试步骤和期望结果。当 lte-testcase-generator 无法找到足够相似的用例时触发此 skill。它能在当前项目文件夹和公共文件中搜索相似步骤，理解测试代码结构，并匹配对应的AW(天线)映射等参数。
  **触发场景**：找不到相似用例、步骤匹配、代码理解、AW映射搜索、测试步骤相似度分析。
triggers:
  - "找不到相似用例"
  - "搜索相似步骤"
  - "理解测试代码"
  - "查找AW映射"
  - "步骤.*相似"
  - "find similar steps"
  - "search.*code"
  - "AW map"
  - "antenna.*mapping"
references:
  - title: "华为LTE测试用例设计规范"
    url: "https://support.huawei.com/enterprise/doc/DOC1100000001"
    type: documentation
    description: "华为LTE测试用例设计标准和步骤定义"
  - title: "华为LTE参数映射表"
    url: "https://support.huawei.com/enterprise/doc/DOC1100000008"
    type: reference
    description: "LTE各参数与设备配置映射关系"
  - title: "华为TestSuite框架"
    url: "https://support.huawei.com/enterprise/doc/DOC1100000002"
    type: reference
    description: "华为测试框架和步骤库"
assets:
  - name: "step_matcher.py"
    type: script
    description: "步骤匹配算法脚本"
  - name: "aw_mapping.yaml"
    type: config-template
    description: "AW天线参数映射配置模板"
---

# LTE 相似步骤查找器

本 skill 用于在无法直接找到相似用例时，通过多维度搜索和分析找到相似的测试步骤、期望结果和代码模式。

## 工作流程

```
用户输入测试规格 → 语义分析 → 多源搜索 → 步骤匹配 → 代码理解 → 生成推荐
```

### 步骤 1：解析测试规格

用户提供的输入可能是：
- 自然语言描述的测试步骤
- 部分测试规格（前置、步骤、期望）
- 期望结果描述
- 目标功能描述

```yaml
输入示例:
  功能: 测试 UE 附着成功率
  前置: 基站已配置，UE 已开机
  步骤: 
    1. UE 发起 attach 请求
    2. 基站转发到 MME
    3. MME 认证 UE
    4. 建立 EPS 承载
  期望: attach 成功，EMM状态=attached
```

### 步骤 2：语义分析

将输入转换为结构化查询：

```python
# 分析输入类型
input_type = detect_input_type(user_input)
# - full_spec: 完整规格
# - partial_spec: 部分规格  
# - expectation_only: 只有期望
# - natural_description: 自然语言描述

# 提取关键实体
entities = extract_entities(user_input)
# - operation: attach, detach, handover...
# - parameters: band, plmn, tac...
# - expected_results: success, failure, timeout...
```

### 步骤 3：多源搜索

按优先级搜索：

**优先级 1：当前项目文件夹**
```bash
# 搜索所有测试文件
find ./test_cases -name "*.py" -o -name "*.yaml"

# 搜索包含关键词的文件
grep -rl "attach" ./test_cases/
grep -rl "UE.*attach" ./test_cases/

# 搜索相似步骤模式
grep -rn "attach_ue\|ATTACH_REQUEST\|EMM_ATTACHED" ./test_cases/
```

**优先级 2：公共步骤库**
```bash
# 搜索公共步骤定义
find ./common -name "steps_*.py"
find ./library -name "*procedure*"

# 搜索期望结果模式
find ./common -name "expectations_*.yaml"
```

**优先级 3：配置和映射文件**
```bash
# 搜索 AW 天线映射
find . -name "*aw*" -o -name "*antenna*"
find . -name "*mapping*"

# 搜索参数映射
grep -rn "band.*mapping\|AW.*config\|antenna.*param" ./
```

**优先级 4：华为规范文档**
```
参考 Huawei DOC1100000001 获取标准步骤定义
参考 Huawei DOC1100000008 获取参数映射关系
```

### 步骤 4：步骤相似度匹配

使用多维度相似度算法：

```python
def calculate_step_similarity(source_steps, target_steps):
    """
    计算步骤相似度
    
    维度:
    - 操作相似度 (0-40%): 核心操作是否相同
    - 参数相似度 (0-30%): 配置参数是否类似
    - 期望相似度 (0-20%): 期望结果结构是否一致
    - 顺序相似度 (0-10%): 步骤顺序是否可调换
    """
    
    scores = {
        'operation': match_operations(source_steps, target_steps),
        'parameters': match_parameters(source_steps, target_steps),
        'expectation': match_expectations(source, target),
        'sequence': match_sequence(source_steps, target_steps)
    }
    
    final_score = (
        scores['operation'] * 0.4 +
        scores['parameters'] * 0.3 +
        scores['expectation'] * 0.2 +
        scores['sequence'] * 0.1
    )
    
    return final_score, scores
```

### 步骤 5：代码理解

当找到相似代码时，分析其结构：

```python
def understand_test_code(file_path):
    """
    理解测试代码结构
    
    输出:
    - setup_patterns: 初始化模式
    - operation_patterns: 操作模式
    - assertion_patterns: 断言模式
    - cleanup_patterns: 清理模式
    """
    
    with open(file_path, 'r') as f:
        code = f.read()
    
    patterns = {
        'setup': extract_setup_patterns(code),
        'operations': extract_operation_patterns(code),
        'assertions': extract_assertion_patterns(code),
        'cleanup': extract_cleanup_patterns(code)
    }
    
    return patterns
```

### 步骤 6：生成推荐

基于搜索和分析结果，生成新的测试用例建议：

```markdown
## 相似步骤分析结果

### 找到的相似用例
1. `test_ue_attach_basic.py` - 相似度 85%
2. `test_ue_attach_with_auth.py` - 相似度 72%
3. `test_eps_bearer_setup.py` - 相似度 65%

### 步骤模式提取
- **初始化**: LTE_API() → set_band() → attach_ue()
- **核心操作**: authenticate → establish_bearer → verify_attach
- **期望模式**: assert success, EMM_STATE == attached

### 推荐的新用例结构
```python
class TestUEAttachExtended:
    def setUp(self):
        # 从相似用例提取的初始化模式
        self.lte_api = LTE_API()
        self.lte_api.set_band(self.target_band)
        
    def test_attach_with_new_param(self):
        # 替换后的操作
        ue = self.lte_api.attach_ue(
            config={
                'plmn': self.new_plmn,  # 新参数
                'tac': self.new_tac
            }
        )
        self.assertEqual(ue.state, 'ATTACHED')
```

### 参数映射参考
| 用户参数 | 对应AW参数 | 说明 |
|---------|-----------|------|
| band=3 | RxWin=7, TxWin=7 | Band 3 映射 |
| plmn=46001 | MCC=460, MNC=01 | PLMN 映射 |
```

## AW 天线映射搜索

### 常用 AW 映射模式

```yaml
# AW天线参数映射表
band_mappings:
  Band_3:
    earfcn_dl: 1850
    earfcn_ul: 24150
    bandwidth: [5, 10, 15, 20]
    rx_antennas: 2
    tx_antennas: 2
    max_tx_power: 46
    rx_gain: 25
    tx_gain: 25
    
  Band_7:
    earfcn_dl: 2550
    earfcn_ul: 2750
    bandwidth: [5, 10, 15, 20]
    rx_antennas: 2
    tx_antennas: 2
    max_tx_power: 46
    rx_gain: 25
    tx_gain: 25

parameter_mappings:
  tx_power:
    name: "发射功率"
    aw_param: "TxPower"
    range: [-40, 46]
    unit: "dBm"
    
  rx_sensitivity:
    name: "接收灵敏度"
    aw_param: "RxSens"
    range: [-100, -20]
    unit: "dBm"
```

### 搜索 AW 映射

```bash
# 搜索本地映射文件
find . -name "*aw*" -o -name "*antenna*" | xargs grep -l "band"

# 搜索华为文档中的映射
reference: Huawei DOC1100000008

# 搜索代码中的映射使用
grep -rn "AW\|antenna\|mapping" ./test_cases/
```

## 代码模式库

### 常见测试步骤模式

| 模式名称 | 步骤序列 | 适用场景 |
|---------|---------|---------|
| basic_attach | connect → attach → verify | 基础附着测试 |
| auth_attach | connect → auth → attach → verify | 带认证附着 |
| bearer_setup | attach → create_bearer → verify | 承载建立 |
| handover_prep | attach → measurement → handover | 切换准备 |
| data_transfer | attach → bearer → start_tx → measure | 数据传输测试 |

### 期望结果模式

```python
# 成功期望
assert result.success == True
assert ue.state == 'ATTACHED'
assert bearer.status == 'ACTIVE'

# 失败期望
assert result.success == False
assert error_code in ['AUTH_FAILED', 'TIMEOUT', 'REJECTED']

# 参数验证期望
assert signal_quality > -10  # dB
assert throughput > 50  # Mbps
assert latency < 100  # ms
```

## 与 lte-testcase-generator 配合

当本 skill 找到足够的相似信息后：

1. **输出结构化数据** → 传递给 lte-testcase-generator
2. **生成完整用例** → 基于提取的模式生成新用例
3. **标记特殊参数** → 如有AW映射需求，标记需要配置

## 注意事项

1. **优先本地搜索**：先搜当前项目，再搜公共库
2. **记录匹配分数**：便于用户判断推荐质量
3. **保留映射关系**：AW参数映射要明确标注
4. **代码可读性**：提取的模式要有中文注释

## 相关 Skill

- `lte-testcase-generator` - 生成完整测试用例
- `lte-testcase-debugger` - 调试生成的用例
- `lte-cell-creation-huawei` - 华为小区创建
