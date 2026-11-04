from components.base_tela import TelaBase
import streamlit as st
from connection.base_api import BaseAPI
import pandas as pd

class AlunoTela(TelaBase):

  def __init__(self):
    self.base = BaseAPI()
    self.titulo = "Tela de Aluno"
    self.descricao = "Essa tela é usada para consultar alunos"

  def consultar(self):
    endpoint = "/alunos/pegar-dados-alunos"
    dados = self.base.get(endpoint)
    return dados

  def consultar_por_id(self, id):
      endpoint = f"/alunos/pegar-dados-alunos-por-id/{id}"
      dados = self.base.get(endpoint)
      return dados

  def criar(self, params):
    endpoint = "/alunos/criar-aluno-com-cep"
    return self.base.post(endpoint, params)

  def atualizar(self, id, params):
    endpoint = f"/alunos/atualizar-aluno/{id}"
    return self.base.put(endpoint, params)

  def deletar(self, id):
    endpoint = f"/alunos/deletar-aluno/{id}"
    return self.base.delete(endpoint)

  def criar_dataframe(self, dados):
    df = pd.DataFrame(dados)
    st.dataframe(df)
  
  def renderizar(self):
    super().cabecalho(self.titulo, self.descricao)
    abas = st.tabs(["Consultar todos", "Consultar por ID", "Criar Aluno", "Atualizar Aluno", "Deletar Aluno"])
    with abas[0]:
      dados = self.consultar()
      self.criar_dataframe(dados)
    with abas[1]:
      id = st.text_input("Digite o ID do aluno:")
      if st.button("Consultar aluno por ID"):
        dados = self.consultar_por_id(id)
        df = pd.DataFrame([dados])
        st.dataframe(df)
    with abas[2]:
      matricula = st.text_input("Digite a matrícula do aluno")
      nome = st.text_input("Digite o nome do aluno")
      email = st.text_input("Digite o email do aluno")
      cep = st.text_input("Digite o CEP do aluno")
      if st.button("Criar aluno"):
        params = {
          "matricula": matricula,
          "nome_aluno": nome,
          "email": email,
          "cep": cep
        }
        retorno = self.criar(params)
        if retorno.status_code == 200:
          st.success("Aluno criado com sucesso")
        else:
          st.error(retorno.text)

    with abas[3]:
      id = st.text_input("Digite o ID do aluno que deseja atualizar")
      matricula = st.text_input("Digite a matrícula do aluno que deseja atualizar")
      nome = st.text_input("Digite o novo nome do aluno")
      email = st.text_input("Digite o novo email do aluno")
      endereco_id = st.text_input("Digite o novo ID do endereço do aluno")
      if st.button("Atualizar aluno"):
        params = {
          "matricula": matricula,
          "nome_aluno": nome,
          "email": email,
          "endereco_id": endereco_id
        }
        params = {chave : valor for chave, valor in params.items() if valor not in ("", None)}
        retorno = self.atualizar(int(id), params)
        if retorno.status_code == 200:
          st.success("Aluno atualizado com sucesso")
        else:
          st.error(retorno.text)
    with abas[4]:
      id = st.text_input("Digite o ID do aluno que deseja deletaar")
      if st.button("Deletar aluno"):
        if not id:
          st.error("Digite o ID do aluno")
        else:
          retorno = self.deletar(int(id))
          if retorno.status_code == 200:
            st.success("Aluno deletado com sucesso")
          else:
            st.error(retorno.text)
    super().rodape()

AlunoTela().renderizar()