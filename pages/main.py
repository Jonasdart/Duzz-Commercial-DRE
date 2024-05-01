from datetime import date
import calendar
import decimal
from functools import lru_cache
from typing import List
from helpers.api import rq, base_url, get_headers
from models.enums import ReferenceTable
from models.payments import Payment
import streamlit as st
import pandas as pd
import numpy as np

from models.sales import Sale
from models.stocks import Stock


@lru_cache
def get_payments(month: date) -> List[Payment]:
    parameters = {
        "startRange": month.replace(day=1),
        "endRange": month.replace(day=calendar.monthrange(month.year, month.month)[-1]),
    }

    payments_data = rq.get(
        base_url + "/payments",
        params=parameters,
        headers=get_headers(st.session_state["company"], st.session_state["session_token"]),
    )

    if payments_data.status_code == 404:
        payments_data = []
    else:
        payments_data = payments_data.json()

    for payment in payments_data:
        payment["done"] = Payment.parse_done(payment["done"])

    return [Payment(**payment) for payment in payments_data]


@lru_cache
def get_stocks():
    parameters = {"withMoves": True}

    stocks_list = rq.get(
        base_url + "/stock",
        params=parameters,
        headers=get_headers(st.session_state["company"], st.session_state["session_token"]),
    )

    if stocks_list.status_code == 404:
        stocks_list = []
    else:
        stocks_list = stocks_list.json()

    for stock in stocks_list:
        stock["startDate"] = Stock.parse_date(stock["startDate"])
        stock["dueDate"] = Stock.parse_date(stock["dueDate"])

    return [Stock(**stock) for stock in stocks_list]


@lru_cache
def get_sales(month: date) -> List[Sale]:
    parameters = {
        "startRange": month.replace(day=1),
        "endRange": month.replace(day=calendar.monthrange(month.year, month.month)[-1]),
    }

    sales_data = rq.get(
        base_url + "/sales",
        params=parameters,
        headers=get_headers(st.session_state["company"], st.session_state["session_token"]),
    )

    if sales_data.status_code == 404:
        return []

    sales_data = sales_data.json()

    for sale in sales_data:
        sale["moment"] = Sale.parse_moment(sale["moment"])

    return [Sale(**sale) for sale in sales_data]


def get_faturamento_data(months):
    faturamento = {
        "despesas": {},
        "cmv": {},
        "receitas": {},
        "descontos": {},
    }
    all_stocks = get_stocks()
    for month in months:
        competence_payments = get_payments(month)
        competence_sales = get_sales(month)

        revenues: decimal = 0
        discounts: decimal = 0
        expenses: decimal = 0
        cmv: decimal = 0

        for stock in all_stocks:
            if (
                stock.start_date.date() > month
                and stock.start_date.date()
                <= month.replace(day=calendar.monthrange(month.year, month.month)[-1])
            ):
                cmv += stock.cmv

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


if __name__ == "__main__":
    st.set_page_config("DRE", layout="wide")

    months = [date(2024, month + 1, 1) for month in range(date.today().month)]
    report_month = st.multiselect(
        "", months, placeholder="Selecione um mês de competência"
    )
    
    report_month.sort()

    if report_month:
        df = pd.DataFrame(get_faturamento_data(report_month))
        df.loc["acumulado"] = df.select_dtypes(np.number).sum()

        despesas_admnistrativas = df["despesas"]["acumulado"]
        despesas_cmv = df["cmv"]["acumulado"]
        lucro_bruto = df["receitas"]["acumulado"]

        despesas_totais = (
            despesas_admnistrativas + despesas_cmv + df["descontos"]["acumulado"]
        )

        lucro_liquido = lucro_bruto - despesas_totais
        discount_percent = (
            df["descontos"]["acumulado"] / df["receitas"]["acumulado"]
        ) * 100

        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.header("DRE DUGOLE")
            st.table(df)
            c_c1, c_c2 = c1.columns(2, gap="medium")
            with c_c1:
                tile = c_c1.container(height=120)
                tile.metric(
                    "Lucro Liquido",
                    value=f"R$ {round(lucro_liquido, 2)}",
                    delta=f"{round((lucro_liquido / lucro_bruto) * 100)} %",
                )
                tile = c_c1.container(height=120)
                tile.metric(
                    "Receitas - Despesas",
                    value=f"R$ {round(lucro_bruto - despesas_admnistrativas, 2)}",
                    delta=f"{round((lucro_bruto / despesas_admnistrativas))} %",
                    delta_color="normal",
                )
            with c_c2:
                tile = c_c2.container(height=120)
                tile.metric(
                    "Descontos s/ Receita",
                    value=f"R$ {round(df['descontos']['acumulado'], 2)}",
                    delta=f"{round(discount_percent, 2)} %",
                    delta_color="off",
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
