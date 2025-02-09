import pickle
import sys
from typing import List

import flask
from bs4 import Tag

import PaperCrawlerUtil.global_val as global_val
from PaperCrawlerUtil.proxypool.storages.proxy_dict import ProxyDict

sys.path.append("PaperCrawlerUtil")
sys.path.append("PaperCrawlerUtil/proxypool")
sys.path.append("PaperCrawlerUtil/proxypool/*")
sys.path.append("proxypool/crawlers/public/*")
sys.path.append("proxypool/crawlers/private/*")
sys.path.append("proxypool/crawlers/*")
sys.path.append("proxypool/exceptions/*")
sys.path.append("proxypool/processors/*")
sys.path.append("proxypool/schemas/*")
sys.path.append("proxypool/storages/*")
sys.path.append("proxypool/utils/*")
sys.path.append("proxypool/*")
import logging
import os
import random
import threading
import time
import requests
from PaperCrawlerUtil.proxypool.setting import *
from requests.cookies import RequestsCookieJar
from PaperCrawlerUtil.proxypool.processors.getter import Getter
from PaperCrawlerUtil.proxypool.processors.server import app
from PaperCrawlerUtil.proxypool.processors.tester import Tester
from PaperCrawlerUtil.constant import *
from tqdm import tqdm
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

PROXY_POOL_URL = ""
log_style = LOG_STYLE_PRINT
PROXY_POOL_CAN_RUN_FLAG = True


