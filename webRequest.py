# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     WebRequest
   Description :   Network Requests Class
   Author :        J_hao
   date：          2017/7/31
-------------------------------------------------
   Change Activity:
                   2017/7/31:
-------------------------------------------------
"""
__author__ = 'J_hao'

import time

import requests
import urllib3
from lxml import etree
from requests.models import Response
from requests.packages.urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from fake_useragent import UserAgent

ua = UserAgent()


class WebRequest(object):
    name = "web_request"

    def __init__(self, *args, **kwargs):
        self.response = Response()

    def req_header(self):
        _header = {'User-Agent': ua.random,
                   'Accept': '*/*',
                   'Connection': 'keep-alive',
                   'Accept-Language': 'zh-CN,zh;q=0.8'}
        return _header

    def get(self, url, header=None, retry_time=3, retry_interval=2, timeout=5, *args, **kwargs):
        """
        get method
        :param url: target url
        :param header: headers
        :param retry_time: retry time
        :param retry_interval: retry interval
        :param timeout: network timeout
        :return:
        """
        headers = self.req_header()
        if header and isinstance(header, dict):
            headers.update(header)

        for attempt in range(retry_time):
            try:
                print(f"Fetching: {url} (attempt {attempt + 1}/{retry_time})")
                self.response = requests.get(
                    url
                    , headers=headers
                    , timeout=timeout
                    , verify=False
                    , *args
                    , **kwargs
                )
                print(f"Success: {url} - Status: {self.response.status_code}")
                return self
            except Exception as e:
                print(f"Failed: {url} - Error: {str(e)} - Attempt {attempt + 1}/{retry_time}")
                if attempt < retry_time - 1:
                    time.sleep(retry_interval)
                else:
                    # Final attempt failed, return empty response
                    resp = Response()
                    resp.status_code = 200
                    self.response = resp
                    return self

    @property
    def tree(self):
        if self.response.status_code == 200:
            return etree.HTML(self.response.content)
        else:
            return ""

    @property
    def text(self):
        if self.response.status_code == 200:
            return self.response.text
        else:
            return ""

    @property
    def json(self):
        try:
            if self.response.status_code == 200:
                return self.response.json()
            else:
                return ""
        except Exception as e:
            return {}
