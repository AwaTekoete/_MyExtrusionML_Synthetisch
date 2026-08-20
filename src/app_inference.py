# =============================================================================
# app_inference.py – Lade- und Vorhersage-Logik fuer die Streamlit-App
# =============================================================================
# Trennung von Logik (hier) und Darstellung (app/main.py) - analog zur
# Referenzstruktur. Laedt die in Notebook 13 persistierten finalen Modelle
# und stellt Vorhersagefunktionen fuer Modell A und Modell B bereit.
# =============================================================================

import joblib
import pandas as pd
import numpy as np

# --- Konfidenz-Einordnung je Y_B-Groesse, aus Notebook 12 (Ridge, getunt) ---
# Drei Stufen: hoch (R2>=0.6), mittel (0.4<=R2<0.6), niedrig (R2<0.4) -
# spiegelt die in Notebook 12 gemessene Bandbreite (0.266 bis 0.950) differenzierter wider.
KONFIDENZ_R2_JE_Y_B = {
    "duesenspalt": 0.950,
    "schneckendrehzahl": 0.831,
    "innenluftdruck": 0.517,
    "massetemperatur": 0.475,
    "vakuumniveau": 0.367,
    "kuehlwassertemperatur": 0.266,
}
KONFIDENZ_SCHWELLE_HOCH = 0.6
KONFIDENZ_SCHWELLE_MITTEL = 0.4


def konfidenz_stufe_bestimmen(r2_wert):
    if pd.isna(r2_wert):
        return "unbekannt"
    if r2_wert >= KONFIDENZ_SCHWELLE_HOCH:
        return "hoch"
    elif r2_wert >= KONFIDENZ_SCHWELLE_MITTEL:
        return "mittel"
    return "niedrig"

# --- NEU: Einheiten je Y_B-Groesse (aus Datenwoerterbuch, Notebook 09) ---
EINHEITEN_JE_Y_B = {
    "schneckendrehzahl": "U/min",
    "massetemperatur": "°C",
    "duesenspalt": "mm",
    "vakuumniveau": "mbar",
    "innenluftdruck": "mbar",
    "kuehlwassertemperatur": "°C",
}

def lade_modell_b(pfad="../models/modell_b_ridge_final.joblib"):
    """Laedt Modell B (Ridge) inkl. Preprocessing-Pipeline."""
    return joblib.load(pfad)


def lade_modell_a(pfad="../models/modell_a_logreg_final.joblib"):
    """Laedt Modell A (LogisticRegression) inkl. Scaler."""
    return joblib.load(pfad)


def vorhersage_modell_b(modell_dict, auftrag_dict):
    """
    Gibt fuer einen Auftrag (X_B-Merkmale als Dict) die 6 empfohlenen
    Prozesseinstellungen zurueck, inkl. Konfidenz-Einordnung je Groesse.

    Parameters
    ----------
    modell_dict : dict
        Rueckgabe von lade_modell_b() - enthaelt "modell", "pipeline", "y_spalten".
    auftrag_dict : dict
        X_B-Merkmale, siehe X_B_MERKMALE_ENCODED in preprocessing.py.

    Returns
    -------
    pd.DataFrame mit Spalten: merkmal, empfehlung, r2_konfidenz, konfidenz_stufe
    """
    modell = modell_dict["modell"]
    pipeline = modell_dict["pipeline"]
    y_spalten = modell_dict["y_spalten"]

    X_eingabe = pd.DataFrame([auftrag_dict])
    X_transformiert = pipeline.transform(X_eingabe)
    vorhersage = modell.predict(X_transformiert)[0]

    ergebnis = []
    for i, y_name in enumerate(y_spalten):
        r2 = round(KONFIDENZ_R2_JE_Y_B.get(y_name, np.nan), 2)
        stufe = konfidenz_stufe_bestimmen(r2)
        ergebnis.append({
            "merkmal": y_name,
            "empfehlung": round(vorhersage[i], 2),
            "einheit": EINHEITEN_JE_Y_B.get(y_name, ""),
            "r2_konfidenz": r2,
            "konfidenz_stufe": stufe,
        })

    return pd.DataFrame(ergebnis)


def vorhersage_modell_a(modell_dict, einstellung_dict):
    """
    Gibt fuer eine Prozesseinstellung (X_A-Merkmale als Dict) die IO/NIO-
    Wahrscheinlichkeit zurueck.

    Parameters
    ----------
    modell_dict : dict
        Rueckgabe von lade_modell_a() - enthaelt "modell", "scaler", "feature_namen".
    einstellung_dict : dict
        X_A-Merkmale (Prozesseinstellungen).

    Returns
    -------
    dict mit "vorhersage" ("IO"/"NIO"), "nio_wahrscheinlichkeit" (float)
    """
    modell = modell_dict["modell"]
    scaler = modell_dict["scaler"]
    feature_namen = modell_dict["feature_namen"]

    X_eingabe = pd.DataFrame([einstellung_dict])[feature_namen]
    X_skaliert = scaler.transform(X_eingabe)

    vorhersage = modell.predict(X_skaliert)[0]
    proba = modell.predict_proba(X_skaliert)[0]
    nio_index = list(modell.classes_).index("NIO")

    return {
        "vorhersage": vorhersage,
        "nio_wahrscheinlichkeit": round(proba[nio_index], 4),
    }