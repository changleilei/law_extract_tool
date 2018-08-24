from function_lib.functions import *
from function_lib.rule_table import *

keys = ['由', '按照']


def sentences_to_parts_three(sentences):
    templates_list = []
    for sentence in sentences:
        templates = dict()
        line = sentence.strip().replace('<p>', '').replace('\u3000', '').replace('"', "“")
        if line:
            first_item = item_title_filter(line)  # 过滤第.*条

            ltp_result_dict = ltp_tool(first_item, 'srl')
            first_segs = filter_three(first_item)
            if not first_segs:
                return templates
            seg = ltp_result_dict['seg']
            behavior = remove_last_de(remove_special_character(first_segs[2]))
            key = first_segs[1]
            key_id = 0
            if seg:
                for n in seg:
                    if n['word'] == key:
                        key_id = n['id']
                        break
            roles = ltp_result_dict['role']
            if roles:
                for role in roles[::-1]:
                    role_type = role['type']
                    beg = role['beg']
                    end = role['end']
                    if role_type == 'A0':
                        if beg >= key_id:
                            sub = ''.join([n['word'] for n in seg[key_id+1:end+1]])
                        else:
                            sub = ''.join([n['word'] for n in seg[beg:end + 1]])
                        be = behavior.replace(sub, '')
                        condition = remove_last_de(remove_dun(remove_special_character(first_segs[0].replace(sub, ''))))
                        if len(sub) <= 1:
                            sub = ''
                        if filter_key_two_behv(be):  # 对于behavior中是result的情况进行了过滤
                            templates['result'] = be
                            templates['subject'] = sub
                            templates['behavior'] = condition
                            templates['key'] = key
                            templates['condition'] = ''
                        else:
                            templates['condition'], templates['subject'], templates['key'], templates['behavior'], templates['result'] = \
                                condition, sub, key, be, ''
                        break
                    else:
                        condition = remove_last_de(remove_dun(remove_special_character(first_segs[0])))
                        if filter_key_two_behv(behavior):
                            templates['result'] = behavior
                            templates['subject'] = ''
                            templates['behavior'] = condition
                            templates['key'] = key
                            templates['condition'] = ''
                        else:
                            templates['condition'], templates['subject'], templates['key'], templates['behavior'], templates['result'] = \
                                condition, '', key, behavior, ''

            templates_list.append(templates)

    return templates_list


def do():
    lines = read_from_file('not_parse.txt')
    count = lines.__len__()
    print(count)
    num = 0
    for line in lines:
        # contents = line.split('\t')
        # law_id, item_id, title, content = contents[0], contents[1], contents[2], contents[3]
        generated_template = sentences_to_parts_three(line)
        if generated_template:
            num += 1
            print('num:', num)
        # print(generated_template)
        yield line + '\n' + str(generated_template)


# 法条句式
# .*(由|按照).*
if __name__ == '__main__':
    # print(subject_condition_filter('<s>部队</s>执行任务、战备训练需要使用航道的，<s>负责航道管理的部门</s>应当给'))
    # # with open('result.out2', 'w', encoding='UTF-8') as out:
    #     for i, r in enumerate(do()):
    #         print(i, r)
    #         # out.write(r + '\n')
    str_tnp = '两个收费站之间的距离，不得小于国务院交通主管部门规定的标准。</p>'
    templte = sentences_to_parts_three([str_tnp])
    print(templte)
