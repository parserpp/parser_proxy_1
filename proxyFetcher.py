# -*- coding: utf-8 -*-

import os
import re
import sys
from time import sleep

import github_api
from check_proxy import check_proxy
from webRequest import WebRequest


def saveData(text):
    with open("proxyData.txt", "a") as f:
        f.write(text)
        f.write("\n")


def freeProxy01():
    """
    米扑代理 https://proxy.mimvcom/
    :return:
    """
    url_list = [
        'https://proxy.mimvcom/freeopen?proxy=in_hp',
        'https://proxy.mimvcom/freeopen?proxy=out_hp',
        'https://proxy.mimvcom/freeopen?proxy=in_socks',
        'https://proxy.mimvcom/freeopen?proxy=out_socks',
        'https://proxy.mimvcom/freesecret',
        'https://proxy.mimvcom/freesole',
        'https://proxy.mimvcom/freeopen'
    ]
    port_img_mage = {'DMxMjg': '3128', 'Dgw': '80', 'DgwODA': '8080',
                     'DgwOA': '808', 'DgwMDA': '8000', 'Dg4ODg': '8888',
                     'DgwODE': '8081', 'Dk5OTk': '9999'}

    for url in url_list:
        html_tree = WebRequest().get(url).tree
        # print(url + "---->" + str(html_tree))
        if html_tree != "":
            for tr in html_tree.xpath(".//table[@class='mimvp-tbl free-proxylist-tbl']/tbody/tr"):
                try:
                    ip = ''.join(tr.xpath('./td[2]/text()'))
                    port_img = ''.join(tr.xpath('./td[3]/img/@src')).split("port=")[-1]
                    # port = port_img_mage(port_img[14:].replace('O0O', ''))
                    key = port_img[14:].replace('O0O', '')
                    port = port_img_mage[key]
                    if port:
                        yield '%s:%s' % (ip, port)
                except Exception as e:
                    print(e)


def freeProxy02():
    """
    代理66 http://www.66icn/
    :return:
    """
    url_list = [
        'http://www.66icn/mo.php',
        'http://www.66icn/nmtq.php?getnum=300&isp=0&anonymoustype=4&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip',
        'http://www.66icn/nmtq.php?getnum=300&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip'
    ]
    for url in url_list:
        resptext = WebRequest().get(url, timeout=10).text
        # print(url + "---->" + str(resptext))
        if resptext != "":
            proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})', resptext)
            for proxy in proxies:
                yield proxy


def freeProxy03():
    """ 开心代理 """
    target_urls = [
        # """高匿代理  """
        'http://www.kxdaili.com/dailiihtml',
        'http://www.kxdaili.com/dailiip.html',
        'http://www.kxdaili.com/dailiip/1/2.html',
        'http://www.kxdaili.com/dailiip/1/3.html',
        'http://www.kxdaili.com/dailiip/1/4.html',
        # """普匿代理"""
        'http://www.kxdaili.com/dailiip/2/1.html',
        'http://www.kxdaili.com/dailiip/2/2.html'
    ]
    for url in target_urls:
        tree = WebRequest().get(url).tree
        # print(url + "---->" + str(tree))
        if tree != "":
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)


def freeProxy04():
    """ 蝶鸟IP """
    url_list = [
        'https://www.dieniao.com/FreeProxy.html',
        'https://www.dieniao.com/FreeProxy/2.html',
        'https://www.dieniao.com/FreeProxy/3.html',
        'https://www.dieniao.com/FreeProxy/4.html'
    ]
    for url in url_list:
        _tree = WebRequest().get(url).tree
        # print(url + "---->" + str(_tree))
        if _tree != "":
            for li in _tree.xpath("//div[@class='free-main col-lg-12 col-md-12 col-sm-12 col-xs-12']/ul/li")[1:]:
                ip = "".join(li.xpath('./span[1]/text()')).strip()
                port = "".join(li.xpath('./span[2]/text()')).strip()
                yield "%s:%s" % (ip, port)


def freeProxy05(page_count=4):
    """ 快代理 https://www.kuaidaili.com """
    url_pattern = [
        'https://www.kuaidaili.com/free/inha/{}/',
        'https://www.kuaidaili.com/free/intr/{}/'
    ]
    url_list = []
    for page_index in range(1, page_count + 1):
        for pattern in url_pattern:
            url_list.append(pattern.format(page_index))

    for url in url_list:
        tree = WebRequest().get(url).tree
        # print(url + "---->" + str(tree))
        if tree != "":
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])


