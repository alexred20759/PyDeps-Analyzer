
"""
PyDeps Analyzer
Modulo: gui.py

Gestisce l'interfaccia grafica dell'applicazione
attraverso la libreria PySide6.

Funzioni:
- Visualizzazione della finestra principale.
- Selezione della cartella del progetto.
- Pulsante per avviare l'analisi.
- Area dedicata alla visualizzazione dei risultati.
"""

from routes.analisi_route import esegui_analisi_route

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Qt


class FinestraPrincipale(QMainWindow):
    """
    Finestra principale di PyDeps Analyzer.
    """

    def __init__(self):
        """Inizializza la finestra e i suoi componenti."""

        super().__init__()

        # Configurazione generale della finestra.
        self.setWindowTitle("PyDeps Analyzer")
        self.resize(950, 700)
        self.setMinimumSize(750, 550)

        # Memorizza la cartella selezionata dall'utente.
        self.cartella_progetto = None

        # Costruisce l'interfaccia grafica.
        self._crea_interfaccia()

        # Centra la finestra sullo schermo.
        self._centra_finestra()

    def _crea_interfaccia(self):
        """Crea e dispone tutti gli elementi grafici."""

        # Widget centrale della finestra.
        widget_centrale = QWidget()
        self.setCentralWidget(widget_centrale)

        # Layout principale verticale.
        layout_principale = QVBoxLayout(widget_centrale)
        layout_principale.setContentsMargins(20, 20, 20, 20)
        layout_principale.setSpacing(15)

        # ----------------------------------------------------
        # INTESTAZIONE
        # ----------------------------------------------------

        titolo = QLabel("PyDeps Analyzer")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titolo.setStyleSheet(
            """
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2563EB;
                padding: 8px;
            }
            """
        )

        sottotitolo = QLabel(
            "Analisi delle dipendenze dei progetti Python"
        )
        sottotitolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sottotitolo.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                color: #64748B;
                padding-bottom: 8px;
            }
            """
        )

        layout_principale.addWidget(titolo)
        layout_principale.addWidget(sottotitolo)

        # ----------------------------------------------------
        # SELEZIONE DELLA CARTELLA
        # ----------------------------------------------------

        gruppo_cartella = QGroupBox("Cartella del progetto")
        layout_cartella = QHBoxLayout(gruppo_cartella)

        # Campo che mostra il percorso selezionato.
        self.campo_cartella = QLineEdit()
        self.campo_cartella.setPlaceholderText(
            "Seleziona la cartella del progetto da analizzare..."
        )
        self.campo_cartella.setReadOnly(True)

        # Pulsante per aprire la finestra di selezione.
        self.pulsante_sfoglia = QPushButton("Sfoglia...")
        self.pulsante_sfoglia.setMinimumWidth(110)
        self.pulsante_sfoglia.clicked.connect(
            self._seleziona_cartella
        )

        layout_cartella.addWidget(self.campo_cartella)
        layout_cartella.addWidget(self.pulsante_sfoglia)

        layout_principale.addWidget(gruppo_cartella)

        # ----------------------------------------------------
        # PULSANTE DI ANALISI
        # ----------------------------------------------------

        self.pulsante_analizza = QPushButton(
            "Analizza progetto"
        )
        self.pulsante_analizza.setMinimumHeight(42)
        self.pulsante_analizza.setEnabled(False)
        self.pulsante_analizza.clicked.connect(
            self._avvia_analisi
        )

        self.pulsante_analizza.setStyleSheet(
            """
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton:disabled {
                background-color: #94A3B8;
            }
            """
        )

        layout_principale.addWidget(self.pulsante_analizza)

        # ----------------------------------------------------
        # AREA DEI RISULTATI
        # ----------------------------------------------------

        gruppo_risultati = QGroupBox("Risultati dell'analisi")
        layout_risultati = QVBoxLayout(gruppo_risultati)

        # Area testuale per i risultati e gli eventuali errori.
        self.area_risultati = QTextEdit()
        self.area_risultati.setReadOnly(True)
        self.area_risultati.setPlaceholderText(
            "I risultati dell'analisi appariranno qui."
        )

        self.area_risultati.setStyleSheet(
            """
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 12px;
                padding: 8px;
            }
            """
        )

        layout_risultati.addWidget(self.area_risultati)
        layout_principale.addWidget(gruppo_risultati, 1)

        # ----------------------------------------------------
        # BARRA DI STATO
        # ----------------------------------------------------

        self.statusBar().showMessage(
            "Pronto. Seleziona una cartella per iniziare."
        )

    def _centra_finestra(self):
        """Centra la finestra rispetto allo schermo disponibile."""

        schermo = self.screen()

        if schermo is not None:
            area_disponibile = schermo.availableGeometry()
            geometria = self.frameGeometry()
            geometria.moveCenter(area_disponibile.center())
            self.move(geometria.topLeft())

    def _seleziona_cartella(self):
        """Permette all'utente di scegliere una cartella."""

        # Apre la finestra di selezione delle cartelle.
        cartella = QFileDialog.getExistingDirectory(
            self,
            "Seleziona la cartella del progetto Python",
            str(Path.home()),
        )

        # Se l'utente annulla, non modifica la selezione.
        if not cartella:
            return

        # Memorizza e visualizza il percorso scelto.
        self.cartella_progetto = Path(cartella)
        self.campo_cartella.setText(cartella)

        # Abilita il pulsante di analisi.
        self.pulsante_analizza.setEnabled(True)

        # Aggiorna il messaggio di stato.
        self.statusBar().showMessage(
            "Cartella selezionata. Puoi avviare l'analisi."
        )

        # Mostra un messaggio iniziale nell'area dei risultati.
        self.area_risultati.setPlainText(
            f"Cartella selezionata:\n{cartella}\n\n"
            "Premi 'Analizza progetto' per iniziare."
        )

    def _avvia_analisi(self):
        """Avvia l'analisi e mostra i risultati nella GUI."""

        # Verifica che sia stata selezionata una cartella.
        if self.cartella_progetto is None:
            QMessageBox.warning(
                self,
                "Cartella non selezionata",
                "Seleziona prima la cartella del progetto.",
            )
            return

        # Aggiorna la barra di stato.
        self.statusBar().showMessage(
            "Analisi del progetto in corso..."
        )

        # Evita doppi clic durante l'elaborazione.
        self.pulsante_analizza.setEnabled(False)

        try:
            # Inoltra la richiesta alla route.
            risultato = esegui_analisi_route(
                self.cartella_progetto
            )

            # Controlla se il controller ha segnalato un errore.
            if not risultato["successo"]:
                messaggio = risultato.get(
                    "errore",
                    "Errore sconosciuto durante l'analisi.",
                )

                self.area_risultati.setPlainText(
                    f"ERRORE DURANTE L'ANALISI\n\n{messaggio}"
                )

                self.statusBar().showMessage(
                    "Analisi non completata."
                )
                return

            # Recupera i risultati dell'analisi e della classificazione.
            analisi = risultato["analisi"]
            classificazione = risultato["classificazione"]

            # Recupera i pacchetti esterni raggruppati dal controller.
            pacchetti_esterni = risultato.get(
                "pacchetti_esterni",
                {},
            )

            # Prepara il riepilogo generale.
            righe = [
                "RISULTATI DELL'ANALISI",
                "=" * 55,
                f"Cartella: {analisi['cartella']}",
                (
                    "File Python analizzati: "
                    f"{len(analisi['file_analizzati'])}"
                ),
                "",
                "MODULI DELLA LIBRERIA STANDARD",
            ]

            # Mostra i moduli standard.
            for modulo in sorted(classificazione["standard"]):
                righe.append(f"  - {modulo}")

            if not classificazione["standard"]:
                righe.append("  Nessun modulo rilevato.")

            # Mostra i moduli locali.
            righe.extend(["", "MODULI LOCALI DEL PROGETTO"])

            for modulo in sorted(classificazione["locali"]):
                righe.append(f"  - {modulo}")

            if not classificazione["locali"]:
                righe.append("  Nessun modulo rilevato.")

            # ------------------------------------------------
            # LIBRERIE ESTERNE RAGGRUPPATE PER PACCHETTO
            # ------------------------------------------------

            righe.extend([
                "",
                "LIBRERIE ESTERNE CANDIDATE",
                "(nomi dei pacchetti pip da verificare)",
            ])

            if pacchetti_esterni:

                # Mostra un solo gruppo per ciascun pacchetto.
                for nome_pacchetto in sorted(pacchetti_esterni):

                    righe.append(f"  - {nome_pacchetto}")

                    # Elenca i moduli che hanno generato il candidato.
                    for modulo in sorted(
                        pacchetti_esterni[nome_pacchetto]
                    ):
                        righe.append(f"      Import: {modulo}")

            elif classificazione["esterni"]:

                # Compatibilità con un controller precedente
                # che non restituisce ancora pacchetti_esterni.
                righe.append(
                    "  Raggruppamento non disponibile; "
                    "mostro i moduli rilevati."
                )

                for modulo in sorted(classificazione["esterni"]):
                    righe.append(f"  - {modulo}")

            else:
                righe.append("  Nessun modulo esterno rilevato.")

            
            # Mostra le importazioni da verificare.
            righe.extend([
                "",
                "IMPORTAZIONI DA VERIFICARE",
            ])

            # Importazioni o moduli non classificati con certezza.
            moduli_da_verificare = set(
                classificazione["da_verificare"]
            )

            # Aggiunge le chiamate dinamiche il cui modulo
            # non è stato identificato staticamente.
            moduli_da_verificare.update(
                analisi["importazioni_dinamiche_da_verificare"]
            )

            for modulo in sorted(moduli_da_verificare):
                righe.append(f"  - {modulo}")

            if not moduli_da_verificare:
                righe.append(
                    "  Nessuna importazione da verificare."
                )


            # Mostra le importazioni dinamiche.
            righe.extend([
                "",
                "IMPORTAZIONI DINAMICHE RILEVATE",
            ])

            for modulo in sorted(
                analisi["importazioni_dinamiche"]
            ):
                righe.append(f"  - {modulo}")

            if not analisi["importazioni_dinamiche"]:
                righe.append(
                    "  Nessuna importazione dinamica rilevata."
                )

            # Mostra gli eventuali errori nei file analizzati.
            righe.extend(["", "ERRORI DI ANALISI"])

            for errore in analisi["errori"]:
                righe.append(f"  File: {errore['file']}")
                righe.append(
                    f"  Problema: {errore['messaggio']}"
                )

            if not analisi["errori"]:
                righe.append("  Nessun errore rilevato.")

            # Visualizza il risultato completo nella GUI.
            self.area_risultati.setPlainText("\n".join(righe))

            self.statusBar().showMessage(
                "Analisi completata."
            )

        except Exception as errore:
            # Mostra gli errori imprevisti senza chiudere la GUI.
            QMessageBox.critical(
                self,
                "Errore",
                f"Si è verificato un errore:\n{errore}",
            )

            self.statusBar().showMessage(
                "Si è verificato un errore durante l'analisi."
            )

        finally:
            # Riabilita il pulsante al termine dell'operazione.
            self.pulsante_analizza.setEnabled(True)


def avvia_gui():
    """Crea l'applicazione e avvia la finestra principale."""

    # Crea l'applicazione Qt.
    applicazione = QApplication(sys.argv)

    # Crea e mostra la finestra.
    finestra = FinestraPrincipale()
    finestra.show()

    # Avvia il ciclo degli eventi grafici.
    sys.exit(applicazione.exec())


# Permette di avviare la GUI anche direttamente con:
# python gui.py
if __name__ == "__main__":
    avvia_gui()
