
"""
PyDeps Analyzer
File: controllers/analisi_controller.py

Coordina l'analisi del progetto e la classificazione
delle dipendenze.

Utilizza i moduli:
- analyzer.py
- dependency_classifier.py

Non gestisce direttamente l'interfaccia grafica.
"""

from pathlib import Path

from analyzer import analizza_progetto

from dependency_classifier import (
    classifica_moduli,
    raggruppa_pacchetti_esterni,
)


# ============================================================
# CONTROLLER DELL'ANALISI
# ============================================================

def esegui_analisi_progetto(cartella_progetto):
    """
    Analizza un progetto Python e classifica le importazioni.

    Parametri:
        cartella_progetto: percorso della cartella da analizzare.

    Restituisce:
        Un dizionario contenente:
        - successo: indica se l'analisi è riuscita
        - analisi: risultati dell'analisi statica
        - classificazione: categorie dei moduli importati
        - pacchetti_esterni: raggruppamento dei pacchetti
          esterni candidati all'installazione tramite pip

    In caso di errore generale, restituisce un dizionario
    con il messaggio dell'errore.
    """

    # Converte il percorso in un oggetto Path.
    cartella = Path(cartella_progetto).resolve()

    # Verifica che la cartella esista.
    if not cartella.is_dir():
        return {
            "successo": False,
            "errore": (
                f"La cartella non esiste o non è valida: {cartella}"
            ),
        }

    try:
        # ----------------------------------------------------
        # 1. ANALISI DEI FILE PYTHON
        # ----------------------------------------------------

        risultati_analisi = analizza_progetto(cartella)

        # ----------------------------------------------------
        # 2. CLASSIFICAZIONE DEI MODULI
        # ----------------------------------------------------

        risultati_classificazione = classifica_moduli(
            risultati_analisi["moduli_importati"],
            cartella,
        )

        # ----------------------------------------------------
        # 3. RAGGRUPPAMENTO DEI PACCHETTI ESTERNI
        # ----------------------------------------------------

        pacchetti_esterni = raggruppa_pacchetti_esterni(
            risultati_classificazione
        )

        # ----------------------------------------------------
        # 4. PREPARAZIONE DEI RISULTATI PER LA GUI
        # ----------------------------------------------------

        return {
            "successo": True,
            "analisi": risultati_analisi,
            "classificazione": risultati_classificazione,
            "pacchetti_esterni": pacchetti_esterni,
        }

    except Exception as errore:
        # Restituisce l'errore al livello superiore,
        # che potrà mostrarlo nella GUI.
        return {
            "successo": False,
            "errore": str(errore),
        }
