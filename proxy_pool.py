# -*- coding: utf-8 -*-
"""
代理池管理模块
"""

import time
import json
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class Proxy:
    """代理数据类"""
    ip: str
    port: int
    score: float = 1.0
    success_count: int = 0
    fail_count: int = 0
    last_success_time: Optional[datetime] = None
    last_fail_time: Optional[datetime] = None
    response_time: float = 0.0
    country: str = ''
    anonymity: str = ''
    proxy_type: str = 'http'

    @property
    def success_rate(self) -> float:
        """计算成功率"""
        total = self.success_count + self.fail_count
        if total == 0:
            return 0.0
        return self.success_count / total

    @property
    def is_valid(self) -> bool:
        """检查代理是否有效"""
        return self.score >= 0.3 and self.success_rate >= 0.5

    @property
    def proxy_url(self) -> str:
        """获取代理URL"""
        return f"{self.ip}:{self.port}"


class ProxyPool:
    """代理池管理类"""

    def __init__(self, config: Dict):
        self.config = config
        self.proxies: Dict[str, Proxy] = {}
        self.banned_proxies: Set[str] = set()
        self.last_health_check = 0

    def add_proxy(self, proxy: Proxy) -> bool:
        """添加代理到池中"""
        proxy_key = proxy.proxy_url

        # 检查是否已禁用
        if proxy_key in self.banned_proxies:
            return False

        # 检查是否超出最大容量
        if len(self.proxies) >= self.config['max_size']:
            # 移除评分最低的代理
            min_score_proxy = min(self.proxies.values(), key=lambda p: p.score)
            del self.proxies[min_score_proxy.proxy_url]

        # 检查是否已存在
        if proxy_key in self.proxies:
            existing = self.proxies[proxy_key]
            # 更新评分
            existing.success_count = proxy.success_count
            existing.fail_count = proxy.fail_count
            existing.response_time = proxy.response_time
            existing.last_success_time = proxy.last_success_time
            existing.last_fail_time = proxy.last_fail_time
            return True

        self.proxies[proxy_key] = proxy
        return True

    def remove_proxy(self, proxy_key: str):
        """移除代理"""
        if proxy_key in self.proxies:
            del self.proxies[proxy_key]

    def update_proxy_score(self, proxy_key: str, success: bool, response_time: float = 0):
        """更新代理评分"""
        if proxy_key not in self.proxies:
            return

        proxy = self.proxies[proxy_key]
        now = datetime.now()

        if success:
            proxy.success_count += 1
            proxy.last_success_time = now
            proxy.response_time = response_time
            # 成功时增加评分
            proxy.score = min(1.0, proxy.score + 0.1)
        else:
            proxy.fail_count += 1
            proxy.last_fail_time = now
            # 失败时减少评分
            proxy.score = max(0.0, proxy.score - 0.2)

        # 检查是否需要禁用
        if proxy.fail_count >= self.config['ban_threshold']:
            self.ban_proxy(proxy_key)

    def ban_proxy(self, proxy_key: str):
        """禁用代理"""
        self.banned_proxies.add(proxy_key)
        self.remove_proxy(proxy_key)
        logger.warning(f"代理已禁用: {proxy_key}")

    def decay_scores(self):
        """评分衰减"""
        decay_factor = self.config['score_decay']
        for proxy in self.proxies.values():
            proxy.score *= decay_factor

    async def health_check(self, proxy: Proxy) -> bool:
        """健康检查"""
        test_urls = self.config.get('test_urls', ['http://httpbin.org/ip'])

        async with aiohttp.ClientSession() as session:
            for test_url in test_urls:
                try:
                    proxy_url = f"http://{proxy.ip}:{proxy.port}"
                    async with session.get(
                        test_url,
                        proxy=proxy_url,
                        timeout=aiohttp.ClientTimeout(total=5),
                        ssl=False
                    ) as response:
                        if response.status == 200:
                            proxy.last_success_time = datetime.now()
                            return True
                except:
                    continue

        proxy.last_fail_time = datetime.now()
        return False

    async def batch_health_check(self, max_concurrent: int = 20):
        """批量健康检查"""
        if not self.proxies:
            return

        logger.info(f"开始批量健康检查，共 {len(self.proxies)} 个代理")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def check_proxy_wrapper(proxy):
            async with semaphore:
                return await self.health_check(proxy)

        tasks = [check_proxy_wrapper(proxy) for proxy in self.proxies.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_count = sum(1 for r in results if r is True)
        logger.info(f"健康检查完成，有效代理: {valid_count}/{len(self.proxies)}")

    def get_best_proxies(self, count: int = 10) -> List[Proxy]:
        """获取最佳代理列表"""
        valid_proxies = [p for p in self.proxies.values() if p.is_valid]
        # 按评分和成功率排序
        sorted_proxies = sorted(
            valid_proxies,
            key=lambda p: (p.score, p.success_rate),
            reverse=True
        )
        return sorted_proxies[:count]

    def get_random_proxy(self) -> Optional[Proxy]:
        """随机获取一个有效代理"""
        valid_proxies = [p for p in self.proxies.values() if p.is_valid]
        if not valid_proxies:
            return None
        import random
        return random.choice(valid_proxies)

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self.proxies)
        valid = sum(1 for p in self.proxies.values() if p.is_valid)
        banned = len(self.banned_proxies)

        return {
            'total_proxies': total,
            'valid_proxies': valid,
            'banned_proxies': banned,
            'success_rate': sum(p.success_rate for p in self.proxies.values()) / max(total, 1),
            'avg_score': sum(p.score for p in self.proxies.values()) / max(total, 1),
        }

    def save_to_file(self, filename: str = 'proxy_pool.json'):
        """保存代理池到文件"""
        data = {
            'proxies': {k: asdict(v) for k, v in self.proxies.items()},
            'banned_proxies': list(self.banned_proxies),
            'timestamp': datetime.now().isoformat(),
        }

        # 转换datetime为字符串
        for proxy_data in data['proxies'].values():
            if proxy_data['last_success_time']:
                proxy_data['last_success_time'] = proxy_data['last_success_time'].isoformat()
            if proxy_data['last_fail_time']:
                proxy_data['last_fail_time'] = proxy_data['last_fail_time'].isoformat()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"代理池已保存到文件: {filename}")

    def load_from_file(self, filename: str = 'proxy_pool.json'):
        """从文件加载代理池"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 转换字符串为datetime
            for proxy_data in data.get('proxies', {}).values():
                if proxy_data['last_success_time']:
                    proxy_data['last_success_time'] = datetime.fromisoformat(proxy_data['last_success_time'])
                if proxy_data['last_fail_time']:
                    proxy_data['last_fail_time'] = datetime.fromisoformat(proxy_data['last_fail_time'])

            self.proxies = {}
            for k, v in data.get('proxies', {}).items():
                self.proxies[k] = Proxy(**v)

            self.banned_proxies = set(data.get('banned_proxies', []))

            logger.info(f"已从文件加载代理池: {len(self.proxies)} 个代理")
            return True

        except Exception as e:
            logger.error(f"加载代理池失败: {str(e)}")
            return False

    def export_to_text(self, filename: str = 'valid_proxies.txt') -> int:
        """导出有效代理到文本文件"""
        valid_proxies = self.get_best_proxies(1000)

        with open(filename, 'w', encoding='utf-8') as f:
            for proxy in valid_proxies:
                f.write(f"{proxy.ip}:{proxy.port}\n")

        logger.info(f"已导出 {len(valid_proxies)} 个有效代理到 {filename}")
        return len(valid_proxies)