class process_bar(object):
    """
    封装进度条类tdqm，实现retrieve_file进度条显示，
    其他也可以使用，保证每次调用process时，必须传入三个参数，
    当前完成到第几块，块的大小，总的大小
    """

    def __init__(self, final_prompt="", iterable=None, desc=None, total=-1, leave=True, file=None,
                 ncols=None, mininterval=0.1, maxinterval=10.0, miniters=None,
                 ascii=None, disable=False, unit='byte', unit_scale=False,
                 dynamic_ncols=False, smoothing=0.3, bar_format=None, initial=0,
                 position=None, postfix=None, unit_divisor=1000, write_bytes=None,
                 lock_args=None, nrows=None, colour=None, delay=0, gui=False):
        """
        :param final_prompt: 任务完成时候的提示信息，显示在进度条结尾
        :param iterable: 迭代对象，可选，用来包装在进度条对象中，手动更新进度条
        :param desc: 前缀描述信息，字符串，可选参数
        :param total: 进度条表示的最大值，即任务总量
        :param leave: 是否需要在完成后保留进度条，默认为True
        :param file: `io.TextIOWrapper` or `io.StringIO`，可选参数，指定输出的位置，默认使用sys.stderr，编码参数见write_bytes
        :param ncols: 整个输出消息的宽度，可选参数，如果指定，则动态调整消息条的宽度，
        如果没有指定，则尝试使用环境中的宽度，默认是10的单位的宽度并且计数器没有限制，如果为0，
        将不会输出除了状态stat之外的所有数据
        :param mininterval:浮点数，默认为0.1，表示进度条更新的最小时间间隔
        :param maxinterval:浮点数，默认为10，在长时间更新滞后之后，自动调整参数miniters，
        当且仅当一个监控线程启动
        :param miniters:整数或者浮点数，可选参数，最小进度显示更新间隔，以迭代为单位。如果该值为0，并且dynamic_miniters参数为真，
        将自动调整与mininterval一致，CPU更有效并且适合于紧密循环。如果该值大于0.将跳过指定数量的迭代，配合mininterval可以得到更有效的循环
        如果进度在快速和慢速迭代都不稳定，如网络等，该值应该设置为1
        :param ascii:布尔值或者字符串，可选参数。如果未指定或者指定为false，将使用Unicode（平滑块）去填充
        :param disable: 可选布尔值，是否禁用整个进度条包装器，默认为False
        :param unit: 可选字符串值，字符串将被用来定义迭代单元，默认值为it
        :param unit_scale:可选布尔值或者整数或者浮点值，如果为1或者真，迭代的数量将会自动缩放，
        并且将添加一个国际单位如（千，兆）等，默认为False。如果该值大于0，将会缩放total和n
        :param dynamic_ncols:可选布尔值， 如果设置，将持续改变ncols和nrows，允许调整窗口，默认为False
        :param smoothing: 可选浮点数，速度估计的指数移动平滑因子，在GUI模式中忽略，范围为【0（平均速度）,1（当前或者瞬时速度）】，默认0.3
        :param bar_format: 可选字符串，指定一个定制的进度条样式字串，可能或改变表现，默认为'{l_bar}{bar}{r_bar}']，其中
         l_bar='{desc}: {percentage:3.0f}%|' 以及 r_bar='| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, '
         '{rate_fmt}{postfix}]'
         可能的变量有：l_bar, bar, r_bar, n, n_fmt, total, total_fmt,
              percentage, elapsed, elapsed_s, ncols, nrows, desc, unit,
              rate, rate_fmt, rate_noinv, rate_noinv_fmt,
              rate_inv, rate_inv_fmt, postfix, unit_divisor,
              remaining, remaining_s, eta.
        注意：{desc} 之后会自动删除结尾的“:” 如果后者为空。
        :param initial:可选整数或者浮点数，定义初始计数器值。重新启动进度时很有用。bar[默认值：0]。 如果使用浮点数，请考虑指定 `{n:.3f}`
             或 `bar_format` 中的类似内容，或指定 `unit_scale`。
        :param position: 可选整数，指定偏移多少行进行输出，从0开始。如果不指定则自动选择。
        在管理多个进度条时很有用，比如多线程
        :param postfix:字典或者其他值，可选，指定附加性状态在进度条末尾显示。
        如果可能请调用set_postfix(**postfix)
        :param unit_divisor:可选浮点数，默认为1000， 除非unit_scale为真，否则忽略
        :param write_bytes: 可选布尔值，如果默认为None并且没有指定file，将会使用python2输出字节，
        如果为真也输出字节bytes，其他情况输出unicode
        :param lock_args:可选元组，传递给 `refresh` 以获取中间输出（初始化、迭代和更新）。
        :param nrows:可选整数，指定屏幕高度，如果指定，则隐藏此之外的嵌套条边界。
        如果未指定，则尝试使用环境高度。后备是 20。
        :param colour: 可选字符串，进度条颜色，例如'green'，'#00ff00'
        :param delay:可选浮点数，不显示直到【默认0】秒过去之后
        :param gui:可选布尔值，
        警告：内部参数 - 不要使用。
             使用 tqdm.gui.tqdm(...) 代替。 如果设置，将尝试使用
             用于图形输出的 matplotlib 动画 [默认值：False]。
        """
        self.final_prompt = final_prompt
        self.batch = -1
        self.bar = None
        self.current = 0
        self.iterable = iterable
        self.desc = desc
        self.total = total
        self.leave = leave
        self.file = global_val.get_value(KEEP_PROCESS_BAR_STYLE_FILE) \
            if global_val.get_value(KEEP_PROCESS_BAR_STYLE) else file
        self.ncols = ncols
        self.mininterval = mininterval
        self.maxinterval = maxinterval
        self.miniters = miniters
        self.ascii = ascii
        self.disable = disable
        self.unit = unit
        self.unit_scale = unit_scale
        self.dynamic_ncols = dynamic_ncols
        self.smoothing = smoothing
        self.bar_format = bar_format
        self.initial = initial
        self.position = position
        self.postfix = postfix
        self.unit_divisor = unit_divisor
        self.write_bytes = write_bytes
        self.lock_args = lock_args
        self.nrows = nrows
        self.colour = colour
        self.delay = delay
        self.gui = gui

    def process(self, *args):
        if self.total == -1:
            self.total = args[2]
        if self.bar is None:
            self.bar = tqdm(iterable=self.iterable, desc=self.desc, total=self.total, leave=self.leave,
                            file=self.file, ncols=self.ncols, maxinterval=self.maxinterval,
                            mininterval=self.mininterval, miniters=self.miniters, ascii=self.ascii, disable=self.disable
                            , unit=self.unit, unit_scale=self.unit_scale, dynamic_ncols=self.dynamic_ncols,
                            smoothing=self.smoothing, bar_format=self.bar_format, initial=self.initial,
                            position=self.position, postfix=self.postfix, unit_divisor=self.unit_divisor,
                            write_bytes=self.write_bytes, lock_args=self.lock_args, nrows=self.nrows, colour=self.colour
                            , delay=self.delay, gui=self.gui)
        else:
            self.batch = args[1]
            if self.current + self.batch >= self.total:
                self.bar.update(self.total - self.current)
                self.current = self.total
                self.bar.set_postfix_str(self.final_prompt)
            else:
                self.bar.update(self.batch)
                self.current = self.current + self.batch

    def __del__(self):
        try:
            if self.bar is not None:
                self.bar.close()
        except Exception as e:
            log("进度条关闭失败:{}".format(e), print_file=sys.stderr)


def verify_rule(rule: dict, origin: float or str or Tag) -> bool:
    """
    verify the element string. if element satisfy all rules provided by rule arg,
    return true.
    :param rule:a dictionary that represent rules. the key is the match string and the value
    is the rule. The rule is only support "in" and "not in" and "equal" and "not equal",
    and more than, less than and greater or equal and less than or equal.
     example:{"href": "in"}
    :param origin:the string will be verified
    :return:a bool value represent whether element satisfy all rule
    """
    if rule is None or len(rule) == 0:
        return True
    if origin is None:
        return False
    for key, value in rule.items():
        if str(value) == IN and str(key) not in str(origin):
            return False
        elif str(value) == NOT_IN and str(key) in str(origin):
            return False
        elif str(value) == EQUAL and str(key) != str(origin):
            return False
        elif str(value) == NOT_EQUAL and str(key) == str(origin):
            return False
        elif str(value) == LESS_THAN or str(value) == LESS_THAN or str(value) == LESS_THAN_AND_EQUAL or str(
                value) == MORE_THAN or str(value) == GREATER_AND_EQUAL:
            if type(origin) != float and type(origin) != int:
                return False
            else:
                if str(value) == LESS_THAN and float(origin) >= float(key):
                    return False
                elif str(value) == LESS_THAN_AND_EQUAL and float(origin) > float(key):
                    return False
                elif str(value) == GREATER_AND_EQUAL and float(origin) < float(key):
                    return False
                elif str(value) == MORE_THAN and float(origin) <= float(key):
                    return False
    return True


