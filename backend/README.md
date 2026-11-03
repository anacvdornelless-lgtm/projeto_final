Instalar o uv (gerenciador de pacotes)
Mac : curl -LsSf https://astral.sh/uv/install.sh | sh
Windows : powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
Conferir que instalou: uv --version
Clonar o repositório (no VS Code ou terminal): git clone <url-do-repo>
Entrar na pasta clonada e abrir no VS Code.
Instalar as dependências do projeto: uv sync
Ativar o ambiente virtual
Mac: source .venv/bin/activate
Windows: .venv\Scripts\activate
Conferir/criar o banco no DBeaver — se não existir, criar com CREATE DATABASE db_escola; (nome tem que bater com o que vai no .env)
Criar o arquivo .env na raiz do projeto (não vem do clone, é sempre manual) com as variáveis que o database.py pede: user, senha, host, port, banco — e salvar o arquivo (Cmd+S / Ctrl+S, esse foi o erro que travou tudo por um tempo).
Rodar as migrations: uv run alembic upgrade head → isso cria as tabelas vazias no banco.
Conferir no DBeaver se as tabelas apareceram (der refresh; se o banco não aparecer na árvore, ativar "Show all databases" nas configurações da conexão).
Subir a API: uv run uvicorn app.main:app --reload
Testar no Postman, respeitando a ordem das chaves estrangeiras (banco vem vazio, é normal):

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
O clone traz o código (e o `.env`, que foi enviado). O banco de dados NÃO vem junto: ele começa vazio.

## 1. Conferir o que precisa estar instalado

```
git --version
uv --version
```

Se o `uv` não existir: `pip install uv`. O PostgreSQL precisa estar rodando e o DBeaver instalado.

## 2. Clonar e instalar as dependências

```
git clone https://github.com/anacvdornelless-lgtm/fastapi_orm_alembic.git
cd fastapi_orm_alembic
uv sync
```

O `uv sync` cria o `.venv` sozinho e instala tudo que está no pyproject.toml.

## 3. Ativar o ambiente virtual

Mac / Linux:
```
source .venv/bin/activate
```

Windows (CMD ou PowerShell):
```
.venv\Scripts\activate
```

O terminal passa a mostrar `(fastapi-orm-alembic)` no começo da linha. Isso quer dizer que está ativado.
Tem que ativar de novo toda vez que abrir um terminal novo.

## 4. Conferir o .env

Abrir o arquivo `.env` (na mesma pasta do pyproject.toml) e ver se bate com o Postgres desta máquina:

```
user=...
senha=...
host=localhost
port=5432
banco=db_escola
```

Se o usuário ou a senha do Postgres daqui forem diferentes, editar o arquivo.

## 5. Criar o banco no DBeaver

Conectar no Postgres e rodar:

```sql
CREATE DATABASE db_escola;
```

## 6. Criar as tabelas (Alembic)

Só `upgrade`. NÃO rodar `revision` de novo.

```
alembic upgrade head
```

No DBeaver, atualizar (F5) e conferir se apareceram: tb_enderecos, tb_alunos, tb_disciplinas, tb_notas e alembic_version.

## 7. Subir a API

```
uvicorn app.main:app --reload
```

Deixar esse terminal aberto. Deve aparecer `Application startup complete`.

---

# Testar no Postman

Para POST e PUT: escolher o método, colar a URL, aba **Body** > **raw** > **JSON** e colar o conteúdo.
Para GET e DELETE: só o método e a URL (sem Body).

Ordem de cadastro por causa das chaves estrangeiras: **endereços → alunos → disciplinas → notas**.
Em banco novo os ids começam em 1.

## POST (criar)

**Endereço:** `POST http://127.0.0.1:8000/enderecos/criar-endereco`
```json
{
  "cep": "70000-001",
  "endereco": "SQN 110 Bloco A",
  "bairro": "Asa Norte",
  "cidade": "Brasília",
  "estado": "DF",
  "regiao": "Centro-Oeste"
}
```

