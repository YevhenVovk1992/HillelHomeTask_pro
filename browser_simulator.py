import requests


def menu():
    print("""Add comment to the review table - 1
Delete comment about EURO - 2
Currency trade PLN to USD from user1 account - 3""")


def post_to_currency_review():
    URL = 'http://127.0.0.1:5000/currency/EURO/review'
    HEADERS = {'content-type': 'application/json'}
    data = {'data':
        {
            "comment": "from simulator for EURO",
            "currency_name": "EURO",
            "rating": 10.0
        },
        'status': 'OK'
    }
    req = requests.post(URL, headers=HEADERS, json=data)
    print(req.status_code, req.text)


def delete_to_currency_review():
    URL = 'http://127.0.0.1:5000/currency/EURO/review'
    HEADERS = {'content-type': 'application/json'}
    data = {'data':
        {
            'id': 12
        },
        'status': 'OK'
    }
    req = requests.delete(URL, headers=HEADERS, json=data)
    print(req.status_code, req.text)


def currency_trade_post():
    URL = 'http://127.0.0.1:5000/currency/trade/PLN/USD'
    HEADERS = {'content-type': 'application/json'}
    data = {'data':
        {
            "id_user": "user1",
            "amount_currency_1": 50
        },
        'status': 'OK'
    }
    req = requests.post(URL, headers=HEADERS, json=data)
    print(req.status_code, req.text)


operations = {1: post_to_currency_review, 2: delete_to_currency_review, 3: currency_trade_post}

if __name__ == "__main__":
    menu()
    operations_number = int(input('What do you want to do?\n'))
    operations[operations_number]()
