
"""
PyDeps Analyzer
File: dependency_classifier.py

Classifica i moduli importati da un progetto Python in:
- moduli standard
- moduli locali
- moduli esterni
- moduli da verificare

Ricava, quando possibile, il nome del pacchetto installabile
tramite pip, evitando di elencare separatamente i sottomoduli.

Se il nome del pacchetto non è presente nella mappatura,
conserva il nome del modulo principale trovato nella scansione.

IMPORTANTE:
- L'analisi è statica: il progetto analizzato non viene eseguito.
- Un import rilevato non dimostra che il pacchetto sia
  indispensabile in ogni possibile esecuzione.
- I moduli non riconosciuti vengono conservati come candidati.
- I moduli interni a una libreria non devono diventare
  voci separate nel requirements.txt.
"""

import sys
from pathlib import Path


# ============================================================
# MODULI DELLA LIBRERIA STANDARD
# ============================================================

MODULI_STANDARD = sys.stdlib_module_names


# ============================================================
# CARTELLE DA ESCLUDERE DALLA RICERCA DEI MODULI LOCALI
# ============================================================

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
# MAPPATURA: MODULO PRINCIPALE -> PACCHETTO PIP
# ============================================================

MAPPATURA_PACCHETTI = {
    # Elaborazione dati e calcolo scientifico.
    "numpy": "numpy",
    "pandas": "pandas",
    "scipy": "scipy",
    "matplotlib": "matplotlib",
    "sklearn": "scikit-learn",

    # Interfacce grafiche.
    "PySide6": "PySide6",
    "PyQt6": "PyQt6",
    "PyQt5": "PyQt5",
    "tkinter": None,
    "tkcalendar": "tkcalendar",

    # Web e richieste HTTP.
    "requests": "requests",
    "httpx": "httpx",
    "aiohttp": "aiohttp",
    "flask": "Flask",
    "django": "Django",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",

    # Database e serializzazione.
    "sqlalchemy": "SQLAlchemy",
    "pymongo": "pymongo",
    "redis": "redis",
    "yaml": "PyYAML",
    "orjson": "orjson",

    # Moduli con nomi diversi su pip.
    "dotenv": "python-dotenv",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "bs4": "beautifulsoup4",
    "serial": "pyserial",
    "Crypto": "pycryptodome",
    "fitz": "PyMuPDF",
    "dateutil": "python-dateutil",
    "OpenGL": "PyOpenGL",
    "usb": "pyusb",
    "win32api": "pywin32",
    "win32com": "pywin32",
    "win32con": "pywin32",
    "win32gui": "pywin32",
    "wx": "wxPython",

   

    # Altri pacchetti comuni.
    "pytest": "pytest",
    "cryptography": "cryptography",
    "bcrypt": "bcrypt",
    "jwt": "PyJWT",
    "passlib": "passlib",
    "lxml": "lxml",
    "openpyxl": "openpyxl",
    "xlsxwriter": "XlsxWriter",
    "docx": "python-docx",
    "pptx": "python-pptx",
    "qrcode": "qrcode",
    "keyring": "keyring",
    "psutil": "psutil",
    "schedule": "schedule",
    "rich": "rich",
    "typer": "typer",
    "click": "click",
    "pydantic": "pydantic",
}


# ============================================================
# MODULI STANDARD DA NON INSERIRE IN REQUIREMENTS
# ============================================================

MODULI_NON_PIP = {
    "tkinter",
    "ensurepip",
    "venv",
}


# ============================================================
# NOMI AMBIGUI DA VERIFICARE
# ============================================================

MODULI_AMBIGUI = {
    "google",
    "azure",
    "gi",
}


# ============================================================
# TROVA I MODULI PRESENTI NEL PROGETTO
# ============================================================

