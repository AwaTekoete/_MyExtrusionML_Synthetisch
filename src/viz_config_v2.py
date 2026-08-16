# =============================================================================
# viz_config_v2.py - Zentrale Visualisierungs-Konfiguration (Store44-Farbschema)
# =============================================================================
# Wird von allen Notebooks importiert, damit Farben/Stil projektweit konsistent
# sind und nur an dieser Stelle gepflegt werden muessen.
#
# VERSIONIERUNG: Dateiname traegt Versionsstand, um Versions-Mismatch zwischen
# Notebooks zu vermeiden. Aeltere Notebooks referenzieren ggf. eine fruehere
# Version bewusst weiter, bis sie explizit aktualisiert werden.
#
# Aenderungs-Historie:
# v1 (Projektstart): Basis-Farbpalette, apply_store44_style(), save_figure()
# v2 (Notebook 03, Boxplot-Faerbung): BOXPLOT_STYLE ergaenzt - matplotlib
#     setzt Whisker/Cap/Outlier-Linien standardmaessig auf Schwarz,
#     unabhaengig von apply_store44_style(); auf dunklem Hintergrund schlecht
#     lesbar. Explizite Style-Konstante fuer konsistente Wiederverwendung.
# =============================================================================

__version__ = "2.0"

import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# Store44-Farbpalette (Referenz: Praesentationsstil_Store44.md)
# -----------------------------------------------------------------------------
COLOR_BACKGROUND = "#1C1C1C"   # Folien-/Plot-Hintergrund
COLOR_CARD_BG = "#2A2A2A"      # Hintergrund fuer Boxen/Tabellen
COLOR_GOLD = "#F5A623"         # Primaerakzent: wichtigste Zahl/Kategorie
COLOR_BLUE = "#6CB4E4"         # Sekundaerakzent: Vergleichswert/Balken
COLOR_GREEN = "#4A5C3A"        # Highlight: Champion/Loesung
COLOR_TEXT = "#FFFFFF"         # Primaerer Text
COLOR_TEXT_MUTED = "#AAAAAA"   # Sekundaerer Text/Captions

# Fuer Klassifikation: feste Zuordnung Klasse -> Farbe (konsistent ueber alle Plots)
# Projektspezifisch (_MyExtrusionML_Synthetisch): IO/NIO statt Katastrophen-Klassen
COLOR_IO = COLOR_GREEN    # "IO" (Gutteil/Erfolg)
COLOR_NIO = COLOR_BLUE    # "NIO" (Ausschuss/Vergleichswert)

# -----------------------------------------------------------------------------
# Boxplot-Style (v2): explizite Farbgebung fuer Whisker/Cap/Median/Ausreisser,
# da matplotlib-Defaults (Schwarz) auf dunklem Hintergrund schlecht lesbar sind
# -----------------------------------------------------------------------------
BOXPLOT_STYLE = dict(
    whiskerprops=dict(color=COLOR_TEXT_MUTED, linewidth=1.2),
    capprops=dict(color=COLOR_TEXT_MUTED, linewidth=1.2),
    medianprops=dict(color=COLOR_GOLD, linewidth=1.8),
    flierprops=dict(marker="o", markeredgecolor=COLOR_GOLD, markerfacecolor="none", markersize=4),
)


def apply_store44_style():
    """
    Setzt globale matplotlib-Parameter fuer das Store44-Farbschema.
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
    Speichert eine Figure mit Store44-Hintergrund (auch ausserhalb der Achsen).
    filepath z. B. 'reports/figures/01_eda_class_balance.png'
    """
    fig.savefig(
        filepath,
        dpi=dpi,
        facecolor=COLOR_BACKGROUND,
        bbox_inches="tight",
    )
