from app.models import Aluno, Endereco
from app.services.cep_service import buscar_cep


def criar_aluno(db, aluno):
    # 1. Pega o endereço na API pelo CEP
    dados = buscar_cep(aluno.cep)

    # 2. Cadastra o endereço
    endereco = Endereco(cep=aluno.cep, endereco=dados["logradouro"], bairro=dados["bairro"],
                        cidade=dados["localidade"], estado=dados["uf"], regiao=dados["regiao"])
    db.add(endereco)
    db.flush()  # gera o endereco.id

    # 3. Cadastra o aluno com o id do endereço
    db.add(Aluno(matricula=aluno.matricula, nome_aluno=aluno.nome_aluno,
                 email=aluno.email, endereco_id=endereco.id))
    db.commit()
