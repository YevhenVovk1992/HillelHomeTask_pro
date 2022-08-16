import json
from flask import Flask, request

from operations.db_operations import get_data, write_data_to_DB


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return 'Hello! It\'s my first API'


@app.get('/currency')
def currency_get():
    data = get_data("SELECT title, avg(cost_relative_USD), amount FROM currency GROUP by title")
    return data


@app.get('/currency/trade/<cur_name1>/<cur_name2>')
def currency_trade_get(cur_name1, cur_name2):
    exchange_rate = get_data(f"""select (SELECT cost_relative_USD FROM currency
                            WHERE act_date='2022-08-12' and title='{cur_name1}')/
                            (SELECT cost_relative_USD FROM currency
                            WHERE act_date='2022-08-12' and title='{cur_name2}') AS exchange;""")
    if exchange_rate[0]['exchange'] is None:
        return 'No currency for sale'
    return exchange_rate



@app.post('/currency/trade/<name1>/<name2>')
def currency_trade_post(name1, name2):
    return f'Currency exchange {name1} to {name2}. Post method'


@app.get('/currency/<cur_name>')
def currency_detail_info(cur_name):
    data = get_data(f"SELECT title, cost_relative_USD, amount, act_date  FROM currency WHERE title='{cur_name}'")
    if not data:
        return 'This currency is not for sale!'
    return data


@app.get('/currency/<cur_name>/review')
def currency_review(cur_name):
    data = get_data(f"""SELECT currency_name, 
                    round((SELECT AVG(rating) FROM rating 
                    GROUP BY currency_name HAVING currency_name='{cur_name}'), 3) AS rating, 
                    comment FROM rating WHERE currency_name='{cur_name}'""")
    if not data:
        return 'Currency is not included in the rating'
    return data


@app.post('/currency/<cur_name>/review')
def currency_review_post(cur_name):
    req = request.json
    rating = req['data']['rating']
    comment = req['data']['comment']
    write_data_to_DB(f"""INSERT INTO rating(currency_name, rating, comment) 
                    VALUES('{cur_name}', {rating}, '{comment}')""")
    return req['status']


@app.put('/currency/<cur_name>/review')
def currency_review_put(name):
    return f'Review currency {name}, PUT method'


@app.delete('/currency/<cur_name>/review')
def currency_review_delete(name):
    return f'Review currency {name}, DELETE method'


@app.get('/user/<user_name>')
def get_user_info(user_name):
    user = get_data(f"""SELECT user.login, bank_account.balance, bank_account.currency
                    FROM user JOIN bank_account WHERE user.login=bank_account.user AND user.login='admin'""")
    if not user:
        return 'This user not registered!'
    return f'Welcome, {user_name}\n{user}'


@app.post('/user/transfer')
def user_transfer():
    return 'User transfer, POST method'


@app.get('/user/<user_name>/history')
def user_history(user_name):
    history = get_data(f"select money_transaction.* FROM money_transaction WHERE user='{user_name}'")
    if not history:
        return 'Transactions not found'
    return history


@app.route('/user/<user_name>/deposit', methods=['GET', 'POST'])
def user_deposit(user_name):
    if request.method == 'GET':
        user_deposit_info = get_data(f'SELECT * FROM deposit WHERE user="{user_name}"')
        return user_deposit_info
    if request.method == 'POST':
        return 'Create user deposit'


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
