import datetime
from flask import Flask, request, render_template
from flask_migrate import Migrate

from models import db
from models import (
    User, Currency, BankAccount, Rating, MoneyTransaction, Deposit
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bd_excharngers.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/', methods=['GET'])
def index() -> str:
    return render_template('index.html')


@app.get('/currency')
def currency_get() -> list:
    all_currency = Currency.query.all()
    return [item.to_dict() for item in all_currency]


@app.get('/currency/trade/<cur_name1>/<cur_name2>')
def currency_trade_get(cur_name1: str, cur_name2: str) -> (dict, str):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    currency_for_sale = Currency.query.filter_by(title=cur_name1, act_date=current_date).first()
    purchased_currency = Currency.query.filter_by(title=cur_name2, act_date=current_date).first()
    if currency_for_sale is None or purchased_currency is None:
        return 'Error! No currency for trade.'
    return {
        'exchange': f'{currency_for_sale.cost_relative_USD / purchased_currency.cost_relative_USD}',
        'status': 'OK'
    }


@app.post('/currency/trade/<cur_name1>/<cur_name2>')
def currency_trade_post(cur_name1: str, cur_name2: str) -> str:
    request_data = request.json
    id_user = request_data['data']['id_user']
    amount_currency_2 = request_data['data']['amount_currency_1']
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Get exchange rate currency 1 to currency 2
    exchange_rate_currency1_currency2 = currency_trade_get(cur_name1, cur_name2)['exchange']

    # Get user's bank account of the first currency and the second currency
    user_bank_account1 = BankAccount.query.filter_by(id_user=id_user, currency=cur_name1).first()
    user_bank_account2 = BankAccount.query.filter_by(id_user=id_user, currency=cur_name2).first()
    if user_bank_account1 is None or user_bank_account2 is None:
        return 'User has not bank account'

    # How march currency 1 must be sold to buy currency2
    how_currency_1_need = round(amount_currency_2 / float(exchange_rate_currency1_currency2), 2)

    # Check the availability of currency 2 in the exchanger
    how_currency_1_in_exchange = Currency.query.filter_by(title=cur_name1, act_date=current_date).first()
    how_currency_2_in_exchange = Currency.query.filter_by(title=cur_name2, act_date=current_date).first()

    """ Make an exchange if: 1) User has bank account with currency 
                             2) User has enough currency 1
                             3) There is enough currency 2 in the exchanger
                             """
    if float(user_bank_account1.balance) > how_currency_1_need and (
            float(how_currency_2_in_exchange.amount) > amount_currency_2
    ):
        user_bank_account1.balance = float(user_bank_account1.balance) - how_currency_1_need
        how_currency_1_in_exchange.amount = float(how_currency_1_in_exchange.amount) + how_currency_1_need
        how_currency_2_in_exchange.amount = float(how_currency_2_in_exchange.amount) - amount_currency_2
        user_bank_account2.balance = float(user_bank_account2.balance) + amount_currency_2

        # Open the session and change date
        try:
            db.session.add(user_bank_account1)
            db.session.add(how_currency_1_in_exchange)
            db.session.add(how_currency_2_in_exchange)
            db.session.add(user_bank_account2)
            db.session.commit()
        except Exception:
            return 'Data Base Error'

        # Record transaction in the history
        money_operation = MoneyTransaction(
            id_user=id_user,
            type_operation='exchange',
            spent_currency=how_currency_1_need,
            start_currency=cur_name1,
            end_currency=cur_name2,
            operation_time=current_date,
            received_currency=amount_currency_2,
            from_bank_account=user_bank_account1.id_bank_account,
            on_which_bank_account=user_bank_account2.id_bank_account
        )
        try:
            db.session.add(money_operation)
            db.session.commit()
        except Exception:
            return 'Data Base Error'

    else:
        return 'Error'
    return request_data['status']


@app.get('/currency/<cur_name>')
def currency_detail_info(cur_name: str) -> (list, str):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    currency_info = Currency.query.filter_by(title=cur_name, act_date=current_date).all()
    if len(currency_info) == 0:
        return 'No currency'
    return [item.to_dict() for item in currency_info]


@app.get('/currency/<cur_name>/review')
def currency_review(cur_name: str) -> (list, str):
    currency_rating = db.session.query(
        Rating.id_currency, Rating.comment).filter(Rating.id_currency == cur_name).all()
    if len(currency_rating) == 0:
        return 'No currency'
    avg_rating = (
        db.session.query(db.func.avg(Rating.rating).label('avg_rate')).filter(Rating.id_currency == cur_name).first()
    )
    res = [dict(i._mapping) for i in currency_rating]
    for i in res:
        i['avg rate'] = round(avg_rating.avg_rate, 2)
    return res


@app.post('/currency/<cur_name>/review')
def currency_review_post(cur_name: str) -> str:
    req = request.json
    review = Rating(
        id_currency=cur_name,
        rating=int(req['data']['rating']),
        comment=req['data']['comment']
    )
    try:
        db.session.add(review)
        db.session.commit()
    except Exception:
        return 'Data Base Error'
    else:
        return req['status']


@app.put('/currency/<cur_name>/review')
def currency_review_put(cur_name) -> (list, str):
    req = request.json
    rating = int(req['data']['rating'])
    comment = req['data']['comment']
    id = int(req['data']['id'])
    review = Rating.query.filter_by(id_currency=cur_name, id=id).first()
    review.rating = rating
    review.comment = comment
    try:
        db.session.add(review)
        db.session.commit()
    except Exception:
        return 'Data Base Error'
    else:
        return req['status']


@app.delete('/currency/<cur_name>/review')
def currency_review_delete(cur_name: str) -> str:
    req = request.json
    id_rating = req['data']['id']
    review = Rating.query.filter_by(id_currency=cur_name, id=id_rating).first()
    try:
        db.session.delete(review)
        db.session.commit()
    except Exception:
        return 'Data Base Error'
    else:
        return req['status']


@app.get('/user/<user_name>')
def get_user_info(user_name: str) -> (list, str):
    user_info = BankAccount.query.filter_by(id_user=user_name).all()
    if len(user_info) == 0:
        return 'No user'
    return [item.to_dict() for item in user_info]


@app.post('/user/transfer')
def user_transfer():
    return 'User transfer, POST method'


@app.get('/user/<user_name>/history')
def user_history(user_name: str) -> list:
    history = MoneyTransaction.query.filter_by(id_user=user_name).all()
    return [item.to_dict() for item in history]


@app.route('/user/<user_name>/deposit', methods=['GET', 'POST'])
def user_deposit(user_name: str) -> (list, str):
    if request.method == 'GET':
        user_deposit_info = Deposit.query.filter_by(id_user=user_name).all()
        if len(user_deposit_info) == 0:
            return 'No user deposit'
        return [item.to_dict() for item in user_deposit_info]
    if request.method == 'POST':
        req = request.json
        deposit_of_user = Deposit(
            id_user=user_name,
            balance=req['data']['balance'],
            open_date=req['data']['open_date'],
            close_date=req['data']['close_date'],
            interest_rate=req['data']['interest_rate'],
            conditions=req['data']['conditions']
        )
        try:
            db.session.delete(deposit_of_user)
            db.session.commit()
        except Exception:
            return 'Data Base Error'
        else:
            return req['status']


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
