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

### Root-Cause-Korrektur (nachtraeglich, vor Beginn der EDA)
Waehrend der Vorbereitung von Notebook 03 wurde die Plausibilitaet des
Merkmals "Vakuumniveau" hinterfragt (Werte um -400 mbar). Recherche ergab:
Vakuum wird bei Wellrohr-Corrugatoren nur bei Nennweiten > 200mm eingesetzt;
bei kleineren Nennweiten erfolgt die Ausformung ueber Formluft/Ueberdruck
(Quelle: Wikipedia "Corrugator (Kunststoffverarbeitung)", DeWiki "Corrugator").
Der urspruengliche Datensatz deckte ausschliesslich DN 50-200mm ab - also
den Formluft-Bereich - wurde aber durchgaengig mit Vakuum-Logik modelliert.

Korrekturmassnahmen (Notebook 02 zurueckverfolgt und angepasst):
- DN-Verteilung um Nennweiten > 200mm erweitert (DN250: 5%, DN315: 3%),
  damit beide Mechanismen im Datensatz tatsaechlich vorkommen
- Merkmal umbenannt/aufgeteilt: `vakuumniveau` -> `kalibrierdruck_mbar`
  (Vorzeichen kodiert Mechanismus) + neue kategoriale Spalte
  `kalibriermechanismus` (Formluft/Vakuum), strukturell aus DN abgeleitet
  (nicht zufaellig)
- Alle abhaengigen Formeln (Ausformungsgrad, Aussendurchmesser-/
  Ovalitaets-Streuung) von `vac_norm` auf mechanismus-unabhaengiges
  `druck_norm` umgestellt
- Parametertabellen (00/01) konsistent korrigiert, inkl. Quellenangabe
- Ergebnis nach Korrektur: 92.3% Formluft-Mechanismus, 7.7% Vakuum-
  Mechanismus - Verteilung entspricht der ueberwiegend kleineren/mittleren
  Nennweiten im urspruenglichen Produktspektrum

Konkrete mbar-Zahlenwerte bleiben fuer beide Mechanismen unbelegte Annahmen
(keine oeffentliche Quelle mit Zahlenwerten gefunden) - nur der MECHANISMUS
(Vorzeichen/Schwelle bei DN200) ist jetzt quellenbasiert, nicht die Betraege.
Dies illustriert das Prinzip "an der Quelle korrigieren, nicht nur an der
Oberflaeche kommentieren".

### Zweite Root-Cause-Korrektur (waehrend EDA, Notebook 03 Zelle 08b/8c)
Waehrend der bivariaten EDA-Analyse (Korrelationsmatrix, Vertiefung
abzugsgeschwindigkeit vs. kalibrierdruck_mbar) fiel eine unerwartete negative
Korrelation innerhalb der Vakuum-Teilgruppe auf. Ursache: abzugsgeschwindigkeit
war bei DN315 zu 100% an der oberen Clip-Grenze (15 m/min) gesaettigt
(Range-Restriktion/Deckeneffekt), da die zugrunde liegende Formel
(quadratisch in DN ueber querschnitt_proxy) nur fuer den urspruenglichen
Bereich DN<=200 kalibriert war und bei der DN-Erweiterung (erste Korrektur,
siehe oben) nicht mitkalibriert wurde.

Daraufhin systematischer Check ALLER DN-abhaengigen Formeln in Notebook 02
(nicht nur des gemeldeten Einzelfalls) durchgefuehrt. Ergebnis: zwei weitere,
bis dahin unentdeckte Faelle mit Vollsaettigung bei DN>200 gefunden:
- wandstaerke_ideal: 72.2% Clipping bei DN>200 (kritisch, da diese latente
  Groesse praktisch alle nachgelagerten Merkmale beeinflusst)
- massedurchsatz: 100% Clipping bei DN>200

Korrekturmassnahme: alle drei Formeln (wandstaerke_ideal, massedurchsatz,
abzugsgeschwindigkeit) von quadratischer auf lineare DN-Abhaengigkeit
umgestellt und fuer den vollen Bereich (DN 50-315) neu kalibriert.
querschnitt_proxy dadurch obsolet, entfernt. Ergebnis nach Korrektur:
0% Clipping bei allen drei Formeln, auch innerhalb der DN>200-Teilmenge.
Notebook 02 (Zellen 02-08b) vollstaendig neu durchlaufen.

