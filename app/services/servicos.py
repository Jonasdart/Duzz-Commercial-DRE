from datetime import date
from typing import Dict
from helpers.api import get_sales, get_service_data
from models import CommonHeaders
from models.responses import ServicosResponse

def buscar_servicos(month: date, headers: CommonHeaders) -> ServicosResponse:
    """
    Fetch service sales summary for a given month.

    Args:
        month (date): The month to fetch data for.
        headers (tuple): Authentication headers.

    Returns:
        Dict[str, float]: A dictionary with service names as keys and quantities sold as values.
    """
    sales = get_sales(month, headers.get_tuple())
    resumo = {}

    for sale in sales:
        for service_id, quantity in sale.services.items():
            service_data = get_service_data(int(service_id), headers.get_tuple())
            if service_data and hasattr(service_data, 'name'):
                service_name = service_data.name
                try:
                    resumo[service_name] += float(quantity)
                except KeyError:
                    resumo[service_name] = float(quantity)

    return ServicosResponse(services=resumo)
