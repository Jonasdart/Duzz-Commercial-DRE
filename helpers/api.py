import calendar
from datetime import date
from functools import lru_cache
from typing import List, Union
import requests as rq

from models.bills import Bills
from models.customers import Customer
from models.payments import Payment
from models.sales import Product, Sale, Service
from models.stocks import Stock
import cachetools.func


base_url = "https://api.duzzsystem.com.br"


@lru_cache
def get_token(username: str, password: str, company: str):
    user_data = rq.get(
        base_url + "/auth/user",
        params={"username": username, "password": password, "company": company},
    )
    user_data.raise_for_status()
    user_data = user_data.json()

    return user_data["sessionToken"], user_data["companyData"]["pseudonimo"]


@lru_cache
def get_headers(company: str, session_token: str) -> tuple:
    return (("company", company), ("sessionToken", session_token))


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_stocks(headers: tuple) -> List[Stock]:
    parameters = {"withMoves": True}

    stocks_list = rq.get(
        base_url + "/stock",
        params=parameters,
        headers=dict(headers),
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


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_stock_by_month(month: date, headers: tuple) -> List[Union[Stock,]]:
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


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_product_data(headers: tuple, product_id: int) -> Product:
    parameters = {"id": product_id}
    response = rq.get(base_url + "/products", params=parameters, headers=dict(headers))
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    product_data = response.json()[0]
    product_data = Product(
        id=product_data["id"],
        name=product_data["name"],
        size=product_data["particulars"]["tamanho"],
        price=product_data["value"],
    )

    return product_data


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_service_data(service_id: int, headers: tuple) -> Service:
    parameters = {"id": service_id}
    response = rq.get(base_url + "/services", params=parameters, headers=dict(headers))
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    service_data = response.json()[0]
    service_data = Service(
        id=service_data["id"],
        name=service_data["name"],
        size=service_data.get("particulars", {}).get("tamanho"),
        price=service_data["value"],
    )

    return service_data


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_customer_data(customer_id: int, headers: tuple) -> Customer:
    headers = dict(headers)
    parameters = {"id": customer_id}
    response = rq.get(base_url + "/customers", params=parameters, headers=headers)
    if response.status_code == 404:
        return []

    response.raise_for_status()
    customer_data = response.json()[0]

    return Customer(**customer_data)


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_sales(month: date, headers: tuple) -> List[Sale]:
    parameters = {
        "startRange": month.replace(day=1),
        "endRange": month.replace(day=calendar.monthrange(month.year, month.month)[-1]),
    }

    sales_data = rq.get(
        base_url + "/sales",
        params=parameters,
        headers=dict(headers),
    )

    if sales_data.status_code == 404:
        return []

    sales_data = sales_data.json()

    for sale in sales_data:
        sale["moment"] = Sale.parse_moment(sale["moment"])

    return [Sale(**sale) for sale in sales_data]


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_payments(month: date, headers: tuple) -> List[Payment]:
    parameters = {
        "startRange": month.replace(day=1),
        "endRange": month.replace(day=calendar.monthrange(month.year, month.month)[-1]),
    }

    payments_data = rq.get(
        base_url + "/payments",
        params=parameters,
        headers=dict(headers),
    )

    if payments_data.status_code == 404:
        payments_data = []
    else:
        payments_data = payments_data.json()

    for payment in payments_data:
        payment["done"] = Payment.parse_done(payment["done"])

    return [Payment(**payment) for payment in payments_data]


@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
def get_bills(headers: tuple):
    bills_data = rq.get(
        base_url + "/bills-to-pay",
        headers=dict(headers),
    )

    if bills_data.status_code == 404:
        bills_data = []
    else:
        bills_data = bills_data.json()

    for bill_to_pay in bills_data:
        bill_to_pay["createdAt"] = Bills.parse_datetime(bill_to_pay["createdAt"])
        bill_to_pay["closedAt"] = Bills.parse_datetime(bill_to_pay["closedAt"])
        bill_to_pay["dueDate"] = Bills.parse_datetime(bill_to_pay["dueDate"])

    return [Bills(**bill) for bill in bills_data]