def get_timestamp(split: str or list = ["-", "-", " ", ":", ":"], accuracy: int = 6) -> str:
    """
    %Y  Year with century as a decimal number.
    %m  Month as a decimal number [01,12].
    %d  Day of the month as a decimal number [01,31].
    %H  Hour (24-hour clock) as a decimal number [00,23].
    %M  Minute as a decimal number [00,59].
    %S  Second as a decimal number [00,61].
    %z  Time zone offset from UTC.
    %a  Locale's abbreviated weekday name.
    %A  Locale's full weekday name.
    %b  Locale's abbreviated month name.
    %B  Locale's full month name.
    %c  Locale's appropriate date and time representation.
    %I  Hour (12-hour clock) as a decimal number [01,12].
    %p  Locale's equivalent of either AM or PM.
    :param split:
    :param accuracy:
    :return:
    """
    time_stamp_name = ["Y", "m", "d", "H", "M", "S", "z", "a", "A", "B", "c", "I", "p"]
    if accuracy >= len(time_stamp_name):
        accuracy = len(time_stamp_name)
    time_style = ""
    if type(split) == str:
        temp = split
        split = []
        for i in range(accuracy):
            split.append(temp)
    elif type(split) == list:
        if len(split) < accuracy:
            for i in range(accuracy - len(split)):
                split.append("-")
    for i in range(accuracy):
        if i == accuracy - 1:
            time_style = time_style + "%" + time_stamp_name[i]
        else:
            time_style = time_style + "%" + time_stamp_name[i] + split[i]
    return time.strftime(time_style, time.localtime())


def write_log(string: str = "", print_file: object = sys.stdout, func: callable = None):
    if func is not None:
        func(string)
    else:
        if print_file == sys.stdout:
            logging.warning(string)
        else:
            logging.error(string)


def log(*string: str or object, print_sep: str = ' ', print_end: str = "\n", print_file: object = sys.stdout,
        print_flush: bool = None, need_time_stamp: bool = True, is_test_out: bool = False,
        funcs: callable = None, level: str = None) -> bool:
    """
    本项目的通用输出函数， 使用这个方法可以避免tqdm进度条被中断重新输出
    :param level: 日志等级
    :param funcs: 日志输出函数
    :param is_test_out: 是否是测试输出，正式场合不需要输出，可以通过common_util.basic_config()控制
    :param need_time_stamp: 是否需要对于输出的日志添加时间戳
    :param process_bar_file: 如果使用process_bar参数并且需要保持格式不变，则设置此项参数
    与process_bar的初始化file参数一致，默认为sys.stderr
    :param string: 待输出字符串或者对象，对象只支持print方式或者可以被str函数转成字符串的对象
    :param print_sep: 输出字符串之间的连接符，同print方法sep，目前被废弃
    :param print_end: 输出字符串之后的结尾添加字符
    :param print_file: 输出流
    :param print_flush: 是否强制输出缓冲区，同print方法flush，目前被废弃
    :return:
    """
    global log_style
    flag = True
    print_file = global_val.get_value(KEEP_PROCESS_BAR_STYLE_FILE) \
        if global_val.get_value(KEEP_PROCESS_BAR_STYLE) else print_file
    is_test_model = global_val.get_value(IS_LOG_TEST_MODE) \
        if global_val.get_value(IS_LOG_TEST_MODE) else False
    if is_test_out and (not is_test_model):
        return flag
    global_log_level = global_val.get_value(GLOBAL_LOG_LEVEL)
    s = ""
    try:
        for k in string:
            s = s + str(k) + print_sep
    except Exception as e:
        s = "待输出的列表中含有无法转换为字符串的值，{}".format(e)
        try:
            print(string, file=print_file, end=print_end, sep=print_sep, flush=print_flush)
        except Exception as ee:
            s = "待输出的日志不是字符串形式，也无法使用print方式显示，{}".format(e)
            flag = False
    if need_time_stamp and type(s) == str:
        s = get_timestamp(split=["-", "-", " ", ":", ":"]) + get_split(lens=3, style=" ") + s
    if log_style == LOG_STYLE_LOG:
        write_log(s, print_file, func=funcs)
    elif log_style == LOG_STYLE_PRINT:
        if (LEVEL2NUM[global_log_level] if type(global_log_level) == str else global_log_level) <= \
                (LEVEL2NUM[level] if type(level) == str else level):
            tqdm.write(s=s, file=print_file, end=print_end)
    elif log_style == LOG_STYLE_ALL:
        if (LEVEL2NUM[global_log_level] if type(global_log_level) == str else global_log_level) <= \
                (LEVEL2NUM[level] if type(level) == str else level):
            write_log(s, print_file, func=funcs)
            tqdm.write(s=s, file=print_file, end=print_end)
    return flag


