#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LTE Test Report Generator - 测试报告生成器

作者: JARVIS
版本: 1.0.0
"""

import os
import sys
import json
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

__version__ = "1.0.0"


# ============================================================================
# 数据结构
# ============================================================================

class TestStatus(Enum):
    """测试状态"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    SKIPPED = "SKIPPED"
    UNKNOWN = "UNKNOWN"


@dataclass
class TestCaseResult:
    """单个测试用例结果"""
    name: str
    class_name: str
    file_path: str
    status: TestStatus
    duration: float
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'class_name': self.class_name,
            'file_path': self.file_path,
            'status': self.status.value,
            'duration': self.duration,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'timestamp': self.timestamp
        }


@dataclass
class TestSuiteResult:
    """测试套件结果"""
    name: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration: float = 0.0
    test_cases: List[TestCaseResult] = field(default_factory=list)
    timestamp: float = 0.0
    
    @property
    def pass_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0.0
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'total': self.total,
            'passed': self.passed,
            'failed': self.failed,
            'errors': self.errors,
            'skipped': self.skipped,
            'duration': self.duration,
            'pass_rate': self.pass_rate,
            'test_cases': [tc.to_dict() for tc in self.test_cases],
            'timestamp': self.timestamp
        }


@dataclass
class TestReport:
    """完整测试报告"""
    project_name: str
    environment: str
    test_suites: List[TestSuiteResult] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_tests(self) -> int:
        return sum(s.total for s in self.test_suites)
    
    @property
    def total_passed(self) -> int:
        return sum(s.passed for s in self.test_suites)
    
    @property
    def total_failed(self) -> int:
        return sum(s.failed for s in self.test_suites)
    
    @property
    def total_errors(self) -> int:
        return sum(s.errors for s in self.test_suites)
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time > 0 else 0.0
    
    @property
    def overall_pass_rate(self) -> float:
        total = self.total_passed + self.total_failed + self.total_errors
        return (self.total_passed / total * 100) if total > 0 else 0.0
    
    def to_dict(self) -> dict:
        return {
            'project_name': self.project_name,
            'environment': self.environment,
            'total_tests': self.total_tests,
            'total_passed': self.total_passed,
            'total_failed': self.total_failed,
            'total_errors': self.total_errors,
            'overall_pass_rate': self.overall_pass_rate,
            'duration': self.duration,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'test_suites': [s.to_dict() for s in self.test_suites],
            'metadata': self.metadata
        }


# ============================================================================
# 报告生成器
# ============================================================================

