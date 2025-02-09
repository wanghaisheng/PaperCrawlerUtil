# -*- coding: utf-8 -*-
# @Time    : 2022/7/16 11:39
# @Author  : 银尘
# @FileName: constant.py
# @Software: PyCharm
# @Email   ：liwudi@liwudi.fun

"""
跨文件全局变量名定义
"""
REDIS_CONF = "REDIS"
STORAGE_CONF = "storage"
CROSS_FILE_GLOBAL_DICT_CONF = "global_dict"
STORAGE_LOG_CONF = "storage_log"
GETTER_LOG_CONF = "getter_log"
TESTER_LOG_CONF = "tester_log"
PROXY_SCORE_MAX = "max_score"
PROXY_SCORE_MIN = "min_score"
PROXY_SCORE_INIT = "init_score"
POOL_MAX = "pool_max"
POOL_MIN = "pool_min"
DICT_STORE_PATH = "dict_store_path"
TEST_BATCH_NUM = "test_batch_num"
TESTER_CYCLE = "tester cycle"
GETTER_CYCLE = "getter cycle"
TESTER_TIMEOUT = "test_timeout"
GETTER_TIMEOUT = "getter_timeout"
TESTER_URL = "tester url"
API_HOST = "api host"
API_PORT = "api port"
ENABLE_TESTER = 'ENABLE_TESTER'
ENABLE_GETTER = 'ENABLE_GETTER'
ENABLE_SERVER = 'ENABLE_SERVER'
TEST_VALID_STATUS = "TEST_VALID_STATUS"
TEST_ANONYMOUS = "TEST_ANONYMOUS"
API_THREADED = "API_THREADED"
KEEP_PROCESS_BAR_STYLE = "keep_process_bar_style"
KEEP_PROCESS_BAR_STYLE_FILE = "keep_process_bar_style_file"
IS_LOG_TEST_MODE = "IS_LOG_TEST_MODE"
GLOBAL_LOG_LEVEL = "global_log_level"


"""
日志级别
"""
INFO = "info"
WARN = "warn"
DEBUG = "debug"
ERROR = "error"
EMAIL = "email"

LEVEL2NUM = {DEBUG: 10, INFO: 20, WARN: 30, ERROR: 40, EMAIL: 50}


"""
chain translate 定义
"""
ACCURACY = "accuracy"
MORE = "MORE"
GOOGLE_TRANSLATOR = "google"
BAIDU_TRANSLATOR = "baidu"


"""
存储方式定义
"""
STORAGE_REDIS = "redis"
STORAGE_DICT = "dict"

"""
比较方式定义
"""
EQUAL = "equal"
NOT_EQUAL = "not equal"
IN = "in"
NOT_IN = "not in"
LESS_THAN = "less than"
MORE_THAN = "more than"
GREATER_AND_EQUAL = "greater and equal"
LESS_THAN_AND_EQUAL = "less than and equal"

"""
日志定义方式
"""
LOG_STYLE_LOG = "log"
LOG_STYLE_PRINT = "print"
LOG_STYLE_ALL = "all"

"""
特殊符号，字符串
"""
HTTP = "http://"
COLON_SEPARATOR = ":"
BAIDU = "http://www.baidu.com"

"""
HTTP 访问方式
"""

POST = "POST"
GET = "GET"
DELETE = "DELETE"
OPTIONS = "OPTIONS"
HEAD = "HEAD"
PUT = "PUT"
PATCH = "PATCH"


"""
office 处理
"""
LIST = "list"
DICT = "dict"
COL = "col"
ROW = "row"
CELL = "cell"
LIST_OF_OBJECT = "list of object"
LIST_OF_TYPE = "list of type"
LIST_OF_VALUE = "list of value"
TYPE_OF_LENGTH = "length"
EXCEL_RETURN_TYPE = {LIST_OF_OBJECT: "list of object", LIST_OF_TYPE: "list of type",
                     LIST_OF_VALUE: "list of value", TYPE_OF_LENGTH: "length"}


"""
谷歌翻译
"""

"""
research util 建表
"""

