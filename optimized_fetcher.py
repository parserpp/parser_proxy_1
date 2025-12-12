# -*- coding: utf-8 -*-
"""
优化的代理获取器 - 使用异步IO和现代技术
"""

import asyncio
import re
import logging
from typing import List, Generator
from urllib.parse import urljoin, urlparse
from config import PROXY_SOURCES, REQUEST_CONFIG
from async_web import AsyncWebRequest, batch_request
from proxy_pool import Proxy

logger = logging.getLogger(__name__)


class OptimizedProxyFetcher:
    """优化的代理获取器"""

    def __init__(self):
        self.sources = PROXY_SOURCES

    async def fetch_from_kuaidaili(self) -> List[Proxy]:
        """从快代理获取代理"""
        source = self.sources['kuaidaili']
        proxies = []

        if not source['enabled']:
            return proxies

        urls = []
        for page in range(1, source['pages'] + 1):
            for url_template in source['urls']:
                urls.append(url_template.format(page))

        logger.info(f"正在从快代理获取代理，共 {len(urls)} 个URL")

        try:
            results = await batch_request(urls, max_concurrent=5)

            for result in results:
                if isinstance(result, dict) and result.get('tree') is not None:
                    tree = result['tree']
                    for tr in tree.xpath('.//table//tr')[1:]:
                        try:
                            cols = tr.xpath('./td/text()')
                            if len(cols) >= 2:
                                ip = cols[0].strip()
                                port = cols[1].strip()
                                if ip and port:
                                    proxy = Proxy(ip=ip, port=int(port))
                                    proxies.append(proxy)
                        except:
                            continue

        except Exception as e:
            logger.error(f"快代理获取失败: {str(e)}")

        logger.info(f"快代理获取到 {len(proxies)} 个代理")
        return proxies

    async def fetch_from_kxdaili(self) -> List[Proxy]:
        """从开心代理获取代理"""
        source = self.sources['kxdaili']
        proxies = []

        if not source['enabled']:
            return proxies

        logger.info(f"正在从开心代理获取代理")

        try:
            results = await batch_request(source['urls'], max_concurrent=5)

            for result in results:
                if isinstance(result, dict) and result.get('tree') is not None:
                    tree = result['tree']
                    for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                        try:
                            ip = ''.join(tr.xpath('./td[1]/text()')).strip()
                            port = ''.join(tr.xpath('./td[2]/text()')).strip()
                            if ip and port:
                                proxy = Proxy(ip=ip, port=int(port))
                                proxies.append(proxy)
                        except:
                            continue

        except Exception as e:
            logger.error(f"开心代理获取失败: {str(e)}")

        logger.info(f"开心代理获取到 {len(proxies)} 个代理")
        return proxies

    async def fetch_from_ip3366(self) -> List[Proxy]:
        """从云代理获取代理"""
        source = self.sources['ip3366']
        proxies = []

        if not source['enabled']:
            return proxies

        logger.info(f"正在从云代理获取代理")

        try:
            results = await batch_request(source['urls'], max_concurrent=5)

            for result in results:
                if isinstance(result, dict) and result.get('tree') is not None:
                    tree = result['tree']
                    for tr in tree.xpath("//table[@class='table table-bordered table-striped']//tr")[1:]:
                        try:
                            ip = ''.join(tr.xpath('./td[1]/text()')).strip()
                            port = ''.join(tr.xpath('./td[2]/text()')).strip()
                            if ip and port:
                                proxy = Proxy(ip=ip, port=int(port))
                                proxies.append(proxy)
                        except:
                            continue

        except Exception as e:
            logger.error(f"云代理获取失败: {str(e)}")

        logger.info(f"云代理获取到 {len(proxies)} 个代理")
        return proxies

    async def fetch_from_proxy11(self) -> List[Proxy]:
        """从Proxy11获取代理"""
        source = self.sources['proxy11']
        proxies = []

        if not source['enabled']:
            return proxies

        logger.info(f"正在从Proxy11获取代理")

        try:
            async with AsyncWebRequest() as requester:
                result = await requester.get(source['url'])

                if result.get('json') and 'data' in result['json']:
                    for item in result['json']['data']:
                        ip = item.get('ip', '').strip()
                        port = item.get('port', '').strip()
                        if ip and port:
                            try:
                                proxy = Proxy(ip=ip, port=int(port))
                                proxies.append(proxy)
                            except:
                                continue

        except Exception as e:
            logger.error(f"Proxy11获取失败: {str(e)}")

        logger.info(f"Proxy11获取到 {len(proxies)} 个代理")
        return proxies

    async def fetch_from_proxy_list(self) -> List[Proxy]:
        """从Proxy List获取代理"""
        source = self.sources['proxy_list']
        proxies = []

        if not source['enabled']:
            return proxies

        logger.info(f"正在从Proxy List获取代理")

        try:
            results = await batch_request(source['urls'], max_concurrent=5)

            for result in results:
                if isinstance(result, dict) and result.get('text'):
                    text = result['text']
                    # 提取Base64编码的代理
                    proxy_matches = re.findall(r"Proxy\('(.*?)'\)", text)

                    import base64
                    for encoded_proxy in proxy_matches:
                        try:
                            decoded = base64.b64decode(encoded_proxy).decode()
                            parts = decoded.split(':')
                            if len(parts) >= 2:
                                ip = parts[0].strip()
                                port = parts[1].strip()
                                if ip and port:
                                    proxy = Proxy(ip=ip, port=int(port))
                                    proxies.append(proxy)
                        except:
                            continue

        except Exception as e:
            logger.error(f"Proxy List获取失败: {str(e)}")

        logger.info(f"Proxy List获取到 {len(proxies)} 个代理")
        return proxies

    async def fetch_from_proxylistplus(self) -> List[Proxy]:
        """从ProxyListPlus获取代理"""
        source = self.sources['proxylistplus']
        proxies = []

        if not source['enabled']:
            return proxies

        logger.info(f"正在从ProxyListPlus获取代理")

        try:
            results = await batch_request(source['urls'], max_concurrent=3)

            for result in results:
                if isinstance(result, dict) and result.get('text'):
                    text = result['text']
                    # 使用正则提取IP和端口
                    proxy_matches = re.findall(
                        r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',
                        text
                    )

                    for ip, port in proxy_matches:
                        try:
                            proxy = Proxy(ip=ip, port=int(port))
                            proxies.append(proxy)
                        except:
                            continue

        except Exception as e:
            logger.error(f"ProxyListPlus获取失败: {str(e)}")

        logger.info(f"ProxyListPlus获取到 {len(proxies)} 个代理")
        return proxies

    async def fetch_from_dieniao(self) -> List[Proxy]:
        """从蝶鸟代理获取代理"""
        source = self.sources['dieniao']
        proxies = []

        if not source['enabled']:
            return proxies

        logger.info(f"正在从蝶鸟代理获取代理")

        try:
            results = await batch_request(source['urls'], max_concurrent=5)

            for result in results:
                if isinstance(result, dict) and result.get('tree') is not None:
                    tree = result['tree']
                    for li in tree.xpath("//div[@class='free-main col-lg-12 col-md-12 col-sm-12 col-xs-12']/ul/li")[1:]:
                        try:
                            ip = ''.join(li.xpath('./span[1]/text()')).strip()
                            port = ''.join(li.xpath('./span[2]/text()')).strip()
                            if ip and port:
                                proxy = Proxy(ip=ip, port=int(port))
                                proxies.append(proxy)
                        except:
                            continue

        except Exception as e:
            logger.error(f"蝶鸟代理获取失败: {str(e)}")

        logger.info(f"蝶鸟代理获取到 {len(proxies)} 个代理")
        return proxies

    async def fetch_from_qiyun(self) -> List[Proxy]:
        """从齐云代理获取代理"""
        source = self.sources['qiyun']
        proxies = []

        if not source['enabled']:
            return proxies

        logger.info(f"正在从齐云代理获取代理")

        try:
            results = await batch_request(source['urls'], max_concurrent=5)

            for result in results:
                if isinstance(result, dict) and result.get('tree') is not None:
                    tree = result['tree']
                    for tr in tree.xpath("//table[@class='table table-bordered table-striped']//tr")[1:]:
                        try:
                            ip = ''.join(tr.xpath('./td[1]/text()')).strip()
                            port = ''.join(tr.xpath('./td[2]/text()')).strip()
                            if ip and port:
                                proxy = Proxy(ip=ip, port=int(port))
                                proxies.append(proxy)
                        except:
                            continue

        except Exception as e:
            logger.error(f"齐云代理获取失败: {str(e)}")

        logger.info(f"齐云代理获取到 {len(proxies)} 个代理")
        return proxies

    async def fetch_all(self) -> List[Proxy]:
        """从所有源获取代理"""
        logger.info("开始从所有源获取代理")

        tasks = [
            self.fetch_from_kuaidaili(),
            self.fetch_from_kxdaili(),
            self.fetch_from_ip3366(),
            self.fetch_from_proxy11(),
            self.fetch_from_proxy_list(),
            self.fetch_from_proxylistplus(),
            self.fetch_from_dieniao(),
            self.fetch_from_qiyun(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_proxies = []
        for result in results:
            if isinstance(result, list):
                all_proxies.extend(result)

        # 去重
        unique_proxies = {}
        for proxy in all_proxies:
            key = proxy.proxy_url
            if key not in unique_proxies:
                unique_proxies[key] = proxy

        final_proxies = list(unique_proxies.values())

        logger.info(f"总共获取到 {len(final_proxies)} 个不重复的代理")
        return final_proxies


async def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    fetcher = OptimizedProxyFetcher()
    proxies = await fetcher.fetch_all()

    print(f"\n获取到 {len(proxies)} 个代理")
    for i, proxy in enumerate(proxies[:10], 1):
        print(f"{i}. {proxy.ip}:{proxy.port}")


if __name__ == '__main__':
    asyncio.run(main())
