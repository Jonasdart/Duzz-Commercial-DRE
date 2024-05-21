from functools import lru_cache
from typing import List
import requests as rq

from models.sales import Product
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


@lru_cache
def get_stocks(headers: tuple) -> List[Stock]:
    headers = dict(headers)
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

    return [Stock(**stock) for stock in stocks_list]


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