def send_email(sender_email, sender_password, receiver_email,
               message, subject="default subject"):
    """
    send email
    :param sender_email:
    :param sender_password:
    :param receiver_email:
    :param message:
    :param subject:
    :return:
    """
    try:
        if sender_email.endswith('@163.com'):
            smtp_server = 'smtp.163.com'
            smtp_port = 25
        elif sender_email.endswith('@qq.com'):
            smtp_server = 'smtp.qq.com'
            smtp_port = 465
        else:
            Logs.log_error('Unsupported email domain')

        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(('Sender', sender_email))
        msg['To'] = formataddr(('Receiver', receiver_email))
        msg['Subject'] = subject

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [receiver_email], msg.as_string())

        Logs.log_info('Email sent successfully!')
    except Exception as e:
        Logs.log_error('Error sending email:', str(e))


class Logs(object):

    def __init__(self, sender_email, sender_password, receiver_email):
        super().__init__()
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    class LOG(object):

        def __init__(self, ):
            super().__init__()

        @staticmethod
        def log_info(string, *args, **keywords):
            logging.info(string, *args, **keywords)

        @staticmethod
        def log_warning(string, *args, **keywords):
            logging.warning(string, *args, **keywords)

        @staticmethod
        def log_error(string, *args, **keywords):
            logging.error(string, *args, **keywords)

        @staticmethod
        def log_debug(string, *args, **keywords):
            logging.debug(string, *args, **keywords)

        @staticmethod
        def log_email(sender_email, sender_password, receiver_email,
                      message, subject="default subject"):
            sender_email(sender_email, sender_password, receiver_email,
                         message, subject="default subject")

        def getMethod(self, funcs):
            return getattr(self, funcs, self.log_warning)

    @staticmethod
    def log(*string: str or object, print_sep: str = ' ', print_end: str = "\n",
            print_file: object = sys.stdout,
            print_flush: bool = None, need_time_stamp: bool = True, level: str = INFO, is_test_out: bool = False,
            **email_param):
        func_factory = Logs.LOG()
        funcs = func_factory.getMethod("log_" + level)
        log(*string, print_sep=print_sep, print_end=print_end, print_file=print_file, print_flush=print_flush,
            need_time_stamp=need_time_stamp, is_test_out=is_test_out, funcs=funcs, level=level, **email_param)

    @staticmethod
    def log_warn(*string: str or object, print_sep: str = ' ', print_end: str = "\n",
                 print_file: object = sys.stdout,
                 print_flush: bool = None, need_time_stamp: bool = True):
        Logs.log(*string, print_sep=print_sep, print_end=print_end, print_file=print_file, print_flush=print_flush,
                 need_time_stamp=need_time_stamp, is_test_out=False, level=WARN)

    @staticmethod
    def log_info(*string: str or object, print_sep: str = ' ', print_end: str = "\n",
                 print_file: object = sys.stdout,
                 print_flush: bool = None, need_time_stamp: bool = True):
        Logs.log(*string, print_sep=print_sep, print_end=print_end, print_file=print_file, print_flush=print_flush,
                 need_time_stamp=need_time_stamp, is_test_out=False, level=INFO)

    @staticmethod
    def log_debug(*string: str or object, print_sep: str = ' ', print_end: str = "\n",
                  print_file: object = sys.stdout,
                  print_flush: bool = None, need_time_stamp: bool = True):
        Logs.log(*string, print_sep=print_sep, print_end=print_end, print_file=print_file, print_flush=print_flush,
                 need_time_stamp=need_time_stamp, is_test_out=False, level=DEBUG)

    @staticmethod
    def log_error(*string: str or object, print_sep: str = ' ', print_end: str = "\n",
                  print_file: object = sys.stdout,
                  print_flush: bool = None, need_time_stamp: bool = True):
        Logs.log(*string, print_sep=print_sep, print_end=print_end, print_file=print_file, print_flush=print_flush,
                 need_time_stamp=need_time_stamp, is_test_out=False, level=ERROR)

    def log_email(self, message, subject="default subject"):
        send_email(sender_email=self.sender_email, sender_password=self.sender_password,
                   receiver_email=self.receiver_email, message=message, subject=subject)


class CanStopThread(threading.Thread):

    def __init__(self) -> None:
        super().__init__()

    def stop(self):
        raise ThreadStopException()

    def save_dict(self) -> bool:
        if global_val.get_value(STORAGE_CONF) == STORAGE_REDIS:
            return True
        else:
            log("保存dict")
            d = ProxyDict()
            return d.save()


