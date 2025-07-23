import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from plotly import graph_objs as go

# Carrega variáveis de ambiente do .env (funciona apenas localmente)
load_dotenv()

# Função para conectar ao banco
def connect_to_db():
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")  # Define 5432 como padrão se não definido

    # Verifica variáveis ausentes
    missing_vars = [
        var_name for var_name, var_value in {
            "POSTGRES_USER": db_user,
            "POSTGRES_PASSWORD": db_password,
            "POSTGRES_DB": db_name,
            "DB_HOST": db_host,
            "DB_PORT": db_port,
        }.items() if not var_value
    ]
    if missing_vars:
        raise ValueError(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")

    # String de conexão
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)
    return engine

# Executa query
def run_query(query, engine):
    with engine.connect() as conn:
        return pd.read_sql_query(query, conn)

# Geração dos gráficos
def create_plot(df, plot_type):
    if plot_type == "bar":
        return go.Figure(data=[go.Bar(x=df["titulo"], y=df["preco"])])
    elif plot_type == "line":
        return go.Figure(data=[go.Scatter(x=df.index, y=df["preco"], mode="lines+markers")])
    elif plot_type == "scatter":
        return go.Figure(data=[go.Scatter(x=df["titulo"], y=df["preco"], mode="markers")])
    elif plot_type == "pie":
        return go.Figure(data=[go.Pie(labels=df["titulo"], values=df["preco"])])

# Função principal
def main():
    st.title("Gerenciador de Produtos")

    try:
        engine = connect_to_db()
        query = "SELECT DISTINCT titulo, preco FROM produtos ORDER BY preco DESC"
        df = run_query(query, engine)
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return

    st.write("Produtos:")
    st.dataframe(df)

    uploaded_file = st.file_uploader("Carregar arquivo Excel", type="xlsx")
    if uploaded_file is not None:
        excel_data = pd.read_excel(uploaded_file)
        df = pd.concat([df, excel_data])
        df = df.nlargest(5, "preco")

    st.write("Top 5 Produtos (Atualizado):")
    st.dataframe(df)

    plot_types = ["bar", "line", "scatter", "pie"]
    plot_type = st.selectbox("Selecione o tipo de gráfico", plot_types)
    plot = create_plot(df, plot_type)
    st.plotly_chart(plot)

    # Inputs adicionais
    st.date_input("Escolha uma data")
    texto = st.text_input("Digite algo")
    numero = st.slider("Escolha um número", 0, 100)
    opcao = st.radio("Escolha uma opção", ["Opção 1", "Opção 2", "Opção 3"])
    check = st.checkbox("Marque a opção")
    cor = st.color_picker("Escolha uma cor")

    st.write("Texto digitado:", texto)
    st.write("Número escolhido:", numero)
    st.write("Opção selecionada:", opcao)
    st.write("Checkbox marcado:", check)
    st.write("Cor escolhida:", cor)

if __name__ == "__main__":
    main()
