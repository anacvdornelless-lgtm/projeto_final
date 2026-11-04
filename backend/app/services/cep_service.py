import requests


def buscar_cep(cep):
    # Manda o CEP para o ViaCEP e devolve o endereço
    return requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
