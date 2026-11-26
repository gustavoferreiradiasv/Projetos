/*
 * CRUD de clientes em C + MySQL (terminal) - versao para Dev-C++ (Windows)
 *
 * Salve como .c (Arquivo > Novo > Arquivo Fonte e salve como crud.c)
 * para o Dev-C++ compilar como C.
 *
 * Configuracao do projeto no Dev-C++ (veja o passo a passo na resposta):
 *   - Include:  <pasta do Connector/C>\include
 *   - Lib:      <pasta do Connector/C>\lib
 *   - Linker:   libmysql.lib  (ou -lmysql)
 *   - Copiar libmysql.dll para a pasta do executavel
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#include <windows.h>
#endif
#include <mysql.h>

/* ---------- Configuracao da conexao: ajuste aqui ---------- */
#define DB_HOST "localhost"
#define DB_USER "root"
#define DB_PASS "123456"
#define DB_NAME "crud_c"
#define DB_PORT 3306

#define TAM_NOME  101
#define TAM_EMAIL 101
#define TAM_TEL   21

/* ---------- Utilitarios ---------- */

static void pausar(void) {
#ifdef _WIN32
    system("pause");
#endif
}

static void ler_linha(const char *prompt, char *buf, size_t tam) {
    printf("%s", prompt);
    fflush(stdout);
    if (fgets(buf, (int)tam, stdin) == NULL) {
        buf[0] = '\0';
        return;
    }
    size_t n = strlen(buf);
    if (n > 0 && buf[n - 1] == '\n') {
        buf[n - 1] = '\0';
    } else {
        int c;
        while ((c = getchar()) != '\n' && c != EOF) { }
    }
}

static int ler_int(const char *prompt) {
    char buf[32];
    ler_linha(prompt, buf, sizeof(buf));
    return atoi(buf);
}

static void erro_stmt(MYSQL_STMT *stmt, const char *contexto) {
    fprintf(stderr, "Erro (%s): %s\n", contexto, mysql_stmt_error(stmt));
}

/*
 * Busca um cliente pelo id e preenche os buffers.
 * Retorna: 1 = encontrado, 0 = nao encontrado, -1 = erro
 */
static int carregar_cliente(MYSQL *conn, int id, char *nome, char *email, char *tel) {
    const char *sql = "SELECT nome, email, telefone FROM clientes WHERE id = ?";
    MYSQL_STMT *stmt = mysql_stmt_init(conn);
    if (!stmt) return -1;

    if (mysql_stmt_prepare(stmt, sql, (unsigned long)strlen(sql))) {
        erro_stmt(stmt, "prepare");
        mysql_stmt_close(stmt);
        return -1;
    }

    MYSQL_BIND in[1];
    memset(in, 0, sizeof(in));
    in[0].buffer_type = MYSQL_TYPE_LONG;
    in[0].buffer = (char *)&id;

    MYSQL_BIND out[3];
    unsigned long len_nome = 0, len_email = 0, len_tel = 0;
    memset(out, 0, sizeof(out));
    out[0].buffer_type = MYSQL_TYPE_STRING;
    out[0].buffer = nome;
    out[0].buffer_length = TAM_NOME - 1;
    out[0].length = &len_nome;
    out[1].buffer_type = MYSQL_TYPE_STRING;
    out[1].buffer = email;
    out[1].buffer_length = TAM_EMAIL - 1;
    out[1].length = &len_email;
    out[2].buffer_type = MYSQL_TYPE_STRING;
    out[2].buffer = tel;
    out[2].buffer_length = TAM_TEL - 1;
    out[2].length = &len_tel;

    if (mysql_stmt_bind_param(stmt, in) ||
        mysql_stmt_execute(stmt) ||
        mysql_stmt_bind_result(stmt, out)) {
        erro_stmt(stmt, "execute");
        mysql_stmt_close(stmt);
        return -1;
    }

    int rc = mysql_stmt_fetch(stmt);
    int resultado;
    if (rc == 0 || rc == MYSQL_DATA_TRUNCATED) {
        nome[len_nome < TAM_NOME - 1 ? len_nome : TAM_NOME - 1] = '\0';
        email[len_email < TAM_EMAIL - 1 ? len_email : TAM_EMAIL - 1] = '\0';
        tel[len_tel < TAM_TEL - 1 ? len_tel : TAM_TEL - 1] = '\0';
        resultado = 1;
    } else if (rc == MYSQL_NO_DATA) {
        resultado = 0;
    } else {
        erro_stmt(stmt, "fetch");
        resultado = -1;
    }

    mysql_stmt_close(stmt);
    return resultado;
}

