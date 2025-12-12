#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统验证脚本
检查代理池系统的各个组件是否正常工作
"""

import sys
import os

def check_module_import():
    """检查模块导入"""
    print("=" * 60)
    print("1. 检查模块导入")
    print("=" * 60)

    modules = [
        ('proxyFetcher', '主程序'),
        ('check_proxy', '代理检测'),
        ('webRequest', '网络请求'),
        ('github_api', 'GitHub API'),
    ]

    all_passed = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}.py - {description}")
        except Exception as e:
            print(f"  ❌ {module_name}.py - {description} - 错误: {e}")
            all_passed = False

    return all_passed


def check_proxy_sources():
    """检查代理源函数"""
    print("\n" + "=" * 60)
    print("2. 检查代理源函数")
    print("=" * 60)

    try:
        import proxyFetcher

        count = 0
        for i in range(1, 21):
            func_name = f'freeProxy{i:02d}'
            if hasattr(proxyFetcher, func_name):
                count += 1
                print(f"  ✅ {func_name}")
            else:
                print(f"  ❌ {func_name} - 缺失")

        print(f"\n总计: {count}/20 个代理源函数")
        return count == 20
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False


def check_detection_methods():
    """检查检测方法"""
    print("\n" + "=" * 60)
    print("3. 检查代理检测方法")
    print("=" * 60)

    try:
        from check_proxy import (
            check_proxy,
            check_proxy_basic,
            check_proxy_fast,
            check_proxy_multiple,
            check_proxy_strict,
            check_proxy_with_retry,
            batch_check_proxies,
            get_proxy_info
        )

        methods = [
            ('check_proxy', '主检测函数'),
            ('check_proxy_basic', '基础检测'),
            ('check_proxy_fast', '快速检测'),
            ('check_proxy_multiple', '多URL检测'),
            ('check_proxy_strict', '严格检测'),
            ('check_proxy_with_retry', '带重试检测'),
            ('batch_check_proxies', '批量检测'),
            ('get_proxy_info', '获取代理信息'),
        ]

        for method_name, description in methods:
            print(f"  ✅ {method_name} - {description}")

        print(f"\n总计: {len(methods)} 种检测方法")
        return True
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False


def check_github_action():
    """检查GitHub Action配置"""
    print("\n" + "=" * 60)
    print("4. 检查GitHub Action配置")
    print("=" * 60)

    workflow_file = '.github/workflows/python-package.yml'
    if os.path.exists(workflow_file):
        print(f"  ✅ 配置文件存在: {workflow_file}")

        with open(workflow_file, 'r') as f:
            content = f.read()

        checks = [
            ('python proxyFetcher.py', '运行命令'),
            ('schedule:', '定时任务'),
            ('cron:', 'Cron表达式'),
            ('GTOKEN', 'Token配置'),
        ]

        for check_str, description in checks:
            if check_str in content:
                print(f"  ✅ {description}: {check_str}")
            else:
                print(f"  ⚠️  {description}: 未找到")

        return True
    else:
        print(f"  ❌ 配置文件不存在: {workflow_file}")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n" + "=" * 60)
    print("5. 检查依赖包")
    print("=" * 60)

    required_packages = [
        'requests',
        'lxml',
        'fake_useragent',
    ]

    all_passed = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 未安装")
            all_passed = False

    return all_passed


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🔍 代理池系统验证")
    print("=" * 60)

    results = []

    # 运行所有检查
    results.append(("模块导入", check_module_import()))
    results.append(("代理源函数", check_proxy_sources()))
    results.append(("检测方法", check_detection_methods()))
    results.append(("GitHub Action", check_github_action()))
    results.append(("依赖包", check_dependencies()))

    # 总结
    print("\n" + "=" * 60)
    print("📊 验证结果总结")
    print("=" * 60)

    passed = 0
    failed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"总计: {passed} 项通过, {failed} 项失败")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 所有检查通过！系统可以正常使用。")
        print("\n📖 使用方法:")
        print("  手动运行: python proxyFetcher.py [GITHUB_TOKEN]")
        print("  自动运行: GitHub Action 每15分钟自动执行")
        return 0
    else:
        print("\n⚠️  部分检查失败，请查看上述信息。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
