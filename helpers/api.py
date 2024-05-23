import calendar
from datetime import date
from functools import lru_cache
from typing import List, Union
import requests as rq

from models.customers import Customer
from models.payments import Payment
from models.sales import Product, Sale
from models.stocks import Stock

base_url = "http://commercial.duzzsystem.com.br:8080"


@lru_cache
def get_token(username: str, password: str, company: str):
    user_data = rq.get(
        base_url + "/auth/user",
        params={"username": username, "password": password, "company": company},
    )
    user_data.raise_for_status()
    user_data = user_data.json()

    return user_data["sessionToken"]


@lru_cache
def get_headers(company: str, session_token: str):
    return {"company": company, "sessionToken": session_token}


def get_stocks(headers: dict) -> List[Stock]:
    parameters = {"withMoves": True}

    stocks_list = rq.get(
        base_url + "/stock",
        params=parameters,
        headers=headers,
    )

    if stocks_list.status_code == 404:
        stocks_list = []
    else:
        stocks_list.raise_for_status()
        stocks_list = stocks_list.json()

    for stock in stocks_list:
        stock["startDate"] = Stock.parse_date(stock["startDate"])
        stock["dueDate"] = Stock.parse_date(stock["dueDate"])
        stock["cogs"] = stock["cmv"]

    return [Stock(**stock) for stock in stocks_list]


def get_stock_by_month(month: date, headers: dict) -> List[Union[Stock,]]:
    filtered_stocks = []
    for stock in get_stocks(headers):
        if (
            stock.due_date
            and (
                stock.start_date.date() >= month
                or stock.due_date.date()
                <= month.replace(day=calendar.monthrange(month.year, month.month)[-1])
            )
        ) or not stock.due_date:
            filtered_stocks.append(stock)

    return filtered_stocks


def get_product_data(headers, product_id: int) -> Product:
    parameters = {"id": product_id}
    response = rq.get(base_url + "/products", params=parameters, headers=headers)
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    product_data = response.json()[0]
    product_data = Product(
        id=product_data["id"],
        size=product_data["particulars"]["tamanho"],
        price=product_data["value"],
    )

    return product_data


@lru_cache
def get_customer_data(customer_id: int, headers: tuple) -> Customer:
    headers = dict(headers)
    parameters = {"id": customer_id}
    response = rq.get(base_url + "/customers", params=parameters, headers=headers)
    if response.status_code == 404:
        return []

    response.raise_for_status()
    customer_data = response.json()[0]

    return Customer(**customer_data)


# @lru_cache
def get_sales(month: date, headers: dict) -> List[Sale]:
    parameters = {
        "startRange": month.replace(day=1),
        "endRange": month.replace(day=calendar.monthrange(month.year, month.month)[-1]),
    }

    sales_data = rq.get(
        base_url + "/sales",
        params=parameters,
        headers=headers,
    )

    if sales_data.status_code == 404:
        return []

    sales_data = sales_data.json()

    for sale in sales_data:
        sale["moment"] = Sale.parse_moment(sale["moment"])

    return [Sale(**sale) for sale in sales_data]


# @lru_cache
def get_payments(month: date, headers: dict) -> List[Payment]:
    parameters = {
        "startRange": month.replace(day=1),
        "endRange": month.replace(day=calendar.monthrange(month.year, month.month)[-1]),
    }

    payments_data = rq.get(
        base_url + "/payments",
        params=parameters,
        headers=headers,
    )

    if payments_data.status_code == 404:
        payments_data = []
    else:
        payments_data = payments_data.json()

    for payment in payments_data:
        payment["done"] = Payment.parse_done(payment["done"])

    return [Payment(**payment) for payment in payments_data]
