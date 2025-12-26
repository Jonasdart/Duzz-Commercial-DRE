from datetime import date
from decimal import Decimal, ROUND_HALF_UP # Importar ROUND_HALF_UP
from typing import Dict
from models import CommonHeaders

from services.faturamento import buscar_faturamento

def calcular_metricas(month: date, headers: CommonHeaders) -> Dict:
    """
    Calculate all business metrics from faturamento data.
    """
    # Helper para forçar 2 casas decimais sempre
    def to_money(value):
        if value is None:
            return Decimal('0.00')
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Get raw faturamento data
    fact = buscar_faturamento(month, headers)

    # Calculate intermediate values
    receita_menos_descontos = fact.receitas - fact.descontos
    despesas_totais = fact.despesas + fact.cmv
    
    # Calculate main metrics
    lucro_liquido = to_money(receita_menos_descontos - despesas_totais)
    receitas_menos_despesas = to_money(receita_menos_descontos - fact.despesas)
    
    # Calculate percentages and ratios (Multiplica por 100 ANTES de arredondar)
    lucro_liquido_percent = Decimal('0.00')
    if receita_menos_descontos > 0:
        lucro_liquido_percent = to_money(lucro_liquido / receita_menos_descontos * 100)
        
    receitas_menos_despesas_percent = Decimal('0.00')
    if receita_menos_descontos > 0:
        receitas_menos_despesas_percent = to_money(receitas_menos_despesas / receita_menos_descontos * 100)
    
    # Calculate ticket metrics
    ticket_medio = Decimal('0.00')
    if fact.vendas > 0:
        ticket_medio = to_money(receita_menos_descontos / fact.vendas)

    custo_ticket = Decimal('0.00')
    if fact.vendas > 0:
        custo_ticket = to_money(fact.despesas / fact.vendas)
    
    # Calculate ticket percentages
    # Substituído round() por to_money() para manter padrão Decimal
    ticket_medio_percent = Decimal('0.00')
    if custo_ticket > 0:
        ticket_medio_percent = to_money(ticket_medio / custo_ticket * 100)

    custo_ticket_percent = Decimal('0.00')
    if ticket_medio > 0:
        custo_ticket_percent = to_money(custo_ticket / ticket_medio * 100)
    
    # Calculate other percentages
    descontos_sobre_receita = to_money(fact.descontos)
    
    descontos_sobre_receita_percent = Decimal('0.00')
    if fact.receitas > 0:
        descontos_sobre_receita_percent = to_money(fact.descontos / fact.receitas * 100)
    
    cmv_sobre_receita = to_money(fact.cmv)
    
    cmv_sobre_receita_percent = Decimal('0.00')
    if receita_menos_descontos > 0:
        cmv_sobre_receita_percent = to_money(fact.cmv / receita_menos_descontos * 100)
    
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
