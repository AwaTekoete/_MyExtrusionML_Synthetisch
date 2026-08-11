# =============================================================================
# preprocessing.py - Wiederverwendbare Auswahlfunktionen (Modell A)
# =============================================================================
# Architektur (Option C, vereinbart bei AP 3.3): Feature-/Zielgroessen-
# KONSTRUKTION erfolgt einmalig in Notebook 04 und wird als vollstaendiger,
# angereicherter Datensatz gespeichert (data/processed/model_a_preprocessed.csv).
# Dieses Modul stellt NUR die AUSWAHL-Logik bereit (welche Spalten bilden
# X, welche bilden y, fuer eine gegebene Kombination) - die eigentliche
# Ablationsschleife (Iteration ueber alle Kombinationen, Training, Vergleich)
# bleibt in Notebook 05/06. Keine Duplizierung, klare Trennung der
# Verantwortlichkeiten.
#
# WICHTIG (Data-Leakage-Hinweis): Dieses Modul waehlt nur Spalten aus,
# es fittet keine Transformationen (Skalierung, Imputation). Diese muessen
# in Notebook 05/06 innerhalb einer sklearn.Pipeline erfolgen, mit
# fit_transform NUR auf Trainingsdaten.
# =============================================================================

import pandas as pd


# -----------------------------------------------------------------------------
# Feature-Sets (X-Varianten)
# -----------------------------------------------------------------------------
# "original": nur die 10 echten X_A-Prozessparameter (inkl. Encoding) -
#             Referenz-/Baseline-Feature-Set
# "residual": DN-bereinigte Residual-Features statt Original-Rohwerte
#             (kategoriale Merkmale bleiben unveraendert, da residualisiert
#             nur fuer numerische Groessen sinnvoll ist)
# "combined": Original UND Residuen gemeinsam (mehr Dimensionen, hoeheres
#             Overfitting-Risiko bei n=700 - im Ablationsvergleich pruefen)
FEATURE_SETS = {
    "original": [
        "schneckendrehzahl", "massedurchsatz", "massetemperatur", "massedruck",
        "duesenspalt", "abzugsgeschwindigkeit", "kalibrierdruck_mbar",
        "kuehlwassertemperatur", "mfr_charge",
        "wandtyp_einwandig", "mechanismus_Vakuum",
    ],
    "residual": [
        "schneckendrehzahl_dn_bereinigt", "massedurchsatz_dn_bereinigt",
        "massetemperatur_dn_bereinigt", "massedruck_dn_bereinigt",
        "duesenspalt_dn_bereinigt", "abzugsgeschwindigkeit_dn_bereinigt",
        "kalibrierdruck_mbar_dn_bereinigt", "kuehlwassertemperatur_dn_bereinigt",
        "mfr_charge_dn_bereinigt",
        "wandtyp_einwandig", "mechanismus_Vakuum",
    ],
}
FEATURE_SETS["combined"] = FEATURE_SETS["original"] + [
    c for c in FEATURE_SETS["residual"] if c.endswith("_dn_bereinigt")
]


# -----------------------------------------------------------------------------
# Zielgroessen-Varianten (y-Varianten)
# -----------------------------------------------------------------------------
# "binary":      io_nio (IO/NIO) - klassische Klassifikation, Referenzvariante
# "continuous":  y_kontinuierlich_sicherheitsabstand - Regression, siehe
#                Notebook 03 Nachtrag (Blocker-A-Gegenmassnahme)
# "multilabel":  9 einzelne y_nio_*-Spalten - Multi-Label-Klassifikation
TARGET_VARIANTS = {
    "binary": {"columns": ["io_nio"], "mask_column": None},
    "continuous": {
        "columns": ["y_kontinuierlich_sicherheitsabstand"],
        "mask_column": "y_od_komponente_zuverlaessig",  # siehe Nachtrag 4, generation_summary.md
    },
    "multilabel": {
        "columns": [
            "y_nio_wandstaerke", "y_nio_ovalitaet", "y_nio_od", "y_nio_wellhoehe",
            "y_nio_bindenaehte", "y_nio_blasenbildung", "y_nio_risse",
            "y_nio_oberflaechenfehler", "y_nio_delamination",
        ],
        "mask_column": None,  # delamination-Spezialfall separat ueber
                               # delamination_anwendbar behandelbar, siehe
                               # get_target() Docstring
    },
}


def load_dataset(path="../data/processed/model_a_preprocessed.csv"):
    """Laedt den finalen Preprocessing-Datensatz aus Notebook 04."""
    return pd.read_csv(path)


