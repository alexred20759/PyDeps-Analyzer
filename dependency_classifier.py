
"""
PyDeps Analyzer
File: dependency_classifier.py

Classifica i moduli importati da un progetto Python in:
- moduli standard
- moduli locali
- moduli esterni
- moduli da verificare

Inoltre, prova a ricondurre i moduli esterni ai nomi
dei pacchetti installabili tramite pip.

La corrispondenza tra modulo e pacchetto è indicativa:
alcuni moduli possono appartenere a pacchetti diversi.

IMPORTANTE:
- L'analisi è statica: il progetto analizzato non viene eseguito.
- Un import rilevato non dimostra che il pacchetto sia
  indispensabile in ogni possibile esecuzione.
- Un modulo non riconosciuto non viene considerato
  automaticamente una dipendenza certa.
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
# MAPPATURA INDICATIVA: MODULO IMPORTATO -> PACCHETTO PIP
# ============================================================

MAPPATURA_PACCHETTI = {
    "dotenv": "python-dotenv",
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "yaml": "PyYAML",
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
    "gi": "PyGObject",
    "wx": "wxPython",
}


# ============================================================
# MODULI PER CUI IL NOME DEL PACCHETTO È SOLITAMENTE UGUALE
# ============================================================

PACCHETTI_CON_NOME_COINCIDENTE = {
    "numpy",
    "pandas",
    "scipy",
    "matplotlib",
    "PySide6",
    "requests",
    "flask",
    "django",
    "sqlalchemy",
    "pytest",
    "httpx",
    "aiohttp",
}


# ============================================================
# NOMI CHE POSSONO ESSERE AMBIGUI
# ============================================================

# Alcuni nomi di moduli non permettono di individuare con
# sufficiente sicurezza un singolo pacchetto pip.
#
# Questi nomi vengono mantenuti come candidati da verificare.
# La lista può essere ampliata in futuro.

MODULI_AMBIGUI = {
    "google",
    "azure",
    "boto3",
    "botocore",
    "gi",
    " OpenGL",
}


# ============================================================
# TROVA I MODULI PRESENTI NEL PROGETTO
# ============================================================

def trova_moduli_locali(cartella_progetto):
    """
    Cerca i moduli e i pacchetti Python presenti nel progetto.

    Restituisce un insieme di nomi che possono essere
    confrontati con i moduli importati.
    """

    cartella = Path(cartella_progetto).resolve()
    moduli_locali = set()

    for percorso in cartella.rglob("*.py"):

        # Ignora file che si trovano in cartelle escluse.
        if any(
            parte in CARTELLE_ESCLUSE
            for parte in percorso.relative_to(cartella).parts
        ):
            continue

        # Calcola il percorso relativo al progetto.
        percorso_relativo = percorso.relative_to(cartella)

        # Converte il percorso in un nome di modulo.
        parti = list(percorso_relativo.with_suffix("").parts)

        # __init__.py rappresenta il pacchetto, non un modulo separato.
        if parti and parti[-1] == "__init__":
            parti.pop()

        if parti:
            nome_modulo = ".".join(parti)
            moduli_locali.add(nome_modulo)

            # Aggiunge anche il nome principale del modulo.
            moduli_locali.add(parti[0])

    return moduli_locali


# ============================================================
# ESTRAE IL NOME PRINCIPALE DA UN'IMPORTAZIONE
# ============================================================

def nome_modulo_principale(nome_importazione):
    """
    Esempi:
        PySide6.QtWidgets -> PySide6
        pandas.core.frame -> pandas

    Le importazioni relative vengono lasciate senza nome,
    perché vengono gestite separatamente.
    """

    if not nome_importazione:
        return ""

    nome_importazione = nome_importazione.strip()

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

    La struttura del dizionario rimane compatibile
    con le versioni precedenti del programma.
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

        # Ignora le importazioni relative, non classificabili
        # senza conoscere il contesto del file.
        if not nome_principale:
            risultati["da_verificare"].add(nome_importazione)
            continue

        # Modulo appartenente alla libreria standard.
        if nome_principale in MODULI_STANDARD:
            risultati["standard"].add(nome_importazione)

        # Modulo trovato all'interno del progetto.
        elif (
            nome_importazione in moduli_locali
            or nome_principale in moduli_locali
        ):
            risultati["locali"].add(nome_importazione)

        # Modulo esterno al progetto.
        else:
            risultati["esterni"].add(nome_importazione)

    return risultati


# ============================================================
# RICAVA UN POSSIBILE NOME DEL PACCHETTO PIP
# ============================================================

def nome_pacchetto_installabile(nome_importazione):
    """
    Prova a ricavare il nome del pacchetto pip da un modulo.

    Esempi:
        dotenv -> python-dotenv
        sklearn -> scikit-learn
        PySide6.QtWidgets -> PySide6
        pandas.core.frame -> pandas

    Il risultato è una stima e non dimostra che il pacchetto
    sia indispensabile o che sia già installato.
    """

    nome_principale = nome_modulo_principale(
        nome_importazione
    )

    if not nome_principale:
        return None

    # Usa la mappatura per i nomi che differiscono da pip.
    if nome_principale in MAPPATURA_PACCHETTI:
        return MAPPATURA_PACCHETTI[nome_principale]

    # Per i pacchetti conosciuti con nome coincidente,
    # restituisce direttamente il nome principale.
    if nome_principale in PACCHETTI_CON_NOME_COINCIDENTE:
        return nome_principale

    # Per gli altri moduli, restituisce un candidato
    # senza garantire che corrisponda al nome corretto su pip.
    return nome_principale


# ============================================================
# DETERMINA IL LIVELLO DI AFFIDABILITÀ DEL CANDIDATO
# ============================================================

def livello_affidabilita_pacchetto(nome_importazione):
    """
    Indica quanto è affidabile la corrispondenza stimata
    tra un modulo importato e un pacchetto pip.

    Valori possibili:
        "conosciuto": corrispondenza presente nelle mappature
                      o nella lista dei nomi coincidenti.
        "da_verificare": nome ambiguo o corrispondenza stimata.
        "non_determinabile": importazione senza nome valido.

    Il livello riguarda la corrispondenza del nome, non prova
    che il pacchetto sia indispensabile per il progetto.
    """

    nome_principale = nome_modulo_principale(
        nome_importazione
    )

    if not nome_principale:
        return "non_determinabile"

    if nome_principale in MODULI_AMBIGUI:
        return "da_verificare"

    if nome_principale in MAPPATURA_PACCHETTI:
        return "conosciuto"

    if nome_principale in PACCHETTI_CON_NOME_COINCIDENTE:
        return "conosciuto"

    return "da_verificare"


# ============================================================
# RAGGRUPPA I MODULI ESTERNI PER PACCHETTO CANDIDATO
# ============================================================

def raggruppa_pacchetti_esterni(risultati_classificazione):
    """
    Raggruppa le importazioni esterne in base al possibile
    pacchetto pip corrispondente.

    Mantiene la struttura già utilizzata dalla GUI:

        {
            "PySide6": {
                "PySide6.QtCore",
                "PySide6.QtWidgets"
            }
        }

    La GUI esistente può quindi continuare a utilizzare
    questa funzione senza modifiche.
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

        # Crea il gruppo se non esiste ancora.
        if nome_pacchetto not in pacchetti:
            pacchetti[nome_pacchetto] = set()

        # Memorizza i moduli che hanno generato il candidato.
        pacchetti[nome_pacchetto].add(nome_importazione)

    return pacchetti


