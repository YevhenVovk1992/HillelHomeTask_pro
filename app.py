import datetime
import os
import uuid
from typing import Union, List, Any

from werkzeug import Response

import database
import dotenv

from flask import Flask, request, render_template, redirect, session, url_for
from flask_session import Session
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
app.secret_key = os.environ.get('SESSION_SECRET')


# This function closes the connection to the database after the view function is executed
@app.teardown_appcontext
def shutdown_session(exception=None) -> None:
    database.db_session.remove()


@app.route('/', methods=['GET', 'POST'])
def index() -> Union[str, Response]:
    if request.method == "GET":
        return render_template('index.html', title='Obmenka for you')
    if request.method == "POST":
        user_login = request.form['contact_name']
        user_password = request.form['password']
        database.init_db()
        get_user_from_db = User.query.filter_by(login=user_login, password=user_password).all()
        if get_user_from_db:
            session['user_name'] = user_login
            session['user_id'] = str(get_user_from_db[0].id)
            return redirect(url_for('index', _anchor='intro'))
        else:
            error_message = 'User not registered!'
            detail_message = 'The user has not been authorized because he is not registered in our database'
            return render_template(
                'error_message.html',
                title='No user',
                message=error_message,
                detail_message=detail_message
            )


@app.get('/currency')
def currency_get() -> dict:
    database.init_db()
    all_currency = Currency.query.all()
    if not all_currency:
        return {
            'data':  'No data',
            'status': 'OK'
        }
    return {
        'data':  [item.to_dict() for item in all_currency],
        'status': 'OK'
    }


@app.get('/currency/trade/<cur_name1>/<cur_name2>')
def currency_trade_get(cur_name1: str, cur_name2: str) -> dict:
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    database.init_db()
    currency_for_sale = Currency.query.filter_by(title=cur_name1, act_date=current_date).first()
    purchased_currency = Currency.query.filter_by(title=cur_name2, act_date=current_date).first()
    if currency_for_sale is None or purchased_currency is None:
        return {
            'exchange': 'No money for trade',
            'status': 'OK'
        }
    return {
        'exchange': f'{currency_for_sale.cost_relative_USD / purchased_currency.cost_relative_USD}',
        'status': 'OK'
    }


@app.post('/currency/trade/<cur_name1>/<cur_name2>')
def currency_trade_post(cur_name1: str, cur_name2: str) -> Union[Response, str]:
    request_data = request.json
    login_user = request_data['data']['id_user']
    amount_currency_2 = request_data['data']['amount_currency_1']
    if login_user != session['user_name']:
        return redirect(url_for('index', _anchor='login'))
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
        login_user,
        amount_currency_2,
        transaction_queue
    ))
    return request_data['status']


@app.get('/currency/<cur_name>')
def currency_detail_info(cur_name: str) -> dict:
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    database.init_db()
    currency_info = Currency.query.filter_by(title=cur_name, act_date=current_date).all()
    if len(currency_info) == 0:
        return {
            'data': 'No such currency',
            'status': 'OK'
        }
    return {
        'data': [item.to_dict() for item in currency_info],
        'status': 'OK'
    }


@app.get('/currency/<cur_name>/review')
def currency_review(cur_name: str) -> dict:
    database.init_db()
    currency_rating = database.db_session.query(
        Rating.title_currency, Rating.comment).filter(Rating.title_currency == cur_name).all()
    if len(currency_rating) == 0:
        return {
            'data': 'No such currency',
            'status': 'OK'
        }
    avg_rating = (
        database.db_session.query(func.avg(Rating.rating).label('avg_rate')).filter(
            Rating.title_currency == cur_name).first()
    )
    res = [dict(i._mapping) for i in currency_rating]
    for i in res:
        i['avg rate'] = round(avg_rating.avg_rate, 2)
    return {
        'data': res,
        'status': 'OK'
    }


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
def currency_review_put(cur_name) -> str:
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
def get_user_info(user_name: str) -> Union[dict, Response]:
    if user_name != session['user_name']:
        return redirect(url_for('index', _anchor='login'))
    database.init_db()
    user_info = BankAccount.query.filter_by(login_user=user_name).all()
    if len(user_info) == 0:
        return {
            'data': 'No bank account',
            'status': 'OK'
        }
    return {
        'data': [item.to_dict() for item in user_info],
        'status': 'OK'
    }


@app.get('/user/<user_name>/history')
def user_history(user_name: str) -> Union[dict, Response]:
    if user_name != session['user_name']:
        return redirect(url_for('index', _anchor='login'))
    database.init_db()
    history = MoneyTransaction.query.filter_by(id_user_1=user_name).all()
    return {
        'data': [item.to_dict() for item in history],
        'status': 'OK'
    }



@app.route('/user/<user_name>/deposit', methods=['GET', 'POST'])
def user_deposit(user_name: str) -> Union[dict, str, Response]:
    if user_name != session['user_name']:
        return redirect(url_for('index', _anchor='login'))
    if request.method == 'GET':
        database.init_db()
        user_deposit_info = Deposit.query.filter_by(login_user=user_name).all()
        if len(user_deposit_info) == 0:
            return {
                'data': 'No user deposit',
                'status': 'OK'
            }
        return {
            'data': [item.to_dict() for item in user_deposit_info],
            'status': 'OK'
        }
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
