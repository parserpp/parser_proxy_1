# -*- coding: utf-8 -*-
"""
代理检测模块
提供多种方法检测代理的有效性
"""

import requests
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import time

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from fake_useragent import UserAgent

ua = UserAgent()

HEADER = {'User-Agent': ua.random,
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}

# 检测URL列表
TEST_URLS = [
    "http://icanhazip.com/",
    "http://httpbin.org/ip",
    "http://ipinfo.io/ip",
    "http://httpbin.org/get",
]

# 支持的代理类型
SUPPORTED_PROXY_TYPES = ['http', 'https']


def req(url, ip_proxy, proxy_type='http'):
    """单个URL检测"""
    try:
        proxy_ip = {
            'http': f"http://{ip_proxy}",
            'https': f"https://{ip_proxy}",
        }

        response = requests.get(
            url,
            headers=HEADER,
            timeout=5,  # 增加超时时间
            proxies=proxy_ip,
            verify=False
        )

        ip = ip_proxy.split(":")[0]
        if response.status_code == 200:
            # 检查响应内容是否包含代理IP
            try:
                # 尝试解析JSON响应
                json_data = response.json()
                if 'origin' in json_data:
                    origin = json_data['origin']
                    if isinstance(origin, str) and ip in origin:
                        return True, response.text
                    elif isinstance(origin, list) and any(ip in o for o in origin):
                        return True, response.text
                elif 'ip' in json_data and ip in json_data['ip']:
                    return True, response.text
            except:
                # 如果不是JSON，检查文本内容
                if ip in response.text:
                    return True, response.text

        return False, response.text
    except requests.exceptions.Timeout:
        print(f'超时---[{ip_proxy}]连接超时')
        return False, 'timeout'
    except requests.exceptions.ConnectionError:
        print(f'连接错误---[{ip_proxy}]连接被拒绝')
        return False, 'connection_error'
    except Exception as e:
        print(f'异常---[{ip_proxy}]{str(e)}')
        return False, str(e)


def check_proxy_basic(proxy):
    """基础检测：检测一个URL"""
    result, _ = req(TEST_URLS[0], proxy)
    return result


def check_proxy_multiple(proxy):
    """多URL检测：检测多个URL，必须全部通过才算成功"""
    success_count = 0
    for url in TEST_URLS:
        try:
            result, _ = req(url, proxy)
            if result:
                success_count += 1
            time.sleep(0.1)  # 避免请求过快
        except:
            continue

    # 至少需要一半的URL检测通过
    return success_count >= len(TEST_URLS) // 2


def check_proxy_fast(proxy):
    """快速检测：只检测一个URL，快速判断"""
    result, _ = req(TEST_URLS[1], proxy)  # 使用 httpbin.org/ip
    return result


def check_proxy_strict(proxy):
    """严格检测：所有URL都必须通过"""
    for url in TEST_URLS:
        try:
            result, _ = req(url, proxy)
            if not result:
                return False
            time.sleep(0.2)
        except:
            return False
    return True


def check_proxy_with_retry(proxy, retry_times=2):
    """带重试的检测"""
    for attempt in range(retry_times):
        if check_proxy_basic(proxy):
            return True
        time.sleep(0.5)
    return False


def get_proxy_info(proxy):
    """获取代理详细信息"""
    info = {
        'proxy': proxy,
        'type': 'http',
        'country': 'unknown',
        'response_time': 0,
        'anonymity': 'unknown'
    }

    try:
        proxy_ip = proxy.split(':')[0]
        proxy_port = proxy.split(':')[1]

        # 测试响应时间
        start_time = time.time()
        result, response_text = req(TEST_URLS[1], proxy)
        end_time = time.time()

        if result:
            info['response_time'] = round(end_time - start_time, 2)
            info['status'] = 'working'

            # 尝试解析响应获取更多信息
            try:
                json_data = json.loads(response_text)
                if 'origin' in json_data:
                    info['country'] = 'detected'
            except:
                pass
        else:
            info['status'] = 'failed'

    except Exception as e:
        info['status'] = f'error: {str(e)}'

    return info


def batch_check_proxies(proxies, check_method='basic', max_workers=10):
    """批量检测代理"""
    import concurrent.futures

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        if check_method == 'basic':
            futures = {executor.submit(check_proxy_basic, proxy): proxy for proxy in proxies}
        elif check_method == 'multiple':
            futures = {executor.submit(check_proxy_multiple, proxy): proxy for proxy in proxies}
        elif check_method == 'fast':
            futures = {executor.submit(check_proxy_fast, proxy): proxy for proxy in proxies}
        elif check_method == 'strict':
            futures = {executor.submit(check_proxy_strict, proxy): proxy for proxy in proxies}
        else:
            futures = {executor.submit(check_proxy_basic, proxy): proxy for proxy in proxies}

        for future in concurrent.futures.as_completed(futures):
            proxy = futures[future]
            try:
                result = future.result()
                results.append((proxy, result))
            except Exception as e:
                results.append((proxy, False))

    return results


def check_proxy(proxy, method='basic'):
    """主检测函数"""
    if method == 'basic':
        return check_proxy_basic(proxy)
    elif method == 'multiple':
        return check_proxy_multiple(proxy)
    elif method == 'fast':
        return check_proxy_fast(proxy)
    elif method == 'strict':
        return check_proxy_strict(proxy)
    else:
        return check_proxy_basic(proxy)


if __name__ == '__main__':
    # 测试用例
    test_proxies = [
        "3.211.17.212:80",
        "103.103.3.6:8080",
        "61.37.223.152:8080",
    ]

    print("测试代理检测功能...")
    for proxy in test_proxies:
        print(f"\n检测代理: {proxy}")
        print(f"  基础检测: {check_proxy(proxy, 'basic')}")
        print(f"  快速检测: {check_proxy(proxy, 'fast')}")
        print(f"  多URL检测: {check_proxy(proxy, 'multiple')}")
        print(f"  详细信息: {get_proxy_info(proxy)}")

