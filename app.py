# =====================================================
# APP.PY - CASSA CENTRO ESTIVO
# VERSIONE DEFINITIVA
# =====================================================

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
    height: 50px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
}

.stDownloadButton > button {
    height: 50px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TITOLO
# =====================================================
st.title("💰 Cassa Centro Estivo")

# =====================================================
# SUCCESSO
# =====================================================
if st.session_state.get("successo"):

    st.success(
        "✅ Movimento salvato correttamente"
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

        st.subheader("👤 Guest")

        st.write("""
        Accesso rapido per:
        - inserimento spese
        - caricamento scontrini
        - invio acquisti
        """)

        if st.button("👤 Entra come Guest"):

            st.session_state.ruolo = "guest"
            st.rerun()

    # =================================================
    # ADMIN
    # =================================================
    with col2:

        st.subheader("👩 Segretaria")

        username = st.text_input("Utente")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("🔐 Login Admin"):

            if (
                username == "admin"
                and password == "admin2026"
            ):

                st.session_state.ruolo = "admin"
                st.rerun()

            else:

                st.error(
                    "❌ Credenziali errate"
                )

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
# FUNZIONE SALVATAGGIO
# =====================================================
def salva_movimento(
    data,
    tipo,
    cassa,
    descrizione,
    metodo,
    importo,
    categoria,
    numero_scontrino,
    esercente,
    data_scontrino,
    uploaded_file,
    inserito_da,
    note
):

    public_url = ""

    # =================================================
    # UPLOAD FILE
    # =================================================
    if uploaded_file:

        estensione = uploaded_file.name.split(".")[-1]

        nome_file = (
            f"{uuid.uuid4()}.{estensione}"
        )

        supabase.storage \
            .from_("scontrini") \
            .upload(
                nome_file,
                uploaded_file.getvalue(),
                {
                    "content-type":
                    uploaded_file.type
                }
            )

        public_url = supabase.storage \
            .from_("scontrini") \
            .get_public_url(nome_file)

    # =================================================
    # DATABASE
    # =================================================
    supabase.table("movimenti").insert({

        "data": str(data),
        "tipo": tipo,
        "cassa": cassa,
        "descrizione": descrizione,
        "metodo": metodo,
        "importo": float(importo),
        "categoria": categoria,

        "numero_scontrino":
        numero_scontrino,

        "esercente":
        esercente,

        "data_scontrino":
        str(data_scontrino),

        "file_scontrino":
        public_url,

        "inserito_da":
        inserito_da,

        "note":
        note

    }).execute()

# =====================================================
# GUEST
# =====================================================
if not is_admin:

    st.header("➕ Inserisci Spesa")

    with st.form(
        "form_guest",
        clear_on_submit=True
    ):

        col1, col2, col3 = st.columns(3)

        # =============================================
        # COLONNA 1
        # =============================================
        with col1:

            data = date.today()

            st.write(
                f"📅 Data: {data}"
            )

            tipo = st.selectbox(
                "Tipo",
                [""] + TIPI
            )

            cassa = st.selectbox(
                "Cassa",
                [""] + CASSE
            )

        # =============================================
        # COLONNA 2
        # =============================================
        with col2:

            descrizione = st.text_input(
                "Descrizione"
            )

            metodo = st.selectbox(
                "Metodo",
                [""] + METODI
            )

            importo = st.number_input(
                "Importo",
                min_value=0.0,
                step=0.50
            )

        # =============================================
        # COLONNA 3
        # =============================================
        with col3:

            categoria = st.selectbox(
                "Categoria",
                [""] + CATEGORIE
            )

            note = st.text_input(
                "Note"
            )

        # =============================================
        # SCONTRINO
        # =============================================
        st.subheader("🧾 Scontrino")

        numero_scontrino = st.text_input(
            "Numero scontrino"
        )

        esercente = st.text_input(
            "Esercente"
        )

        data_scontrino = st.date_input(
            "Data scontrino"
        )

        # =============================================
        # UPLOAD
        # =============================================
        tab1, tab2 = st.tabs([
            "📸 Fotocamera",
            "📂 Upload file"
        ])

        uploaded_file = None

        # FOTO
        with tab1:

            foto_camera = st.camera_input(
                "📸 Scatta foto",
                key=f"guest_camera_"
                    f"{st.session_state.upload_key}"
            )

            if foto_camera:
                uploaded_file = foto_camera

        # FILE
        with tab2:

            file_upload = st.file_uploader(
                "📂 Seleziona file",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "pdf"
                ],
                key=f"guest_upload_"
                    f"{st.session_state.upload_key}"
            )

            if file_upload:
                uploaded_file = file_upload

        # =============================================
        # ANTEPRIMA
        # =============================================
        if uploaded_file:

            st.subheader("👁 Anteprima")

            if uploaded_file.type.startswith(
                "image"
            ):

                st.image(
                    uploaded_file,
                    width=300
                )

            elif (
                uploaded_file.type
                == "application/pdf"
            ):

                st.success(
                    "📄 PDF caricato"
                )

        # =============================================
        # CHI INSERISCE
        # =============================================
        st.subheader("👤 Chi inserisce")

        inserito_da = st.text_input(
            "Nome e Cognome"
        )

        # =============================================
        # SUBMIT
        # =============================================
        submit = st.form_submit_button(
            "✅ Invia Spesa"
        )

        # =============================================
        # INVIO
        # =============================================
        if submit:

            if (
                tipo == ""
                or cassa == ""
                or metodo == ""
                or categoria == ""
            ):

                st.error(
                    "❌ Compila tutti "
                    "i campi obbligatori"
                )

            elif inserito_da.strip() == "":

                st.error(
                    "❌ Inserisci nome "
                    "e cognome"
                )

            else:

                try:

                    salva_movimento(
                        data,
                        tipo,
                        cassa,
                        descrizione,
                        metodo,
                        importo,
                        categoria,
                        numero_scontrino,
                        esercente,
                        data_scontrino,
                        uploaded_file,
                        inserito_da,
                        note
                    )

                    st.session_state[
                        "successo"
                    ] = True

                    st.session_state[
                        "upload_key"
                    ] += 1

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Errore inserimento: {e}"
                    )

