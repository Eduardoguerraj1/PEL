import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from sheets_utils import conectar_planilha, carregar_dados, salvar_dados

# Substitua pelos seus dados:
json_credenciais = "credenciais.json"
sheet_id = "1iw5uB1nj3cHij7FrVqPWBRyP1Tjl-5aQSbwaYLAaHa8"  # Cole o ID da planilha aqui
aba_nome = "dados"

# Conecta à planilha no início do app
aba = conectar_planilha(json_credenciais, sheet_id, aba_nome)
df_antigos = carregar_dados(aba)

# Verifique se os dados antigos foram carregados corretamente
if not df_antigos.empty:
    st.write("Dados antigos carregados com sucesso!")
else:
    st.write("Nenhum dado antigo encontrado.")

st.set_page_config(page_title="Carta de Controle", layout="wide")
st.title("Carta de Controle de Ensaios")

# Selecionar número de amostras
num_amostras = st.number_input("Número de amostras", min_value=1, max_value=50, value=1)

# Inicializa a lista de dados na sessão
if 'dados' not in st.session_state:
    st.session_state.dados = []

# Campos para cada amostra
for i in range(num_amostras):
    st.markdown(f"### Amostra {i+1}")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 2])

    with col1:
        dia = st.text_input(f"Dia", max_chars=2, key=f"dia_{i}")
    with col2:
        mes = st.text_input(f"Mês", max_chars=2, key=f"mes_{i}")
    with col3:
        ano = st.text_input(f"Ano", max_chars=2, key=f"ano_{i}")
    with col4:
        valor = st.number_input("Valor (mg/L)", min_value=0.0, format="%.3f", key=f"valor_{i}")
    with col5:
        lote = st.text_input("Lote", key=f"lote_{i}")

    # Botão para adicionar os dados dessa amostra
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

# Exibir os dados inseridos
if len(st.session_state.dados) > 0 or not df_antigos.empty:
    st.subheader("Dados Inseridos")
    
    # Mescla os dados antigos com os novos
    dados_df = pd.DataFrame(st.session_state.dados)
    if not df_antigos.empty:
        df_antigos["Data"] = pd.to_datetime(df_antigos["Data"], errors='coerce')  # Garantir que "Data" esteja no formato datetime
        dados_df = pd.concat([df_antigos, dados_df], ignore_index=True)
    
    dados_df = dados_df.sort_values(by="Data")
    st.dataframe(dados_df)

    # Botão para gerar o gráfico
    if st.button("Gerar Carta de Controle"):
        # Parâmetros da carta de controle
        padrao = 0.1  # mg/L
        limite_superior = padrao * 1.10
        limite_inferior = padrao * 0.90

        # Criar o gráfico
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
else:
    st.info("Nenhuma amostra foi adicionada ainda.")

# Salvar no Google Sheets
salvar_dados(aba, dados_df)
st.success("Dados salvos com sucesso no Google Sheets!")
