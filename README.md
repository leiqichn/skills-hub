# skill-hub

LTE 测试自动化 Skill 生态系统

## 📚 Skill 列表

### 核心 Skill

| Skill | 说明 | 用途 |
|-------|------|------|
| [lte-testcase-generator](./lte-testcase-generator/) | LTE 测试用例生成器 | 基于相似用例自动生成测试代码 |
| [lte-testcase-debugger](./lte-testcase-debugger/) | LTE 测试用例调试器 | 分析错误、定位问题、生成修复方案 |
| [lte-similar-steps-finder](./lte-similar-steps-finder/) | LTE 相似步骤查找器 | 分层搜索相似测试步骤 |
| [lte-test-runner](./lte-test-runner/) | LTE 测试执行引擎 | 自动执行测试、迭代调试修复 |
| [lte-report-generator](./lte-report-generator/) | LTE 测试报告生成器 | 生成 JSON/Markdown/HTML 测试报告 |
| [lte-cell-creation-huawei](./lte-cell-creation-huawei/) | 华为 LTE 小区创建工具 | 通过 MML 命令创建和配置 LTE 小区 |

### 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    LTE 测试 Skill 生态系统                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐                                        │
│  │ lte-testcase-       │  ← 用户输入测试规格                    │
│  │ generator           │    (case_name/preconditions/steps/expected) │
│  └──────────┬──────────┘                                        │
│             │                                                   │
│             ▼                                                   │
│  ┌─────────────────────┐                                        │
│  │ 第一层搜索           │  在当前项目测试用例库查找相似用例      │
│  │ (用例级相似度)       │                                        │
│  └──────────┬──────────┘                                        │
│             │ 相似度 < 60%                                      │
│             ▼                                                   │
│  ┌─────────────────────┐                                        │
│  │ 第二层搜索           │  调用 lte-similar-steps-finder         │
│  │ (步骤级 + 路径权重) │  逐级向上搜索相似步骤                  │
│  │                     │  当前文件夹 → 父文件夹 → 公共库        │
│  └──────────┬──────────┘                                        │
│             │                                                   │
│             ▼                                                   │
│  ┌─────────────────────┐                                        │
│  │ lte-test-runner     │  ← 执行测试 + 自动调试                │
│  └──────────┬──────────┘                                        │
│             │                                                   │
│             ▼                                                   │
│  ┌─────────────────────┐                                        │
│  │ lte-testcase-       │  ← 分析错误 + 生成修复建议              │
│  │ debugger            │                                        │
│  └──────────┬──────────┘                                        │
│             │                                                   │
│             ▼                                                   │
│  ┌─────────────────────┐                                        │
│  │ lte-report-         │  ← 生成测试报告 (JSON/MD/HTML)        │
│  │ generator           │                                        │
│  └─────────────────────┘                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 分层搜索机制

### 第一层：当前项目用例库
- 在当前项目的测试用例库中查找相似**测试用例**
- 权重：项目内用例 ★★★★★

### 第二层：逐级向上搜索相似**步骤**
当用例相似度 < 60% 时触发：

```
当前文件夹        (★★★ 权重)
    ↓
父文件夹          (★★ 权重)
    ↓
公共库文件夹      (★ 权重，所有公共文件夹权重相同)
    - ../common/
    - ../../shared/steps/
    - /path/to/shared/library/
```

## 📦 安装

将需要的 Skill 目录复制到 OpenClaw 的 skills 目录：

```bash
# 方式1: 克隆整个仓库
git clone https://github.com/leiqichn/skills-hub.git ~/.openclaw/workspace/skillhub

# 方式2: 只复制单个skill
cp -r lte-testcase-generator ~/.openclaw/workspace/skills/
```

## 🚀 快速开始

### 1. 生成测试用例

用户提供测试规格：
- `case_name`: 用例名称
- `preconditions`: 前置步骤
- `test_steps`: 测试步骤
- `expected_results`: 期望结果

AI 自动：
1. 搜索相似用例
2. 如相似度不足，逐级向上搜索相似步骤
3. 生成新的测试代码

### 2. 执行测试

```bash
# 运行单个测试
python lte-test-runner/scripts/test_runner.py run tests/test_sample.py --auto-debug

# 批量执行
python lte-test-runner/scripts/test_runner.py batch test1.py test2.py --auto-debug
```

### 3. 调试迭代

Runner 自动：
- 执行测试
- 捕获错误
- 调用 Debugger 分析
- 生成修复建议
- 迭代重试（最多5次）

## 📁 目录结构

```
skillhub/
├── README.md
├── README.en.md
├── lte-testcase-generator/     # 测试用例生成器
│   ├── SKILL.md
│   └── scripts/
│       └── similarity.py       # 相似度计算
├── lte-testcase-debugger/     # 测试用例调试器
│   ├── SKILL.md
│   └── scripts/
├── lte-similar-steps-finder/  # 相似步骤查找器
│   ├── SKILL.md
│   └── scripts/
├── lte-test-runner/           # 测试执行引擎
│   ├── SKILL.md
│   └── scripts/
│       ├── test_runner.py
│       └── config.yaml
└── lte-cell-creation-huawei/  # 华为小区创建工具
    └── SKILL.md
```

## 🔧 配置

### lte-test-runner 配置

```yaml
# lte-test-runner/scripts/config.yaml
runner:
  max_iterations: 5      # 最大迭代次数
  retry_delay: 2         # 重试间隔(秒)
  test_dir: ./test_cases # 测试目录
  output_dir: ./output   # 输出目录

debugger:
  mode: detailed         # 调试模式
  analysis_timeout: 30    # 分析超时(秒)
```

### LTE_API 配置

确保 `lte_api` 模块路径正确：
```python
import sys
sys.path.insert(0, '/path/to/your/lte_api')
from lte_api import LTE_API
```

## 📖 文档

- [LTE 测试用例生成器](./lte-testcase-generator/SKILL.md)
- [LTE 测试用例调试器](./lte-testcase-debugger/SKILL.md)
- [LTE 相似步骤查找器](./lte-similar-steps-finder/SKILL.md)
- [LTE 测试执行引擎](./lte-test-runner/SKILL.md)
- [华为 LTE 小区创建](./lte-cell-creation-huawei/SKILL.md)

## 🤝 参与贡献

1. Fork 本仓库
2. 新建 Feature 分支
3. 提交代码
4. 新建 Pull Request

## 📄 许可证

MIT License