def freeProxy06():
    """ PROXY11 https://proxy11.com 主页还有可用的 """

    ## 取消约束条件
    # url = "https://proxy11.com/api/demoweb/proxy.json?country=hk&speed=2000"
    url = "https://proxy11.com/api/demoweb/proxy.json"
    try:
        resp_json = WebRequest().get(url).json
        # print(url + "---->" + str(len(resp_json)) +"----" +str(resp_json))
        if resp_json != "":
            for each in resp_json.get("data", []):
                yield "%s:%s" % (each.get("ip", ""), each.get("port", ""))
    except Exception as e:
        print(e)


def freeProxy07():
    """ 云代理 """
    urls = [
        'http://www.ip3366.net/free/?stype=1',
        'http://www.ip3366.net/free/?stype=1&page=2',
        'http://www.ip3366.net/free/?stype=1&page=3',
        'http://www.ip3366.net/free/?stype=2'
    ]
    ## 方案一: 正则文字方式
    # for url in urls:
    #     r = WebRequest().get(url)
    #     proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
    #     for proxy in proxies:
    #         yield ":".join(proxy)
    ## 方案二: xpath方案
    for url in urls:
        tree = WebRequest().get(url).tree
        # print(url + "---->" + str(tree))
        if tree != "":
            for tr in tree.xpath("//table[@class='table table-bordered table-striped']//tr")[1:]:
                # print(tr.xpath('./td[1]/text()')[0].strip()
                #       + ":"
                #       + tr.xpath('./td[2]/text()')[0].strip())
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)


# TODO 可以优化,使用xpath方式工作
def freeProxy08():
    """ 小幻代理 . 有提取API"""
    urls = [
        'https://iihuan.me/address/5Lit5Zu9.html'
    ]
    for url in urls:
        r = WebRequest().get(url)
        proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', r.text)
        for proxy in proxies:
            yield ":".join(proxy)


#  TODO 不可访问 可以优化：5页，可加条件，高匿等
def freeProxy09(page_count=1):
    """ 高可用全球免费代理ip库"""
    for i in range(1, page_count + 1):
        url = 'http://ijiangxianli.com/?country=中国&page={}'.format(i)
        html_tree = WebRequest().get(url).tree
        # print(url + "---->" + str(html_tree))
        if html_tree != "":
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()


# TODO 可以提取IP和端口. https://www.89icn/tqdl.html?num=800&address=&kill_address=&port=&kill_port=&isp=
def freeProxy10():
    """ 89免费代理 """
    urls = [
        'https://www.89icn/index_1.html',
        'https://www.89icn/index_2.html',
        'https://www.89icn/index_3.html',
        'https://www.89icn/index_4.html',
        'https://www.89icn/index_5.html',
        'https://www.89icn/index_6.html',
        'https://www.89icn/index_7.html',
    ]
    for url in urls:
        r = WebRequest().get(url)
        if r.response.status_code == 200:
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            for proxy in proxies:
                yield ':'.join(proxy)


def freeProxy11():
    """
    https://proxy-list.org/english/index.php
    :return:
    """
    urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
    request = WebRequest()
    import base64
    for url in urls:
        resptext = request.get(url).text
        # print(url+"------>"+resptext)
        if resptext != "":
            proxies = re.findall(r"Proxy\('(.*?)'\)", resptext)
            for proxy in proxies:
                yield base64.b64decode(proxy).decode()


# TODO 还有https/socket/google
def freeProxy12():
    """ proxylist+ """
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-%s' % n for n in range(1, 7)]

    request = WebRequest()
    for url in urls:
        resptext = request.get(url).text
        # print(url+"---->"+resptext)
        if resptext != "":
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', resptext)
            for proxy in proxies:
                yield ':'.join(proxy)


