
"""
PyDeps Analyzer
Modulo: gui.py

Gestisce l'interfaccia grafica dell'applicazione
attraverso la libreria PySide6.

Funzioni:
- Visualizzazione della finestra principale.
- Selezione della cartella del progetto.
- Pulsante per avviare l'analisi.
- Pulsante per creare requirements.txt.
- Selezione di un file requirements.txt esistente.
- Creazione dell'ambiente virtuale .venv.
- Apertura di PowerShell con l'ambiente virtuale attivato.
- Installazione delle dipendenze nell'ambiente virtuale.
- Area dedicata alla visualizzazione dei risultati.
"""

from routes.analisi_route import esegui_analisi_route
from routes.ambiente_route import (
    crea_ambiente_route,
    attiva_ambiente_route,
    installa_requirements_route,
)

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
        self.resize(950, 800)
        self.setMinimumSize(750, 650)

        # Memorizza la cartella selezionata dall'utente.
        self.cartella_progetto = None

        # Memorizza i risultati dell'ultima analisi riuscita.
        self.ultimo_risultato_analisi = None

        # Memorizza il percorso del requirements.txt selezionato.
        self.percorso_requirements = None

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
        # PULSANTI OPERATIVI
        # ----------------------------------------------------

        # Stile comune: pulsanti compatti, con colori distintivi.
        stile_pulsante = """
            QPushButton {
                color: white;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 7px 5px;
                min-height: 30px;
            }
            QPushButton:disabled {
                background-color: #94A3B8;
                color: #E2E8F0;
            }
        """

        # Layout verticale con due righe da tre pulsanti.
        layout_pulsanti = QVBoxLayout()
        layout_pulsanti.setSpacing(8)

        riga_pulsanti_1 = QHBoxLayout()
        riga_pulsanti_1.setSpacing(8)

        riga_pulsanti_2 = QHBoxLayout()
        riga_pulsanti_2.setSpacing(8)

        # Pulsante per avviare l'analisi.
        self.pulsante_analizza = QPushButton("Analizza progetto")
        self.pulsante_analizza.setEnabled(False)
        self.pulsante_analizza.clicked.connect(self._avvia_analisi)
        self.pulsante_analizza.setStyleSheet(
            stile_pulsante + """
            QPushButton { background-color: #2563EB; }
            QPushButton:hover { background-color: #1D4ED8; }
            """
        )

        # Pulsante per generare requirements.txt.
        self.pulsante_requirements = QPushButton("Crea requirements.txt")
        self.pulsante_requirements.setEnabled(False)
        self.pulsante_requirements.clicked.connect(
            self._crea_requirements
        )
        self.pulsante_requirements.setStyleSheet(
            stile_pulsante + """
            QPushButton { background-color: #15803D; }
            QPushButton:hover { background-color: #166534; }
            """
        )

        # Pulsante per creare l'ambiente virtuale.
        self.pulsante_crea_venv = QPushButton("Crea ambiente virtuale")
        self.pulsante_crea_venv.setEnabled(False)
        self.pulsante_crea_venv.clicked.connect(
            self._crea_ambiente_virtuale
        )
        self.pulsante_crea_venv.setStyleSheet(
            stile_pulsante + """
            QPushButton { background-color: #475569; }
            QPushButton:hover { background-color: #334155; }
            """
        )

        # Pulsante per installare le dipendenze.
        self.pulsante_installa_requirements = QPushButton(
            "Installa requirements nella .venv"
        )
        self.pulsante_installa_requirements.setEnabled(False)
        self.pulsante_installa_requirements.clicked.connect(
            self._installa_requirements
        )
        self.pulsante_installa_requirements.setStyleSheet(
            stile_pulsante + """
            QPushButton { background-color: #7C3AED; }
            QPushButton:hover { background-color: #6D28D9; }
            """
        )

        # Pulsante per attivare la .venv in PowerShell.
        self.pulsante_attiva_venv = QPushButton(
            "Attiva ambiente virtuale"
        )
        self.pulsante_attiva_venv.setEnabled(False)
        self.pulsante_attiva_venv.clicked.connect(
            self._attiva_ambiente_virtuale
        )
        self.pulsante_attiva_venv.setStyleSheet(
            stile_pulsante + """
            QPushButton { background-color: #475569; }
            QPushButton:hover { background-color: #334155; }
            """
        )

        # Pulsante per chiudere l'applicazione.
        self.pulsante_chiudi = QPushButton("Chiudi")
        self.pulsante_chiudi.clicked.connect(self.close)
        self.pulsante_chiudi.setStyleSheet(
            stile_pulsante + """
            QPushButton { background-color: #DC2626; }
            QPushButton:hover { background-color: #B91C1C; }
            """
        )

        # Prima riga: analisi, requirements e creazione della .venv.
        riga_pulsanti_1.addWidget(self.pulsante_analizza)
        riga_pulsanti_1.addWidget(self.pulsante_requirements)
        riga_pulsanti_1.addWidget(self.pulsante_crea_venv)

        # Seconda riga: installazione, attivazione e chiusura.
        riga_pulsanti_2.addWidget(self.pulsante_installa_requirements)
        riga_pulsanti_2.addWidget(self.pulsante_attiva_venv)
        riga_pulsanti_2.addWidget(self.pulsante_chiudi)

        layout_pulsanti.addLayout(riga_pulsanti_1)
        layout_pulsanti.addLayout(riga_pulsanti_2)

        layout_principale.addLayout(layout_pulsanti)

        # ----------------------------------------------------
        # GESTIONE DELL'AMBIENTE VIRTUALE
        # ----------------------------------------------------

        gruppo_ambiente = QGroupBox(
            "Gestione ambiente virtuale Python"
        )
        layout_ambiente = QVBoxLayout(gruppo_ambiente)

        # Campo per selezionare un requirements.txt esistente.
        etichetta_requirements = QLabel(
            "File requirements.txt da utilizzare:"
        )
        layout_ambiente.addWidget(etichetta_requirements)

        layout_selezione_requirements = QHBoxLayout()

        self.campo_percorso_requirements = QLineEdit()
        self.campo_percorso_requirements.setReadOnly(True)
        self.campo_percorso_requirements.setPlaceholderText(
            "Seleziona il file requirements.txt..."
        )

        self.pulsante_sfoglia_requirements = QPushButton("Sfoglia...")
        self.pulsante_sfoglia_requirements.setMinimumWidth(110)
        self.pulsante_sfoglia_requirements.clicked.connect(
            self._seleziona_requirements
        )

        layout_selezione_requirements.addWidget(
            self.campo_percorso_requirements
        )
        layout_selezione_requirements.addWidget(
            self.pulsante_sfoglia_requirements
        )

        layout_ambiente.addLayout(layout_selezione_requirements)

        # Informazione sul funzionamento della sezione.
        nota_ambiente = QLabel(
            "L'ambiente .venv viene creato nella cartella del progetto. "
            "L'installazione utilizza il Python di quell'ambiente."
        )
        nota_ambiente.setWordWrap(True)
        nota_ambiente.setStyleSheet(
            "color: #64748B; font-size: 11px;"
        )

        layout_ambiente.addWidget(nota_ambiente)
        layout_principale.addWidget(gruppo_ambiente)


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

    # --------------------------------------------------------
    # METODI DI SUPPORTO PER L'AMBIENTE VIRTUALE
    # --------------------------------------------------------

    def _percorso_venv(self):
        """Restituisce il percorso della cartella .venv."""

        if self.cartella_progetto is None:
            return None

        return self.cartella_progetto / ".venv"

    def _python_venv(self):
        """Restituisce il percorso del Python della .venv."""

        percorso_venv = self._percorso_venv()

        if percorso_venv is None:
            return None

        return percorso_venv / "Scripts" / "python.exe"

    def _aggiorna_pulsanti_ambiente(self):
        """Aggiorna lo stato dei pulsanti dell'ambiente virtuale."""

        progetto_selezionato = (
            self.cartella_progetto is not None
            and self.cartella_progetto.is_dir()
        )

        percorso_venv = self._percorso_venv()
        python_venv = self._python_venv()

        # La .venv è considerata disponibile se contiene
        # l'eseguibile Python previsto per Windows.
        venv_disponibile = (
            python_venv is not None
            and python_venv.is_file()
        )

        self.pulsante_crea_venv.setEnabled(
            progetto_selezionato and not venv_disponibile
        )

        self.pulsante_attiva_venv.setEnabled(
            venv_disponibile
        )

        requirements_disponibile = (
            self.percorso_requirements is not None
            and self.percorso_requirements.is_file()
        )

        self.pulsante_installa_requirements.setEnabled(
            venv_disponibile and requirements_disponibile
        )

    def _seleziona_requirements(self):
        """Permette di selezionare un file requirements.txt."""

        # Se possibile, apre la finestra nella cartella del progetto.
        cartella_iniziale = (
            str(self.cartella_progetto)
            if self.cartella_progetto is not None
            else str(Path.home())
        )

        percorso, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona il file requirements.txt",
            cartella_iniziale,
            "File requirements (*.txt);;Tutti i file (*)",
        )

        # Se l'utente annulla, mantiene la selezione precedente.
        if not percorso:
            return

        percorso_selezionato = Path(percorso)

        if not percorso_selezionato.is_file():
            QMessageBox.warning(
                self,
                "File non valido",
                "Il file selezionato non esiste o non è accessibile.",
            )
            return

        self.percorso_requirements = percorso_selezionato
        self.campo_percorso_requirements.setText(percorso)

        self._aggiorna_pulsanti_ambiente()

        self.statusBar().showMessage(
            "File requirements.txt selezionato."
        )

    def _crea_ambiente_virtuale(self):
        """Richiede alla route la creazione della .venv e mostra l'esito."""

        if self.cartella_progetto is None:
            QMessageBox.warning(
                self,
                "Cartella non selezionata",
                "Seleziona prima la cartella del progetto.",
            )
            return

        # Evita di sovrascrivere una cartella .venv già esistente.
        percorso_venv = self._percorso_venv()
        if percorso_venv.exists():
            QMessageBox.warning(
                self,
                "Ambiente virtuale già presente",
                "La cartella .venv esiste già.\n\n"
                "Per sicurezza non verrà sovrascritta. Se l'ambiente è "
                "incompleto, verifica la cartella prima di eliminarla o ricrearla.",
            )
            self._aggiorna_pulsanti_ambiente()
            return

        self.pulsante_crea_venv.setEnabled(False)
        self.statusBar().showMessage(
            "Creazione dell'ambiente virtuale in corso..."
        )

        try:
            # La GUI inoltra la richiesta alla route: il comando operativo
            # viene eseguito dal controller.
            risultato = crea_ambiente_route(self.cartella_progetto)

            if not risultato.get("successo", False):
                messaggio = risultato.get(
                    "errore",
                    "Errore sconosciuto durante la creazione della .venv.",
                )
                QMessageBox.critical(
                    self,
                    "Errore nella creazione della .venv",
                    "Non è stato possibile creare l'ambiente virtuale.\n\n"
                    f"Dettagli:\n{messaggio}",
                )
                self.statusBar().showMessage(
                    "Creazione dell'ambiente virtuale non riuscita."
                )
                return

            QMessageBox.information(
                self,
                "Ambiente virtuale creato",
                risultato.get(
                    "messaggio",
                    "L'ambiente virtuale è stato creato correttamente.",
                ),
            )
            self.statusBar().showMessage(
                "Ambiente virtuale creato correttamente."
            )

        except Exception as errore:
            QMessageBox.critical(
                self,
                "Errore",
                "Si è verificato un problema durante la creazione "
                f"della .venv.\n\nDettagli: {errore}",
            )
            self.statusBar().showMessage(
                "Errore durante la creazione dell'ambiente virtuale."
            )

        finally:
            self._aggiorna_pulsanti_ambiente()

    def _attiva_ambiente_virtuale(self):
        """Richiede alla route di aprire PowerShell con la .venv attivata."""

        if self.cartella_progetto is None:
            QMessageBox.warning(
                self,
                "Cartella non selezionata",
                "Seleziona prima la cartella del progetto.",
            )
            return

        # Controllo rapido dell'interprete prima di chiamare la route.
        python_venv = self._python_venv()
        if python_venv is None or not python_venv.is_file():
            QMessageBox.warning(
                self,
                "Ambiente virtuale non disponibile",
                "Non è stata trovata una .venv valida nella cartella del progetto.\n\n"
                "Crea prima l'ambiente virtuale.",
            )
            self._aggiorna_pulsanti_ambiente()
            return

        try:
            risultato = attiva_ambiente_route(self.cartella_progetto)

            if not risultato.get("successo", False):
                QMessageBox.critical(
                    self,
                    "Errore di avvio PowerShell",
                    risultato.get(
                        "errore",
                        "Non è stato possibile aprire PowerShell.",
                    ),
                )
                self.statusBar().showMessage(
                    "Errore durante l'apertura di PowerShell."
                )
                return

            self.statusBar().showMessage(
                risultato.get(
                    "messaggio",
                    "PowerShell avviata con la .venv.",
                )
            )

        except Exception as errore:
            QMessageBox.critical(
                self,
                "Errore di avvio PowerShell",
                f"Non è stato possibile aprire PowerShell.\n\nDettagli: {errore}",
            )
            self.statusBar().showMessage(
                "Errore durante l'apertura di PowerShell."
            )

    def _installa_requirements(self):
        """Richiede alla route l'installazione delle dipendenze nella .venv."""

        if self.cartella_progetto is None:
            QMessageBox.warning(
                self,
                "Cartella non selezionata",
                "Seleziona prima la cartella del progetto.",
            )
            return

        if self.percorso_requirements is None:
            QMessageBox.warning(
                self,
                "File non selezionato",
                "Seleziona prima un file requirements.txt.",
            )
            return

        percorso_venv = self._percorso_venv()
        python_venv = self._python_venv()
        if python_venv is None or not python_venv.is_file():
            QMessageBox.warning(
                self,
                "Ambiente virtuale non disponibile",
                "Non è stata trovata una .venv valida.\n\n"
                "Crea prima l'ambiente virtuale.",
            )
            self._aggiorna_pulsanti_ambiente()
            return

        if not self.percorso_requirements.is_file():
            QMessageBox.warning(
                self,
                "File non trovato",
                "Il file requirements.txt selezionato non esiste più.\n\n"
                "Seleziona nuovamente il file.",
            )
            self.percorso_requirements = None
            self.campo_percorso_requirements.clear()
            self._aggiorna_pulsanti_ambiente()
            return

        # Chiede conferma prima di installare i pacchetti.
        risposta = QMessageBox.question(
            self,
            "Conferma installazione",
            "Vuoi installare le dipendenze indicate in questo file?\n\n"
            f"File:\n{self.percorso_requirements}\n\n"
            f"Ambiente di destinazione:\n{percorso_venv}\n\n"
            "Verrà utilizzato il Python della .venv selezionata.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if risposta != QMessageBox.StandardButton.Yes:
            self.statusBar().showMessage(
                "Installazione delle dipendenze annullata."
            )
            return

        self.pulsante_installa_requirements.setEnabled(False)
        self.statusBar().showMessage(
            "Installazione delle dipendenze in corso..."
        )
        self.area_risultati.append(
            "\n" + "=" * 55
            + "\nINSTALLAZIONE DELLE DIPENDENZE\n"
            + "=" * 55
            + f"\nFile: {self.percorso_requirements}"
            + f"\nAmbiente: {percorso_venv}\n"
        )

        try:
            # La route inoltra la richiesta al controller, che esegue pip.
            risultato = installa_requirements_route(
                self.cartella_progetto,
                self.percorso_requirements,
            )

            output = risultato.get("output", "")
            if output:
                self.area_risultati.append("\nOUTPUT INSTALLAZIONE:\n" + output)

            if risultato.get("successo", False):
                messaggio = risultato.get(
                    "messaggio",
                    "Le dipendenze sono state installate correttamente nella .venv.",
                )
                self.area_risultati.append(
                    "\n\nINSTALLAZIONE COMPLETATA.\n" + messaggio
                )
                QMessageBox.information(
                    self,
                    "Installazione completata",
                    messaggio + f"\n\nFile utilizzato:\n{self.percorso_requirements}",
                )
                self.statusBar().showMessage(
                    "Installazione delle dipendenze completata."
                )
            else:
                errore = risultato.get(
                    "errore",
                    "L'installazione delle dipendenze non è riuscita.",
                )
                self.area_risultati.append(
                    "\n\nINSTALLAZIONE NON COMPLETATA.\n" + errore
                )
                QMessageBox.critical(
                    self,
                    "Errore di installazione",
                    "L'installazione non è stata completata.\n\n"
                    f"Dettagli:\n{errore}\n\n"
                    "Consulta anche l'area dei risultati.",
                )
                self.statusBar().showMessage(
                    "Errore durante l'installazione delle dipendenze."
                )

        except Exception as errore:
            self.area_risultati.append(
                f"\nERRORE DURANTE L'INSTALLAZIONE:\n{errore}"
            )
            QMessageBox.critical(
                self,
                "Errore",
                "Si è verificato un problema durante l'installazione.\n\n"
                f"Dettagli: {errore}",
            )
            self.statusBar().showMessage(
                "Errore durante l'installazione delle dipendenze."
            )

        finally:
            self._aggiorna_pulsanti_ambiente()

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

        # I risultati precedenti non valgono automaticamente
        # per la nuova cartella selezionata.
        self.ultimo_risultato_analisi = None
        self.pulsante_requirements.setEnabled(False)

        # Abilita il pulsante di analisi.
        self.pulsante_analizza.setEnabled(True)

        # Cerca un requirements.txt nella cartella selezionata.
        # Se esiste, lo propone automaticamente.
        requirements_predefinito = (
            self.cartella_progetto / "requirements.txt"
        )

        if requirements_predefinito.is_file():
            self.percorso_requirements = requirements_predefinito
            self.campo_percorso_requirements.setText(
                str(requirements_predefinito)
            )
        else:
            self.percorso_requirements = None
            self.campo_percorso_requirements.clear()

        # Aggiorna i pulsanti della gestione ambiente.
        self._aggiorna_pulsanti_ambiente()

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

        # I risultati precedenti non devono essere riutilizzati
        # se la nuova analisi fallisce.
        self.ultimo_risultato_analisi = None
        self.pulsante_requirements.setEnabled(False)

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

            # ------------------------------------------------
            # IMPORTAZIONI DA VERIFICARE
            # ------------------------------------------------

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
                analisi.get(
                    "importazioni_dinamiche_da_verificare",
                    set(),
                )
            )

            for modulo in sorted(moduli_da_verificare):
                righe.append(f"  - {modulo}")

            if not moduli_da_verificare:
                righe.append(
                    "  Nessuna importazione da verificare."
                )

            # ------------------------------------------------
            # IMPORTAZIONI DINAMICHE
            # ------------------------------------------------

            righe.extend([
                "",
                "IMPORTAZIONI DINAMICHE RILEVATE",
            ])

            for modulo in sorted(
                analisi.get("importazioni_dinamiche", set())
            ):
                righe.append(f"  - {modulo}")

            if not analisi.get("importazioni_dinamiche"):
                righe.append(
                    "  Nessuna importazione dinamica rilevata."
                )

            # ------------------------------------------------
            # ERRORI DI ANALISI
            # ------------------------------------------------

            righe.extend(["", "ERRORI DI ANALISI"])

            errori_analisi = analisi.get("errori", [])

            for errore in errori_analisi:
                righe.append(f"  File: {errore['file']}")
                righe.append(
                    f"  Problema: {errore['messaggio']}"
                )

            if not errori_analisi:
                righe.append("  Nessun errore rilevato.")

            # Salva il risultato per il pulsante requirements.txt.
            self.ultimo_risultato_analisi = risultato

            # Abilita la generazione solo se l'analisi
            # non ha errori di lettura o di sintassi.
            self.pulsante_requirements.setEnabled(
                not errori_analisi
            )

            if errori_analisi:
                righe.extend([
                    "",
                    "ATTENZIONE",
                    "La generazione di requirements.txt è disabilitata",
                    "perché alcuni file non sono stati analizzati.",
                ])

            # Visualizza il risultato completo nella GUI.
            self.area_risultati.setPlainText("\n".join(righe))

            if errori_analisi:
                self.statusBar().showMessage(
                    "Analisi terminata con errori. "
                    "Risolvi gli errori prima di generare requirements.txt."
                )
            else:
                self.statusBar().showMessage(
                    "Analisi completata."
                )

        except Exception as errore:
            # In caso di errore imprevisto, invalida i risultati.
            self.ultimo_risultato_analisi = None
            self.pulsante_requirements.setEnabled(False)

            # Mostra gli errori senza chiudere la GUI.
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
            self.pulsante_analizza.setEnabled(
                self.cartella_progetto is not None
            )

    def _crea_requirements(self):
        """Crea requirements.txt usando i pacchetti riconosciuti."""

        # Verifica che esista una cartella selezionata.
        if self.cartella_progetto is None:
            QMessageBox.warning(
                self,
                "Cartella non selezionata",
                "Seleziona prima la cartella del progetto.",
            )
            return

        # Verifica che sia stata eseguita un'analisi valida.
        if self.ultimo_risultato_analisi is None:
            QMessageBox.warning(
                self,
                "Analisi necessaria",
                "Prima di creare requirements.txt, "
                "esegui l'analisi del progetto.",
            )
            return

        risultato = self.ultimo_risultato_analisi
        analisi = risultato.get("analisi", {})

        # Non genera il file se alcuni sorgenti non sono stati
        # letti o analizzati correttamente.
        errori_analisi = analisi.get("errori", [])

        if errori_analisi:
            QMessageBox.warning(
                self,
                "Analisi incompleta",
                "Non posso creare requirements.txt perché "
                "uno o più file Python contengono errori "
                "di lettura o di sintassi.\n\n"
                "Correggi gli errori e ripeti l'analisi.",
            )
            return

        # Recupera i pacchetti che il classificatore ha
        # riconosciuto con sufficiente certezza.
        informazioni_requirements = risultato.get(
            "requirements",
            {},
        )

        pacchetti = informazioni_requirements.get(
            "pacchetti_conosciuti",
            set(),
        )

        # Elimina eventuali duplicati e ordina i pacchetti.
        pacchetti = sorted({
            str(pacchetto).strip()
            for pacchetto in pacchetti
            if str(pacchetto).strip()
        })

        if not pacchetti:
            QMessageBox.information(
                self,
                "Nessun pacchetto riconosciuto",
                "L'analisi non ha individuato pacchetti esterni "
                "installabili riconosciuti con certezza.\n\n"
                "Non è stato creato alcun file.",
            )
            return

        # Definisce il percorso del file nella cartella analizzata.
        percorso_requirements = (
            self.cartella_progetto / "requirements.txt"
        )

        # Se il file esiste già, chiede conferma prima
        # di sovrascriverlo.
        if percorso_requirements.exists():
            risposta = QMessageBox.question(
                self,
                "Conferma sovrascrittura",
                "Il file requirements.txt esiste già.\n\n"
                "Vuoi sovrascriverlo con i pacchetti "
                "riconosciuti dall'ultima analisi?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if risposta != QMessageBox.StandardButton.Yes:
                self.statusBar().showMessage(
                    "Generazione annullata: file esistente mantenuto."
                )
                return

        # Prepara il contenuto: un pacchetto per riga.
        contenuto = "\n".join(pacchetti) + "\n"

        try:
            # Scrive il file usando la codifica UTF-8.
            percorso_requirements.write_text(
                contenuto,
                encoding="utf-8",
            )

        except OSError as errore:
            QMessageBox.critical(
                self,
                "Errore di scrittura",
                "Non è stato possibile creare requirements.txt.\n\n"
                f"Dettagli: {errore}",
            )

            self.statusBar().showMessage(
                "Errore durante la creazione di requirements.txt."
            )
            return

        # Aggiorna il percorso selezionato per la nuova sezione.
        self.percorso_requirements = percorso_requirements
        self.campo_percorso_requirements.setText(
            str(percorso_requirements)
        )
        self._aggiorna_pulsanti_ambiente()

        # Raccoglie i moduli che richiedono un controllo manuale.
        moduli_da_verificare = set(
            risultato.get("classificazione", {}).get(
                "da_verificare",
                set(),
            )
        )

        moduli_da_verificare.update(
            analisi.get(
                "importazioni_dinamiche_da_verificare",
                set(),
            )
        )

        informazioni_requirements_da_verificare = (
            informazioni_requirements.get("da_verificare", set())
        )

        moduli_da_verificare.update(
            informazioni_requirements_da_verificare
        )

        # Il file contiene solo i pacchetti riconosciuti.
        # Se ci sono dubbi, lo comunichiamo chiaramente all'utente.
        if moduli_da_verificare:
            messaggio = (
                "requirements.txt è stato creato correttamente.\n\n"
                f"Percorso:\n{percorso_requirements}\n\n"
                "Il file contiene soltanto i pacchetti riconosciuti "
                "con certezza.\n\n"
                "ATTENZIONE: alcune importazioni richiedono "
                "una verifica manuale. Il file potrebbe quindi "
                "non contenere tutte le dipendenze del progetto.\n\n"
                "Controlla la sezione 'IMPORTAZIONI DA VERIFICARE' "
                "nei risultati dell'analisi."
            )

            QMessageBox.warning(
                self,
                "File creato con verifiche necessarie",
                messaggio,
            )
        else:
            QMessageBox.information(
                self,
                "Requirements creato",
                "requirements.txt è stato creato correttamente.\n\n"
                f"Percorso:\n{percorso_requirements}\n\n"
                "Sono stati inseriti soltanto i pacchetti "
                "riconosciuti dall'analisi.",
            )

        self.statusBar().showMessage(
            "requirements.txt creato."
        )


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
