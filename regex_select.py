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


def regex_filter(sentence, reg):
    return re.match(reg, sentence)


def tag_by_regex(sentence):
    """
    按句式选择标注算法
    :param sentence: 句子
    :return: 标注结果
    """
    if regex_filter(sentence, regex1):
        print('Use regex-1:', regex1)
        return do_regex_one(sentence), 1
    elif regex_filter(sentence, regex2):
        print('Use regex-2:', regex2)
        return do_regex_two(sentence), 2
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
    if has_key_one(content) and has_key_one_plus(content):
        print(content)
        generate_temp = sentences_to_parts_one(contents)
        # if generate_temp:
        #     print('Use regex-1:', regex1)
        return generate_temp, 1
    elif filter_four(content) and not has_key_three(content):
        print(content)
        generate_temp = sentences_to_parts_four(contents)
        return generate_temp, 4
    elif not has_key_two_plus(content) and has_key_two(content):
        print(content)
        generate_temp = sentences_to_parts_two(contents)
        # if generate_temp:
        #     print('Use regex-2:', regex2)
        return generate_temp, 2
    elif has_key_three(content):
        print(content)
        generate_temp = sentences_to_parts_three(contents)
        # if generate_temp:
        #     print('Use regex-3:', regex3)
        return generate_temp, 3
    else:
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
        elif has_key_one_plus(item) and beg_flag == 0:
            beg_flag = 1
            content_temp += item + '</p>'
        # 检测到（一）……（十)
        elif has_key_one(item) and beg_flag == 1:
            content_temp += item + '</p>'
            num_flag = 1
        # 未检测到（一）……（十）前要一直用content_temp存储
        elif (has_key_one(item) is False) and beg_flag == 1 and num_flag == 0:
            content_temp += item
            content_temp = re.sub('</p>', '，', content_temp)
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
    :return: 拆分后的句子列表
    """
    line = sentence.strip().replace('“', '').replace('”', '').replace('\u3000', '')\
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


def law_item_split_test():
    # 法条拆分句子测试
    sql = 'select content from zllawcolumn limit 0, 20'
    contents = get_data_from_mysql(sql)
    for c in contents:
        print(c[0])
        ids, sens = law_to_sentence(c[0])
        for s in sens:
            print(s, end='\n')
        print('\n')


if __name__ == '__main__':
    print()
    get_sentence_sql = 'select item_id, sentence from law_item_split limit 0, 500'
    # sentences = get_data_from_mysql(get_sentence_sql)
    sentences = [('1', '<p>二十五、将第四十四条改为第五十二条，修改为：经营者提供商品或者服务，造成消费者财产损害的，应当依照法律规定或者当事人约定承担修理、重作、更换、退货、补足商品数量、退还货款和服务费用或者赔偿损失等民事责任。</p><p>二十五、将第四十四条改为第五十二条，修改为：经营者提供商品或者服务，造成消费者财产损害的，应当依照法律规定或者当事人约定承担修理、重作、更换、退货、补足商品数量、退还货款和服务费用或者赔偿损失等民事责任。</p> ')]

    # sentences = [('11','<p>九、增加一条，作为第二十五条：经营者采用网络、电视、电话、邮购等方式销售商品，消费者有权自收到商品之日起七日内退货，且无需说明理由，但下列商品除外：</p><p>（一）消费者定作的；</p><p>（二）')]
    for s in sentences:
        item_id, content = s[0], s[1]
        split_result, _ = sentences_to_parts(content)
        if split_result:
            print(item_id, content, '\n', split_result, '\n')

