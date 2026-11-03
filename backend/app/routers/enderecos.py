from fastapi import Depends, FastAPI, APIRouter
import pandas as pd
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import Endereco
from app.schemas import EnderecoIn, EnderecoUpdateIn
from sqlalchemy import select, text

router = APIRouter(prefix="/enderecos")

@router.get("/pegar-mensagem")
def primeira_api():
    return {"message": "Hello World"}


@router.get("/pegar-dados-endereco")
def pegar_dados_endereco(db: Session = Depends(get_db)):
    # query = "SELECT * FROM tb_enderecos"
    # df = pd.read_sql(query, engine)
    # df = df.astype(object).where(pd.notnull(df), None)
    # return df.to_dict(orient="records")
    enderecos = db.scalars(select(Endereco).order_by(Endereco.id)).all()
    return enderecos

@router.get("/pegar-dados-endereco-por-id/{id}")
def pegar_dados_endereco_por_id(id: int, db: Session = Depends(get_db)):
    # query = text("SELECT * FROM tb_enderecos WHERE id = :id")
    # df = pd.read_sql(query, engine, params={"id": id})
    # df = df.astype(object).where(pd.notnull(df), None)
    # return df.to_dict(orient="records")
    endereco = db.get(Endereco, id)
    return endereco

@router.post("/criar-endereco")
def criar_endereco(endereco: EnderecoIn, db: Session = Depends(get_db)):
    # # Transformando dict em df
    # df = pd.DataFrame([endereco.model_dump()])
    # # Insert no banco de dados
    # df.to_sql("tb_enderecos", engine, if_exists="append", index=False)
    # return {"mensagem": "Endereço cadastrado com sucesso!"}
    dados = Endereco(
        cep = endereco.cep,
        endereco = endereco.endereco,
        bairro = endereco.bairro,
        cidade = endereco.cidade,
        estado = endereco.estado,
        regiao = endereco.regiao
    )
    db.add(dados)
    db.commit()

@router.delete("/deletar-endereco/{id}")
def deletar_endereco(id: int, db: Session = Depends(get_db)):
    # query = "DELETE FROM tb_enderecos WHERE id = :id"
    # with engine.connect() as conn:
    #     conn.execute(text(query), {"id": id})
    #     conn.commit()
    # return {"mensagem": "Endereço deletado com sucesso!"}
    dados = db.get(Endereco,  id)
    db.delete(dados)
    db.commit()
    return {"mensagem": "Endereço deletado com sucesso!"}

@router.put("/atualizar-endereco/{id}")
def atualizar_endereco(id: int, endereco: EnderecoUpdateIn, db: Session = Depends(get_db)):
    # # pega só os campos que foram enviados
    # dados = endereco.model_dump(exclude_unset=True)
    # # monta o SET dinamicamente (ex: "bairro = :bairro, cidade = :cidade")
    # campos_sql = ", ".join([f"{chave} = :{chave}" for chave in dados.keys()])
    # query = f"UPDATE tb_enderecos SET {campos_sql} WHERE id = :id"
    # with engine.connect() as conn:
    #     conn.execute(text(query), {"id": id, **dados})
    #     conn.commit()
    # return {"mensagem": "Endereço atualizado com sucesso!"}
    dados = db.get(Endereco, id)
    campos = endereco.model_dump(exclude_unset=True)
    for chave, valor in campos.items():
        setattr(dados, chave, valor)
    db.commit()
    return {"mensagem": "Endereço atualizado com sucesso!"}