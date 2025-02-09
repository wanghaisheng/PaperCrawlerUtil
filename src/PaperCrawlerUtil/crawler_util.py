import struct
import sys
import time
import urllib
from typing import Callable
from urllib.request import urlretrieve
from requests.cookies import RequestsCookieJar
import requests
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent

from PaperCrawlerUtil.common_util import *


def random_proxy_header_access(url: str, proxy: str = '',
                               require_proxy: bool = False, max_retry: int = 10, sleep_time: float = 1.2,
                               random_proxy: bool = True, time_out: tuple = (10, 20),
                               need_log: bool = True, cookie: str = "", if_bytes_encoding: str = "utf-8",
                               method: str = GET, get_params: List[tuple] or dict or bytes = None,
                               post_data: dict or List[tuple] or bytes = None,
                               json=None, allow_redirects: bool = True, return_type: str = "str",
                               need_random_headers: bool = True) -> str or object:
    """
    如果达到max_retry之后，仍然访问不到，返回空值
    use random header and proxy to access url and get content
    if access the url beyond max_retry, will return a blank string
    :param need_random_headers: 是否需要随机请求头
    :param allow_redirects: 是否启用重定向
    :param json: 请求体json序列化对象
    :param method: 请求方法
    :param post_data: POST方式的请求体数据
    :param get_params: URL参数
    :param if_bytes_encoding: 如果爬取到的是字节，需要通过什么字符集转换
    :param cookie: 对于需要cookie即登录才能访问的网站，需要提供cookie
    :param need_log: 是否需要日志
    :param url:链接
    :param proxy:提供代理，例如："127.0.0.1:1080"
    :param require_proxy:是否需要代理，默认为真
    :param max_retry:默认最大尝试10次
    :param sleep_time:每次爬取睡眠时间
    :return:返回爬取的网页或者最大尝试次数之后返回空
    :param random_proxy:随机使用代理，默认为真，随机使用真实地址而不使用代理
    :param time_out: 一个元组或者浮点数，元组前者表示连接超时阈值，后者表示获取内容超时阈值、
                    如果是浮点数，则两者值设为一样
    :param return_type: 需要返回处理过的字符串（“str”）还是原始对象（“object”）
    """
    proxy_provide = False
    cookie_jar = RequestsCookieJar()
    if len(cookie) != 0:
        cookie_jar = cookieString2CookieJar(cookie)
    if len(proxy) == 0:
        proxy_provide = False
    else:
        proxy_provide = True
    for i in range(max_retry):
        html = ''
        try:
            if len(proxy) == 0 and require_proxy:
                proxy = get_proxy()
            elif (not proxy_provide) and require_proxy:
                proxy = get_proxy()
            if require_proxy:
                if need_log:
                    log("使用代理：{}".format(proxy))
            if need_random_headers:
                ua = UserAgent()
                headers = {"User-Agent": ua.random}
            else:
                headers = None
            proxies = {'http': "http://" + proxy, 'https': 'http://' + proxy}
            if need_log:
                log("第{}次准备爬取{}的内容".format(str(i), url))
            if require_proxy:
                if random_proxy and two_one_choose():
                    if need_log:
                        log("随机使用代理")
                    request = requests.request(method=method, url=url, headers=headers, proxies=proxies,
                                               timeout=time_out, cookies=cookie_jar, allow_redirects=allow_redirects,
                                               json=json, data=post_data, params=get_params)
                elif random_proxy and not two_one_choose():
                    if need_log:
                        log("随机不使用代理")
                    request = requests.request(method=method, url=url, headers=headers, timeout=time_out,
                                               cookies=cookie_jar, allow_redirects=allow_redirects,
                                               json=json, data=post_data, params=get_params)
                elif not random_proxy:
                    request = requests.request(method=method, url=url, headers=headers, proxies=proxies,
                                               timeout=time_out, cookies=cookie_jar, allow_redirects=allow_redirects,
                                               json=json, data=post_data, params=get_params)
                else:
                    request = requests.request(method=method, url=url, headers=headers, proxies=proxies,
                                               timeout=time_out, cookies=cookie_jar, allow_redirects=allow_redirects,
                                               json=json, data=post_data, params=get_params)
            else:
                request = requests.request(method=method, url=url, headers=headers, timeout=time_out, cookies=cookie_jar
                                           , allow_redirects=allow_redirects, json=json, data=post_data,
                                           params=get_params)
            html = None
            if return_type != "str":
                return request
            html = request.content
            if need_log:
                log("爬取成功，返回内容")
            time.sleep(sleep_time)
        except NoProxyException as e:
            raise e
        except Exception as result:
            log("错误信息:%s" % result, print_file=sys.stderr)
            log("尝试重连")
            time.sleep(sleep_time)
        if (type(html) == str or type(html) == bytes) and len(html) > 0 and return_type == "str":
            if need_log:
                log(get_split(lens=100))
            if type(html) == bytes:
                try:
                    html = str(html, encoding=if_bytes_encoding)
                except Exception as e:
                    log("字节转字符串错误：{}".format(e), print_file=sys.stderr)
            return html
    if return_type == "str":
        return ""
    else:
        return None


