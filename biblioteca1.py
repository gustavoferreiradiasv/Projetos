import csv
import json
import os
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta

# ----------------------------------------------------------------------
# Configurações
# ----------------------------------------------------------------------
PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DADOS = os.path.join(PASTA, "biblioteca.json")
ARQUIVO_CSV = os.path.join(PASTA, "livros_exportados.csv")

PRAZO_EMPRESTIMO_DIAS = 14
MAX_RENOVACOES = 2
MULTA_POR_DIA = 1.00
ANO_ATUAL = date.today().year


# ----------------------------------------------------------------------
# Modelo
# ----------------------------------------------------------------------
@dataclass
class Livro:
    id: int
    titulo: str
    autor: str
    ano: int
    genero: str = "Não informado"
    disponivel: bool = True
    emprestado_para: str | None = None
    data_emprestimo: str | None = None
    data_prevista: str | None = None
    renovacoes: int = 0

    def dias_atraso(self, hoje: date | None = None) -> int:
        """Quantos dias o livro está atrasado (0 se não estiver)."""
        if self.disponivel or not self.data_prevista:
            return 0
        hoje = hoje or date.today()
        previsto = date.fromisoformat(self.data_prevista)
        return max((hoje - previsto).days, 0)

    def multa(self, hoje: date | None = None) -> float:
        return self.dias_atraso(hoje) * MULTA_POR_DIA


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def normalizar(texto: str) -> str:
    """Minúsculas e sem acentos, para buscas mais tolerantes."""
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def formatar_data(iso: str | None) -> str:
    if not iso:
        return "-"
    return date.fromisoformat(iso).strftime("%d/%m/%Y")


