# =============================================================================
# app/main.py – Streamlit Web-App: Extruder GmbH Prozessparameter-Empfehlung
# Stil: Store44 (Dunkel, Gold, Grün, Blau)
# Tabs: Auftragseingabe & Empfehlung | Qualitaetspruefung
# =============================================================================

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import shap
import warnings
warnings.filterwarnings("ignore")

from app_inference import lade_modell_b, lade_modell_a, vorhersage_modell_b, vorhersage_modell_a

# =============================================================================
# SEITEN-KONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Extruder GmbH – Prozessparameter-Assistent",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# STORE44 CSS STYLING
# =============================================================================
st.markdown("""
<style>
    .stApp { background-color: #1C1C1C; color: #FFFFFF; }

    .main-title {
        font-family: 'Georgia', serif; font-size: 2.6rem; font-weight: 900;
        color: #FFFFFF; border-left: 6px solid #F5A623; padding-left: 20px;
        margin-bottom: 0.2rem;
    }
    .gold-line { height: 3px; background: #F5A623; margin: 0.5rem 0 1.5rem 0; border: none; }

    .kpi-card {
        background-color: #2A2A2A; border-top: 3px solid #F5A623;
        border-radius: 4px; padding: 1.2rem; text-align: center; margin-bottom: 1rem;
    }
    .kpi-value { font-size: 2.0rem; font-weight: 900; color: #F5A623; font-family: 'Georgia', serif; }
    .kpi-label { font-size: 0.8rem; color: #AAAAAA; margin-top: 0.2rem; text-transform: uppercase; }
    .kpi-konfidenz-hoch { font-size: 0.75rem; color: #4A5C3A; font-weight: 700; }
    .kpi-konfidenz-mittel { font-size: 0.75rem; color: #6CB4E4; font-weight: 700; }
    .kpi-konfidenz-niedrig { font-size: 0.75rem; color: #777777; font-weight: 700; }

    .section-header {
        font-size: 1.05rem; font-weight: 700; color: #F5A623;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.8rem;
    }

    .decision-io {
        background-color: #4A5C3A; border-top: 4px solid #F5A623;
        border-radius: 4px; padding: 1.5rem; text-align: center;
    }
    .decision-nio {
        background-color: #2A3F4F; border-top: 4px solid #6CB4E4;
        border-radius: 4px; padding: 1.5rem; text-align: center;
    }
    .decision-text { font-size: 1.8rem; font-weight: 900; color: #FFFFFF; font-family: 'Georgia', serif; }
    .confidence-text { font-size: 0.95rem; color: #AAAAAA; margin-top: 0.4rem; }

    .stTabs [data-baseweb="tab-list"] { background-color: #2A2A2A; border-bottom: 2px solid #F5A623; }
    .stTabs [data-baseweb="tab"] { color: #AAAAAA; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #F5A623 !important; border-bottom: 3px solid #F5A623; }

    label { color: #AAAAAA !important; font-size: 0.85rem !important; }

    .stButton > button {
        background-color: #F5A623; color: #1C1C1C; font-weight: 800;
        border: none; border-radius: 2px; padding: 0.6rem 2rem; width: 100%;
    }
    .stButton > button:hover { background-color: #D4891F; color: #1C1C1C; }

    .footer { text-align: center; color: #555555; font-size: 0.75rem; margin-top: 3rem;
              padding-top: 1rem; border-top: 1px solid #2A2A2A; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MODELLE LADEN (gecacht)
# =============================================================================
@st.cache_resource
def lade_alle_modelle():
    modell_b = lade_modell_b("models/modell_b_ridge_final.joblib")
    modell_a = lade_modell_a("models/modell_a_logreg_final.joblib")
    return modell_b, modell_a

modell_b_geladen, modell_a_geladen = lade_alle_modelle()

# =============================================================================
# HEADER
# =============================================================================
st.markdown('<div class="main-title">PROZESSPARAMETER-ASSISTENT</div>', unsafe_allow_html=True)
st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#AAAAAA; font-size:0.9rem; margin-bottom:2rem;">'
    'Extruder GmbH &nbsp;|&nbsp; Machbarkeitsstudie &nbsp;|&nbsp; Synthetische Daten</p>',
    unsafe_allow_html=True
)

# =============================================================================
# TABS
# =============================================================================
tab1, tab2 = st.tabs(["📋  AUFTRAGSEINGABE & EMPFEHLUNG", "🔍  QUALITÄTSPRÜFUNG"])

# ===========================================================================
# TAB 1 – AUFTRAGSEINGABE & EMPFEHLUNG
# ===========================================================================
with tab1:
    st.markdown('<p class="section-header">Kundenauftrag Eingabe</p>', unsafe_allow_html=True)

    with st.form("auftrag_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Material & Geometrie**")
            material_mfr = st.number_input("Material MFR (g/10min)", min_value=0.3, max_value=1.5, value=0.7, step=0.05)
            dn_ziel = st.number_input("Ziel-Nennweite DN (mm)", min_value=50, max_value=315, value=150, step=5)
            wandstaerke_soll = st.number_input("Wandstärke-Soll (mm)", min_value=0.8, max_value=6.0, value=2.2, step=0.1)

        with col2:
            st.markdown("**Toleranzen & Anforderungen**")
            dickentoleranz = st.number_input("Dickentoleranz (mm)", min_value=0.05, max_value=0.30, value=0.15, step=0.01)
            ovalitaet_anforderung = st.number_input("Ovalitäts-Anforderung", min_value=0.3, max_value=1.0, value=0.6, step=0.05,
                                                      help="Kleinerer Wert = strengere Anforderung")
            produktionsgeschwindigkeit_soll = st.number_input("Produktionsgeschwindigkeit (m/min)", min_value=2.0, max_value=17.0, value=10.0, step=0.5)

        with col3:
            st.markdown("**Konstruktion**")
            wandtyp = st.selectbox("Wandtyp", ["einwandig", "doppelwandig"])

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("EMPFEHLUNG BERECHNEN")

    if submitted:
        auftrag_dict = {
            "material_mfr": material_mfr, "dn_ziel": dn_ziel, "wandstaerke_soll": wandstaerke_soll,
            "dickentoleranz": dickentoleranz, "produktionsgeschwindigkeit_soll": produktionsgeschwindigkeit_soll,
            "ovalitaet_anforderung": ovalitaet_anforderung,
            "wandtyp_einwandig": 1 if wandtyp == "einwandig" else 0,
        }

        ergebnis_df = vorhersage_modell_b(modell_b_geladen, auftrag_dict)

        # Im Session State speichern, fuer Vorbefuellung in Tab 2
        st.session_state["empfehlung"] = dict(zip(ergebnis_df["merkmal"], ergebnis_df["empfehlung"]))

        st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-header">Empfohlene Prozesseinstellungen</p>', unsafe_allow_html=True)

        konfidenz_klassen = {"hoch": "kpi-konfidenz-hoch", "mittel": "kpi-konfidenz-mittel", "niedrig": "kpi-konfidenz-niedrig"}
        konfidenz_labels = {"hoch": "● Hohe Konfidenz", "mittel": "● Mittlere Konfidenz", "niedrig": "● Niedrige Konfidenz"}

        kpi_cols = st.columns(3)
        for i, (_, row) in enumerate(ergebnis_df.iterrows()):
            col = kpi_cols[i % 3]
            konf_klasse = konfidenz_klassen[row["konfidenz_stufe"]]
            konf_label = konfidenz_labels[row["konfidenz_stufe"]]
            col.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{row['empfehlung']} {row['einheit']}</div>
                <div class="kpi-label">{row['merkmal'].replace('_', ' ').title()}</div>
                <div class="{konf_klasse}">{konf_label} (R²={row['r2_konfidenz']:.2f})</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            '<p style="color:#AAAAAA; font-size:0.85rem; margin-top:1rem;">'
            'Hinweis: Werte mit niedriger/mittlerer Konfidenz sind eine erste Orientierung – '
            'die endgültige Feinjustierung erfolgt durch den Experten während der Inbetriebnahme. '
            'Wechseln Sie zum Tab "Qualitätsprüfung", um diese Einstellung zu testen.</p>',
            unsafe_allow_html=True
        )

# ===========================================================================
# TAB 2 – QUALITÄTSPRÜFUNG (Modell A + SHAP)
# ===========================================================================
with tab2:
    st.markdown('<p class="section-header">Prozesseinstellung prüfen</p>', unsafe_allow_html=True)

    vorbefuellung = st.session_state.get("empfehlung", {})

    with st.form("pruefung_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Extruder-Parameter**")
            schneckendrehzahl = st.number_input("Schneckendrehzahl (U/min)", min_value=10.0, max_value=80.0,
                                                  value=float(vorbefuellung.get("schneckendrehzahl", 44.0)), step=0.5)
            massedurchsatz = st.number_input("Massedurchsatz (kg/h)", min_value=5.0, max_value=100.0, value=35.0, step=1.0)
            massetemperatur = st.number_input("Massetemperatur (°C)", min_value=190.0, max_value=232.0,
                                                value=float(vorbefuellung.get("massetemperatur", 204.0)), step=0.5)
            massedruck = st.number_input("Massedruck (bar)", min_value=50.0, max_value=250.0, value=145.0, step=5.0)

        with col2:
            st.markdown("**Kalibrierung**")
            duesenspalt = st.number_input("Düsenspalt (mm)", min_value=0.35, max_value=6.5,
                                            value=float(vorbefuellung.get("duesenspalt", 2.3)), step=0.05)
            abzugsgeschwindigkeit = st.number_input("Abzugsgeschwindigkeit (m/min)", min_value=0.3, max_value=15.0, value=1.4, step=0.1)
            kalibrierdruck_mbar = st.number_input("Kalibrierdruck (mbar)", min_value=-400.0, max_value=200.0, value=90.0, step=5.0)
            kuehlwassertemperatur = st.number_input("Kühlwassertemperatur (°C)", min_value=5.0, max_value=28.0,
                                                      value=float(vorbefuellung.get("kuehlwassertemperatur", 19.0)), step=0.5)

        with col3:
            st.markdown("**Material & Konstruktion**")
            mfr_charge = st.number_input("MFR Charge (g/10min)", min_value=0.3, max_value=1.5, value=0.7, step=0.05)
            wandtyp_pruef = st.selectbox("Wandtyp", ["einwandig", "doppelwandig"], key="wandtyp_pruef")
            mechanismus_pruef = st.selectbox("Kalibriermechanismus", ["Formluft", "Vakuum"], key="mechanismus_pruef")

            st.markdown("<br>", unsafe_allow_html=True)
            geprueft = st.form_submit_button("QUALITÄT PRÜFEN")

    if geprueft:
        einstellung_dict = {
            "schneckendrehzahl": schneckendrehzahl, "massedurchsatz": massedurchsatz,
            "massetemperatur": massetemperatur, "massedruck": massedruck,
            "duesenspalt": duesenspalt, "abzugsgeschwindigkeit": abzugsgeschwindigkeit,
            "kalibrierdruck_mbar": kalibrierdruck_mbar, "kuehlwassertemperatur": kuehlwassertemperatur,
            "mfr_charge": mfr_charge,
            "wandtyp_einwandig": 1 if wandtyp_pruef == "einwandig" else 0,
            "mechanismus_Vakuum": 1 if mechanismus_pruef == "Vakuum" else 0,
        }

        ergebnis_a = vorhersage_modell_a(modell_a_geladen, einstellung_dict)

        st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-header">Ergebnis</p>', unsafe_allow_html=True)

        if ergebnis_a["vorhersage"] == "IO":
            st.markdown(f"""
            <div class="decision-io">
                <div class="decision-text">✅ IO (In Ordnung)</div>
                <div class="confidence-text">NIO-Wahrscheinlichkeit: {ergebnis_a['nio_wahrscheinlichkeit']:.1%}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="decision-nio">
                <div class="decision-text">⚠️ NIO (Nicht in Ordnung)</div>
                <div class="confidence-text">NIO-Wahrscheinlichkeit: {ergebnis_a['nio_wahrscheinlichkeit']:.1%}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">SHAP Erklärung</p>', unsafe_allow_html=True)
        st.markdown(
            '<p style="color:#AAAAAA; font-size:0.85rem;">Welche Parameter haben diese Einschätzung am stärksten beeinflusst?</p>',
            unsafe_allow_html=True
        )

        try:
            modell_obj = modell_a_geladen["modell"]
            scaler_obj = modell_a_geladen["scaler"]
            feature_namen = modell_a_geladen["feature_namen"]
            X_train_referenz = modell_a_geladen["X_train_skaliert"]

            X_eingabe_df = pd.DataFrame([einstellung_dict])[feature_namen]
            X_skaliert = scaler_obj.transform(X_eingabe_df)
            X_skaliert_df = pd.DataFrame(X_skaliert, columns=feature_namen)

            explainer = shap.LinearExplainer(modell_obj, X_train_referenz)
            shap_werte = explainer(X_skaliert_df)

            # --- Kombinierte Beschriftung: "Originalwert (Z=x.xx) = merkmal" ---
            kombinierte_labels = [
                f"{name} (Z={X_skaliert_df.iloc[0][name]:.2f})"
                for name in feature_namen
            ]
            shap_werte_kombiniert = shap.Explanation(
                values=shap_werte.values[0],
                base_values=shap_werte.base_values[0],
                data=X_eingabe_df.values[0],   # Original-Wert statt Z-Score als "data"
                feature_names=kombinierte_labels,
            )

            plt.rcParams["figure.facecolor"] = "#1C1C1C"
            plt.rcParams["axes.facecolor"] = "#1C1C1C"
            fig = plt.figure(figsize=(10, 5))
            shap.plots.waterfall(shap_werte_kombiniert, show=False)
            fig = plt.gcf()
            fig.patch.set_facecolor("#1C1C1C")
            for a in fig.get_axes():
                a.set_facecolor("#1C1C1C")
                a.tick_params(colors="white", labelcolor="white")
                for t in a.texts:
                    t.set_color("white")
                for patch in a.patches:
                    farbe = patch.get_facecolor()
                    if farbe[0] > farbe[2]:
                        patch.set_facecolor("#F5A623")
                    else:
                        patch.set_facecolor("#6CB4E4")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            st.markdown(
                '<p style="color:#AAAAAA; font-size:0.8rem; margin-top:0.5rem;">'
                'Format: [tatsächlicher Prozesswert] (Z=[standardisierter Wert, wie das Modell rechnet]) = Parameter. '
                'Die SHAP-Werte (Balkenlängen) sind auf der Log-Odds-Skala.</p>',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.warning(f"SHAP-Erklärung konnte nicht berechnet werden: {e}")
# --- Footer ---
st.markdown(
    '<div class="footer">Extruder GmbH Machbarkeitsstudie &nbsp;|&nbsp; Ridge (Modell B) + LogisticRegression (Modell A)</div>',
    unsafe_allow_html=True
)