def get_opener(require_proxy, random_proxy, need_random_header, proxies):

    opener = urllib.request.build_opener()
    if require_proxy and need_random_header:
        ua = UserAgent()
        if random_proxy and two_one_choose():
            opener.addheaders = [('User-Agent', ua.random),
                                 ('proxy', "http://" + proxies),
                                 ('proxy', "https://" + proxies)]
        elif random_proxy and not two_one_choose():
            opener.addheaders = [('User-Agent', ua.random)]
        else:
            opener.addheaders = [('User-Agent', ua.random)]
    elif require_proxy:
        if random_proxy and two_one_choose():
            opener.addheaders = [('proxy', "http://" + proxies),
                                 ('proxy', "https://" + proxies)]
    elif need_random_header:
        ua = UserAgent()
        opener.addheaders = [('User-Agent', ua.random)]
    return opener


def retrieve_file(url: str, path: str = "", proxies: str = "",
                  require_proxy: bool = False, max_retry: int = 10,
                  sleep_time: float = 1.2, random_proxy: bool = True,
                  need_log: bool = True, reporthook: Callable[[], None] = None,
                  data: str = None, need_random_header: bool = True) -> bool:
    """
    retrieve file from provided url and save to path
    :param need_random_header: 是否需要使用随机header
    :param data: 使用url encode的参数
    :param reporthook: 用来在获取url链接信息之后调用的函数,例如函数def test(a: int, b: int, c: int) -> None,
    三个参数分别表示，当前下载第几块，每块的大小，文件的总大小
    :param need_log: 是否需要日志
    :param url: file url
    :param path: the save path
    :param proxies: proxy string, if this args not null, will always use this proxy if decide to use proxy
    :param require_proxy:decide whether use proxy
    :param max_retry: max times to retry if fail to retrieve
    :param sleep_time: thread sleep time which finish part function
    :param random_proxy: if this arg is true, whatever provide proxy,
    will random to use local address to access url
    :return:a bool value represent whether success to save file
    """
    success = False
    proxy_provide = False
    if len(path) == 0:
        path = local_path_generate("")
    if len(proxies) == 0:
        proxy_provide = False
    else:
        proxy_provide = True
    for i in range(max_retry):
        if need_log:
            log("第{}次准备抽取{}文件".format(str(i), url))
        try:
            if len(proxies) == 0 and require_proxy:
                proxies = get_proxy()
            if not proxy_provide and require_proxy:
                proxies = get_proxy()
            opener = get_opener(require_proxy, random_proxy, need_random_header, proxies)
            urllib.request.install_opener(opener)
            bar = None
            if reporthook:
                reporthook = reporthook
            else:
                bar = process_bar(final_prompt="文件下载完成", desc="文件下载进度：")
                reporthook = bar.process
            urlretrieve(url=url, filename=path, reporthook=reporthook, data=data)
            success = True
            time.sleep(sleep_time)
        except Exception as e:
            log("抽取:{},失败:{}".format(url, e), print_file=sys.stderr)
            time.sleep(sleep_time)
        if success:
            return success
            time.sleep(sleep_time)
    if not success:
        log("{}提取失败".format(url), print_file=sys.stderr)
        time.sleep(sleep_time)
        return success