def trova_moduli_locali(cartella_progetto):
    """
    Cerca i moduli e i pacchetti Python presenti nel progetto.

    Restituisce un insieme di nomi che possono essere confrontati
    con i moduli importati.
    """

    cartella = Path(cartella_progetto).resolve()
    moduli_locali = set()

    if not cartella.is_dir():
        return moduli_locali

    for percorso in cartella.rglob("*.py"):

        percorso_relativo = percorso.relative_to(cartella)

        if any(
            parte in CARTELLE_ESCLUSE
            for parte in percorso_relativo.parts
        ):
            continue

        parti = list(
            percorso_relativo.with_suffix("").parts
        )

        if parti and parti[-1] == "__init__":
            parti.pop()

        if not parti:
            continue

        nome_modulo = ".".join(parti)

        moduli_locali.add(nome_modulo)
        moduli_locali.add(parti[0])

        for indice in range(1, len(parti)):
            moduli_locali.add(
                ".".join(parti[:indice])
            )

    return moduli_locali


# ============================================================
# ESTRAE IL NOME PRINCIPALE DA UN'IMPORTAZIONE
# ============================================================

def nome_modulo_principale(nome_importazione):
    """
    Estrae il primo elemento del nome di un modulo.

    Esempi:
        PySide6.QtWidgets -> PySide6
        pandas.core.frame -> pandas
        dotenv.main -> dotenv

    Le importazioni relative vengono lasciate senza nome.
    """

    if not nome_importazione:
        return ""

    nome_importazione = nome_importazione.strip()

    if not nome_importazione:
        return ""

    if nome_importazione.startswith("."):
        return ""

    return nome_importazione.split(".", maxsplit=1)[0]


# ============================================================
# CLASSIFICA I MODULI IMPORTATI
# ============================================================

def classifica_moduli(moduli_importati, cartella_progetto):
    """
    Classifica i moduli importati dal progetto.

    Restituisce un dizionario con quattro categorie:
    standard, locali, esterni e da_verificare.
    """

    moduli_locali = trova_moduli_locali(
        cartella_progetto
    )

    risultati = {
        "standard": set(),
        "locali": set(),
        "esterni": set(),
        "da_verificare": set(),
    }

    for nome_importazione in moduli_importati:

        nome_principale = nome_modulo_principale(
            nome_importazione
        )

        if not nome_principale:
            risultati["da_verificare"].add(
                nome_importazione
            )
            continue

        if nome_principale in MODULI_STANDARD:
            risultati["standard"].add(
                nome_importazione
            )
            continue

        if (
            nome_importazione in moduli_locali
            or nome_principale in moduli_locali
        ):
            risultati["locali"].add(
                nome_importazione
            )
            continue

        # I nomi ambigui vengono conservati separatamente.
        # Saranno comunque inclusi come candidati in requirements.
        if nome_principale in MODULI_AMBIGUI:
            risultati["da_verificare"].add(
                nome_importazione
            )
            continue

        risultati["esterni"].add(
            nome_importazione
        )

    return risultati


# ============================================================
# RICAVA IL NOME DEL PACCHETTO INSTALLABILE
# ============================================================

def nome_pacchetto_installabile(nome_importazione):
    """
    Ricava il nome del pacchetto da inserire in requirements.

    Se il modulo è presente nella mappatura, usa il nome
    della distribuzione pip corrispondente.

    Se il modulo non è presente nella mappatura, restituisce
    il nome principale trovato nella scansione.

    Restituisce None per i moduli che non devono essere
    inseriti in requirements.
    """

    nome_principale = nome_modulo_principale(
        nome_importazione
    )

    if not nome_principale:
        return None

    if nome_principale in MODULI_STANDARD:
        return None

    if nome_principale in MODULI_NON_PIP:
        return None

    # Se il modulo è presente nella mappatura,
    # utilizza il nome della distribuzione pip.
    if nome_principale in MAPPATURA_PACCHETTI:

        nome_pacchetto = MAPPATURA_PACCHETTI[
            nome_principale
        ]

        if nome_pacchetto is not None:
            return nome_pacchetto

        return None

    # Se non esiste una corrispondenza, conserva
    # il nome principale rilevato durante la scansione.
    return nome_principale


