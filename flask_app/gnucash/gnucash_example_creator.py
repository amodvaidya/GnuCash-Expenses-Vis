from piecash import Account, create_book, Transaction, Split
import pandas as pd
import random
from decimal import Decimal
import os


class GnucashExampleCreator(object):

    def __init__(self, file_path, currency, low_proba_value=0.05, medium_proba_value=0.3, high_proba_value=0.6,
                 shop_proba_value=0.4, date_range=pd.date_range("01-Jan-2019", "31-Dec-2019"), seed=1010):

        self.file_path = file_path
        self.currency = currency
        self.low_proba = low_proba_value
        self.medium_proba = medium_proba_value
        self.high_proba = high_proba_value
        self.shop_proba = shop_proba_value
        self.date_range = date_range

        random.seed(seed)

    def create_example_book(self):

        book = create_book(currency=self.currency, sqlite_file=self.file_path, overwrite=True)
        curr = book.default_currency

        asset_acc = Account("Assets", "ASSET", curr, parent=book.root_account, placeholder=True)
        john_acc = Account("John", "ASSET", curr, parent=asset_acc)
        susan_acc = Account("Susan", "ASSET", curr, parent=asset_acc)
        family_acc = Account("Family", "ASSET", curr, parent=asset_acc)

        income = Account("Income", "INCOME", curr, parent=book.root_account, placeholder=True)
        john_income = Account("John's Income", "INCOME", curr, parent=income)
        susan_income = Account("Susan's Income", "INCOME", curr, parent=income)

        exp = Account("Expenses", "EXPENSE", curr, parent=book.root_account, placeholder=True)
        john_exp = Account("John's Expenses", "EXPENSE", curr, parent=exp, placeholder=True)
        clothes_john = Account("Clothes", "EXPENSE", curr, parent=john_exp)
        susan_exp = Account("Susan's Expenses", "EXPENSE", curr, parent=exp, placeholder=True)
        clothes_susan = Account("Clothes", "EXPENSE", curr, parent=susan_exp)
        family_exp = Account("Family", "EXPENSE", curr, parent=exp, placeholder=True)
        grocery = Account("Grocery", "EXPENSE", curr, parent=family_exp, placeholder=True)
        bread = Account("Bread", "EXPENSE", curr, parent=grocery)
        meat = Account("Meat", "EXPENSE", curr, parent=grocery)
        eggs = Account("Eggs", "EXPENSE", curr, parent=grocery)
        chips = Account("Chips", "EXPENSE", curr, parent=grocery)
        fruits = Account("Fruits and Vegetables", "EXPENSE", curr, parent=grocery)
        car = Account("Car", "EXPENSE", curr, parent=family_exp, placeholder=True)
        petrol = Account("Petrol", "EXPENSE", curr, parent=car)
        flat = Account("Flat", "EXPENSE", curr, parent=family_exp, placeholder=True)
        rent = Account("Rent", "EXPENSE", curr, parent=flat)
        water = Account("Water and Electricity", "EXPENSE", curr, parent=flat)
        bathroom = Account("Bathroom", "EXPENSE", curr, parent=family_exp, placeholder=True)
        toilet = Account("Toilet", "EXPENSE", curr, parent=bathroom)
        personal_john = Account("Personal - John", "EXPENSE", curr, parent=bathroom)
        personal_susan = Account("Personal - Susan", "EXPENSE", curr, parent=bathroom)
        other = Account("Other", "EXPENSE", curr, parent=family_exp)

        book.save()

        stuff = {
            john_acc: {("Salary", john_income): (3000,)},
            susan_acc: {("Salary", susan_income): (3000,)},
            family_acc: {("Transaction", john_acc): (500,),
                         ("Transaction", susan_acc): (500,)},
            clothes_john: {("Clothes", john_acc): (100, 350)},
            clothes_susan: {("Clothes", susan_acc): (100, 350)},
            bread: {("White Bread", family_acc): (1, 4),
                    ("Rye Bread", family_acc): (3, 6),
                    ("Butter", family_acc): (4, 7)},
            meat: {("Chicken", family_acc): (9, 16),
                   ("Cow", family_acc): (15, 30)},
            eggs: {("Eggs", family_acc): (8, 16)},
            chips: {("Chips", family_acc): (5, 17),
                    ("Lollipops", family_acc): (1, 2)},
            fruits: {("Apple", family_acc): (3, 5),
                     ("Banana", family_acc): (5, 7),
                     ("Tomato", family_acc): (2, 4),
                     ("Pear", family_acc): (3, 5)},
            petrol: {("Petrol", family_acc): (50, 250)},
            rent: {("Rent", family_acc): (2000,)},
            water: {("Water and Electricity", family_acc): (20, 150)},
            toilet: {("Toilet Paper", family_acc): (5, 15),
                     ("Facial Tissues", family_acc): (2, 8)},
            personal_john: {("Beard Balm", john_acc): (15, 50)},
            personal_susan: {("Shampoo", susan_acc): (10, 15),
                             ("Face Cleanser", susan_acc): (10, 13)},
            other: {("Other", family_acc): (1, 100)}
        }

        low_proba_list = [clothes_john, clothes_susan, petrol, toilet, personal_john, personal_susan]
        medium_proba_list = [meat, chips, other]
        high_proba_list = [bread, eggs, fruits]

        probas = [
            (low_proba_list, self.low_proba),
            (medium_proba_list, self.medium_proba),
            (high_proba_list, self.high_proba)
        ]

        fixed_transactions = [
            (20, (rent, water)),
            (25, (john_acc, susan_acc)),
            (26, (family_acc,))
        ]

        shops = ["Grocery Shop #1", "Grocery Shop #2"]
        shop_items = (high_proba_list,)

        self.__create_transactions(book, self.date_range, stuff, curr, probas, fixed_transactions, shops, shop_items)
        book.save()

    def __create_transactions(self, book, date_range, stuff, currency, probas, fixed_transactions, shops, shop_items):

        for date_item in date_range:

            date = date_item.date()

            for fixed in fixed_transactions:
                fixed_tr_date = fixed[0]
                fixed_accounts = fixed[1]

                if fixed_tr_date == date.day:
                    for fixed_to_account in fixed_accounts:
                        fixed_transaction_list = self.__extract_data(stuff, fixed_to_account)
                        for fixed_transaction in fixed_transaction_list:
                            self.__add_transaction(book, date, currency, fixed_to_account, fixed_transaction)

            for _ in probas:

                to_account_list = _[0]
                proba = _[1]

                if to_account_list in shop_items and random.random() <= self.shop_proba:
                    shop_description = random.choice(shops)
                    list_of_splits = []
                    for to_account in to_account_list:
                        transaction_list = self.__extract_data(stuff, to_account)
                        for transaction in transaction_list:
                            if random.random() <= proba:
                                list_of_splits.append((to_account, transaction))

                    if len(list_of_splits) > 0:
                        self.__add_shop_transaction(book, date, currency, list_of_splits, shop_description)
                else:
                    for to_account in to_account_list:
                        transaction_list = self.__extract_data(stuff, to_account)
                        for transaction in transaction_list:
                            if random.random() <= proba:
                                self.__add_transaction(book, date, currency, to_account, transaction)

    def __extract_data(self, d, acc):

        internal_dict = d[acc].items()

        if len(internal_dict) > 1:
            ret_list = []
            for tpl in list(internal_dict):
                desc, second_acc = tpl[0]
                price_range = tpl[1]
                ret_list.append((desc, second_acc, price_range))
            ret_tuple = tuple(ret_list)

        else:
            _ = list(internal_dict)[0]
            desc, second_acc = _[0]
            price_range = _[1]
            ret_tuple = ((desc, second_acc, price_range),)

        return ret_tuple

    def __add_transaction(self, book, date, currency, to_account, transaction):

        description, from_account, price_range = transaction

        if len(price_range) > 1:
            value = random.uniform(price_range[0], price_range[1])
        else:
            value = price_range[0]

        price = Decimal(str(round(value, 2)))
        tr = Transaction(currency=currency,
                         description=description,
                         post_date=date,
                         splits=[
                             Split(account=from_account, value=-price),
                             Split(account=to_account, value=price)
                         ])

        book.flush()

    def __add_shop_transaction(self, book, date, currency, list_of_splits, shop_name):

        sp_list = []

        for split in list_of_splits:
            to_account = split[0]
            description, from_account, price_range = split[1]

            if len(price_range) > 1:
                value = random.uniform(price_range[0], price_range[1])
            else:
                value = price_range[0]
            price = Decimal(str(round(value, 2)))

            sp_list.append(Split(account=to_account, memo=description, value=price))
            sp_list.append(Split(account=from_account, value=-price))

        tr = Transaction(currency=currency,
                         description=shop_name,
                         post_date=date,
                         splits=sp_list
                         )

        book.flush()


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "gnucash_examples", "example_gnucash.gnucash")
    currency = "PLN"
    example_creator = GnucashExampleCreator(file_path, currency)
    example_creator.create_example_book()
