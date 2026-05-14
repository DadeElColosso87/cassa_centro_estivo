import streamlit as st
import pandas as pd
import io
import uuid

from datetime import date

from supabase_client import supabase
from config import CASSE, TIPI, METODI, CATEGORIE

# =====================================================
# CONFIG PAGINA
# =====================================================
st.set_page_config(
    page_title="Cassa Centro Estivo",
    layout="wide"
)

# =====================================================
# STYLE
# =====================================================
st.markdown("""
<style>

[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    padding-top: 2rem;
}

div.stButton > button {
    height: 55px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
}

.stDownloadButton > button {
    height: 55px;
    font-size: 18px;
    border-radius: 12px;
}

.card {
    border: 1px solid #dfe6ee;
    border-radius: 18px;
    padding: 20px;
    background-color: white;
}

.preview-box {
    border: 1px solid #dfe6ee;
    border-radius: 18px;
    padding: 20px;
    background-color: #fafcff;
}

.small-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TITOLO
# =====================================================
st.title("💰 Cassa Centro Estivo")

# =====================================================
# MESSAGGIO SUCCESSO
# =====================================================
if st.session_state.get("successo"):

    st.success(
        "✅ Spesa inviata correttamente alla segreteria"
    )

    st.session_state["successo"] = False

# =====================================================
# SESSIONE
# =====================================================
if "ruolo" not in st.session_state:
    st.session_state.ruolo = None

if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

# =====================================================
# LOGIN
# =====================================================
if st.session_state.ruolo is None:

    st.header("🔐 Accesso")

    col1, col2 = st.columns(2)

    # =================================================
    # GUEST
    # =================================================
    with col1:

        st.markdown("""
        <div class="card">
        <h3>👤 Guest</h3>

        Inserisci:
        <ul>
        <li>Spese</li>
        <li>Scontrini</li>
        <li>Acquisti effettuati</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        if st.button("👤 Entra come Guest"):
            st.session_state.ruolo = "guest"
            st.rerun()

    # =================================================
    # ADMIN
    # =================================================
    with col2:

        st.markdown("""
        <div class="card">
        <h3>👩 Segretaria</h3>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Utente")
        password = st.text_input("Password", type="password")

        if st.button("🔐 Login Admin"):

            if username == "admin" and password == "admin2026":

                st.session_state.ruolo = "admin"
                st.rerun()

            else:

                st.error("❌ Credenziali errate")

    st.stop()

# =====================================================
# CONTROLLO RUOLO
# =====================================================
is_admin = st.session_state.ruolo == "admin"

# =====================================================
# LOGOUT
# =====================================================
if st.button("🚪 Logout"):

    st.session_state.ruolo = None
    st.rerun()

# =====================================================
# INSERIMENTO
# =====================================================
st.header("➕ Inserisci Spesa")

with st.form("form_movimento", clear_on_submit=True):

    col1, col2, col3 = st.columns(3)

    # =================================================
    # COLONNA 1
    # =================================================
    with col1:

        data = date.today()

        st.write(f"📅 Data: {data}")

        tipo = st.selectbox(
            "Tipo",
            [""] + TIPI
        )

        cassa = st.selectbox(
            "Cassa",
            [""] + CASSE
        )

    # =================================================
    # COLONNA 2
    # =================================================
    with col2:

        descrizione = st.text_input("Descrizione")

        metodo = st.selectbox(
            "Metodo",
            [""] + METODI
        )

        importo = st.number_input(
            "Importo",
            min_value=0.0,
            step=0.50
        )

    # =================================================
    # COLONNA 3
    # =================================================
    with col3:

        categoria = st.selectbox(
            "Categoria",
            [""] + CATEGORIE
        )

        note = st.text_input("Note")

    # =================================================
    # SCONTRINO
    # =================================================
    st.subheader("🧾 Scontrino")

    numero_scontrino = st.text_input("Numero scontrino")

    esercente = st.text_input("Esercente")

    data_scontrino = st.date_input("Data scontrino")

    # =================================================
    # TABS
    # =================================================
    tab1, tab2 = st.tabs([
        "📸 Fotocamera",
        "📂 Upload file"
    ])

    uploaded_file = None

    # =================================================
    # FOTO
    # =================================================
    with tab1:

        foto_camera = st.camera_input(
            "📸 Scatta foto scontrino",
            key=f"camera_{st.session_state.upload_key}"
        )

        if foto_camera:
            uploaded_file = foto_camera

    # =================================================
    # FILE
    # =================================================
    with tab2:

        file_upload = st.file_uploader(
            "📂 Seleziona file",
            type=["jpg", "jpeg", "png", "pdf"],
            key=f"upload_{st.session_state.upload_key}"
        )

        if file_upload:
            uploaded_file = file_upload

    # =================================================
    # ANTEPRIMA
    # =================================================
    if uploaded_file:

        st.subheader("👁 Anteprima")

        if uploaded_file.type.startswith("image"):

            st.image(
                uploaded_file,
                width=300
            )

        elif uploaded_file.type == "application/pdf":

            st.success("📄 PDF caricato correttamente")

    # =================================================
    # CHI INSERISCE
    # =================================================
    st.subheader("👤 Chi inserisce")

    if is_admin:

        inserito_da = "Segretaria"

    else:

        inserito_da = st.text_input(
            "Nome e Cognome"
        )

    # =================================================
    # SUBMIT
    # =================================================
    submit = st.form_submit_button(
        "✅ Invia Spesa"
    )

    # =================================================
    # INVIO
    # =================================================
    if submit:

        if (
            tipo == ""
            or cassa == ""
            or metodo == ""
            or categoria == ""
        ):

            st.error(
                "❌ Compila tutti i campi obbligatori"
            )

        elif (
            not is_admin
            and inserito_da.strip() == ""
        ):

            st.error(
                "❌ Inserisci nome e cognome"
            )

        else:

            try:

                public_url = ""

                # =====================================
                # UPLOAD FILE
                # =====================================
                if uploaded_file:

                    estensione = uploaded_file.name.split(".")[-1]

                    nome_file = f"{uuid.uuid4()}.{estensione}"

                    supabase.storage \
                        .from_("scontrini") \
                        .upload(
                            nome_file,
                            uploaded_file.getvalue(),
                            {
                                "content-type": uploaded_file.type
                            }
                        )

                    public_url = supabase.storage \
                        .from_("scontrini") \
                        .get_public_url(nome_file)

                # =====================================
                # DATABASE
                # =====================================
                supabase.table("movimenti").insert({

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

                    "file_scontrino": public_url,

                    "inserito_da": inserito_da,
                    "note": note

                }).execute()

                st.session_state["successo"] = True
                st.session_state.upload_key += 1

                st.rerun()

            except Exception as e:

                st.error(
                    f"Errore inserimento: {e}"
                )

# =====================================================
# ADMIN
# =====================================================
if is_admin:

    st.divider()

    st.header("📊 Movimenti")

    try:

        response = supabase.table(
            "movimenti"
        ).select("*").execute()

        df = pd.DataFrame(response.data)

        if df.empty:

            st.info("Nessun movimento registrato")

        else:

            # =========================================
            # ORDINA
            # =========================================
            df = df.sort_values(
                by="data",
                ascending=False
            )

            # =========================================
            # FILTRO
            # =========================================
            filtro_cassa = st.selectbox(
                "Filtra per cassa",
                ["Tutte"] + CASSE
            )

            if filtro_cassa != "Tutte":

                df = df[
                    df["cassa"] == filtro_cassa
                ]

            # =========================================
            # TABELLA PULITA
            # =========================================
            colonne_tabella = [
                "data",
                "tipo",
                "importo",
                "categoria",
                "descrizione",
                "metodo",
                "inserito_da",
                "esercente",
                "numero_scontrino",
                "data_scontrino"
            ]

            st.dataframe(
                df[colonne_tabella],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # =========================================
            # VISUALIZZA ALLEGATO
            # =========================================
            st.markdown("""
            <div class="preview-box">
            <div class="small-title">
            👁 Visualizza allegato
            </div>
            """, unsafe_allow_html=True)

            opzioni = []

            for i, row in df.iterrows():

                testo = (
                    f"{row['data']} - "
                    f"{row['importo']} € - "
                    f"{row['descrizione']} "
                    f"({row['inserito_da']})"
                )

                opzioni.append(testo)

            scelta = st.selectbox(
                "Seleziona movimento",
                opzioni
            )

            # =========================================
            # MOVIMENTO SELEZIONATO
            # =========================================
            indice = opzioni.index(scelta)

            movimento = df.iloc[indice]

            col_preview, col_info = st.columns([1, 1])

            # =========================================
            # PREVIEW
            # =========================================
            with col_preview:

                st.subheader("🧾 Anteprima scontrino")

                url = movimento["file_scontrino"]

                if url:

                    if (
                        ".jpg" in url
                        or ".jpeg" in url
                        or ".png" in url
                    ):

                        st.image(
                            url,
                            width=350
                        )

                    elif ".pdf" in url:

                        st.link_button(
                            "📄 Apri PDF",
                            url
                        )

                else:

                    st.info("Nessun allegato")

            # =========================================
            # DETTAGLI
            # =========================================
            with col_info:

                st.subheader("📋 Dettagli movimento")

                st.write(f"**Tipo:** {movimento['tipo']}")
                st.write(f"**Importo:** {movimento['importo']} €")
                st.write(f"**Categoria:** {movimento['categoria']}")
                st.write(f"**Descrizione:** {movimento['descrizione']}")
                st.write(f"**Metodo:** {movimento['metodo']}")
                st.write(f"**Inserito da:** {movimento['inserito_da']}")
                st.write(f"**Esercente:** {movimento['esercente']}")
                st.write(f"**Numero scontrino:** {movimento['numero_scontrino']}")
                st.write(f"**Data scontrino:** {movimento['data_scontrino']}")
                st.write(f"**Note:** {movimento['note']}")

            st.markdown("</div>", unsafe_allow_html=True)

            # =========================================
            # EXPORT
            # =========================================
            st.divider()

            st.header("📥 Esporta Excel")

            output = io.BytesIO()

            df.to_excel(
                output,
                index=False
            )

            st.download_button(
                label="📊 Scarica Excel",
                data=output.getvalue(),
                file_name="cassa.xlsx"
            )

    except Exception as e:

        st.error(
            f"Errore lettura dati: {e}"
        )

    # =================================================
    # SALDI
    # =================================================
    st.divider()

    st.header("💰 Saldi Casse")

    try:

        response = supabase.table(
            "movimenti"
        ).select("*").execute()

        df_all = pd.DataFrame(response.data)

        for cassa in CASSE:

            df_cassa = df_all[
                df_all["cassa"] == cassa
            ]

            entrate = df_cassa[
                df_cassa["tipo"] == "Entrata"
            ]["importo"].sum()

            uscite = df_cassa[
                df_cassa["tipo"] == "Uscita"
            ]["importo"].sum()

            saldo = entrate - uscite

            if saldo >= 0:

                st.success(
                    f"{cassa}: {saldo:.2f} €"
                )

            else:

                st.error(
                    f"{cassa}: {saldo:.2f} €"
                )

    except Exception as e:

        st.error(
            f"Errore saldi: {e}"
        )

# =====================================================
# GUEST
# =====================================================
else:

    st.info("""
    👤 Modalità Guest

    Puoi:
    - inserire spese
    - caricare scontrini
    - inviare acquisti alla segreteria
    """)
