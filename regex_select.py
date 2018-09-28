# coding:utf-8
from function_lib.rule_table import *
from function_lib.functions import *
from model_1.law_extract_one import do_regex_one, law_item_parse_j
from model_2.law_extract_two import do_regex_two, item_info_parse_j
from model_3.law_extract_three import sentences_to_parts_three
from model_4.law_extract_four import sentences_to_parts_four
import uuid

regex1 = '.*(下列|以下|如下).*'

regex2 = '.*(应当|不得|禁止|严禁|可以|方可).*'

regex3 = '(.*?)(由|按照)(.*)'

regex4 = '(.*?)(责令|没收)(.*)'
item_list = ['逾期不改正的，撤销港口岸线使用批准文件', '情节严重的，吊销港口经营许可证','有违法所得的，没收违法所得','逾期不改正的，可以处五千元以上二万元以下的罚款',
             '经限期整改仍未达到法定许可条件的，依法吊销其港口经营许可证','造成严重后果，构成犯罪的，依法追究刑事责任', '逾期仍不缴纳的，依法申请人民法院强制执行。']


def write_to_file_append(res, path, flag=1):
    with open(path, 'a+', encoding='UTF-8') as outfile:
        for s in res:
            if flag == 0:
                outfile.write('\t'.join(map(str, s)).replace(r'\u3000', ' ').replace('\n','') + '\n')
            else:
                outfile.write(str(s).replace(r'\u3000', ' ') + '\n')
        # print('lines:', len(res))


def regex_filter(sentence, reg):
    return re.match(reg, sentence)


def tag_by_regex(sentence):
    """
    按句式选择标注算法
    :param sentence: 句子
    :return: 标注结果
    """
    if regex_filter(sentence, regex1):
        # print('Use regex-1:', regex1)
        return do_regex_one(sentence), 1
    elif regex_filter(sentence, regex2):
        # print('Use regex-2:', regex2)
        return do_regex_two(sentence), 2
    elif regex_filter(sentence, regex3):
        return ('Use regex-3:', regex3), 3
    elif regex_filter(sentence, regex4):
        return ('Use regex-4:', regex4) ,4
    else:
        return None, 0



# 传入参数：需要知道对应的法条line，剩下两个不会用到
def sentences_to_parts(line):
    # 如果有（一）……（十） 以及“以下”，“如下”等，则证明属于第一类，然后需要判断它是否应该属于在行为中，若是（一）……（十），则需要放在行为中
    # 否则需要再划分

    content = line.strip().replace('；', '</p>').replace(' ', ''). \
        replace('“', '').replace('”', '').replace('\u3000', '').replace('<p>', '').replace('\ufeff', '')
    contents = content.split('</p>')

    # 判断是否有model_1和model_2的句子
    if (has_key_one(content) or has_key_one_v2(content)) and has_key_one_plus(content) :
        write_to_file_append([content], 'model_1_sentence.out')
        generate_temp = sentences_to_parts_one(contents)
        return generate_temp, 1
    elif filter_four(content) and not has_key_three(content):
        generate_temp = sentences_to_parts_four(contents)
        return generate_temp, 4
    elif not has_key_two_plus(content) and has_key_two(content):
        generate_temp = sentences_to_parts_two(contents)
        return generate_temp, 2
    elif has_key_three(content) and not filter_three_v3(content):
        generate_temp = sentences_to_parts_three(contents)
        return generate_temp, 3
    else:
        write_to_file_append(contents, 'not_parse1.txt')
        return None, 0


# 第一类
def sentences_to_parts_one(contents):
    # 这两个flag用于检验“以下”和“（一）……（十）”
    beg_flag = 0
    num_flag = 0
    # content_temp 用于暂存（一）……（十）文本
    content_temp = ''
    generated_template = []

    for item in contents:
        if item == '':
            continue

        # 如果未能检测到（以下，如下，下列）等关键词
        elif (has_key_one_plus(item) is False) and beg_flag == 0:
            if has_key_two(item):
                continue

        # 如果第一次检测到（下列，以下，如下）关键词
        elif has_key_one_plus(item) and has_key_one_v3(item) and beg_flag == 0:
            beg_flag = 1
            content_temp += item + '</p>'
        # 检测到（一）……（十)
        elif ((has_key_one(item) or (has_key_one_v2(item) or has_key_one_v4(item)) and has_key_one_v3(item))) and beg_flag == 1:
            content_temp += item + '</p>'
            num_flag = 1
        # 未检测到（一）……（十）前要一直用content_temp存储
        elif (has_key_one(item) is False) and beg_flag == 1 and num_flag == 0:
            content_temp += item
            content_temp = re.sub('</p>', '，', content_temp)
            content_temp += '</p>'
        elif(has_key_one(item) is False) and beg_flag == 1 and (item in item_list):  # 参见
            content_temp = re.sub('(</p>)+$', '，', content_temp)
            content_temp += item
            content_temp += '</p>'
        # 处理content_temp
        elif (has_key_one(item) is False) and beg_flag == 1 and num_flag == 1:
            generated_template.append(law_item_parse_j(content_temp))
            content_temp = ''
            beg_flag = 0
            num_flag = 0
    if len(generated_template) == 0:
        generated_template.append(law_item_parse_j(content_temp))

    return generated_template


# 第二类
def sentences_to_parts_two(lines):
    generated_final = []
    sub_temp = ''
    for i, s in enumerate(lines):
        if s == '':
            continue
        # 主函数
        generated_template_list = item_info_parse_j(s)  # 原版model2
        # generated_template = item_info_parse_cll(s)  # v2版
        # 用分号隔开的两句话，若本句没有主语，则拿上一句的主语过来作为本句主语
        for item in generated_template_list[:]:

            if item['subject'] != '':
                sub_temp = item['subject']
            elif item['subject'] == '':
                item['subject'] = sub_temp
            generated_final.append(item)
    return generated_final


def law_to_sentence(sentence):
    """
    法条拆分成句子
    :param sentence: 法条句子
    :return: 拆分后的句子列表和ID列表
    """
    line = sentence.strip().replace('“', '').replace('”', '').replace('\u3000', '').replace('\r', '')\
        .replace('\n', '').replace('\ufeff', '').replace('。', '。</p>|<p>').replace('。</p><p>', '。</p>|<p>')

    con = line.split('|')

    # sen是句子对应的list，sen_id是句子对应的id的list
    sen = []
    sen_id = []
    for c in con:
        c = c.replace('<p></p>', '')
        if c == '<p>' or c == '</p>' or c == '<p></p>' or len(c) <= 1:
            continue
        sentence_id = str(uuid.uuid1())
        sen_id.append(sentence_id)
        sen.append(c)
    return sen_id, sen


if __name__ == '__main__':
    print()
    get_sentence_sql = 'select item_id, sentence from law_item_split limit 0, 500'
    # sentences = get_data_from_mysql(get_sentence_sql)
    sentences = [('1', '<p>六、第二十二条修改为：“汽车贷款发放实施贷款最高发放比例要求制度，贷款人发放的汽车贷款金额占借款人所购汽车价格的比例，不得超过贷款最高发放比例要求；贷款最高发放比例要求由中国人民银行、中国银行业监督管理委员会根据宏观经济、行业发展等实际情况另行规定。</p>')]

    for s in sentences:
        item_id, content = s[0], s[1]
        split_result, _ = sentences_to_parts(content)
        if split_result:
            print(item_id, content, '\n', split_result, '\n')

