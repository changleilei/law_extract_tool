import pymysql
from DBUtils.PooledDB import PooledDB
import json
import os

class DBPool(object):
    __pool = None

    def __init__(self):  # 构造函数，创建数据库连接
        self.conn = DBPool.getmysqlconn(self)
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)


    def get_config(self, file_name="db_config"):
        path = os.getcwd()  # 获取当前工作目录
        with open(path +'\DB_pool\\' + file_name, "r", encoding='utf8') as f:
            config = json.load(f)
        return config

    @staticmethod
    def getmysqlconn(self):
        conf = self.get_config()
        if DBPool.__pool is None:
            __pool = PooledDB(creator=pymysql,
                              mincached=conf['db_pool']['mincached'],
                              maxcached=conf['db_pool']['maxcached'],
                              maxshared=conf['db_pool']['maxshared'],
                              maxconnections=conf['db_pool']['maxconnections'],
                              blocking=conf['db_pool']['blocking'],
                              maxusage=conf['db_pool']['maxusage'],
                              setsession=None,
                              host=conf['db']['host'],
                              port=conf['db']['port'],
                              user=conf['db']['user'],
                              passwd=conf['db']['password'],
                              db = conf['db']['database'],
                              charset=conf['db']['charset']
                              )
        return __pool.connection()

    def op_select(self, sql):
        """
        查找
        :param sql:
        :return:
        """
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def op_modify(self, sql, args):
        try:
            num = self.cur.executemany(sql, args)
            self.conn.commit()
            return num
        except Exception as e:
            self.conn.rollback()

    def dispose(self):
        self.cur.close()
        self.conn.close()


if __name__=='__main__':

    ad = DBPool()
    sql = 'select * from law_item_split where `index`>=3968080'
    # sql_ = "INSERT INTO law_item_split VALUES (%s,%s,%s,%s,%s,%s,%s)"
    id = '1'
    law_id = '1'
    item_id = '1'
    sentence = 'test'
    law_title = 'test'
    chapter = 'test'
    sql_args = [id, law_id, item_id, sentence, law_title, chapter, 0]
    result = ad.op_select(sql)
    # num = ad.op_insert(sql_, [sql_args])
    print(result)

    # sql = 'select * from law_item_split where `index`>=3968080'
