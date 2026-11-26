# Simulador de Cash Dispenser (ATM)

Simulador de caixa eletrônico (ATM) em Python via terminal, com controle de estoque de cédulas (R$10, R$20, R$50 e R$100), abastecimento e cálculo de saque usando abordagem gulosa das maiores notas disponíveis.

## Funcionalidades
- Abastecimento inicial e reposição de notas de R$10, R$20, R$50 e R$100.
- Consulta da quantidade atual de cédulas disponíveis.
- Cálculo de saque priorizando notas de maior valor e exibindo data e horário (`America/Sao_Paulo`).
- Validação de entradas inválidas ou valores impossíveis de compor com o estoque atual.

## Como executar
```bash
python cash_dispenser.py
