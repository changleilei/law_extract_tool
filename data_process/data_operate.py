import sys
import uuid
sys.path.append(r'F:\law_git_cll')
from model_2 import law_extract_two as lof
from function_lib.functions import *
from regex_select import sentences_to_parts
import logging
import time
from function_lib.rule_table import *


def write_to_file(res, path, flag=1):
    with open(path, 'w', encoding='UTF-8') as outfile:
        for s in res:
            if flag == 0:
                outfile.write('\t'.join(map(str, s)).replace(r'\u3000', ' ').replace('\n','') + '\n')
            else:
                outfile.write(str(s).replace(r'\u3000', ' ') + '\n')
        print('lines:', len(res))


def write_to_file_append(res, path, flag=1):
    with open(path, 'a+', encoding='UTF-8') as outfile:
        for s in res:
            if flag == 0:
                outfile.write('\t'.join(map(str, s)).replace(r'\u3000', ' ').replace('\n','') + '\n')
            else:
                outfile.write(str(s).replace(r'\u3000', ' ') + '\n')
        print('lines:', len(res))


# 驾驶机动车有下列情形之一的，处200元罚款
def regex_filter(sentences, reg):
    data = []
    for s in sentences:
        matcher = re.match(reg, s)
        if matcher:
            data.append(matcher.group())
    return data


def not_filter(sentences, reg):
    data = []
    for s in sentences:
        matcher = re.match(reg, s)
        if not matcher:
            data.append(s)
    return data


def build_condition(condition_id, sentence_id, condition):
    condition_sql = 'insert into lawcrf_condition values (%s,%s,%s)'
    condition_args = [condition_id, str(sentence_id), condition]
    write_data_to_mysql(condition_sql, [condition_args])


def build_subject(subject_id, sentence_id,  subject):
    subject_sql = 'insert into lawcrf_subject values (%s,%s,%s)'
    subject_args = [subject_id, str(sentence_id), subject]
    write_data_to_mysql(subject_sql, [subject_args])


def build_behavior(behavior_id, sentence_id, behavior, condition_id, subject_id, result_id, key_id=None):
    behavior_sql = 'insert into lawcrf_behavior values (%s,%s,%s,%s,%s,%s,%s)'
    behavior_args = [behavior_id, str(sentence_id), behavior, condition_id, subject_id, result_id,  key_id]
    write_data_to_mysql(behavior_sql, [behavior_args])


def build_result(result_id, sentence_id, result):
    result_sql = 'insert into lawcrf_result values (%s,%s,%s)'
    result_args = [result_id, str(sentence_id), result]
    write_data_to_mysql(result_sql, [result_args])


def build_key(key_id, sentence_id, key):
    key_sql = 'insert into lawcrf_key values (%s,%s,%s)'
    key_args = [key_id, str(sentence_id), key]
    write_data_to_mysql(key_sql, [key_args])


def full_result_1(data):
    # sql_1 = 'select law_item_id, full_result from lawcrflabel where template_num = 1'
    # data = get_data_from_mysql(sql_1)
    # print('data_1 size:', len(data))
    for i, t in enumerate(data[:]):
        # print(str(i) + '--' + str(t))
        sentence_id = t[0]
        full_result = t[1]
        # full_result = full_result.replace("'", '"')
        # full_result_dict = json.loads(full_result, encoding='UTF-8')
        for res in full_result:
            full_result_dict = res
            if not full_result_dict:
                continue
            condition = full_result_dict['condition']
            subject = full_result_dict['subject']
            behavior = full_result_dict['behavior']
            result = full_result_dict['result']
            # key = full_result_dict['key']

            condition_id = None
            if len(condition) > 1:
                condition_id = str(uuid.uuid1())
                build_condition(condition_id, sentence_id, condition)

            result_id = None
            if len(result) > 1:
                result_id = str(uuid.uuid1())
                build_result(result_id, sentence_id, result)

            subject_id = None
            if isinstance(subject, str):
                if len(subject) > 1:
                    subject_id = str(uuid.uuid1())
                    build_subject(subject_id, sentence_id, subject)
                if behavior:
                    for be in behavior:
                        behavior_id = str(uuid.uuid1())
                        build_behavior(behavior_id, sentence_id, be, condition_id, subject_id, result_id,  None)
            elif isinstance(subject, list):
                for i, su in enumerate(subject):
                    if su != '':
                        subject_id = str(uuid.uuid1())
                        build_subject(subject_id, sentence_id, su)
                    if behavior:
                        behavior_id = str(uuid.uuid1())
                        build_behavior(behavior_id, sentence_id, behavior[i], condition_id, subject_id, result_id, None)


