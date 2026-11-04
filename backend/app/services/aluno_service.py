from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Aluno, Endereco
from app.schemas import AlunoComCepIn, AlunoIn, AlunoUpdateIn
from app.services import cep_service


def listar_alunos(db: Session):
    return db.scalars(select(Aluno).order_by(Aluno.id)).all()


def listar_alunos_por_id(db: Session, aluno_id: int):
    aluno = db.get(Aluno, aluno_id)
    return [aluno] if aluno is not None else []


def buscar_aluno(db: Session, aluno_id: int) -> Aluno:
    aluno = db.get(Aluno, aluno_id)
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


# Cadastro antigo: recebe o endereco_id
def criar_aluno(db: Session, dados: AlunoIn) -> Aluno:
    email = dados.email.strip().lower()
    if db.get(Endereco, dados.endereco_id) is None:
        raise HTTPException(status_code=404, detail="Endereço não encontrado")
    aluno = Aluno(
        matricula=dados.matricula,
        nome_aluno=dados.nome_aluno,
        email=email,
        endereco_id=dados.endereco_id,
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno


# Cadastro novo: recebe o CEP e busca o endereço no ViaCEP
def criar_com_cep(db: Session, dados: AlunoComCepIn) -> Aluno:
    endereco_dados = cep_service.consultar_cep(dados.cep)

    # O CEP já está no banco? Então reaproveita o endereço
    consulta = select(Endereco).where(Endereco.cep == endereco_dados.cep)
    endereco = db.scalar(consulta)
    if endereco is None:
        endereco = Endereco(
            cep=endereco_dados.cep,
            endereco=endereco_dados.endereco,
            bairro=endereco_dados.bairro,
            cidade=endereco_dados.cidade,
            estado=endereco_dados.estado,
            regiao=endereco_dados.regiao,
        )
        db.add(endereco)
        db.flush()  # Gera o ID do endereço, sem confirmar a transação

    aluno = Aluno(
        matricula=dados.matricula,
        nome_aluno=dados.nome_aluno,
        email=dados.email.strip().lower(),
        endereco_id=endereco.id,
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno


def atualizar_aluno(db: Session, aluno_id: int, dados: AlunoUpdateIn) -> Aluno:
    aluno = buscar_aluno(db, aluno_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(aluno, campo, valor)
    db.commit()
    db.refresh(aluno)
    return aluno


def deletar_aluno(db: Session, aluno_id: int):
    aluno = buscar_aluno(db, aluno_id)
    db.delete(aluno)
    db.commit()
