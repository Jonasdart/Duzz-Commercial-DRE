from datetime import date
import calendar
import decimal
from functools import lru_cache
from typing import List

from requests import HTTPError
from helpers.api import rq, base_url, get_headers
from models.enums import ReferenceTable
from models.payments import Payment
import streamlit as st
import pandas as pd
import numpy as np

from models.sales import Sale
from models.stocks import Stock


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


all_stocks = get_stocks(
    tuple(
        get_headers(
            st.session_state["company"], st.session_state["session_token"]
        ).items()
    )
)


@lru_cache
def get_payments(month: date) -> List[Payment]:
    parameters = {
        "startRange": month.replace(day=1),
        "endRange": month.replace(day=calendar.monthrange(month.year, month.month)[-1]),
    }

    payments_data = rq.get(
        base_url + "/payments",
        params=parameters,
        headers=get_headers(
            st.session_state["company"], st.session_state["session_token"]
        ),
    )

    if payments_data.status_code == 404:
        payments_data = []
    else:
        payments_data = payments_data.json()

    for payment in payments_data:
        payment["done"] = Payment.parse_done(payment["done"])

    return [Payment(**payment) for payment in payments_data]


@lru_cache
def get_sales(month: date) -> List[Sale]:
    parameters = {
        "startRange": month.replace(day=1),
        "endRange": month.replace(day=calendar.monthrange(month.year, month.month)[-1]),
    }

    sales_data = rq.get(
        base_url + "/sales",
        params=parameters,
        headers=get_headers(
            st.session_state["company"], st.session_state["session_token"]
        ),
    )

    if sales_data.status_code == 404:
        return []

    sales_data = sales_data.json()

    for sale in sales_data:
        sale["moment"] = Sale.parse_moment(sale["moment"])

    return [Sale(**sale) for sale in sales_data]


@lru_cache
def get_period_cmv(month: date):
    cmv = 0
    for stock in all_stocks:
        if (
            (
                stock.due_date
                and (
                    stock.start_date.date() >= month
                    or stock.due_date.date()
                    <= month.replace(
                        day=calendar.monthrange(month.year, month.month)[-1]
                    )
                )
            )
            or not stock.due_date
            and (stock.start_date.date() <= month)
        ):
            for move in stock.outs.moves:
                if move.moment.date() >= month and move.moment.date() <= month.replace(
                    day=calendar.monthrange(month.year, month.month)[-1]
                ):
                    cmv += move.value

    return cmv


def get_faturamento_data(months: List[date]):
    faturamento = {
        "despesas": {},
        "cmv": {},
        "receitas": {},
        "descontos": {},
    }

    for month in months:
        competence_payments = get_payments(month)
        competence_sales = get_sales(month)

        revenues: decimal = 0
        discounts: decimal = 0
        expenses: decimal = 0
        cmv: decimal = get_period_cmv(month)

        for payment in competence_payments:
            if payment.reference_table is ReferenceTable.SALES:
                revenues += payment.value
                try:
                    sale = [
                        sale
                        for sale in competence_sales
                        if sale.id == payment.reference_id
                    ][0]
                except IndexError:
                    continue
                revenues += sale.discount
                discounts += sale.discount

            if payment.reference_table is ReferenceTable.BILLS_TO_PAY:
                expenses += payment.value

        faturamento["receitas"][month.strftime("%m/%y")] = revenues
        faturamento["despesas"][month.strftime("%m/%y")] = expenses
        faturamento["descontos"][month.strftime("%m/%y")] = discounts
        faturamento["cmv"][month.strftime("%m/%y")] = cmv

    return faturamento


months = [date(2023, month + 1, 1) for month in range(12)]
months.extend([date(2024, month + 1, 1) for month in range(date.today().month)])
report_month = st.multiselect(
    "", months, default=months[-1], placeholder="Selecione um mês de competência"
)

report_month.sort()

if report_month:
    try:
        df = pd.DataFrame(get_faturamento_data(report_month))
    except HTTPError as e:
        if e.response.status_code == 401:
            st.switch_page("login.py")
        raise e

    df.loc["acumulado"] = df.select_dtypes(np.number).sum()

    despesas_admnistrativas = df["despesas"]["acumulado"]
    despesas_cmv = df["cmv"]["acumulado"]
    lucro_bruto = df["receitas"]["acumulado"]
    descontos_totais = df["descontos"]["acumulado"]

    despesas_totais = despesas_admnistrativas + despesas_cmv + descontos_totais

    lucro_liquido = lucro_bruto - despesas_totais
    discount_percent = (descontos_totais / lucro_bruto if lucro_bruto else 1) * 100

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.header("DRE DUZZ COMMERCIAL")
        st.table(df)
        c_c1, c_c2 = c1.columns(2, gap="medium")
        with c_c1:
            tile = c_c1.container(border=True)
            tile.metric(
                "Lucro Liquido",
                value=f"R$ {round(lucro_liquido, 2)}",
                delta=f"{round((lucro_liquido / lucro_bruto if lucro_bruto else 1) * 100)} %",
            )
            tile = c_c1.container(border=True)
            tile.metric(
                "Receitas - Despesas",
                value=f"R$ {round(lucro_bruto - despesas_admnistrativas, 2)}",
                delta=f"{round(((lucro_bruto - despesas_admnistrativas) / despesas_admnistrativas if despesas_admnistrativas else 1) * 100)} %",
                delta_color="normal",
            )
        with c_c2:
            tile = c_c2.container(border=True)
            tile.metric(
                "Descontos sobre Receita",
                value=f"R$ {round(descontos_totais, 2)}",
                delta=f"{round(discount_percent, 2)} %",
                delta_color="off",
            )
            tile = c_c2.container(border=True)
            tile.metric(
                "Margem sobre o CMV",
                value=f"R$ {round((lucro_bruto - descontos_totais) - despesas_cmv, 2)}",
                delta=f"{round((((lucro_bruto - descontos_totais) - despesas_cmv) / despesas_cmv) * 100, 2)} %",
            )

    with c2:
        st.bar_chart(
            df,
            color=("#FF5F35", "#FCAF19", "#EF4854", "#70F06D"),
            width=500,
            use_container_width=False,
        )
        st.area_chart(
            df,
            color=("#FF5F35", "#FCAF19", "#EF4854", "#70F06D"),
            width=500,
            use_container_width=False,
        )
