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
