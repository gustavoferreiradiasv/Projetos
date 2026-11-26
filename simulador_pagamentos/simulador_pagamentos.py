import calendar
from datetime import datetime, timedelta
import math
from zoneinfo import ZoneInfo

FUSO_SP = ZoneInfo("America/Sao_Paulo")
TAXA_MDR_DEBITO = 0.01   # 1%
TAXA_MDR_CREDITO = 0.05  # 5%


def agora_sp() -> datetime:
    return datetime.now(FUSO_SP)


def proximo_dia_util(data_base: datetime | None = None, dias_apos: int = 1) -> str:
    if data_base is None:
        data_base = agora_sp()

    proximo = data_base + timedelta(days=dias_apos)
    while proximo.weekday() >= 5:  # 5 = Sábado, 6 = Domingo
        proximo += timedelta(days=1)

    return proximo.strftime("%d/%m/%Y")


def adicionar_meses(data_base: datetime, meses: int) -> datetime:
    mes = data_base.month + meses
    ano = data_base.year + (mes - 1) // 12
    mes = ((mes - 1) % 12) + 1
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    dia = min(data_base.day, ultimo_dia)
    return data_base.replace(year=ano, month=mes, day=dia)


def calcular_parcelas(valor_total: float, qtd_parcelas: int) -> list[float]:
    if qtd_parcelas == 3:
        primeira = float(math.ceil(valor_total / 3))
        segunda = math.floor((valor_total - primeira) / 2) + 0.5
        terceira = round(valor_total - primeira - segunda, 2)
        return [primeira, segunda, terceira]

    base = round(valor_total / qtd_parcelas, 2)
    parcelas = [base for _ in range(qtd_parcelas)]
    diferenca = round(valor_total - sum(parcelas), 2)
    parcelas[0] = round(parcelas[0] + diferenca, 2)
    return parcelas


def exibir_resumo_transacao(
    momento: datetime,
    descricao_meio: str,
    valor_bruto: float,
    taxa_mdr: float,
) -> tuple[float, float]:
    valor_mdr = round(valor_bruto * taxa_mdr, 2)
    valor_liquido = round(valor_bruto - valor_mdr, 2)

    print(f"\nData da compra: {momento.strftime('%d/%m/%Y')}")
    print(f"Hora da compra: {momento.strftime('%H:%M:%S')}")
    print(f"Meio de pagamento: {descricao_meio}")
    print(f"Valor da compra: R${valor_bruto:.2f}")
    print(f"Valor do MDR (taxa de transação): R${valor_mdr:.2f}")
    print(f"Valor líquido: R${valor_liquido:.2f}")
    return valor_mdr, valor_liquido


def processar_debito(valor_compra: float, momento: datetime) -> None:
    exibir_resumo_transacao(momento, "1 - Cartão de débito", valor_compra, TAXA_MDR_DEBITO)
    print("Dia de crédito:", proximo_dia_util(momento, dias_apos=1))


def processar_credito_avista(valor_compra: float, momento: datetime) -> None:
    exibir_resumo_transacao(momento, "2 - Cartão de crédito", valor_compra, TAXA_MDR_CREDITO)
    print("Dia de crédito:", proximo_dia_util(momento, dias_apos=30))


def processar_credito_parcelado(valor_compra: float, momento: datetime) -> None:
    while True:
        qp = input("Digite em quantas vezes deseja parcelar (2 ou 3): ").strip()
        if qp in {"2", "3"}:
            qtd_parcelas = int(qp)
            break
        print("\nMínimo de parcelas = 2 | Máximo de parcelas = 3")

    exibir_resumo_transacao(
        momento,
        "3 - Pagamento crédito parcelado",
        valor_compra,
        TAXA_MDR_CREDITO,
    )

    parcelas = calcular_parcelas(valor_compra, qtd_parcelas)
    for idx, valor_parcela in enumerate(parcelas, start=1):
        data_parcela = adicionar_meses(momento, idx - 1)
        dia_credito = proximo_dia_util(data_parcela, dias_apos=30)

        print(f"\nParcela {idx}/{qtd_parcelas}")
        print(f"Valor da parcela: R${valor_parcela:.2f}")
        print(f"Data de crédito: {dia_credito}")


def executar_caixa() -> None:
    print("-" * 57)
    print("Simulador de Meio de Pagamento")
    print("-" * 57)

    while True:
        entrada = input("\nDigite o valor da venda (ou 0 para fechar o caixa): ").strip()
        try:
            valor_compra = float(entrada.replace(",", "."))
        except ValueError:
            print("\nPor favor, digite um valor numérico.")
            continue

        if valor_compra < 0:
            print("\nO valor da venda não pode ser negativo.")
            continue

        if valor_compra == 0:
            print("\nCaixa fechado.")
            break

        while True:
            print("\nOpções de pagamento")
            print("1 - Pagamento débito")
            print("2 - Pagamento crédito")
            print("3 - Pagamento crédito parcelado")
            print("9 - Cancelar compra")
            opc = input("\nEscolha a forma de pagamento: ").strip()

            if opc in {"1", "2", "3", "9"}:
                break
            print("\nOpção inválida.")

        if opc == "9":
            print("\nVocê cancelou a operação atual!")
            break

        momento = agora_sp()
        if opc == "1":
            processar_debito(valor_compra, momento)
        elif opc == "2":
            processar_credito_avista(valor_compra, momento)
        elif opc == "3":
            processar_credito_parcelado(valor_compra, momento)


if __name__ == "__main__":
    executar_caixa()