def get_pdf_link_from_sci_hub_download_page_and_download(html: str, work_path: str, sleep_time: float = 1.2,
                                                         max_retry: int = 10,
                                                         require_proxy: bool = False,
                                                         proxies: bool = "", need_log: bool = True) -> bool:
    attr_list = get_attribute_of_html(html, {"href=": "in"}, ["button"])
    for paths in attr_list:
        paths = str(paths)
        try:
            path = paths.split("href=")[1].split("?download")[0]
        except Exception as e:
            log("链接{}截取错误:{}".format(paths, e), print_file=sys.stderr)
            continue
        time.sleep(sleep_time)
        for i in range(max_retry):
            path = path.replace("'", "").replace("\"", "").replace(",", "")
            if (not path.startswith("http:")) and (not path.startswith("https:")):
                if "sci" not in path or "hub" not in path:
                    path = "https://" + random.choice(['sci-hub.se', 'sci-hub.st', 'sci-hub.ru']) + (
                        path.replace("//", "", 1))
                else:
                    path = "https://" + (path.replace("//", "", 1))
            else:
                path = path
            success = retrieve_file(
                path,
                work_path, proxies=proxies, require_proxy=require_proxy, max_retry=1)
            if success:
                if need_log:
                    log("文件{}提取成功".format(work_path))
                return True
        if not success:
            log("抽取文件达到最大次数，停止获取{}".format(path), print_file=sys.stderr)
            return False
    return False


def get_pdf_url_by_doi(search: str, work_path: str, sleep_time: float = 1.2, max_retry: int = 10,
                       require_proxy: bool = False, random_proxy: bool = True,
                       proxies: bool = "", need_log: bool = True, is_doi: bool = True) -> bool:
    """
    save file from sci_hub by doi string provided
    :param is_doi: search字段是否是doi，还是名称
    :param need_log: 是否需要日志
    :param require_proxy:是否需要代理
    :param random_proxy:是否在使用代理时，随机使用本机地址
    :param proxies:提供代理，如果提供，则一直使用该代理，并且受random_proxy影响
    :param search: 搜索字段
    :param work_path: file path to save
    :param sleep_time: thread sleep time which finish part function
    :param max_retry: max times to retry if fail to retrieve
    :return:
    """
    domain_list = ['sci-hub.se/', 'sci-hub.st/', 'sci-hub.ru/']
    html = ''

    if is_doi:
        for i in range(max_retry):
            url = 'https://' + domain_list[random.randint(0, 2)]
            url = url + search
            html = random_proxy_header_access(url,
                                              max_retry=1, proxy=proxies,
                                              random_proxy=random_proxy,
                                              require_proxy=require_proxy)
            if len(html) == 0:
                log("爬取失败，字符串长度为0", print_file=sys.stderr)
                time.sleep(sleep_time)
                continue
            elif len(html) != 0 and len(get_attribute_of_html(html, {"href=": "in"}, ["button"])) == 0:
                log("爬取失败，无法从字符串中提取需要的元素", print_file=sys.stderr)
                time.sleep(sleep_time)
                continue
            else:
                if need_log:
                    log("从sichub获取目标文件链接成功，等待分析提取")
                break
        if len(html) == 0:
            log("获取html文件达到最大次数，停止获取doi:{}".format(search), print_file=sys.stderr)
            return
        return get_pdf_link_from_sci_hub_download_page_and_download(html=html, work_path=work_path,
                                                                    sleep_time=sleep_time,
                                                                    max_retry=max_retry, require_proxy=require_proxy,
                                                                    proxies="", need_log=need_log)
    else:
        for i in range(max_retry):
            url = 'https://' + domain_list[random.randint(0, 2)]
            html = random_proxy_header_access(method=POST, post_data={"request": search}, require_proxy=require_proxy,
                                              max_retry=max_retry, sleep_time=sleep_time, random_proxy=random_proxy,
                                              need_log=need_log, return_type="object", url=url)
            if html is not None and \
                    verify_rule(rule={400: LESS_THAN, 200: GREATER_AND_EQUAL}, origin=float(html.status_code)):
                if verify_rule(rule={0: MORE_THAN}, origin=len(html.url)) \
                        and verify_rule(rule={"未找到文章": NOT_IN, "article not found": NOT_IN}, origin=html.text):
                    if need_log:
                        log("重定向到网址：{}".format(html.url))
                    download_page = random_proxy_header_access(method=GET, require_proxy=require_proxy,
                                                               max_retry=max_retry, sleep_time=sleep_time,
                                                               random_proxy=random_proxy,
                                                               need_log=need_log, return_type="str", url=html.url)
                    res = get_pdf_link_from_sci_hub_download_page_and_download(html=download_page, work_path=work_path,
                                                                               sleep_time=sleep_time,
                                                                               max_retry=max_retry,
                                                                               require_proxy=require_proxy,
                                                                               proxies=proxies,
                                                                               need_log=need_log)
                    if res:
                        return res
                else:
                    log("未查询到对应文件名文件: {}".format(search), print_file=sys.stderr)
                    return False
            elif html is not None:
                log("访问失败，状态为：{}".format(str(html.status_code)), print_file=sys.stderr)
            else:
                log("访问出错，再次尝试", print_file=sys.stderr)
        log("抽取文件达到最大次数，停止获取文件:{}".format(search), print_file=sys.stderr)
        return False


