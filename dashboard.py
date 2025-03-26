import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Hellu's & MyBroker", layout="wide")

st.title("📊 Dashboard")

# Carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel("dados.xlsx")
    df.columns = [col.strip() for col in df.columns]  # limpa espaços
    df["Crédito Desejado (R$)"] = df["Crédito Desejado (R$)"].replace(
        {"R\$ ": "", ",": "", ".": ""}, regex=True
    ).astype(float)
    df["Data da Solicitação"] = pd.to_datetime(df["Data da Solicitação"])
    return df

df = carregar_dados()

# Filtros na sidebar
st.sidebar.header("🔎 Filtros")
corretor = st.sidebar.multiselect("Corretor Responsável", df["Corretor Responsável"].unique())
finalidade = st.sidebar.multiselect("Finalidade do Crédito", df["Finalidade do Crédito"].unique())
unidade = st.sidebar.multiselect("Unidade da Corretora", df["Unidade da Corretora"].unique())

# Aplicar filtros
df_filtrado = df.copy()
if corretor:
    df_filtrado = df_filtrado[df_filtrado["Corretor Responsável"].isin(corretor)]
if finalidade:
    df_filtrado = df_filtrado[df_filtrado["Finalidade do Crédito"].isin(finalidade)]
if unidade:
    df_filtrado = df_filtrado[df_filtrado["Unidade da Corretora"].isin(unidade)]

# Gráfico 1 – Total de crédito por finalidade
fig1 = px.bar(
    df_filtrado.groupby("Finalidade do Crédito")["Crédito Desejado (R$)"].sum().reset_index(),
    x="Finalidade do Crédito",
    y="Crédito Desejado (R$)",
    title="💰 Total de Crédito por Finalidade",
    color="Finalidade do Crédito",
)

# Gráfico 2 – Solicitações por corretor
df_corretores = df_filtrado["Corretor Responsável"].value_counts().reset_index()
df_corretores.columns = ["Corretor", "Quantidade"]

fig2 = px.bar(
    df_corretores,
    x="Corretor",
    y="Quantidade",
    title="👤 Solicitações por Corretor",
    color="Corretor"
)


# Gráfico 3 – Status da negociação (pizza)
fig3 = px.pie(
    df_filtrado,
    names="Status da Negociação",
    title="📌 Status da Negociação"
)

# Gráfico 4 – Crédito por unidade da corretora
fig4 = px.bar(
    df_filtrado.groupby("Unidade da Corretora")["Crédito Desejado (R$)"].sum().reset_index(),
    x="Unidade da Corretora",
    y="Crédito Desejado (R$)",
    title="🏢 Crédito por Unidade da Corretora",
    color="Unidade da Corretora"
)

# Gráfico 5 – Evolução ao longo do tempo
fig5 = px.line(
    df_filtrado.groupby("Data da Solicitação")["Crédito Desejado (R$)"].sum().reset_index(),
    x="Data da Solicitação",
    y="Crédito Desejado (R$)",
    title="📈 Evolução do Crédito Solicitado por Data"
)

# Layout em colunas
col1, col2 = st.columns(2)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
col3.plotly_chart(fig3, use_container_width=True)
col4.plotly_chart(fig4, use_container_width=True)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.caption("Feito com 💙 por HiCon Soluções Integradas de Marketing e IA.")
