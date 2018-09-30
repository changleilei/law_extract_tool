from function_lib import functions
from function_lib import rule_table
from data_process.data_operate import get_data_from_mysql
from DB_pool import db_pooling

def demo(sentence):
    parse_result = functions.ltp_tool(sentence, 'srl')
    print(parse_result)
    filter_three_res = rule_table.filter_three(sentence)
    print(filter_three_res)


def get_data():
    sql = 'select lc.item_condition, ls.item_subject, lk.item_key, lb.item_behavior, lr.item_result , lit.sentence ' \
          'from  lawcrf_behavior lb left join law_item_split lit on lit.id = lb.sentence_id ' \
          'left join lawcrf_condition lc on lb.condition_id = lc.id ' \
          'left join lawcrf_subject ls on lb.subject_id = ls.id ' \
          'left join lawcrf_key lk on lb.key_id = lk.id ' \
          'left join lawcrf_result lr on lb.result_id = lr.id'
    data = get_data_from_mysql(sql)
    for item in data:
        print(item)
    return data


if __name__=='__main__':
    dbop = db_pooling.DBPool()
    sql = 'select * from law_item_split where `index`>=3968080'
    # sql = "INSERT INTO law_item_split VALUES (%s,%s,%s,%s,%s,%s,%s)"
    id = '1'
    law_id = '1'
    item_id = '1'
    sentence = 'test'
    law_title = 'test'
    chapter = 'test'
    sql_args = [id, law_id, item_id, sentence, law_title, chapter, 0]
    result = dbop.op_select(sql)
    # num = dbop.op_insert(sql, [sql_args])
    print(result)
    dbop.dispose()