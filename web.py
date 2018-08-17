from flask import Flask, request
from flask_cors import CORS
from regex_select import sentences_to_parts, law_to_sentence

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
    return str(data)


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
    return str(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8484, debug=True)