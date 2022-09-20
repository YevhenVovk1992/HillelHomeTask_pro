from sqlalchemy import Column, Integer, String, Numeric, Text
from database import Base

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=False)
    login = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "password": self.password
        }


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(50), nullable=False, unique=False)
    cost_relative_USD = Column(Numeric(10, 2), nullable=False)
    amount = Column(Numeric(10, 2))
    act_date = Column(String(30), nullable=False, default=None)

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


class BankAccount(Base):
    __tablename__ = 'bank_account'

    id = Column(Integer, primary_key=True, nullable=False)
    login_user = Column(String(50), ForeignKey('user.login'), nullable=False, unique=False)
    balance = Column(Numeric(10, 2), nullable=False, default=0)
    currency = Column(String(50))

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


class Rating(Base):
    __tablename__ = 'rating'

    id = Column(Integer, primary_key=True, nullable=False)
    title_currency = Column(String(50), nullable=False)
    rating = Column(Integer, nullable=False, default=0)
    comment = Column(String(50))

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            "title_currency": self.title_currency,
            "rating": self.rating,
            "comment": self.comment
        }


class MoneyTransaction(Base):
    __tablename__ = 'money_transaction'

    id = Column(Integer, primary_key=True, nullable=False)
    uuid_money_transaction = Column(String(), ForeignKey('queue_status.uuid_money_transaction'), nullable=False, unique=True)
    id_user_1 = Column(String(50), nullable=False)
    id_user_2 = Column(String(50), nullable=False, default='No user')
    type_operation = Column(String(30), nullable=False)
    spent_currency = Column(Numeric(10, 2))
    start_currency = Column(String(30))
    end_currency = Column(String(30))
    operation_time = Column(String(30), nullable=False)
    received_currency = Column(Numeric(10, 2))
    commission = Column(Integer, default=0)
    from_bank_account = Column(Integer, nullable=False)
    on_which_bank_account = Column(Integer, nullable=False)

    def __repr__(self):
        return f'{self.to_dict()}'

    def to_dict(self):
        return {
            "id": self.id,
            'uuid_money_transaction': self.uuid_money_transaction,
            "id_user_1": self.id_user_1,
            "id_user_2": self.id_user_2,
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

    queue_status = relationship('QueueStatus', back_populates='MoneyTransaction')


class Deposit(Base):
    __tablename__ = 'deposit'

    id = Column(Integer, primary_key=True, nullable=False)
    login_user = Column(String(50), nullable=False)
    balance = Column(Numeric(10, 2), nullable=False)
    open_date = Column(String(50), nullable=False)
    close_date = Column(String(50), default='Not close')
    interest_rate = Column(Integer, nullable=False)
    conditions = Column(Text, nullable=False)

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


class QueueStatus(Base):
    __tablename__ = 'queue_status'

    id = Column(Integer, primary_key=True, nullable=False)
    uuid_money_transaction = Column(String, nullable=False, unique=True)
    operation_status = Column(String(50), nullable=False)

    MoneyTransaction = relationship('MoneyTransaction', back_populates='queue_status')