class ThreadGetter(CanStopThread):
    def __init__(self, redis_host: str, redis_port: int, redis_password: str, redis_database: str,
                 storage: str, need_log: bool = True, getter_cycle: float = 100):
        threading.Thread.__init__(self)
        self.need_log = need_log
        self.host = redis_host
        self.port = redis_port
        self.password = redis_password
        self.database = redis_database
        self.storage = storage
        self.getter_cycle = getter_cycle

    def run(self):
        log("启动getter")
        g = Getter(redis_host=self.host, redis_port=self.port,
                   redis_password=self.password, redis_database=self.database,
                   need_log=self.need_log, storage=self.storage)
        loop = 0
        while True:
            if self.need_log:
                log(f'getter loop {loop} start...')
            g.run()
            loop += 1
            time.sleep(self.getter_cycle)


class ThreadTester(CanStopThread):
    def __init__(self, redis_host: str, redis_port: int, redis_password: str, redis_database: int,
                 storage: str, need_log: bool = True, tester_cycle: float = 20):
        threading.Thread.__init__(self)
        self.need_log = need_log
        self.host = redis_host
        self.port = redis_port
        self.password = redis_password
        self.database = redis_database
        self.storage = storage
        self.tester_cycle = tester_cycle

    def run(self):
        log("启动tester")
        t = Tester(redis_host=self.host, redis_port=self.port,
                   redis_password=self.password, redis_database=self.database,
                   need_log=self.need_log, storage=self.storage)
        loop = 0
        while True:
            if self.need_log:
                logger.debug(f'tester loop {loop} start...')
            t.run()
            loop += 1
            time.sleep(self.tester_cycle)


class ThreadServer(CanStopThread):
    def __init__(self, host, port, threaded):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.threaded = threaded

    def run(self):
        log("启动server")
        app.run(host=self.host, port=self.port, threaded=self.threaded, use_reloader=False)


def set_cross_file_variable(key_val: List[tuple]) -> bool:
    """
    设置全局跨文件变量，根据给出的tuple列表
    :param key_val: 列表，其中元素为tuple，第一个元素为key，第二为value
    :return:
    """
    if type(key_val) != list:
        log("全局变量设置错误，请提供List类型并且保证所有元素都是tuple", print_file=sys.stderr)
        return False
    for k_v in key_val:
        if type(k_v) != tuple:
            log("全局变量设置错误，请提供List类型并且保证所有元素都是tuple", print_file=sys.stderr)
            return False
    global_val._init()
    for k_v in key_val:
        try:
            global_val.set_value(k_v[0], k_v[1])
        except Exception as e:
            log("设置全局跨文件变量{}错误：{}".format(k_v, e), print_file=sys.stderr)
            return False
    return True


def is_ip(proxy_test: str = "") -> bool:
    """
    测试字符串是否是一个http | https ip地址
    :param proxy_test: 待测试字符串
    :return:是则返回True
    """
    flag = False
    if type(proxy_test) != str:
        log("参数{}不是字符串".format(proxy_test), print_file=sys.stderr)
        return False
    if len(proxy_test) == 0:
        return flag
    for i in list(proxy_test):
        if i != ":" and i != "." and not i.isdigit() and i != "h" and i != "h" and (
                i != "t") and i != "p" and i != "s" and i != "/":
            flag = False
            break
        if i == list(proxy_test)[len(proxy_test) - 1]:
            flag = True
    return flag


def stop_thread(thread_list: List[CanStopThread] = []) -> int:
    count = 0
    for t in thread_list:
        try:
            t.stop()
        except ThreadStopException as e:
            log("线程{}结束".format(t.name), print_file=sys.stderr)
            count = count + 1
        except Exception as e:
            log("结束线程{}错误{}".format(t.name, e), print_file=sys.stderr)
    return count


