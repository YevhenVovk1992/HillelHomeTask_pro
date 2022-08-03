from flask import Flask
from flask import request


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return 'Hello! It\'s my first API.'


@app.get('/currency')
def currency_get():
    return 'Currency info, get method'


@app.get('/user')
def login_get():
    return 'User info, get method'


@app.get('/currency/trade/<name1>/<name2>')
def currency_trade_get(name1, name2):
    return f'Currency exchange {name1} to {name2}. Get method'


@app.post('/currency/trade/<name1>/<name2>')
def currency_trade_post(name1, name2):
    return f'Currency exchange {name1} to {name2}. Post method'


@app.get('/currency/<name>')
def currency_detail_info(name):
    return f'Currency detail info of {name}, get method'


@app.get('/currency/<name>/review')
def currency_review_get(name):
    return f'Review currency {name}, GET method'


@app.post('/currency/<name>/review')
def currency_review_post(name):
    return f'Review currency {name}, POST method'


@app.put('/currency/<name>/review')
def currency_review_put(name):
    return f'Review currency {name}, PUT method'


@app.delete('/currency/<name>/review')
def currency_review_gelete(name):
    return f'Review currency {name}, DELETE method'


@app.post('/user/transfer')
def user_transfer():
    return 'User transfer, POST method'


@app.get('/user/history')
def user_history():
    return 'User history, GET method'


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)