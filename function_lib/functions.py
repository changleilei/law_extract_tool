import re
import requests
import json
import pymysql

conn = pymysql.connect(host="192.168.120.4", port=3306, user="root", password="root", db="flfgk", charset='utf8')


def ltp_tool(text, target):
    """
    使用 LTP 作语义分析
    :param text: 输入句子
    :param target: 选择解析器(seg, ner, parse, srl)
    :return:
    """
    url_prefix = 'http://192.168.2.32:8082/ltp'
    # url_prefix = 'http://localhost:5000/ltp'
    # url_prefix = 'http://192.168.70.110:8082/ltp'

    json_str = {'text': text}
    url = url_prefix + '/' + target
    res = requests.post(url, json=json_str)
    if res.status_code == 200:
        ltp_result_json = res.text.replace("'", '"')
        print('ltp_result_json:', ltp_result_json)
        if not ltp_result_json:
            return None
        try:
            ltp_result_dict = json.loads(ltp_result_json, encoding='UTF-8')
            return ltp_result_dict
        except Exception:
            print('error_ltp: ', ltp_result_json)

    else:
        return None


def read_from_file(path):
    with open(path, 'r', encoding='UTF-8') as infile:
        return infile.readlines()


def get_data_from_mysql(sql):
    with conn.cursor() as cursor:
        cursor.execute(sql)
        records = cursor.fetchall()
    return records


def write_data_to_mysql(sql, args):
    with conn.cursor() as cursor:
        cursor.executemany(sql, args)
        conn.commit()