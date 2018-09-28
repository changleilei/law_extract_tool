from model_1 import sentence_template as st
from function_lib.rule_table import *
from function_lib.functions import *


def write_to_file_append(res, path):
    with open(path, 'a+', encoding='UTF-8') as outfile:
        for s in res:
            outfile.write(str(s).replace(r'\u3000', ' ') + '\n')


key = ['下列', '以下', '如下']
key2 = ['应当', '不得', '禁止', '可以', '由']
condition_list = ['发生', '违反本条例的规定']
condition_list_2 = ['道路交通管理处罚分为']  # 过滤第八条  道路交通管理处罚分为下列五种：</p><p>（一）警告；</p><p>（二）罚款：五十元以上、五万元以下；</p><p>（三）吊扣驾驶证：十五日以上、六十日以下；
sub_list = ['交通警察', '主管机关', '港务监督', '交通部门']
sub_list_2 = ['的', '本条例', '违反本条例']  # 除去sub_list_2中的sub

def first_item_filter(sentence):
    """
    (驾驶机动车)有下列情形之一的，(处200元罚款)
    :param sentence:
    :return:
    """
    data = []
    reg = '(.*?)(有下列情形之一的|有下列行为|下列情形|下列|以下|如下).*?(，|：)(.*)'

    matcher = re.match(reg, sentence)
    if matcher:
        data.append(matcher.group(1))
        data.append(matcher.group(4))

    return data


def second_item_filter(sentence):
    data = []
    reg = '(.*?)(不得|应当|可以)(.*)'
    matcher = re.match(reg, sentence)
    if matcher:
        data.append(matcher.group(1))
        data.append(matcher.group(3))
    return data


# 如果behavior中有result过滤取出result
def get_result_from_beh(sentence):
    data = []
    reg = '(.*?)(吊销|拘留|责令|没收|处|注销)(.*)'
    matcher = re.match(reg, sentence)
    if matcher:
        data.append(matcher.group(1))
        data.append(matcher.group(2))
        data.append(matcher.group(3))
    return data


def do_regex_one(item):
    generated_template = law_item_parse_j(item)
    print('generated_template_regex_1', generated_template)
    return generated_template