CREATE_DB_TABLE = "\nCREATE SCHEMA `research` ;" \
                  "\n\nCREATE TABLE `research`.`record_result` " \
                  "(\n  `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'record number'," \
                  "\n  `file_execute` VARCHAR(200) BINARY NULL DEFAULT 'unkonwn file'," \
                  "\n  `execute_time` VARCHAR(200)  NULL  ," \
                  "\n  `finish_time` VARCHAR(200)  NULL  ," \
                  "\n  `result` VARCHAR(1000) NULL DEFAULT 'unkonwn result'," \
                  "\n  `args` text NULL," \
                  "\n  `other` text null," \
                  "\n  `default1` text null," \
                  "\n  `default2` text null," \
                  "\n  `default3` text null," \
                  "\n  `default4` text null," \
                  "\n  `delete_flag` tinyint(2) NULL DEFAULT 0," \
                  "\n  PRIMARY KEY (`id`))" \
                  "\nENGINE = InnoDB" \
                  "\nDEFAULT CHARACTER SET = utf8" \
                  "\nCOMMENT = 'research result record record_result table'; "
TABLE_TITLE = ["id", "file_execute", "execute_time", "finish_time", "result", "args", "other", "default1", "default2",
               "default3", "default4", "delete_flag"]
OP_TYPE = ["INSERT", "UPDATE", "DELETE", "SELECT"]
INSERT = OP_TYPE[0]
UPDATE = OP_TYPE[1]
DELETE = OP_TYPE[2]
SELECT = OP_TYPE[3]

"""自动识别，只能用在源语言"""
AUTO = "auto"
"""南非荷兰语"""
AF = "af"
"""阿尔巴尼亚语"""
SQ = "sq"
"""阿姆哈拉语"""
AM = "am"
"""阿拉伯语"""
AR = "ar"
"""亚美尼亚语"""
HY = "hy"
"""阿塞拜疆语"""
AZ = "az"
"""巴斯克语"""
EU = "eu"
"""白俄罗斯语"""
BE = "be"
"""孟加拉语"""
BN = "bn"
"""波斯尼亚语"""
BS = "bs"
"""保加利亚语"""
BG = "bg"
"""加泰罗尼亚语"""
CA = "ca"
"""宿务语"""
CEB = "ceb"
"""中文（简体）"""
ZH_CN = "zh-CN"
"""中文（繁体）"""
ZH_TW = "zh-TW"
"""科西嘉语"""
CO = "co"
"""克罗地亚语"""
HR = "hr"
"""捷克语"""
CS = "cs"
"""丹麦语"""
DA = "da"
"""荷兰语"""
NL = "nl"
"""英语"""
EN = "en"
"""世界语"""
EO = "eo"
"""爱沙尼亚语"""
ET = "et"
"""芬兰语"""
FI = "fi"
"""法语"""
FR = "fr"
"""弗里斯兰语"""
FY = "fy"
"""加利西亚语"""
GL = "gl"
"""格鲁吉亚语"""
KA = "ka"
"""德语"""
DE = "de"
"""希腊语"""
EL = "el"
"""古吉拉特语"""
GU = "gu"
"""海地克里奥尔语"""
HT = "ht"
"""豪萨语"""
HA = "ha"
"""夏威夷语"""
HAW = "haw"
"""希伯来语"""
HE = "he"
"""印地语"""
HI = "hi"
"""苗语"""
HMN = "hmn"
"""匈牙利语"""
HU = "hu"
"""冰岛语"""
IS_ = "is"
"""伊博语"""
IG = "ig"
"""印度尼西亚语"""
ID = "id"
"""爱尔兰语"""
GA = "ga"
"""意大利语"""
IT = "it"
"""日语"""
JA = "ja"
"""爪哇语"""
JV = "jv"
"""卡纳达语"""
KN = "kn"
"""哈萨克语"""
KK = "kk"
"""高棉语"""
KM = "km"
"""卢旺达语"""
RW = "rw"
"""韩语"""
KO = "ko"
"""库尔德语"""
KU = "ku"
"""吉尔吉斯语"""
KY = "ky"
"""老挝语"""
LO = "lo"
"""拉丁文"""
LA = "la"
"""拉脱维亚语"""
LV = "lv"
"""立陶宛语"""
LT = "lt"
"""卢森堡语"""
LB = "lb"
"""马其顿语"""
MK = "mk"
"""马尔加什语"""
MG = "mg"
"""马来语"""
MS = "ms"
"""马拉雅拉姆文"""
ML = "ml"
"""马耳他语"""
MT = "mt"
"""毛利语"""
MI = "mi"
"""马拉地语"""
MR = "mr"
"""蒙古文"""
MN = "mn"
"""缅甸语"""
MY = "my"
"""尼泊尔语"""
NE = "ne"
"""挪威语"""
NO = "no"
"""尼杨扎语（齐切瓦语）"""
NY = "ny"
"""奥里亚语（奥里亚）"""
OR_ = "or"
"""普什图语"""
PS = "ps"
"""波斯语"""
FA = "fa"
"""波兰语"""
PL = "pl"
"""葡萄牙语（葡萄牙、巴西）"""
PT = "pt"
"""旁遮普语"""
PA = "pa"
"""罗马尼亚语"""
RO = "ro"
"""俄语"""
RU = "ru"
"""萨摩亚语"""
SM = "sm"
"""苏格兰盖尔语"""
GD = "gd"
"""塞尔维亚语"""
SR = "sr"
"""塞索托语"""
ST = "st"
"""修纳语"""
SN = "sn"
"""信德语"""
SD = "sd"
"""僧伽罗语"""
SI = "si"
"""斯洛伐克语"""
SK = "sk"
"""斯洛文尼亚语"""
SL = "sl"
"""索马里语"""
SO = "so"
"""西班牙语"""
ES = "es"
"""巽他语"""
SU = "su"
"""斯瓦希里语"""
SW = "sw"
"""瑞典语"""
SV = "sv"
"""塔加路语（菲律宾语）"""
TL = "tl"
"""塔吉克语"""
TG = "tg"
"""泰米尔语"""
TA = "ta"
"""鞑靼语"""
TT = "tt"
"""泰卢固语"""
TE = "te"
"""泰文"""
TH = "th"
"""土耳其语"""
TR = "tr"
"""土库曼语"""
TK = "tk"
"""乌克兰语"""
UK = "uk"
"""乌尔都语"""
UR = "ur"
"""维吾尔语"""
UG = "ug"
"""乌兹别克语"""
UZ = "uz"
"""越南语"""
VI = "vi"
"""威尔士语"""
CY = "cy"
"""班图语"""
XH = "xh"
"""意第绪语"""
YI = "yi"
"""约鲁巴语"""
YO = "yo"
"""祖鲁语"""
ZU = "zu"

