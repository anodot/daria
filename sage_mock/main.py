from datetime import datetime
from flask import Flask, request, make_response, jsonify

app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def parse_date_string(date_string):
    return datetime.strptime(date_string, DATE_FORMAT)


@app.route('/api/search', methods=['POST'])
def search():
    token = request.headers.get('Authorization')
    if token != 'Bearer correct_token':
        return make_response(jsonify({'status': 'fail'}), 401)

    data = [
        {"ver": 1, "Country": "USA", "AdType": "Display",
         "Exchange": "DoubleClick", "Clicks": 6784.6904, "@timestamp": "2017-12-10T01:00:00Z"},
        {"ver": 1, "Country": "USA", "AdType": "Display",
         "Exchange": "DoubleClick", "Clicks": 6839, "@timestamp": "2017-12-10T02:00:00Z"},
        {"ver": 1, "Country": "USA", "AdType": "Search",
         "Exchange": "DoubleClick", "Clicks": 6909993404034934004,
         "@timestamp": "2017-12-10T03:00:00Z"},
        {"ver": 1, "Country": "USA", "AdType": "Display",
         "Exchange": "DoubleClick", "Clicks": 7158.972598273843,
         "@timestamp": "2017-12-10T04:00:00Z"},
        {"ver": 1, "Country": "USA", "AdType": "Search",
         "Exchange": "DoubleClick", "Clicks": 7235.7574, "@timestamp": "2017-12-10T05:00:00Z"},
        {"ver": 1, "Country": "USA", "AdType": "Display",
         "Exchange": "DoubleClick", "Clicks": "", "@timestamp": "2017-12-10T06:00:00Z"},
        {"ver": 1, "Country": "", "AdType": "Display",
         "Exchange": "DoubleClick", "Clicks": 7427.7744, "@timestamp": "2017-12-10T07:00:00Z"}
    ]
    response = []
    time_start = parse_date_string(request.json.get('startTime'))
    time_end = parse_date_string(request.json.get('endTime'))
    for item in data:
        date = parse_date_string(item['@timestamp'])
        if date < time_start or date > time_end:
            break
        response.append(item)

    return jsonify({"hits": response})


if __name__ == '__main__':
    app.run()
