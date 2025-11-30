from datetime import date
from typing import Dict
from helpers.api import get_sales, get_service_data

def buscar_servicos(month: date, headers: tuple) -> Dict[str, float]:
    """
    Fetch service sales summary for a given month.

    Args:
        month (date): The month to fetch data for.
        headers (tuple): Authentication headers.

    Returns:
        Dict[str, float]: A dictionary with service names as keys and quantities sold as values.
    """
    sales = get_sales(month, headers)
    resumo = {}

    for sale in sales:
        for service_id, quantity in sale.services.items():
            service_data = get_service_data(int(service_id), headers)
            if service_data and hasattr(service_data, 'name'):
                service_name = service_data.name
                try:
                    resumo[service_name] += float(quantity)
                except KeyError:
                    resumo[service_name] = float(quantity)

    return resumo
