from datetime import date
import calendar
import decimal
from functools import lru_cache
from typing import List

from requests import HTTPError
from helpers.api import (
    get_customer_data,
    get_payments,
    get_sales,
    get_service_data,
    get_stock_by_month,
    rq,
    base_url,
    get_headers,
    get_stocks,
)
from models.enums import ReferenceTable
from models.payments import Payment
import streamlit as st
import pandas as pd
import numpy as np

from models.sales import Sale
from models.stocks import Stock


st.set_page_config(
    "dcommercial - Resumo da Empresa", layout="wide", initial_sidebar_state="collapsed"
)
if not st.query_params.get("company") or not st.query_params.get("session_token"):
    try:
        st.query_params.company = st.session_state.company
        st.query_params.session_token = st.session_state.session_token
    except:
        st.switch_page("login.py")
else:
    st.session_state.company = st.query_params.company
    st.session_state.session_token = st.query_params.session_token


def get_faturamento_data(
    payments: List[Payment], sales: List[Sale], stocks: List[Stock]
):
    revenues: decimal = 0
    discounts: decimal = 0
    expenses: decimal = 0
    cogs = 0
    for stock in stocks:
        for move in stock.outs.moves:
            if move.moment.date() >= month and move.moment.date() <= month.replace(
                day=calendar.monthrange(month.year, month.month)[-1]
            ):
                cogs += move.value

    for payment in payments:
        if payment.reference_table is ReferenceTable.SALES:
            revenues += payment.value
            try:
                sale = [sale for sale in sales if sale.id == payment.reference_id][0]
            except IndexError:
                continue
            revenues += sale.discount
            discounts += sale.discount

        if payment.reference_table is ReferenceTable.BILLS_TO_PAY:
            expenses += payment.value

    return {
        "receitas": revenues,
        "despesas": expenses,
        "descontos": discounts,
        "cmv": cogs,
    }


months = [date(2023, month + 1, 1) for month in range(12)]
months.extend([date(2024, month + 1, 1) for month in range(date.today().month)])
report_months = st.multiselect(
    "", months, default=months[-1], placeholder="Selecione um mês de competência"
)

report_months.sort()

if report_months:
    resume = {
        "faturamento": {f"{month.strftime('%m/%y')}": {} for month in report_months},
        "clientes": {f"{month.strftime('%m/%y')}": {} for month in report_months},
        "produtos": {f"{month.strftime('%m/%y')}": {} for month in report_months},
        "serviços": {f"{month.strftime('%m/%y')}": {} for month in report_months},
    }
    ## Generate Data
    headers = get_headers(
        st.session_state["company"], st.session_state["session_token"]
    )

    def buscar_faturamento(month: date, headers: dict):
        payments = get_payments(month, headers)
        sales = get_sales(
            month,
            headers,
        )
        stocks = get_stock_by_month(month, headers)
        return get_faturamento_data(payments, sales, stocks)

    def buscar_produtos(month: date, headers: dict):
        stocks = get_stock_by_month(month, headers)
        resumo = {}

        for stock in stocks:
            for move in stock.outs.moves:
                if move.moment.date() >= month and move.moment.date() <= month.replace(
                    day=calendar.monthrange(month.year, month.month)[-1]
                ):
                    try:
                        resumo[move.product_id] += move.amount
                    except KeyError:
                        resumo[move.product_id] = move.amount

        return resumo

    def buscar_servicos(month: date, headers: dict):
        sales = get_sales(month, headers)
        resumo = {}

        for sale in sales:
            for service in sale.services.items():
                service_data = get_service_data(service[0], headers)
                try:
                    resumo[service_data.name] += float(service[1])
                except KeyError:
                    resumo[service_data.name] = float(service[1])

        return resumo

    def buscar_fidelidade(month: date, headers: dict) -> dict:
        sales = get_sales(month, headers)
        resumo = {}

        for sale in sales:
            customer = get_customer_data(sale.customer, tuple(headers.items()))
            try:
                resumo[customer.get_full_name()] += sale.value
            except KeyError:
                resumo[customer.get_full_name()] = sale.value

        return resumo

    try:
        for month in report_months:
            resume["faturamento"][month.strftime("%m/%y")] = buscar_faturamento(
                month, headers
            )
            resume["clientes"][month.strftime("%m/%y")] = buscar_fidelidade(
                month, headers
            )
            resume["produtos"][month.strftime("%m/%y")] = buscar_produtos(
                month, headers
            )
            resume["serviços"][month.strftime("%m/%y")] = buscar_servicos(
                month, headers
            )

        df_fat = pd.DataFrame(resume.pop("faturamento")).T
        df_fat.loc["acumulado"] = df_fat.select_dtypes(np.number).sum()

        df_clientes = pd.DataFrame(resume.pop("clientes"))
        df_clientes.fillna(0, inplace=True)
        df_clientes["acumulado"] = df_clientes.cumsum(axis=1).iloc[:, -1]
        df_clientes = df_clientes.sort_values("acumulado", ascending=False)

        df_produtos = pd.DataFrame(resume.pop("produtos"))
        df_produtos["acumulado"] = df_produtos.cumsum(axis=1).iloc[:, -1]
        df_produtos = df_produtos.sort_values("acumulado", ascending=False)

        df_servicos = pd.DataFrame(resume.pop("serviços"))
        df_servicos["acumulado"] = df_servicos.cumsum(axis=1).iloc[:, -1]
        df_servicos = df_servicos.sort_values("acumulado", ascending=False)
    except HTTPError as e:
        if e.response.status_code == 401:
            st.switch_page("login.py")
        raise e

    despesas_admnistrativas = df_fat["despesas"]["acumulado"]
    despesas_cmv = df_fat["cmv"]["acumulado"]
    lucro_bruto = df_fat["receitas"]["acumulado"]
    descontos_totais = df_fat["descontos"]["acumulado"]

    despesas_totais = despesas_admnistrativas + despesas_cmv + descontos_totais

    lucro_liquido = lucro_bruto - despesas_totais
    discount_percent = (descontos_totais / lucro_bruto if lucro_bruto else 1) * 100

    # Visualize geral data
    with st.expander("Resumo Geral", expanded=True):
        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.header("DRE DUZZ COMMERCIAL")
            st.table(df_fat)

            c1.bar_chart(
                df_fat,
                color=("#FF5F35", "#FCAF19", "#EF4854", "#70F06D"),
                width=500,
                use_container_width=False,
            )

        with c2:
            c_c1, c_c2 = c2.columns(2, gap="medium")
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

            c2.area_chart(
                df_fat,
                color=("#FF5F35", "#FCAF19", "#EF4854", "#70F06D"),
                width=500,
                use_container_width=False,
            )

    with st.expander("Resumo Fidelidade"):
        show_customers = st.number_input(
            "Visualizar o top:", value=10, min_value=1, key="customers"
        )
        st.subheader(f"TOP {show_customers} CLIENTES")
        st.table(df_clientes.head(show_customers))
        st.bar_chart(df_clientes.head(show_customers)["acumulado"])

    with st.expander("Resumo Produtos e Serviços"):
        show_num = st.number_input("Visualizar o top:", value=10, min_value=1)
        st.subheader(f"TOP {show_num} PRODUTOS MAIS VENDIDOS")
        st.table(df_produtos.head(show_num))

        st.subheader(f"TOP {show_num} SERVIÇOS MAIS VENDIDOS")
        st.table(df_servicos.head(show_num))
