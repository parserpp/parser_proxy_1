# -*- coding: utf-8 -*-
"""
异步网络请求模块
"""

import asyncio
import time
from typing import Optional, Dict, Any
import aiohttp
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

ua = UserAgent()


class AsyncWebRequest:
    """异步HTTP请求类"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'User-Agent': ua.random}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """异步GET请求"""
        if not self.session:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': ua.random}
            ) as session:
                return await self._request(session, url, **kwargs)
        else:
            return await self._request(self.session, url, **kwargs)

    async def _request(self, session: aiohttp.ClientSession, url: str, **kwargs) -> Dict[str, Any]:
        """执行HTTP请求"""
        retry_times = kwargs.pop('retry_times', 3)
        retry_interval = kwargs.pop('retry_interval', 2)

        for attempt in range(retry_times):
            try:
                async with session.get(url, **kwargs) as response:
                    content = await response.read()
                    text = content.decode('utf-8', errors='ignore')

                    # 尝试解析JSON
                    json_data = {}
                    try:
                        json_data = await response.json()
                    except:
                        pass

                    # 解析HTML
                    tree = None
                    try:
                        from lxml import etree
                        tree = etree.HTML(content)
                    except:
                        pass

                    return {
                        'status_code': response.status,
                        'text': text,
                        'json': json_data,
                        'tree': tree,
                        'content': content,
                        'url': str(response.url),
                    }

            except Exception as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{retry_times}): {url} - {str(e)}")
                if attempt < retry_times - 1:
                    await asyncio.sleep(retry_interval)
                else:
                    return {
                        'status_code': 0,
                        'text': '',
                        'json': {},
                        'tree': None,
                        'content': b'',
                        'url': url,
                        'error': str(e),
                    }

    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """异步POST请求"""
        if not self.session:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': ua.random}
            ) as session:
                return await self._post_request(session, url, **kwargs)
        else:
            return await self._post_request(self.session, url, **kwargs)

    async def _post_request(self, session: aiohttp.ClientSession, url: str, **kwargs) -> Dict[str, Any]:
        """执行POST请求"""
        retry_times = kwargs.pop('retry_times', 3)
        retry_interval = kwargs.pop('retry_interval', 2)

        for attempt in range(retry_times):
            try:
                async with session.post(url, **kwargs) as response:
                    content = await response.read()
                    text = content.decode('utf-8', errors='ignore')

                    # 尝试解析JSON
                    json_data = {}
                    try:
                        json_data = await response.json()
                    except:
                        pass

                    return {
                        'status_code': response.status,
                        'text': text,
                        'json': json_data,
                        'content': content,
                        'url': str(response.url),
                    }

            except Exception as e:
                logger.warning(f"POST请求失败 (尝试 {attempt + 1}/{retry_times}): {url} - {str(e)}")
                if attempt < retry_times - 1:
                    await asyncio.sleep(retry_interval)
                else:
                    return {
                        'status_code': 0,
                        'text': '',
                        'json': {},
                        'content': b'',
                        'url': url,
                        'error': str(e),
                    }


async def batch_request(urls: list, max_concurrent: int = 10) -> list:
    """批量异步请求"""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch(url):
        async with semaphore:
            async with AsyncWebRequest() as requester:
                return await requester.get(url)

    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)