# ============================================================
# DETERMINA IL LIVELLO DI AFFIDABILITÀ DEL PACCHETTO
# ============================================================

def livello_affidabilita_pacchetto(nome_importazione):
    """
    Indica l'affidabilità della corrispondenza tra modulo
    e pacchetto pip.

    Valori possibili:
        "conosciuto"
        "da_verificare"
        "non_determinabile"
    """

    nome_principale = nome_modulo_principale(
        nome_importazione
    )

    if not nome_principale:
        return "non_determinabile"

    if (
        nome_principale in MODULI_STANDARD
        or nome_principale in MODULI_NON_PIP
    ):
        return "non_determinabile"

    if nome_principale in MODULI_AMBIGUI:
        return "da_verificare"

    if nome_principale in MAPPATURA_PACCHETTI:

        if (
            MAPPATURA_PACCHETTI[nome_principale]
            is not None
        ):
            return "conosciuto"

    # Il modulo viene conservato anche se la mappatura
    # non permette di confermare il nome della distribuzione.
    return "da_verificare"


# ============================================================
# RAGGRUPPA I MODULI ESTERNI PER PACCHETTO CANDIDATO
# ============================================================

def raggruppa_pacchetti_esterni(
    risultati_classificazione,
):
    """
    Raggruppa i moduli esterni per nome del pacchetto candidato.

    Se il nome pip è conosciuto, usa quello.
    Altrimenti conserva il nome principale del modulo.
    """

    pacchetti = {}

    moduli_esterni = risultati_classificazione.get(
        "esterni",
        set(),
    )

    for nome_importazione in moduli_esterni:

        nome_pacchetto = nome_pacchetto_installabile(
            nome_importazione
        )

        if nome_pacchetto is None:
            continue

        if nome_pacchetto not in pacchetti:
            pacchetti[nome_pacchetto] = set()

        pacchetti[nome_pacchetto].add(
            nome_importazione
        )

    return pacchetti


# ============================================================
# CREA UN RESOCONTO DETTAGLIATO DEI PACCHETTI CANDIDATI
# ============================================================

def dettagli_pacchetti_esterni(
    risultati_classificazione,
):
    """
    Crea un resoconto dettagliato dei pacchetti candidati.
    """

    pacchetti = raggruppa_pacchetti_esterni(
        risultati_classificazione
    )

    dettagli = {}

    for nome_pacchetto, moduli in pacchetti.items():

        livelli = {
            livello_affidabilita_pacchetto(modulo)
            for modulo in moduli
        }

        if "da_verificare" in livelli:
            affidabilita = "da_verificare"

        elif "non_determinabile" in livelli:
            affidabilita = "non_determinabile"

        else:
            affidabilita = "conosciuto"

        dettagli[nome_pacchetto] = {
            "pacchetto": nome_pacchetto,
            "moduli_importati": set(moduli),
            "affidabilita": affidabilita,
        }

    return dettagli


# ============================================================
# RICAVA I PACCHETTI CONOSCIUTI E QUELLI DA VERIFICARE
# ============================================================

