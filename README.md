# Projeto Final — Sistema Escolar

Sistema escolar com **backend** (FastAPI + SQLAlchemy + Alembic + PostgreSQL) e **frontend** (Streamlit), no mesmo repositório.

```
projeto_final/
├── backend/    → API (FastAPI)
└── frontend/   → telas (Streamlit)
```

---

## O que foi implementado: cadastro de endereço pelo CEP (ViaCEP)

**Antes:** para cadastrar um aluno, era preciso digitar o `endereco_id`, e o endereço inteiro (rua, bairro, cidade...) era digitado à mão.

**Agora:** basta digitar o **CEP**. A API consulta o [ViaCEP](https://viacep.com.br), preenche o endereço sozinha, salva em `tb_enderecos` e liga o aluno a esse endereço pelo `endereco_id`.

### Como funciona

```
Front (matrícula, nome, email, CEP)
   ↓
schemas.py                  → valida a entrada (matrícula até 20 caracteres, CEP com 8 números)
   ↓
routers/alunos.py           → rota criar-aluno, chama o aluno_service
   ↓
services/aluno_service.py   → chama o cep_service, cadastra o endereço e depois o aluno
   ↓
services/cep_service.py     → manda o CEP para https://viacep.com.br/ws/{cep}/json/ e devolve o endereço
   ↓
Banco (tb_enderecos e tb_alunos)
```

- **Schema:** valida o que entra antes de chegar na rota.
- **Router:** recebe a requisição e chama o service.
- **Service:** é onde fica a lógica do back-end (aqui, consultar uma API externa e cadastrar).
- **Models:** não mudou. O banco continua igual, por isso não foi preciso criar migration.

O CEP é único em `tb_enderecos`: **use um CEP diferente para cada aluno**.

### Onde mexemos

| Arquivo | O que mudou |
|---|---|
| `backend/pyproject.toml` | Adicionada a biblioteca `requests` (para chamar a API) |
| `backend/app/schemas.py` | No `AlunoIn`, `endereco_id: int` virou `cep: str`, com validação (8 números) e matrícula com no máximo 20 caracteres |
| `backend/app/services/cep_service.py` | **Novo.** `buscar_cep`: chama o ViaCEP e devolve o endereço |
| `backend/app/services/aluno_service.py` | **Novo.** `criar_aluno`: usa o `cep_service`, cadastra o endereço e o aluno |
| `backend/app/routers/alunos.py` | A rota `criar-aluno` só chama `aluno_service.criar_aluno` |
| `frontend/menus/pagina_aluno.py` | Na tela "Criar Aluno", o campo "ID do endereço" virou "CEP" |

O resto (endereços, disciplinas, notas, atualizar aluno) continua igual.

> Digite o CEP só com números (ex: `01001000`). Com hífen, o schema recusa (erro 422).

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