def freeProxy13():
    """
    PzzQz https://pzzqz.com/
    """
    from requests import Session
    from lxml import etree
    session = Session()
    try:
        index_resp = session.get("https://pzzqz.com/", timeout=20, verify=False).text
        x_csrf_token = re.findall('X-CSRFToken": "(.*?)"', index_resp)
        # print(x_csrf_token)
        if x_csrf_token:
            data = {"http": "on", "ping": "3000", "country": "cn", "ports": ""}
            proxy_resp = session.post("https://pzzqz.com/", verify=False,
                                      headers={"X-CSRFToken": x_csrf_token[0]}, json=data).json()
            tree = etree.HTML(proxy_resp["proxy_html"])
            for tr in tree.xpath("//tr"):
                ip = "".join(tr.xpath("./td[1]/text()"))
                port = "".join(tr.xpath("./td[2]/text()"))
                yield "%s:%s" % (ip, port)
    except Exception as e:
        print(e)


def freeProxy14():
    """
    墙外网站 cn-proxy
    :return:
    """
    urls = [
        'http://cn-proxy.com/',
        'http://cn-proxy.com/archives/218'
    ]
    request = WebRequest()
    for url in urls:
        resptext = request.get(url).text
        if resptext != "":
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', resptext)
            for proxy in proxies:
                yield ':'.join(proxy)


def freeProxy15():
    """ 齐云代理"""
    urls = [
        'https://proxy.ip3366.net/free/?action=china&page=%s' % n for n in range(1, 11)
    ]
    ##  xpath方案
    for url in urls:
        tree = WebRequest().get(url).tree
        # print(url + "---->" + str(tree))
        if tree != "":
            for tr in tree.xpath("//table[@class='table table-bordered table-striped']//tr")[1:]:
                # print(tr.xpath('./td[1]/text()')[0].strip()
                #       + ":"
                #       + tr.xpath('./td[2]/text()')[0].strip())
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)


# #  TODO 解析规则需要进一步优化
# def freeProxy16():
#     """ new net time proxy : http://nntime.com/"""
#     urls = [
#         'http://nntime.com/proxy-list-%02d.htm' % n for n in range(1, 16)
#     ]
#     ##  xpath方案
#     for url in urls:
#         tree = WebRequest().get(url).tree
#         #print(url + "---->" + str(tree))
#         if tree != "":
#             for tr in tree.xpath("//table[@id='proxylist']//tr")[1:]:
#                 # print(tr.xpath('./td[1]/text()')[0].strip()
#                 #       + ":"
#                 #       + tr.xpath('./td[2]/text()')[0].strip())
#                 ip = "".join(tr.xpath('./td[1]/text()')).strip()
#                 port = "".join(tr.xpath('./td[2]/text()')).strip()
#                 yield "%s:%s" % (ip, port)


# http://www.nimadaili.com/gaoni/

lproxy_list = []
final_list = []


def runAllwork():
    global lproxy_list
    # 0. get token
    # print(str(len(sys.argv)) + "--->" + str(sys.argv))
    token = os.getenv('GITHUB_TOKEN', "")
    if len(sys.argv) > 1:
        token = sys.argv[1]
    # 1. get info https://github.com/parserpp/ip_ports/blob/main/proxyinfo.txt
    con = github_api.get_content("parserpp", "ip_ports", "/proxyinfo.txt", token)
    # 2. convery info to memory data
    lproxy_list = con.split("\n")
    print(len(lproxy_list))
    # print(type(lproxy_list))
    # 3. request newest data from net

    for proxys in (
            freeProxy01(), freeProxy02()
            , freeProxy03(), freeProxy04()
            , freeProxy05(), freeProxy06()
            , freeProxy07(), freeProxy08()
            , freeProxy09(), freeProxy10()
            , freeProxy11(), freeProxy12()
            , freeProxy13(), freeProxy14()
            , freeProxy15()
    ):
        for oneProxy in proxys:
            if oneProxy not in lproxy_list:
                lproxy_list.append(oneProxy)
                print("found new proxy:" + oneProxy)
    print("request net address, ips count:" + str(len(lproxy_list)))
    # # 4. ip alive check
    # for proxy_info in lproxy_list:
    #     # print("will check: "+ str(proxy_info))
    #     if check_proxy(proxy_info):
    #         if proxy_info not in final_list:
    #             final_list.append(proxy_info)
    # print("ip check over, ips count:" + str(len(final_list)))
    # 5.update data
    update_data = ""
    for _s in lproxy_list:
        if _s != "":
            update_data = update_data + _s + "\n"
    print("will send data to github libs")
    saveData(update_data)
    github_api.update_content("parserpp", "ip_ports", "/proxyinfo.txt"
                              , _token=token
                              , _content_not_base64=update_data)
    print("update  github libs over")


if __name__ == '__main__':
    runAllwork()