def get_feature_set(df, feature_set_name):
    """
    Gibt X (DataFrame) fuer das angegebene Feature-Set zurueck.

    Parameters
    ----------
    df : pd.DataFrame
        Vollstaendiger Preprocessing-Datensatz (aus load_dataset()).
    feature_set_name : str
        Einer von: "original", "residual", "combined" (siehe FEATURE_SETS).

    Returns
    -------
    pd.DataFrame
        Nur die Spalten des gewaehlten Feature-Sets.
    """
    if feature_set_name not in FEATURE_SETS:
        raise ValueError(f"Unbekanntes Feature-Set '{feature_set_name}'. "
                          f"Verfuegbar: {list(FEATURE_SETS.keys())}")
    spalten = FEATURE_SETS[feature_set_name]
    fehlend = [c for c in spalten if c not in df.columns]
    if fehlend:
        raise KeyError(f"Feature-Spalten fehlen im Datensatz: {fehlend}")
    return df[spalten].copy()


def get_target(df, target_variant_name, respect_mask=True):
    """
    Gibt y (Series oder DataFrame) fuer die angegebene Zielgroessen-Variante
    zurueck, sowie eine boolesche Maske gueltiger Zeilen.

    Parameters
    ----------
    df : pd.DataFrame
        Vollstaendiger Preprocessing-Datensatz (aus load_dataset()).
    target_variant_name : str
        Einer von: "binary", "continuous", "multilabel" (siehe TARGET_VARIANTS).
    respect_mask : bool, default True
        Falls True, werden Zeilen mit bekannten Unsicherheiten/Nicht-
        Anwendbarkeit ueber die zugehoerige mask_column ausmaskiert
        (siehe TARGET_VARIANTS). Bei "multilabel" betrifft dies zusaetzlich
        delamination_anwendbar fuer die y_nio_delamination-Spalte speziell -
        wird hier NICHT automatisch behandelt, da es nur eine von neun
        Spalten betrifft (partielle Maskierung eines Multi-Label-Vektors
        ist modellabhaengig zu loesen, z.B. per Klassifikator-Kette mit
        spaltenweiser Maske) - bei Bedarf gesondert in Notebook 05/06
        umsetzen, siehe delamination_anwendbar-Spalte im Datensatz.

    Returns
    -------
    y : pd.Series oder pd.DataFrame
        Zielgroesse(n) fuer die gueltigen Zeilen (nach Maskierung).
    valid_mask : pd.Series (bool)
        True fuer Zeilen, die in y enthalten sind (Index-kompatibel zu df).
    """
    if target_variant_name not in TARGET_VARIANTS:
        raise ValueError(f"Unbekannte Zielgroessen-Variante '{target_variant_name}'. "
                          f"Verfuegbar: {list(TARGET_VARIANTS.keys())}")

    konfiguration = TARGET_VARIANTS[target_variant_name]
    spalten = konfiguration["columns"]
    mask_spalte = konfiguration["mask_column"]

    fehlend = [c for c in spalten if c not in df.columns]
    if fehlend:
        raise KeyError(f"Zielgroessen-Spalten fehlen im Datensatz: {fehlend}")

    valid_mask = pd.Series(True, index=df.index)
    if respect_mask and mask_spalte is not None:
        if mask_spalte not in df.columns:
            raise KeyError(f"Masken-Spalte '{mask_spalte}' fehlt im Datensatz")
        valid_mask = df[mask_spalte].astype(bool)

    y = df.loc[valid_mask, spalten]
    if len(spalten) == 1:
        y = y.iloc[:, 0]  # als Series statt einspaltigem DataFrame

    return y, valid_mask


def select_dataset(df, feature_set_name, target_variant_name, respect_mask=True):
    """
    Kombinierte Auswahl: X und y fuer eine gegebene Feature-Set/Zielgroessen-
    Kombination, konsistent nach der Zielgroessen-Maske gefiltert.

    Beispiel
    --------
    >>> df = load_dataset()
    >>> X, y = select_dataset(df, "residual", "continuous")

    Parameters
    ----------
    df : pd.DataFrame
    feature_set_name : str
        Siehe FEATURE_SETS.
    target_variant_name : str
        Siehe TARGET_VARIANTS.
    respect_mask : bool, default True

    Returns
    -------
    X : pd.DataFrame
    y : pd.Series oder pd.DataFrame
    """
    y, valid_mask = get_target(df, target_variant_name, respect_mask=respect_mask)
    X = get_feature_set(df.loc[valid_mask], feature_set_name)
    return X, y
