import sys
sys.path.append(r'F:\law_git_cll')
import self_log
from flask import Flask, request
from flask_cors import CORS
from regex_select import sentences_to_parts, law_to_sentence
from data_process.data_operate import full_result_1,full_result_2,full_result_3,full_result_4,build_item_spilt
from DB_pool.db_pooling import DBPool
app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/tagging', methods=['GET', 'POST'])
def tagging():
    law_sentence = request.get_json()

    print('items:', law_sentence)

    if law_sentence is None or len(law_sentence) == 0:
        return ""

    data = dict()
    for key, sentence in law_sentence.items():
        result, flag = sentences_to_parts(sentence)
        if result:
            data['data'] = result
            data['flag'] = flag
    return str(data).replace("'", '"')


@app.route('/splitting', methods=['GET', 'POST'])
def splitting():
    law_items = request.get_json()

    print('items:', law_items)

    if law_items is None or len(law_items) == 0:
        return ""

    data = dict()
    for key, item in law_items.items():
        ids, sentences = law_to_sentence(item)
        data['ids'] = ids
        data['sentences'] = sentences
    return str(data).replace("'", '"')


@app.route('/store', methods=['GET', 'POST'])
def store():
    law_items = request.get_json()
    dbOperate = DBPool()
    if law_items is None or len(law_items) == 0:
        return ''
    try:
        law_id = law_items['law_id']
        item_id = law_items['item_id']
        law_item = '<p>' + law_items['item'] + '</p>'
        law_title = law_items['law_title']
        chapter = law_items['chapter']

        ids, sentences = law_to_sentence(law_item)

        for id, sentence in zip(ids, sentences):
            # print(id, sentence)
            build_item_spilt(id, law_id, item_id, sentence, law_title, chapter)
            parse_result, flag = sentences_to_parts(sentence)
            if flag == 1:
                # print([id, parse_result])
                full_result_1([[id, parse_result]])
            elif flag == 2:
                # print([id, parse_result])
                full_result_2([[id, parse_result]])
            elif flag == 3:
                # print([id, parse_result])
                full_result_3([[id, parse_result]])
            elif flag == 4:
                # print([id, parse_result])
                full_result_4([[id, parse_result]])
        print('\n')
    except Exception as e:
        self_log.self_log()
    dbOperate.dispose()
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8484)