def basic_config(log_file_name: str = "crawler_util.log",
                 log_level=logging.DEBUG,
                 proxy_pool_url: str = "",
                 logs_style: str = LOG_STYLE_PRINT,
                 require_proxy_pool: bool = False,
                 redis_host: str = "127.0.0.1",
                 redis_port: int = 6379,
                 redis_database: int = 0,
                 redis_password: str = "",
                 redis_key: str = "proxies:universal",
                 redis_string: str = "",
                 need_getter_log: bool = True,
                 need_tester_log: bool = True,
                 need_storage_log: bool = True,
                 api_host: str = "127.0.0.1",
                 api_port: int = 5555,
                 proxypool_storage: str = STORAGE_REDIS,
                 set_daemon: bool = True,
                 proxy_score_max: int = 100,
                 proxy_score_min: int = 0,
                 proxy_score_init: int = 10,
                 proxy_number_max: int = 50000,
                 proxy_number_min: int = 0,
                 dict_store_path: str = "dict.db",
                 tester_cycle: float = 20,
                 getter_cycle: float = 100,
                 test_batch: int = 20,
                 getter_timeout: int = 10,
                 tester_timeout: int = 10,
                 tester_url: str = BAIDU,
                 enable_tester: bool = True,
                 enable_getter: bool = True,
                 enable_server: bool = True,
                 test_valid_stats: List[int] = [200, 206, 302],
                 api_threaded: bool = True,
                 test_anonymous: bool = True,
                 keep_process_bar_style: bool = True,
                 keep_process_bar_style_file: object = sys.stderr,
                 is_test_out: bool = True) -> tuple:
    """
    :param is_test_out: 是否需要输出测试内容
    :param keep_process_bar_style_file: 保持进度条格式时，需要的输出流参数
    :param keep_process_bar_style: 是否保持进度条格式，如果此项为True，则log函数中参数print_file参数不会生效
    :param test_anonymous: 是否仅获取匿名代理，默认为True
    :param api_threaded:
    :param test_valid_stats: 测试代理时，指定什么状态为代理可以使用
    :param enable_server: 是否启动flask server线程
    :param enable_getter: 是否启动代理爬虫线程
    :param enable_tester: 是否启动测试代理线程
    :param tester_url: 代理链接的测试目的url
    :param tester_timeout: 测试代理时，访问测试链接tester_url的超时时间
    :param getter_timeout: 爬虫的超时时间
    :param redis_string: redis链接信息，优先使用这个参数
    :param redis_key: redis键值
    :param test_batch: 每次测试的链接数量，由于windows系统和linux系统均对最大文件打开数量
    有限制（windows：509， linux：1024）所以，该值推荐在500以内
    :param getter_cycle: 每轮爬虫线程获取代理连接之间的间隔，单位为秒
    :param tester_cycle: 每轮测试线程获取代理连接之间的间隔，单位为秒
    :param dict_store_path: 选择字典方式存储时，最后文件保存的地址（同时也是加载地址）
    :param proxy_number_min: 最小池容量
    :param proxy_number_max: 最大池容量
    :param proxy_score_init: proxy评分的初始值，添加的时候自动赋值为该值
    :param proxy_score_min: proxy评分的最小值，小于此值时，丢弃
    :param proxy_score_max: proxy评分的最大值，测试可用时，赋值为该值
    :param set_daemon: 设置是否需要守护线程，即主线程结束，子线程也结束
    :param need_storage_log: 是否需要存储模块（redis)等的日志信息（不影响重要信息输出）
    :param proxypool_storage:代理池的存储方式，可以选择redis或者dict
    :param api_port: FLASK端口
    :param api_host: FLASK地址
    :param redis_password: redis 密码
    :param need_tester_log: 是否需要测试代理模块的日志信息（不影响重要信息输出）
    :param need_getter_log: 是否需要获取代理模块的日志信息（不影响重要信息输出）
    :param redis_database: redis数据库
    :param redis_port: redis端口号
    :param redis_host: redis主机ip
    :param require_proxy_pool: 是否需要启用proxy_pool项目获取代理连接
    :param log_file_name: 日志文件名称
    :param log_level: 日志等级
    :param proxy_pool_url: 代理获取地址
    :param logs_style: log表示使用日志文件，print表示使用控制台，all表示两者都使用
    :return:
    """
    global PROXY_POOL_URL, PROXY_POOL_CAN_RUN_FLAG
    global log_style
    if len(log_file_name) != 0 and log_level != 0 and (logs_style == LOG_STYLE_ALL or logs_style == LOG_STYLE_LOG):
        logging.basicConfig(filename=log_file_name, level=log_level, force=True)
    set_cross_file_variable(
        [(REDIS_CONF, (redis_host, redis_port, redis_password, redis_database, redis_key, redis_string)),
         (STORAGE_CONF, proxypool_storage), (CROSS_FILE_GLOBAL_DICT_CONF, {}),
         (STORAGE_LOG_CONF, need_storage_log), (GETTER_LOG_CONF, need_getter_log),
         (TESTER_LOG_CONF, need_tester_log), (PROXY_SCORE_MAX, proxy_score_max),
         (PROXY_SCORE_MIN, proxy_score_min), (PROXY_SCORE_INIT, proxy_score_init),
         (POOL_MAX, proxy_number_max), (POOL_MIN, proxy_number_min),
         (DICT_STORE_PATH, dict_store_path), (TEST_BATCH_NUM, test_batch),
         (API_HOST, api_host), (API_PORT, api_port), (TESTER_TIMEOUT, tester_timeout),
         (GETTER_TIMEOUT, getter_timeout), (TESTER_URL, tester_url),
         (ENABLE_TESTER, enable_tester), (ENABLE_GETTER, enable_getter),
         (ENABLE_SERVER, enable_server), (TEST_VALID_STATUS, test_valid_stats), (TEST_ANONYMOUS, test_anonymous),
         (API_THREADED, api_threaded), (KEEP_PROCESS_BAR_STYLE, keep_process_bar_style),
         (KEEP_PROCESS_BAR_STYLE_FILE, keep_process_bar_style_file), (IS_LOG_TEST_MODE, is_test_out),
         (GLOBAL_LOG_LEVEL, log_level)])
    PROXY_POOL_URL = proxy_pool_url if len(proxy_pool_url) != 0 else PROXY_POOL_URL
    log_style = logs_style
    if require_proxy_pool and PROXY_POOL_CAN_RUN_FLAG and len(
            redis_host) > 0 and 0 <= redis_database <= 65535 and (
            0 <= redis_port <= 65535) and len(api_host) > 0 and (65535 >= api_port >= 0):
        s = None
        t = None
        g = None
        try:
            if enable_tester:
                t = ThreadTester(redis_host=redis_host, redis_port=redis_port, redis_password=redis_password,
                                 redis_database=redis_database, need_log=need_tester_log, storage=proxypool_storage,
                                 tester_cycle=tester_cycle)
                t.setDaemon(set_daemon)
                t.start()
            if enable_getter:
                g = ThreadGetter(redis_host=redis_host, redis_port=redis_port, redis_password=redis_password,
                                 redis_database=redis_database, need_log=need_getter_log, storage=proxypool_storage,
                                 getter_cycle=getter_cycle)
                g.setDaemon(set_daemon)
                g.start()
            if enable_server:
                s = ThreadServer(host=api_host, port=api_port, threaded=api_threaded)
                s.setDaemon(set_daemon)
                s.start()
        except Exception as e:
            log("proxypool线程异常{}".format(e), print_file=sys.stderr)
        proxy_test = ""
        url = HTTP + api_host + COLON_SEPARATOR + str(api_port) + "/random"
        is_ip_flag = False
        log("所有线程启动，测试是否已经有代理.......")
        if enable_server and enable_getter:
            while len(proxy_test) == 0 or (not is_ip_flag):
                try:
                    proxy_test = requests.get(url, timeout=(20, 20)).text
                    is_ip_flag = is_ip(proxy_test)
                except Exception as e:
                    log("测试proxypool项目报错:{}".format(e), print_file=sys.stderr)
                    proxy_test = ""
                time.sleep(2)
            if len(proxy_pool_url) == 0:
                PROXY_POOL_URL = url
        log("启动proxypool完成")
        PROXY_POOL_CAN_RUN_FLAG = False
        return s, g, t
    else:
        if require_proxy_pool and PROXY_POOL_CAN_RUN_FLAG:
            log("redis或者Flask配置错误", print_file=sys.stderr)
            return ()
        elif require_proxy_pool and not PROXY_POOL_CAN_RUN_FLAG:
            log("无法重复启动proxypool")
            return ()
        elif not require_proxy_pool:
            return ()
        return ()


