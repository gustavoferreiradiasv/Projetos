# Sistema de Biblioteca em Python

Sistema de gerenciamento de biblioteca via terminal em Python, com persistência segura em JSON, busca sem acentos, controle de empréstimos, renovações, multas por atraso e exportação para CSV.

## Funcionalidades
- Cadastro, listagem com ordenação/filtro, busca (por título, autor ou gênero, ignorando acentos), alteração e remoção de livros.
- Controle de empréstimos (prazo padrão de 14 dias), renovações (até 2 vezes, bloqueadas se houver atraso) e devoluções com cálculo automático de multa (`R$ 1,00` por dia de atraso).
- Histórico das devoluções mais recentes e painel de estatísticas do acervo.
- Salvamento atômico em `biblioteca.json` (com backup automático se o arquivo estiver corrompido) e exportação em `livros_exportados.csv` (separado por `;` em UTF-8 BOM).

## Como executar
```bash
python biblioteca.py
