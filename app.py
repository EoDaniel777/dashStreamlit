import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import requests
from requests.auth import HTTPBasicAuth
import plotly.express as px
import plotly.graph_objects as go

# Configurações de estilo
st.set_page_config(page_title="Senar Pernambuco", layout="wide", initial_sidebar_state="expanded")

# Função para buscar dados da API
def fetch_data_from_api(url, user, password):
    response = requests.get(url, auth=HTTPBasicAuth(user, password))
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro ao buscar dados da API: {response.status_code}")
        return None

# URL da API e credenciais
api_url = "http://apisenarpe.dematech.io:8051/api/framework/v1/consultaSQLServer/RealizaConsulta/WS.ORC.REAL.DASH/1/T?"
api_user = st.secrets["API_USER"]
api_password = st.secrets["API_PASSWORD"]

# Buscar dados da API
data = fetch_data_from_api(api_url, api_user, api_password)

# Função para classificar CODCLASSIFICA
def classify_codclassifica(codclassifica):
    if codclassifica == "01":
        return "Meio"
    elif codclassifica == "02":
        return "FIM"
    elif codclassifica == "03":
        return "Recurso de Terceiro"
    else:
        return "Não Classificado"

# Classificar e processar os dados
if data:
    # Verificar a estrutura dos dados retornados pela API
    if isinstance(data, list) and len(data) > 0:
        df = pd.DataFrame(data)
        df["Classificacao"] = df["CODCLASSIFICA"].apply(classify_codclassifica)
        df = df[df["Classificacao"] != "Não Classificado"]  # Remover opção "Não Classificado"
    else:
        st.error("Dados da API não estão no formato esperado.")
else:
    st.error("Falha ao obter dados da API.")

# Comparação por trimestre
df["Trimestre1"] = df["Janeiro"] + df["Fevereiro"] + df["Março"]
df["Trimestre2"] = df["Abril"] + df["Maio"] + df["Junho"]
df["Trimestre3"] = df["Julho"] + df["Agosto"] + df["Setembro"]
df["Trimestre4"] = df["Outubro"] + df["Novembro"] + df["Dezembro"]

df_trimestral = df.groupby("Classificacao")[["Trimestre1", "Trimestre2", "Trimestre3", "Trimestre4"]].sum().reset_index()

# Comparação do mês de Janeiro
df_janeiro = df.groupby("Classificacao")[["Janeiro"]].sum().reset_index()

# Natureza mais gasta do mês de Janeiro por área
df_natureza_janeiro = df.loc[df.groupby("Classificacao")["Janeiro"].idxmax()]

# Sidebar
svg_file_path = "dematech.svg"
if not os.path.isfile(svg_file_path):
    st.error(f"Arquivo {svg_file_path} não encontrado. Verifique se o arquivo está no local correto.")
else:
    # Leitura do arquivo SVG
    with open(svg_file_path, "r") as file:
        svg_icon = file.read()

    # Codificação do SVG para base64
    svg_base64 = base64.b64encode(svg_icon.encode()).decode()

    st.sidebar.markdown(f"""
        <div style="text-align:center;">
            <img src="data:image/svg+xml;base64,{svg_base64}" style="width:100%; height:auto;" />
        </div>
    """, unsafe_allow_html=True)

st.sidebar.title("Opções")
st.sidebar.radio("Escolha uma opção:", ["Natureza", "Serviços"])

# Ajuste do estilo do título
title_html = """
    <div style="padding:10px;margin-top:-70px;">
    <h1 style="color:white;text-align:center;">Senar Pernambuco</h1>
    </div>
    """
st.markdown(title_html, unsafe_allow_html=True)

# Configuração dos gráficos
figsize = (6, 4)

# Gráficos lado a lado
col1, col2 = st.columns(2)

# Gráfico de comparação por trimestre
with col1:
    st.subheader('Comparação por Trimestre')
    fig1 = px.bar(df_trimestral, x='Classificacao', y=['Trimestre1', 'Trimestre2', 'Trimestre3', 'Trimestre4'], title='Comparação por Trimestre', labels={'value':'Valores', 'variable':'Trimestre'}, barmode='group')
    fig1.update_layout(xaxis_title='Classificação', yaxis_title='Valores')
    fig1.update_xaxes(tickangle=0)  # Deixar as palavras retas
    st.plotly_chart(fig1)

# Gráfico de comparação do mês de Janeiro
with col2:
    st.subheader('Comparação do Mês de Janeiro')
    fig2 = px.bar(df_janeiro, x='Classificacao', y='Janeiro', title='Comparação do Mês de Janeiro', labels={'Janeiro':'Valores'})
    fig2.update_layout(xaxis_title='Classificação', yaxis_title='Valores')
    fig2.update_xaxes(tickangle=0)  # Deixar as palavras retas
    st.plotly_chart(fig2)

# Natureza mais gasta do mês de Janeiro por área
col3, col4 = st.columns(2)

with col3:
    st.subheader('Natureza Mais Gasta do Mês de Janeiro por Área')
    fig3 = px.bar(df_natureza_janeiro, x='Classificacao', y='Janeiro', title='Natureza Mais Gasta do Mês de Janeiro por Área', labels={'Janeiro':'Valores'})
    fig3.update_layout(xaxis_title='Classificação', yaxis_title='Valores')
    fig3.update_xaxes(tickangle=0)  # Deixar as palavras retas
    st.plotly_chart(fig3)

# Comparação dos serviços mais feitos em cada área
with col4:
    st.subheader('Serviço Mais Feito em Cada Área')
    df_servico = df.loc[df.groupby("Classificacao")["Total"].idxmax()]
    fig4 = px.bar(df_servico, x='Classificacao', y='Total', title='Serviço Mais Feito em Cada Área', labels={'Total':'Valores'})
    fig4.update_layout(xaxis_title='Classificação', yaxis_title='Valores')
    fig4.update_xaxes(tickangle=0)  # Deixar as palavras retas
    st.plotly_chart(fig4)