# 法律条目解析
# 句式为：……（以下/如下/下列）……（first_item），（一）……（十）……(item)，……（普通的句式）……(item_ap)
def law_item_parse_j(lines):
    global template
    templates = dict()
    # 按照</p>拆
    result_list = []
    key_list = []
    last_behavior = ''  # 如果behavior，说的是同一个behavior
    key_item = ''
    last_beh = ''  # 必须对其所有的或者所经营的船舶、排筏、设施的安全负责，并且应当 '做到' 下列各项 拿出做到 加到behavior上
    lines = lines.strip().replace('<p>', '').replace('\u3000', '').split('</p>')
    # 非空行
    if lines:
        # first_item是（一）到（十）前面的说明性文字
        first_item = lines[0]
        # 去掉所有的第……条
        first_item = item_title_filter(first_item)

        items = []
        items_ap = []
        if len(lines) > 1:
            # 第0行一般是“有下列情形之一的……”
            for i, word in enumerate(lines[1:]):
                if has_key_one(word) or has_key_one_v2(word) or has_key_one_v4(word):  # 有（一）或 一或 １、
                    items.append(word)
                else:
                    items_ap = lines[(i+1):]
                    break
        # 去掉（一）等
        items = [number_zh_filter_plus(number_zh_filter(remove_special_character(it))) for it in items]
        # 对第一条进行语意角色标注
        # 对应的字典有两个key分别为role 和 seg，role部分是每个词（可能不止一个词，具体几个词由beg和end决定）
        # type代表角色对应类型，id代表这个类型的角色在role里服务的个体
        ltp_result_dict = ltp_tool(first_item, 'srl')
        # ltp_jufa_dict = ltp_parse(first_item, 'parse')
        # 这个用来将“有下列情形之一的”的主客体分开
        first_segs = first_item_filter(first_item)

        if not first_segs:
            return templates
        if ltp_result_dict:
            seg = ltp_result_dict['seg']
            key_id = 0
            if seg:
                for n in seg:
                    if n['word'] in key2 or n['word'] in key:
                        key_id = n['id']
                        key_item = n['word']
                        if key_item in key:  # 找到key2中的关键词
                            key_item = ''
                            continue
                        if key_item in key2:
                            break
            roles = ltp_result_dict['role']
            # key_id之前的部分是subject，之后的都是result
            if roles:
                # 逆序roles
                for role in roles[::-1]:
                    role_type = role['type']
                    beg = role['beg']
                    end = role['end']
                    result = remove_special_character(first_segs[1]).replace(key_item, '')  # 除去result中的key
                    # 实际上是直到找到A0为止，否则会一直循环下去
                    # 优先判断特殊情况
                    if check_sub_v2(first_segs[0]):
                        try:
                            sub = ''
                            condition = remove_special_character((first_segs[0].replace(key_item, '')))
                            if second_item_filter(first_segs[0]):  # 未经自治县交通主管部门批准，在乡道和乡道用地范围内，不得从事下列活动：
                                second_result = second_item_filter(first_segs[0])
                                condition = remove_special_character(second_result[0])
                                last_beh = second_result[1]
                            template = st.SentenceTemplate(subject=sub, condition=condition, result=result, flag=0)
                        except Exception:
                            write_to_file_append(lines, 'model_1_error.txt')
                    elif role_type == 'A0' and end < key_id:
                        sub = ''.join([n['word'] for n in seg[beg:end+1]])
                        if sub in sub_list_2:
                            sub = ''
                        condition = remove_special_character(first_segs[0].replace(sub, ''))
                        if second_item_filter(condition):
                            second_result = second_item_filter(condition)
                            condition = remove_special_character(second_result[0])
                            last_beh = second_result[1]
                        template = st.SentenceTemplate(subject=sub, condition=condition, result=result, flag=0)
                        break
                    elif role_type == 'A1' and end < key_id:
                        segs_ = remove_special_character(first_segs[0])
                        template = st.SentenceTemplate(subject='', condition=segs_, result=result, flag=1)
                        continue
                    else:
                        template = st.SentenceTemplate(subject='', condition='', result=result, flag=1)
                if template:
                    # condition, subject, behavior, result = template.parse_items(items)
                    beh = []
                    for i, tiao in enumerate(items):
                        try:
                            pre_behavior = ''
                            if get_sentence_key(tiao):
                                get_result = get_sentence_key(tiao)
                                key_list.append(''.join(s for s in get_result[0]))
                                behavior = last_beh + remove_last_de(tiao.replace(key_list[i], ''))
                                if filter_key_one_behv(behavior) and template.subject not in sub_list:  # 对于behavior中是result的情况进行了过滤
                                    filter_result = get_result_from_beh(behavior)
                                    if filter_result:
                                        if filter_result[0]:
                                            pre_behavior = remove_last_de(remove_special_character(filter_result[0]))
                                        if not pre_behavior:
                                            pre_behavior = last_behavior
                                        beh.append(pre_behavior)
                                        if filter_result[2]:
                                            result_list.append(filter_result[1]+filter_result[2])
                                        else:
                                            result_list.append(filter_result[1])
                                        last_behavior = pre_behavior
                                else:
                                    beh.append(behavior)
                            else:
                                key_item = '' if key_item == '由' else key_item
                                key_list.append(key_item)
                                behavior = last_beh + remove_last_de(tiao)
                                if filter_key_one_behv(behavior) and filter_key_one_behv_plus(behavior) and template.subject not in sub_list \
                                        and template.condition not in condition_list_2:  # 对于behavior中是result的情况进行了过滤
                                    filter_result = get_result_from_beh(behavior)
                                    if filter_result:
                                        if filter_result[0]:
                                            pre_behavior = remove_last_de(remove_special_character(filter_result[0]))
                                        if not pre_behavior:
                                            pre_behavior = last_behavior
                                        beh.append(pre_behavior)
                                        if filter_result[2]:
                                            result_list.append(filter_result[1]+filter_result[2])
                                        else:
                                            result_list.append(filter_result[1])
                                        last_behavior = pre_behavior
                                else:
                                    beh.append(behavior)
                        except Exception:
                            write_to_file_append(lines, 'model_1_error.txt')
                    if len(template.condition) <= 1 or template.condition in condition_list:
                        template.condition = ''
                    if result_list:
                        templates['condition'], templates['subject'], templates['key'], templates['behavior'], \
                            templates['result'] = \
                            template.condition+template.result, template.subject, key_list, beh, result_list
                    else:
                        templates['condition'], templates['subject'], templates['key'], templates['behavior'], templates['result'] = \
                            template.condition, template.subject, key_list, beh, template.result.replace(template.subject, '')
    return templates


# 法条句式
# *(下列|以下).*
if __name__ == '__main__':
    # print()
    # with open('result.out2', 'w', encoding='UTF-8') as out:
    tmp = '对违反本条例第二十七条规定的，由轨道交通经营单位责令改正，可以处以下罚款：</p>（一）有第一项行为的，按照每处五十元计算罚款</p></p>（二）有第三项至六项行为之一的，处五十元以上一百元以下罚款</p></p>（三）有第七项至十一项行为之一的，处一百元以上二百元以下罚款。</p>'
    print(law_item_parse_j(tmp))


