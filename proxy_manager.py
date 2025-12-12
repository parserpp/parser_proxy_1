# -*- coding: utf-8 -*-
"""
代理管理器 - 主控制器
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import List

from config import PROXY_POOL_CONFIG, LOG_CONFIG, GITHUB_CONFIG
from optimized_fetcher import OptimizedProxyFetcher
from proxy_pool import ProxyPool
from github_api import update_content, get_content


class ProxyManager:
    """代理管理器"""

    def __init__(self):
        self.fetcher = OptimizedProxyFetcher()
        self.pool = ProxyPool(PROXY_POOL_CONFIG)
        self.setup_logging()

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=getattr(logging, LOG_CONFIG['level']),
            format=LOG_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOG_CONFIG['file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def fetch_and_validate(self) -> int:
        """获取并验证代理"""
        self.logger.info("开始获取代理...")

        # 获取代理
        proxies = await self.fetcher.fetch_all()
        self.logger.info(f"获取到 {len(proxies)} 个原始代理")

        if not proxies:
            self.logger.warning("未获取到任何代理")
            return 0

        # 验证代理
        self.logger.info("开始验证代理...")

        valid_count = 0
        for proxy in proxies:
            # 添加到池中
            self.pool.add_proxy(proxy)

            # 快速验证
            is_valid = await self.pool.health_check(proxy)

            if is_valid:
                self.pool.update_proxy_score(proxy.proxy_url, success=True)
                valid_count += 1
            else:
                self.pool.update_proxy_score(proxy.proxy_url, success=False)

        self.logger.info(f"验证完成，有效代理: {valid_count}/{len(proxies)}")

        # 执行批量健康检查
        await self.pool.batch_health_check(max_concurrent=30)

        # 保存代理池
        self.pool.save_to_file('proxy_pool.json')

        # 导出有效代理
        exported_count = self.pool.export_to_text('valid_proxies.txt')

        return exported_count

    async def sync_to_github(self, token: str = None) -> bool:
        """同步代理到GitHub"""
        if not token:
            token = os.getenv('GITHUB_TOKEN', '')

        if not token:
            self.logger.warning("未提供GitHub token，跳过同步")
            return False

        try:
            # 获取当前GitHub上的代理列表
            self.logger.info("获取GitHub上的代理列表...")
            github_content = get_content(
                GITHUB_CONFIG['owner'],
                GITHUB_CONFIG['repo'],
                GITHUB_CONFIG['file_path'],
                token
            )

            # 合并本地和GitHub的代理
            github_proxies = set()
            if github_content:
                github_proxies = set(line.strip() for line in github_content.split('\n') if line.strip())

            # 获取本地有效代理
            local_proxies = {proxy.proxy_url for proxy in self.pool.get_best_proxies(1000)}

            # 合并并去重
            all_proxies = github_proxies.union(local_proxies)

            # 生成新的代理列表
            new_content = '\n'.join(sorted(all_proxies))

            # 更新GitHub
            self.logger.info(f"同步 {len(all_proxies)} 个代理到GitHub...")
            update_content(
                GITHUB_CONFIG['owner'],
                GITHUB_CONFIG['repo'],
                GITHUB_CONFIG['file_path'],
                _token=token,
                _content_not_base64=new_content,
                _commit_msg=f"Update proxy list - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            self.logger.info("成功同步到GitHub")
            return True

        except Exception as e:
            self.logger.error(f"同步到GitHub失败: {str(e)}")
            return False

    def get_statistics(self) -> dict:
        """获取统计信息"""
        return self.pool.get_statistics()

    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print("代理池统计信息")
        print("="*50)
        print(f"总代理数量: {stats['total_proxies']}")
        print(f"有效代理数量: {stats['valid_proxies']}")
        print(f"已禁用代理: {stats['banned_proxies']}")
        print(f"平均成功率: {stats['success_rate']:.2%}")
        print(f"平均评分: {stats['avg_score']:.2f}")
        print("="*50)

    def print_best_proxies(self, count: int = 20):
        """打印最佳代理"""
        best_proxies = self.pool.get_best_proxies(count)
        print(f"\n前 {count} 个最佳代理:")
        print("-" * 80)
        print(f"{'排名':<6} {'代理地址':<25} {'评分':<8} {'成功率':<10} {'响应时间':<10}")
        print("-" * 80)

        for i, proxy in enumerate(best_proxies, 1):
            print(f"{i:<6} {proxy.proxy_url:<25} {proxy.score:.2f}<8 {proxy.success_rate:.2%}<10 {proxy.response_time:.2f}s<10")

        print("-" * 80)


async def run_once():
    """运行一次获取和验证"""
    manager = ProxyManager()

    # 加载现有代理池
    manager.pool.load_from_file('proxy_pool.json')

    # 获取并验证代理
    exported_count = await manager.fetch_and_validate()

    # 打印统计信息
    manager.print_statistics()

    # 打印最佳代理
    manager.print_best_proxies(20)

    # 同步到GitHub
    if len(sys.argv) > 1:
        await manager.sync_to_github(sys.argv[1])

    return exported_count


async def run_continuously(interval_hours: int = 6):
    """持续运行模式"""
    manager = ProxyManager()

    # 加载现有代理池
    manager.pool.load_from_file('proxy_pool.json')

    while True:
        try:
            manager.logger.info(f"开始新一轮代理获取 (间隔: {interval_hours}小时)")

            # 获取并验证代理
            exported_count = await manager.fetch_and_validate()

            # 打印统计信息
            manager.print_statistics()

            # 同步到GitHub
            if len(sys.argv) > 1:
                await manager.sync_to_github(sys.argv[1])

            manager.logger.info(f"本轮完成，导出 {exported_count} 个有效代理")
            manager.logger.info(f"等待 {interval_hours} 小时后进行下一轮...")

            # 等待指定时间
            await asyncio.sleep(interval_hours * 3600)

        except KeyboardInterrupt:
            manager.logger.info("用户中断，退出")
            break
        except Exception as e:
            manager.logger.error(f"运行时发生错误: {str(e)}")
            # 等待1小时后重试
            await asyncio.sleep(3600)


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
代理池管理器

用法:
    python proxy_manager.py [GitHub_TOKEN]           # 运行一次
    python proxy_manager.py continuous [GitHub_TOKEN] # 持续运行

环境变量:
    GITHUB_TOKEN                                     # GitHub访问令牌
        """)
        return

    if len(sys.argv) > 1 and sys.argv[1] == 'continuous':
        # 持续运行模式
        asyncio.run(run_continuously(interval_hours=6))
    else:
        # 运行一次
        asyncio.run(run_once())


if __name__ == '__main__':
    main()
