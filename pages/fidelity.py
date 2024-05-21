import calendar
from datetime import date, datetime, timedelta
import math
from typing import Dict, List

import pandas as pd
from requests import HTTPError
from helpers.api import get_product_data, rq, base_url, get_headers
import streamlit as st

from models.customers import Customer
from models.plans import Plan, Subscriber
from models.sales import Product, Sale

products_data: Dict[str, Product] = {}

st.set_page_config("DRE", layout="wide")
if not st.query_params.get("company") or not st.query_params.get("session_token"):
    try:
        st.query_params.company = st.session_state.company
        st.query_params.session_token = st.session_state.session_token
    except:
        st.switch_page("login.py")
else:
    st.session_state.company = st.query_params.company
    st.session_state.session_token = st.query_params.session_token


def get_fidelity_plans() -> List[Plan]:
    headers = get_headers(st.session_state.company, st.session_state.session_token)
    parameters = {"name": "Plano"}
    response = rq.get(base_url + "/services", params=parameters, headers=headers)
    if response.status_code == 404:
        return []

    response.raise_for_status()
    plans = response.json()
    for plan in plans:
        plan["promotion"] = Plan.find_promotion(plan["name"])
        plan["limit"] = plan["particulars"]["limite"].replace("L", "000")

    plans = [Plan(**plan) for plan in plans]

    return plans


def get_customer_data(customer_id: int) -> Customer:
    headers = get_headers(st.session_state.company, st.session_state.session_token)
    parameters = {"id": customer_id}
    response = rq.get(base_url + "/customers", params=parameters, headers=headers)
    if response.status_code == 404:
        return []

    response.raise_for_status()

    return response.json()[0]


def get_subscribers(plan: Plan) -> List[Subscriber]:
    headers = get_headers(st.session_state.company, st.session_state.session_token)
    today = datetime.today().replace(hour=23, minute=59, second=59)
    vigency_init = (today - timedelta(days=45)).replace(hour=0, minute=0, second=0)
    parameters = {
        "services": f"[{plan.id}]",
        "startRange": vigency_init,
        "endRange": today,
    }
    response = rq.get(base_url + "/sales", params=parameters, headers=headers)
    if response.status_code == 404:
        return []

    response.raise_for_status()
    subscribers = response.json()
    for subscriber in subscribers:
        subscriber["moment"] = Subscriber.parse_moment(subscriber["moment"])
        subscriber["due_date"] = subscriber["moment"] + timedelta(days=30)
        subscriber["customer"] = Customer(**get_customer_data(subscriber["customer"]))
        subscriber["promotion"] = plan.promotion

    subscribers = [Subscriber(**subscriber) for subscriber in subscribers]
    subscribers.sort(key=lambda subscriber: subscriber.moment)

    return subscribers


def get_subscriber_shopps(subscriber: Subscriber) -> List[Sale]:
    headers = get_headers(st.session_state.company, st.session_state.session_token)
    vigency_init = subscriber.moment
    vigency_end = (subscriber.moment + timedelta(days=30)).replace(
        hour=23, minute=59, second=59
    )

    parameters = {
        "promotion": subscriber.promotion.value,
        "customer": subscriber.customer.id,
        "startRange": vigency_init,
        "endRange": vigency_end,
    }

    response = rq.get(base_url + "/sales", params=parameters, headers=headers)
    if response.status_code == 404:
        return []

    shopps = response.json()
    for shopp in shopps:
        shopp["moment"] = Sale.parse_moment(shopp["moment"])

    return [Sale(**shopp) for shopp in shopps]


def get_subscriber_consume(shopps: List[Sale]) -> float:
    consume = 0
    for shopp in shopps:
        products = shopp.products
        for product in products:
            if product not in products_data:
                product_data = get_product_data(
                    get_headers(
                        st.session_state.company, st.session_state.session_token
                    ),
                    product,
                )
                products_data[product] = product_data
            consume += products_data[product].size * float(products[product])

    return consume


def calc_due_date_interval(due_date: date):
    interval = (due_date - datetime.today()).days

    if interval <= 5:
        return "Finaliza em até 5 dias"

    if interval <= 15:
        return "Finaliza em até 15 dias"

    return "Finaliza em 16 dias ou mais"


