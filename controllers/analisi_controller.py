
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
    analizza_pacchetti_requirements,
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
        - requirements: pacchetti riconosciuti e moduli da verificare
        - requirements_completo: indica se l'analisi è priva di errori

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
        # 2. AGGIUNGE LE IMPORTAZIONI DINAMICHE RICONOSCIUTE
        # ----------------------------------------------------

        # Le importazioni dinamiche con nome letterale, come:
        # importlib.import_module("pandas")
        #
        # devono essere considerate insieme alle importazioni
        # normali. Il set evita automaticamente i duplicati.
        moduli_importati = set(
            risultati_analisi["moduli_importati"]
        )

        moduli_importati.update(
            risultati_analisi.get(
                "importazioni_dinamiche",
                set(),
            )
        )

        # ----------------------------------------------------
        # 3. CLASSIFICAZIONE DEI MODULI
        # ----------------------------------------------------

        risultati_classificazione = classifica_moduli(
            moduli_importati,
            cartella,
        )

        # ----------------------------------------------------
        # 4. RAGGRUPPAMENTO DEI PACCHETTI ESTERNI
        # ----------------------------------------------------

        pacchetti_esterni = raggruppa_pacchetti_esterni(
            risultati_classificazione
        )

        # ----------------------------------------------------
        # 5. PREPARAZIONE DEI PACCHETTI PER REQUIREMENTS
        # ----------------------------------------------------

        requirements = analizza_pacchetti_requirements(
            risultati_classificazione
        )

        # ----------------------------------------------------
        # 6. CONTROLLO DEGLI ERRORI DI ANALISI
        # ----------------------------------------------------

        # Se anche un solo file non è stato letto o analizzato
        # correttamente, non possiamo garantire che tutte le
        # dipendenze siano state individuate.
        errori_analisi = risultati_analisi.get(
            "errori",
            [],
        )

        requirements_completo = not errori_analisi

        # ----------------------------------------------------
        # 7. PREPARAZIONE DEI RISULTATI PER LA GUI
        # ----------------------------------------------------

        return {
            "successo": True,
            "analisi": risultati_analisi,
            "classificazione": risultati_classificazione,
            "pacchetti_esterni": pacchetti_esterni,
            "requirements": requirements,
            "requirements_completo": requirements_completo,
        }

    except Exception as errore:
        # Restituisce l'errore al livello superiore,
        # che potrà mostrarlo nella GUI.
        return {
            "successo": False,
            "errore": str(errore),
        }
