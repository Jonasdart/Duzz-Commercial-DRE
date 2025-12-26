from datetime import date
from decimal import Decimal
from typing import Dict
from models import CommonHeaders

from services.faturamento import buscar_faturamento

def calcular_metricas(month: date, headers: CommonHeaders) -> Dict:
    """
    Calculate all business metrics from faturamento data.
    
    Args:
        month (date): The month to fetch data for.
        headers (tuple): Authentication headers.

    Returns:
        Dict: Dictionary with all calculated metrics.
    """
    # Get raw faturamento data
    fact = buscar_faturamento(month, headers)

    # Calculate intermediate values
    receita_menos_descontos = fact.receitas - fact.descontos
    despesas_totais = fact.despesas + fact.cmv
    
    # Calculate main metrics
    lucro_liquido = (receita_menos_descontos - despesas_totais).quantize(Decimal('0.01'))
    receitas_menos_despesas = (receita_menos_descontos - fact.despesas).quantize(Decimal('0.01'))
    
    # Calculate percentages and ratios
    lucro_liquido_percent = (lucro_liquido / fact.receitas * 100).quantize(Decimal('0.01')) if fact.receitas > 0 else Decimal('0')
    receitas_menos_despesas_percent = (receitas_menos_despesas / fact.despesas * 100).quantize(Decimal('0.01')) if fact.despesas > 0 else Decimal('0')
    
    # Calculate ticket metrics
    ticket_medio = (receita_menos_descontos / fact.vendas).quantize(Decimal('0.01')) if fact.vendas > 0 else Decimal('0')
    custo_ticket = (fact.despesas / fact.vendas).quantize(Decimal('0.01')) if fact.vendas > 0 else Decimal('0')
    
    # Calculate ticket percentages (using the same logic as frontend)
    ticket_medio_percent = round(
        (ticket_medio / custo_ticket) if custo_ticket > 0 else Decimal('0')
    )
    custo_ticket_percent = round(
        (custo_ticket / ticket_medio) * 100 if ticket_medio > 0 else Decimal('0')
    )
    
    # Calculate other percentages
    descontos_sobre_receita = fact.descontos.quantize(Decimal('0.01'))
    descontos_sobre_receita_percent = (fact.descontos / fact.receitas * 100).quantize(Decimal('0.01')) if fact.receitas > 0 else Decimal('0')
    
    cmv_sobre_receita = lucro_bruto = (receita_menos_descontos - fact.cmv).quantize(Decimal('0.01'))
    cmv_sobre_receita_percent = (fact.cmv / receita_menos_descontos * 100).quantize(Decimal('0.01')) if receita_menos_descontos > 0 else Decimal('0')
    
    return {
        "lucro_liquido": {
            "valor": lucro_liquido,
            "porcentagem": lucro_liquido_percent
        },
        "receitas_menos_despesas": {
            "valor": receitas_menos_despesas,
            "porcentagem": receitas_menos_despesas_percent
        },
        "ticket_medio": {
            "valor": ticket_medio,
            "porcentagem": ticket_medio_percent
        },
        "descontos_sobre_receita": {
            "valor": descontos_sobre_receita,
            "porcentagem": descontos_sobre_receita_percent
        },
        "cmv_sobre_receita": {
            "valor": cmv_sobre_receita,
            "porcentagem": cmv_sobre_receita_percent
        },
        "custo_ticket": {
            "valor": custo_ticket,
            "porcentagem": custo_ticket_percent
        }
    }
