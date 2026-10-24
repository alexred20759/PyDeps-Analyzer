
"""
PyDeps Analyzer
File: analyzer.py

Motore per l'analisi statica delle importazioni Python.

Il codice viene letto e analizzato con ast.
I file del progetto NON vengono eseguiti.

L'analisi rileva:
- importazioni normali;
- importazioni relative;
- alcune importazioni dinamiche;
- chiamate dinamiche non risolvibili staticamente;
- errori di lettura e di sintassi.

NOTA:
L'analisi statica non può individuare con certezza tutte
le dipendenze caricate durante l'esecuzione del programma.
"""

import ast
import sys
from pathlib import Path


# ============================================================
# CONFIGURAZIONE
# ============================================================

# Cartelle che non devono essere analizzate.
CARTELLE_ESCLUSE = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "site-packages",
    "node_modules",
    "build",
    "dist",
}


# ============================================================
# ANALIZZATORE DELLE IMPORTAZIONI
# ============================================================

class AnalizzatoreImportazioni(ast.NodeVisitor):
    """Raccoglie le importazioni presenti in un file Python."""

    def __init__(self):
        self.moduli = set()
        self.importazioni_relative = set()
        self.importazioni_dinamiche = set()
        self.importazioni_dinamiche_da_verificare = set()

    def visit_Import(self, nodo):
        """Gestisce istruzioni come: import pandas."""

        for elemento in nodo.names:
            self.moduli.add(elemento.name)

        self.generic_visit(nodo)

    def visit_ImportFrom(self, nodo):
        """
        Gestisce istruzioni come:
            from pathlib import Path
            from .models import storico
            from ..controllers import analisi
        """

        if nodo.level == 0 and nodo.module:
            # Importazione assoluta.
            self.moduli.add(nodo.module)

        elif nodo.level > 0:
            # Conserva il livello e il modulo relativo.
            if nodo.module:
                nome_relativo = (
                    "." * nodo.level + nodo.module
                )
            else:
                nome_relativo = "." * nodo.level

            self.importazioni_relative.add(nome_relativo)

        self.generic_visit(nodo)

    
    def visit_Call(self, nodo):
        """Rileva le importazioni dinamiche e le verifiche dei moduli."""

        funzione = nodo.func
        nome_funzione = None

        # Esempio: __import__("pandas")
        if (
            isinstance(funzione, ast.Name)
            and funzione.id == "__import__"
        ):
            nome_funzione = "__import__"

        # Esempio: importlib.import_module("pandas")
        elif (
            isinstance(funzione, ast.Attribute)
            and isinstance(funzione.value, ast.Name)
            and funzione.value.id == "importlib"
            and funzione.attr == "import_module"
        ):
            nome_funzione = "importlib.import_module"

        # Esempio: importlib.util.find_spec("pandas")
        elif (
            isinstance(funzione, ast.Attribute)
            and funzione.attr == "find_spec"
            and (
                (
                    isinstance(funzione.value, ast.Name)
                    and funzione.value.id == "importlib"
                )
                or (
                    isinstance(funzione.value, ast.Attribute)
                    and isinstance(funzione.value.value, ast.Name)
                    and funzione.value.value.id == "importlib"
                    and funzione.value.attr == "util"
                )
            )
        ):
            nome_funzione = "find_spec"

        if nome_funzione:

            # Verifica se il nome del modulo è una stringa
            # identificabile direttamente nel codice.
            if (
                nodo.args
                and isinstance(nodo.args[0], ast.Constant)
                and isinstance(nodo.args[0].value, str)
            ):
                nome = nodo.args[0].value.strip()

                if nome:
                    if nome_funzione == "find_spec":
                        # È una verifica di disponibilità,
                        # non necessariamente un'importazione.
                        if not hasattr(self, "moduli_verificati"):
                            self.moduli_verificati = set()

                        self.moduli_verificati.add(nome)

                    else:
                        # Importazione dinamica identificata.
                        self.importazioni_dinamiche.add(nome)

            else:
                # Il nome potrebbe essere costruito a runtime.
                # Segnaliamo la chiamata senza inventare il modulo.
                self.importazioni_dinamiche_da_verificare.add(
                    nome_funzione
                )

        self.generic_visit(nodo)



# ============================================================
# SCANSIONE DEL PROGETTO
# ============================================================

def trova_file_python(cartella):
    """Trova i file Python, ignorando le cartelle escluse."""

    cartella = Path(cartella).resolve()
    file_trovati = []

    if not cartella.is_dir():
        return file_trovati

    for percorso in cartella.rglob("*.py"):

        # Controlla soltanto le parti relative al progetto.
        percorso_relativo = percorso.relative_to(cartella)

        if any(
            parte in CARTELLE_ESCLUSE
            for parte in percorso_relativo.parts
        ):
            continue

        file_trovati.append(percorso)

    return sorted(file_trovati)


# ============================================================
# ANALISI DI UN SINGOLO FILE
# ============================================================

