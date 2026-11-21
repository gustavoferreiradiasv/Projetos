# Projeto CRUD em C com MySQL

Aplicação de console desenvolvida em **linguagem C** para realizar operações básicas de banco de dados (**CRUD**: *Create*, *Read*, *Update* e *Delete*) utilizando a API nativa do **MySQL C Connector** (`libmysql`).

## Estrutura do Projeto

- `crud.c`: Código-fonte principal contendo a conexão com o banco de dados e as rotinas de cadastro, consulta, atualização e remoção.
- `Projeto2.dev`: Arquivo de configuração do projeto para a IDE **Dev-C++**.
- `Makefile.win`: Script de compilação gerado para ambiente Windows (MinGW).

## Pré-requisitos

Para compilar e executar este projeto localmente, você precisará de:

1. **Compilador C** (ex.: MinGW / GCC via Dev-C++).
2. **Servidor MySQL** ativo (local ou remoto).
3. **MySQL C Connector** (`libmysql`), com os diretórios `include/` (cabeçalhos como `mysql.h`) e `lib/` (`libmysql.lib` e `libmysql.dll`) configurados no compilador.

> **Nota:** As pastas `include/`, `lib/` e as DLLs de terceiros (`libmysql.dll`, `libcrypto-3-x64.dll`, `libssl-3-x64.dll`) não foram incluídas neste repositório para manter o versionamento leve.

## Como Compilar e Executar

1. Abra o arquivo `Projeto2.dev` no **Dev-C++** (ou utilize o `Makefile.win` via linha de comando com `mingw32-make`).
2. Verifique nas opções do projeto (*Project Options > Directories*) se os caminhos de **Include** e **Libraries** apontam para a pasta onde o MySQL C Connector está instalado no seu computador.
3. Confira as credenciais de conexão (host, usuário, senha e nome do banco de dados) definidas em `crud.c`.
4. Compile e execute o projeto (`F11` no Dev-C++), garantindo que a `libmysql.dll` esteja acessível no diretório do executável ou no `PATH` do sistema.