ALL_LANGUAGE_LIST = [AUTO, "auto", AF, "af", SQ, "sq", AM, "am", AR, "ar", HY, "hy", AZ, "az", EU, "eu", BE, "be", BN,
                     "bn", BS, "bs", BG, "bg", CA, "ca", CEB, "ceb", ZH_CN, "zh-CN", ZH_TW, "zh-TW", CO, "co", HR, "hr",
                     CS, "cs", DA, "da", NL, "nl", EN, "en", EO, "eo", ET, "et", FI, "fi", FR, "fr", FY, "fy", GL, "gl",
                     KA, "ka", DE, "de", EL, "el", GU, "gu", HT, "ht", HA, "ha", HAW, "haw", HE, "he", HI, "hi", HMN,
                     "hmn", HU, "hu", IS_, "is", IG, "ig", ID, "id", GA, "ga", IT, "it", JA, "ja", JV, "jv", KN, "kn",
                     KK, "kk", KM, "km", RW, "rw", KO, "ko", KU, "ku", KY, "ky", LO, "lo", LA, "la", LV, "lv", LT, "lt",
                     LB, "lb", MK, "mk", MG, "mg", MS, "ms", ML, "ml", MT, "mt", MI, "mi", MR, "mr", MN, "mn", MY, "my",
                     NE, "ne", NO, "no", NY, "ny", OR_, "or", PS, "ps", FA, "fa", PL, "pl", PT, "pt", PA, "pa", RO,
                     "ro", RU, "ru", SM, "sm", GD, "gd", SR, "sr", ST, "st", SN, "sn", SD, "sd", SI, "si", SK, "sk", SL,
                     "sl", SO, "so", ES, "es", SU, "su", SW, "sw", SV, "sv", TL, "tl", TG, "tg", TA, "ta", TT, "tt", TE,
                     "te", TH, "th", TR, "tr", TK, "tk", UK, "uk", UR, "ur", UG, "ug", UZ, "uz", VI, "vi", CY, "cy", XH,
                     "xh", YI, "yi", YO, "yo", ZU, "zu"]

"""
谷歌国家地区域名
"""
HONG_KONG = ".com.hk"
AUSTRALIA = ".com.au"
JAPAN = ".jp"
RUSSIA = ".com.ru"
ROOT = ".com"
SINGAPORE = ".com.sg"
DOMAIN_LIST = [HONG_KONG, AUSTRALIA, JAPAN, RUSSIA, ROOT, SINGAPORE]

"""
文件名不能包含的字符
"""

FORBIDDEN_LIST = ["#", "%", "&", "*", "|", ":", "\"", "<", ">", "?", "/", "\\", "\n"]
