import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from sheets_utils import conectar_planilha, carregar_dados, salvar_dados

# Configurações
json_credenciais = "credenciais.json"
sheet_id = "1iw5uB1nj3cHij7FrVqPWBRyP1Tjl-5aQSbwaYLAaHa8"
aba_nome = "dados"

# Conecta à planilha
aba = conectar_planilha(json_credenciais, sheet_id, aba_nome)

# Configuração da página
st.set_page_config(page_title="Carta de Controle", layout="wide")
st.title("Carta de Controle de Ensaios")

# Número de amostras
num_amostras = st.number_input("Número de amostras", min_value=1, max_value=50, value=1)

# Inicializa os dados na sessão
if 'dados' not in st.session_state:
    st.session_state.dados = []

# Formulário para inserção de amostras
for i in range(num_amostras):
    st.markdown(f"### Amostra {i+1}")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 2])

    with col1:
        dia = st.text_input("Dia", max_chars=2, key=f"dia_{i}")
    with col2:
        mes = st.text_input("Mês", max_chars=2, key=f"mes_{i}")
    with col3:
        ano = st.text_input("Ano", max_chars=2, key=f"ano_{i}")
    with col4:
        valor = st.number_input("Valor (mg/L)", min_value=0.0, format="%.3f", key=f"valor_{i}")
    with col5:
        lote = st.text_input("Lote", key=f"lote_{i}")

    if st.button(f"Adicionar Amostra {i+1}", key=f"adicionar_{i}"):
        try:
            data_str = f"20{ano.zfill(2)}-{mes.zfill(2)}-{dia.zfill(2)}"
            data_formatada = datetime.strptime(data_str, "%Y-%m-%d")
            st.session_state.dados.append({
                "Data": data_formatada,
                "Valor (mg/L)": valor,
                "Lote": lote
            })
            st.success(f"Amostra {i+1} adicionada com sucesso!")
        except ValueError:
            st.error(f"Data inválida para Amostra {i+1}. Verifique o dia, mês e ano.")

st.markdown("---")

# Exibição dos dados e geração da carta de controle
if st.session_state.dados:
    st.subheader("Amostras Registradas")
    dados_df = pd.DataFrame(st.session_state.dados)
    dados_df = dados_df.sort_values(by="Data")
    st.dataframe(dados_df, use_container_width=True)

    if st.button("Gerar Carta de Controle"):
        padrao = 0.1
        limite_superior = padrao * 1.10
        limite_inferior = padrao * 0.90

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(dados_df["Data"], dados_df["Valor (mg/L)"], marker='o', color='blue', label='Resultados')
        ax.axhline(padrao, color='green', linestyle='--', label='Padrão (0,1 mg/L)')
        ax.axhline(limite_superior, color='red', linestyle='--', label='Limite Superior (+10%)')
        ax.axhline(limite_inferior, color='red', linestyle='--', label='Limite Inferior (-10%)')
        ax.fill_between(dados_df["Data"], limite_inferior, limite_superior, color='red', alpha=0.1)
        ax.set_title("Carta de Controle de Ensaios")
        ax.set_xlabel("Data")
        ax.set_ylabel("Valor (mg/L)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # Botão de salvar
    if st.button("Salvar no Google Sheets"):
        dados_para_salvar = dados_df.copy()
        dados_para_salvar["Data"] = dados_para_salvar["Data"].dt.strftime("%d/%m/%Y")
        salvar_dados(aba, dados_para_salvar)
        st.success("Dados salvos com sucesso no Google Sheets!")

else:
    st.info("Nenhuma amostra foi adicionada ainda.")
