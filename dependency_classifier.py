
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

IMPORTANTE:
- L'analisi è statica: il progetto analizzato non viene eseguito.
- Un import rilevato non dimostra che il pacchetto sia
  indispensabile in ogni possibile esecuzione.
- I nomi non riconosciuti non vengono considerati
  automaticamente dipendenze certe.
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

# Queste corrispondenze sono note e vengono utilizzate
# per ricavare il nome del pacchetto da installare.
#
# La chiave è il nome principale del modulo importato.
# Il valore è il nome del pacchetto installabile tramite pip.

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
    "PIL": "Pillow",
    "PIL.Image": "Pillow",
    "cryptography": "cryptography",
    "bcrypt": "bcrypt",
    "jwt": "PyJWT",
    "passlib": "passlib",
    "yaml": "PyYAML",
    "lxml": "lxml",
    "bs4": "beautifulsoup4",
    "openpyxl": "openpyxl",
    "xlsxwriter": "XlsxWriter",
    "docx": "python-docx",
    "pptx": "python-pptx",
    "fitz": "PyMuPDF",
    "qrcode": "qrcode",
    "PIL": "Pillow",
    "dotenv": "python-dotenv",
    "keyring": "keyring",
    "psutil": "psutil",
    "schedule": "schedule",
    "yaml": "PyYAML",
    "rich": "rich",
    "typer": "typer",
    "click": "click",
    "pydantic": "pydantic",
    "PIL": "Pillow",
}


# ============================================================
# MODULI STANDARD DA NON INSERIRE IN REQUIREMENTS
# ============================================================

# Alcuni moduli fanno parte di Python ma non sempre sono
# inclusi nell'insieme principale dei moduli standard.
#
# tkinter, per esempio, viene distribuito con molte installazioni
# di Python, ma può richiedere componenti di sistema separati.
# Non è quindi un pacchetto pip da aggiungere automaticamente.

MODULI_NON_PIP = {
    "tkinter",
    "ensurepip",
    "venv",
}


# ============================================================
# NOMI AMBIGUI DA VERIFICARE
# ============================================================

# Il nome principale da solo non permette sempre di determinare
# quale pacchetto installare.
#
# Questi moduli vengono mantenuti tra i candidati da verificare.

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

        # Ignora i file che si trovano in cartelle escluse.
        percorso_relativo = percorso.relative_to(cartella)

        if any(
            parte in CARTELLE_ESCLUSE
            for parte in percorso_relativo.parts
        ):
            continue

        # Converte il percorso relativo in un nome di modulo.
        parti = list(percorso_relativo.with_suffix("").parts)

        # __init__.py rappresenta il pacchetto.
        if parti and parti[-1] == "__init__":
            parti.pop()

        if not parti:
            continue

        nome_modulo = ".".join(parti)

        # Registra il nome completo.
        moduli_locali.add(nome_modulo)

        # Registra anche il nome principale.
        moduli_locali.add(parti[0])

        # Registra i livelli intermedi dei pacchetti.
        # Esempio: progetto.models.utente aggiunge anche
        # progetto.models.
        for indice in range(1, len(parti)):
            moduli_locali.add(".".join(parti[:indice]))

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

    # Le importazioni relative iniziano con un punto.
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

    Mantiene la struttura utilizzata dalle versioni precedenti.
    """

    moduli_locali = trova_moduli_locali(cartella_progetto)

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

        # Un nome vuoto o relativo non è un pacchetto pip.
        if not nome_principale:
            risultati["da_verificare"].add(nome_importazione)
            continue

        # Modulo appartenente alla libreria standard.
        if nome_principale in MODULI_STANDARD:
            risultati["standard"].add(nome_importazione)
            continue

        # Modulo appartenente al progetto.
        if (
            nome_importazione in moduli_locali
            or nome_principale in moduli_locali
        ):
            risultati["locali"].add(nome_importazione)
            continue

        # Modulo esterno con nome potenzialmente ambiguo.
        if nome_principale in MODULI_AMBIGUI:
            risultati["da_verificare"].add(nome_importazione)
            continue

        # Modulo esterno da ricondurre a un pacchetto pip.
        risultati["esterni"].add(nome_importazione)

    return risultati


# ============================================================
# RICAVA IL NOME DEL PACCHETTO INSTALLABILE
# ============================================================

def nome_pacchetto_installabile(nome_importazione):
    """
    Ricava il nome del pacchetto pip quando la corrispondenza
    è presente nella mappatura conosciuta.

    Esempi:
        dotenv -> python-dotenv
        sklearn -> scikit-learn
        PySide6.QtWidgets -> PySide6
        pandas.core.frame -> pandas

    Restituisce None quando il nome non può essere determinato
    con sufficiente sicurezza.
    """

    nome_principale = nome_modulo_principale(
        nome_importazione
    )

    if not nome_principale:
        return None

    # Non propone moduli che non rappresentano pacchetti pip.
    if nome_principale in MODULI_NON_PIP:
        return None

    # Evita di inventare una corrispondenza per nomi ambigui.
    if nome_principale in MODULI_AMBIGUI:
        return None

    # Restituisce esclusivamente le corrispondenze conosciute.
    return MAPPATURA_PACCHETTI.get(nome_principale)


# ============================================================
# DETERMINA IL LIVELLO DI AFFIDABILITÀ DEL PACCHETTO
# ============================================================

def livello_affidabilita_pacchetto(nome_importazione):
    """
    Indica l'affidabilità della corrispondenza tra modulo e
    pacchetto pip.

    Valori possibili:
        "conosciuto"
        "da_verificare"
        "non_determinabile"

    Questo livello riguarda il nome del pacchetto e non dimostra
    che esso sia indispensabile in ogni possibile esecuzione.
    """

    nome_principale = nome_modulo_principale(
        nome_importazione
    )

    if not nome_principale:
        return "non_determinabile"

    if nome_principale in MODULI_NON_PIP:
        return "non_determinabile"

    if nome_principale in MODULI_AMBIGUI:
        return "da_verificare"

    if nome_principale in MAPPATURA_PACCHETTI:
        return "conosciuto"

    # Non conosciamo con certezza il pacchetto corrispondente.
    return "da_verificare"


# ============================================================
# RAGGRUPPA I MODULI ESTERNI PER PACCHETTO CANDIDATO
# ============================================================

def raggruppa_pacchetti_esterni(risultati_classificazione):
    """
    Raggruppa i moduli esterni per pacchetto pip conosciuto.

    Esempio:
        PySide6.QtCore
        PySide6.QtGui
        PySide6.QtWidgets

    Producono un unico gruppo:
        {
            "PySide6": {
                "PySide6.QtCore",
                "PySide6.QtGui",
                "PySide6.QtWidgets"
            }
        }

    I moduli non riconosciuti non vengono trasformati
    automaticamente in nomi di pacchetti installabili.
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

        # Salta i moduli per cui non abbiamo una corrispondenza.
        if nome_pacchetto is None:
            continue

        # Crea il gruppo se non esiste ancora.
        if nome_pacchetto not in pacchetti:
            pacchetti[nome_pacchetto] = set()

        # Registra il modulo che ha generato il candidato.
        pacchetti[nome_pacchetto].add(nome_importazione)

    return pacchetti


