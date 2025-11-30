from datetime import date
from decimal import Decimal
from typing import Dict

from app.services.faturamento import buscar_faturamento

def calcular_metricas(month: date, headers: tuple) -> Dict:
    """
    Calculate all business metrics from faturamento data.
    
    Args:
        month (date): The month to fetch data for.
        headers (tuple): Authentication headers.

    Returns:
        Dict: Dictionary with all calculated metrics.
    """
    # Get raw faturamento data
    faturamento_data = buscar_faturamento(month, headers)
    
    # Extract raw values
    receitas = Decimal(str(faturamento_data['receitas']))
    despesas = Decimal(str(faturamento_data['despesas']))
    descontos = Decimal(str(faturamento_data['descontos']))
    cmv = Decimal(str(faturamento_data['cmv']))
    vendas = faturamento_data['vendas']
    
    # Calculate intermediate values
    receita_menos_descontos = receitas - descontos
    despesas_totais = despesas + cmv
    
    # Calculate main metrics
    lucro_liquido = (receita_menos_descontos - despesas_totais).quantize(Decimal('0.01'))
    receitas_menos_despesas = (receita_menos_descontos - despesas).quantize(Decimal('0.01'))
    
    # Calculate percentages and ratios
    lucro_liquido_percent = (lucro_liquido / receitas * 100).quantize(Decimal('0.01')) if receitas > 0 else Decimal('0')
    receitas_menos_despesas_percent = (receitas_menos_despesas / despesas * 100).quantize(Decimal('0.01')) if despesas > 0 else Decimal('0')
    
    # Calculate ticket metrics
    ticket_medio = (receita_menos_descontos / vendas).quantize(Decimal('0.01')) if vendas > 0 else Decimal('0')
    custo_ticket = (despesas / vendas).quantize(Decimal('0.01')) if vendas > 0 else Decimal('0')
    
    # Calculate ticket percentages (using the same logic as frontend)
    ticket_medio_percent = round(
        (ticket_medio / custo_ticket) if custo_ticket > 0 else Decimal('0')
    )
    custo_ticket_percent = round(
        (custo_ticket / ticket_medio) * 100 if ticket_medio > 0 else Decimal('0')
    )
    
    # Calculate other percentages
    descontos_sobre_receita = descontos.quantize(Decimal('0.01'))
    descontos_sobre_receita_percent = (descontos / receitas * 100).quantize(Decimal('0.01')) if receitas > 0 else Decimal('0')
    
    cmv_sobre_receita = lucro_bruto = (receita_menos_descontos - cmv).quantize(Decimal('0.01'))
    cmv_sobre_receita_percent = (cmv / receita_menos_descontos * 100).quantize(Decimal('0.01')) if receita_menos_descontos > 0 else Decimal('0')
    
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
