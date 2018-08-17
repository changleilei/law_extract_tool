from model_1 import sentence_template as st
from function_lib.rule_table import *
from function_lib.functions import *

key1 = ['下列', '以下', '如下']


def law_item_parse(item):
    templates = dict()
    lines = item.strip().replace('<p>', '').replace('\u3000', '').split('</p>')
    if lines:
        first_item = lines[0]
        first_item = item_title_filter(first_item)
        if len(lines) > 1:
            items = lines[1:]
        else:
            items = []
        items = [number_zh_filter(it) for it in items]

        ltp_result_dict = ltp_tool(first_item, 'srl')

        first_segs = first_item_filter(first_item)
        if not first_segs:
            return templates
        seg = ltp_result_dict['seg']
        key_id = 0
        if seg:
            for n in seg:
                if n['word'] in key1:  # 应该为关键字列表
                    key_id = n['id']
                    break
        roles = ltp_result_dict['role']
        if roles:
            for role in roles[::-1]:
                role_type = role['type']
                beg = role['beg']
                end = role['end']
                result = remove_special_character(first_segs[1])
                if role_type == 'A0' and end < key_id:
                    sub = ''.join([n['word'] for n in seg[beg:end+1]])
                    condition = remove_special_character(first_segs[0].replace(sub, ''))
                    template = st.SentenceTemplate(subject=[sub], condition=condition, result=result, flag=0)
                    break
                elif role_type == 'A1' and end < key_id:
                    segs_ = remove_special_character(first_segs[0])
                    template = st.SentenceTemplate(subject=[], condition=segs_, result=result, flag=1)
                    continue

                else:
                    template = st.SentenceTemplate(subject=[], condition='', result=first_segs[1], flag=1)
            if template:
                condition, subject, behavior, result = template.parse_items(items)
                templates['condition'], templates['subject'], templates['behavior'], templates['result'] = \
                    condition, subject, behavior, result
    return templates


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


def do():
    lines = read_from_file('../data_process/four_law.txt')
    for line in lines[:]:
        contents = line.split('\t')
        law_id, item_id, title, content = contents[0], contents[1], contents[2], contents[3]

        generated_template = law_item_parse(content)
        print(item_id, title, content, generated_template)
        yield line + '\n' + str(generated_template)


def do_regex_one(item):
    generated_template = law_item_parse(item)
    print('generated_template_regex_1', generated_template)
    return generated_template


# 法律条目解析
# 句式为：……（以下/如下/下列）……（first_item），（一）……（十）……(item)，……（普通的句式）……(item_ap)
def law_item_parse_j(lines):
    global template
    templates = dict()
    # 按照</p>拆
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
                if has_key_one(word):
                    items.append(word)
                else:
                    items_ap = lines[(i+1):]
                    break
        # 去掉（一）等
        items = [number_zh_filter(remove_special_character(it)) for it in items]
        # 对第一条进行语意角色标注
        # 对应的字典有两个key分别为role 和 seg，role部分是每个词（可能不止一个词，具体几个词由beg和end决定）
        # type代表角色对应类型，id代表这个类型的角色在role里服务的个体
        ltp_result_dict = ltp_tool(first_item, 'srl')
        # ltp_jufa_dict = ltp_parse(first_item, 'parse')
        # 这个用来将“有下列情形之一的”的主客体分开
        first_segs = first_item_filter(first_item)

        if not first_segs:
            return templates
        seg = ltp_result_dict['seg']
        key_id = 0
        if seg:
            for n in seg:
                if n['word'] in key1:
                    key_id = n['id']
                    break
        roles = ltp_result_dict['role']
        # key_id之前的部分是subject，之后的都是result
        if roles:
            # 逆序roles
            for role in roles[::-1]:
                role_type = role['type']
                beg = role['beg']
                end = role['end']
                result = remove_special_character(first_segs[1])
                # 实际上是直到找到A0为止，否则会一直循环下去
                if role_type == 'A0' and end < key_id:
                    sub = ''.join([n['word'] for n in seg[beg:end+1]])
                    condition = remove_special_character(first_segs[0].replace(sub, ''))
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
                for tiao in items:
                    beh.append(tiao)
                if len(template.condition)<=1:
                    template.condition = ''
                templates['condition'], templates['subject'], templates['behavior'], templates['result'] = \
                    template.condition, template.subject, beh, template.result
    return templates


# 法条句式
# *(下列|以下).*
if __name__ == '__main__':
    # print()
    # with open('result.out2', 'w', encoding='UTF-8') as out:
        for i, r in enumerate(do()):
            print(i, end='\n')
            # out.write(r + '\n')