**Methodische Lehre:** Eine nachtraegliche Erweiterung des Wertebereichs
einer latenten Variable (hier: DN-Verteilung) erfordert eine systematische
Neuvalidierung ALLER davon abhaengigen Formeln, nicht nur der Formel, bei
der ein Problem zuerst auffiel. Ein einzelner behobener Fall ist kein
Beleg dafuer, dass keine weiteren aehnlich gelagerten Faelle existieren.

### Naechster Schritt
Notebook 03: EDA fuer Modell A, "blind" durchgefuehrt (kein Vorwissen ueber
den Generator vorausgesetzt). Latente Referenzgroessen dienen im Anschluss
als Ground-Truth-Validierung der gefundenen Clusterstruktur. WICHTIG: bereits
durchgefuehrte EDA-Zellen (Struktur-Check, Kruskal-Wallis, Korrelationsmatrix)
basierten auf dem VOR der zweiten Korrektur generierten Datensatz und muessen
mit dem korrigierten Datensatz erneut ausgefuehrt werden, bevor die
EDA-Ergebnisse als belastbar gelten.

---

## Nachtrag (nach Abschluss EDA Modell A): Kritische Reflexion Zielsetzung
## + theoretischer Noise-Floor

Nach Abschluss der urspruenglichen EDA (Notebook 03) wurde die Zielgroessen-
Definition von Modell A (binaeres io_nio) kritisch hinterfragt: welches
Problem soll Modell A tatsaechlich loesen, und ist eine binaere Aggregation
aus 8 unabhaengigen Kriterien die beste Loesung dafuer?

**Zentrales quantitatives Ergebnis - theoretischer Noise-Floor (Monte-Carlo-
Simulation, n=2000 Wiederholungen je Zeile, Prozessparameter X_A fixiert):**

| Kennzahl | Wert |
|---|---|
| Bayes-optimale Accuracy | 78.0% |
| Bayes-optimales F1 (Standardschwelle 0.5) | 0.227 |
| Bayes-optimales F1 (bester Schwellenwert 0.22) | 0.447 |
| Referenz: erwartetes F1 bei reinem Zufallsraten | 0.343 |
| Anteil Zeilen im "unsicheren Bereich" (P(NIO) 10-90%) | 92.7% |

**Bedeutung:** F1=0.447 ist die harte Obergrenze fuer JEDES Modell auf
dieser Datengrundlage - auch bei perfektem Training. Das liegt spuerbar,
aber nicht dramatisch ueber reinem Zufallsraten (0.343). Ein spaeteres
Modellergebnis nahe F1=0.40-0.45 ist demnach sehr gut einzuordnen, nicht
enttaeuschend; deutlich hoehere Werte waeren ein Alarmsignal (Data Leakage).

**Empirischer Beleg fuer Informationsverlust durch binaere Aggregation:**
15.3% der NIO-Faelle im Datensatz haben 2 oder mehr gleichzeitig erfuellte
NIO-Kriterien (z. B. Ovalitaet UND Bindenaehte) - diese Information geht
durch die aktuelle binaere io_nio-Zielgroesse vollstaendig verloren.

**Konsequenz - drei parallele Zielgroessen-Varianten fuer Modell A ab
Notebook 05/06:**
1. Variante 1 (bisherig): binaere Klassifikation io_nio
2. Variante 2 (neu): Regression auf kontinuierlichen, normierten
   Sicherheitsabstand zur kritischsten Toleranzgrenze (Korrelation -0.604
   zum binaeren Label - bestaetigt zusaetzlichen Informationsgehalt)
3. Variante 3 (neu): Multi-Label-Klassifikation der 8 Einzelkriterien als
   Vektor (nicht CNN - tabellarische Daten ohne raeumliche Struktur;
   MultiOutputClassifier/ClassifierChain oder MLP mit mehreren
   Sigmoid-Ausgaengen als passende Verfahren)

Gespeichert: `data/processed/model_a_zielgroessen_varianten.csv`,
`reports/tables/03_eda_bayes_noise_floor.csv`,
`reports/tables/03_eda_nio_kriterien_kombinationen.csv`.

**Blocker-Uebersicht (vollstaendig, inkl. Einordnung "aenderbar vs. gewollt"):**

