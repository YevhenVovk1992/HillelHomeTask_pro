import datetime

from celery import Celery

import database
from models import (
    Currency, BankAccount, MoneyTransaction, QueueStatus
)

app = Celery('celery_worker', broker='pyamqp://guest@localhost//')


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


@app.task
def task_money_transaction(cur_name1,
                           cur_name2,
                           id_user,
                           amount_currency_2,
                           transaction_queue):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    database.init_db()

    # Get exchange rate currency 1 to currency 2
    exchange_rate_currency1_currency2 = currency_trade_get(cur_name1, cur_name2)['exchange']

    # Get user's bank account of the first currency and the second currency
    user_bank_account1 = BankAccount.query.filter_by(login_user=id_user, currency=cur_name1).first()
    user_bank_account2 = BankAccount.query.filter_by(login_user=id_user, currency=cur_name2).first()
    if user_bank_account1 is None or user_bank_account2 is None:
        return 'User has not bank account'

    # How march currency 1 must be sold to buy currency2
    how_currency_1_need = round(amount_currency_2 / float(exchange_rate_currency1_currency2), 2)

    # Check the availability of currency 2 in the exchanger
    how_currency_1_in_exchange = Currency.query.filter_by(title=cur_name1, act_date=current_date).first()
    how_currency_2_in_exchange = Currency.query.filter_by(title=cur_name2, act_date=current_date).first()

    # Take information about the status of the transaction from the table 'QueueStatus'
    status_queue = QueueStatus.query.filter_by(uuid_money_transaction=transaction_queue).first()

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
            database.db_session.add(user_bank_account1)
            database.db_session.add(how_currency_1_in_exchange)
            database.db_session.add(how_currency_2_in_exchange)
            database.db_session.add(user_bank_account2)
            database.db_session.commit()
        except Exception:
            return 'Data Base Error Stop Transaction'

        # Record transaction in the history
        money_operation = MoneyTransaction(
            uuid_money_transaction=transaction_queue,
            id_user_1=id_user,
            id_user_2=id_user,
            type_operation='exchange',
            spent_currency=how_currency_1_need,
            start_currency=cur_name1,
            end_currency=cur_name2,
            operation_time=current_date,
            received_currency=amount_currency_2,
            from_bank_account=user_bank_account1.id,
            on_which_bank_account=user_bank_account2.id
        )
        try:
            status_queue.operation_status = 'Done'
            database.db_session.add(money_operation)
            database.db_session.add(status_queue)
            database.db_session.commit()
        except Exception:
            return 'Data Base Error Transaction History'
    else:
        status_queue.operation_status = 'Error! No money'
        database.db_session.add(status_queue)
        database.db_session.commit()
        return 'Stop transaction! No money!'
    return 'Successful'
