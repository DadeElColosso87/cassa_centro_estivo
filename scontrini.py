import os
from config import SCONTRINI_DIR

def inizializza_cartella():
    if not os.path.exists(SCONTRINI_DIR):
        os.makedirs(SCONTRINI_DIR)

def salva_scontrino(file, data, importo, categoria):
    if file is None:
        return ""

    estensione = file.name.split(".")[-1]
    nome_file = f"{data}_{importo}_{categoria}.{estensione}"
    percorso = os.path.join(SCONTRINI_DIR, nome_file)

    with open(percorso, "wb") as f:
        f.write(file.getbuffer())

    return nome_file