/* ---------- CRUD ---------- */

/* CREATE */
static void criar_cliente(MYSQL *conn) {
    char nome[TAM_NOME], email[TAM_EMAIL], tel[TAM_TEL];

    ler_linha("Nome: ", nome, sizeof(nome));
    ler_linha("E-mail: ", email, sizeof(email));
    ler_linha("Telefone: ", tel, sizeof(tel));

    if (nome[0] == '\0' || email[0] == '\0') {
        printf("Nome e e-mail sao obrigatorios.\n");
        return;
    }

    const char *sql = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)";
    MYSQL_STMT *stmt = mysql_stmt_init(conn);
    if (!stmt) return;

    if (mysql_stmt_prepare(stmt, sql, (unsigned long)strlen(sql))) {
        erro_stmt(stmt, "prepare");
        mysql_stmt_close(stmt);
        return;
    }

    unsigned long ln = (unsigned long)strlen(nome);
    unsigned long le = (unsigned long)strlen(email);
    unsigned long lt = (unsigned long)strlen(tel);

    MYSQL_BIND b[3];
    memset(b, 0, sizeof(b));
    b[0].buffer_type = MYSQL_TYPE_STRING;
    b[0].buffer = nome;
    b[0].buffer_length = ln;
    b[0].length = &ln;
    b[1].buffer_type = MYSQL_TYPE_STRING;
    b[1].buffer = email;
    b[1].buffer_length = le;
    b[1].length = &le;
    b[2].buffer_type = MYSQL_TYPE_STRING;
    b[2].buffer = tel;
    b[2].buffer_length = lt;
    b[2].length = &lt;

    if (mysql_stmt_bind_param(stmt, b) || mysql_stmt_execute(stmt)) {
        erro_stmt(stmt, "insert");
    } else {
        printf("Cliente cadastrado com sucesso! ID: %lu\n",
               (unsigned long)mysql_stmt_insert_id(stmt));
    }
    mysql_stmt_close(stmt);
}

/* READ (listar todos) */
static void listar_clientes(MYSQL *conn) {
    if (mysql_query(conn, "SELECT id, nome, email, telefone FROM clientes ORDER BY id")) {
        fprintf(stderr, "Erro ao listar: %s\n", mysql_error(conn));
        return;
    }

    MYSQL_RES *res = mysql_store_result(conn);
    if (!res) {
        fprintf(stderr, "Erro ao obter resultado: %s\n", mysql_error(conn));
        return;
    }

    printf("\n%-5s %-30s %-30s %-15s\n", "ID", "NOME", "E-MAIL", "TELEFONE");
    printf("--------------------------------------------------------------------------------\n");

    MYSQL_ROW row;
    unsigned long total = 0;
    while ((row = mysql_fetch_row(res))) {
        printf("%-5s %-30s %-30s %-15s\n",
               row[0] ? row[0] : "",
               row[1] ? row[1] : "",
               row[2] ? row[2] : "",
               row[3] ? row[3] : "");
        total++;
    }
    if (total == 0) printf("(nenhum cliente cadastrado)\n");
    printf("\nTotal: %lu\n", total);

    mysql_free_result(res);
}

/* READ (buscar por id) */
static void buscar_cliente(MYSQL *conn) {
    int id = ler_int("ID do cliente: ");
    char nome[TAM_NOME], email[TAM_EMAIL], tel[TAM_TEL];

    int r = carregar_cliente(conn, id, nome, email, tel);
    if (r == 1) {
        printf("\nID: %d\nNome: %s\nE-mail: %s\nTelefone: %s\n", id, nome, email, tel);
    } else if (r == 0) {
        printf("Cliente nao encontrado.\n");
    }
}