if __name__ == "__main__":
    try:
        plans = get_fidelity_plans()
    except HTTPError as e:
        if e.response.status_code == 401:
            st.switch_page("login.py")
        raise e

    resume = {
        plan.id: {
            "limite": {},
            "consumo": {},
        }
        for plan in plans
    }
    consumo_restante = {
        plan.id: {
            "Consumido": {},
            "ML": {},
            "Litros": {},
            "Garrafa": {},
            "Piriguete": {},
            "Latão": {},
            "Latinha": {},
            "Refri 2L": {},
            "Refri Pitchulinha": {},
            "Redbull": {},
        }
        for plan in plans
    }
    data_limites = {
        plan.id: {"Início": {}, "Término": {}, "Hoje": {}, "Restante": {}}
        for plan in plans
    }
    if plans:
        for plan in plans:
            subscribers = get_subscribers(plan)
            if subscribers:
                for subscriber in subscribers:
                    subscriber_name = (
                        f"{subscriber.customer.name} {subscriber.customer.last_name}"
                    )
                    shopps = get_subscriber_shopps(subscriber)
                    consume = get_subscriber_consume(shopps)
                    resume[plan.id]["limite"][subscriber_name] = plan.limit
                    resume[plan.id]["consumo"][subscriber_name] = consume
                    data_limites[plan.id]["Início"][subscriber_name] = subscriber.moment
                    data_limites[plan.id]["Término"][
                        subscriber_name
                    ] = subscriber.due_date
                    data_limites[plan.id]["Hoje"][subscriber_name] = datetime.today()
                    data_limites[plan.id]["Restante"][
                        subscriber_name
                    ] = calc_due_date_interval(subscriber.due_date)

                    _consumo_restante = plan.limit - consume

                    consumo_restante[plan.id]["Consumido"][subscriber_name] = round(
                        consume
                    )
                    consumo_restante[plan.id]["ML"][subscriber_name] = round(
                        _consumo_restante
                    )
                    consumo_restante[plan.id]["Litros"][subscriber_name] = round(
                        _consumo_restante / 1000
                    )
                    consumo_restante[plan.id]["Garrafa"][subscriber_name] = math.ceil(
                        _consumo_restante / 600
                    )
                    consumo_restante[plan.id]["Piriguete"][subscriber_name] = math.ceil(
                        _consumo_restante / 300
                    )
                    consumo_restante[plan.id]["Latão"][subscriber_name] = math.ceil(
                        _consumo_restante / 473
                    )
                    consumo_restante[plan.id]["Latinha"][subscriber_name] = math.ceil(
                        _consumo_restante / 350
                    )
                    consumo_restante[plan.id]["Refri 2L"][subscriber_name] = round(
                        _consumo_restante / 2000
                    )
                    consumo_restante[plan.id]["Refri Pitchulinha"][
                        subscriber_name
                    ] = math.ceil(_consumo_restante / 200)
                    consumo_restante[plan.id]["Redbull"][subscriber_name] = math.ceil(
                        _consumo_restante / 250
                    )

        if resume and consumo_restante:
            with st.expander("Assinantes"):
                tabs = st.tabs([plan.name for plan in plans])
                for tab, plan in enumerate(plans):
                    # tabs[tab].table(pd.DataFrame(consumo_restante[plan.id]))
                    tabs[tab].data_editor(
                        consumo_restante[plan.id],
                        column_config={
                            "Consumido": st.column_config.ProgressColumn(
                                "Total Consumido",
                                help="Total Consumido do Plano",
                                format="%f ML",
                                min_value=0,
                                max_value=plan.limit,
                                width="large",
                            ),
                        },
                    )
                    tabs[tab].scatter_chart(pd.DataFrame(resume[plan.id]))
                    tabs[tab].scatter_chart(
                        pd.DataFrame(data_limites[plan.id]),
                        y=["Início", "Término", "Hoje"],
                        size="Restante",
                        color="Restante",
                    )

        if resume:
            with st.expander("Visão Geral"):
                tile = st.container(border=True)
                tile.metric(
                    "Total de Assinantes",
                    sum([len(resume[sub]["consumo"].keys()) for sub in resume]),
                )

                tabs = st.tabs([plan.name for plan in plans])
                for tab, plan in enumerate(plans):
                    tile = tabs[tab].container(border=True)
                    tile.metric(
                        f"Total de Assinantes: {plan.name}",
                        len(resume[plan.id]["consumo"].keys()),
                    )
                    tabs[tab].area_chart(pd.DataFrame(resume[plan.id]))