def analizza_pacchetti_requirements(
    risultati_classificazione,
):
    """
    Prepara i pacchetti per la generazione di requirements.txt.

    Restituisce:
        {
            "pacchetti_conosciuti": set(),
            "da_verificare": set()
        }

    La chiave "pacchetti_conosciuti" contiene tutti i nomi
    candidati da scrivere in requirements.txt:
    - nome pip dalla mappatura, se disponibile;
    - nome principale trovato nella scansione, altrimenti.

    La chiave "da_verificare" conserva i moduli incerti
    per eventuali avvisi all'utente.
    """

    pacchetti_conosciuti = set()
    da_verificare = set()

    # I moduli esterni vengono elaborati normalmente.
    moduli_esterni = risultati_classificazione.get(
        "esterni",
        set(),
    )

    # Anche i moduli ambigui vengono conservati come candidati.
    moduli_da_verificare = risultati_classificazione.get(
        "da_verificare",
        set(),
    )

    tutti_i_candidati = (
        set(moduli_esterni)
        | set(moduli_da_verificare)
    )

    for modulo in tutti_i_candidati:

        nome_principale = nome_modulo_principale(
            modulo
        )

        if not nome_principale:
            # Non inserisce importazioni relative
            # di cui non è possibile ricavare il nome.
            da_verificare.add(modulo)
            continue

        if (
            nome_principale in MODULI_STANDARD
            or nome_principale in MODULI_NON_PIP
        ):
            continue

        nome_pacchetto = nome_pacchetto_installabile(
            modulo
        )

        if nome_pacchetto is None:
            # Un modulo escluso dalla generazione non
            # viene inserito in requirements.txt.
            continue

        # Inserisce il nome pip mappato oppure il nome
        # principale rilevato durante la scansione.
        #
        # Il set elimina automaticamente i duplicati.
        pacchetti_conosciuti.add(
            nome_pacchetto
        )

        # Se non esiste una corrispondenza affidabile,
        # conserva il modulo per l'avviso di verifica.
        if (
            livello_affidabilita_pacchetto(modulo)
            != "conosciuto"
        ):
            da_verificare.add(modulo)

    return {
        "pacchetti_conosciuti": pacchetti_conosciuti,
        "da_verificare": da_verificare,
    }


# ============================================================
# STAMPA LA CLASSIFICAZIONE NEL TERMINALE
# ============================================================

def stampa_classificazione(risultati):
    """
    Stampa le categorie della classificazione e i pacchetti
    candidati, indicando quali nomi richiedono una verifica.
    """

    categorie = [
        ("MODULI STANDARD", "standard"),
        ("MODULI LOCALI", "locali"),
        ("MODULI ESTERNI", "esterni"),
        ("MODULI DA VERIFICARE", "da_verificare"),
    ]

    for titolo, chiave in categorie:

        print()
        print("=" * 60)
        print(titolo)
        print("=" * 60)

        moduli = sorted(
            risultati.get(chiave, set())
        )

        if not moduli:
            print("Nessun modulo trovato.")
            continue

        for modulo in moduli:
            print(f"- {modulo}")

    riepilogo = analizza_pacchetti_requirements(
        risultati
    )

    print()
    print("=" * 60)
    print("PACCHETTI CANDIDATI PER REQUIREMENTS")
    print("=" * 60)

    if riepilogo["pacchetti_conosciuti"]:

        for nome_pacchetto in sorted(
            riepilogo["pacchetti_conosciuti"]
        ):
            print(f"- {nome_pacchetto}")

    else:
        print("Nessun pacchetto candidato trovato.")

    print()
    print("=" * 60)
    print("MODULI DA VERIFICARE MANUALMENTE")
    print("=" * 60)

    if riepilogo["da_verificare"]:

        for modulo in sorted(
            riepilogo["da_verificare"]
        ):
            print(f"- {modulo}")

    else:
        print("Nessun modulo da verificare.")


# ============================================================
# TEST DA TERMINALE
# ============================================================

def main():
    """
    Esegue una classificazione di prova sul progetto
    che contiene questo file.
    """

    cartella_progetto = Path(
        __file__
    ).resolve().parent

    from analyzer import analizza_progetto

    risultati_analisi = analizza_progetto(
        cartella_progetto
    )

    risultati_classificazione = classifica_moduli(
        risultati_analisi["moduli_importati"],
        cartella_progetto,
    )

    stampa_classificazione(
        risultati_classificazione
    )


if __name__ == "__main__":
    main()
