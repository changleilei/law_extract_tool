import re


# 去除句子开始的（一）、（十）
def number_zh_filter(s):
    return re.sub('^\（.*\）| （.*）', '', s)


# 除去句子开始的 一、 二、
def number_zh_filter_plus(s):
    return re.sub('[一二三四五六七八九十]+、', '', s)


# 获取第一种句式中，下列之后句子的关键词
def get_sentence_key(s):
    pattern = re.compile('^(应当)|^(不得)|^(禁止)')
    result = re.findall(pattern, s)
    return result  # [('', '不得', '')]


# 去除句子首位的标点符号
def remove_special_character(s):
    return re.sub('^(、|，|；|。|：)+|(、|，|；|。|：)+$', '', s)


# 去除句子最后一个“的”字
def remove_last_de(s):
    return re.sub('的$', '', s)


def item_title_filter(s):
    item = re.sub('^第.*?条', '',  s)
    return item


# 去除条件中的描述性文字“四、增加一款，作为第二款：”
# “第三款修改为：”
def remove_useless_desc(s):
    return re.sub('.*：', '', s)


def condition_trim(s):
    return re.sub('(，|：).*', '', s)


def remove_dun(s):
    return re.sub('^（[一二三四五六七八九十]+）', '', s)


# 判断的方法应该是看法条里有没有“（一）（二）”
def has_key_one(s):
    has_key_flag = False
    pattern = re.compile('（[一二三四五六七八九十]+）')
    sub_matcher = pattern.findall(s)
    if len(sub_matcher) >= 1:
        has_key_flag = True
    return has_key_flag


def has_key_one_v3(s):
    keys = ['元以下', '倍以下']   # 元以下 和 以下冲突
    has_key_flag = True
    for k in keys:
        if k in s:
            has_key_flag = False
            break
    return has_key_flag


# 判断的方法应该是看法条里有没有“一、二、”
def has_key_one_v2(s):
    has_key_flag = False
    pattern = re.compile('[一二三四五六七八九十]+')
    sub_matcher = pattern.findall(s)
    if len(sub_matcher) >= 1:
        has_key_flag = True
    return has_key_flag


def check_sub_v2(s):
    keys = ['使用港口', '自治县交通主管部门', '申请机动车登记']  # 使用港口岸线禁止下列行为
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def has_key_one_plus(s):
    key1 = ['下列', '以下', '如下']
    has_key_flag = False
    for k in key1:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def has_key_two(s):
    keys = ['当', '应当', '方可', '不得', '禁止', '严禁', '可以']
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def filter_key_two_behv(s):  # 判断behavior中是否有表示后果的关键词
    keys = ['吊销', '拘留', '没收', '罚款', '责令', '扣留']
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def filter_key_one_behv(s):  # 判断behavior中是否有表示后果的关键词
    keys = ['吊销', '拘留', '没收', '责令', '扣留']
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def filter_key_one_behv_plus(s):  # 与上个规则关键字有冲突的
    keys = ['不及时吊销', '违法扣留']
    has_key_flag = True
    for k in keys:
        if k in s:
            has_key_flag = False
            break
    return has_key_flag
def check_end(s):
    keys = ['救险车']
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def has_key_two_plus(s):
    keys = ['维护尺度', '可以并', '由']  # 航道维护尺度是指航道在不同水位期应当保持的水深、宽度、弯曲半径等技术要求。</p> 说明性的法律过滤掉
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def has_key_three(s):
    reg = '(.*?)(由|按照)(.*)'
    return re.match(reg, s)


def filter_three(sentence):
    """
    :param sentence:
    :return:
    """
    reg = '(.*?)(由|按照)(.*)'  # 匹配到第一个停下来
    pattern = re.compile(reg)

    matcher = re.match(pattern, sentence)
    plus_result = filter_three_plus(sentence)
    if plus_result:
        data = []
        matcher_2 = re.match(pattern, plus_result[2])
        if plus_result[1] == '理由' and matcher_2:
            st = ''.join(item for item in plus_result[:2])  # 如果一个句子中同时有‘理由’和‘由’，用st拿到‘由’前面的数据
            st += matcher_2.group(1)
            data.append(st)
            data.append(matcher_2.group(2))
            data.append(matcher_2.group(3))
            return data
    elif matcher:
        data = []
        data.append(matcher.group(1))
        data.append(matcher.group(2))
        data.append(matcher.group(3))
        return data


def filter_three_plus(sentence):
    """
    :param sentence:
    :return:
    """
    data = []
    reg = '(.*?)(由于|理由|缘由|自由|是由|未按照)(.*)'
    matcher = re.match(reg, sentence)
    if matcher:
        data.append(matcher.group(1))
        data.append(matcher.group(2))
        data.append(matcher.group(3))
    return data


def filter_four(sentence):
    data = []
    reg = '(.*?)(责令|没收)(.*)'
    matcher = re.match(reg, sentence)
    if matcher:
        data.append(matcher.group(1))
        data.append(matcher.group(2))
        data.append(matcher.group(3))
    return data


def has_four_plus(sentence):
    keys = ['全民', '报废']
    has_key_flag = False
    for k in keys:
        if k in sentence:
            has_key_flag = True
            break
    return has_key_flag


def check_sub(sentence):  # 检测一个句子中是否含有主语部分关键字
    keys = ['部门', '单位', '机构', '政府', '人', '警察', '机关', '车', '航道', '国家', '拖拉机', '者', '工', '船', '设施', '乘客', '同胞', '驾驶员']
    has_key_flag = False
    for k in keys:
        if k in sentence:
            has_key_flag = True
            break
    return has_key_flag


# 检测垃圾数据，直接过滤掉
def check_sentence(sentence):  #'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp'
    keys = ['&nbsp']
    has_key_flag = False
    for k in keys:
        if k in sentence:
            has_key_flag = True
            break
    return has_key_flag

if __name__=='__main__':
    st = '（三）摩托车非法从事载客业务'
    st = number_zh_filter(st)
    print(st)
