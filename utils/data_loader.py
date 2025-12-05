import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    """Carrega dados do arquivo parquet processado"""
    try:
        # Tentar carregar parquet existente
        if os.path.exists("requisicoes_data.parquet"):
            df = pd.read_parquet("requisicoes_data.parquet")
            return df
        else:
            st.error("Arquivo de dados não encontrado. Faça upload dos arquivos primeiro.")
            return None
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None