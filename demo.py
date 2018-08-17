from function_lib import functions
from function_lib import rule_table


def demo(sentence):
    parse_result = functions.ltp_tool(sentence, 'srl')
    print(parse_result)
    filter_three_res = rule_table.filter_three(sentence)
    print(filter_three_res)


if __name__ == '__main__':

    sentence = '第四十条使用全民所有的水域、滩涂从事养殖生产，无正当理由使水域、滩涂荒芜满一年的，由发放养殖证的机关责令限期开发利用'
    demo(sentence)