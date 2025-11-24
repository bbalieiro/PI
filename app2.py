# app.py
import streamlit as st
import pandas as pd
import io
import os
from modelo import TreinadorModelo
from utils import compress_bytes_to_zip, encrypt_bytes_fernet, decrypt_bytes_fernet, carregar_chave, KEY_PATH

st.set_page_config(page_title="Regressão Linear - Compress+Encrypt", layout="centered")
st.title("📈 Regressão Linear — Uploads comprimidos e criptografados (server-side)")

st.sidebar.header("Configuração")
st.sidebar.write("Se possível, defina FERNET_KEY em Settings → Secrets para produção.")
st.sidebar.write("Caso não exista, o app gera secret.key localmente (apenas dev).")

# força existência da chave (gera local se não houver secrets) — apenas dev friendly
try:
    _ = carregar_chave()
except Exception as e:
    st.sidebar.error(f"Erro ao carregar/generar chave: {e}")

modelo = TreinadorModelo()

# ------------------- TREINO -------------------
st.header("⚙️ Treinar modelo")
file_train = st.file_uploader("Envie o CSV de treino (com coluna 'time')", type=["csv"], key="train")

if file_train:
    raw = file_train.read()  # bytes do CSV
    try:
        df_train = pd.read_csv(io.BytesIO(raw))
    except Exception as e:
        st.error(f"Erro ao ler CSV de treino: {e}")
        st.stop()

    st.write("Pré-visualização da base de treino:")
    st.dataframe(df_train.head())

    try:
        mse = modelo.treinar(df_train)
        modelo.salvar()
        st.success(f"Treino concluído! MSE (treino): {mse:.4f}")
    except Exception as e:
        st.error(f"Erro durante treino: {e}")
        st.stop()

    # compressa e criptografa (arquivo para armazenamento / evidência)
    zip_bytes = compress_bytes_to_zip(raw, file_train.name)
    enc_bytes = encrypt_bytes_fernet(zip_bytes)

    os.makedirs("uploads", exist_ok=True)
    save_path = os.path.join("uploads", f"{file_train.name}.zip.enc")
    with open(save_path, "wb") as f:
        f.write(enc_bytes)

    st.info(f"Arquivo comprimido e criptografado salvo localmente em: {save_path}")

    # disponibiliza download criptografado
    st.download_button(
        "🔒 Baixar (comprimido + criptografado)",
        data=enc_bytes,
        file_name=f"{file_train.name}.zip.enc",
        mime="application/octet-stream"
    )

# ------------------- TESTE -------------------
st.header("🧪 Testar modelo")
file_test = st.file_uploader("Envie o CSV de teste", type=["csv"], key="test")
tem_rotulos = st.checkbox("O CSV contém rótulos ('time')?")

if file_test:
    raw_test = file_test.read()
    try:
        df_test = pd.read_csv(io.BytesIO(raw_test))
    except Exception as e:
        st.error(f"Erro ao ler CSV de teste: {e}")
        st.stop()

    st.write("Pré-visualização da base de teste:")
    st.dataframe(df_test.head())

    try:
        preds_df, desempenho = modelo.testar(df_test, tem_rotulos)
    except Exception as e:
        st.error(f"Erro ao testar: {e}")
        st.stop()

    # CSV puro (download)
    csv_bytes = preds_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Baixar previsões (CSV)",
        data=csv_bytes,
        file_name="predicoes.csv",
        mime="text/csv"
    )

    # CSV comprimido + criptografado
    zip_bytes = compress_bytes_to_zip(csv_bytes, "predicoes.csv")
    enc_preds = encrypt_bytes_fernet(zip_bytes)

    st.download_button(
        "🔒 Baixar previsões (comprimido + criptografado)",
        data=enc_preds,
        file_name="predicoes.zip.enc",
        mime="application/octet-stream"
    )

    if desempenho is not None:
        st.success(f"Desempenho (MSE): {desempenho:.4f}")

# ------------------- RESET -------------------
st.header("🔁 Resetar Modelo")
if st.button("Resetar Modelo"):
    modelo.resetar()
    st.success("Modelo resetado.")
