# Generation Summary – Synthetische Datengenerierung

Laufend gepflegtes Dokument; wird bei jedem Generierungs-Notebook ergaenzt.

---

## Notebook 02 – Modell A (Prozessparameter -> Qualitaet)

### Durchgefuehrte Schritte
| Zelle | Inhalt | Status |
|---|---|---|
| 01 | Setup & Imports | Erledigt |
| 02 | X_A-Basisvariablen (geclusterte Verteilung ueber latente DN-Groesse) | Erledigt |
| 03 | Geometrie-Zielgroessen (Wandstaerke, Aussendurchmesser, Ovalitaet) | Erledigt |
| 04 | Wellgeometrie (Wellhoehe/-teilung Ist) | Erledigt |
| 05 | Strukturelle/Oberflaechen-Fehlermerkmale | Erledigt |
| 05b | Wandtyp + Delamination | Erledigt |
| 06 | IO/NIO-Aggregation | Erledigt |
| 07 | Realismus-Luecken (MCAR, 4.4%) | Erledigt |
| 08 | Speichern (raw + latente Referenzdatei) | Erledigt |

### Zentrale Entscheidungen
- N = 700 Datensaetze (begruendet: 5-Fold-CV-Tauglichkeit, Lernkurven-Analyse moeglich;
  Erik-Entscheidung nach Empfehlung 500-800)
- Realistische, geclusterte (nicht gleichverteilte) X-Generierung ueber latente
  Nennweiten-Groesse `rohr_dn_latent` (Generierungshilfsgroesse, nicht Teil
  der finalen Trainingsdaten - vgl. Datenverfuegbarkeits-Prinzip: kein Feature,
  das ein realer Bediener bei reinen Prozessdaten nicht haette)
- Kausale Kopplung statt unabhaengiger Zufallsziehung, z. B.:
  - Wandstaerke_Ist = Duesenspalt / realisierter Die-Swell-Faktor
    (realisierter Faktor haengt von Massetemperatur/MFR ab, weicht vom beim
    Duesenspalt-Setzen angenommenen Faktor ab -> Kernmechanismus fuer Modell A)
  - Wellhoehe_Ist = Wellhoehe_Soll * Ausformungsgrad (Ausformungsgrad haengt
    von Vakuumstaerke ab)
  - Aussendurchmesser/Ovalitaet-Streuung haengt von Vakuum-Kalibrierguete ab
- AZV und v_D (Abzugsverhaeltnis, Duesenaustrittsgeschwindigkeit) bewusst NICHT
  in Rohdatengenerierung aufgenommen - das sind laut Parametertabelle
  `Erfassungsart=berechnet`-Groessen und gehoeren methodisch ins Feature
  Engineering (Notebook 04_preprocessing), nicht in die Rohdaten (Erik-Hinweis)
- Zwei Kalibrierungs-Iterationen noetig: urspruengliche Formel-Konstanten
  fuehrten zu massivem Clipping (Massedruck 100% an oberer Grenze, Drehzahl 74%) -
  behoben durch (a) Korrektur der massedurchsatz-Formel (Ursache lag dort),
  (b) gedaempfte sqrt-Kopplung Durchsatz->Drehzahl statt linear, (c) normierte
  statt absolute Groessen bei Massedruck-Formel. Ergebnis: 0-4% Clipping.
- Delamination nachtraeglich ergaenzt: Wandtyp als Kontextvariable eingefuehrt
  (urspruengliche X_A-Liste sah kein Wandtyp-Merkmal vor); Delamination nur
  bei doppelwandig ueberhaupt anwendbar/gemessen
- Fehlende Werte bewusst zweigeteilt:
  - MNAR (strukturell): Delamination bei einwandigen Rohren (nicht messbar)
  - MCAR (zufaellig): 4 Spalten (kuehlwassertemperatur, mfr_charge,
    wellteilung_ist, aussendurchmesser_ist), Rate 4.4%
  Diese Unterscheidung ist fuer die spaetere EDA (Missing-Value-Mechanismus
  pruefen) bewusst relevant.
- Delamination-Schwelle musste nachtraeglich rekalibriert werden (erste
  Version: 0% Rate, da Schwellenwert ausserhalb des realistischen
  Massetemperatur-Wertebereichs lag)

### Ergebnis
- NIO-Rate: 26.1% (183/700 Datensaetze) - kein Extremungleichgewicht
- Hauptursachen NIO (Anteil an allen NIO-Faellen):
  - Ovalitaet: 33.9%
  - Wandstaerke: 24.0%
  - Oberflaechenfehler: 24.0%
  - Wellhoehe: 17.5%
  - Aussendurchmesser: 16.9%
  - Risse: 6.0%
  - Blasenbildung: 3.8%
  - Bindenaehte: 0.5%
- Delamination-Rate (nur doppelwandig, 24.7% aller Faelle): 1.7%

### Gespeicherte Artefakte
- `data/raw/model_a_raw.csv` (700 Zeilen, 21 Spalten: 11 X_A, 10 Y_A inkl. io_nio)
- `data/raw/model_a_latent_reference.csv` (700 Zeilen, 2 Spalten: rohr_dn_latent,
  wandstaerke_ideal_latent) - NICHT Teil der Trainingsdaten, dient ausschliesslich
  als Ground-Truth-Referenz fuer spaetere Validierung: erkennt eine "blinde"
  Cluster-Analyse (z. B. PCA/t-SNE + Clustering in Notebook 03) die latente
  DN-Struktur korrekt wieder? (Erik-Idee, als festes Element fuer Phase 3.2
  EDA vorgemerkt)

### Bekannte Limitationen / offene Annahmen (Quelle/Annahme-Transparenz)
- Wellgeometrie-Sollformeln (Wellhoehe/-teilung proportional zu DN):
  unbelegte Annahme, wellrohrspezifische Literatur nicht frei verfuegbar
  (dokumentiert bereits bei Recherche-Phase)
- Fehlermechanismen (Bindenaehte-, Blasenbildungs-, Riss-Schwellenwerte):
  plausibilisierte Annahmen, keine literaturbelegten Schwellenwerte
- Datengenerierung stellt EINE mögliche Realisierung der Mini-Physik dar;
  systematische Sensitivitätsanalyse der Kalibrierungskonstanten steht
  noch aus (moeglicher spaeterer Analyseschritt)
- SOTA-Einordnung fuer dieses Notebook nicht anwendbar (siehe Projektanweisung:
  SOTA = Methodik + interner Noise-Floor, kein externer Datensatz-Benchmark)

### Naechster Schritt
Notebook 03: EDA fuer Modell A, "blind" durchgefuehrt (kein Vorwissen ueber
den Generator vorausgesetzt). Latente Referenzgroessen dienen im Anschluss
als Ground-Truth-Validierung der gefundenen Clusterstruktur.

---

## Notebook [Modell B – wird ergaenzt, sobald Datengenerierung fuer Modell B beginnt]
