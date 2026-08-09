# _MyExtrusionML_Synthetisch

Machbarkeitsstudie + Proof-of-Concept (auf synthetischen Daten) für ein
ML-gestütztes Assistenzsystem zur Extrusionsparameter-Empfehlung bei
UNICOR GmbH (Korrugatoren/Wellrohr-Extrusion).

## Hintergrund
Wissens-Digitalisierung vor Renteneintritt eines erfahrenen Einrichters.
Ziel: UNICOR zeigen, wie eine Lösung aussehen könnte – auf Basis
realistisch generierter synthetischer Daten, da aktuell kein Zugriff
auf Realdaten besteht.

## Modellarchitektur
- **Modell A** (Qualitätsvorhersage): Prozessparameter → Qualitätsmerkmale/IO-NIO
- **Modell B** (Parameter-Empfehlung, Kernziel): Auftragsvorgaben → empfohlene Einstellungen
- Kopplung: Modell A filtert IO-Fälle als Trainingsgrundlage für Modell B

## Status
Phase III (Proof of Concept) – in Bearbeitung.

## Struktur
Siehe `notebooks/` für den Phasenablauf, `reports/tables/` für alle
Analyseergebnisse als CSV, `app/` für den Streamlit-Demonstrator.

## Umgebung
- Python 3.11, Conda-Environment `extrusion-ml`
- `pip install -r requirements.txt`