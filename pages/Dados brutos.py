import pandas as pd
import requests 
import streamlit as st
import time

@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = '🔥')
    st.balloons()
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS :game_die:')

url = 'https://labdados.com/produtos'

@st.cache_data
def fetch_and_clean_data(url_api):
    return requests.get(url_api)

response = fetch_and_clean_data(url)

dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0, 5000))
                                   
with st.sidebar.expander('Data de compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))


query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]



st.dataframe(dados_filtrados)

st.markdown(f'### A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva o nome para o arquivo a ser baixado')
coluna1, coluna2 = st.columns(2)
with coluna1:
        nome_arquivo = st.text_input('', label_visibility='collapsed', value = 'dados')
        nome_arquivo += '.csv'
with coluna2:
     st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados),
                         file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)