def get_split(lens: int = 20, style: str = '=') -> str:
    """
    get a series of splits,like "======"
    :param lens: the length of split string
    :param style: the char used to create split string
    :return: a string of split
    """
    s = ''
    lens = max(lens, 1)
    for i in range(lens):
        s = s + style
    return s


def get_proxy() -> str or None:
    """
    get a proxy from proxy url which create by me to collect
    ip proxies
    :return:
    """
    if len(PROXY_POOL_URL) <= 0:
        log("使用了代理（require_proxy=Ture）,但是没有设置代理连接", print_file=sys.stderr)
        log("请使用basic_config(proxy_pool_url=\"\")设置", print_file=sys.stderr)
        raise Exception("无法获取代理连接")
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError as e:
        log(e, print_file=sys.stderr)
        return None


def two_one_choose(p: int = 0.5) -> bool:
    """
    :parameter p:概率, 0 <= p <= 1
    :return: return a bool value which decide whether choose two choices
    """
    k = random.randint(0, 10)
    if k > p * 10:
        return True
    else:
        return False


def local_path_generate(folder_name: str = "", file_name: str = "",
                        suffix: str = ".pdf", need_log: bool = True,
                        create_folder_only: bool = False) -> str:
    """
    create a folder whose name is folder_name in folder which code in if folder_name
    is not exist. and then concat pdf_name to create file path.
    :param create_folder_only: 是否只创建文件夹
    :param need_log: 是否需要日志，不影响重要信息输出
    :param suffix: 自动命名时文件后缀
    :param folder_name: 待创建的文件夹名称
    :param file_name: 文件名称，带后缀格式
    :return: 返回文件绝对路径
    """
    if folder_name is None or len(folder_name) == 0:
        folder_name = os.path.abspath(".")
    try:
        if os.path.exists(folder_name):
            if need_log:
                log("文件夹{}存在".format(folder_name))
        else:
            os.makedirs(folder_name)
    except Exception as e:
        log("创建文件夹{}失败".format(e), print_file=sys.stderr)
        return ""
    if create_folder_only:
        return os.path.abspath(folder_name)
    if len(file_name) == 0:
        file_name = str(time.strftime("%H_%M_%S", time.localtime()))
        file_name = file_name + str(random.randint(10000, 99999))
        file_name = file_name + suffix
    dir = os.path.abspath(folder_name)
    for k in FORBIDDEN_LIST:
        file_name = file_name.replace(k, "")
    work_path = os.path.join(dir, file_name)

    return work_path


