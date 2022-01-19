# -*- coding: utf-8 -*-

import requests
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from fake_useragent import UserAgent

ua = UserAgent()

HEADER = {'User-Agent': ua.random,
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}


def req(url, ip_proxy):
    try:
        proxy_ip = {
            'http': "http://" + ip_proxy,
            'https': "https://" + ip_proxy,
        }
        # print('使用代理的IP:', proxy_ip)
        response = requests.get(url
                                , headers=HEADER
                                , timeout=3
                                , proxies=proxy_ip
                                , verify=False
                                )
        # print(response)
        ip = ip_proxy.split(":")[0]
        if response.status_code == 200:
            if ip in response.text:
                print('200---[' + str(ip_proxy) + ']IP有效')
                return True
            else:
                print('200---[' + str(ip_proxy) + ']IP无效')
        else:
            print(str(response.status_code) + '---[' + str(ip_proxy) + ']IP无效')
    except Exception as e:
        # print(e.args[0])
        print('异常---[' + str(ip_proxy) + ']IP无效')
        return False


def check_proxy(proxy):
    if req("http://icanhazip.com/", proxy) != True:
        return req("http://httpbin.org/ip", proxy)
    else:
        return True


if __name__ == '__main__':
    check_proxy("3.211.17.212:80")
    check_proxy("103.103.3.6:8080")
    check_proxy("61.37.223.152:8080")
