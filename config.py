# -*- coding: utf-8 -*-
"""
配置文件
"""

# 代理验证配置
PROXY_CHECK_CONFIG = {
    'timeout': 5,  # 验证超时时间（秒）
    'retry_times': 2,  # 验证重试次数
    'test_urls': [  # 测试URL列表
        'http://httpbin.org/ip',
        'http://icanhazip.com/',
        'http://ipinfo.io/ip'
    ],
    'min_success_rate': 0.5,  # 最小成功率阈值
}

# 代理池配置
PROXY_POOL_CONFIG = {
    'max_size': 1000,  # 最大代理数量
    'min_score': 0.3,  # 最小评分阈值
    'health_check_interval': 300,  # 健康检查间隔（秒）
    'score_decay': 0.95,  # 评分衰减因子
    'ban_threshold': 3,  # 连续失败次数阈值
}

# 请求配置
REQUEST_CONFIG = {
    'timeout': 10,  # 请求超时
    'retry_times': 3,  # 重试次数
    'retry_interval': 2,  # 重试间隔（秒）
    'max_concurrent': 50,  # 最大并发数
    'rate_limit': 10,  # 每秒请求数限制
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'proxy_pool.log',
}

# GitHub配置
GITHUB_CONFIG = {
    'owner': 'parserpp',
    'repo': 'ip_ports',
    'file_path': '/proxyinfo.txt',
    'commit_msg': 'Update proxy list',
}

# 代理源网站配置（修复失效网站）
PROXY_SOURCES = {
    'kuaidaili': {
        'urls': [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ],
        'pages': 5,
        'enabled': True,
    },
    'kxdaili': {
        'urls': [
            'http://www.kxdaili.com/dailiip.html',
            'http://www.kxdaili.com/dailiip/1/2.html',
            'http://www.kxdaili.com/dailiip/1/3.html',
            'http://www.kxdaili.com/dailiip/1/4.html',
        ],
        'enabled': True,
    },
    'ip3366': {
        'urls': [
            'http://www.ip3366.net/free/?stype=1',
            'http://www.ip3366.net/free/?stype=1&page=2',
            'http://www.ip3366.net/free/?stype=1&page=3',
        ],
        'enabled': True,
    },
    'proxy11': {
        'url': 'https://proxy11.com/api/demoweb/proxy.json',
        'enabled': True,
    },
    'proxy_list': {
        'urls': ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 5)],
        'enabled': True,
    },
    'proxylistplus': {
        'urls': ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-%s' % n for n in range(1, 4)],
        'enabled': True,
    },
    'dieniao': {
        'urls': [
            'https://www.dieniao.com/FreeProxy.html',
            'https://www.dieniao.com/FreeProxy/2.html',
        ],
        'enabled': True,
    },
    'qiyun': {
        'urls': [
            'https://proxy.ip3366.net/free/?action=china&page=%s' % n for n in range(1, 6)
        ],
        'enabled': True,
    },
}
