# -*- coding: utf-8 -*-
# @Time    : 2022/10/21 16:39
# @Author  : 银尘
# @FileName: research_util.py
# @Software: PyCharm
# @Email   ：liwudi@liwudi.fun
import sys

from PaperCrawlerUtil.constant import *
from PaperCrawlerUtil.common_util import *
from sshtunnel import SSHTunnelForwarder
from PaperCrawlerUtil.office_util import *
import pymysql


class ResearchRecord(object):
    """
    目前，数据库和表都是限定的固定值，之后再改
    """

    def __init__(self, **db_conf) -> None:
        """
        :param db_conf:详见readme文件
        """
        if len(db_conf) <= 0:
            log("需要配置字典", print_file=sys.stderr)
            return None
        super().__init__()
        check_ssl = True if db_conf.get("ssl_ip") is not None and db_conf.get("ssl_admin") is not None and \
                            db_conf.get("ssl_pwd") is not None and db_conf.get("ssl_db_port") is not None \
                            and db_conf.get("ssl_port") is not None else False
        if check_ssl:
            self.ssl = SSHTunnelForwarder(
                ssh_address_or_host=(db_conf.get("ssl_ip"), db_conf.get("ssl_port")),
                ssh_username=db_conf.get("ssl_admin"),
                ssh_password=db_conf.get("ssl_pwd"),
                remote_bind_address=('localhost', db_conf["ssl_db_port"])
            )
            self.ssl.start()

        self.db_url = "127.0.0.1" if check_ssl else db_conf["db_url"]
        self.db_username = db_conf["db_username"]
        self.db_pass = db_conf["pass"]
        self.port = self.ssl.local_bind_port if check_ssl else db_conf["port"]
        self.db_database = "research"
        self.db_table = "record_result"
        self.db_type = "mysql"
        self.conn = None
        self.cursor = None
        self.ignore_error = db_conf.get("ignore_error") if db_conf.get("ignore_error") is not None else True
        try:
            self.create_db_conn()
            self.cursor = self.conn.cursor()
        except Exception as e:
            log("链接数据库失败，请修改配置，云服务器请配置ssl：{}".format(e))

    @staticmethod
    def create_db_table():
        return CREATE_DB_TABLE

    def create_db_conn(self):
        connection = pymysql.connect(host=self.db_url,
                                     user=self.db_username,
                                     password=self.db_pass,
                                     db=self.db_database,
                                     port=self.port
                                     )
        self.conn = connection
        self.conn.autocommit(True)

    def _execute(self, sql: str) -> bool:
        """
        内部方法，执行sql
        :param sql: 待执行的sql
        :return:
        """
        try:
            self.cursor.execute(sql)
            return True
        except Exception as e:
            log("执行失败：{}".format(e))
            if self.ignore_error:
                write_file(local_path_generate("", "record_error.log"), mode="a+", string=sql + "\n")
            return False

    def insert(self, file: str, exec_time: str) -> tuple:
        """
        插入，初始化记录，记录执行的文件，开始的时间
        :param file: 执行的文件，使用__file__即可
        :param exec_time: 开始执行的时间
        :return:
        """
        exec_time = exec_time if len(exec_time) > 0 else get_timestamp()
        sql = "insert into `{}`.`{}`(`file_execute`, `excute_time`) " \
              "values ('{}', '{}')".format(self.db_database, self.db_table, file, exec_time)
        if self._execute(sql):
            sql = "select   id   from  " + self.db_database + "." + self.db_table + \
                  " order   by   id   desc   limit   1"
            if self._execute(sql):
                return self.cursor.fetchone()
            else:
                return -1,
        else:
            return -1,

    def update(self, id: int, finish_time: str = "", result: str = "") -> bool:
        """
        执行结束之后，使用该方法更新
        :param id: 要更新的记录id，可以从插入方法的返回值获得
        :param finish_time: 结束的时间
        :param result: 执行的结果
        :return:
        """
        finish_time = finish_time if len(finish_time) > 0 else get_timestamp()
        sql = "update `" + self.db_database + "." + self.db_table + "` set result='{}', finish_time='{}' where id = {}". \
            format(result, finish_time, str(id))
        if self._execute(sql):
            return True
        else:
            return False

    def select_all(self):
        sql = "select count(*) from `" + self.db_database + "`.`" + self.db_table + "`"
        res = []
        if self._execute(sql):
            num = self.cursor.fetchone()[0]
            for i in range(int(num / 100) + 1):
                res.extend(self.select_page(page_no=i))
            return res
        else:
            return []

    def select_page(self, page: int = 100, page_no: int = 0) -> List:
        res = []
        sql = "select * from `" + self.db_database + "`.`" + self.db_table + "` LIMIT {} OFFSET {}" \
            .format(str(page), str(page_no * page))
        if self._execute(sql):
            return self.cursor.fetchall()
        else:
            return []

    def export(self, id_range: tuple or List = [-100], file_type: str = "csv", export_path: str = "") -> bool:
        """
        导出文件
        :param export_path: 导出文件的地址，默认为当前目录
        :param id_range:id的范围，可以在select general中查询，当id_range中有负值存在时，负值生效，且只生效第一个负值
        负值表示从倒数方向导出，i.e. -100表示导出最后100条。 tuple表示连续的id值，list表示单个id，tuple不支持负值
        :param file_type: 导出的类型，包括["csv", "xls"]
        :return:
        """
        id_list = []
        neg_flag = False
        if type(id_range) == list:
            for i in id_range:
                if i < 0:
                    id_list.clear()
                    id_list.append(i)
                    neg_flag = True
                    break
                id_list.append(i)
        elif type(id_range) == tuple:
            if len(id_range) == 1:
                id_list.append(id_range[0])
            elif len(id_range) >= 2:
                l = id_range[0] if id_range[0] <= id_range[1] else id_range[1]
                r = id_range[1] if id_range[0] <= id_range[1] else id_range[0]
                for i in range(l, r):
                    id_list.append(i)
        else:
            log("仅支持tuple和list", print_file=sys.stderr)
            return False
        res_list = []
        if neg_flag:
            sql = "select * from  " + self.db_database + "." + self.db_table + \
                  " order by id desc limit {}".format(str(abs(id_list[0])))
            if self._execute(sql):
                temp = []
                for i in self.cursor.fetchall():
                    temp.append(list(i))
                res_list.extend(temp)
            else:
                res_list.extend([])
        else:
            s = ""
            for i in range(len(id_list)):
                if i == len(id_list) - 1:
                    s = s + "'" + str(id_list[i]) + "'"
                else:
                    s = s + "'" + str(id_list[i]) + "', "
            sql = "select * from  " + self.db_database + "." + self.db_table + \
                  " where id in({})".format(s)
            if self._execute(sql):
                temp = []
                for i in self.cursor.fetchall():
                    temp.append(list(i))
                res_list.extend(temp)
            else:
                res_list.extend([])
        res_list.insert(0, TABLE_TITLE)
        export_path = export_path if len(export_path) > 0 else \
            local_path_generate("", suffix=".csv" if file_type == "csv" else ".xls")
        try:
            if file_type == "csv":
                csv = CsvProcess()
                csv.write_csv(res_list, write_path=export_path)
            else:
                ExcelProcess().write_excel(res_list, path=export_path)
            return True
        except Exception as e:
            log("导出失败：{}".format(e))
            return False

    def __del__(self):
        if self.ssl is not None:
            self.ssl.close()
        if self.conn is not None:
            self.conn.close()
        if self.cursor is not None:
            self.cursor.close()


if __name__ == "__main__":
    basic_config(logs_style=LOG_STYLE_PRINT)
