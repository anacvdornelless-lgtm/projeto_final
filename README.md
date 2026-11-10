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
# Projeto Final — Sistema Escolar

Sistema escolar com **backend** (FastAPI + SQLAlchemy + Alembic + PostgreSQL) e **frontend** (Streamlit), no mesmo repositório.

```
projeto_final/
├── backend/    → API (FastAPI)
└── frontend/   → telas (Streamlit)
```

---

## O que foi implementado: cadastro de aluno pelo CEP (ViaCEP)

**Antes:** para cadastrar um aluno, era preciso digitar o `endereco_id`.

**Agora:** existe também a rota `POST /alunos/criar-aluno-com-cep`. O usuário manda matrícula, nome, e-mail e **CEP**, e o sistema consulta o [ViaCEP](https://viacep.com.br), cadastra o endereço e depois o aluno. A rota antiga (`criar-aluno`, com `endereco_id`) continua funcionando.

### Como funciona

```
Front (matrícula, nome, email, CEP)
   ↓
schemas.py (AlunoComCepIn)   → valida a entrada (tamanho da matrícula, do nome e do e-mail)
   ↓
routers/alunos.py            → rota criar-aluno-com-cep, chama o aluno_service
   ↓
services/aluno_service.py    → criar_com_cep: chama o cep_service, cadastra o endereço
                               (ou reaproveita, se o CEP já existe) e depois o aluno
   ↓
services/cep_service.py      → consultar_cep: chama https://viacep.com.br/ws/{cep}/json/
                               e devolve um EnderecoIn
   ↓
Banco (tb_enderecos e tb_alunos)
   ↓
schemas.py (AlunoOut)        → formato da resposta
```

- **Schemas:** validam o que entra (`AlunoComCepIn`) e o que sai (`AlunoOut`, `EnderecoIn`).
- **Router:** recebe a requisição e chama o service. Não tem lógica.
- **Services:** é onde fica a lógica do back-end (consultar a API externa, cadastrar, buscar, atualizar e deletar).
- **Models:** não mudou. O banco continua igual, por isso não foi preciso criar migration.

### Onde mexemos

| Arquivo | O que mudou |
|---|---|
| `backend/app/schemas.py` | Novos `AlunoOut` (saída) e `AlunoComCepIn` (entrada com CEP e validações de tamanho) |
| `backend/app/services/cep_service.py` | **Novo.** `consultar_cep`: chama o ViaCEP com `urllib` e devolve um `EnderecoIn`; se der erro, devolve 502 |
| `backend/app/services/aluno_service.py` | **Novo.** `listar_alunos`, `listar_alunos_por_id`, `buscar_aluno`, `criar_aluno`, `criar_com_cep`, `atualizar_aluno`, `deletar_aluno` |
| `backend/app/routers/alunos.py` | Todas as rotas chamam o `aluno_service`; nova rota `POST /alunos/criar-aluno-com-cep` |
| `frontend/menus/pagina_aluno.py` | A tela "Criar Aluno" pede o CEP e chama `/alunos/criar-aluno-com-cep` |

### Erros tratados

| Situação | Resposta |
|---|---|
| CEP que não existe ou ViaCEP fora do ar | 502: "Não foi possível consultar o CEP" |
| Matrícula com mais de 20 caracteres, nome vazio, e-mail curto | 422 (validação do schema) |
| Aluno não encontrado (buscar, atualizar, deletar) | 404 |
| `criar-aluno` com `endereco_id` que não existe | 404: "Endereço não encontrado" |

---

## Como clonar e rodar em outro computador

### Pré-requisitos

- [uv](https://docs.astral.sh/uv/) instalado
- PostgreSQL rodando, com um banco criado para o projeto
- Git

### 1. Clonar

```bash
git clone https://github.com/anacvdornelless-lgtm/projeto_final.git
cd projeto_final
```

### 2. Configurar o banco (`.env`)

O `.env` tem senha, então **não vai para o GitHub**. Crie o seu a partir do modelo:

```bash
cd backend
cp .env.example .env
```

Abra o `.env` e preencha com os dados do seu PostgreSQL:

```
user=postgres
senha=sua_senha
host=localhost
port=5432
banco=nome_do_banco
```

### 3. Criar as tabelas (Alembic)

Ainda dentro de `backend/`:

```bash
uv sync
uv run alembic upgrade head
```

### 4. Rodar o backend (terminal 1)

```bash
cd backend
uv run uvicorn app.main:app --reload
```

A API fica em http://127.0.0.1:8000, e a documentação para testar fica em http://127.0.0.1:8000/docs.

### 5. Rodar o frontend (terminal 2)

```bash
cd frontend
uv sync
uv run streamlit run app.py
```

---

## Como testar se está funcionando

1. **Front:** em Alunos → Criar Aluno, preencha matrícula (até 20 caracteres), nome, e-mail e CEP, e clique em criar. Tem que aparecer "Aluno criado com sucesso".

### Conferir no DBeaver se salvou

Conecte no banco do `.env` e rode:

```sql
-- endereços que vieram do ViaCEP
SELECT * FROM tb_enderecos ORDER BY id;

-- alunos com o endereço de cada um
SELECT a.id, a.matricula, a.nome_aluno, e.cep, e.endereco, e.bairro, e.cidade, e.estado, e.regiao
FROM tb_alunos a
JOIN tb_enderecos e ON e.id = a.endereco_id
ORDER BY a.id;
```

O aluno novo tem que aparecer com rua, bairro e cidade preenchidos, mesmo que você só tenha digitado o CEP.

> Se a tabela não atualizar no DBeaver, clique com o botão direito nela e escolha **Refresh** (ou aperte F5).

---

## Prompt para a prova (gerar código de novas tabelas)

Como usar: cole o prompt abaixo na IA **junto com a foto do desenho**. Troque só o que está entre `[colchetes]`.
Antes de enviar: faça `commit` e `push` (a IA só enxerga o que está no GitHub) e deixe o repositório público.
Se a IA não conseguir abrir o link, cole o conteúdo de `models.py`, `schemas.py`, `aluno_service.py` e `cep_service.py` no prompt.

```
Leia meu projeto no GitHub antes de responder:
https://github.com/anacvdornelless-lgtm/projeto_final

Arquivos de referência (pasta backend/app):
- models.py: padrão das classes e quais tabelas já existem
- schemas.py: padrão dos schemas (Field, ConfigDict)
- services/aluno_service.py: padrão do service (criar_com_cep)
- services/cep_service.py: consulta do ViaCEP (já existe, reutilize)
- routers/alunos.py: padrão das rotas
- main.py: onde os routers são incluídos

Siga exatamente esse estilo e NÃO recrie o que já existe.

Stack: FastAPI + SQLAlchemy 2.0 (Mapped, mapped_column) + Alembic + PostgreSQL.
Anexei a foto do desenho das tabelas: siga o desenho (nomes, colunas, FKs e relações).

TABELAS QUE JÁ EXISTEM (não recriar, só usar como destino de FK):
- [Endereco -> tb_enderecos]
- [Disciplina -> tb_disciplinas]

TABELAS NOVAS (criar só estas):
1. [Funcionario] (tb_[funcionarios]): id (PK), [nome_funcionario], [endereco_id] FK -> tb_enderecos.id
2. [Profissao] (tb_[profissoes]): id (PK), [nome_profissao]
3. [FuncionarioProfissao] (tb_[funcionario_profissao]) - associativa N:N:
   id (PK), [id_funcionario] FK -> tb_funcionarios.id, [id_profissao] FK -> tb_profissoes.id, [salario] float
4. [FuncionarioDisciplina] (tb_[funcionario_disciplina]) - associativa N:N:
   id (PK), [id_funcionario] FK -> tb_funcionarios.id, [id_disciplina] FK -> tb_disciplinas.id

CADASTRO PELO CEP:
A rota [POST /criar-funcionario] recebe [nome_funcionario] e [cep]. O service deve:
a) consultar o CEP com cep_service.consultar_cep (já existe),
b) reaproveitar o Endereco se o CEP já existir no banco, senão criar (incluindo o campo regiao),
c) usar db.flush() para gerar o id do endereço,
d) criar o [Funcionario] com endereco_id,
e) db.commit() e db.refresh().

GERE NESTA ORDEM, cada item em um bloco separado:
1. models.py: só as classes NOVAS, para eu colar no final do arquivo.
2. schemas.py: APENAS [FuncionarioComCepIn] (com Field de tamanho, igual ao AlunoComCepIn). NÃO crie schema de saída (Out).
3. services/[funcionario_service].py: função criar_com_cep no mesmo estilo do aluno_service.
4. routers/[funcionarios].py: o router só chama o service, sem lógica e SEM response_model (não existe schema Out); retorne uma mensagem de sucesso com o id criado.
5. A linha do main.py que inclui o novo router.
6. Os comandos do Alembic: revision --autogenerate e upgrade head.

REGRAS:
- Prefixo tb_ nas tabelas; o ForeignKey deve ser igual ao __tablename__ da outra classe.
- Relação 1:N: FK no lado "N". Relação N:N: tabela associativa com as duas FKs.
- Dado que depende do par (ex.: [salario]) fica na tabela associativa.
- Não crie schemas de saída (Out) nem use response_model: o professor não quer Out.
- Tipos: texto String(255), decimais Float, ids int.
- Responda só com o código e uma frase curta por arquivo. Não repita imports nem classes existentes.
```

### Conferência depois que a IA responder
- Cada FK aponta para a tabela e a coluna certas (nome igual ao `__tablename__`)?
- Ela deixou de recriar as tabelas que já existem?
- O service faz `flush` antes de usar `endereco.id` e só então `commit`?
- O router só chama o service?
- No Alembic, abra o arquivo novo em `alembic/versions/` e confira se cria só as tabelas novas antes do `upgrade head`.

---

## Prompt 2 (genérico, para qualquer situação)

Use quando o tema da prova for outro (loja, hospital, academia...) ou quando o enunciado não falar de CEP.
Aqui você **não precisa listar coluna por coluna**: a IA lê a foto do desenho e o enunciado. Troque só os `[colchetes]`.

```
Leia meu projeto no GitHub antes de responder:
https://github.com/anacvdornelless-lgtm/projeto_final
Referência (pasta backend/app): models.py, schemas.py, services/aluno_service.py,
services/cep_service.py, routers/alunos.py e main.py.
Siga exatamente esse estilo (SQLAlchemy 2.0 com Mapped/mapped_column, prefixo tb_,
services com a lógica, routers só chamando o service) e NÃO recrie o que já existe.

ENUNCIADO DA PROVA:
[cole aqui o enunciado]

Anexei a foto do meu desenho das tabelas. Siga o desenho: nomes, colunas, FKs e relações.

TABELAS QUE JÁ EXISTEM NO MEU models.py (não recriar, só usar como destino de FK):
[liste, ex.: Endereco (tb_enderecos), Disciplina (tb_disciplinas), Aluno (tb_alunos)]

ENTIDADE PRINCIPAL DO CADASTRO: [ex.: Funcionario]
- Campos que a rota recebe: [ex.: nome_funcionario e cep]
- Rota: [ex.: POST /criar-funcionario]
- [Se houver CEP: usar cep_service.consultar_cep, reaproveitar o Endereco se o CEP já existir
  (senão criar, incluindo regiao), db.flush() para gerar o id e só então criar a entidade,
  depois db.commit() e db.refresh().]
- [Se NÃO houver CEP: o service valida as FKs recebidas (db.get na tabela de destino e 404 se
  não existir), cria a entidade, db.commit() e db.refresh().]

GERE NESTA ORDEM, cada item em um bloco separado, só o que for NOVO:
1. models.py: classes novas para eu colar no final do arquivo (sem repetir imports).
2. schemas.py: APENAS o schema de entrada (com Field de tamanho, igual ao AlunoComCepIn).
   NÃO crie schema de saída (Out).
3. services/[nome]_service.py: no mesmo estilo do aluno_service.
4. routers/[nome].py: o router só chama o service, sem response_model (não existe schema Out);
   retorne uma mensagem de sucesso com o id criado.
5. A linha do main.py que inclui o novo router.
6. Comandos do Alembic: revision --autogenerate e upgrade head.

REGRAS DE MODELAGEM:
- Relação 1:N: a FK fica no lado "N".
- Relação N:N: tabela associativa com id (PK) e as duas FKs.
- Dado que depende do par (nota, salário, data, valor...) fica na tabela associativa.
- O nome dentro do ForeignKey deve ser igual ao __tablename__ da outra classe.
- Não crie schemas de saída (Out) nem use response_model: o professor não quer Out.
- Tipos: texto String(255), decimais Float, datas Date, ids int.
- Se alguma relação do desenho estiver ambígua, escolha a mais simples e me diga em uma frase.

FORMATO DA RESPOSTA: só código e uma frase curta por arquivo. Não repita classes existentes.
```

### Variações rápidas (acrescente ao prompt, se precisar)
- **Rotas de listar/atualizar/deletar também:** "Gere também listar, buscar por id, atualizar e deletar no mesmo estilo do aluno_service (404 quando não achar)."
- **Mais de uma entidade para cadastrar:** repita o bloco "ENTIDADE PRINCIPAL" para cada uma.
- **Cadastro já vinculando N:N** (ex.: funcionário e suas disciplinas): "Na mesma rota, receba a lista de ids de [disciplinas] e crie as linhas da associativa dentro do mesmo commit."
- **Guardar o CEP sem hífen:** "Normalize o CEP com replace('-', '') ao gravar e ao consultar."

### Conferência depois que a IA responder
- Os nomes de tabelas e colunas batem com o **meu desenho**?
- Cada FK aponta para a tabela certa e nada existente foi recriado?
- O service salva o que é "pai" antes do que é "filho" (flush antes de usar o id)?
- O Alembic vai criar só as tabelas novas? Abra o arquivo em `alembic/versions/` antes do `upgrade head`.

---

## Passo a passo para a prova (do zero até a rota funcionando)

Ordem do que fazer na máquina da prova. Cada passo diz **como saber que deu certo**.

### Parte A: preparar a máquina

1. **Instalar o uv** (PowerShell):
   ```
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   Feche e abra o terminal. Deu certo se `uv --version` mostra uma versão.

2. **Criar a pasta e clonar:**
   ```
   mkdir prova
   cd prova
   git clone https://github.com/anacvdornelless-lgtm/projeto_final.git
   cd projeto_final\backend
   ```
   Deu certo se `dir` mostra `app`, `alembic` e `pyproject.toml`.

3. **Instalar as dependências:**
   ```
   uv sync
   ```
   Deu certo se termina sem erro. O uv baixa o Python 3.13 sozinho se faltar.

4. **Criar o `.env`** dentro de `backend` (ele não vem no clone, porque está no `.gitignore`):
   ```
   user=postgres
   senha=SUA_SENHA
   host=localhost
   port=5432
   banco=NOME_DO_BANCO
   ```
   O banco precisa **já existir**. Se não existir, crie no DBeaver ou no pgAdmin.

5. **Recriar as tabelas que já existem:**
   ```
   uv run alembic upgrade head
   ```
   Deu certo se aparecem `tb_alunos`, `tb_disciplinas`, `tb_enderecos` e `tb_notas` no banco.
   Faça isso **antes** de adicionar qualquer model. Se pular, o `--autogenerate` vai tentar criar tudo de novo e dar conflito.

6. **Testar o projeto antes de mexer:**
   ```
   uv run uvicorn app.main:app --reload
   ```
   Abra http://127.0.0.1:8000/docs. Deu certo se a página abre com as rotas. Pare o servidor com `Ctrl+C`.

### Parte B: adicionar o código novo (ordem do quadro)

7. **Models:** cole as classes novas no **final** do `app/models.py`.
   Confira se o texto dentro de cada `ForeignKey('tb_x.id')` é igual ao `__tablename__` da outra classe.

8. **Schemas:** cole só o schema de **entrada** (`...In`) no `app/schemas.py`. O professor não quer o `Out` (no quadro está riscado com X).

9. **Service:** crie `app/services/[nome]_service.py`.

10. **Router:** crie `app/routers/[nome].py` e inclua no `app/main.py`:
    ```python
    from app.routers import [nome]
    app.include_router([nome].router)
    ```
    Rode o servidor de novo. Se der `ImportError`, o erro é de nome (arquivo, classe ou função) entre schemas, service e router.

### Parte C: migration e teste final

11. **Gerar a migration:**
    ```
    uv run alembic revision --autogenerate -m "cria tabelas novas"
    ```
    **Abra o arquivo novo** em `alembic/versions/` e confira: ele deve ter só `create_table` das tabelas **novas**. Se aparecer tabela antiga, volte ao passo 5.

12. **Aplicar:**
    ```
    uv run alembic upgrade head
    ```
    Dê refresh no DBeaver (F5). Deu certo se as tabelas novas aparecem com as FKs.

13. **Testar no `/docs`:** suba o servidor e chame a rota nova (por exemplo `criar-funcionario` com nome e CEP `70040010`).
    Deu certo se responde 200 com o `id`. Confirme no DBeaver:
    ```sql
    SELECT * FROM tb_enderecos;
    SELECT * FROM [tabela_nova];
    ```

14. **Opcional, se pedirem:** `git add .`, `git commit -m "..."` e `git push`.

### Erros mais comuns e onde olhar

| Erro | Causa provável | Onde olhar |
|---|---|---|
| `NoReferencedTableError` | Nome da tabela errado dentro do `ForeignKey` | Passo 7 |
| Autogenerate criou tabelas antigas | Faltou rodar o `upgrade head` antes | Passo 5 |
| `relation already exists` | Migration rodada duas vezes ou banco já tinha tabelas | `uv run alembic current` |
| 502 na rota do CEP | Sem internet ou CEP inválido | Passo 13 |
| `endereco_id` nulo | Faltou o `db.flush()` no service | Passo 9 |
| `ImportError` ao subir a API | Nome diferente entre schema, service e router | Passo 10 |

**Tempo de referência para treinar:** as partes A e B em cerca de 15 a 20 minutos, com o código novo já pronto. Treine a Parte A inteira em uma pasta nova antes da prova, porque é onde mais se perde tempo.