def write_file(path: str, mode: str, string: str, encoding: str = "utf-8") -> bool:
    """
    写文件
    :param path: 文件路径
    :param mode: 模式
    :param string: 字符串
    :param encoding: 编码
    :return:
    """
    try:
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(string)
        f.close()
        log("写入文件{}成功".format(path))
        return True
    except Exception as e:
        log("写入文件{}失败：{}".format(path, e), print_file=sys.stderr)
        return False


def cookieString2CookieJar(cookie: str = "") -> RequestsCookieJar:
    """
    将字符串形式的cookie转成RequestsCookieJar
    :param cookie: 待转换的cookie字符串
    :return: RequestsCookieJar 对象
    """
    if len(cookie) == 0:
        log("cookie为空，返回空值")
        return RequestsCookieJar()
    cookie = cookie.replace(" ", "")
    cookies = cookie.split(";")
    cookie_dict = {}
    for c in cookies:
        cookie_list = list(c)
        name = ""
        value = ""
        flag = True
        for item in cookie_list:
            if item == "=" and flag:
                flag = False
                continue
            if flag:
                name = name + item
            else:
                value = value + item
        if len(name) != 0 and len(value) != 0:
            cookie_dict[name] = value
    cookie_jar = RequestsCookieJar()
    for item in cookie_dict.items():
        cookie_jar.set(item[0], item[1])
    return cookie_jar


def deleteSpecialCharFromHtmlElement(html: str = "", sep: str = "") -> str:
    """
    从html文本中删除标签，如：”<a>b</a>“ -> "b"
    :param html: html文本
    :param sep: 在每次去除完一个标签之后，加入的间隔符，如：sep=” “, ”<a>b</a>“ -> " b "
    :return: 处理完的字符串
    """
    names = []
    flag = True
    for k in list(html):
        if k == "<":
            flag = False
            continue
        if k == ">":
            flag = True
            names.append(sep)
            continue
        if flag:
            names.append(k)
    return "".join(names)


def save_obj(src: object, path: str = "") -> bool:
    """
    保存对象
    :param src: 需要保存的对象
    :param path: 保存的路径
    :return: 返回是否保存成功,True 表示成功
    """
    path = path if len(path) > 0 else local_path_generate("", suffix="." + "".join(filter(str.isalpha, str(type(src)))).
                                                          replace("class", "")).replace("main", "")
    try:
        with open(path, mode="wb") as f:
            pickle.dump(src, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        return True
    except Exception as e:
        log("保存object错误：{}".format(e), print_file=sys.stderr)
        return False


def load_obj(path: str) -> object:
    """
    加载对象
    :param path: 被加载对象的保存路径
    :return: 返回对象
    """
    res = None
    try:
        with open(path, mode="rb") as f:
            res = pickle.load(f)
        f.close()
        return res if (res is not None) else None
    except Exception as e:
        log("加载object错误：{}".format(e), print_file=sys.stderr)
        return None


def get_variable_name_from_string(string: str = "") -> str:
    """
    获得常量的名称，主要是懒得自己大写
    :param string: "list of value"
    :return: LIST_OF_VALUE = "list of value"
    """
    k = string
    return k.replace(" ", "_").upper() + " = \"" + string + "\""


class NoProxyException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return repr("无法获取代理")

    def __repr__(self) -> str:
        return super().__repr__()


class ThreadStopException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return repr("停止线程")

    def __repr__(self) -> str:
        return super().__repr__()


def generate_result(code: int = 0, msg: str = "success", data: object = None):
    """
    生成api的返回结果
    :param code: 状态码
    :param msg: 消息
    :param data: 数据
    :return:
    """
    return {"code": code, "msg": msg, "data": data}


def getAllFiles(target_dir: str, cascade: bool = True) -> list:
    """
    遍历文件夹
    :param cascade: 是否级联遍历子文件夹
    :param target_dir: 遍历的文件夹
    :return: 所有文件的名称
    """
    files = []
    if len(target_dir) == 0:
        log("文件路径为空", print_file=sys.stderr)
        return files
    try:
        listFiles = os.listdir(target_dir)
    except Exception as e:
        log("打开文件夹{}异常：{}".format(target_dir, e), print_file=sys.stderr)
        return files
    for i in range(0, len(listFiles)):
        path = os.path.join(target_dir, listFiles[i])
        if os.path.isdir(path) and cascade:
            files.extend(getAllFiles(path))
        elif os.path.isfile(path):
            files.append(path)
    return files


if __name__ == "__main__":
    basic_config(logs_style=LOG_STYLE_PRINT, log_level=EMAIL)
