import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import gspread
from google.oauth2.service_account import Credentials
import os

import streamlit as st
import json
from google.oauth2.service_account import Credentials

import json
from google.oauth2.service_account import Credentials
import streamlit as st

info = dict(st.secrets["google_credentials"])
info["private_key"] = info["private_key"].replace("\\n", "\n")

credenciais = Credentials.from_service_account_info(info)


info = st.secrets["google_credentials"]
credenciais = Credentials.from_service_account_info(info)

# Configuração da página
st.set_page_config(page_title="Verificação", layout="centered")

# Google Sheets
SHEET_ID = "1iw5uB1nj3cHij7FrVqPWBRyP1Tjl-5aQSbwaYLAaHa8"
ABA_NOME = "verificacoes"
CRED_FILE = "credenciais.json"
escopos = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/spreadsheets"]
credenciais = Credentials.from_service_account_file(CRED_FILE, scopes=escopos)
cliente = gspread.authorize(credenciais)
aba = cliente.open_by_key(SHEET_ID).worksheet(ABA_NOME)
dados = aba.get_all_records()
df = pd.DataFrame(dados)

# Título
st.markdown("<h4 style='text-align:center;'>🔧 Verificação de Equipamentos</h4>", unsafe_allow_html=True)

# Controle de navegação
if "idx" not in st.session_state:
    st.session_state.idx = 0

equipamentos_unicos = df["Equipamento"].unique().tolist()
col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️", key="voltar"):
        st.session_state.idx = (st.session_state.idx - 1) % len(equipamentos_unicos)

with col2:
    if st.button("➡️", key="avancar"):
        st.session_state.idx = (st.session_state.idx + 1) % len(equipamentos_unicos)


equipamento = st.selectbox("Equipamento", equipamentos_unicos + ["Novo"], index=st.session_state.idx)

if equipamento == "Novo":
    equipamento = st.text_input("Novo nome")
else:
    imagem_path = f"imagens/{equipamento}.jpg"
    if os.path.exists(imagem_path):
        st.image(imagem_path, width=150)

dados_eq = df[df["Equipamento"] == equipamento]
if not dados_eq.empty:
    ultimo = dados_eq.sort_values("Data", ascending=False).iloc[0]
    st.markdown(f"<small>Último valor: <b>{ultimo['Valor']} mg/L</b></small>", unsafe_allow_html=True)
    st.markdown(f"<small>Validade: <b>{ultimo['Validade']}</b></small>", unsafe_allow_html=True)
    try:
        validade_data = datetime.strptime(ultimo['Validade'], "%d/%m/%Y")
        if validade_data < datetime.today():
            st.error("⚠️ Vencido")
    except:
        st.warning("Data inválida")

st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
st.markdown("<b><small>Inserir nova verificação</small></b>", unsafe_allow_html=True)

# Inputs compactos
valor = st.number_input("Valor (mg/L)", min_value=0.0, step=0.001, format="%.3f", key="valor")
data = st.date_input("Data", value=datetime.today(), key="data")
validade = st.date_input("Validade", value=datetime.today() + timedelta(days=180), key="validade")
obs = st.text_area("Obs", key="obs")

if st.button("Salvar", key="salvar"):
    nova_linha = [equipamento, valor, data.strftime("%d/%m/%Y"), validade.strftime("%d/%m/%Y"), obs]
    aba.append_row(nova_linha)
    st.success("Salvo!")
    st.experimental_rerun()

if st.button("Equipamento ausente", key="ausente"):
    hoje = datetime.today()
    aba.append_row([equipamento, "", hoje.strftime("%d/%m/%Y"), (hoje + timedelta(days=180)).strftime("%d/%m/%Y"), "Equipamento ausente"])
    st.success("Ausência registrada.")
    st.experimental_rerun()

st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
st.markdown("<small><b>📄 PDF da semana</b></small>", unsafe_allow_html=True)

# PDF
df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")
semana = df[df["Data"] >= datetime.today() - timedelta(days=7)]

if st.button("Gerar PDF", key="pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 8, txt="Relatório Semanal", ln=True, align="C")
    pdf.ln(5)
    for _, row in semana.iterrows():
        texto = f"{row['Equipamento']}, {row['Valor']} mg/L, {row['Data'].strftime('%d/%m/%Y')}, Val.: {row['Validade']}\nObs: {row['Observacoes']}\n"
        pdf.multi_cell(0, 8, texto)
    pdf_file = "relatorio_semanal.pdf"
    pdf.output(pdf_file)
    with open(pdf_file, "rb") as f:
        st.download_button("📥 Baixar", f, file_name=pdf_file)


import os

os.system("git config --global user.name 'Eduardoguerraj1'")
os.system("git config --global user.email 'eduardoquimica@poli.ufrj.br'")


#git config --global user.name "Eduardoguerraj1"
#git config --global user.email "eduardoquimica@poli.ufrj.br"


# streamlit run PEL.py