def analizza_file(percorso):
    """Analizza un singolo file Python senza eseguirlo."""

    percorso = Path(percorso)

    risultato = {
        "file": str(percorso),
        "moduli": set(),
        "importazioni_relative": set(),
        "importazioni_dinamiche": set(),
        "importazioni_dinamiche_da_verificare": set(),
        "errore": None,
    }

    try:
        sorgente = percorso.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        albero = ast.parse(
            sorgente,
            filename=str(percorso),
        )

        analizzatore = AnalizzatoreImportazioni()
        analizzatore.visit(albero)

        risultato["moduli"] = analizzatore.moduli

        risultato["importazioni_relative"] = (
            analizzatore.importazioni_relative
        )

        risultato["importazioni_dinamiche"] = (
            analizzatore.importazioni_dinamiche
        )

        risultato["importazioni_dinamiche_da_verificare"] = (
            analizzatore.importazioni_dinamiche_da_verificare
        )

    except SyntaxError as errore:
        risultato["errore"] = (
            f"Errore di sintassi alla riga {errore.lineno}: "
            f"{errore.msg}"
        )

    except (OSError, UnicodeError) as errore:
        risultato["errore"] = (
            f"Impossibile leggere il file: {errore}"
        )

    return risultato


# ============================================================
# ANALISI COMPLETA DEL PROGETTO
# ============================================================

def analizza_progetto(cartella):
    """Analizza tutti i file Python trovati nel progetto."""

    cartella = Path(cartella).resolve()
    file_python = trova_file_python(cartella)

    risultati = {
        "cartella": str(cartella),
        "file_analizzati": [],
        "moduli_importati": set(),
        "importazioni_relative": set(),
        "importazioni_dinamiche": set(),
        "importazioni_dinamiche_da_verificare": set(),
        "errori": [],
    }

    # Segnala una cartella non valida senza interrompere
    # in modo anomalo l'applicazione.
    if not cartella.is_dir():
        risultati["errori"].append({
            "file": str(cartella),
            "messaggio": "La cartella del progetto non esiste.",
        })

        return risultati

    for percorso in file_python:

        risultato = analizza_file(percorso)

        risultati["file_analizzati"].append(risultato)

        risultati["moduli_importati"].update(
            risultato["moduli"]
        )

        risultati["importazioni_relative"].update(
            risultato["importazioni_relative"]
        )

        risultati["importazioni_dinamiche"].update(
            risultato["importazioni_dinamiche"]
        )

        risultati["importazioni_dinamiche_da_verificare"].update(
            risultato["importazioni_dinamiche_da_verificare"]
        )

        if risultato["errore"]:
            risultati["errori"].append({
                "file": str(percorso),
                "messaggio": risultato["errore"],
            })

    return risultati


# ============================================================
# RISULTATI A VIDEO
# ============================================================

def stampa_risultati(risultati):
    """Mostra un riepilogo leggibile dell'analisi."""

    print("\n" + "=" * 55)
    print("              RISULTATO ANALISI")
    print("=" * 55)

    print(f"\nCartella analizzata: {risultati['cartella']}")

    print(
        "\nFile Python trovati e analizzati: "
        f"{len(risultati['file_analizzati'])}"
    )

    print("\nMODULI IMPORTATI")

    if risultati["moduli_importati"]:
        for modulo in sorted(risultati["moduli_importati"]):
            print(f"  - {modulo}")
    else:
        print("  Nessuna importazione rilevata.")

    print("\nIMPORTAZIONI RELATIVE")

    if risultati["importazioni_relative"]:
        for modulo in sorted(
            risultati["importazioni_relative"]
        ):
            print(f"  - {modulo}")
    else:
        print("  Nessuna importazione relativa rilevata.")

    print("\nIMPORTAZIONI DINAMICHE RILEVATE")

    if risultati["importazioni_dinamiche"]:
        for modulo in sorted(
            risultati["importazioni_dinamiche"]
        ):
            print(f"  - {modulo}")
    else:
        print("  Nessuna importazione dinamica rilevata.")

    print("\nIMPORTAZIONI DINAMICHE DA VERIFICARE")

    if risultati["importazioni_dinamiche_da_verificare"]:
        for nome_funzione in sorted(
            risultati["importazioni_dinamiche_da_verificare"]
        ):
            print(f"  - {nome_funzione}")
    else:
        print("  Nessuna chiamata dinamica irrisolta rilevata.")

    print("\nERRORI DI ANALISI")

    if risultati["errori"]:
        for errore in risultati["errori"]:
            print(f"  File: {errore['file']}")
            print(f"  Problema: {errore['messaggio']}")
    else:
        print("  Nessun errore rilevato.")

    print("\n" + "=" * 55)


# ============================================================
# FUNZIONE DI AVVIO DEL MODULO
# ============================================================

def main():
    """Permette di provare l'analizzatore direttamente."""

    if len(sys.argv) > 1:
        cartella = Path(sys.argv[1])
    else:
        cartella = Path.cwd()

    if not cartella.exists() or not cartella.is_dir():
        print(f"[ERRORE] Cartella non valida: {cartella}")
        return

    risultati = analizza_progetto(cartella)
    stampa_risultati(risultati)


if __name__ == "__main__":
    main()
