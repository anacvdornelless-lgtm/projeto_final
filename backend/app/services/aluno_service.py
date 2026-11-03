import requests
from app.models import Aluno, Endereco


def criar_aluno(db, aluno):
    # Chama a API do ViaCEP
    dados = requests.get(f"https://viacep.com.br/ws/{aluno.cep}/json/").json()

    # Salva o endereço que veio da API
    endereco = Endereco(cep=aluno.cep, endereco=dados["logradouro"], bairro=dados["bairro"],
                        cidade=dados["localidade"], estado=dados["uf"], regiao=dados["regiao"])
    db.add(endereco)
    db.flush()

    # Salva o aluno com o id do endereço
    db.add(Aluno(matricula=aluno.matricula, nome_aluno=aluno.nome_aluno,
                 email=aluno.email, endereco_id=endereco.id))
    db.commit()