/* UPDATE */
static void atualizar_cliente(MYSQL *conn) {
    int id = ler_int("ID do cliente a atualizar: ");
    char nome[TAM_NOME], email[TAM_EMAIL], tel[TAM_TEL];

    int r = carregar_cliente(conn, id, nome, email, tel);
    if (r == 0) {
        printf("Cliente nao encontrado.\n");
        return;
    }
    if (r < 0) return;

    printf("Dados atuais -> Nome: %s | E-mail: %s | Telefone: %s\n", nome, email, tel);
    printf("(deixe em branco para manter o valor atual)\n");

    char novo_nome[TAM_NOME], novo_email[TAM_EMAIL], novo_tel[TAM_TEL];
    ler_linha("Novo nome: ", novo_nome, sizeof(novo_nome));
    ler_linha("Novo e-mail: ", novo_email, sizeof(novo_email));
    ler_linha("Novo telefone: ", novo_tel, sizeof(novo_tel));

    if (novo_nome[0])  strcpy(nome, novo_nome);
    if (novo_email[0]) strcpy(email, novo_email);
    if (novo_tel[0])   strcpy(tel, novo_tel);

    const char *sql = "UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?";
    MYSQL_STMT *stmt = mysql_stmt_init(conn);
    if (!stmt) return;

    if (mysql_stmt_prepare(stmt, sql, (unsigned long)strlen(sql))) {
        erro_stmt(stmt, "prepare");
        mysql_stmt_close(stmt);
        return;
    }

    unsigned long ln = (unsigned long)strlen(nome);
    unsigned long le = (unsigned long)strlen(email);
    unsigned long lt = (unsigned long)strlen(tel);

    MYSQL_BIND b[4];
    memset(b, 0, sizeof(b));
    b[0].buffer_type = MYSQL_TYPE_STRING;
    b[0].buffer = nome;
    b[0].buffer_length = ln;
    b[0].length = &ln;
    b[1].buffer_type = MYSQL_TYPE_STRING;
    b[1].buffer = email;
    b[1].buffer_length = le;
    b[1].length = &le;
    b[2].buffer_type = MYSQL_TYPE_STRING;
    b[2].buffer = tel;
    b[2].buffer_length = lt;
    b[2].length = &lt;
    b[3].buffer_type = MYSQL_TYPE_LONG;
    b[3].buffer = (char *)&id;

    if (mysql_stmt_bind_param(stmt, b) || mysql_stmt_execute(stmt)) {
        erro_stmt(stmt, "update");
    } else {
        printf("Cliente atualizado com sucesso!\n");
    }
    mysql_stmt_close(stmt);
}

/* DELETE */
static void excluir_cliente(MYSQL *conn) {
    int id = ler_int("ID do cliente a excluir: ");
    char nome[TAM_NOME], email[TAM_EMAIL], tel[TAM_TEL];

    int r = carregar_cliente(conn, id, nome, email, tel);
    if (r == 0) {
        printf("Cliente nao encontrado.\n");
        return;
    }
    if (r < 0) return;

    char conf[8];
    printf("Excluir \"%s\"?\n", nome);
    ler_linha("(s/N): ", conf, sizeof(conf));
    if (conf[0] != 's' && conf[0] != 'S') {
        printf("Operacao cancelada.\n");
        return;
    }

    const char *sql = "DELETE FROM clientes WHERE id = ?";
    MYSQL_STMT *stmt = mysql_stmt_init(conn);
    if (!stmt) return;

    if (mysql_stmt_prepare(stmt, sql, (unsigned long)strlen(sql))) {
        erro_stmt(stmt, "prepare");
        mysql_stmt_close(stmt);
        return;
    }

    MYSQL_BIND b[1];
    memset(b, 0, sizeof(b));
    b[0].buffer_type = MYSQL_TYPE_LONG;
    b[0].buffer = (char *)&id;

    if (mysql_stmt_bind_param(stmt, b) || mysql_stmt_execute(stmt)) {
        erro_stmt(stmt, "delete");
    } else {
        printf("Cliente excluido com sucesso!\n");
    }
    mysql_stmt_close(stmt);
}

/* ---------- Programa principal ---------- */

static void menu(void) {
    printf("\n===== CRUD DE CLIENTES =====\n");
    printf("1 - Cadastrar\n");
    printf("2 - Listar todos\n");
    printf("3 - Buscar por ID\n");
    printf("4 - Atualizar\n");
    printf("5 - Excluir\n");
    printf("0 - Sair\n");
}

int main(void) {
    MYSQL *conn = mysql_init(NULL);
    if (!conn) {
        fprintf(stderr, "Falha ao inicializar o MySQL.\n");
        pausar();
        return EXIT_FAILURE;
    }

    if (!mysql_real_connect(conn, DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT, NULL, 0)) {
        fprintf(stderr, "Erro de conexao: %s\n", mysql_error(conn));
        mysql_close(conn);
        pausar();
        return EXIT_FAILURE;
    }
    mysql_set_character_set(conn, "utf8mb4");

    int opcao;
    do {
        menu();
        opcao = ler_int("Escolha: ");
        switch (opcao) {
            case 1: criar_cliente(conn);     break;
            case 2: listar_clientes(conn);   break;
            case 3: buscar_cliente(conn);    break;
            case 4: atualizar_cliente(conn); break;
            case 5: excluir_cliente(conn);   break;
            case 0: printf("Saindo...\n");   break;
            default: printf("Opcao invalida.\n");
        }
    } while (opcao != 0);

    mysql_close(conn);
    pausar();
    return EXIT_SUCCESS;
}
