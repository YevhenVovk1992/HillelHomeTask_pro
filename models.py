from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    login = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "password": self.password
        }


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(50), nullable=False, unique=True)
    cost_relative_USD = db.Column(db.Numeric(10, 2), nullable=False)
    amount = db.Column(db.Numeric(10, 2))
    act_date = db.Column(db.String(30), nullable=False, default=None)

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "cost_relative_USD": self.cost_relative_USD,
            "amount": self.amount,
            "act_date": self.act_date
        }


class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    login_user = db.Column(db.String(50), ForeignKey('user.login'), nullable=False, unique=True)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    currency = db.Column(db.String(50))

    user = relationship('User', backref='BankAccount')

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            "login_user": self.login_user,
            "balance": self.balance,
            "currency": self.currency
        }


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title_currency = db.Column(db.String(50), ForeignKey('currency.title'), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    comment = db.Column(db.String(50))

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            "title_currency": self.title_currency,
            "rating": self.rating,
            "comment": self.comment
        }


class MoneyTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    id_user_1 = db.Column(db.String(50), nullable=False)
    id_user_2 = db.Column(db.String(50), nullable=False, default='No user')
    type_operation = db.Column(db.String(30), nullable=False)
    spent_currency = db.Column(db.Numeric(10, 2))
    start_currency = db.Column(db.String(30))
    end_currency = db.Column(db.String(30))
    operation_time = db.Column(db.String(30), nullable=False)
    received_currency = db.Column(db.Numeric(10, 2))
    commission = db.Column(db.Integer, default=0)
    from_bank_account = db.Column(db.Integer, nullable=False)
    on_which_bank_account = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "type_operation": self.type_operation,
            "spent_currency": self.spent_currency,
            "start_currency": self.start_currency,
            "end_currency": self.end_currency,
            "operation_time": self.operation_time,
            "received_currency": self.received_currency,
            "commission": self.commission,
            "from_bank_account": self.from_bank_account,
            "on_which_bank_account": self.on_which_bank_account
        }


class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    login_user = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    open_date = db.Column(db.String(50), nullable=False)
    close_date = db.Column(db.String(50), default='Not close')
    interest_rate = db.Column(db.Integer, nullable=False)
    conditions = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            "login_user": self.login_user,
            "balance": self.balance,
            "open_date": self.open_date,
            "close_date": self.close_date,
            "interest_rate": self.interest_rate,
            "conditions": self.conditions
        }
