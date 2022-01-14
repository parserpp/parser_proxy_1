# -*- coding: utf-8 -*-
import base64
import json
import os

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

"""
https://github.com/NetCapture/PyGithubApi

"""
_VERSION = "v1.0.0"
_NAME = "sanbo"
_EMAIL = "sanbo.xyz@gmail.com"
_COMMIT_MSG = "commit by python api[{}].".format(_VERSION)
isDebug = False

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# support full path: README.md、/Users/root/Desktop/test.txt, and so on
# @TODO not support: ~/Desktop/test.txt
def read_file_as_str(file_path):
    # 判断路径文件存在
    if not os.path.isfile(file_path):
        if isDebug:
            print("文件不存在")
        return ""
    st = open(file_path).read()
    if isDebug:
        print("result: " + st)
    return st


def getGithubRequestHeader(__token):
    __headers = {
        "User-Agent": "Github createFile By python api",
        "Content-Type": "charset=UTF-8",
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token " + __token,
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    return __headers


def prepareContent(_content_base64ed: str = "", _content_not_base64: str = "", _filename: str = ""):
    # content. from args. priority:
    # 1. text about base64ed.           need do nothing
    # 2. text about has not base64.     need base64
    # 3. file name.                     need read content,and base64
    if _content_base64ed != "":
        return _content_base64ed;
    elif _content_not_base64 != "":
        return str(base64.b64encode(_content_not_base64.encode("utf-8")), "utf-8")
    elif _filename != "":
        need_base64 = read_file_as_str(_filename)
        return str(base64.b64encode(need_base64.encode("utf-8")), "utf-8")
    else:
        return ""


#  masure prefix
def preparePath(info, make_prefix):
    if info.startswith(make_prefix) != True:
        info = make_prefix + info
    return info


#  support file: public/private repo , result: single file sha
#  support dir: public/private repo ,  result: all files sha
def getSha(_owner, _repo, _path=""
           , __token=os.getenv('GITHUB_TOKEN', "")):
    # check path, the data which not startwith "/", will append "/" add the header
    _path = preparePath(_path, make_prefix="/")
    sha_url = "https://api.github.com/repos/{}/{}/contents{}".format(_owner, _repo, _path)
    _headers = getGithubRequestHeader(__token)
    resp = requests.request("get", url=sha_url, headers=_headers, verify=False)
    rsult = resp.text
    if isDebug:
        print("getSha url: " + sha_url)
        print("getSha result: " + rsult)
    return rsult


def create_file(_owner, _repo, _path=""
                , _token=os.getenv('GITHUB_TOKEN', "")
                , _filename: str = ""
                , _content_not_base64: str = ""
                , _content_base64ed: str = ""
                , _commit_msg=_COMMIT_MSG
                , _name=_NAME
                , _email=_EMAIL
                ):
    # content. from args. priority:
    # 1. text about base64ed.           need do nothing
    # 2. text about has not base64.     need base64
    # 3. file name.                     need read content,and base64
    content_final = prepareContent(_content_base64ed, _content_not_base64, _filename)

    # check path, the data which not startwith "/", will append "/" add the header
    _path = preparePath(_path, make_prefix="/")

    create_url = "https://api.github.com/repos/{}/{}/contents{}".format(_owner, _repo, _path)
    # TODO: format error.
    # data = "{\"content\":\"{}\",\"message\":\"{}\" ,\"committer\":{ \"name\":\"{}\",\"email\":\"{}\" }}".format(
    #     content_final, _commit_msg, _name, _email)
    _data = "{\"content\":\"" + content_final + "\",\"message\":\"" + _commit_msg + "\" ,\"committer\":{ \"name\":\"" + _name + "\",\"email\":\"" + _email + "\" }}"
    _headers = getGithubRequestHeader(_token)
    resp = requests.request(method="put", url=create_url, data=_data, headers=_headers, verify=False)
    result = resp.text
    if isDebug:
        print("create_file url:" + create_url)
        print("create_file data:" + _data)
        print("create_file resp:" + result)
    return result


#  support private/public repo file
def update_content(_owner, _repo, _path=""
                   , _token=os.getenv('GITHUB_TOKEN', "")
                   , _filename: str = ""
                   , _content_not_base64: str = ""
                   , _content_base64ed: str = ""
                   , _commit_msg=_COMMIT_MSG
                   , _name=_NAME
                   , _email=_EMAIL
                   ):
    # content. from args. priority:
    # 1. text about base64ed.           need do nothing
    # 2. text about has not base64.     need base64
    # 3. file name.                     need read content,and base64
    content_final = prepareContent(_content_base64ed, _content_not_base64, _filename)

    # check path, the data which not startwith "/", will append "/" add the header
    _path = preparePath(_path, make_prefix="/")
    update_url = "https://api.github.com/repos/{}/{}/contents{}".format(_owner, _repo, _path)
    sha_text = getSha(_owner, _repo, _path, __token=_token)
    sha_json = json.loads(sha_text)
    # need support dir's data. @TODO if dir will crash
    sha = sha_json['sha']
    # if isDebug:
    #     print("sha：" + sha)
    _data = "{\"content\":\"" + content_final + "\",\"message\":\"" + _commit_msg + "\" ,\"sha\":\"" + sha + "\" ,\"committer\":{ \"name\":\"" + _name + "\",\"email\":\"" + _email + "\" }}"
    # _data = "{\"content\":\"" + content_final + "\",\"message\":\"" + _commit_msg + "\", \"sha\":\"" + sha + "\" }"
    _headers = getGithubRequestHeader(_token)
    resp = requests.request(method="put", url=update_url, data=_data, headers=_headers, verify=False)
    result = resp.text
    if isDebug:
        print("update_content url:" + update_url)
        print(_headers)
        print("update_content data:" + _data)
        print("update_content resp:" + result)
    return result


def delete_file(_owner, _repo, _path=""
                , _token=os.getenv('GITHUB_TOKEN', "")
                , _commit_msg=_COMMIT_MSG
                , _name=_NAME
                , _email=_EMAIL
                ):
    # check path, the data which not startwith "/", will append "/" add the header
    _path = preparePath(_path, make_prefix="/")
    update_url = "https://api.github.com/repos/{}/{}/contents{}".format(_owner, _repo, _path)
    sha_text = getSha(_owner, _repo, _path, __token=_token)
    sha_json = json.loads(sha_text)
    # need support dir's data. @TODO if dir will crash
    sha = sha_json['sha']

    _data = "{\"message\":\"" + _commit_msg + "\" ,\"sha\":\"" + sha + "\" ,\"committer\":{ \"name\":\"" + _name + "\",\"email\":\"" + _email + "\" }}"
    # _data = "{\"message\":\""+_commit_msg+"\", \"sha\":\""+sha+"\" }"
    _headers = getGithubRequestHeader(_token)
    resp = requests.request(method="delete", url=update_url, data=_data, headers=_headers, verify=False)
    result = resp.text
    if isDebug:
        print("delete_file url:" + update_url)
        print(_headers)
        print("delete_file data:" + _data)
        print("delete_file resp:" + result)

    return result


def get_content(_owner, _repo, _path="", _token=os.getenv('GITHUB_TOKEN', "")):
    # check path, the data which not startwith "/", will append "/" add the header
    _path = preparePath(_path, make_prefix="/")
    info = getSha(_owner, _repo, _path, _token)
    if isDebug:
        print("get_content sha info:"+info)
    sha_json = json.loads(info)
    if isDebug:
        print(sha_json)
    # suport base64
    ct = sha_json['content']
    eds = sha_json['encoding']
    if "base64" == eds:
        res = str(base64.b64decode(ct.encode("utf-8")), "utf-8")
        return res
    return ct


if __name__ == '__main__':
    # test create
    # tes: str = "hello"
    # uPs: str = "python更新内容1"
    # base64Text()
    # testReadFile()
    # testCreateFiles(_content_not_base64)
    # testGetSha()
    # testUpdateContent(uPs)
    # testDeleteFileTest()

    # get info
    # https://github.com/parserpp/ip_ports/blob/main/proxyinfo.txt
    tss = get_content("parserpp", "ip_ports", "/proxyinfo.txt")
    print(tss)
    # sas = getSha("parserpp", "ip_ports", "/proxyinfo.txt")
    # print(sas)


#
# def testDeleteFileTest():
#     #  public repo demo: https://github.com/hhhaiai/Git_result/tree/main/tt
#     delete_file("hhhaiai", "Git_result", "/tt/update.txt")
#     #  private repo demo: https://github.com/parserpp/data/blob/main/appList.csv
#     delete_file("parserpp", "data", "/update.txt")
#
# def testUpdateContent(uPs):
#     #  public repo demo: https://github.com/hhhaiai/Git_result/tree/main/tt
#     update_content("hhhaiai", "Git_result", "/tt/update.txt", _content_not_base64=uPs)
#     #  private repo demo: https://github.com/parserpp/data/blob/main/appList.csv
#     update_content("parserpp", "data", "/update.txt", _content_not_base64=uPs)
#
# def testGetSha():
#     #  File: public repo demo: https://github.com/hhhaiai/Git_result/blob/main/tt/test1.txt
#     getSha("hhhaiai", "Git_result", "/tt/test1.txt")
#     #  File: private repo demo: https://github.com/parserpp/data/blob/main/README.md
#     getSha("parserpp", "data", "/README.md")
#     # Dir
#     getSha("hhhaiai", "Git_result", "/")
#     getSha("parserpp", "data", "/")
#     # testReadFile()
#
#
# def testCreateFiles(_content_not_base64):
#     #  public repo demo: https://github.com/hhhaiai/Git_result/tree/main/tt
#     create_file("hhhaiai", "Git_result", "/tt/test2.txt", _content_not_base64=_content_not_base64)
#     #  private repo demo: https://github.com/parserpp/data/blob/main/appList.csv
#     create_file("parserpp", "data", "/1.txt", _content_not_base64=_content_not_base64)

#
# def base64Text():
#     s = "你好"
#      # 得到的编码结果前带有 b
#     # bs = base64.b64encode(s.encode("utf-8"))  # 将字符为unicode编码转换为utf-8编码
#      # 得到的编码结果前带有 b
#     bs = str(base64.b64encode(s.encode("utf-8")), "utf-8")
#
# def testReadFile():
#     # 直接路径测试。
#     ss = read_file_as_str("README.md")
#     print(ss)
#     ss = read_file_as_str("/Users/sanbo/Desktop/test.txt")
#     print(ss)
#
