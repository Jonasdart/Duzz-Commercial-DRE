from datetime import date
from typing import List, Dict
from models import CommonHeaders
from models.payments import Payment
from models.responses import FaturamentoResponse
from models.sales import Sale
from models.stocks import Stock
from models.bills import Bills
from models.enums import PaymentsMethods, ReferenceTable
import calendar
from decimal import Decimal


# Fix imports for API helpers
from helpers.api import get_payments, get_sales, get_stock_by_month, get_bills

days = [
    "Segunda",
    "Terça",
    "Quarta",
    "Quinta",
    "Sexta",
    "Sábado",
    "Domingo",
]

periods = {
    "manha": ((6, 0), (11, 59)),
    "tarde": ((12, 0), (17, 59)),
    "noite": ((18, 0), (23, 59)),
    "madrugada": ((0, 0), (5, 59)),
}

def get_faturamento_data(
    payments: List[Payment],
    sales: List[Sale],
    stocks: List[Stock],
    bills_to_pay: List[Bills],
    month: date
) -> FaturamentoResponse:
    revenues: Decimal = Decimal(0)
    discounts: Decimal = Decimal(0)
    expenses: Decimal = Decimal(0)
    cogs = Decimal(0)
    daily = {day: Decimal(0) for day in days}
    by_period = {period: Decimal(0) for period in periods}
    by_payment_methods = {payment: Decimal(0) for payment in PaymentsMethods.__members__}
    for stock in stocks:
        for move in stock.outs.moves:
            if move.moment.date() >= month and move.moment.date() <= month.replace(
                day=calendar.monthrange(month.year, month.month)[-1]
            ):
                cogs += Decimal(move.value)

    for sale in sales:
        for period in periods:
            if (
                sale.moment.hour >= periods[period][0][0]
                and sale.moment.hour <= periods[period][1][0]
            ):
                by_period[period] += Decimal(sale.value + sale.discount)

        daily[days[sale.moment.weekday()]] += Decimal(sale.value + sale.discount)

    for payment in payments:
        if payment.reference_table is ReferenceTable.SALES:
            revenues += Decimal(payment.value)
            try:
                sale = [sale for sale in sales if sale.id == payment.reference_id][0]
            except IndexError:
                continue
            revenues += Decimal(sale.discount)
            discounts += Decimal(sale.discount)
            by_payment_methods[payment.payment_method.name] += Decimal(payment.value)

        if payment.reference_table is ReferenceTable.BILLS_TO_PAY:
            for bill in bills_to_pay:
                if (
                    bill.id == payment.reference_id
                    and bill.reference_table is not ReferenceTable.STOCK_ENTRIES
                ):
                    expenses += Decimal(payment.value)

    return FaturamentoResponse(**{
        "daily": {day: daily.get(day, 0) for day in days},
        "by_payment_methods": by_payment_methods,
        "by_periods": by_period,
        "receitas": revenues,
        "despesas": expenses,
        "descontos": discounts,
        "cmv": cogs,
        "vendas": len(sales),
    })

def buscar_faturamento(month: date, headers: CommonHeaders) -> FaturamentoResponse:
    """
    Fetch faturamento data for a given month.

    Args:
        month (date): The month to fetch data for.
        headers (tuple): Authentication headers.

    Returns:
        Dict: Processed faturamento data.
    """
    payments: List[Payment] = get_payments(month, headers.get_tuple())
    sales: List[Sale] = get_sales(month, headers.get_tuple())
    stocks: List[Stock] = get_stock_by_month(month, headers.get_tuple())
    bills_to_pay: List[Bills] = get_bills(headers.get_tuple())

    return get_faturamento_data(payments, sales, stocks, bills_to_pay, month)
