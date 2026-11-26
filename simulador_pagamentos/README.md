# Simulador de Meio de Pagamento

Simulador de terminal em Python para vendas no débito, crédito à vista e crédito parcelado (2x ou 3x), com cálculo automático de taxa MDR, valor líquido e datas de liquidação em dias úteis (`America/Sao_Paulo`).

## Funcionalidades
- **Débito:** aplica taxa MDR de 1% e calcula liquidação para o próximo dia útil (`D+1`).
- **Crédito à vista:** aplica taxa MDR de 5% e calcula liquidação para o próximo dia útil após 30 dias (`D+30`).
- **Crédito parcelado (2x ou 3x):** aplica taxa MDR de 5%, divide as parcelas e exibe o cronograma mensal de recebimento em dias úteis.
- **Validação de entradas:** aceita valores com vírgula ou ponto e ignora finais de semana no cálculo de liquidação.

## Como executar
```bash
python simulador_pagamentos.py