def get_attribute_of_html(html: str, rule: dict = None, attr_list: list = None) -> list:
    """
    Use beautifulsoup4 to scan the html string get by urllib.get().
    And select all attribute in attr_list and then select satisfy all rules in rule
    in list.then return the list which contains all attribute
    :param html: html string
    :param rule: a dictionary that represent rules. the key is the match string and the value
    is the rule. The rule is only support "in" and "not in". example:{"href": "in"}
    :param attr_list: a list that contain attribute which you want. example:["a", "button"]
    :return: a list of attribute string
    """
    if attr_list is None:
        attr_list = ['a']
    if rule is None:
        rule = {'href': 'in'}
    res_list = []
    if len(html) == 0:
        return res_list
    bs = BeautifulSoup(html, 'html.parser')
    elements_list = []
    for k in attr_list:
        elements_list.extend(bs.find_all(k))
    for elements in elements_list:
        if verify_rule(rule, elements):
            res_list.append(str(elements))
    return list(set(res_list))


def get_pdf_form_arXiv(title: str, folder_name: str, sleep_time: float = 1.2,
                       max_retry: int = 10, require_proxy: bool = False,
                       random_proxy: bool = True, proxies: str = "", max_get: int = 3) -> None:
    """
    从arXiv获取论文，
    :param title:
    :param folder_name:
    :param sleep_time:
    :param max_retry:
    :param require_proxy:
    :param random_proxy:
    :param proxies:
    :param max_get: 当搜索结果有多个时，最多获取的数量
    :return:
    """
    html = random_proxy_header_access(url="https://arxiv.org/search/?query="
                                          + title.replace(" ", "+")
                                          + "&searchtype=all&source=header",
                                      proxy=proxies, require_proxy=require_proxy, max_retry=max_retry,
                                      sleep_time=sleep_time, random_proxy=random_proxy)
    attr_list = get_attribute_of_html(html, rule={"pdf": IN, "arxiv": IN, "href": IN})
    count = 0
    for k in attr_list:
        path = k.split("href=\"")[1].split("\"")[0]
        retrieve_file(path,
                      local_path_generate(folder_name=folder_name, file_name=title + str(count) + ".pdf"),
                      proxies=proxies, require_proxy=require_proxy,
                      max_retry=max_retry, sleep_time=sleep_time, random_proxy=random_proxy)
        count = count + 1
        if count >= max_get:
            break
    get_split()


