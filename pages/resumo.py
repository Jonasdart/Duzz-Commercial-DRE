from datetime import date
import calendar
import decimal
from functools import lru_cache
from typing import List

from requests import HTTPError
from helpers.api import (
    get_bills,
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
from helpers import float_container
from models.bills import Bills
from models.enums import ReferenceTable
from models.payments import Payment
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

from models.sales import Sale
from models.stocks import Stock

days = [
    "7 - Domingo",
    "1 - Segunda",
    "2 - Terça",
    "3 - Quarta",
    "4 - Quinta",
    "5 - Sexta",
    "6 - Sábado",
]

periods = {
    "madrugada": ((0, 0), (5, 59)),
    "manha": ((6, 0), (11, 59)),
    "tarde": ((12, 0), (17, 59)),
    "noite": ((18, 0), (23, 59)),
}
# days = list(range(7))


st.set_page_config(
    "dcommercial - Resumo da Empresa", layout="wide", initial_sidebar_state="collapsed"
)
if not st.query_params.get("company") or not st.query_params.get("session_token"):
    try:
        st.query_params.company = st.session_state.company
        st.query_params.session_token = st.session_state.session_token
        st.query_params.pseudonym = st.session_state.pseudonym
    except:
        st.switch_page("login.py")
else:
    st.session_state.company = st.query_params.company
    st.session_state.session_token = st.query_params.session_token
    st.session_state.pseudonym = st.query_params.pseudonym

st.header(st.query_params.pseudonym.upper())

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_faturamento_data(
    payments: List[Payment],
    sales: List[Sale],
    stocks: List[Stock],
    bills_to_pay: List[Bills],
):
    revenues: decimal = 0
    discounts: decimal = 0
    expenses: decimal = 0
    cogs = 0
    daily = {day: 0 for day in days}
    by_period = {period: 0 for period in periods}
    for stock in stocks:
        for move in stock.outs.moves:
            if move.moment.date() >= month and move.moment.date() <= month.replace(
                day=calendar.monthrange(month.year, month.month)[-1]
            ):
                cogs += move.value

    for sale in sales:
        for period in periods:
            if (
                sale.moment.hour >= periods[period][0][0]
                and sale.moment.hour <= periods[period][1][0]
            ):
                by_period[period] += sale.value
        daily[days[sale.moment.weekday()]] += sale.value

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
            for bill in bills_to_pay:
                if (
                    bill.id == payment.reference_id
                    and bill.reference_table is not ReferenceTable.STOCK_ENTRIES
                ):
                    expenses += payment.value

    return {
        **{day: daily.get(day, 0) for day in [*days[1:], days[0]]},
        "by_periods": by_period,
        "receitas": revenues,
        "despesas": expenses,
        "descontos": discounts,
        "cmv": cogs,
        "vendas": len(sales),
    }


headers = get_headers(st.session_state["company"], st.session_state["session_token"])

try:
    bills_to_pay = get_bills(headers)
except Exception as e:
    st.balloons()
    st.title("Faça o :blue[Upgrade]⬆️ do seu plano!")
    st.title("E garanta já essa e muitas outras funcionalidades! :sunglasses:")
    st.link_button(
        "É pra já! 📲",
        url="https://api.whatsapp.com/send/?phone=5538998588893&text=Ola, gostaria de fazer upgrade do meu plano&type=phone_number&app_absent=0",
        use_container_width=True,
        type="primary",
    )
else:
    months = [date(2024, month + 1, 1) for month in range(date.today().month)]
    report_months = st.multiselect(
        "", months, default=months[-1], placeholder="Selecione um mês de competência"
    )

    report_months.sort()
    ## Generate Data

    if report_months:
        resume = {
            "daily": {f"{month.strftime('%m/%y')}": {} for month in report_months},
            "by_period": {f"{month.strftime('%m/%y')}": {} for month in report_months},
            "faturamento": {
                f"{month.strftime('%m/%y')}": {} for month in report_months
            },
            "clientes": {f"{month.strftime('%m/%y')}": {} for month in report_months},
            "produtos": {f"{month.strftime('%m/%y')}": {} for month in report_months},
            "serviços": {f"{month.strftime('%m/%y')}": {} for month in report_months},
        }

        def buscar_faturamento(month: date, headers: tuple):
            payments = get_payments(month, headers)
            sales = get_sales(
                month,
                headers,
            )
            stocks = get_stock_by_month(month, headers)
            return get_faturamento_data(payments, sales, stocks, bills_to_pay)

        def buscar_produtos(month: date, headers: tuple):
            stocks = get_stock_by_month(month, headers)
            resumo = {}

            for stock in stocks:
                for move in stock.outs.moves:
                    if (
                        move.moment.date() >= month
                        and move.moment.date()
                        <= month.replace(
                            day=calendar.monthrange(month.year, month.month)[-1]
                        )
                    ):
                        try:
                            resumo[move.product_id] += move.amount
                        except KeyError:
                            resumo[move.product_id] = move.amount

            return resumo

        def buscar_servicos(month: date, headers: tuple):
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

        def buscar_fidelidade(month: date, headers: tuple) -> dict:
            sales = get_sales(month, headers)
            resumo = {}

            for sale in sales:
                customer = get_customer_data(sale.customer, headers)
                try:
                    resumo[customer.get_full_name()] += sale.value
                except KeyError:
                    resumo[customer.get_full_name()] = sale.value

            return resumo

        try:
            for month in report_months:
                faturamento_data = buscar_faturamento(month, headers)
                total_vendas = faturamento_data.pop("vendas")
                resume["faturamento"][month.strftime("%m/%y")] = {
                    "receitas": faturamento_data.pop("receitas"),
                    "despesas": faturamento_data.pop("despesas"),
                    "descontos": faturamento_data.pop("descontos"),
                    "cmv": faturamento_data.pop("cmv"),
                }
                resume["by_period"][month.strftime("%m/%y")] = faturamento_data.pop(
                    "by_periods"
                )
                resume["daily"][month.strftime("%m/%y")] = faturamento_data
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

            df_daily = pd.DataFrame(resume.pop("daily")).T
            df_daily.fillna(0, inplace=True)
            df_daily.loc["acumulado"] = df_daily.select_dtypes(np.number).sum()

            df_period = pd.DataFrame(resume.pop("by_period")).T
            df_period.fillna(0, inplace=True)
            df_period.loc["acumulado"] = df_period.select_dtypes(np.number).sum()

            df_clientes = pd.DataFrame(resume.pop("clientes"))
            df_clientes.fillna(0, inplace=True)
            df_clientes["acumulado"] = df_clientes.cumsum(axis=1).iloc[:, -1]
            df_clientes = df_clientes.sort_values("acumulado", ascending=False)

            df_produtos = pd.DataFrame(resume.pop("produtos"))
            df_produtos.fillna(0, inplace=True)
            df_produtos["acumulado"] = df_produtos.cumsum(axis=1).iloc[:, -1]
            df_produtos = df_produtos.sort_values("acumulado", ascending=False)

            df_servicos = pd.DataFrame(resume.pop("serviços"))
            df_servicos.fillna(0, inplace=True)
            df_servicos["acumulado"] = df_servicos.cumsum(axis=1).iloc[:, -1]
            df_servicos = df_servicos.sort_values("acumulado", ascending=False)
        except HTTPError as e:
            if e.response.status_code == 401:
                st.switch_page("login.py")
            raise e

        despesas_admnistrativas = df_fat["despesas"]["acumulado"]
        custo_mercadoria_vendida = df_fat["cmv"]["acumulado"]
        receita_bruta = df_fat["receitas"]["acumulado"]
        descontos_totais = df_fat["descontos"]["acumulado"]
        receita_menos_descontos = receita_bruta - descontos_totais
        lucro_bruto = receita_menos_descontos - custo_mercadoria_vendida

        despesas_totais = despesas_admnistrativas + custo_mercadoria_vendida

        lucro_liquido = receita_menos_descontos - despesas_totais
        discount_percent = (
            descontos_totais / receita_bruta if receita_bruta else 1
        ) * 100

        # Visualize geral data
        with float_container.sticky_container(position="top", border=False):
            apenas_acumulado = st.toggle("Ver apenas o acumulado")

        with st.expander("Resumo Geral", expanded=True):
            c1, c2 = st.columns(2, gap="large")

            with c1:
                c1.dataframe(
                    df_fat,
                    use_container_width=True,
                    column_config={
                        col: st.column_config.NumberColumn(
                            col.title(),
                            help=f"Total de {col.split('-')[-1].lower()} no período",
                            step=1,
                            format="R$ %.2f",
                        )
                        for col in df_fat.columns
                    },
                )
                c1.area_chart(
                    df_fat.transpose(),
                    width=500,
                    use_container_width=True,
                    y="acumulado" if apenas_acumulado else None,
                )
                c1.area_chart(
                    df_daily.transpose(),
                    use_container_width=True,
                    y="acumulado" if apenas_acumulado else None,
                )
                c1.dataframe(
                    df_daily,
                    column_config={
                        col: st.column_config.NumberColumn(
                            col.split("-")[-1].title(),
                            help=f"Total vendido {col.split('-')[-1].lower()} no período",
                            step=1,
                            format="R$ %.2f",
                        )
                        for col in df_daily.columns
                    },
                    use_container_width=True,
                )

                c1.subheader("Vendas por período do dia")
                c1.area_chart(
                    df_period.transpose(),
                    use_container_width=True,
                    y="acumulado" if apenas_acumulado else None,
                )
            with c2:
                c_c1, c_c2 = c2.columns(2, gap="medium")
                with c_c1:
                    tile = c_c1.container(border=True)
                    tile.metric(
                        "Lucro Liquido",
                        value=f"R$ {round(lucro_liquido, 2)}",
                        delta=f"{round((lucro_liquido / receita_bruta if receita_bruta else 1) * 100)} %",
                    )
                    tile = c_c1.container(border=True)
                    tile.metric(
                        "Receitas - Despesas",
                        value=f"R$ {round(receita_menos_descontos - despesas_admnistrativas, 2)}",
                        delta=f"{round(((receita_menos_descontos - despesas_admnistrativas) / despesas_admnistrativas if despesas_admnistrativas else 1) * 100)} %",
                        delta_color="normal",
                    )

                    ticket_medio_delta = round(
                        (
                            round(receita_menos_descontos / total_vendas, 2)
                            / round(despesas_admnistrativas / total_vendas, 2)
                        )
                    )
                    tile = c_c1.container(border=True)
                    tile.metric(
                        "Ticket Médio",
                        value=f"R$ {round(receita_menos_descontos / total_vendas, 2)}",
                        delta=f"{ticket_medio_delta} %",
                        delta_color="inverse"
                        if ticket_medio_delta <= 2
                        else "off"
                        if ticket_medio_delta < 3
                        else "normal",
                        help="É o valor médio recebido por cliente em cada compra, calculado dividindo o total das vendas pelo número de vendas realizadas",
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

                    _cmv_delta = round(
                        custo_mercadoria_vendida / receita_menos_descontos * 100, 2
                    )
                    tile.metric(
                        "CMV Sobre Receita",
                        value=f"R$ {round(lucro_bruto, 2)}",
                        delta=f"{_cmv_delta} %",
                        delta_color="inverse" if _cmv_delta > 50 else "normal",
                    )

                    tile = c_c2.container(border=True)
                    custo_ticket_delta = round(
                        (
                            round(despesas_admnistrativas / total_vendas, 2)
                            / round(receita_menos_descontos / total_vendas, 2)
                        )
                        * 100
                    )
                    tile.metric(
                        "Custo Ticket",
                        value=f"R$ {round(despesas_admnistrativas / total_vendas, 2)}",
                        delta=f"{custo_ticket_delta} %",
                        delta_color="inverse" if custo_ticket_delta > 30 else "normal",
                        help="Representa o gasto médio em despesas operacionais para realizar cada venda. É calculado dividindo as despesas operacionais pelo número total de vendas realizadas.",
                    )
                fig = px.pie(
                    df_daily.transpose(),
                    names=[day.split("-")[-1] for day in df_daily.columns],
                    values="acumulado",
                    title=f"Vendas por dia da semana",
                )
                c2.plotly_chart(fig, use_container_width=True)

                fig = px.pie(
                    df_period.transpose(),
                    names=[period for period in df_period.columns],
                    values="acumulado",
                    title=f"Vendas por período do dia",
                )
                c2.plotly_chart(fig, use_container_width=True)
            st.dataframe(
                        df_period,
                        column_config={
                            col: st.column_config.NumberColumn(
                                col.split("-")[-1].title(),
                                help=f"Total vendido {col.split('-')[-1].lower()} no horário",
                                step=1,
                                format="R$ %.2f",
                            )
                            for col in df_daily.columns
                        },
                        use_container_width=True,
                    )
        with st.expander("Resumo Fidelidade"):
            show_customers = st.slider(
                "Visualizar o top:",
                min_value=1,
                max_value=100,
                value=10,
                key="customers",
            )
            st.subheader(f"TOP {show_customers} CLIENTES")
            st.dataframe(df_clientes.head(show_customers))
            st.bar_chart(
                df_clientes.head(show_customers),
                y="acumulado" if apenas_acumulado else None,
                use_container_width=True,
            )

        with st.expander("Resumo Produtos e Serviços"):
            show_items = st.slider(
                "Visualizar o top:",
                min_value=1,
                max_value=100,
                value=10,
                key="items",
            )
            i_c1, i_c2 = st.columns(2)
            with i_c1:
                i_c1.subheader(f"TOP {show_items} PRODUTOS MAIS VENDIDOS")
                i_c1.dataframe(df_produtos.head(show_items))
                i_c1.area_chart(
                    df_produtos.head(show_items),
                    y="acumulado" if apenas_acumulado else None,
                    use_container_width=True,
                )

            with i_c2:
                i_c2.subheader(f"TOP {show_items} SERVIÇOS MAIS VENDIDOS")
                i_c2.dataframe(df_servicos.head(show_items))
                i_c2.area_chart(
                    df_servicos.head(show_items),
                    y="acumulado" if apenas_acumulado else None,
                    use_container_width=True,
                )