**Aluno:** `POST http://127.0.0.1:8000/alunos/criar-aluno`
```json
{
  "matricula": "2026001",
  "nome_aluno": "Maria Silva",
  "email": "maria@email.com",
  "endereco_id": 1
}
```

**Disciplina:** `POST http://127.0.0.1:8000/disciplinas/criar-disciplina`
```json
{
  "nome_disciplina": "Banco de Dados",
  "carga": "60h",
  "semestre": "2026.2"
}
```

**Nota:** `POST http://127.0.0.1:8000/notas/criar-nota`
```json
{
  "nome_id": 1,
  "disciplina_id": 1,
  "nota": 8.5
}
```

## GET (listar)

```
GET http://127.0.0.1:8000/enderecos/pegar-dados-endereco
GET http://127.0.0.1:8000/alunos/pegar-dados-alunos
GET http://127.0.0.1:8000/disciplinas/pegar-dados-disciplina
GET http://127.0.0.1:8000/notas/pegar-dados-notas
```

GET por id:
```
GET http://127.0.0.1:8000/alunos/pegar-dados-alunos-por-id/1
GET http://127.0.0.1:8000/notas/pegar-dados-notas-por-id/1
```

## PUT (atualizar) — manda só o campo que quer mudar

**Endereço:** `PUT http://127.0.0.1:8000/enderecos/atualizar-endereco/1`
```json
{
  "bairro": "Asa Sul"
}
```

**Aluno:** `PUT http://127.0.0.1:8000/alunos/atualizar-aluno/1`
```json
{
  "email": "maria.nova@email.com"
}
```

**Disciplina:** `PUT http://127.0.0.1:8000/disciplinas/atualizar-disciplina/1`
```json
{
  "carga": "80h"
}
```

**Nota:** `PUT http://127.0.0.1:8000/notas/atualizar-nota/1`
```json
{
  "nota": 9.0
}
```

Depois de cada PUT, rodar o GET da mesma tabela para ver se mudou.

## DELETE (apagar) — sem Body

Apagar do fim para o começo, senão o banco recusa (chave estrangeira):

```
DELETE http://127.0.0.1:8000/notas/deletar-nota/1
DELETE http://127.0.0.1:8000/alunos/deletar-aluno/1
DELETE http://127.0.0.1:8000/disciplinas/deletar-disciplina/1
DELETE http://127.0.0.1:8000/enderecos/deletar-endereco/1
```

Depois de cada DELETE, rodar o GET para ver que sumiu.

---

# Conferir no DBeaver (depois de cada teste)

O DBeaver não passa pela API: mostra o que realmente está gravado no banco.

```sql
SELECT * FROM tb_enderecos;
SELECT * FROM tb_alunos;
SELECT * FROM tb_disciplinas;
SELECT * FROM tb_notas;
```

Alterar ou apagar direto no banco (sem API). O WHERE é obrigatório, senão afeta a tabela inteira:

```sql
UPDATE tb_alunos SET endereco_id = 2 WHERE id = 1;
DELETE FROM tb_notas WHERE id = 1;
```

---

# Se der erro

- `command not found: uvicorn` ou `alembic` → ambiente não ativado (rodar o passo 3). Se já estiver ativado e continuar: `rm -rf .venv`, `uv sync` e ativar de novo
- No Windows PowerShell, se o `activate` for bloqueado: usar o CMD, ou rodar `Set-ExecutionPolicy -Scope Process RemoteSigned` antes
- 405 Method Not Allowed → método errado no Postman (GET em rota POST, por exemplo)
- 404 Not Found → URL errada
- 422 `Field required` → Body vazio: Body > raw > JSON
- 500 `UniqueViolation` → CEP repetido, usar outro
- 500 `ForeignKeyViolation` ao criar → o endereço, aluno ou disciplina referenciado não existe ainda
- 500 `ForeignKeyViolation` ao apagar → apagar antes quem depende dele (notas → alunos → disciplinas/endereços)
- 500 de conexão ou senha → Postgres desligado, ou `.env` não bate com o Postgres desta máquina
- Tabelas não existem → faltou o `alembic upgrade head`