# ============================================================
# CREA UN RESOCONTO DETTAGLIATO DEI PACCHETTI CANDIDATI
# ============================================================

def dettagli_pacchetti_esterni(risultati_classificazione):
    """
    Crea un resoconto dettagliato dei pacchetti candidati.

    Per ogni candidato restituisce:
    - nome del pacchetto ipotizzato;
    - moduli importati che lo hanno generato;
    - livello di affidabilità della corrispondenza.

    Questa funzione è aggiuntiva: non modifica il formato
    restituito da raggruppa_pacchetti_esterni().
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

        # Se anche un modulo richiede verifica, il gruppo
        # viene segnalato come da verificare.
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
# STAMPA LA CLASSIFICAZIONE NEL TERMINALE
# ============================================================

def stampa_classificazione(risultati):
    """
    Stampa le quattro categorie della classificazione
    e i pacchetti esterni candidati con il relativo livello
    di affidabilità del nome.
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

    # Stampa anche i pacchetti pip candidati.
    dettagli = dettagli_pacchetti_esterni(risultati)

    print()
    print("=" * 60)
    print("PACCHETTI ESTERNI CANDIDATI")
    print("=" * 60)

    if not dettagli:
        print("Nessun pacchetto candidato trovato.")
        return

    for nome_pacchetto in sorted(dettagli):

        informazioni = dettagli[nome_pacchetto]

        print(f"- {nome_pacchetto}")
        print(
            f"    Affidabilità del nome: "
            f"{informazioni['affidabilita']}"
        )

        for modulo in sorted(
            informazioni["moduli_importati"]
        ):
            print(f"    import: {modulo}")


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
