#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LTE FDD 测试用例调试辅助工具
"""

import re
import subprocess
import os


def run_nosetest(test_path, verbose=True):
    """运行 nosetest 并返回结果"""
    cmd = ['nosetests', '-v']
    if verbose:
        cmd.append('-vv')
    cmd.append(test_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Test timeout after 120s',
            'success': False
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }


def parse_error(output):
    """解析测试输出，提取错误信息"""
    error_info = {
        'type': None,
        'message': None,
        'traceback': [],
        'file': None,
        'line': None,
        'suggestions': []
    }

    # 提取错误类型
    error_match = re.search(r'(AssertionError|ImportError|NameError|AttributeError|SyntaxError|TimeoutError|ConnectionError)', output)
    if error_match:
        error_info['type'] = error_match.group(1)

    # 提取错误消息
    msg_match = re.search(r'(AssertionError|Error):?\s*(.+)', output)
    if msg_match:
        error_info['message'] = msg_match.group(2).strip()

    # 提取堆栈跟踪
    tb_match = re.search(r'Traceback \(most recent call last\):(.+?)(?=\n\n|\Z)', output, re.DOTALL)
    if tb_match:
        error_info['traceback'] = tb_match.group(1).strip().split('\n')

    # 提取文件和行号
    file_match = re.search(r'File "([^"]+)", line (\d+)', output)
    if file_match:
        error_info['file'] = file_match.group(1)
        error_info['line'] = int(file_match.group(2))

    # 根据错误类型生成建议
    error_type = error_info['type']
    if error_type == 'AssertionError':
        error_info['suggestions'] = [
            '检查期望值是否合理',
            '确认比较逻辑是否正确',
            '考虑添加更详细的断言消息',
            '检查数据是否为 None'
        ]
    elif error_type == 'ImportError':
        error_info['suggestions'] = [
            '检查 import 语句是否正确',
            '确认模块路径是否在 sys.path 中',
            '检查模块是否已安装'
        ]
    elif error_type == 'NameError':
        error_info['suggestions'] = [
            '检查变量名拼写是否正确',
            '确认变量在使用前已赋值',
            '检查是否有作用域问题'
        ]
    elif error_type == 'AttributeError':
        error_info['suggestions'] = [
            '检查对象是否有该属性/方法',
            '确认 API 调用方式是否正确',
            '检查是否需要先初始化对象'
        ]
    elif error_type == 'TimeoutError':
        error_info['suggestions'] = [
            '增加超时等待时间',
            '检查异步操作是否正常',
            '确认网络连接是否稳定'
        ]
    elif error_type == 'ConnectionError':
        error_info['suggestions'] = [
            '检查网络连接配置',
            '确认设备 IP 和端口是否正确',
            '检查防火墙设置'
        ]

    return error_info


def generate_fix_snippet(error_info):
    """根据错误信息生成修复代码片段"""
    error_type = error_info['type']

    fixes = {
        'AssertionError': '''
# 防御性断言示例
result = perform_action()
self.assertIsNotNone(result, "Action returned None")
if hasattr(result, 'value'):
    self.assertGreater(result.value, 0, f"Value {result.value} should be positive")
''',
        'ImportError': '''
# 添加模块路径示例
import sys
sys.path.insert(0, '/path/to/module')
from module_name import ClassName
''',
        'NameError': '''
# 确保变量已定义
self.variable = initial_value()  # 在 setUp 中初始化
''',
        'AttributeError': '''
# 检查对象属性
if hasattr(self.obj, 'method'):
    self.obj.method()
else:
    # 使用替代方法或正确初始化
    self.obj = initialize_object()
''',
        'TimeoutError': '''
# 增加超时配置
self.api.set_timeout(30)  # 30 seconds
self.api.retry_count = 3
''',
        'ConnectionError': '''
# 网络连接配置
self.lte_api.connect(
    host='192.168.1.100',
    port=5000,
    timeout=30
)
'''
    }

    return fixes.get(error_type, '# No specific fix suggestion available')


def create_debug_report(error_info, test_file, test_method):
    """创建调试报告"""
    report = f'''
=== LTE 测试用例调试报告 ===
测试文件: {test_file}
测试方法: {test_method}

错误类型: {error_info['type'] or 'Unknown'}
错误信息: {error_info['message'] or 'No message'}

'''
    if error_info['file']:
        report += f'问题位置: {error_info["file"]}, 行 {error_info["line"]}\n'

    if error_info['traceback']:
        report += '\n堆栈跟踪:\n'
        for line in error_info['traceback'][-5:]:  # 只显示最后 5 行
            report += f'  {line}\n'

    if error_info['suggestions']:
        report += '\n修复建议:\n'
        for i, suggestion in enumerate(error_info['suggestions'], 1):
            report += f'  {i}. {suggestion}\n'

    return report