def full_result_2(data):
    # sql_2 = 'select law_item_id, full_result from lawcrflabel where template_num = 2'
    # data = get_data_from_mysql(sql_2)
    # print('data_2 size:', len(data))
    for i, t in enumerate(data[:]):
        # print(str(i) + '--' + str(t))
        sentence_id = t[0]
        full_result = t[1]
        # full_result = full_result.replace("'", '"')
        for res in full_result:
            # full_result_dict = json.loads(re, encoding='UTF-8')
            full_result_dict = res
            if not full_result_dict:
                continue
            condition = full_result_dict['condition']
            subject = full_result_dict['subject']
            behavior = full_result_dict['behavior']
            key = full_result_dict['key']

            condition_id = None
            if condition:
                condition_id = str(uuid.uuid1())
                build_condition(condition_id, sentence_id, condition)

            subject_id = None
            if subject:
                subject_id = str(uuid.uuid1())
                build_subject(subject_id, sentence_id, subject)

            result_id = None
            key_id = None
            if key:
                key_id = str(uuid.uuid1())
                build_key(key_id, sentence_id, key)

            if behavior:
                behavior_id = str(uuid.uuid1())
                build_behavior(behavior_id, sentence_id, behavior, condition_id, subject_id, result_id, key_id)


def full_result_3(data):
    # print('data_3 size:', len(data))
    for i, t in enumerate(data[:]):
        # print(str(i) + '--' + str(t))
        sentence_id = t[0]
        full_result = t[1]
        for res in full_result:
            full_result_dict = res
            if not full_result_dict:
                continue
            condition = full_result_dict['condition']
            subject = full_result_dict['subject']
            behavior = full_result_dict['behavior']
            key = full_result_dict['key']

            condition_id = None
            if condition:
                condition_id = str(uuid.uuid1())
                build_condition(condition_id, sentence_id, condition)
            # print('condition:', condition_id, sentence_id, condition)

            subject_id = None
            if subject:
                subject_id = str(uuid.uuid1())
                build_subject(subject_id, sentence_id, subject)
            # print('subject:', subject_id, sentence_id, subject)

            result_id = None

            key_id = None
            if key:
                key_id = str(uuid.uuid1())
                build_key(key_id, sentence_id, key)
            # print('key', key_id, sentence_id, key)

            behavior_id = None
            if behavior:
                behavior_id = str(uuid.uuid1())
                build_behavior(behavior_id, sentence_id, behavior, condition_id, subject_id, result_id, key_id)
            # print('behavior', behavior_id, sentence_id, behavior, condition_id, subject_id, result_id, key_id)


def full_result_4(data):
    # print('data_4 size:', len(data))
    for i, t in enumerate(data[:]):
        # print(str(i) + '--' + str(t))
        sentence_id = t[0]
        full_result = t[1]
        for res in full_result:
            full_result_dict = res
            if not full_result_dict:
                continue
            # condition = full_result_dict['condition']
            # subject = full_result_dict['subject']
            result = full_result_dict['result']
            # key = full_result_dict['key']
            behavior = full_result_dict['behavior']

            condition_id = None
            # build_condition(condition_id, sentence_id, condition)
            # print('condition:', condition_id, sentence_id, condition)
            #
            subject_id = None
            # build_subject(subject_id, sentence_id, subject)
            # print('subject:', subject_id, sentence_id, subject)

            key_id = None
            # build_key(key_id, sentence_id, key)
            # print('key', key_id, sentence_id, key)

            result_id = str(uuid.uuid1())
            build_result(result_id, sentence_id, result)

            behavior_id = str(uuid.uuid1())
            build_behavior(behavior_id, sentence_id, behavior, condition_id,subject_id, result_id, key_id)


# 所有法条，按照三种句模，执行成分标注
def all_law_parse(sql):
    # sql = 'select id, law_id, item_id, sentence from law_item_split'
    all_law_data = get_data_from_mysql(sql)
    # write_to_file_append(all_law_data, 'all_law_data.out')
    data_1 = []
    data_2 = []
    data_3 = []
    data_4 = []

    for line in all_law_data[:]:
        s_id, law_id, item_id, sentence = line[0], line[1], line[2], line[3]
        result, num = sentences_to_parts(sentence)
        if not result:
            continue
        if num == 1:
            data_1.append([s_id, result])
        elif num == 2:
            data_2.append([s_id, result])
        elif num == 3:
            data_3.append([s_id, result])
        elif num == 4:
            data_4.append([s_id, result])

    write_to_file_append(data_2, 'result2.txt')
    for item in data_2[:]:
        print(item)


    # full_result_1(data_1)
    # full_result_2(data_2)
    # full_result_3(data_3)
    # full_result_4(data_4)


