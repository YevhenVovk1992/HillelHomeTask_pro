import datetime
from flask import Flask, request

from operations.db_operations import get_data, write_data_to_DB, delete_data_from_DB

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
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    exchange_rate = get_data(f"""select (SELECT cost_relative_USD FROM currency
                            WHERE act_date='{current_date}' and title='{cur_name1}')/
                            (SELECT cost_relative_USD FROM currency
                            WHERE act_date='{current_date}' and title='{cur_name2}') AS exchange;""")
    if exchange_rate[0]['exchange'] is None:
        return 'No currency for sale'
    return exchange_rate


@app.post('/currency/trade/<cur_name1>/<cur_name2>')
def currency_trade_post(cur_name1, cur_name2):
    request_data = request.json
    id_user = request_data['data']['id_user']
    amount_currency_2 = request_data['data']['amount_currency_1']
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Get exchange rate currency 1 to currency 2
    exchange_rate_currency1_currency2 = get_data(f"""select (SELECT cost_relative_USD FROM currency
        WHERE act_date='{current_date}' and title='{cur_name1}')/
        (SELECT cost_relative_USD FROM currency
        WHERE act_date='{current_date}' and title='{cur_name2}') AS exchange;""")

    # Get user's bank account of the first currency and the second currency
    user_bank_account1 = get_data(f"select * from bank_account where id_user='{id_user}' and currency='{cur_name1}'")
    user_bank_account2 = get_data(f"select * from bank_account where id_user='{id_user}' and currency='{cur_name2}'")

    # How march currency 1 must be sold to buy currency2
    how_currency_1_need = round(amount_currency_2 / exchange_rate_currency1_currency2[0]['exchange'], 2)

    # Check the availability of currency 2 in the exchanger
    how_currency_2_in_exchange = get_data(f"select * from currency where title='{cur_name2}'")

    """ Make an exchange if: 1) User has bank account with currency 
                             2) User has enough currency 1
                             3) There is enough currency 2 in the exchanger
                             """
    if user_bank_account2 and (user_bank_account1[0]['balance'] > how_currency_1_need) and (
            how_currency_2_in_exchange[0]['amount'] > amount_currency_2):
        write_data_to_DB(f"""UPDATE bank_account SET 
            balance=(SELECT balance FROM bank_account 
            WHERE id_user='{id_user}' and currency='{cur_name1}') - {how_currency_1_need} 
            WHERE id_user='{id_user}' AND currency='{cur_name1}';
            """)
        write_data_to_DB(f"""UPDATE currency SET
            amount=(SELECT amount FROM currency 
            WHERE title='{cur_name1}' and act_date='{current_date}') + {how_currency_1_need} 
            WHERE title='{cur_name1}' and act_date='{current_date}';
            """)
        write_data_to_DB(f"""UPDATE currency SET
            amount=(SELECT amount FROM currency 
            WHERE title='{cur_name2}' and act_date='{current_date}') - {amount_currency_2} 
            WHERE title='{cur_name2}' and act_date='{current_date}';
            """)
        write_data_to_DB(f"""UPDATE bank_account SET
            balance=(SELECT balance FROM bank_account WHERE id_user='{id_user}' and currency='{cur_name2}') + 50 
            WHERE id_user='{id_user}' and currency='{cur_name2}';
            """)

        # Record transaction in the history
        write_data_to_DB(f"""Insert INTO money_transaction(id_user, type_operation, spent_currency, start_currency, 
            end_currency, operation_time, received_currency, commission, from_bank_account, on_which_bank_account) 
            VALUES('{id_user}', 'exchange', {how_currency_1_need}, '{cur_name1}', '{cur_name2}', 
            '{current_date}', {amount_currency_2}, 0, 
            {user_bank_account1[0]['id_bank_account']}, {user_bank_account2[0]['id_bank_account']});
            """)
    else:
        return 'ERROR'
    return request_data['status']


@app.get('/currency/<cur_name>')
def currency_detail_info(cur_name):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    data = get_data(f"""SELECT title, cost_relative_USD, amount, act_date  FROM currency WHERE title='{cur_name}' 
        and act_date='{current_date}'""")
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
    write_data_to_DB(f"""INSERT INTO rating(id_currency, rating, comment) 
                    VALUES('{cur_name}', {rating}, '{comment}')""")
    return req['status']


@app.put('/currency/<cur_name>/review')
def currency_review_put(name):
    return f'Review currency {name}, PUT method'


@app.delete('/currency/<cur_name>/review')
def currency_review_delete(cur_name):
    req = request.json
    id_rating = req['data']['id']
    delete_data_from_DB(f"""DELETE FROM rating WHERE id={id_rating} and id_currency='{cur_name}' """)
    return req['status']


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
