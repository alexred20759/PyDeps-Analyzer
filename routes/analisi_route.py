
"""
PyDeps Analyzer
File: routes/analisi_route.py

Collega l'interfaccia grafica al controller
che gestisce l'analisi del progetto e prepara
i dati per la generazione di requirements.txt.
"""

from controllers.analisi_controller import esegui_analisi_progetto


# ============================================================
# ROUTE DELL'ANALISI
# ============================================================

def esegui_analisi_route(cartella_progetto):
    """
    Riceve dalla GUI la cartella da analizzare
    e inoltra la richiesta al controller.

    Restituisce i risultati preparati dal controller,
    compresi i pacchetti riconosciuti e quelli da verificare
    per la futura generazione di requirements.txt.
    """

    return esegui_analisi_progetto(cartella_progetto)
