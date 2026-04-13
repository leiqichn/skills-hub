#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LTE FDD 测试用例相似度计算和代码生成工具
"""

import re
import os
from datetime import datetime


def parse_test_case_content(content):
    """解析测试用例内容，提取关键信息"""
    info = {
        'name': '',
        'class_name': '',
        'test_methods': [],
        'setup': '',
        'teardown': '',
        'full_text': content
    }

    # 提取测试类名
    class_match = re.search(r'class\s+(Test\w+)', content)
    if class_match:
        info['class_name'] = class_match.group(1)

    # 提取测试方法名
    method_matches = re.findall(r'def\s+(test_\w+)', content)
    info['test_methods'] = method_matches

    # 提取 setUp 内容
    setup_match = re.search(r'def\s+setUp\(self\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    if setup_match:
        info['setup'] = setup_match.group(1).strip()

    # 提取 tearDown 内容
    teardown_match = re.search(r'def\s+tearDown\(self\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    if teardown_match:
        info['teardown'] = teardown_match.group(1).strip()

    return info


def calculate_similarity(query_info, case_info):
    """
    计算两个用例的相似度
    返回 0-100 的分数
    """
    score = 0.0

    # 功能相似度 (40%)
    func_sim = _text_similarity(
        query_info.get('case_name', ''),
        case_info.get('class_name', '') + ' ' + ' '.join(case_info.get('test_methods', []))
    )
    score += func_sim * 0.4

    # 步骤相似度 (30%)
    step_sim = _text_similarity(
        query_info.get('test_steps', ''),
        case_info.get('full_text', '')
    )
    score += step_sim * 0.3

    # 期望相似度 (20%)
    exp_sim = _text_similarity(
        query_info.get('expected_results', ''),
        case_info.get('full_text', '')
    )
    score += exp_sim * 0.2

    # 上下文相似度 (10%)
    ctx_query = query_info.get('preconditions', '') + ' ' + query_info.get('recovery_steps', '')
    ctx_case = case_info.get('setup', '') + ' ' + case_info.get('teardown', '')
    ctx_sim = _text_similarity(ctx_query, ctx_case)
    score += ctx_sim * 0.1

    return round(score * 100, 2)


def _text_similarity(text1, text2):
    """简单的文本相似度计算（基于词重叠）"""
    if not text1 or not text2:
        return 0.0

    # 分词
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))

    if not words1 or not words2:
        return 0.0

    # Jaccard 相似度
    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union) if union else 0.0


def find_similar_cases(query_info, case_files, top_n=3):
    """
    在所有测试用例文件中查找最相似的用例
    """
    results = []

    for file_path in case_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            case_info = parse_test_case_content(content)
            similarity = calculate_similarity(query_info, case_info)

            results.append({
                'file_path': file_path,
                'similarity': similarity,
                'case_info': case_info
            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

    # 按相似度排序
    results.sort(key=lambda x: x['similarity'], reverse=True)

    return results[:top_n]


def generate_test_code(query_info, template_case_info):
    """基于模板用例生成新的测试代码"""
    case_name = query_info.get('case_name', 'NewTestCase')
    preconditions = query_info.get('preconditions', '')
    test_steps = query_info.get('test_steps', '')
    recovery_steps = query_info.get('recovery_steps', '')
    expected_results = query_info.get('expected_results', '')

    # 从用例名称提取类别和标识
    class_name = _extract_class_name(case_name)
    test_id = _extract_test_id(case_name)

    # 格式化时间
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 生成代码
    code = f'''# -*- coding: utf-8 -*-
"""
LTE FDD 测试用例
自动生成用例: {case_name}
生成时间: {timestamp}
"""

import unittest
import time


class Test{class_name}(unittest.TestCase):
    """
    {case_name}
    """

    def setUp(self):
        """前置步骤"""
        {preconditions if preconditions else "# TODO: 添加前置步骤"}

    def test_{test_id}(self):
        """
        测试步骤: {test_steps}
        期望结果: {expected_results}
        """
        # TODO: 填写测试逻辑
        pass

    def tearDown(self):
        """恢复步骤"""
        {recovery_steps if recovery_steps else "# TODO: 添加恢复步骤"}
'''

    return code


def _extract_class_name(case_name):
    """从用例名称提取类名"""
    # 移除特殊字符，保留中文和英文
    name = re.sub(r'[^\w\u4e00-\u9fff]', '', case_name)
    if len(name) > 20:
        name = name[:20]
    return name or 'NewTest'


def _extract_test_id(case_name):
    """从用例名称提取测试方法标识"""
    # 转为拼音或英文标识
    name = re.sub(r'[^\w]', '_', case_name)
    name = re.sub(r'_+', '_', name)
    return name.lower() or 'new_test'


def find_test_files(directory):
    """查找目录下所有可能的测试用例文件"""
    test_files = []
    patterns = ['test_*.py', '*_test.py', 'Test*.py']

    for root, dirs, files in os.walk(directory):
        for pattern in patterns:
            for filename in files:
                if re.match(pattern.replace('*', '.*'), filename):
                    test_files.append(os.path.join(root, filename))

    return test_files
