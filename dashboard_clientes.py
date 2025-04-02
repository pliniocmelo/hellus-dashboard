import streamlit as st
import pandas as pd
import plotly.express as px

# ------ TEMA CUSTOMIZADO ------
def aplicar_estilo():
    st.markdown("""
        <style>
        body {
            background-color: #0f1117;
            color: white;
        }
        .stApp {
            background-color: #0f1117;
        }
        .stMetric label, .stMetric span {
            color: #c9a0ff !important;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .css-1v0mbdj.edgvbvh3 {
            color: #c9a0ff;
        }
        </style>
    """, unsafe_allow_html=True)

# ------ CONFIGURAÇÃO INICIAL ------
st.set_page_config(page_title="Dashboard Hellu's Prime & MyBroker", layout="wide")
aplicar_estilo()
st.title("📊 Dashboard Hellu's Prime & MyBroker")

# ------ CARREGAMENTO DE DADOS ------
sheet_url = "https://docs.google.com/spreadsheets/d/1NBfJeO1i2f6GXQHkCleblbMNvDwFC7ZPx8m9ZiejVWw/export?format=csv"

def carregar_dados():
    df = pd.read_csv(sheet_url)
    df.columns = [col.strip() for col in df.columns]

    # Tratamento de valor em R$
    if "Crédito Desejado (R$)" in df.columns:
        df["Crédito Desejado (R$)"] = (
            df["Crédito Desejado (R$)"].astype(str)
            .str.replace("R$", "")
            .str.replace(".", "", regex=False)
            .str.replace(",", ".")
            .str.strip()
        )
        df["Crédito Desejado (R$)"] = pd.to_numeric(df["Crédito Desejado (R$)"], errors="coerce")

    # Tratamento de data
    if "Data da Solicitação" in df.columns:
        df["Data da Solicitação"] = pd.to_datetime(df["Data da Solicitação"], dayfirst=True, errors="coerce")

    return df

df = carregar_dados()

# ------ FILTROS ------
st.sidebar.markdown("## 🎯 Filtros")
unidades = st.sidebar.multiselect("Unidade da Corretora", df["Unidade da Corretora"].dropna().unique())
corretores = st.sidebar.multiselect("Corretor Responsável", df["Corretor Responsável"].dropna().unique())
status = st.sidebar.multiselect("Status da Negociação", df["Status da Negociação"].dropna().unique())

filtro = pd.Series([True] * len(df))
if unidades:
    filtro &= df["Unidade da Corretora"].isin(unidades)
if corretores:
    filtro &= df["Corretor Responsável"].isin(corretores)
if status:
    filtro &= df["Status da Negociação"].isin(status)

df_filtrado = df[filtro]

# ------ MÉTRICAS GERAIS ------
total_solicitacoes = len(df_filtrado)
total_credito = df_filtrado["Crédito Desejado (R$)"].sum()

col1, col2 = st.columns([1,1])
col1.metric("📌 Total de Solicitações", f"{total_solicitacoes}")
col2.metric("💰 Valor Total Solicitado", f'R$ {total_credito:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# ------ GRÁFICOS ------
st.markdown("### 📈 Visualização Gráfica")

# Gráfico de barras: Total de crédito por Unidade da Corretora
if "Unidade da Corretora" in df_filtrado.columns:
    credito_por_unidade = df_filtrado.groupby("Unidade da Corretora")["Crédito Desejado (R$)"].sum().reset_index()
    fig1 = px.bar(credito_por_unidade, x="Unidade da Corretora", y="Crédito Desejado (R$)", title="Crédito por Unidade", text_auto=True, color_discrete_sequence=["#ffffff"])
    st.plotly_chart(fig1, use_container_width=True)

# Gráfico de pizza: Finalidade do Crédito
if "Finalidade do Crédito" in df_filtrado.columns:
    finalidade_counts = df_filtrado["Finalidade do Crédito"].value_counts().reset_index()
    finalidade_counts.columns = ["Finalidade", "Quantidade"]
    fig2 = px.pie(finalidade_counts, values="Quantidade", names="Finalidade", title="Distribuição por Finalidade")
    st.plotly_chart(fig2, use_container_width=True)

# Gráfico de barras: Total de Crédito por Corretor
if "Corretor Responsável" in df_filtrado.columns:
    credito_por_corretor = df_filtrado.groupby("Corretor Responsável")["Crédito Desejado (R$)"].sum().reset_index()
    fig3 = px.bar(credito_por_corretor, x="Corretor Responsável", y="Crédito Desejado (R$)", title="Crédito por Corretor", text_auto=True, color_discrete_sequence=["#f1bf23"])
    st.plotly_chart(fig3, use_container_width=True)

# Gráfico de linha: Evolução de solicitações ao longo do tempo
if "Data da Solicitação" in df_filtrado.columns:
    solicitacoes_por_data = df_filtrado.groupby("Data da Solicitação").size().reset_index(name="Quantidade")
    fig4 = px.line(solicitacoes_por_data, x="Data da Solicitação", y="Quantidade", title="Evolução de Solicitações")
    st.plotly_chart(fig4, use_container_width=True)

# Gráfico de pizza: Status
if "status" in df_filtrado.columns:
    status_counts = df_filtrado["status"].value_counts().reset_index()
    fig5 = px.pie(status_counts, values="status", names="index", title="Status Geral")
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ------ TABELA DETALHADA ------
df_visual = df_filtrado.copy()

# Formatando valores para exibição
if "Crédito Desejado (R$)" in df_visual.columns:
    df_visual["Crédito Desejado (R$)"] = df_visual["Crédito Desejado (R$)"].apply(lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else "")

if "Data da Solicitação" in df_visual.columns:
    df_visual["Data da Solicitação"] = df_visual["Data da Solicitação"].dt.strftime("%d/%m/%Y")

st.markdown("### 📒 Dados detalhados")
st.dataframe(df_visual, use_container_width=True)

st.markdown("---")
st.caption("Feito com 💜 por Hicon Soluções Integradas de Marketing e IA (34) 9 9717-5427")
