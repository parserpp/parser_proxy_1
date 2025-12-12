# -*- coding: utf-8 -*-
"""
代理池系统使用演示
"""

import asyncio
import json
from proxy_manager import ProxyManager
from proxy_pool import ProxyPool, Proxy


async def demo_basic_usage():
    """基本使用演示"""
    print("=" * 60)
    print("基本使用演示")
    print("=" * 60)

    # 创建管理器
    manager = ProxyManager()

    # 获取并验证代理
    print("\n1. 正在获取代理...")
    exported_count = await manager.fetch_and_validate()
    print(f"   ✓ 获取到 {exported_count} 个有效代理")

    # 查看统计信息
    print("\n2. 代理池统计:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

    # 查看最佳代理
    print("\n3. 前 5 个最佳代理:")
    best_proxies = manager.pool.get_best_proxies(5)
    for i, proxy in enumerate(best_proxies, 1):
        print(f"   {i}. {proxy.ip}:{proxy.port} "
              f"[评分: {proxy.score:.2f}, 成功率: {proxy.success_rate:.2%}]")


async def demo_proxy_selection():
    """代理选择演示"""
    print("\n" + "=" * 60)
    print("代理选择演示")
    print("=" * 60)

    # 加载代理池
    pool = ProxyPool({})
    if pool.load_from_file('proxy_pool.json'):
        print(f"\n✓ 已加载 {len(pool.proxies)} 个代理")

        # 获取随机代理
        random_proxy = pool.get_random_proxy()
        if random_proxy:
            print(f"\n随机选择一个代理: {random_proxy.proxy_url}")

        # 获取评分最高的代理
        best_proxy = pool.get_best_proxies(1)[0] if pool.get_best_proxies(1) else None
        if best_proxy:
            print(f"最佳代理: {best_proxy.proxy_url} (评分: {best_proxy.score:.2f})")

        # 导出代理列表
        count = pool.export_to_text('demo_proxies.txt')
        print(f"\n✓ 已导出 {count} 个代理到 demo_proxies.txt")
    else:
        print("\n⚠ 未找到代理池文件，请先运行代理获取")


async def demo_proxy_info():
    """代理信息演示"""
    print("\n" + "=" * 60)
    print("代理详细信息演示")
    print("=" * 60)

    # 创建示例代理
    proxy = Proxy(
        ip='192.168.1.1',
        port=8080,
        score=0.8,
        success_count=10,
        fail_count=2
    )

    print(f"\n代理地址: {proxy.proxy_url}")
    print(f"当前评分: {proxy.score}")
    print(f"成功率: {proxy.success_rate:.2%}")
    print(f"有效状态: {'✓' if proxy.is_valid else '✗'}")

    # 模拟成功/失败
    print("\n模拟使用过程:")
    proxy.update_proxy_score(proxy.proxy_url, success=True, response_time=1.5)
    print(f"  成功响应后评分: {proxy.score:.2f}")

    proxy.update_proxy_score(proxy.proxy_url, success=False)
    print(f"  失败响应后评分: {proxy.score:.2f}")


def demo_read_proxies():
    """读取代理文件演示"""
    print("\n" + "=" * 60)
    print("读取代理文件演示")
    print("=" * 60)

    try:
        # 读取纯文本代理列表
        with open('valid_proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]

        print(f"\n✓ 从 valid_proxies.txt 读取到 {len(proxies)} 个代理")
        print("\n前 10 个代理:")
        for i, proxy in enumerate(proxies[:10], 1):
            print(f"  {i}. {proxy}")

        # 读取JSON格式
        with open('proxy_pool.json', 'r') as f:
            data = json.load(f)

        print(f"\n✓ 从 proxy_pool.json 读取到 {len(data['proxies'])} 个代理数据")
        print(f"  包含评分、成功率、响应时间等详细信息")

    except FileNotFoundError:
        print("\n⚠ 文件不存在，请先运行代理获取")


async def main():
    """主演示函数"""
    print("\n" + "=" * 60)
    print("🎯 代理池系统使用演示")
    print("=" * 60)

    # 演示1: 基本使用
    await demo_basic_usage()

    # 演示2: 代理选择
    await demo_proxy_selection()

    # 演示3: 代理信息
    await demo_proxy_info()

    # 演示4: 读取文件
    demo_read_proxies()

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n📚 更多文档:")
    print("  - README.md: 完整使用说明")
    print("  - QUICKSTART.md: 快速开始指南")
    print("  - OPTIMIZATION_REPORT.md: 优化报告")
    print("\n💡 使用建议:")
    print("  1. 定期运行代理获取以获取最新代理")
    print("  2. 监控代理池统计信息以评估质量")
    print("  3. 根据需要调整 config.py 中的参数")
    print("")


if __name__ == '__main__':
    asyncio.run(main())
