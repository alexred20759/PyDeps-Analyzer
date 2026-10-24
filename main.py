"""
PyDeps_Analyzer/
│
├── .venv/
│
├── controllers/
│   └── analisi_controller.py
│
├── routes/
│   └── analisi_route.py
│
├── views/
│   └── gui.py
│
├── main.py
├── analyzer.py
└── dependency_classifier.py
├── requirements.txt        # Dipendenze esterne
└── README.md               # Documentazione
"""


"""
PyDeps Analyzer
File: main.py

Punto di ingresso del programma.

In questa prima versione:
- verifica la versione di Python;
- individua la cartella del progetto;
- verifica se è attivo un ambiente virtuale;
- mostra un riepilogo iniziale.

Il programma non esegue il codice dei progetti da analizzare.
"""


"""
PyDeps Analyzer
File: main.py

Punto di ingresso dell'applicazione.
Avvia l'interfaccia grafica.
"""

from views.gui import avvia_gui


# ============================================================
# AVVIO DEL PROGRAMMA
# ============================================================

if __name__ == "__main__":
    avvia_gui()
