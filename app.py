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
    height: 52px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
}

.stDownloadButton > button {
    height: 52px;
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

        Inserimento:
        <ul>
        <li>Spese</li>
        <li>Scontrini</li>
        <li>Acquisti</li>
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
        Dashboard completa gestione cassa
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
# GUEST
# =====================================================
if not is_admin:

    st.header("➕ Inserisci Spesa")

    with st.form("form_guest", clear_on_submit=True):

        col1, col2, col3 = st.columns(3)

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

        with col3:

            categoria = st.selectbox(
                "Categoria",
                [""] + CATEGORIE
            )

            note = st.text_input("Note")

        st.subheader("🧾 Scontrino")

        numero_scontrino = st.text_input("Numero scontrino")

        esercente = st.text_input("Esercente")

        data_scontrino = st.date_input("Data scontrino")

        # =================================================
        # TABS SCONTRINO
        # =================================================
        tab1, tab2 = st.tabs([
            "📸 Fotocamera",
            "📂 Upload file"
        ])

        uploaded_file = None

        with tab1:

            foto_camera = st.camera_input(
                "📸 Scatta foto scontrino",
                key=f"camera_guest_{st.session_state.upload_key}"
            )

            if foto_camera:
                uploaded_file = foto_camera

        with tab2:

            file_upload = st.file_uploader(
                "📂 Seleziona file",
                type=["jpg", "jpeg", "png", "pdf"],
                key=f"upload_guest_{st.session_state.upload_key}"
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
        # NOME
        # =================================================
        st.subheader("👤 Chi inserisce")

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
        # SALVA
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

            elif inserito_da.strip() == "":

                st.error(
                    "❌ Inserisci nome e cognome"
                )

            else:

                try:

                    public_url = ""

                    # =====================================
                    # UPLOAD
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

    st.info("""
    👤 Modalità Guest

    Puoi:
    - inserire spese
    - caricare scontrini
    - inviare acquisti alla segreteria
    """)

# =====================================================
# ADMIN
# =====================================================
else:

    # =================================================
    # TABS ADMIN
    # =================================================
    tab_dashboard, tab_inserimento = st.tabs([
        "📊 Dashboard",
        "➕ Inserisci Spesa"
    ])

    # =================================================
    # DASHBOARD
    # =================================================
    with tab_dashboard:

        try:

            response = supabase.table(
                "movimenti"
            ).select("*").execute()

            df = pd.DataFrame(response.data)

            if df.empty:

                st.info("Nessun movimento registrato")

            else:

                # =====================================
                # ORDINA
                # =====================================
                df = df.sort_values(
                    by="data",
                    ascending=False
                )

                # =====================================
                # TOTALI
                # =====================================
                totale_entrate = df[
                    df["tipo"] == "Entrata"
                ]["importo"].sum()

                totale_uscite = df[
                    df["tipo"] == "Uscita"
                ]["importo"].sum()

                totale_generale = (
                    totale_entrate - totale_uscite
                )

                numero_movimenti = len(df)

                # =====================================
                # CARD
                # =====================================
                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "💰 Totale Generale",
                    f"{totale_generale:.2f} €"
                )

                col2.metric(
                    "📈 Entrate",
                    f"{totale_entrate:.2f} €"
                )

                col3.metric(
                    "📉 Uscite",
                    f"{totale_uscite:.2f} €"
                )

                col4.metric(
                    "📋 Movimenti",
                    numero_movimenti
                )

                st.divider()

                # =====================================
                # SALDI
                # =====================================
                st.header("💰 Saldi Casse")

                col_saldi = st.columns(len(CASSE))

                for i, cassa in enumerate(CASSE):

                    df_cassa = df[
                        df["cassa"] == cassa
                    ]

                    entrate = df_cassa[
                        df_cassa["tipo"] == "Entrata"
                    ]["importo"].sum()

                    uscite = df_cassa[
                        df_cassa["tipo"] == "Uscita"
                    ]["importo"].sum()

                    saldo = entrate - uscite

                    with col_saldi[i]:

                        st.metric(
                            cassa,
                            f"{saldo:.2f} €"
                        )

                st.divider()

                # =====================================
                # MOVIMENTI
                # =====================================
                st.header("📊 Movimenti")

                filtro_cassa = st.selectbox(
                    "Filtra per cassa",
                    ["Tutte"] + CASSE
                )

                if filtro_cassa != "Tutte":

                    df = df[
                        df["cassa"] == filtro_cassa
                    ]

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

                # =====================================
                # VISUALIZZA ALLEGATO
                # =====================================
                st.header("👁 Visualizza Allegato")

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

                indice = opzioni.index(scelta)

                movimento = df.iloc[indice]

                col_preview, col_info = st.columns([1, 1])

                # =====================================
                # PREVIEW
                # =====================================
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

                # =====================================
                # DETTAGLI
                # =====================================
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

                st.divider()

                # =====================================
                # EXPORT
                # =====================================
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
    # TAB INSERIMENTO ADMIN
    # =================================================
    with tab_inserimento:

        st.header("➕ Inserisci Spesa")

        with st.form("form_admin", clear_on_submit=True):

            col1, col2, col3 = st.columns(3)

            with col1:

                data = date.today()

                st.write(f"📅 Data: {data}")

                tipo = st.selectbox(
                    "Tipo",
                    [""] + TIPI,
                    key="admin_tipo"
                )

                cassa = st.selectbox(
                    "Cassa",
                    [""] + CASSE,
                    key="admin_cassa"
                )

            with col2:

                descrizione = st.text_input(
                    "Descrizione",
                    key="admin_descrizione"
                )

                metodo = st.selectbox(
                    "Metodo",
                    [""] + METODI,
                    key="admin_metodo"
                )

                importo = st.number_input(
                    "Importo",
                    min_value=0.0,
                    step=0.50,
                    key="admin_importo"
                )

            with col3:

                categoria = st.selectbox(
                    "Categoria",
                    [""] + CATEGORIE,
                    key="admin_categoria"
                )

                note = st.text_input(
                    "Note",
                    key="admin_note"
                )

            st.subheader("🧾 Scontrino")

            numero_scontrino = st.text_input(
                "Numero scontrino",
                key="admin_numero"
            )

            esercente = st.text_input(
                "Esercente",
                key="admin_esercente"
            )

            data_scontrino = st.date_input(
                "Data scontrino",
                key="admin_data_scontrino"
            )

            tab1, tab2 = st.tabs([
                "📸 Fotocamera",
                "📂 Upload file"
            ])

            uploaded_file = None

            with tab1:

                foto_camera = st.camera_input(
                    "📸 Scatta foto scontrino",
                    key=f"camera_admin_{st.session_state.upload_key}"
                )

                if foto_camera:
                    uploaded_file = foto_camera

            with tab2:

                file_upload = st.file_uploader(
                    "📂 Seleziona file",
                    type=["jpg", "jpeg", "png", "pdf"],
                    key=f"upload_admin_{st.session_state.upload_key}"
                )

                if file_upload:
                    uploaded_file = file_upload

            # =========================================
            # ANTEPRIMA
            # =========================================
            if uploaded_file:

                st.subheader("👁 Anteprima")

                if uploaded_file.type.startswith("image"):

                    st.image(
                        uploaded_file,
                        width=300
                    )

                elif uploaded_file.type == "application/pdf":

                    st.success(
                        "📄 PDF caricato correttamente"
                    )

            submit = st.form_submit_button(
                "✅ Inserisci Movimento"
            )

            # =========================================
            # SALVA
            # =========================================
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

                else:

                    try:

                        public_url = ""

                        # =============================
                        # UPLOAD
                        # =============================
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

                        # =============================
                        # DATABASE
                        # =============================
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

                            "inserito_da": "Segretaria",
                            "note": note

                        }).execute()

                        st.session_state["successo"] = True
                        st.session_state.upload_key += 1

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Errore inserimento: {e}"
                        )
