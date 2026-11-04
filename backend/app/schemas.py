from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
class EnderecoIn(BaseModel):
    cep:str
    endereco: str
    bairro: str
    cidade: str
    estado: str
    regiao: str

class EnderecoUpdateIn(BaseModel):
    cep: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    regiao: Optional[str] = None

#schema de entrada para tb disciplinas
class DisciplinaIn(BaseModel):
    nome_disciplina: str
    carga: str
    semestre: str


class DisciplinaUpdateIn(BaseModel):
    nome_disciplina: Optional[str] = None
    carga: Optional[str] = None
    semestre: Optional[str] = None

#schema de entrada para tb alunos
class AlunoUpdateIn(BaseModel):
    matricula: Optional[str] = None
    nome_aluno: Optional[str] = None
    email: Optional[str] = None
    endereco_id: Optional[int] = None

class AlunoIn(BaseModel):
    matricula: str
    nome_aluno: str
    email: str
    endereco_id: int

#schema de saída do aluno
class AlunoOut(AlunoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int

#schema de entrada para criar aluno usando o CEP (ViaCEP)
class AlunoComCepIn(BaseModel):
    matricula: str = Field(min_length=1, max_length=20)
    nome_aluno: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=100)
    cep: str


#schema de entrada para tb notas
class NotaIn(BaseModel):
    nome_id: int
    disciplina_id: int
    nota: float


class NotaUpdateIn(BaseModel):
    nome_id: Optional[int] = None
    disciplina_id: Optional[int] = None
    nota: Optional[float] = None