from sqlalchemy.orm import Session

from app.models import Aluno
from app.schemas import AlunoIn, AlunoUpdateIn
from fastapi import APIRouter, Depends
from sqlalchemy import select, text
import pandas as pd
from app.database import engine, get_db
from app.services import aluno_service

router = APIRouter(prefix="/alunos")


@router.get("/")
def primeira_api():
    return {"message": "rotas alunos"}

@router.get("/pegar-dados-alunos")
def pegar_dados_alunos(db: Session = Depends(get_db)):
    #query = "SELECT * FROM tb_alunos"
    #df = pd.read_sql(query, engine)
    #return df.to_dict(orient="records")
    alunos = db.scalars(select(Aluno).order_by(Aluno.id)).all()
    return alunos

@router.get("/pegar-dados-alunos-por-id/{id}")
def pegar_dados_alunos_por_id(id: int, db: Session = Depends(get_db)):
    #query = text("SELECT * FROM tb_alunos WHERE id = :id")
    #df = pd.read_sql(query, engine, params={"id": id})
    #return df.to_dict(orient="records")
    aluno = db.get(Aluno, id)
    return aluno

@router.post("/criar-aluno")
def criar_aluno(aluno: AlunoIn, db: Session = Depends(get_db)):
    # # Transformando dict em df
    # df = pd.DataFrame([aluno.model_dump()])
    # # Insert no banco de dados
    # df.to_sql("tb_alunos", engine, if_exists="append", index=False)
    # return {"mensagem": "Aluno cadastrado com sucesso!"}
    aluno_service.criar_aluno(db, aluno)
    return {"mensagem": "Aluno cadastrado com sucesso!"}

@router.put("/atualizar-aluno/{id}")
def atualizar_aluno(id: int, aluno: AlunoUpdateIn, db: Session = Depends(get_db)):
    # #monta clausula SET dinamicamente (Ex: "nome_aluno = :nome_aluno")
    # campos_sql= ", ".join([f"{chave} = :{chave}" for chave in aluno.model_dump(exclude_unset=True).keys()])
    # query= f"""
    # UPDATE tb_alunos
    # SET {campos_sql}
    # WHERE id = :id
    # """
    # with engine.connect() as conn:
    #     conn.execute(
    #     text(query),
    #     {"id" :id, **aluno.model_dump(exclude_unset=True)}
    #     )
    #     conn.commit()
    # return {"mensagem": "aluno atualizado com sucesso"}
    dados = db.get(Aluno, id)
    campos = aluno.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(dados, campo, valor)
    db.commit()
    return {"mensagem": "Aluno atualizado com sucesso!"}


@router.delete("/deletar-aluno/{id}")
def deletar_aluno(id: int, db: Session = Depends(get_db)):
    # query = "DELETE FROM tb_alunos WHERE id = :id"
    # with engine.connect() as conn:
    #     conn.execute(text(query), {"id": id})
    #     conn.commit()
    # return {"mensagem": "Aluno deletado com sucesso!"}
    dados = db.get(Aluno, id)
    db.delete(dados)
    db.commit()
    return {"mensagem": "Aluno deletado com sucesso!"}