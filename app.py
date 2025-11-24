import streamlit as st
import pandas as pd
import io
import os

from modelo import TreinadorModelo
from utils import encrypt_bytes, carregar_chave

st.set_page_config(page_title="Regressão Linear Criptografada", layout="centered")

# Garante a existência de chave AES
key = carregar_chave()

modelo = TreinadorModelo()

st.title("📈 Sistema de Regressão Linear com Criptografia AES (pyaes)")

# ============================================================
# TREINO
# ============================================================
st.header("⚙️ Treinar Modelo")

file_train = st.file_uploader("Envie o CSV de treino", type=["csv"], key="train")

if file_train:
    raw = file_train.read()  # bytes

    df_train = pd.read_csv(io.BytesIO(raw))
    st.write("Pré-visualização da base de treino:")
    st.dataframe(df_train.head())

    mse = modelo.treinar(df_train)
    modelo.salvar()

    st.success(f"Treino concluído! MSE: {mse:.4f}")

    # Salvar criptografado localmente
    os.makedirs("uploads", exist_ok=True)
    encrypted_path = f"uploads/treino_{file_train.name}.aes"

    with open(encrypted_path, "wb") as f:
        f.write(encrypt_bytes(raw, key))

    st.info(f"Arquivo de treino criptografado armazenado em: {encrypted_path}")


# ============================================================
# TESTE
# ============================================================
st.header("🧪 Testar Modelo")

file_test = st.file_uploader("Envie o CSV de teste", type=["csv"], key="test")
tem_rotulos = st.checkbox("O CSV contém rótulo ('time')?")

if file_test:
    raw_test = file_test.read()
    df_test = pd.read_csv(io.BytesIO(raw_test))

    st.write("Pré-visualização da base de teste:")
    st.dataframe(df_test.head())

    preds, desempenho = modelo.testar(df_test, tem_rotulos)

    # CSV puro para download
    csv_bytes = preds.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Baixar previsões (CSV)",
        data=csv_bytes,
        file_name="predicoes.csv",
        mime="text/csv"
    )

    # CSV criptografado
    enc_preds = encrypt_bytes(csv_bytes, key)

    st.download_button(
        "🔒 Baixar previsões criptografadas (AES)",
        data=enc_preds,
        file_name="predicoes.csv.aes",
        mime="application/octet-stream"
    )

    if desempenho is not None:
        st.success(f"Desempenho (MSE): {desempenho:.4f}")


# ============================================================
# RESET
# ============================================================
st.header("🔁 Resetar Modelo")

if st.button("Resetar Modelo"):
    modelo.resetar()
    st.success("Modelo resetado com sucesso!")
