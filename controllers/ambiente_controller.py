
"""
PyDeps Analyzer
File: controllers/ambiente_controller.py

Gestisce le operazioni relative all'ambiente virtuale Python
del progetto selezionato.

Funzionalità:
- Creazione dell'ambiente virtuale .venv.
- Apertura di PowerShell con l'ambiente virtuale attivato.
- Installazione delle dipendenze da requirements.txt.

Non gestisce direttamente l'interfaccia grafica.
"""

import shutil
import subprocess
import sys
from pathlib import Path


# ============================================================
# CONTROLLER DELL'AMBIENTE VIRTUALE
# ============================================================

def crea_ambiente_virtuale(cartella_progetto):
    """
    Crea un ambiente virtuale Python nella cartella .venv
    del progetto selezionato.
    """

    try:
        cartella = Path(cartella_progetto).resolve()

        if not cartella.is_dir():
            return {
                "successo": False,
                "errore": f"La cartella del progetto non esiste: {cartella}",
            }

        percorso_venv = cartella / ".venv"

        if percorso_venv.exists():
            return {
                "successo": False,
                "errore": f"La cartella .venv esiste già: {percorso_venv}",
            }

        risultato = subprocess.run(
            [
                sys.executable,
                "-m",
                "venv",
                str(percorso_venv),
            ],
            cwd=str(cartella),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if risultato.returncode != 0:
            return {
                "successo": False,
                "errore": (
                    risultato.stderr.strip()
                    or risultato.stdout.strip()
                    or "Non è stato possibile creare l'ambiente virtuale."
                ),
            }

        if not (percorso_venv / "Scripts" / "python.exe").is_file():
            return {
                "successo": False,
                "errore": (
                    "Il comando è terminato, ma non è stato trovato "
                    "python.exe all'interno di .venv."
                ),
            }

        return {
            "successo": True,
            "messaggio": (
                f"Ambiente virtuale creato correttamente:\n{percorso_venv}"
            ),
            "percorso_venv": str(percorso_venv),
        }

    except Exception as errore:
        return {
            "successo": False,
            "errore": str(errore),
        }


def attiva_ambiente_virtuale(cartella_progetto):
    """
    Apre una nuova finestra PowerShell nella cartella del progetto
    e attiva al suo interno l'ambiente virtuale .venv.

    L'attivazione riguarda la nuova finestra PowerShell,
    non il processo della GUI.
    """

    try:
        cartella = Path(cartella_progetto).resolve()

        if not cartella.is_dir():
            return {
                "successo": False,
                "errore": f"La cartella del progetto non esiste: {cartella}",
            }

        percorso_venv = cartella / ".venv"
        script_attivazione = percorso_venv / "Scripts" / "Activate.ps1"

        if not script_attivazione.is_file():
            return {
                "successo": False,
                "errore": (
                    "Ambiente virtuale non trovato o incompleto. "
                    "Crea prima il virtual environment."
                ),
            }

        powershell = _trova_powershell()

        if powershell is None:
            return {
                "successo": False,
                "errore": "PowerShell non è stato trovato nel sistema.",
            }

        # Prepara i comandi PowerShell.
        percorso_cartella = _proteggi_percorso_powershell(cartella)
        percorso_script = _proteggi_percorso_powershell(
            script_attivazione
        )

        comando = (
            f"Set-Location -LiteralPath '{percorso_cartella}'; "
            f". '{percorso_script}'; "
            "Write-Host ''; "
            "Write-Host 'Ambiente virtuale attivato.' -ForegroundColor Green; "
            "Write-Host ('Python utilizzato: ' + (Get-Command python).Source)"
        )

        # Crea esplicitamente una nuova console Windows.
        subprocess.Popen(
            [
                powershell,
                "-NoLogo",
                "-NoExit",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                comando,
            ],
            cwd=str(cartella),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            shell=False,
        )

        return {
            "successo": True,
            "messaggio": (
                "Il processo PowerShell è stato avviato. "
                "Verifica che la finestra sia visibile."
            ),
        }

    except Exception as errore:
        return {
            "successo": False,
            "errore": str(errore),
        }


def installa_requirements(cartella_progetto, percorso_requirements):
    """
    Installa le dipendenze di requirements.txt utilizzando
    il Python dell'ambiente virtuale .venv.
    """

    try:
        cartella = Path(cartella_progetto).resolve()
        file_requirements = Path(percorso_requirements).resolve()

        if not cartella.is_dir():
            return {
                "successo": False,
                "errore": f"La cartella del progetto non esiste: {cartella}",
            }

        if not file_requirements.is_file():
            return {
                "successo": False,
                "errore": (
                    f"Il file requirements.txt non esiste: "
                    f"{file_requirements}"
                ),
            }

        python_venv = cartella / ".venv" / "Scripts" / "python.exe"

        if not python_venv.is_file():
            return {
                "successo": False,
                "errore": (
                    "Non è stato trovato il Python dell'ambiente virtuale. "
                    "Crea prima .venv."
                ),
            }

        risultato = subprocess.run(
            [
                str(python_venv),
                "-m",
                "pip",
                "install",
                "-r",
                str(file_requirements),
            ],
            cwd=str(cartella),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if risultato.returncode != 0:
            return {
                "successo": False,
                "errore": (
                    risultato.stderr.strip()
                    or risultato.stdout.strip()
                    or "L'installazione delle dipendenze non è riuscita."
                ),
                "output": risultato.stdout.strip(),
            }

        return {
            "successo": True,
            "messaggio": (
                "Dipendenze installate correttamente nell'ambiente .venv."
            ),
            "output": risultato.stdout.strip(),
        }

    except Exception as errore:
        return {
            "successo": False,
            "errore": str(errore),
        }


# ============================================================
# FUNZIONI DI SUPPORTO
# ============================================================

def _trova_powershell():
    """
    Individua PowerShell 7 oppure Windows PowerShell.
    """

    powershell_7 = _trova_eseguibile("pwsh.exe")

    if powershell_7:
        return powershell_7

    powershell_windows = _trova_eseguibile("powershell.exe")

    if powershell_windows:
        return powershell_windows

    # Percorso standard di Windows PowerShell, se non presente nel PATH.
    percorso_standard = (
        Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
    )

    if percorso_standard.is_file():
        return str(percorso_standard)

    return None


def _trova_eseguibile(nome_eseguibile):
    """
    Cerca un eseguibile utilizzando il PATH di Windows.
    """

    return shutil.which(nome_eseguibile)


def _proteggi_percorso_powershell(percorso):
    """
    Protegge gli apostrofi nei percorsi racchiusi tra apici singoli.
    """

    return str(percorso).replace("'", "''")
