import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

def conectar_planilha(json_credenciais, sheet_id, aba_nome):
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credenciais = Credentials.from_service_account_file(json_credenciais, scopes=escopos)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(sheet_id)
    aba = planilha.worksheet(aba_nome)
    return aba

def carregar_dados(aba):
    try:
        dados = aba.get_all_records()
        if not dados:
            return pd.DataFrame(columns=["Data", "Valor (mg/L)", "Lote"])
        df = pd.DataFrame(dados)
        df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors="coerce")
        return df
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(columns=["Data", "Valor (mg/L)", "Lote"])

def salvar_dados(aba, df):
    try:
        # Carregar os dados existentes da planilha
        dados_existentes = aba.get_all_records()
        df_existente = pd.DataFrame(dados_existentes)
        
        # Se já existir dados, adicionar as novas amostras no final
        if not df_existente.empty:
            # Concatenar dados existentes com os novos dados
            df = pd.concat([df_existente, df], ignore_index=True)
        
        # Atualizar os dados na planilha
        aba.clear()  # Limpa a planilha para evitar sobrescrita de cabeçalhos
        aba.update([df.columns.values.tolist()] + df.values.tolist())
        
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
