from datetime import date
from typing import Dict
from decimal import Decimal
from helpers.api import get_sales, get_customer_data
from models import CommonHeaders
from models.responses import FidelidadeResponse

def buscar_fidelidade(month: date, headers: CommonHeaders) -> FidelidadeResponse:
    """
    Fetch customer loyalty data for a given month.

    Args:
        month (date): The month to fetch data for.
        headers (tuple): Authentication headers.

    Returns:
        Dict[str, Decimal]: A dictionary with customer names as keys and total sales as values.
    """
    sales = get_sales(month, headers.get_tuple())
    resumo = {}

    for sale in sales:
        customer = get_customer_data(sale.customer, headers.get_tuple())
        if customer and hasattr(customer, 'get_full_name'):
            customer_name = customer.get_full_name()
            try:
                resumo[customer_name] += Decimal(str(sale.value))
            except KeyError:
                resumo[customer_name] = Decimal(str(sale.value))

    return FidelidadeResponse(customers=resumo)
