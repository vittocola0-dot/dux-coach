"""
Data Manager - Coach Fitness Dinamico
======================================
Gestisce tutte le operazioni CRUD sui file locali:
- profilo_utente.json  → profilo antropometrico dell'utente
- registro_giornaliero.csv → log degli allenamenti completati
- storico_peso.csv → storico settimanale del peso

Tutti i file vengono salvati nella directory 'data/' nella root del progetto.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Directory dei dati: data/ nella root del progetto (un livello sopra execution/)
_BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = _BASE_DIR / "data"

# Percorsi dei file
PROFILO_PATH = DATA_DIR / "profilo_utente.json"
REGISTRO_PATH = DATA_DIR / "registro_giornaliero.csv"
STORICO_PESO_PATH = DATA_DIR / "storico_peso.csv"
CORSE_PATH = DATA_DIR / "corse_registrate.json"

# Colonne dei CSV
REGISTRO_COLUMNS = ["data", "opzione", "nome_opzione", "esercizi", "tempo_minuti", "energia"]
STORICO_PESO_COLUMNS = ["data", "peso", "note"]


def _assicura_directory():
    """Crea la directory data/ se non esiste."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# PROFILO UTENTE
# =============================================================================

def salva_profilo(dati: dict) -> None:
    """Salva il profilo utente in profilo_utente.json.

    Args:
        dati: Dizionario con i dati del profilo (peso, altezza, età, ecc.)
    """
    _assicura_directory()
    dati["ultimo_aggiornamento"] = datetime.now().isoformat()
    with open(PROFILO_PATH, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)


def carica_profilo() -> dict | None:
    """Carica il profilo utente da profilo_utente.json.

    Returns:
        Dizionario con i dati del profilo, o None se il file non esiste.
    """
    if not PROFILO_PATH.exists():
        return None
    try:
        with open(PROFILO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


# =============================================================================
# REGISTRO ALLENAMENTI GIORNALIERO
# =============================================================================

def registra_allenamento(data: str, opzione: str, nome_opzione: str,
                          esercizi: str, tempo_minuti: int, energia: str) -> None:
    """Registra un allenamento completato nel registro giornaliero.

    Args:
        data: Data dell'allenamento (formato YYYY-MM-DD).
        opzione: Lettera dell'opzione scelta (A, B, C).
        nome_opzione: Nome descrittivo (es. "Alta Intensità").
        esercizi: Stringa con la lista degli esercizi svolti.
        tempo_minuti: Durata in minuti dell'allenamento.
        energia: Livello di energia selezionato.
    """
    _assicura_directory()
    nuova_riga = pd.DataFrame([{
        "data": data,
        "opzione": opzione,
        "nome_opzione": nome_opzione,
        "esercizi": esercizi,
        "tempo_minuti": tempo_minuti,
        "energia": energia,
    }])

    if REGISTRO_PATH.exists():
        try:
            df = pd.read_csv(REGISTRO_PATH)
            df = pd.concat([df, nuova_riga], ignore_index=True)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            df = nuova_riga
    else:
        df = nuova_riga

    df.to_csv(REGISTRO_PATH, index=False)


def carica_registro() -> pd.DataFrame:
    """Carica l'intero registro degli allenamenti.

    Returns:
        DataFrame con tutti gli allenamenti registrati, o DataFrame vuoto.
    """
    if not REGISTRO_PATH.exists():
        return pd.DataFrame(columns=REGISTRO_COLUMNS)
    try:
        df = pd.read_csv(REGISTRO_PATH)
        df["data"] = pd.to_datetime(df["data"]).dt.strftime("%Y-%m-%d")
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=REGISTRO_COLUMNS)


def allenamenti_ultimi_7_giorni() -> pd.DataFrame:
    """Restituisce gli allenamenti completati negli ultimi 7 giorni.

    Returns:
        DataFrame filtrato sugli ultimi 7 giorni.
    """
    df = carica_registro()
    if df.empty:
        return df

    oggi = datetime.now().date()
    sette_giorni_fa = oggi - timedelta(days=7)

    df["data_dt"] = pd.to_datetime(df["data"]).dt.date
    filtrato = df[df["data_dt"] >= sette_giorni_fa].copy()
    filtrato.drop(columns=["data_dt"], inplace=True)
    return filtrato