def take_out_colon(num, item):
    num1 = ''
    item1 = item
    pattern = re.compile('^(.*?)：')
    sub_matcher = pattern.findall(item)
    if sub_matcher:
        num1 = num + sub_matcher[0]
        item1 = item.replace(num, '')
    return num1, item1


def take_out_num(num, item):
    num1 = ''
    item1 = item
    pattern = re.compile('^(第.*?条)')
    sub_matcher = pattern.findall(item)
    if sub_matcher:
        num1 = num + sub_matcher[0]
        item1 = item.replace(num, '')
    return num1, item1


def law_to_sentences(law_id, item_id, line):
    num = ''
    line = line.strip().replace('；', '</p>').replace('\t', '</p>').replace('。', '</p>').replace(' ', '').replace('“', '').replace('”', '')
    contents_temp = line.split('</p>')
    le = len(contents_temp)
    sen = []
    sen_id = []
    for i in range(0, le):
        item = contents_temp[i].replace('\u3000', '').replace('<p>', '').replace('</p>', '')
        item = remove_dun(item)
        num, item = take_out_num(num, item)
        num, item = take_out_colon(num, item)
        if item:
            item = '<p>' + ' ' + item + '</p>'
            sen_id.append(str(uuid.uuid1()))
            sen.append(item)
        else:
            continue
    return law_id, item_id, sen_id, sen


if __name__ == '__main__':
    print()

    # 97644 交通领域的
    # traffic_sql = "select c.id, z.TITLE, c.CONTENT from zllawcolumn c inner join zllaw z on c.LAWID = z.id where z.TYPENAME like '%交通%'"
    # traffic_res = get_data_from_mysql(traffic_sql)
    # write_to_file(traffic_res, 'traffic_law.txt', 0)

    # 1134 
    # start = time.time()
    # reg = '.*有下列情形之一的.*'
    # traffic_data = read_from_file('traffic_law.txt')
    # traffic_punish_data = regex_filter(traffic_data, reg)
    # write_to_file(traffic_punish_data, 'traffic_punish_law.txt')
    # end = time.time()
    # print('cost time:%s s' % str(end - start))

    # 658 
    # start = time.time()
    # reg = '.*有下列情形之一的.*(处罚|罚款|警告|责令|处分|追究).*'
    # traffic_data = read_from_file('traffic_law.txt')
    # traffic_punish_data = regex_filter(traffic_data, reg)
    # write_to_file(traffic_punish_data, 'traffic_punish_law1.txt')
    # end = time.time()
    # print('cost time:%s s' % str(end-start))

    # 39984
    # start = time.time()
    # reg = '.*(应当|不得|禁止|严禁).*'
    # traffic_data = read_from_file('traffic_law.txt')
    # traffic_not_below_data = not_filter(traffic_data, '.*下列.*')
    # traffic_obli_forbid_data = regex_filter(traffic_not_below_data, reg)
    # write_to_file(traffic_obli_forbid_data, 'traffic_obligation_forbidden.txt')
    # end = time.time()
    # print('cost time:%s s' % str(end - start))

    # 将解析结果从文件写入数据库
    # model_result_parse('../model_2/result.out2', 2)

    # 解析full_result数据
    # full_result_1()

    # read_four_law()
    # four_law_parse()
    # four_law_split()
    # four_law_parse_from_db()
    import os
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 设置log等级
    rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    log_path = os.path.dirname(os.getcwd()) + '/Logs/'
    log_name = log_path + rq + '.log'
    logfile = log_name
    fh = logging.FileHandler(logfile, mode='a')
    fh.setLevel(logging.ERROR)

    # 定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    try:
        size = 10
        step = 100
        for i in range(size):
            sql = 'select lit.id, law_id, item_id, sentence from law_item_split lit LEFT JOIN zllaw ON lit.law_id = zllaw.ID  WHERE zllaw.TYPENAME like '+r"'%交通%'"+' limit '+str(i*step)+", "+str(step)
            all_law_parse(sql)
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception:
        logger.error('程序崩啦！！！', exc_info=True)