class ReportGenerator:
    """LTE 测试报告生成器"""
    
    def __init__(self, project_name: str = "LTE Test Project",
                 environment: str = "真实基站"):
        self.project_name = project_name
        self.environment = environment
        self.report = TestReport(
            project_name=project_name,
            environment=environment
        )
    
    def add_test_result(self, name: str, class_name: str, file_path: str,
                       status: TestStatus, duration: float,
                       error_type: str = None, error_message: str = None):
        """添加单个测试结果"""
        tc = TestCaseResult(
            name=name,
            class_name=class_name,
            file_path=file_path,
            status=status,
            duration=duration,
            error_type=error_type,
            error_message=error_message,
            timestamp=time.time()
        )
        
        suite_name = os.path.basename(file_path)
        suite = self._find_or_create_suite(suite_name)
        suite.test_cases.append(tc)
    
    def _find_or_create_suite(self, name: str) -> TestSuiteResult:
        """查找或创建测试套件"""
        for suite in self.report.test_suites:
            if suite.name == name:
                return suite
        
        suite = TestSuiteResult(name=name, timestamp=time.time())
        self.report.test_suites.append(suite)
        return suite
    
    def finalize(self):
        """完成报告生成，更新统计"""
        self.report.start_time = min(s.timestamp for s in self.report.test_suites) if self.report.test_suites else time.time()
        self.report.end_time = time.time()
        
        for suite in self.report.test_suites:
            suite.total = len(suite.test_cases)
            suite.passed = sum(1 for tc in suite.test_cases if tc.status == TestStatus.PASSED)
            suite.failed = sum(1 for tc in suite.test_cases if tc.status == TestStatus.FAILED)
            suite.errors = sum(1 for tc in suite.test_cases if tc.status == TestStatus.ERROR)
            suite.skipped = sum(1 for tc in suite.test_cases if tc.status == TestStatus.SKIPPED)
            suite.duration = sum(tc.duration for tc in suite.test_cases)
    
    def generate_json(self, output_path: str = None) -> str:
        """生成 JSON 格式报告"""
        self.finalize()
        
        if output_path:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.report.to_dict(), f, indent=2, ensure_ascii=False)
            return output_path
        
        return json.dumps(self.report.to_dict(), indent=2, ensure_ascii=False)
    
    def generate_markdown(self, output_path: str = None) -> str:
        """生成 Markdown 格式报告"""
        self.finalize()
        
        r = self.report
        timestamp = datetime.fromtimestamp(r.start_time).strftime('%Y-%m-%d %H:%M:%S')
        
        status_emoji = {
            'PASSED': '✅',
            'FAILED': '❌',
            'ERROR': '⚠️',
            'TIMEOUT': '⏱️',
            'SKIPPED': '⏭️',
            'UNKNOWN': '❓'
        }
        
        md = f"""# {r.project_name} - 测试报告

## 📊 概览

| 指标 | 值 |
|------|-----|
| 项目名称 | {r.project_name} |
| 测试环境 | {r.environment} |
| 测试时间 | {timestamp} |
| 总测试数 | {r.total_tests} |
| 通过 | {r.total_passed} |
| 失败 | {r.total_failed} |
| 错误 | {r.total_errors} |
| 通过率 | {r.overall_pass_rate:.1f}% |
| 总耗时 | {r.duration:.2f}s |

"""
        
        if r.total_tests > 0:
            passed_pct = r.total_passed / r.total_tests * 100
            failed_pct = r.total_failed / r.total_tests * 100
            error_pct = r.total_errors / r.total_tests * 100
            
            md += f"""```
通过率: {passed_pct:.1f}% {'█' * int(passed_pct/5)}{'░' * (20-int(passed_pct/5))}
失败率: {failed_pct:.1f}% {'█' * int(failed_pct/5)}{'░' * (20-int(failed_pct/5))}
错误率: {error_pct:.1f}% {'█' * int(error_pct/5)}{'░' * (20-int(error_pct/5))}
```

"""
        
        for suite in r.test_suites:
            md += f"\n## 📁 {suite.name}\n\n"
            md += f"| 用例 | 状态 | 耗时 | 错误 |\n|------|------|------|------|\n"
            
            for tc in suite.test_cases:
                emoji = status_emoji.get(tc.status.value, '❓')
                error_info = tc.error_message[:30] + '...' if tc.error_message and len(tc.error_message) > 30 else tc.error_message or '-'
                md += f"| {tc.class_name}::{tc.name} | {emoji} {tc.status.value} | {tc.duration:.2f}s | {error_info} |\n"
            
            md += f"\n**套件汇总:** 通过 {suite.passed}/{suite.total} ({suite.pass_rate:.1f}%) | 耗时 {suite.duration:.2f}s\n"
        
        failed_cases = [tc for s in r.test_suites for tc in s.test_cases if tc.status == TestStatus.FAILED]
        if failed_cases:
            md += "\n## 🔍 失败用例详情\n\n"
            for tc in failed_cases:
                md += f"""### ❌ {tc.class_name}::{tc.name}

- **文件:** `{tc.file_path}`
- **耗时:** {tc.duration:.2f}s
- **错误类型:** {tc.error_type or 'Unknown'}
- **错误信息:** 
```
{tc.error_message or 'No error message'}
```

"""
        
        md += f"""

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*LTE Test Report Generator v{__version__}*
"""
        
        if output_path:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md)
            return output_path
        
        return md


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LTE Test Report Generator')
    parser.add_argument('--project', default='LTE Test', help='项目名称')
    parser.add_argument('--env', default='真实基站', help='测试环境')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['json', 'md'], default='md', help='输出格式')
    
    args = parser.parse_args()
    
    gen = ReportGenerator(args.project, args.env)
    
    # 添加示例数据
    gen.add_test_result('test_ue_attach', 'TestUEAttach', 'test_attach.py',
                        TestStatus.PASSED, 1.23)
    gen.add_test_result('test_throughput', 'TestThroughput', 'test_throughput.py',
                        TestStatus.PASSED, 12.45)
    gen.add_test_result('test_handover', 'TestHandover', 'test_handover.py',
                        TestStatus.FAILED, 5.67, 'AssertionError', 'Expected RSRP > -100, got -120')
    
    if args.format == 'json':
        output = gen.generate_json(args.output)
    else:
        output = gen.generate_markdown(args.output)
    
    if args.output:
        print(f"报告已保存: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
