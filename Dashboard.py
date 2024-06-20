import pandas as pd
import requests 
import streamlit as st
import plotly.express as px

st.set_page_config(layout='wide',
                   page_title='Dashboard de Vendas - Alura',
                   page_icon=':shopping_trolley:',
                   initial_sidebar_state='auto')

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

#Funções auxiliares
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

#Tabelas

url = 'https://labdados.com/produtos'

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(),
                'ano':ano}

@st.cache_data
def fetch_and_clean_data(url_api, parametros):
    return requests.get(url_api, params = parametros)

response = fetch_and_clean_data(url, query_string)

dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas para aba de receita
receita_estado = dados.groupby(['Local da compra', 'lat', 'lon']).agg({'Preço': 'sum'}).reset_index().sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')['Preço'].sum().reset_index().sort_values('Preço', ascending=False)

## Tabelas para aba de quantidade
qtd_estado = dados.groupby(['Local da compra', 'lat', 'lon']).agg({'Produto': 'count'}).reset_index().sort_values('Produto', ascending=False)
qtd_estado.columns = ['Local da compra', 'lat', 'lon', 'Qtd']

qtd_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Produto'].count().reset_index()
qtd_mensal.columns = ['Data da Compra', 'Qtd']
qtd_mensal['Ano'] = qtd_mensal['Data da Compra'].dt.year
qtd_mensal['Mês'] = qtd_mensal['Data da Compra'].dt.month_name()

qtd_categorias = dados.groupby('Categoria do Produto')['Produto'].count().reset_index().sort_values('Produto', ascending=False)
qtd_categorias.columns = ['Categoria do Produto', 'Qtd']

## Tabelas para aba de vendedores
vendedores = dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']).reset_index()
vendedores.columns = ['Vendedor', 'Receita', 'Qtd']
vendedores = vendedores.sort_values('Receita', ascending=False)
#Gráficos

## Aba de receita
fig_mapa_receita = px.scatter_geo(receita_estado,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name='Local da compra',
                                  hover_data= {'lat':False, 'lon':False},
                                  title = 'Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y=(0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash= 'Ano',
                             title= 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estado.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (Receita)'
                             )
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias.head(),
                             x = 'Categoria do Produto',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Receita por Categoria de Produto'
                             )
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Aba de receita
fig_mapa_qtd = px.scatter_geo(qtd_estado,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Qtd',
                                  template = 'seaborn',
                                  hover_name='Local da compra',
                                  hover_data= {'lat':False, 'lon':False},
                                  title = 'Quantidade por Estado')

fig_qtd_mensal = px.line(qtd_mensal,
                             x = 'Mês',
                             y = 'Qtd',
                             markers = True,
                             range_y=(0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash= 'Ano',
                             title= 'Quantidade Mensal')

fig_qtd_estados = px.bar(qtd_estado.head(),
                             x = 'Local da compra',
                             y = 'Qtd',
                             text_auto = True,
                             title = 'Top estados (Quantidade)'
                             )

fig_qtd_categorias = px.bar(qtd_categorias.head(),
                             x = 'Categoria do Produto',
                             y = 'Qtd',
                             text_auto = True,
                             title = 'Quantidade por Categoria de Produto'
                             )

#Visualização

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])



with aba1:
    col1, col2 = st.columns(2)

    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)

    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_qtd, use_container_width=True)
        st.plotly_chart(fig_qtd_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtd_mensal, use_container_width=True)
        st.plotly_chart(fig_qtd_categorias, use_container_width=True)
        
with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores',  2, 10, 5) #min, max, padrao
    col1, col2 = st.columns(2)

    with col1:
        st.metric(f'Receita Top {qtd_vendedores} Vendedores',
                   formata_numero(vendedores.head(qtd_vendedores)['Receita'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores.head(qtd_vendedores).sort_values('Receita'),
                                        y = 'Vendedor',
                                        x = 'Receita',
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores por Receita'
                                        )
        st.plotly_chart(fig_receita_vendedores)
    with col2:
        st.metric(f'Quantidade Top {qtd_vendedores} Vendedores',
                   formata_numero(vendedores.sort_values('Qtd', ascending=False).head(qtd_vendedores)['Qtd'].sum()))
        fig_receita_vendedores = px.bar(vendedores.sort_values('Qtd', ascending=False).head(qtd_vendedores).sort_values('Qtd'),
                                        y = 'Vendedor',
                                        x = 'Qtd',
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores por Quantidade'
                                        )
        st.plotly_chart(fig_receita_vendedores)

#st.dataframe(dados.head())