from datetime import datetime
import time
from zoneinfo import ZoneInfo

FUSO_SP = ZoneInfo("America/Sao_Paulo")
DENOMINACOES = (100, 50, 20, 10)


def agora_sp() -> datetime:
    return datetime.now(FUSO_SP)


def solicitar_inteiro_nao_negativo(mensagem: str) -> int:
    while True:
        try:
            valor = int(input(mensagem))
            if valor < 0:
                print("Por favor, insira um número inteiro maior ou igual a zero.")
                continue
            return valor
        except ValueError:
            print("Por favor, insira apenas valores inteiros.")


def abastecer_estoque(estoque: dict[int, int]) -> None:
    print("\n--- Abastecer ATM ---")
    for denom in (10, 20, 50, 100):
        qtd = solicitar_inteiro_nao_negativo(
            f"Quantas notas de R${denom} deseja acrescentar? "
        )
        estoque[denom] += qtd
    print("\nNotas atualizadas com sucesso!")


def mostrar_estoque(estoque: dict[int, int]) -> None:
    print("\n--- Notas disponíveis ---")
    for denom in (10, 20, 50, 100):
        print(f"Quantidade de notas de R${denom}: {estoque[denom]}")


def calcular_saque(
    estoque: dict[int, int], valor: int
) -> tuple[bool, dict[int, int]]:
    restante = valor
    entrega: dict[int, int] = {}

    for denom in DENOMINACOES:
        usadas = min(estoque[denom], restante // denom)
        entrega[denom] = usadas
        restante -= usadas * denom

    if restante != 0:
        return False, {}

    for denom in DENOMINACOES:
        estoque[denom] -= entrega[denom]

    return True, entrega


def realizar_saque(estoque: dict[int, int]) -> None:
    print("\n--- Saque ---")
    try:
        valor = int(input("Qual valor deseja sacar? "))
    except ValueError:
        print("Por favor, insira apenas valores inteiros.")
        return

    if valor <= 0:
        print("Valor inválido para saque.")
        return

    sucesso, entrega = calcular_saque(estoque, valor)
    if not sucesso:
        print("Não é possível sacar esse valor com as notas disponíveis.")
        return

    momento = agora_sp()
    time.sleep(0.8)
    print(f"\nValor sacado: R${valor}")
    print(f"Data: {momento.strftime('%d/%m/%y')}")
    print(f"Horário: {momento.strftime('%H:%M')}")
    print("\nSaque realizado com sucesso! Notas entregues:")

    alguma_nota = False
    for denom in DENOMINACOES:
        if entrega[denom] > 0:
            print(f"R${denom}: {entrega[denom]}")
            alguma_nota = True

    if not alguma_nota:
        print("Nenhuma nota foi entregue.")


def executar_simulador() -> None:
    estoque = {10: 0, 20: 0, 50: 0, 100: 0}

    print("-" * 57)
    print("Simulador de Cash Dispenser (ATM)")
    print("-" * 57)

    # Abastecimento inicial obrigatório (pelo menos 1 nota)
    while sum(estoque.values()) < 1:
        print("\nPrimeiro abasteça o caixa (mínimo de 1 nota no total).")
        abastecer_estoque(estoque)

    while True:
        momento = agora_sp()
        print(f"\nOpções de pagamento - {momento.strftime('%d/%m/%y')}")
        print("1 - Mostrar quantidade de notas disponíveis de cada valor")
        print("2 - Abastecer ATM com quantidade de notas para cada valor")
        print("3 - Sacar dinheiro no ATM")
        print("0 - Sair")

        opc = input("\nEscolha o que deseja fazer: ").strip()

        if opc == "0":
            print("Encerrando simulador...")
            break
        if opc == "1":
            mostrar_estoque(estoque)
        elif opc == "2":
            abastecer_estoque(estoque)
        elif opc == "3":
            realizar_saque(estoque)
        else:
            print("\nOpção inválida.")


if __name__ == "__main__":
    executar_simulador()