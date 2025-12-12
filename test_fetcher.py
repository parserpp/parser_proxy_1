# -*- coding: utf-8 -*-
"""
测试代理获取器
"""

import asyncio
import logging
from optimized_fetcher import OptimizedProxyFetcher

logging.basicConfig(level=logging.INFO)


async def test_fetcher():
    """测试代理获取器"""
    fetcher = OptimizedProxyFetcher()

    # 测试单个源
    print("测试快代理...")
    proxies = await fetcher.fetch_from_kuaidaili()
    print(f"快代理获取到: {len(proxies)} 个代理")
    for i, proxy in enumerate(proxies[:5], 1):
        print(f"  {i}. {proxy.ip}:{proxy.port}")

    # 测试所有源
    print("\n测试所有源...")
    all_proxies = await fetcher.fetch_all()
    print(f"总共获取到: {len(all_proxies)} 个代理")

    return all_proxies


if __name__ == '__main__':
    asyncio.run(test_fetcher())
