
"""
PyDeps Analyzer
File: routes/ambiente_route.py

Collega l'interfaccia grafica al controller
che gestisce l'ambiente virtuale Python.
"""

from controllers.ambiente_controller import (
    crea_ambiente_virtuale,
    attiva_ambiente_virtuale,
    installa_requirements,
)


# ============================================================
# ROUTE DELL'AMBIENTE VIRTUALE
# ============================================================

def crea_ambiente_route(cartella_progetto):
    """
    Riceve dalla GUI la cartella del progetto
    e inoltra la richiesta di creazione del .venv.
    """

    return crea_ambiente_virtuale(cartella_progetto)


def attiva_ambiente_route(cartella_progetto):
    """
    Riceve dalla GUI la cartella del progetto
    e richiede l'apertura di PowerShell con .venv attivato.
    """

    return attiva_ambiente_virtuale(cartella_progetto)


def installa_requirements_route(cartella_progetto, percorso_requirements):
    """
    Riceve dalla GUI la cartella del progetto e il percorso
    di requirements.txt, quindi inoltra la richiesta
    di installazione delle dipendenze.
    """

    return installa_requirements(
        cartella_progetto,
        percorso_requirements,
    )