def conta_allenamenti_per_tipo(df: pd.DataFrame) -> dict:
    """Conta gli allenamenti per tipo (A, B, C) in un DataFrame.

    Args:
        df: DataFrame del registro (filtrato o completo).

    Returns:
        Dizionario con il conteggio per opzione, es. {"A": 2, "B": 1, "C": 0}.
    """
    conteggio = {"A": 0, "B": 0, "C": 0}
    if df.empty:
        return conteggio

    for opzione in ["A", "B", "C"]:
        conteggio[opzione] = int((df["opzione"] == opzione).sum())

    return conteggio


# =============================================================================
# STORICO PESO SETTIMANALE
# =============================================================================

def salva_peso(peso: float, note: str = "") -> None:
    """Salva una nuova registrazione del peso nello storico.

    Args:
        peso: Peso in kg.
        note: Note opzionali dell'utente.
    """
    _assicura_directory()
    nuova_riga = pd.DataFrame([{
        "data": datetime.now().strftime("%Y-%m-%d"),
        "peso": peso,
        "note": note,
    }])

    if STORICO_PESO_PATH.exists():
        try:
            df = pd.read_csv(STORICO_PESO_PATH)
            df = pd.concat([df, nuova_riga], ignore_index=True)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            df = nuova_riga
    else:
        df = nuova_riga

    df.to_csv(STORICO_PESO_PATH, index=False)


def carica_storico_peso() -> pd.DataFrame:
    """Carica l'intero storico del peso.

    Returns:
        DataFrame con tutte le registrazioni del peso, o DataFrame vuoto.
    """
    if not STORICO_PESO_PATH.exists():
        return pd.DataFrame(columns=STORICO_PESO_COLUMNS)
    try:
        df = pd.read_csv(STORICO_PESO_PATH)
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=STORICO_PESO_COLUMNS)


def variazione_peso() -> tuple:
    """Calcola la variazione di peso rispetto alla registrazione precedente.

    Returns:
        Tupla (peso_attuale, peso_precedente, delta).
        Se non ci sono abbastanza dati, restituisce (None, None, None).
    """
    df = carica_storico_peso()
    if df.empty or len(df) < 1:
        return (None, None, None)

    peso_attuale = float(df.iloc[-1]["peso"])

    if len(df) < 2:
        return (peso_attuale, None, None)

    peso_precedente = float(df.iloc[-2]["peso"])
    delta = round(peso_attuale - peso_precedente, 1)
    return (peso_attuale, peso_precedente, delta)


# =============================================================================
# REGISTRO CORSE (GPS)
# =============================================================================

def registra_corsa(distanza: float, tempo_sec: int, pace: str, passi: int, kcal: int, gps_path: list) -> None:
    """Registra una corsa nel database JSON.
    
    Args:
        distanza: KM percorsi.
        tempo_sec: Durata in secondi.
        pace: Passo in min/km.
        passi: Passi totali stimati.
        kcal: Calorie bruciate.
        gps_path: Lista di coordinate [[lon, lat], [lon, lat], ...].
    """
    _assicura_directory()
    
    nuova_corsa = {
        "data": datetime.now().isoformat(),
        "distanza": distanza,
        "tempo_sec": tempo_sec,
        "pace": pace,
        "passi": passi,
        "kcal": kcal,
        "gps_path": gps_path
    }
    
    corse = []
    if CORSE_PATH.exists():
        try:
            with open(CORSE_PATH, "r", encoding="utf-8") as f:
                corse = json.load(f)
        except (json.JSONDecodeError, IOError):
            corse = []
            
    corse.append(nuova_corsa)
    
    with open(CORSE_PATH, "w", encoding="utf-8") as f:
        json.dump(corse, f, ensure_ascii=False, indent=2)


def carica_corse() -> list:
    """Carica tutte le corse registrate dal database JSON.
    
    Returns:
        Lista di dizionari con i dati delle corse.
    """
    if not CORSE_PATH.exists():
        return []
    try:
        with open(CORSE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
