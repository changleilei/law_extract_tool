from function_lib.rule_table import *
from function_lib.functions import *


class SentenceTemplate:
    def __init__(self, subject=[], condition='', result='', flag=0):
        self.subject = subject
        self.condition = condition
        self.result = result
        self.behavior = []
        self.flag = flag

    def template_one(self, items):
        self.behavior.extend([remove_last_de(remove_special_character(s)) for s in items])

    def template_two(self, items):
        for line in items:

            if len(line.strip()) == 0:
                continue
            ltp_parse = ltp_tool(line, 'parse')
            # print('ltp_result', ltp_parse)

            ltp_srl = ltp_tool(line, 'srl')
            # print('ltp_srl', ltp_srl['role'])
            for i, r in enumerate(ltp_parse):
                if r['relate'] == 'SBV':
                    if ltp_parse[i+1]['relate'] == 'SBV':
                        continue
                    sub = ''.join([d['word'] for d in ltp_parse[:r['id']+1]])
                    sub_id = [d['id'] for d in ltp_parse[:r['id']+1]]
                    for n in ltp_srl['role']:
                        if (sub_id[0] >= n['beg'] and sub_id[-1] <= n['end'] or sub_id[0] <= n['beg'] and sub_id[-1] >= n['end']) and n['type'] == 'A0':
                            break
                    else:
                        sub = ''
                    self.subject.append(sub.strip())
                    behavior = line.replace(sub, '').strip()
                    b1 = remove_special_character(behavior)
                    b2 = remove_last_de(b1)
                    self.behavior.append(b2)
                    break
            else:
                b3 = remove_special_character(line.strip())
                b4 = remove_last_de(b3)
                self.behavior.append(b4)

    def parse_items(self, items):
        if self.flag == 0:
            self.template_one(items)
        elif self.flag == 1:
            self.template_two(items)
        return self.condition, self.subject, self.behavior, self.result