# =====================================================
# ADMIN
# =====================================================
else:

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

            df = pd.DataFrame(
                response.data
            )

            if df.empty:

                st.info(
                    "Nessun movimento"
                )

            else:

                # =====================================
                # ORDINA
                # =====================================
                df = df.sort_values(
                    by="data",
                    ascending=False
                )

                # =====================================
                # SALDI
                # =====================================
                st.header(
                    "💰 Saldi Casse"
                )

                saldi = {}

                for cassa in CASSE:

                    df_cassa = df[
                        df["cassa"] == cassa
                    ]

                    entrate = df_cassa[
                        df_cassa["tipo"]
                        == "Entrata"
                    ]["importo"].sum()

                    uscite = df_cassa[
                        df_cassa["tipo"]
                        == "Uscita"
                    ]["importo"].sum()

                    saldi[cassa] = (
                        entrate - uscite
                    )

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "ELEMENTARI",
                        f"{saldi['Elementari']:.2f} €"
                    )

                with col2:

                    st.metric(
                        "MEDIE",
                        f"{saldi['Medie']:.2f} €"
                    )

                with col3:

                    st.metric(
                        "MATERNA",
                        f"{saldi['Materna']:.2f} €"
                    )

                with col4:

                    st.metric(
                        "CAMPO S+L",
                        f"{saldi['Campo S+L']:.2f} €"
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

                df_filtrato = df.copy()

                if filtro_cassa != "Tutte":

                    df_filtrato = df_filtrato[
                        df_filtrato["cassa"]
                        == filtro_cassa
                    ]

                # =====================================
                # RENAME COLONNE
                # =====================================
                df_tabella = df_filtrato.rename(
                    columns={

                        "data":
                        "Data Movimento",

                        "tipo":
                        "Tipo",

                        "importo":
                        "Importo",

                        "categoria":
                        "Categoria",

                        "descrizione":
                        "Descrizione",

                        "metodo":
                        "Metodo",

                        "inserito_da":
                        "Inserito Da",

                        "esercente":
                        "Esercente",

                        "numero_scontrino":
                        "Numero Scontrino",

                        "data_scontrino":
                        "Data Scontrino"

                    }
                )

                # =====================================
                # CHECKBOX
                # =====================================
                df_tabella.insert(
                    0,
                    "Seleziona",
                    False
                )

                # =====================================
                # TABELLA EDITABILE
                # =====================================
                df_edit = st.data_editor(

                    df_tabella,

                    use_container_width=True,

                    hide_index=True,

                    disabled=[
                        "Data Movimento"
                    ]
                )

                col_btn1, col_btn2 = st.columns(2)

                # =====================================
                # ELIMINA
                # =====================================
                with col_btn1:

                    if st.button(
                        "🗑 Elimina selezionati"
                    ):

                        for i, row in df_edit.iterrows():

                            if row["Seleziona"]:

                                id_movimento = \
                                    df_filtrato.iloc[i]["id"]

                                supabase.table(
                                    "movimenti"
                                ).delete().eq(
                                    "id",
                                    id_movimento
                                ).execute()

                        st.success(
                            "✅ Eliminazione completata"
                        )

                        st.rerun()

                # =====================================
                # SALVA MODIFICHE
                # =====================================
                with col_btn2:

                    if st.button(
                        "💾 Salva modifiche"
                    ):

                        for i, row in df_edit.iterrows():

                            id_movimento = \
                                df_filtrato.iloc[i]["id"]

                            supabase.table(
                                "movimenti"
                            ).update({

                                "tipo":
                                row["Tipo"],

                                "importo":
                                row["Importo"],

                                "categoria":
                                row["Categoria"],

                                "descrizione":
                                row["Descrizione"],

                                "metodo":
                                row["Metodo"],

                                "inserito_da":
                                row["Inserito Da"],

                                "esercente":
                                row["Esercente"],

                                "numero_scontrino":
                                row["Numero Scontrino"],

                                "data_scontrino":
                                row["Data Scontrino"]

                            }).eq(
                                "id",
                                id_movimento
                            ).execute()

                        st.success(
                            "✅ Modifiche salvate"
                        )

                        st.rerun()

                st.divider()

                # =====================================
                # VISUALIZZA ALLEGATO
                # =====================================
                st.header(
                    "👁 Visualizza Allegato"
                )

                opzioni = []

                for i, row in df_filtrato.iterrows():

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

                movimento = \
                    df_filtrato.iloc[indice]

                col1, col2 = st.columns([1, 1])

                # =====================================
                # PREVIEW
                # =====================================
                with col1:

                    st.subheader(
                        "🧾 Anteprima scontrino"
                    )

                    url = movimento[
                        "file_scontrino"
                    ]

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

                        st.info(
                            "Nessun allegato"
                        )

                # =====================================
                # DETTAGLI
                # =====================================
                with col2:

                    st.subheader(
                        "📋 Dettagli movimento"
                    )

                    st.write(
                        f"**Tipo:** "
                        f"{movimento['tipo']}"
                    )

                    st.write(
                        f"**Importo:** "
                        f"{movimento['importo']} €"
                    )

                    st.write(
                        f"**Categoria:** "
                        f"{movimento['categoria']}"
                    )

                    st.write(
                        f"**Descrizione:** "
                        f"{movimento['descrizione']}"
                    )

                    st.write(
                        f"**Metodo:** "
                        f"{movimento['metodo']}"
                    )

                    st.write(
                        f"**Inserito da:** "
                        f"{movimento['inserito_da']}"
                    )

                    st.write(
                        f"**Esercente:** "
                        f"{movimento['esercente']}"
                    )

                    st.write(
                        f"**Numero scontrino:** "
                        f"{movimento['numero_scontrino']}"
                    )

                    st.write(
                        f"**Data scontrino:** "
                        f"{movimento['data_scontrino']}"
                    )

                    st.write(
                        f"**Note:** "
                        f"{movimento['note']}"
                    )

                st.divider()

                # =====================================
                # EXPORT
                # =====================================
                st.header(
                    "📥 Esporta Excel"
                )

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
                f"Errore dashboard: {e}"
            )

    # =================================================
    # TAB INSERIMENTO ADMIN
    # =================================================
    with tab_inserimento:

        st.header(
            "➕ Inserisci Spesa"
        )

        with st.form(
            "form_admin",
            clear_on_submit=True
        ):

            col1, col2, col3 = st.columns(3)

            # =========================================
            # COLONNA 1
            # =========================================
            with col1:

                data = date.today()

                st.write(
                    f"📅 Data: {data}"
                )

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

            # =========================================
            # COLONNA 2
            # =========================================
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

            # =========================================
            # COLONNA 3
            # =========================================
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

            # =========================================
            # SCONTRINO
            # =========================================
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

            # =========================================
            # UPLOAD
            # =========================================
            tab1, tab2 = st.tabs([
                "📸 Fotocamera",
                "📂 Upload file"
            ])

            uploaded_file = None

            # FOTO
            with tab1:

                foto_camera = st.camera_input(
                    "📸 Scatta foto",
                    key=f"admin_camera_"
                        f"{st.session_state.upload_key}"
                )

                if foto_camera:
                    uploaded_file = foto_camera

            # FILE
            with tab2:

                file_upload = st.file_uploader(
                    "📂 Seleziona file",
                    type=[
                        "jpg",
                        "jpeg",
                        "png",
                        "pdf"
                    ],
                    key=f"admin_upload_"
                        f"{st.session_state.upload_key}"
                )

                if file_upload:
                    uploaded_file = file_upload

            # =========================================
            # ANTEPRIMA
            # =========================================
            if uploaded_file:

                st.subheader(
                    "👁 Anteprima"
                )

                if uploaded_file.type.startswith(
                    "image"
                ):

                    st.image(
                        uploaded_file,
                        width=300
                    )

                elif (
                    uploaded_file.type
                    == "application/pdf"
                ):

                    st.success(
                        "📄 PDF caricato"
                    )

            # =========================================
            # SUBMIT
            # =========================================
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
                        "❌ Compila tutti "
                        "i campi obbligatori"
                    )

                else:

                    try:

                        salva_movimento(
                            data,
                            tipo,
                            cassa,
                            descrizione,
                            metodo,
                            importo,
                            categoria,
                            numero_scontrino,
                            esercente,
                            data_scontrino,
                            uploaded_file,
                            "Segretaria",
                            note
                        )

                        st.session_state[
                            "successo"
                        ] = True

                        st.session_state[
                            "upload_key"
                        ] += 1

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Errore inserimento: {e}"
                        )
