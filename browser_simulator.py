import requests


def menu():
    print("""Add comment to the review table - 1
Delete comment about EURO - 2""")


def post_to_currency_review():
    URL = 'http://127.0.0.1:5000/currency/EURO/review'
    data = {'data':
                {
                  "comment": "from simulator for EURO",
                  "currency_name": "EURO",
                  "rating": 10.0
                },
        'status': 'OK'
    }
    req = requests.post(URL, json=data)
    print(req.status_code, req.text)


def delete_to_currency_review():
    pass


operations = {1: post_to_currency_review, 2: delete_to_currency_review}


if __name__ == "__main__":
    menu()
    operations_number = int(input('What do you want to do?\n'))
    operations[operations_number]()