def formatar_dinheiro(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def linha(char: str = "=", tamanho: int = 60) -> None:
    print(char * tamanho)


def pausar() -> None:
    input("\nPressione ENTER para continuar...")


# ----------------------------------------------------------------------
# Leitura de dados do usuário (com validação)
# ----------------------------------------------------------------------
def ler_texto(mensagem: str, obrigatorio: bool = True, padrao: str | None = None) -> str:
    while True:
        sufixo = f" [{padrao}]" if padrao else ""
        valor = input(f"{mensagem}{sufixo}: ").strip()
        if not valor and padrao is not None:
            return padrao
        if valor or not obrigatorio:
            return valor
        print("  Este campo não pode ficar vazio.")


def ler_inteiro(mensagem: str, minimo: int, maximo: int, padrao: int | None = None) -> int:
    while True:
        sufixo = f" [{padrao}]" if padrao is not None else ""
        valor = input(f"{mensagem}{sufixo}: ").strip()
        if not valor and padrao is not None:
            return padrao
        try:
            numero = int(valor)
        except ValueError:
            print("  Digite um número inteiro válido.")
            continue
        if minimo <= numero <= maximo:
            return numero
        print(f"  Digite um valor entre {minimo} e {maximo}.")


def confirmar(mensagem: str) -> bool:
    while True:
        resp = input(f"{mensagem} (s/n): ").strip().lower()
        if resp in ("s", "sim"):
            return True
        if resp in ("n", "nao", "não"):
            return False
        print("  Responda com 's' ou 'n'.")


# ----------------------------------------------------------------------
# Biblioteca (lógica + persistência)
# ----------------------------------------------------------------------
class Biblioteca:
    def __init__(self, caminho: str = ARQUIVO_DADOS):
        self.caminho = caminho
        self.livros: list[Livro] = []
        self.historico: list[dict] = []
        self.carregar()

    # --- persistência ---------------------------------------------------
    def carregar(self) -> None:
        if not os.path.exists(self.caminho):
            self._dados_iniciais()
            self.salvar()
            return
        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self.livros = [Livro(**item) for item in dados["livros"]]
            self.historico = dados.get("historico", [])
        except (json.JSONDecodeError, KeyError, TypeError):
            backup = self.caminho + ".corrompido"
            os.replace(self.caminho, backup)
            print(f"Arquivo de dados inválido. Cópia guardada em: {backup}")
            self._dados_iniciais()
            self.salvar()

    def salvar(self) -> None:
        """Salva de forma segura (arquivo temporário + substituição)."""
        dados = {
            "livros": [asdict(l) for l in self.livros],
            "historico": self.historico,
        }
        temporario = self.caminho + ".tmp"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        os.replace(temporario, self.caminho)

    def _dados_iniciais(self) -> None:
        self.livros = [
            Livro(1, "Meridiano de Sangue", "Cormac McCarthy", 1985, "Romance"),
            Livro(2, "O Sol é para Todos", "Harper Lee", 1960, "Romance"),
        ]
        self.historico = []

    # --- consultas --------------------------------------------------------
    def proximo_id(self) -> int:
        return max((l.id for l in self.livros), default=0) + 1

    def obter(self, livro_id: int) -> Livro | None:
        return next((l for l in self.livros if l.id == livro_id), None)

    def buscar(self, termo: str) -> list[Livro]:
        """Busca por título, autor ou gênero (parcial, sem acento)."""
        t = normalizar(termo)
        return [
            l for l in self.livros
            if t in normalizar(l.titulo)
            or t in normalizar(l.autor)
            or t in normalizar(l.genero)
        ]

    def titulo_existe(self, titulo: str, autor: str) -> bool:
        return any(
            normalizar(l.titulo) == normalizar(titulo)
            and normalizar(l.autor) == normalizar(autor)
            for l in self.livros
        )

    # --- operações --------------------------------------------------------
    def cadastrar(self, titulo: str, autor: str, ano: int, genero: str) -> Livro:
        livro = Livro(self.proximo_id(), titulo, autor, ano, genero)
        self.livros.append(livro)
        self.salvar()
        return livro

    def remover(self, livro: Livro) -> None:
        self.livros.remove(livro)
        self.salvar()

    def emprestar(self, livro: Livro, leitor: str) -> None:
        hoje = date.today()
        livro.disponivel = False
        livro.emprestado_para = leitor
        livro.data_emprestimo = hoje.isoformat()
        livro.data_prevista = (hoje + timedelta(days=PRAZO_EMPRESTIMO_DIAS)).isoformat()
        livro.renovacoes = 0
        self.salvar()

    def renovar(self, livro: Livro) -> None:
        previsto = date.fromisoformat(livro.data_prevista)
        livro.data_prevista = (previsto + timedelta(days=PRAZO_EMPRESTIMO_DIAS)).isoformat()
        livro.renovacoes += 1
        self.salvar()

    def devolver(self, livro: Livro) -> float:
        multa = livro.multa()
        self.historico.append({
            "livro_id": livro.id,
            "titulo": livro.titulo,
            "leitor": livro.emprestado_para,
            "emprestado_em": livro.data_emprestimo,
            "devolvido_em": date.today().isoformat(),
            "multa": multa,
        })
        livro.disponivel = True
        livro.emprestado_para = None
        livro.data_emprestimo = None
        livro.data_prevista = None
        livro.renovacoes = 0
        self.salvar()
        return multa

    def exportar_csv(self, caminho: str = ARQUIVO_CSV) -> str:
        campos = ["id", "titulo", "autor", "ano", "genero", "disponivel", "emprestado_para",
                  "data_emprestimo", "data_prevista"]
        with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
            escritor = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore", delimiter=";")
            escritor.writeheader()
            for l in self.livros:
                escritor.writerow(asdict(l))
        return caminho


# ----------------------------------------------------------------------
# Interface (funções de tela)
# ----------------------------------------------------------------------
def mostrar_livro(l: Livro) -> None:
    print(f"ID: {l.id}")
    print(f"Título: {l.titulo}")
    print(f"Autor: {l.autor}")
    print(f"Ano: {l.ano}")
    print(f"Gênero: {l.genero}")
    if l.disponivel:
        print("Situação: Disponível")
    else:
        print(f"Situação: Emprestado para {l.emprestado_para}")
        print(f"Emprestado em: {formatar_data(l.data_emprestimo)}")
        print(f"Devolução prevista: {formatar_data(l.data_prevista)}")
        atraso = l.dias_atraso()
        if atraso:
            print(f"ATRASADO há {atraso} dia(s) - multa atual: {formatar_dinheiro(l.multa())}")
    linha("-")


def mostrar_tabela(livros: list[Livro]) -> None:
    if not livros:
        print("Nenhum livro encontrado.")
        return
    print(f"{'ID':<4} {'Título':<28} {'Autor':<20} {'Ano':<5} {'Situação'}")
    linha("-", 78)
    for l in livros:
        titulo = l.titulo if len(l.titulo) <= 27 else l.titulo[:24] + "..."
        autor = l.autor if len(l.autor) <= 19 else l.autor[:16] + "..."
        if l.disponivel:
            situacao = "Disponível"
        elif l.dias_atraso():
            situacao = f"Atrasado ({l.dias_atraso()}d)"
        else:
            situacao = "Emprestado"
        print(f"{l.id:<4} {titulo:<28} {autor:<20} {l.ano:<5} {situacao}")
    linha("-", 78)
    print(f"Total: {len(livros)} livro(s)")


def escolher_livro(bib: Biblioteca, mensagem: str) -> Livro | None:
    """Busca por termo ou ID; se houver vários resultados, pede o ID."""
    entrada = ler_texto(f"{mensagem} (título, autor ou ID)")

    if entrada.isdigit():
        livro = bib.obter(int(entrada))
        if livro:
            return livro

    resultados = bib.buscar(entrada)
    if not resultados:
        print("Nenhum livro encontrado.")
        return None
    if len(resultados) == 1:
        return resultados[0]

    print("\nVários livros encontrados:")
    mostrar_tabela(resultados)
    ids = {l.id for l in resultados}
    while True:
        escolha = input("Digite o ID desejado (ou ENTER para cancelar): ").strip()
        if not escolha:
            return None
        if escolha.isdigit() and int(escolha) in ids:
            return bib.obter(int(escolha))
        print("  ID inválido.")


# --- ações do menu ------------------------------------------------------
def acao_listar(bib: Biblioteca) -> None:
    print("\nOrdenar por: 1 - Título | 2 - Autor | 3 - Ano | 4 - ID")
    ordem = ler_inteiro("Opção", 1, 4, padrao=4)
    chaves = {
        1: lambda l: normalizar(l.titulo),
        2: lambda l: normalizar(l.autor),
        3: lambda l: l.ano,
        4: lambda l: l.id,
    }
    print("\nFiltro: 1 - Todos | 2 - Só disponíveis | 3 - Só emprestados")
    filtro = ler_inteiro("Opção", 1, 3, padrao=1)

    livros = sorted(bib.livros, key=chaves[ordem])
    if filtro == 2:
        livros = [l for l in livros if l.disponivel]
    elif filtro == 3:
        livros = [l for l in livros if not l.disponivel]
    print()
    mostrar_tabela(livros)


def acao_cadastrar(bib: Biblioteca) -> None:
    titulo = ler_texto("Título do livro")
    autor = ler_texto("Autor")
    if bib.titulo_existe(titulo, autor):
        print("Esse livro (mesmo título e autor) já está cadastrado.")
        if not confirmar("Cadastrar mesmo assim?"):
            return
    ano = ler_inteiro("Ano de publicação", 1, ANO_ATUAL)
    genero = ler_texto("Gênero (opcional)", obrigatorio=False) or "Não informado"
    livro = bib.cadastrar(titulo, autor, ano, genero)
    print(f"Livro cadastrado com sucesso! (ID {livro.id})")


def acao_buscar(bib: Biblioteca) -> None:
    termo = ler_texto("Digite título, autor ou gênero")
    resultados = bib.buscar(termo)
    print()
    if not resultados:
        print("Nenhum livro encontrado.")
        return
    print(f"{len(resultados)} resultado(s):\n")
    for l in resultados:
        mostrar_livro(l)


def acao_alterar(bib: Biblioteca) -> None:
    livro = escolher_livro(bib, "Qual livro deseja alterar?")
    if not livro:
        return
    print()
    mostrar_livro(livro)
    print("O que deseja alterar?")
    print("1 - Título\n2 - Autor\n3 - Ano\n4 - Gênero\n0 - Cancelar")
    opcao = ler_inteiro("Opção", 0, 4)

    if opcao == 0:
        return
    if opcao == 1:
        livro.titulo = ler_texto("Novo título", padrao=livro.titulo)
    elif opcao == 2:
        livro.autor = ler_texto("Novo autor", padrao=livro.autor)
    elif opcao == 3:
        livro.ano = ler_inteiro("Novo ano", 1, ANO_ATUAL, padrao=livro.ano)
    elif opcao == 4:
        livro.genero = ler_texto("Novo gênero", padrao=livro.genero)
    bib.salvar()
    print("Alteração realizada!")


def acao_emprestar(bib: Biblioteca) -> None:
    livro = escolher_livro(bib, "Qual livro deseja emprestar?")
    if not livro:
        return
    if not livro.disponivel:
        print(f"Esse livro já está emprestado para {livro.emprestado_para} "
              f"(devolução prevista: {formatar_data(livro.data_prevista)}).")
        return
    leitor = ler_texto("Nome do leitor")
    bib.emprestar(livro, leitor)
    print(f"Livro emprestado para {leitor}! Devolução até {formatar_data(livro.data_prevista)}.")


def acao_devolver(bib: Biblioteca) -> None:
    livro = escolher_livro(bib, "Qual livro está sendo devolvido?")
    if not livro:
        return
    if livro.disponivel:
        print("Esse livro já está disponível (não consta como emprestado).")
        return
    multa = bib.devolver(livro)
    print("Livro devolvido com sucesso!")
    if multa > 0:
        print(f"Multa por atraso a pagar: {formatar_dinheiro(multa)}")


def acao_renovar(bib: Biblioteca) -> None:
    livro = escolher_livro(bib, "Qual empréstimo deseja renovar?")
    if not livro:
        return
    if livro.disponivel:
        print("Esse livro não está emprestado.")
    elif livro.dias_atraso():
        print("Não é possível renovar um livro em atraso. Devolva-o primeiro.")
    elif livro.renovacoes >= MAX_RENOVACOES:
        print(f"Limite de {MAX_RENOVACOES} renovações atingido.")
    else:
        bib.renovar(livro)
        print(f"Renovado! Nova devolução prevista: {formatar_data(livro.data_prevista)} "
              f"({livro.renovacoes}/{MAX_RENOVACOES} renovações).")


def acao_remover(bib: Biblioteca) -> None:
    livro = escolher_livro(bib, "Qual livro deseja remover?")
    if not livro:
        return
    if not livro.disponivel:
        print("Não é possível remover um livro que está emprestado.")
        return
    mostrar_livro(livro)
    if confirmar("Tem certeza que deseja remover este livro?"):
        bib.remover(livro)
        print("Livro removido com sucesso!")
    else:
        print("Remoção cancelada.")


def acao_emprestados(bib: Biblioteca) -> None:
    emprestados = [l for l in bib.livros if not l.disponivel]
    if not emprestados:
        print("Nenhum livro emprestado no momento.")
        return
    emprestados.sort(key=lambda l: l.data_prevista)
    print(f"{len(emprestados)} livro(s) emprestado(s):\n")
    for l in emprestados:
        mostrar_livro(l)


def acao_historico(bib: Biblioteca) -> None:
    if not bib.historico:
        print("Ainda não há devoluções registradas.")
        return
    print(f"{'Livro':<28} {'Leitor':<16} {'Emprestado':<11} {'Devolvido':<11} {'Multa'}")
    linha("-", 80)
    for h in reversed(bib.historico[-20:]):
        titulo = h["titulo"] if len(h["titulo"]) <= 27 else h["titulo"][:24] + "..."
        print(f"{titulo:<28} {h['leitor']:<16} {formatar_data(h['emprestado_em']):<11} "
              f"{formatar_data(h['devolvido_em']):<11} {formatar_dinheiro(h['multa'])}")
    linha("-", 80)
    print("(mostrando até as 20 devoluções mais recentes)")


def acao_estatisticas(bib: Biblioteca) -> None:
    total = len(bib.livros)
    disponiveis = sum(1 for l in bib.livros if l.disponivel)
    emprestados = total - disponiveis
    atrasados = [l for l in bib.livros if l.dias_atraso()]
    multa_pendente = sum(l.multa() for l in atrasados)

    print(f"Total de livros: {total}")
    print(f"Disponíveis: {disponiveis}")
    print(f"Emprestados: {emprestados}")
    print(f"Em atraso: {len(atrasados)} (multas acumuladas: {formatar_dinheiro(multa_pendente)})")

    if bib.livros:
        mais_antigo = min(bib.livros, key=lambda l: l.ano)
        mais_novo = max(bib.livros, key=lambda l: l.ano)
        print(f"Mais antigo: {mais_antigo.titulo} ({mais_antigo.ano})")
        print(f"Mais recente: {mais_novo.titulo} ({mais_novo.ano})")

        generos: dict[str, int] = {}
        for l in bib.livros:
            generos[l.genero] = generos.get(l.genero, 0) + 1
        print("\nLivros por gênero:")
        for genero, qtd in sorted(generos.items(), key=lambda x: -x[1]):
            print(f"  {genero}: {qtd}")

    if bib.historico:
        contagem: dict[str, int] = {}
        for h in bib.historico:
            contagem[h["titulo"]] = contagem.get(h["titulo"], 0) + 1
        popular = max(contagem, key=contagem.get)
        print(f"\nLivro mais emprestado: {popular} ({contagem[popular]}x)")
        print(f"Total de empréstimos concluídos: {len(bib.historico)}")


def acao_exportar(bib: Biblioteca) -> None:
    caminho = bib.exportar_csv()
    print(f"Arquivo CSV gerado em: {caminho}")


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
MENU = [
    ("1", "Mostrar os livros", acao_listar),
    ("2", "Cadastrar livro", acao_cadastrar),
    ("3", "Procurar livro", acao_buscar),
    ("4", "Alterar livro", acao_alterar),
    ("5", "Emprestar livro", acao_emprestar),
    ("6", "Devolver livro", acao_devolver),
    ("7", "Renovar empréstimo", acao_renovar),
    ("8", "Remover livro", acao_remover),
    ("9", "Livros emprestados / atrasados", acao_emprestados),
    ("10", "Histórico de empréstimos", acao_historico),
    ("11", "Estatísticas", acao_estatisticas),
    ("12", "Exportar para CSV", acao_exportar),
    ("0", "Sair", None),
]


def main() -> None:
    bib = Biblioteca()
    acoes = {codigo: funcao for codigo, _, funcao in MENU}

    while True:
        print()
        linha()
        print(" BIBLIOTECA ".center(60, "="))
        linha()
        atrasados = sum(1 for l in bib.livros if l.dias_atraso())
        if atrasados:
            print(f"  ATENÇÃO: {atrasados} livro(s) em atraso!")
        for codigo, texto, _ in MENU:
            print(f"{codigo:>3} - {texto}")
        linha("-")

        opcao = input("Digite a opção desejada: ").strip()

        if opcao == "0":
            print("Saindo da biblioteca... Até logo!")
            break
        if opcao not in acoes:
            print("Opção inválida.")
            continue

        print()
        try:
            acoes[opcao](bib)
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")
        except OSError as erro:
            print(f"Erro ao acessar o arquivo de dados: {erro}")
        pausar()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")