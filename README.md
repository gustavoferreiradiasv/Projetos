# 📂 Organizador Automático de Arquivos

Script em Python que organiza automaticamente os arquivos de uma pasta
(por exemplo, `Downloads`) em subpastas por categoria — Imagens,
Documentos, Planilhas, Vídeos, e assim por diante.

Feito para resolver um problema bem real: aquela pasta de Downloads
com 300 arquivos bagunçados. 😅

## ✨ Funcionalidades

- **Organização automática** por tipo de arquivo, com base em um `config.json` totalmente editável
- **Modo simulação** (`--dry-run`): mostra o que seria feito sem mover nada
- **Modo monitoramento** (`--watch`): fica rodando e organiza novos arquivos assim que eles chegam na pasta
- **Sem sobrescrever arquivos**: se já existe um arquivo com o mesmo nome, o novo é renomeado automaticamente (`arquivo (1).pdf`)
- **Log completo** de tudo que foi feito, salvo em `organizer.log`
- **Testado** com `pytest`

## 🚀 Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/organizador-automatico.git
cd organizador-automatico
```

### 2. (Opcional) Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Instale as dependências (só necessário para rodar os testes)

```bash
pip install -r requirements.txt
```

### 4. Execute

Organizar uma pasta:

```bash
python organizer.py --source ~/Downloads
```

Simular antes de organizar de verdade (recomendado na primeira vez):

```bash
python organizer.py --source ~/Downloads --dry-run
```

Deixar rodando e organizando automaticamente novos arquivos:

```bash
python organizer.py --source ~/Downloads --watch
```

## ⚙️ Personalizando as categorias

Edite o arquivo `config.json` para adicionar, remover ou criar novas categorias:

```json
{
    "Imagens": [".jpg", ".jpeg", ".png"],
    "MeusProjetos": [".psd", ".ai", ".fig"]
}
```

Qualquer extensão que não estiver no arquivo vai parar na pasta `Outros`.

## 🧪 Rodando os testes

```bash
pytest
```

## 🗂️ Estrutura do projeto

```
organizador-automatico/
├── organizer.py          # Script principal
├── config.json            # Categorias e extensões (editável)
├── requirements.txt        # Dependências (só para testes)
├── tests/
│   └── test_organizer.py  # Testes automatizados
├── .gitignore
├── LICENSE
└── README.md
```

## 🛠️ Tecnologias

- Python 3.8+ (apenas biblioteca padrão — sem dependências externas para rodar)
- `pytest` para os testes

## 💡 Possíveis melhorias futuras

- [ ] Interface gráfica simples (Tkinter)
- [ ] Suporte a regras por data de criação/modificação do arquivo
- [ ] Notificação por e-mail/Telegram ao organizar
- [ ] Empacotar como executável (`pyinstaller`)

## 📄 Licença

Este projeto está sob a licença MIT — veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Feito como projeto de portfólio, com foco em código limpo e organizado. Sugestões e PRs são bem-vindos!