def google_scholar_search_crawler(contain_all: List[str] = None, contain_complete_sentence: List[str] = None,
                                  least_contain_one: List[str] = None, not_contain: List[str] = None,
                                  q: str = "", need_log: bool = True, sleep_time: float = 15,
                                  need_retrieve_file: bool = False, start: int = 0, proxy: str = "",
                                  file_sava_directory: str = "") -> object or List:
    """
    爬取谷歌学术爬虫
    :param contain_all:高级搜索，包含列表中全部字符
    :param contain_complete_sentence: 高级搜索，必须包含完整字句
    :param least_contain_one: 高级搜索，至少包含列表中的某一个字符
    :param not_contain: 高级搜索，不包含列表中的所有字符串
    :param q: 普通搜索，输入查询内容，优先级高于以上四个高级搜索关键词
    :param need_log: 是否需要日志
    :param sleep_time: 睡眠时间，防止被封ip
    :param need_retrieve_file: 是否需要爬取PDF文件，如果有
    :param start: 开始索引，必须为10的整数倍或者0
    :param proxy: 可以爬取谷歌的代理ip：port
    :param file_sava_directory: 文件保存的目录，文件名自动爬取
    :return: 返回文件列表或者html对象，参考need_retrieve_file
    """
    if len(proxy) == 0:
        log("谷歌学术需要提供代理", print_file=sys.stderr)
        return None
    if contain_all is None and contain_complete_sentence is None and least_contain_one is None and not_contain is None \
            and len(q) == 0:
        log("查询内容q或者高级查找关键词不能全部为空", print_file=sys.stderr)
        return None
    base_url = "https://scholar.google"
    base_url = base_url + random.choice(DOMAIN_LIST)
    base_url = base_url + "/scholar?start=" + str(start) + "&hl=zh-CN&as_sdt=0%2C5&q="
    q_ = "+".join(contain_all) + "+" \
         + "OR+" + "+OR+".join(least_contain_one) + "+" \
         + ("\"" + "+".join(contain_complete_sentence) + "\"") + "+" \
         + "-" + "+-".join(not_contain)
    q = q.replace(" ", "+")
    q = q if len(q) != 0 else q_
    base_url = base_url + q + "&oq="
    html = random_proxy_header_access(url=base_url, require_proxy=True, proxy=proxy,
                                      random_proxy=False, need_log=need_log, return_type="object",
                                      sleep_time=sleep_time)
    if need_retrieve_file:
        file_list = []
        if type(html) == str:
            html = html
        else:
            html = html.content
        div_list = get_attribute_of_html(html=html, rule={"div class=\"gs_r gs_or gs_scl\"": IN, "data-cid": IN,
                                                          "data-did": IN, "data-aid": IN, "data-rp": IN,
                                                          "引用": IN, "<div id=\"gs_top\" onclick=\"\">": NOT_IN,
                                                          "<div id=\"gs_bdy\">": NOT_IN,
                                                          "<div id=\"gs_bdy_ccl\" role=\"main\">": NOT_IN,
                                                          "<div id=\"gs_res_ccl\">": NOT_IN,
                                                          "<div id=\"gs_res_ccl_mid\">": NOT_IN},
                                         attr_list=["div"])
        for div in div_list:
            name = get_attribute_of_html(html=div, rule={"class=\"gs_rt\"": IN}, attr_list=["h3"])
            if len(name) != 0:
                name = deleteSpecialCharFromHtmlElement(html=name[0], sep="")
                name = name + ".pdf"
                name = name.replace(":", "")
            else:
                continue
            link = get_attribute_of_html(html=div, rule={"[PDF]": IN})[0].split("href=\"")[1].split("\">")[0]
            if len(link) == 0:
                log("文件：{}没有PDF可下载".format(name))
                continue
            file_sava_path = local_path_generate(file_sava_directory, file_name=name)
            retrieve_file(url=link, path=file_sava_path, need_log=False, require_proxy=True, proxies=proxy)
            log("文件：{}保存成功到：{}".format(name, file_sava_path))
            file_list.append(file_sava_path)
        return file_list
    else:
        return html


def get_all_link_from_html(html: str, get_type: str = ACCURACY):
    """
    获取html中所有链接，有两种模式，一种是保证正确型，只识别http，https开头和href开头的
    还有一种是全面型，尽可能多的识别链接，比如/adta/download/jafs.pdf等等也识别为链接，这种需要配合前缀链接使用
    后一种返回时，会分为两部分，一部分是保证正确型，另一部分是尽可能多的识别的链接
    :param get_type:
    :param html:
    :return:
    """


if __name__ == "__main__":
    basic_config(logs_style=LOG_STYLE_PRINT)
