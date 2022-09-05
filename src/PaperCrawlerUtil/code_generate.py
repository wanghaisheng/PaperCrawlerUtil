# -*- coding: utf-8 -*-
# @Time    : 2022/9/5 16:50
# @Author  : 银尘
# @FileName: code_generate.py
# @Software: PyCharm
# @Email   ：liwudi@liwudi.fun
import json
from common_util import *
from flask import Flask, request
from constant import *

code_generate = Flask(__name__)


@code_generate.route("/")
def hello_world():
    return 'hello world'


@code_generate.route("/code_generate/", methods=[POST])
def generate():
    data = json.loads(request.get_data())
    # 到最终保存或提取文件需要多少层
    layer = data['layer']
    # rule， 爬取链接之后，需要根据这个条件抽取元素，每层一个
    rule = data['rule']
    element = data['element']
    url_pre = data["url_pre"]
    ele_split = data["ele_split"]
    file_directory = data["file_directory"]
    url = data["url"]
    imports = "from PaperCrawlerUtil.common_util import * \n from PaperCrawlerUtil.crawler_util import * \nfrom PaperCrawlerUtil.document_util import *\n\n"
    config = "basic_config(logs_style=LOG_STYLE_PRINT, require_proxy_pool=True, need_tester_log=False, need_getter_log=False)\n"
    body = ""
    for l in range(int(layer)):
        body = body + get_split(lens=l, style="   ") + "html_" + str(l) + " = " + "random_proxy_header_access(\"" + url + "\"," + ")\n"
        body = body + get_split(lens=l, style="   ") + "attr_list_" + str(l) + " = get_attribute_of_html(html_" + str(l) + ", " + str(rule[l]) + ")\n"
        body = body + get_split(lens=l, style="   ") + "for ele_" + str(l) + " in attr_list_"+ str(l) +":\n"
        body = body + get_split(lens=l+1, style="   ") + "path_" + str(l) + " = ele_" + str(l) + ".split(\"" + ele_split[2 * l] +"\")[1].split(\"" + ele_split[2 * l + 1] + "\")[0]\n"
    code = imports + config + body
    return code


if __name__ == "__main__":
    code_generate.run(host="0.0.0.0", port=8000, debug=True)
