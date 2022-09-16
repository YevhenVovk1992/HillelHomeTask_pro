import datetime
import os
import uuid

import database
import dotenv

from flask import Flask, request, render_template
from sqlalchemy.sql import func
from os.path import join, dirname


from models import (
    User, Currency, BankAccount, Rating, MoneyTransaction, Deposit, QueueStatus
)
from celery_worker import task_money_transaction


# Loading environment variables into the project
dotenv_path = join(dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()


@app.route('/', methods=['GET'])
def index() -> str:
    """
    Start page display with instruction
    """
    return render_template('index.html', title='Obmenka for you')


@app.get('/currency')
def currency_get() -> list:
    database.init_db()
    all_currency = Currency.query.all()
    if not all_currency:
        return ['No data']
    return [item.to_dict() for item in all_currency]


@app.get('/currency/trade/<cur_name1>/<cur_name2>')
def currency_trade_get(cur_name1: str, cur_name2: str) -> (dict, str):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    database.init_db()
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
    transaction_queue = uuid.uuid4()
    status_queue = QueueStatus(
        uuid_money_transaction=transaction_queue,
        operation_status='Send to the celery'
    )
    try:
        database.db_session.add(status_queue)
        database.db_session.commit()
    except Exception:
        return 'Can not write status_queue to the database'

    task_money_transaction.apply_async(args=(
        cur_name1,
        cur_name2,
        id_user,
        amount_currency_2,
        transaction_queue
    ))
    return request_data['status']


@app.get('/currency/<cur_name>')
def currency_detail_info(cur_name: str) -> (list, str):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    database.init_db()
    currency_info = Currency.query.filter_by(title=cur_name, act_date=current_date).all()
    if len(currency_info) == 0:
        return 'No currency'
    return [item.to_dict() for item in currency_info]


@app.get('/currency/<cur_name>/review')
def currency_review(cur_name: str) -> (list, str):
    database.init_db()
    currency_rating = database.db_session.query(
        Rating.title_currency, Rating.comment).filter(Rating.title_currency == cur_name).all()
    if len(currency_rating) == 0:
        return 'No currency'
    avg_rating = (
        database.db_session.query(func.avg(Rating.rating).label('avg_rate')).filter(Rating.title_currency == cur_name).first()
    )
    res = [dict(i._mapping) for i in currency_rating]
    for i in res:
        i['avg rate'] = round(avg_rating.avg_rate, 2)
    return res


@app.post('/currency/<cur_name>/review')
def currency_review_post(cur_name: str) -> str:
    req = request.json
    review = Rating(
        title_currency=cur_name,
        rating=int(req['data']['rating']),
        comment=req['data']['comment']
    )
    database.init_db()
    try:
        database.db_session.add(review)
        database.db_session.commit()
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
    database.init_db()
    review = Rating.query.filter_by(title_currency=cur_name, id=id).first()
    review.rating = rating
    review.comment = comment
    try:
        database.db_session.add(review)
        database.db_session.commit()
    except Exception:
        return 'Data Base Error'
    else:
        return req['status']


@app.delete('/currency/<cur_name>/review')
def currency_review_delete(cur_name: str) -> str:
    req = request.json
    id_rating = req['data']['id']
    database.init_db()
    review = Rating.query.filter_by(title_currency=cur_name, id=id_rating).first()
    try:
        database.db_session.delete(review)
        database.db_session.commit()
    except Exception:
        return 'Data Base Error'
    else:
        return req['status']


@app.get('/user/<user_name>')
def get_user_info(user_name: str) -> (list, str):
    database.init_db()
    user_info = BankAccount.query.filter_by(login_user=user_name).all()
    if len(user_info) == 0:
        return 'No user'
    return [item.to_dict() for item in user_info]


@app.post('/user/transfer')
def user_transfer():
    return 'User transfer, POST method'


@app.get('/user/<user_name>/history')
def user_history(user_name: str) -> list:
    database.init_db()
    history = MoneyTransaction.query.filter_by(id_user=user_name).all()
    return [item.to_dict() for item in history]


@app.route('/user/<user_name>/deposit', methods=['GET', 'POST'])
def user_deposit(user_name: str) -> (list, str):
    if request.method == 'GET':
        database.init_db()
        user_deposit_info = Deposit.query.filter_by(login_user=user_name).all()
        if len(user_deposit_info) == 0:
            return 'No user deposit'
        return [item.to_dict() for item in user_deposit_info]
    if request.method == 'POST':
        req = request.json
        deposit_of_user = Deposit(
            login_user=user_name,
            balance=req['data']['balance'],
            open_date=req['data']['open_date'],
            close_date=req['data']['close_date'],
            interest_rate=req['data']['interest_rate'],
            conditions=req['data']['conditions']
        )
        database.init_db()
        try:
            database.db_session.delete(deposit_of_user)
            database.db_session.commit()
        except Exception:
            return 'Data Base Error'
        else:
            return req['status']


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
