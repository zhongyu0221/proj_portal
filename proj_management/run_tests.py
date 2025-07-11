#!/usr/bin/env python
"""
测试运行脚本
用于运行项目的所有测试
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def run_tests():
    """运行所有测试"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # 运行所有测试
    failures = test_runner.run_tests([
        'userprofiles.tests',
        'project.tests',
    ])
    
    return failures

def run_specific_tests():
    """运行特定测试"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # 运行特定测试
    test_patterns = [
        'userprofiles.tests.UserProfileModelTest',
        'project.tests.ProjectModelTest',
        'project.tests.TaskModelTest',
    ]
    
    failures = test_runner.run_tests(test_patterns)
    return failures

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--specific':
        failures = run_specific_tests()
    else:
        failures = run_tests()
    
    sys.exit(bool(failures)) 