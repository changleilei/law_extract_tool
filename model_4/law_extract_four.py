from function_lib.functions import *
from function_lib.rule_table import *

keys = ['责令', '没收']


def sentences_to_parts_four(sentences):
    templates_list = []
    for sentence in sentences:
        templates = dict()
        line = sentence.strip().replace('<p>', '').replace('\u3000', '')
        if line:
            first_item = item_title_filter(line)  # 过滤第.*条

            ltp_result_dict = ltp_tool(first_item, 'srl')
            first_segs = filter_four(first_item)
            if not first_segs:
                return templates
            seg = ltp_result_dict['seg']
            result = first_segs[2]
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
                        res = result.replace(sub, '')
                        if has_four_plus(first_segs[0]):  # 包含全民即A0标签但又不是主语的
                            behavior = remove_last_de(remove_dun(remove_special_character(first_segs[0])))
                            sub = ''
                        else:
                            behavior = remove_last_de(remove_dun(remove_special_character(first_segs[0].replace(sub, ''))))
                        if sub == '的':
                            sub = ''
                        templates['condition'], templates['subject'], templates['key'], templates['behavior'], templates['result'] = \
                            '', sub, '', behavior, key+res
                        break
                    else:
                        behavior = remove_last_de(remove_dun(remove_special_character(first_segs[0])))
                        templates['condition'], templates['subject'], templates['key'], templates['behavior'], templates['result'] = \
                            '', '', '', behavior, key+result

            templates_list.append(templates)
    return templates_list


if __name__ == '__main__':
    sentence = ['未依法取得养殖证或者超越养殖证许可范围在全民所有的水域从事养殖阿生产，妨碍航运、行洪的，责令限期拆除养殖设施，可以并处一万元以下的罚款。']

    # sentence = '第四十三条涂改、买卖、出租或者以其他形式转让捕捞许可证的，没收违法所得，吊销捕捞许可证，可以并处一万元以下的罚款</p>伪造、变造、买卖捕捞许可证，构成犯罪的，依法追究刑事责任。'
    result = sentences_to_parts_four(sentence)
    print(result)
