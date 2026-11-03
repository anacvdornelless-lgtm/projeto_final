from sqlalchemy.orm import Session

from app.models import Nota
from app.schemas import NotaIn, NotaUpdateIn
from fastapi import Depends, FastAPI, APIRouter
from sqlalchemy import create_engine, select, text
import pandas as pd
from typing import Optional
from pydantic import BaseModel 
from app.database import engine, get_db


router = APIRouter(prefix="/notas")


@router.get("/pegar-mensagem")
def primeira_api():
    return {"message": "rotas notas"}


@router.get("/pegar-dados-notas")
def pegar_dados_notas(db: Session = Depends(get_db)):
    # query = "SELECT * FROM tb_notas"
    # df = pd.read_sql(query, engine)
    # df = df.astype(object).where(pd.notnull(df), None)
    # return df.to_dict(orient="records")
    notas = db.scalars(select(Nota).order_by(Nota.id)).all()
    return notas


@router.get("/pegar-dados-notas-por-id/{id}")
def pegar_dados_notas_por_id(id: int, db: Session = Depends(get_db)):
    # query = text("SELECT * FROM tb_notas WHERE id = :id")
    # df = pd.read_sql(query, engine, params={"id": id})
    # df = df.astype(object).where(pd.notnull(df), None)
    # return df.to_dict(orient="records")
    nota = db.get(Nota, id)
    return nota


@router.post("/criar-nota")
def criar_nota(nota: NotaIn, db: Session = Depends(get_db)):
    # # Transformando dict em df
    # df = pd.DataFrame([nota.model_dump()])
    # # Insert no banco de dados
    # df.to_sql("tb_notas", engine, if_exists="append", index=False)
    # return {"mensagem": "Nota cadastrada com sucesso!"}
    dados = Nota(
        nome_id = nota.nome_id,
        disciplina_id = nota.disciplina_id,
        nota = nota.nota
    )
    db.add(dados)
    db.commit()


@router.put("/atualizar-nota/{id}")
def atualizar_nota(id: int, nota: NotaUpdateIn, db: Session = Depends(get_db)):
    # # pega só os campos que foram enviados
    # dados = nota.model_dump(exclude_unset=True)
    # # monta o SET dinamicamente (ex: "nota = :nota")
    # campos_sql = ", ".join([f"{chave} = :{chave}" for chave in dados.keys()])
    # query = f"UPDATE tb_notas SET {campos_sql} WHERE id = :id"
    # with engine.connect() as conn:
    #     conn.execute(text(query), {"id": id, **dados})
    #     conn.commit()
    # return {"mensagem": "Nota atualizada com sucesso!"}
    dados = db.get(Nota, id)
    campos = nota.model_dump(exclude_unset=True)
    for chave, valor in campos.items():
        setattr(dados, chave, valor)
    db.commit()
    return {"mensagem": "Nota atualizada com sucesso!"}


@router.delete("/deletar-nota/{id}")
def deletar_nota(id: int, db: Session = Depends(get_db)):
    # query = "DELETE FROM tb_notas WHERE id = :id"
    # with engine.connect() as conn:
    #     conn.execute(text(query), {"id": id})
    #     conn.commit()
    # return {"mensagem": "Nota deletada com sucesso!"}
    dados = db.get(Nota,  id)
    db.delete(dados)
    db.commit()
    return {"mensagem": "Nota deletada com sucesso!"}