# ============================================================
# CREA UN RESOCONTO DETTAGLIATO DEI PACCHETTI CANDIDATI
# ============================================================

def dettagli_pacchetti_esterni(risultati_classificazione):
    """
    Crea un resoconto dettagliato dei pacchetti candidati.

    Per ogni pacchetto restituisce:
    - nome del pacchetto;
    - moduli importati che lo hanno generato;
    - affidabilità della corrispondenza.
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

def analizza_pacchetti_requirements(risultati_classificazione):
    """
    Prepara i pacchetti per la futura generazione del file
    requirements.txt.

    Restituisce:
        {
            "pacchetti_conosciuti": set(),
            "da_verificare": set()
        }

    I pacchetti conosciuti sono deduplicati.
    I nomi incerti restano separati e non vengono inseriti
    automaticamente nel requirements.txt.
    """

    pacchetti_conosciuti = set()
    da_verificare = set()

    # Raggruppa i moduli esterni riconosciuti.
    for nome_pacchetto, moduli in raggruppa_pacchetti_esterni(
        risultati_classificazione
    ).items():

        if all(
            livello_affidabilita_pacchetto(modulo) == "conosciuto"
            for modulo in moduli
        ):
            pacchetti_conosciuti.add(nome_pacchetto)
        else:
            da_verificare.update(moduli)

    # Recupera anche i moduli esterni non associati a un
    # pacchetto conosciuto.
    for modulo in risultati_classificazione.get("esterni", set()):

        if nome_pacchetto_installabile(modulo) is None:
            da_verificare.add(modulo)

    # Aggiunge i moduli già classificati come ambigui.
    da_verificare.update(
        risultati_classificazione.get("da_verificare", set())
    )

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

        moduli = sorted(risultati.get(chiave, set()))

        if not moduli:
            print("Nessun modulo trovato.")
            continue

        for modulo in moduli:
            print(f"- {modulo}")

    # Mostra i pacchetti conosciuti e i candidati da verificare.
    riepilogo = analizza_pacchetti_requirements(risultati)

    print()
    print("=" * 60)
    print("PACCHETTI PRINCIPALI RICONOSCIUTI")
    print("=" * 60)

    if riepilogo["pacchetti_conosciuti"]:
        for nome_pacchetto in sorted(
            riepilogo["pacchetti_conosciuti"]
        ):
            print(f"- {nome_pacchetto}")
    else:
        print("Nessun pacchetto riconosciuto.")

    print()
    print("=" * 60)
    print("MODULI DA VERIFICARE MANUALMENTE")
    print("=" * 60)

    if riepilogo["da_verificare"]:
        for modulo in sorted(riepilogo["da_verificare"]):
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

    cartella_progetto = Path(__file__).resolve().parent

    # Importa l'analizzatore statico.
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
