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
# KORREKTUR: "residual" und "combined" referenzierten bisher die in
# Notebook 04 VORAB (auf dem Gesamtdatensatz) berechneten *_dn_bereinigt-
# Spalten - das ist Data Leakage bei Verwendung im Modelltraining (PCA und
# Regressionen wurden nicht nur auf Trainingsdaten gefittet). Diese Sets
# definieren daher nur noch die BASIS-Spalten (Rohwerte + kategorial); die
# eigentliche Residualisierung erfolgt erst innerhalb der Pipeline ueber
# DNResidualizer (siehe unten), pro CV-Fold neu gefittet.
#
# "original":              9 Rohwerte + 2 kategoriale Merkmale
# "original_no_kategorial": nur die 9 numerischen Rohwerte, ohne wandtyp/
#                           mechanismus - prueft deren eigenstaendigen
#                           Beitrag (siehe Cramer's V-Befund Notebook 03:
#                           kaum eigenstaendiger Effekt erwartet)
# "residual":               DNResidualizer wird in der Pipeline auf die
#                           9 numerischen Basis-Spalten angewendet, plus
#                           die 2 kategorialen Merkmale unveraendert
# "combined":               Original-Rohwerte UND Residuen gemeinsam
#                           (durch FeatureUnion in der Pipeline)
NUMERISCHE_BASIS_SPALTEN = [
    "schneckendrehzahl", "massedurchsatz", "massetemperatur", "massedruck",
    "duesenspalt", "abzugsgeschwindigkeit", "kalibrierdruck_mbar",
    "kuehlwassertemperatur", "mfr_charge",
]
KATEGORIALE_SPALTEN = ["wandtyp_einwandig", "mechanismus_Vakuum"]

FEATURE_SETS = {
    "original": NUMERISCHE_BASIS_SPALTEN + KATEGORIALE_SPALTEN,
    "original_no_kategorial": NUMERISCHE_BASIS_SPALTEN,
    "residual": NUMERISCHE_BASIS_SPALTEN + KATEGORIALE_SPALTEN,  # Basis-Spalten, DNResidualizer transformiert diese in der Pipeline
    "combined": NUMERISCHE_BASIS_SPALTEN + KATEGORIALE_SPALTEN,  # Basis-Spalten, FeatureUnion in der Pipeline fuegt Residuen hinzu
}

# Hinweis fuer Notebook 05: welche Sets brauchen DNResidualizer in der Pipeline,
# und in welchem Modus (ersetzen vs. ergaenzen)
FEATURE_SET_RESIDUALIZATION_MODE = {
    "original": None,
    "original_no_kategorial": None,
    "residual": "replace",   # Rohwerte durch Residuen ersetzen
    "combined": "augment",   # Residuen zusaetzlich zu Rohwerten
}


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

# =============================================================================
# DNResidualizer - leakage-sicherer sklearn-Transformer
# =============================================================================
# Ersetzt die explorative Residualisierung aus Notebook 04 (dort auf dem
# GESAMTEN Datensatz berechnet - nur fuer die EDA/Validierung zulaessig,
# NICHT fuer das eigentliche Modelltraining). Dieser Transformer lernt
# PCA-Achse (dn_proxy) und die numerischen Regressionen AUSSCHLIESSLICH in
# fit() aus den ihm uebergebenen Daten - bei Verwendung in einer
# sklearn.Pipeline geschieht das automatisch nur auf dem jeweiligen
# Trainings-Fold, transform() wendet die gelernten Parameter unveraendert
# auf Trainings- UND Testdaten an. Strukturell leakage-sicher.
# =============================================================================

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression


class DNResidualizer(BaseEstimator, TransformerMixin):
    """
    Berechnet DN-bereinigte Residual-Features fuer numerische X_A-Merkmale.

    fit(X): lernt StandardScaler, PCA(1 Komponente) -> dn_proxy, und je
            numerischem Merkmal eine LinearRegression auf dn_proxy -
            ausschliesslich aus den in fit() uebergebenen Daten (bei
            Pipeline-Nutzung: nur Trainings-Fold).
    transform(X): wendet die gelernten Parameter an, gibt die Residuen
                  (und optional dn_proxy) fuer beliebige neue Daten zurueck.
    """

    def __init__(self, numerische_spalten, include_dn_proxy=False):
        self.numerische_spalten = numerische_spalten
        self.include_dn_proxy = include_dn_proxy

    def fit(self, X, y=None):
        X = pd.DataFrame(X, columns=self.numerische_spalten) if not isinstance(X, pd.DataFrame) else X
        self.scaler_ = StandardScaler().fit(X[self.numerische_spalten])
        X_scaled = self.scaler_.transform(X[self.numerische_spalten])

        self.pca_ = PCA(n_components=1, random_state=42).fit(X_scaled)
        dn_proxy_train = self.pca_.transform(X_scaled).flatten()

        self.regressions_ = {}
        for col in self.numerische_spalten:
            lr = LinearRegression().fit(dn_proxy_train.reshape(-1, 1), X[col])
            self.regressions_[col] = lr

        return self

    def transform(self, X):
        X = pd.DataFrame(X, columns=self.numerische_spalten) if not isinstance(X, pd.DataFrame) else X
        X_scaled = self.scaler_.transform(X[self.numerische_spalten])
        dn_proxy = self.pca_.transform(X_scaled).flatten()

        residuen = pd.DataFrame(index=X.index)
        for col in self.numerische_spalten:
            vorhersage = self.regressions_[col].predict(dn_proxy.reshape(-1, 1))
            residuen[f"{col}_dn_bereinigt"] = X[col].values - vorhersage

        if self.include_dn_proxy:
            residuen["dn_proxy"] = dn_proxy

        return residuen