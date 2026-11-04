import json
from urllib.request import urlopen
from fastapi import HTTPException
from app.schemas import EnderecoIn


def consultar_cep(cep: str) -> EnderecoIn:
    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        with urlopen(url, timeout=5) as resposta:
            dados = json.load(resposta)
        # Retorna os campos do ViaCEP com os nomes da tb_enderecos
        return EnderecoIn(
            cep=dados["cep"],
            endereco=dados.get("logradouro", ""),
            bairro=dados.get("bairro", ""),
            cidade=dados["localidade"],
            estado=dados["uf"],
            regiao=dados.get("regiao", ""),
        )
    except (OSError, ValueError, KeyError, AttributeError):
        raise HTTPException(status_code=502, detail="Não foi possível consultar o CEP")