| Blocker | Art | Status |
|---|---|---|
| Zusammengesetzte Zielgroesse (ODER-Verknuepfung) | Design-Entscheidung | Wird durch Zielgroessen-Varianten 2/3 adressiert |
| PC1 (Nennweite) traegt kein NIO-Signal | Struktureigenschaft | Erklaert schwache Silhouette-Trennbarkeit (0.037), kein Fehler |
| Fehlende DN-relative Abweichungsfeatures | Feature-Engineering-Luecke | Wird in Notebook 04 behoben |
| Wenige Faelle fuer seltene Einzelfehler (z. B. Bindenaehte: 2-7 Faelle) | Informationsgrenze | Nicht durch Analyse loesbar, nur durch mehr Daten |
| Rauschen nahe an Toleranzschwellen (~2 Sigma) | Kalibrierungsentscheidung | Bewusst dokumentiert, keine rueckwirkende Aenderung |

Naechster Schritt bleibt Notebook 04 (Preprocessing Modell A), jetzt um die
Zielgroessen-Varianten und DN-relative Feature-Konstruktion erweitert.

---

## Nachtrag 2: Korrektur Data-Leakage-Risiko in der EDA (X_A/Y_A-Vermischung)

Nach kritischer Rueckfrage (User: "muessen wir nicht verstehen, was wir
tatsaechlich ins Modell schicken?") wurde festgestellt, dass die
urspruengliche EDA-Analysevariable `numerische_cols` X_A-Prozessparameter
mit Y_A-Qualitaetsmesswerten vermischte. Da io_nio direkt per Schwellenwert
aus den Y_A-Merkmalen (wandstaerke_ist, ovalitaet, aussendurchmesser_ist,
wellhoehe_ist/wellteilung_ist) berechnet wird, fuehrte deren Einbeziehung
als "Praediktoren" zu einem naeherungsweise tautologischen, kuenstlich
optimistischen Bild der Trennbarkeit.

**Korrigierte Ergebnisse (nur X_A_MERKMALE, 9 echte Prozessparameter,
die tatsaechlich VOR der Fertigung bekannt sind):**

| Kennzahl | Mit Y_A vermischt (fehlerhaft) | Nur X_A (korrekt) |
|---|---|---|
| Kruskal-Wallis signifikant | 10 von 14 | 5 von 9 |
| Silhouette-Score IO/NIO | 0.037 | 0.017 |
| PC1-Varianzanteil | 58.4% | 48.0% |
| PC1 <-> latente DN (Ground Truth) | r=0.993 | r=0.984 |

**Einordnung:** Die grundlegende Datenstruktur (PC1=Nennweitenfaktor)
bleibt stabil und wird weiterhin korrekt erkannt, unabhaengig von der
Korrektur. Die tatsaechliche IO/NIO-Trennbarkeit aus reinen
Prozesseinstellungen ist schwaecher als das urspruengliche, leicht
verzerrte Bild suggerierte - konsistent mit dem unabhaengig berechneten
Bayes-Noise-Floor (F1=0.447, Zelle 14), der von Anfang an korrekt nur
auf X_A-Groessen basierte und dadurch als verlaesslichste bisherige
Referenzgroesse gilt.

**Aktualisierte Referenzvariable fuer Notebook 04:** X_A_MERKMALE (9
Spalten: schneckendrehzahl, massedurchsatz, massetemperatur, massedruck,
duesenspalt, abzugsgeschwindigkeit, kalibrierdruck_mbar,
kuehlwassertemperatur, mfr_charge). Y_A-Qualitaetsmesswerte duerfen NICHT
als Modell-Input fuer die Kernaufgabe (Qualitaet vor Fertigung vorhersagen)
verwendet werden - nur zur Zielgroessen-Konstruktion.

---

## Nachtrag 3: wandtyp fehlte in X_A_MERKMALE (Notebook 04, waehrend Delamination-Behandlung entdeckt)

Bei der Delamination-Sonderbehandlung (Notebook 04) wurde festgestellt,
dass `wandtyp` nicht in X_A_MERKMALE (Nachtrag 2, Zelle 18) enthalten war,
obwohl es ein vor der Fertigung bekanntes Auftragsmerkmal ist und direkt
bestimmt, welche Fehlermechanismen ueberhaupt moeglich sind (Delamination
nur bei doppelwandig). Die X_A-only-EDA (Nachtrag 2) war dadurch selbst
unvollstaendig.

**Korrekturmassnahmen:**
- X_A_MERKMALE auf 10 Merkmale erweitert (Notebook 03 Zelle 22, Notebook 04)
- Kategoriale Ergaenzungsanalyse nachgeholt (Cramer's V statt Kruskal-
  Wallis, da wandtyp kategorial ist): wandtyp vs. io_nio zeigt KEINEN
  signifikanten Zusammenhang (Chi2 p=0.343, Cramer's V=0.036 - praktisch
  kein Effekt). Erwartungskonform: wandtyp beeinflusst in der
  Generierungslogik nur den seltenen Delamination-Mechanismus (6 Faelle
  gesamt), alle anderen 7 NIO-Kriterien sind unabhaengig von wandtyp.
- Parametertabellen (00_parameter_kandidatenliste.csv,
  01_parameter_final.csv) korrigiert: XB005 (wandtyp) Modell-Feld von "B"
  auf "beide" geaendert.

**Wichtige Klarstellung zur Projektarchitektur:** Die Parametertabellen
(00/01) sind KEIN per Code generiertes/reproduzierbares Artefakt, sondern
einmalig manuell erstelltes Planungsdokument - ihre Korrektur beeinflusst
nicht die Reproduzierbarkeit der eigentlichen Datenpipeline (Notebook 02).
`wandtyp` war in der Datengenerierung (Notebook 02, Zelle 05b) von Anfang
an korrekt enthalten - das Luecke betraf ausschliesslich die
Analyse-Referenzliste X_A_MERKMALE in Notebook 03.

### Zusaetzlich (Notebook 04): Imputations- und Delamination-Entscheidungen

**Imputation MCAR-Spalten (kuehlwassertemperatur, mfr_charge):**
Median-Imputation getestet und verworfen (erzeugt kuenstlichen
Verteilungs-Spike, groesserer Std-Abweichungsverlust: -2.3%/-2.0%).
KNN-Imputation (n_neighbors=5) gewaehlt: naeher am Original in Std-
Abweichung (-2.0%/-0.7%), nutzt Korrelationsstruktur zu anderen
X_A-Merkmalen (z. B. mfr_charge<->massedruck, r=-0.74). WICHTIG fuer
Notebook 05/06: KNNImputer muss dort nur auf Trainingsdaten gefittet
werden (Data-Leakage-Vermeidung).

**Delamination-Sonderbehandlung (MNAR):** Kein Fake-Kategorie-Ansatz
("nicht_anwendbar" als drittes Klassifikationslabel verworfen - waere
fuer ein Modell nur ein beliebiges drittes Label, wuerde bei naiver
Nutzung als 3-Klassen-Ziel triviale Scheingenauigkeit erzeugen, da
nicht_anwendbar quasi perfekt aus wandtyp ableitbar ist). Stattdessen:
maskierter Ansatz - delamination bleibt binaer mit echten NaN,
zusaetzliche Spalte delamination_anwendbar (0/1) fuer spaeteres
maskiertes Training/Auswertung dieses spezifischen Labels (Standardtechnik
bei partiell anwendbaren Multi-Label-Zielen).

Naechster Schritt: DN-relative Abweichungsfeatures konstruieren (muss ueber
einen aus X_A ableitbaren Proxy erfolgen, nicht ueber die latente DN direkt
- sonst neues Leck).

---

## Notebook 04 – Preprocessing Modell A (Fortsetzung: Feature Engineering,
## Encoding, Skalierungs-/Transformations-Vorpruefung)

### DN-Proxy und Residual-Features (Blocker-C-Hypothesentest)

DN-Proxy berechnet als PC1 einer PCA ausschliesslich ueber die 9
numerischen X_A_MERKMALE (kein Zugriff auf die latente rohr_dn_latent -
Leakage-frei). Erklaert 48.2% Varianz. Fuer jedes Merkmal per lineare
Regression auf den DN-Proxy der baugroessenerklaerte Anteil (R²) bestimmt:

| Gruppe | Merkmale | R² | Einordnung |
|---|---|---|---|
| Stark baugroessengetrieben | massedurchsatz (0.970), abzugsgeschwindigkeit (0.952), schneckendrehzahl (0.913), duesenspalt (0.886), kalibrierdruck_mbar (0.574) | >0.5 | Residuum liefert neue, baugroessenunabhaengige Information |
| Baugroessenunabhaengig | massetemperatur (0.000), kuehlwassertemperatur (0.005), mfr_charge (0.013), massedruck (0.028) | <0.05 | Residuum ≈ Original, redundant |

9 Residual-Features (`<merkmal>_dn_bereinigt`) erzeugt.

**Validierung der Blocker-C-Hypothese:** Kruskal-Wallis auf Residual-
Features: 4 von 9 signifikant (vs. 5 von 9 bei Original-X_A). Silhouette-
Score: 0.0152 (vs. 0.017 Original) - praktisch unveraendert. **Hypothese
bestaetigt sich in dieser einfachen linearen Form NICHT** - kein
dramatischer Trennbarkeitsgewinn durch DN-Bereinigung. Interessante
Verschiebung im Detail: bei massedurchsatz/abzugsgeschwindigkeit (R²>0.95)
verschwindet die Signifikanz nach Bereinigung (ihr urspruenglicher
IO/NIO-Zusammenhang kam ueberwiegend ueber die Baugroesse selbst zustande);
massedruck wird dagegen neu signifikant (vorher durch Rauschen/
Baugroesseneffekt ueberdeckt). Residual-Features werden ZUSAETZLICH zu
Original-Werten fuer den spaeteren Ablationsvergleich (Notebook 05/06)
mitgefuehrt, nicht als Ersatz. Vermutung: die Zielgroessen-Varianten
(kontinuierlicher Abstand, Multi-Label) sind der wirksamere Hebel als
reine Feature-Bereinigung, konsistent mit dem strukturellen Bayes-
Noise-Floor (F1=0.447).

### Encoding kategorialer Merkmale

One-Hot-Encoding fuer wandtyp (2 Kategorien) und kalibriermechanismus
(2 Kategorien) - kein Leakage-Risiko, da Kategorienliste endlich/bekannt
ist (im Gegensatz zu Skalierungsstatistiken).

### Skalierung (Vorschau) und Yeo-Johnson-Transformation (Vorpruefung)

Skalierungs-Vorschau (StandardScaler) bestaetigt korrekte
Vereinheitlichung sehr unterschiedlicher Wertebereiche (Mean~0, Std~1).
Finale Skalierung erfolgt leakage-sicher in der Pipeline (Notebook 05/06,
fit nur auf Trainingsdaten).

Yeo-Johnson-Transformation explorativ getestet (Frage: hilft eine
verteilungsform-veraendernde Transformation gegen die in Notebook 03
festgestellte Nicht-Normalverteilung der meisten X_A-Merkmale?).
**Ergebnis: kaum Wirkung** - 7 von 9 Merkmalen bleiben signifikant
nicht-normal (Shapiro-Wilk p<0.05) vor UND nach Transformation.
Nur massetemperatur und mfr_charge waren schon vorher normalverteilt
und blieben es. kuehlwassertemperatur komplett unveraendert (p=0.0001
in beiden Faellen, vermutlich Clipping-Randeffekt statt Schiefe).

**Ursachenanalyse:** Yeo-Johnson korrigiert Schiefe einer eingipfligen
Verteilung, kann aber Multimodalitaet (mehrere ueberlagerte Baugroessen-
Teilpopulationen, siehe DN-Analyse oben) nicht beheben - eine monotone
Transformation einer Variable kann eine Mischung mehrerer Teilpopulationen
nicht in eine einzelne Glockenkurve ueberfuehren. Bestaetigt indirekt,
dass der DN-Residualisierungsansatz methodisch die richtigere
Herangehensweise war, auch wenn er die Trennbarkeit nicht dramatisch
verbesserte. Yeo-Johnson wird NICHT in die finale Pipeline aufgenommen
(kein belegter Nutzen). Falls lineare Modelle im spaeteren Modellvergleich
mitgefuehrt werden, sollten sie eher auf DN-residualisierten Features
trainiert werden als auf Yeo-Johnson-transformierten Rohwerten.

Naechster Schritt: Zielgroessen-Varianten integrieren, finale
sklearn.Pipeline aufbauen, Preprocessing-Validierungs-EDA.

---

## Nachtrag 4: Fehlendes Delamination-Kriterium im Multi-Label-Target
## + Imputationsgrenzen bei Ausreisserwerten (Notebook 03/04, waehrend
## Preprocessing-Validierung entdeckt)

Bei der Preprocessing-Validierungs-EDA (Notebook 04, Zelle 10) wurde
geprueft, ob Variante 3 (Multi-Label) und Variante 1 (binaer) konsistent
zueinander sind. Ergebnis: nur 99.0% Uebereinstimmung, 7 abweichende
Zeilen.

**Ursache 1 (Hauptursache):** y_multilabel (Notebook 03, Zelle 16)
enthielt nur 8 statt 9 Kriterien - delamination fehlte als eigenstaendige
Spalte, obwohl es in der urspruenglichen io_nio-Logik (Notebook 02,
Zelle 06) das neunte gleichberechtigte ODER-Kriterium ist. Korrektur:
y_nio_delamination als 9. Spalte ergaenzt. Reduzierte die Abweichungen
von 7 auf 2 Zeilen.

**Ursache 2 (Restdiskrepanz, 2 Zeilen):** aussendurchmesser_ist enthaelt
MCAR-Luecken (Notebook 02, Realismus-Luecken). Ein NaN-Vergleich (z.B.
">1.2") wertet in Pandas automatisch als False - das Kriterium nio_od
wuerde bei fehlenden Werten faelschlich nie ausloesen. Fuer die
Zielgroessen-Rekonstruktion wurden die benoetigten Y_A-Spalten
(wandstaerke_ist, aussendurchmesser_ist, ovalitaet, wellhoehe_ist,
wellteilung_ist) daher per KNN imputiert (nur fuer diesen Zweck, data/raw
bleibt unveraendert).

**Wichtige methodische Erkenntnis - Imputation kann Ausreisser nicht
rekonstruieren:** Diagnose der verbliebenen 2 Zeilen zeigte, dass die
imputierten OD-Werte NICHT nahe der Toleranzgrenze lagen (Abstand 0.82mm
bzw. 1.04mm zur 1.2mm-Schwelle) - urspruengliche Vermutung "Grenzfall"
war falsch. Tatsaechliche Ursache: die echten (geloeschten) Original-
werte waren offenbar statistische Ausreisser, die deutlich ueber der
Toleranz lagen. KNN-Imputation schaetzt einen plausiblen/typischen Wert
("was normalerweise zu erwarten waere"), kann aber einen individuellen
Zufalls-Ausreisser grundsaetzlich nicht treffen - eine inhaerente Grenze
jeder Imputationsmethode (verwandt mit "Regression zur Mitte"), kein
Konstruktionsfehler.

**Entscheidung zu Loeschen vs. Behalten:** beide betroffenen Zeilen NICHT
geloescht - ihr binaeres io_nio-Label bleibt korrekt (auf den
vollstaendigen Originalwerten vor Luecken-Einfuegung berechnet), nur die
davon abgeleiteten Zielgroessen-Varianten 2/3 sind fuer die OD-Komponente
unscharf. Stattdessen: gezielte Maskierung statt Datenverlust - neue
Spalte y_od_komponente_zuverlaessig (0/1), grundsaetzlich fuer ALLE 32
Zeilen mit imputiertem aussendurchmesser_ist gesetzt (nicht nur die 2
sichtbar abweichenden - bei den uebrigen 30 ist unbekannt, ob die
Imputation zufaellig korrekt lag; Maskierung erfolgt daher prinzipiell,
nicht ergebnisbasiert). Analog zum bereits etablierten
delamination_anwendbar-Muster.

**Finales Ergebnis:** Konsistenz Multi-Label vs. binaer: 99.7% (2 von 700
Zeilen dokumentierte Restungenauigkeit, ueber Flag fuer spaeteres
maskiertes Training/Auswertung identifizierbar).

Naechster Schritt: sklearn.Pipeline-Grundgerueст in src/preprocessing.py
(Option C: Auswahlfunktion fuer Feature-Set x Zielgroessen-Variante),
Preprocessing-Validierungs-EDA-Nachtrag, Abschluss-Markdown Notebook 04.

---

## Notebook 05 – Modelltraining Modell A (AP 3.4)

### Vorbereitung: DNResidualizer (leakage-sicherer Custom-Transformer)

Kritische Nachbesserung vor Trainingsstart: die in Notebook 04 gespeicherten
*_dn_bereinigt-Spalten wurden auf dem GESAMTEN Datensatz berechnet (PCA +
9 Regressionen) - fuer explorative EDA zulaessig, aber Data Leakage bei
Verwendung im Modelltraining. Loesung: DNResidualizer als eigener
sklearn-Transformer (BaseEstimator, TransformerMixin) in src/preprocessing.py,
lernt PCA-Achse und Regressionen ausschliesslich in fit() - bei Nutzung
innerhalb einer sklearn.Pipeline automatisch nur auf dem jeweiligen
Trainings-Fold, strukturell leakage-sicher ohne manuellen Eingriff.

FEATURE_SETS auf 4 Varianten erweitert (original, original_no_kategorial,
residual, combined) - original_no_kategorial ergaenzt, um den
eigenstaendigen Beitrag von wandtyp/kalibriermechanismus zu pruefen
(Cramer's V aus Notebook 03 deutete auf geringen Effekt hin).

### Ablationsstudie: 4 Feature-Sets x Modelle x 3 Zielgroessen-Varianten

Modellkatalog (nach kritischer Diskussion erweitert, inkl. bewusst
"ungeeigneter" Kandidaten als Negativ-Beleg):
- Binaer (9 Modelle): LogisticRegression, kNN, SVC, RandomForest,
  HistGradientBoosting, XGBoost, LightGBM, GaussianNB, MLP
- Kontinuierlich (8 Modelle): Ridge, kNN, SVR, RandomForest,
  HistGradientBoosting, XGBoost, LightGBM, MLP
- Multi-Label (9 Modelle, via MultiOutputClassifier): analog binaer

Gesamt: 104 Kombinationen, gemeinsamer 5-Fold-StratifiedKFold-Split
(stratifiziert auf io_nio) fuer alle Kombinationen wiederverwendet -
sichert Vergleichbarkeit ueber alle drei Zielgroessen-Varianten hinweg.
Bei "continuous" werden die durch y_od_komponente_zuverlaessig maskierten
Zeilen pro Fold ausgeschlossen.

**Ergebnis erster Durchlauf:** 100/104 erfolgreich. 4 Fehlschlaege isoliert
auf XGBoost + binaere Zielgroesse: XGBoost akzeptiert bei binaerer
Klassifikation keine String-Labels ("IO"/"NIO"), erwartet numerisch
kodierte Klassen (0/1) - andere sklearn-kompatible Modelle kodieren dies
intern automatisch, XGBoost nicht. Behoben durch lokale Label-Kodierung
nur fuer diesen Modell/Zielgroessen-Fall, Vorhersage wird vor der
Metrik-Berechnung zurueckuebersetzt, damit alle Metrik-Funktionen
weiterhin einheitlich mit "IO"/"NIO"-Strings arbeiten. Nach Korrektur:
104/104 erfolgreich.

**Robustheitsmassnahmen bei grossen Ablationsstudien:** Try/Except je
Einzelkombination (Fehler stoppen nicht die Gesamtschleife, werden als
Status "fehlgeschlagen" mit Fehlermeldung dokumentiert) + Zwischen-
speicherung nach jeder Kombination (kein Datenverlust bei Abbruch).
Rechenzeit je Fit protokolliert (fit_time_sekunden) fuer spaeteren
Aufwand-Nutzen-Vergleich.

**Gemeinsame Rueckfall-Metrik (f1_rueckuebersetzt):** Da binaere,
kontinuierliche und Multi-Label-Zielgroessen native, nicht direkt
vergleichbare Metriken nutzen (F1 vs. RMSE/R² vs. Macro-F1), wird
zusaetzlich jede Vorhersage in ein binaeres IO/NIO zurueckuebersetzt
(kontinuierlich: Schwellenwert 0 am Sicherheitsabstand; Multi-Label:
irgendein Label=1) und dort F1 gegen denselben Bayes-Noise-Floor (0.447)
gemessen - schafft eine faire, gemeinsame Vergleichsbasis ueber alle drei
Zielgroessen-Varianten.

Gespeichert: reports/tables/05_ablation_results.csv (104 Zeilen).

Naechster Schritt: erneuter Durchlauf mit zusaetzlicher Train-Score-
Messung (Train-CV-Gap als Overfitting-Diagnose), dann Ergebnisanalyse
(Effekt Feature-Set, Modelltyp, Zielgroessen-Variante; Naive-Bayes-
Vergleich als Negativ-Beleg; Einordnung gegen Bayes-Noise-Floor).

---

## Notebook [Modell B – wird ergaenzt, sobald Datengenerierung fuer Modell B beginnt]
