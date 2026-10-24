# P# PyDeps Analyzer

**Analisi delle dipendenze Python attraverso l'analisi statica del codice**

## 🖥️ Screenshot dell'applicazione

![PyDeps Analyzer - Interfaccia grafica](assets/pydeps_analyzer_gui.png)

PyDeps Analyzer è un'applicazione desktop sviluppata in Python con PySide6, progettata per analizzare il codice sorgente di un progetto Python e individuare le importazioni utilizzate e le potenziali dipendenze esterne.

L'obiettivo è aiutare gli sviluppatori a comprendere meglio le dipendenze di un progetto e facilitare la preparazione di un file `requirements.txt`.

**Autore:** Gaetano Alabrese  
**Repository:** [alexred20759/PyDeps-Analyzer](https://github.com/alexred20759/PyDeps-Analyzer)

---

## 🇮🇹 Italiano

### Caratteristiche

- **Analisi statica del codice Python:** esamina i file sorgente alla ricerca delle istruzioni di importazione.
- **Rilevamento degli import:** individua le importazioni presenti nel codice analizzato.
- **Classificazione delle dipendenze:** aiuta a distinguere i moduli locali del progetto dalle potenziali dipendenze esterne.
- **Rilevamento degli import dinamici:** riconosce alcuni schemi di importazione dinamica, come `__import__()` e `importlib.import_module()`, quando il nome del modulo è espresso letteralmente.
- **Segnalazione degli import da verificare:** evidenzia i casi che richiedono un controllo manuale, per esempio quando il nome del modulo viene determinato durante l'esecuzione.
- **Interfaccia grafica desktop:** permette di utilizzare l'analizzatore attraverso un'interfaccia basata su PySide6.

### Requisiti

- Python 3.11 o una versione compatibile con il codice del progetto.
- pip, per installare le dipendenze.
- PySide6, per l'interfaccia grafica.

### Installazione

Clona il repository:

```bash
git clone https://github.com/alexred20759/PyDeps-Analyzer.git
```

Entra nella cartella del progetto:

```bash
cd PyDeps-Analyzer
```

Crea un ambiente virtuale:

```bash
python -m venv .venv
```

Attiva l'ambiente virtuale su Windows.

**Prompt dei comandi:**

```bat
.venv\Scripts\activate
```

**PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

Installa PySide6:

```bash
python -m pip install PySide6
```

### Avvio

Dalla cartella principale del progetto, esegui:

```bash
python main.py
```

### Utilizzo

1. Avvia l'applicazione.
2. Seleziona il progetto Python che desideri analizzare, utilizzando le funzionalità disponibili nell'interfaccia.
3. Avvia l'analisi.
4. Esamina le importazioni rilevate e le eventuali segnalazioni che richiedono una verifica.

I risultati devono essere valutati in relazione alla struttura e alle modalità di esecuzione del progetto analizzato.

### Limiti dell'analisi

PyDeps Analyzer utilizza l'analisi statica: esamina il codice senza eseguire l'intero progetto analizzato.

Di conseguenza:

- Un'importazione rilevata non implica necessariamente che il relativo pacchetto sia indispensabile in ogni configurazione del programma.
- Le importazioni dinamiche possono essere individuate solo quando le informazioni disponibili nel codice sono sufficienti.
- Le importazioni costruite a runtime, le dipendenze opzionali, i plugin e i moduli caricati attraverso configurazioni esterne possono richiedere verifiche aggiuntive.
- Il nome di un modulo Python non sempre coincide con il nome del pacchetto da installare tramite pip.
- L'ambiente Python nel quale viene eseguita l'applicazione può influenzare la disponibilità e la risoluzione dei moduli.

Per questi motivi, i risultati dell'analisi non devono essere considerati una garanzia automatica della completezza di un file `requirements.txt`. È consigliabile verificare le dipendenze individuate e testare il progetto in un ambiente virtuale pulito.

### Licenza e diritto d'autore

Copyright © 2026 Gaetano Alabrese. Tutti i diritti riservati.

Il repository è pubblico, ma non è stata aggiunta una licenza open source. La pubblicazione del codice non costituisce un'autorizzazione generale alla sua riproduzione, distribuzione o modifica al di fuori di quanto consentito dalla legge e dai termini applicabili della piattaforma.

---

## 🇬🇧 English

### Overview

PyDeps Analyzer is a desktop application developed in Python with PySide6. It analyzes Python source code to identify import statements and potential external dependencies.

Its purpose is to help developers understand project dependencies and support the preparation of a `requirements.txt` file.

### Features

- **Static Python code analysis:** examines source files for import statements.
- **Import detection:** identifies imports in the analyzed source code.
- **Dependency classification:** helps distinguish local project modules from potential external dependencies.
- **Dynamic import detection:** recognizes certain dynamic import patterns, including `__import__()` and `importlib.import_module()`, when module names are provided as string literals.
- **Unresolved import reporting:** highlights cases that require manual inspection, such as imports whose names are determined at runtime.
- **Desktop graphical interface:** provides a graphical user interface built with PySide6.

### Requirements

- Python 3.11 or a version compatible with the project code.
- pip for installing dependencies.
- PySide6 for the graphical interface.

### Installation

Clone the repository:

```bash
git clone https://github.com/alexred20759/PyDeps-Analyzer.git
```

Navigate to the project directory:

```bash
cd PyDeps-Analyzer
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows.

**Command Prompt:**

```bat
.venv\Scripts\activate
```

**PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

Install PySide6:

```bash
python -m pip install PySide6
```

### Running the application

From the project root directory, run:

```bash
python main.py
```

### Usage

1. Launch the application.
2. Select the Python project to analyze using the available interface.
3. Start the analysis.
4. Review the detected imports and any warnings requiring further investigation.

Results should be interpreted in the context of the analyzed project's structure and execution requirements.

### Analysis limitations

PyDeps Analyzer uses static analysis. It examines source code without executing the entire target project.

Therefore:

- A detected import does not necessarily mean that the corresponding package is required in every configuration of the application.
- Dynamic imports can only be identified when sufficient information is available in the source code.
- Runtime-generated imports, optional dependencies, plugins, and modules loaded through external configuration may require additional investigation.
- A Python module name does not always match the package name used by pip.
- The Python environment used to run the analyzer may affect module availability and resolution.

For these reasons, the analysis results should not be treated as an automatic guarantee that a generated `requirements.txt` would be complete. Detected dependencies should be reviewed and the target project should be tested in a clean virtual environment.

### Copyright and licensing

Copyright © 2026 Gaetano Alabrese. All rights reserved.

The repository is public, but no open-source license has been added. Publishing the code does not constitute a general authorization to reproduce, distribute, or modify it beyond what is permitted by applicable law and the platform's applicable terms.

---

*PyDeps Analyzer — Understanding Python project dependencies, one import at a time.*yDeps-Analyzer
