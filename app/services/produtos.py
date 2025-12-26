from datetime import date
import calendar
from typing import List, Dict

from helpers.api import get_stock_by_month
from models import CommonHeaders
from models.responses import ProdutosResponse
from models.stocks import Stock

def buscar_produtos(month: date, headers: CommonHeaders) -> ProdutosResponse:
    """
    Fetch product sales summary for a given month.

    Args:
        month (date): The month to fetch data for.
        headers (tuple): Authentication headers.

    Returns:
        Dict[int, int]: A dictionary with product IDs as keys and quantities sold as values.
    """
    stocks: List[Stock] = get_stock_by_month(month, headers.get_tuple())
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

    return ProdutosResponse(products=resumo)