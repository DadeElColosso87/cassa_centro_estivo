import streamlit as st
import pandas as pd
import os

from supabase_client import supabase
from config import CASSE, TIPI, METODI, CATEGORIE

st.set_page_config(page_title="Cassa Centro Estivo", layout="wide")

# CARTELLA SCONTRINI
SCONTRINI_DIR = "scontrini"
if not os.path.exists(SCONTRINI_DIR):
    os.makedirs(SCONTRINI_DIR)

st.title("💰 Cassa Centro Estivo")

# =========================
# SCELTA RUOLO
# =========================
if "ruolo" not in st.session_state:
    st.session_state.ruolo = None

if st.session_state.ruolo is None:

    st.header("Seleziona accesso")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👤 Guest"):
            st.session_state.ruolo = "guest"
            st.rerun()

    with col2:
        username = st.text_input("Utente")
        password = st.text_input("Password", type="password")

        if st.button("Login Admin"):
            if username == "admin" and password == "admin2026":
                st.session_state.ruolo = "admin"
                st.rerun()
            else:
                st.error("Credenziali errate")

    st.stop()

is_admin = st.session_state.ruolo == "admin"

# LOGOUT
if st.button("🚪 Logout"):
    st.session_state.ruolo = None
    st.rerun()

# =========================
# INSERIMENTO
# =========================
st.header("➕ Inserisci Movimento")

with st.form("form", clear_on_submit=True):

    col1, col2, col3 = st.columns(3)

    with col1:
        data = st.date_input("Data")
        tipo = st.selectbox("Tipo", TIPI)
        cassa = st.selectbox("Cassa", CASSE)

    with col2:
        descrizione = st.text_input("Descrizione")
        metodo = st.selectbox("Metodo", METODI)
        importo = st.number_input("Importo", min_value=0.0)

    with col3:
        categoria = st.selectbox("Categoria", CATEGORIE)
        note = st.text_input("Note")

    st.subheader("🧾 Scontrino")

    numero_scontrino = st.text_input("Numero")
    esercente = st.text_input("Esercente")
    data_scontrino = st.date_input("Data scontrino")

    uploaded_file = st.file_uploader("📸 Carica scontrino", type=["jpg", "png", "jpeg"])

    st.subheader("👤 Chi inserisce")

    if is_admin:
        inserito_da = "Segretaria"
    else:
        inserito_da = st.text_input("Nome e Cognome")

    submit = st.form_submit_button("✅ Inserisci")

    if submit:

        if not is_admin and inserito_da.strip() == "":
            st.error("Inserisci nome e cognome")
        else:
            try:
                # SALVA SCONTRINO
                nome_file = ""
                if uploaded_file:
                    nome_file = f"{data}_{importo}_{uploaded_file.name}"
                    path = os.path.join(SCONTRINI_DIR, nome_file)
                    with open(path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                # SALVA SU DATABASE
                response = supabase.table("movimenti").insert({
                    "data": str(data),
                    "tipo": tipo,
                    "cassa": cassa,
                    "descrizione": descrizione,
                    "metodo": metodo,
                    "importo": float(importo),
                    "categoria": categoria,
                    "numero_scontrino": numero_scontrino,
                    "esercente": esercente,
                    "data_scontrino": str(data_scontrino),
                    "file_scontrino": nome_file,
                    "inserito_da": inserito_da,
                    "note": note
                }).execute()

                st.success("✅ Inserimento riuscito")
                st.write(response)

                st.rerun()

            except Exception as e:
                st.error(f"❌ Errore inserimento: {e}")

# =========================
# ADMIN
# =========================
if is_admin:

    st.header("📊 Movimenti")

    try:
        response = supabase.table("movimenti").select("*").execute()
        df = pd.DataFrame(response.data)

        if df.empty:
            st.info("Nessun dato")
        else:
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Errore lettura: {e}")

    # SALDI
    st.header("💰 Saldi")

    try:
        response = supabase.table("movimenti").select("*").execute()
        df_all = pd.DataFrame(response.data)

        for cassa in CASSE:
            df_c = df_all[df_all["cassa"] == cassa]

            entrate = df_c[df_c["tipo"] == "Entrata"]["importo"].sum()
            uscite = df_c[df_c["tipo"] == "Uscita"]["importo"].sum()

            saldo = entrate - uscite

            st.write(f"{cassa}: {saldo:.2f} €")

    except Exception as e:
        st.error(e)

else:
    st.info("👤 Guest può solo inserire")
