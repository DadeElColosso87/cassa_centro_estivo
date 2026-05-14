import pandas as pd
import os
from config import FILE_NAME, SEPARATORE

def inizializza_file():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=[
            "Data",
            "Tipo",
            "Cassa",
            "Descrizione",
            "Metodo",
            "Importo",
            "Categoria",
            "Numero_Scontrino",
            "Esercente",
            "Data_Scontrino",
            "File_Scontrino",
            "Inserito_da",
            "Note"
        ])
        df.to_csv(FILE_NAME, index=False, sep=SEPARATORE)

def carica_dati():
    return pd.read_csv(FILE_NAME, sep=SEPARATORE)

def salva_spesa(df):
    df.to_csv(FILE_NAME, index=False, sep=SEPARATORE)
