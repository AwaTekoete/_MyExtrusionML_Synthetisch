# =============================================================================
# viz_config.py – Zentrale Visualisierungs-Konfiguration (Store44-Farbschema)
# =============================================================================
# Wird von allen Notebooks importiert, damit Farben/Stil projektweit konsistent
# sind und nur an dieser Stelle gepflegt werden müssen.

import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# Store44-Farbpalette (Referenz: Praesentationsstil_Store44.md)
# -----------------------------------------------------------------------------
COLOR_BACKGROUND = "#1C1C1C"   # Folien-/Plot-Hintergrund
COLOR_CARD_BG = "#2A2A2A"      # Hintergrund für Boxen/Tabellen
COLOR_GOLD = "#F5A623"         # Primärakzent: wichtigste Zahl/Kategorie
COLOR_BLUE = "#6CB4E4"         # Sekundärakzent: Vergleichswert/Balken
COLOR_GREEN = "#4A5C3A"        # Highlight: Champion/Lösung
COLOR_TEXT = "#FFFFFF"         # Primärer Text
COLOR_TEXT_MUTED = "#AAAAAA"   # Sekundärer Text/Captions

# Für Klassifikation: feste Zuordnung Klasse -> Farbe (konsistent über alle Plots)
COLOR_CLASS_0 = COLOR_BLUE   # "keine Katastrophe"
COLOR_CLASS_1 = COLOR_GOLD   # "Katastrophe"


def apply_store44_style():
    """
    Setzt globale matplotlib-Parameter für das Store44-Farbschema.
    Einmal pro Notebook aufrufen (z. B. in Zelle 01 nach den Imports).
    """
    plt.rcParams.update({
        "figure.facecolor": COLOR_BACKGROUND,
        "axes.facecolor": COLOR_BACKGROUND,
        "axes.edgecolor": COLOR_TEXT_MUTED,
        "axes.labelcolor": COLOR_TEXT,
        "text.color": COLOR_TEXT,
        "xtick.color": COLOR_TEXT_MUTED,
        "ytick.color": COLOR_TEXT_MUTED,
        "axes.titlecolor": COLOR_TEXT,
        "grid.color": "#3A3A3A",
        "font.size": 12,
    })


def save_figure(fig, filepath, dpi=150):
    """
    Speichert eine Figure mit Store44-Hintergrund (auch außerhalb der Achsen).
    filepath z. B. 'reports/figures/01_eda_class_balance.png'
    """
    fig.savefig(
        filepath,
        dpi=dpi,
        facecolor=COLOR_BACKGROUND,
        bbox_inches="tight",
    )