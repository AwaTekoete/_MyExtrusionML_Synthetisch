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

### Hyperparameter-Kalibrierung (Abgrenzung zu Tuning, AP 3.6)

Nach der ersten vollstaendigen Ablationsschleife (104/104 erfolgreich)
zeigte die Train-CV-Gap-Messung bei allen vier Baummodellen (RandomForest,
HistGradientBoosting, XGBoost, LightGBM) train_f1≈1.0 bei binaerer
Zielgroesse - vollstaendiges Auswendiglernen der Trainingsdaten, macht den
Gap-Vergleich zwischen diesen Modellen uninformativ.

**Wichtige methodische Abgrenzung:** Einzelne, offensichtlich degenerierte
Standardwerte fuer die gegebene Datenmenge (n=560/448 pro Fold) zu
korrigieren ist KEIN Hyperparameter-Tuning (systematische Suche nach dem
besten Wert, vorgesehen fuer AP 3.6), sondern Vermeidung eines Artefakts,
das jeden sinnvollen Modellvergleich verzerren wuerde.

**Korrekturschritte (zwei Iterationen, jeweils mit Zelle-7-Check
verifiziert, nicht blind uebernommen):**
- Iteration 1 (nur Baumtiefe begrenzt: max_depth=8 RandomForest, max_depth=6
  Boosting-Verfahren): RandomForest deutlich verbessert (train_f1 1.0->0.63-0.72),
  Boosting-Verfahren kaum veraendert (train_f1 weiterhin ~0.99-1.00) -
  Baumtiefe allein reicht bei Boosting-Ensembles mit vielen (200)
  aufeinanderfolgenden Baeumen nicht aus.
- Iteration 2 (Ensemble-Kapazitaet direkt adressiert): n_estimators 200->50,
  zusaetzlich subsample=0.8, colsample_bytree=0.8 (Zeilen-/Spalten-
  Subsampling je Baum), min_samples_leaf/min_child_samples erhoeht,
  L2-Regularisierung (reg_lambda=2.0 XGBoost, l2_regularization=1.0
  HistGradientBoosting). Ergebnis: train_f1 sank auf 0.47-0.72 bei allen
  vier Baummodellen, Gap von ~0.75 auf 0.27-0.53 reduziert.

**Bewusster Stopp-Punkt:** verbleibender Gap (0.27-0.53) als plausibel
akzeptiert angesichts n≈448 und dem bekannten Bayes-Noise-Floor (F1=0.447) -
ein gewisser Train-Val-Unterschied ist bei dieser Datenmenge normal.
Weiteres iteratives Nachjustieren wuerde die Grenze zu echtem Tuning
ueberschreiten - bewusst hier gestoppt, verbleibende Optimierung bleibt
AP 3.6 vorbehalten.

### Fairness-Korrektur: Skalierung kategorialer Merkmale

Vor der Ergebnisanalyse festgestellt: kategoriale Dummy-Spalten
(wandtyp_einwandig, mechanismus_Vakuum) wurden nicht durch StandardScaler
skaliert (Std 0.27-0.45), waehrend alle numerischen Merkmale auf Std≈1.0
gebracht wurden. Betrifft distanz-/regularisierungsempfindliche Modelle
(kNN, SVM, MLP, LogReg/Ridge) - implizite Untergewichtung kategorialer
Merkmale. Korrigiert: kategoriale Spalten ebenfalls durch StandardScaler
geleitet. Ergebnis: kaum Einfluss auf die Top-Werte (GaussianNB blieb
Spitzenreiter), aber notwendig fuer methodische Fairness des Vergleichs.

### Root-Cause-Fix: kontinuierliche Zielgroesse unvollstaendig konstruiert

Erste Ergebnisanalyse zeigte eine grosse Ueberraschung: bestes
f1_rueckuebersetzt bei "continuous" lag bei nur 0.222 - schlechter als
die Zufalls-Baseline (0.343). Diagnose (Notebook 05, Zelle 11): der
Sicherheitsabstand (Notebook 03, Zelle 16) erfasste nur 4 der 9
NIO-Kriterien (Wandstaerke, Ovalitaet, Aussendurchmesser, Wellhoehe) -
die 5 binaeren Kriterien (Bindenaehte, Blasenbildung, Risse,
Oberflaechenfehler, Delamination) fehlten komplett in der kontinuierlichen
Groesse. Konsistenz mit dem binaeren io_nio-Label lag dadurch nur bei
91.7% (58 abweichende Zeilen, 48.3% davon durch oberflaechenfehler
verursacht - haeufigstes der fehlenden Kriterien).

**Fix:** binaere Kriterien wirken als harter Strafterm - trifft eines zu,
wird der Sicherheitsabstand auf einen stark negativen Wert (-1.0) gesetzt,
unabhaengig vom Wert der 4 kontinuierlichen Kriterien. Ergebnis: Konsistenz
auf 99.7% verbessert (identisch zur bereits akzeptierten Imputations-
Restungenauigkeit bei der OD-Komponente, keine neue Fehlerquelle mehr).
**Nach dem Fix: bestes f1_rueckuebersetzt bei continuous sprang von 0.222
auf 0.384** - von "schlechter als Zufall" zu "nahe am Bayes-Floor".
Bestaetigt: die vorherige schwache Performance war ein
Konstruktionsfehler der Zielgroesse, keine echte Eigenschaft der Daten.

### Ergebnisueberblick nach allen Korrekturen (104/104 Kombinationen)

| Zielgroesse | Bestes Modell (Feature-Set) | F1 (bzw. Rueckfall-F1) |
|---|---|---|
| binary | GaussianNB (original_no_kategorial) | 0.423 |
| multilabel | GaussianNB (original) | 0.413 |
| continuous | MLP (residual) | 0.384 |

Alle drei liegen nahe, aber unterhalb des Bayes-Floors (0.447) - konsistentes,
plausibles Gesamtbild. **Wichtige Ueberraschung:** GaussianNB (urspruenglich
als "ungeeignet" erwarteter Negativ-Beleg, da Unabhaengigkeitsannahme
zwischen stark korrelierten Merkmalen verletzt) gewinnt deutlich bei
binaer/multilabel, statistisch abgesichert (Abstand zum Zweitplatzierten
LightGBM: 0.204, kombinierte Std beider Modelle: 0.086 - Abstand >2x
combinierte Streuung, robuster Befund ueber alle 5 CV-Folds).
Interpretation: bei kleiner, stark verrauschter Datenmenge (n=560,
92.7% der Faelle im "unsicheren Bereich" laut Bayes-Analyse) kann ein
einfaches, wenig komplexes Modell komplexere Modelle schlagen, da es
weniger Kapazitaet hat, Rauschen mitzulernen. Muss als eigener,
gegenueber der urspruenglichen Erwartung korrigierter Befund in der
Studie dokumentiert werden.

Auffaellig zusaetzlich: original_no_kategorial schneidet bei binaer/
continuous oft gleich gut oder besser ab als Sets mit kategorialen
Merkmalen - konsistent mit dem fruehen Cramer's-V-Befund (wandtyp/
kalibriermechanismus kaum eigenstaendiger Effekt auf io_nio).

Naechster Schritt: Grafik 2 (Effekt Feature-Set), Grafik 3 (Effekt
Modelltyp), Grafik 4 (Train-CV-Gap vs. Validierungs-F1).

### Ergebnisanalyse: Grafiken 1-4 (Notebook 05, Zellen 13-16)

**Grafik 1 (F1-Vergleich je Modell, bestes Feature-Set):** bestaetigt
den Gesamtueberblick aus Zelle 8 - GaussianNB fuehrt bei binaer (0.423)
und multilabel (0.413), MLP bei continuous (0.384). Alle drei nahe, aber
unterhalb des Bayes-Floors (0.447).

**Grafik 2 (Effekt Feature-Set, Boxplot gepoolt ueber Modelle):** KEIN
Feature-Set schneidet systematisch besser ab als die anderen - Mediane
liegen bei allen drei Zielgroessen-Varianten nah beieinander. Bei binaer
zeigen original/residual breite Boxen mit Ausreissern nach oben
(GaussianNB), original_no_kategorial/combined schmalere Boxen ohne
Spitzenmodell. Bei continuous liegen alle vier eng um/knapp ueber der
Zufalls-Baseline. Bei multilabel liegen alle vier Mediane sehr niedrig,
mit durchgaengigem GaussianNB-Ausreisser nach oben unabhaengig vom
Feature-Set. Schlussfolgerung: Modellwahl dominiert deutlich staerker
als Feature-Set-Wahl - relativiert den DN-Residualisierungsaufwand
nochmals empirisch (kein Feature-Set-Sieger identifizierbar).

**Wichtige Klarstellung zur Boxplot-Interpretation:** die Boxplots zeigen
den TYPISCHEN (Median) von 9 Modellen, nicht die Bestleistung. Mehrere
schwache Modelle (v.a. SVC, MLP mit F1=0.000 bei binaer - sagen
durchgaengig nur die Mehrheitsklasse IO vorher) ziehen den Median unter
die Zufalls-Baseline, obwohl das beste Modell (GaussianNB) bereits
darueber liegt. Kein Widerspruch, sondern Hinweis auf ein separates
Problem: mehrere Modelle sind bei Klassenungleichgewicht (26% NIO) mit
Standard-Konfiguration nicht funktionsfaehig.

**Grafik 3 (Effekt Modelltyp, Boxplot gepoolt ueber Feature-Sets) +
Spannweiten-Tabelle (max-min je Modell):** MLP durchgaengig am
empfindlichsten gegenueber Feature-Set-Wahl (Spannweite binaer 0.295,
multilabel 0.190) - typisch fuer neuronale Netze. GaussianNB zeigt
gegensaetzliches Bild: bei binaer noch spuerbar schwankend (0.131),
bei multilabel praktisch feature-set-unabhaengig konstant (0.002) -
zusaetzliches Qualitaetsmerkmal (Robustheit) neben reiner F1-Hoehe.
LogisticRegression/SVC zeigen kleinste Spannweiten, aber "truegerische
Robustheit" (durchgaengig schlecht, nicht durchgaengig gut).

**Grafik 4 (Train-CV-Gap vs. Validierungs-F1, Overfitting-Diagnose):**
GaussianNB liegt bei binaer/multilabel konsequent im Idealbereich (hohe
Guete, minimaler Gap) - zusaetzliche Bestaetigung als vertrauenswuerdiger
Kandidat, nicht nur bestes F1 sondern auch am wenigsten Overfitting-
verdaechtig. Baumbasierte Modelle liegen in einem moderaten Band
(Gap 0.15-0.55 bei binaer) - Kalibrierung aus vorherigem Schritt zeigt
Wirkung, aber Trade-off bleibt sichtbar. MLP zeigt inkonsistentes
Verhalten (mal nahe Idealbereich, mal komplett bei F1≈0).

**Store44-Farbschema-Ausnahme (dokumentiert):** fuer Grafik 4 (9
gleichrangige, individuell zu unterscheidende Modelltypen) wurde bewusst
von der 3-Farben-Konvention abgewichen - eine erweiterte, aber weiterhin
dezente Palette macht die Modelle eindeutig unterscheidbar. Mit 3 Kern-
Akzentfarben waere bei 9 Kategorien zwangslaeufig Mehrfachbelegung und
Bedeutungsverlust entstanden. Fuer Praesentation/finale Dokumentation
gesondert zu vermerken.

Alle vier Grafiken UND die zugrunde liegenden Daten als CSV gespeichert
(reports/tables/05_ablation_*.csv) - ermoeglicht spaetere rechnerische
Nachanalyse ohne Grafik-Neuerstellung.

Naechster Schritt: Sane-Default-Kalibrierungszyklus Iteration 2
(class_weight="balanced" fuer Modelle mit Klassenungleichgewichts-
Problem), erneute Messung, Vorher-Nachher-Vergleich.

### Sane-Default-Kalibrierungszyklus Iteration 2: Klassenungleichgewicht

Grafiken 1-4 (Iteration 1) zeigten ein systematisches Problem: SVC und
LogisticRegression kollabierten bei binaerer/Multi-Label-Zielgroesse auf
reine Mehrheitsklassen-Vorhersage (F1=0.000) - bedingt durch das
Klassenungleichgewicht (26% NIO) ohne Klassengewichtung in den
Standard-Hyperparametern.

**Massnahme (Sane-Default, kein Tuning):** class_weight="balanced" (bzw.
scale_pos_weight bei XGBoost, berechnet aus dem tatsaechlichen Trainings-
Klassenverhaeltnis: 2.84) fuer alle Modelle ergaenzt, die den Parameter
unterstuetzen. MLP und GaussianNB/kNN bewusst unveraendert gelassen
(kein natives class_weight in sklearn verfuegbar - Resampling-Ansatz
haette die Grenze zu Tuning ueberschritten). Iteration 2 umfasste 72
Kombinationen (binaer + multilabel, continuous unveraendert da
Klassengewichtung fuer Regression nicht anwendbar).

**Vorher-Nachher-Ergebnis (Zelle 19):** SVC/LogisticRegression massiv
verbessert - binaer +0.35 bis +0.41 F1, multilabel sogar +0.40 bis +0.43
F1 (von komplettem Versagen zu Spitzengruppe). Auch baumbasierte Modelle
(bereits vorher funktionsfaehig) zeigten spuerbare Verbesserung
(+0.11 bis +0.34) - class_weight verbesserte generell die Recall/
Precision-Balance, nicht nur das Extremfall-Versagen.

**Wichtige Neueinordnung:** GaussianNB (unveraendert, kein class_weight)
ist nach dieser Korrektur NICHT mehr der alleinige Spitzenreiter -
SVC/LogisticRegression liegen nun in vergleichbarer Groessenordnung
(binaer: GaussianNB 0.423 vs. SVC ~0.41; multilabel: SVC 0.425 vor
LogisticRegression 0.425 vor GaussianNB 0.413). Ein wesentlicher Teil
des urspruenglichen GaussianNB-Vorsprungs (Notebook 05, erste
Ergebnisanalyse) lag an einem behebbaren Konfigurationsmangel der
Konkurrenzmodelle, nicht ausschliesslich an methodischer Eignung von
Naive Bayes fuer dieses Problem - wichtige Selbstkorrektur einer
vorschnellen Interpretation.

### Finale konsolidierte Ergebnisse (104 Kombinationen)

Finale Tabelle (reports/tables/05_ablation_results_final.csv) kombiniert:
binaer/multilabel aus Iteration 2 (v2_class_weight_balanced), continuous
aus Iteration 1 (v1_original_hyperparameter) - Spalte
kalibrierungs_version dokumentiert Herkunft je Zeile. Grafiken 1-4 mit
_final-Suffix erneut erzeugt.

**Finale Top-Ergebnisse:**

| Zielgroesse | Bestes Modell (Feature-Set) | F1 |
|---|---|---|
| binary | GaussianNB (original_no_kategorial) | 0.423 |
| continuous | MLP (residual) | 0.384 |
| multilabel | SVC (original_no_kategorial) | 0.425 |

**Feature-Set-Effekt (final, Grafik 2b):** weiterhin kein systematischer
Gewinner - Unterschiede maximal ~0.03 zwischen bestem/schlechtestem
Median je Zielgroesse. original_no_kategorial erweist sich als robuster
Standardkandidat (nie schlechtestes Set, geringste Dimensionalitaet).

**Modelltyp-Effekt (final, Grafik 3):** klare Trennung zwischen Modellen
MIT class_weight-Unterstuetzung (jetzt Spitzengruppe, eng beieinander)
und OHNE (kNN, MLP - bleiben klar abgeschlagen, einzige verbliebene
Schwachpunkte nach der Kalibrierung).

**Overfitting-Diagnose (final, Grafik 4/4b mit einheitlicher Skala):**
GaussianNB/LogisticRegression/SVC liegen konsequent im Idealbereich
(hohe Guete, minimaler Train-CV-Gap) - "billig gut". Boosting-Modelle
erreichen aehnliche/niedrigere Guete bei deutlich hoeherem Gap - "teuer
gut", weniger vertrauenswuerdig fuer echte Generalisierung. Wichtiges
Zusatzargument fuer einfache Modelle als Champion-Kandidaten, nicht nur
wegen der F1-Zahl sondern wegen nachgewiesener Robustheit. Einheitliche
Achsenskala (Grafik 4b) zeigte zusaetzlich: bei continuous ist die
Modell/Overfitting-Beziehung weniger klar geclustert als bei den beiden
Klassifikationsvarianten - kNN/SVR ueber die ganze Gap-Breite verteilt,
erreichen dabei nie Top-Werte.

Naechster Schritt: konsolidierte Zusammenfassung/Champion-Diskussion,
danach Uebergang zu AP 3.6 (systematisches Hyperparameter-Tuning).

### Champion-Kandidaten-Diskussion (Zellen 26-27)

Vollstaendige Kandidaten-Tabelle erstellt: alle bereits berechneten
quantitativen Metriken (F1, Precision, Recall, MCC, ROC-AUC, Train-CV-Gap,
Feature-Set-Spannweite, Fit-Zeit) kombiniert mit dokumentiertem
Fachwissen zu qualitativen Modelleigenschaften (Interpretierbarkeit,
Black-Box-Status, SHAP-Explainer-Typ) - relevant fuer die spaetere
SHAP-Integration im Streamlit-Demonstrator (AP 3.7, fest zugesagtes
Feature).

**Wichtiger methodischer Hinweis:** F1-Unterschiede zwischen den Top-
Kandidaten sind klein relativ zur Fold-zu-Fold-Streuung (Std typischerweise
0.03-0.09) - eine Rangfolge auf die dritte Nachkommastelle waere unseriös.
Bewertung erfolgte daher ueber mehrere Kriterien gemeinsam (Guete +
Robustheit + SHAP-Eignung), nicht allein ueber die hoechste F1-Zahl.

**Binaere Zielgroesse, vier engste Kandidaten im Detailvergleich:**

| Modell | F1 | Precision | Recall | MCC | Gap | Feature-Spannweite | SHAP |
|---|---|---|---|---|---|---|---|
| GaussianNB | 0.423 | 0.350 | 0.556 | 0.161 | 0.032 | 0.131 | approximativ |
| SVC | 0.410 | 0.338 | 0.520 | 0.144 | 0.142 | 0.018 | approximativ, langsam |
| LightGBM | 0.395 | 0.341 | 0.473 | 0.130 | 0.307 | 0.033 | exakt, schnell |
| LogisticRegression | 0.382 | 0.294 | 0.548 | 0.072 | 0.070 | 0.008 | exakt, schnell |

GaussianNB gewinnt konsistent bei F1, Precision, Recall UND MCC
gleichzeitig (kein Trade-off-Artefakt, echter Gesamtvorteil) bei
gleichzeitig sehr niedrigem Overfitting-Gap. LightGBM/HistGradientBoosting
erreichen aehnliche F1-Werte, aber mit deutlich hoeherem Gap (0.30-0.34) -
Guete teilweise durch Auswendiglernen erkauft, weniger vertrauenswuerdig
fuer echte Generalisierung.

**Finale Drei-Kandidaten-Shortlist (bewusst KEIN einzelner Champion,
Entscheidung vertagt auf AP 3.6/3.7):**
1. **GaussianNB** - mathematisch staerkster Kandidat (F1/Precision/Recall/
   MCC/Gap durchgaengig vorn), aber nur approximatives, langsameres SHAP
2. **LogisticRegression** - taktischer Kandidat: exaktes, schnelles SHAP
   (LinearExplainer), direkt interpretierbare Koeffizienten, sehr
   niedrigste Feature-Set-Spannweite (0.008) - Demo-Tauglichkeit als
   Hauptargument trotz etwas niedrigerer Guete
3. **SVC** - dritte Option: F1 knapp hinter GaussianNB, robustester
   Kandidat gegenueber Feature-Set-Wahl (Spannweite 0.018), aber
   ebenfalls nur approximatives und zusaetzlich langsames SHAP (Kernel-
   Explainer mit RBF-Kernel)

Begruendung fuer Shortlist statt Einzelentscheidung: die Guete-Unterschiede
liegen im Rauschbereich der CV-Streuung; die eigentliche Differenzierung
(SHAP-Geschwindigkeit in der Live-Demo) ist erst in AP 3.7 empirisch zu
pruefen, nicht vorab zu entscheiden.

Vollstaendige Tabelle: reports/tables/05_champion_kandidaten_komplett.csv

Naechster Schritt: Abschluss-Markdown Notebook 05, AP 3.4 formal
abgeschlossen. Shortlist (GaussianNB, LogisticRegression, SVC) geht in
AP 3.6 (Hyperparameter-Tuning) und AP 3.7 (Evaluation, SHAP) weiter.

---

## Notebook 06 – Hyperparameter-Tuning Modell A (AP 3.6)

### Vorbereitung: Empirische Zeitschaetzung vor Nested-CV-Schleife

Vor dem vollstaendigen Durchlauf wurde eine Pilot-Messung (ein Fit je
Kandidat) durchgefuehrt, um die Gesamtlaufzeit realistisch abzuschaetzen -
vermeidet ungeplant lange Rechenzeiten. Zwei Probleme dabei aufgedeckt
und behoben:

1. **Reihenfolge-Fehler:** Pipeline-Builder-Funktionen (baue_preprocessing_
   pipeline, DNResidualizer) wurden zunaechst NACH der Pilot-Messung
   definiert - erste Messung lief dadurch auf einer fehlerhaften, nicht
   skalierten Pipeline. Nach Umsortierung (Pipeline-Builder vor Pilot-
   Messung) korrigiert - wichtige Lehre: Notebooks muessen von oben nach
   unten ohne Vorgriffe ausfuehrbar sein.

2. **ConvergenceWarning bei LogisticRegression:** lbfgs-Solver konvergierte
   bei binaerer UND multilabel Zielgroesse nicht zuverlaessig (dominierte
   bei multilabel 80% der geschaetzten Gesamtlaufzeit: 2321 von 2861
   Sekunden). Ursache: mehrere der 9 Multi-Label-Kriterien sind extrem
   selten (Shannon-Entropie-Analyse, Notebook 03), kombiniert mit
   class_weight="balanced" wird lbfgs numerisch instabil. Behoben durch
   solver="liblinear" (robuster bei kleinen, unbalancierten Teilproblemen).
   Ergebnis: Gesamtlaufzeit-Schaetzung von 47.7 auf 7.6 Minuten reduziert.

### Nested-CV-Tuning (8 Kandidaten, 5 aeussere x 5 innere Folds)

Aeussere Folds identisch zu Notebook 05 reproduziert (gleicher SEED,
gleiche Methode) - stellt sicher, dass Vorher-Nachher-Vergleich (Default-
vs. getunte Hyperparameter) auf denselben Datenpartitionen erfolgt.
Feature-Set pro Modell auf das jeweils beste aus Notebook 05 fixiert
(keine erneute Feature-Set-Suche - diese Frage bereits in AP 3.4
datengetrieben beantwortet: kein systematischer Feature-Set-Effekt).

**Root-Cause-Korrektur waehrend der Durchfuehrung:** scoring fuer binaere
Zielgroesse war zunaechst "f1_macro" gesetzt - inkonsistent zur
bisherigen Hauptmetrik (NIO-spezifisches F1). Korrigiert auf
make_scorer(f1_score, pos_label="NIO") - die innere Grid-Search muss
dasselbe Ziel optimieren, das auch berichtet wird, sonst ist der
Vergleich nicht aussagekraeftig.

### Ergebnis: Vorher-Nachher-Vergleich (Default- vs. getunte Hyperparameter)

| Zielgroesse | Modell | Default | Getunt | Differenz |
|---|---|---|---|---|
| binary | GaussianNB | 0.423 | 0.420 | -0.003 |
| binary | LogisticRegression | 0.382 | 0.423 | **+0.041** |
| binary | SVC | 0.410 | 0.423 | +0.013 |
| multilabel | GaussianNB | 0.078 | 0.085 | +0.007 |
| multilabel | LogisticRegression | 0.115 | 0.088 | -0.027 |
| multilabel | SVC | 0.108 | 0.098 | -0.010 |
| continuous | Ridge | -0.001 | 0.016 | +0.017 |
| continuous | RandomForest | -0.030 | 0.022 | +0.052 |

**Binaer - wichtigstes Ergebnis:** Nach Tuning liegen alle drei Shortlist-
Kandidaten praktisch GLEICHAUF (0.420-0.423) - GaussianNB ist nicht mehr
klar fuehrend, LogisticRegression/SVC holen den vollen Rueckstand auf.
Staerkt die taktische Wahl von LogisticRegression zusaetzlich (schnelles,
exaktes SHAP bei nun gleichwertiger Guete). GaussianNB zeigt erwartungs-
gemaess kaum Veraenderung (-0.003) - nur eine sinnvolle Stellschraube
(var_smoothing) vorhanden, bestaetigt die Vermutung aus der Shortlist-
Diskussion empirisch.

**Multilabel - wichtiger Negativbefund, tiefergehend diagnostiziert:**
LogisticRegression/SVC verschlechtern sich nach Tuning. Diagnose (Best-
Params je der 5 aeusseren Folds) zeigt: KEINE konsistente "beste"
Hyperparameter-Wahl - C schwankt bei LogReg ueber drei Groessenordnungen
(0.01 bis 10.0) ohne Muster, SVC aehnlich instabil bei C und gamma.
**Schlussfolgerung:** die innere 5-Fold-Suche ist bei nur ~448
Trainingszeilen pro aeusserem Fold UND einem MultiOutputClassifier ueber
9 teils extrem seltene Labels zu instabil fuer eine robuste Hyperparameter-
Wahl - die Suche optimiert teilweise auf Zufallsrauschen einzelner innerer
Folds, nicht auf ein echtes, generalisierbares Signal. Kein Fehler in der
Implementierung, sondern eine Grenze des Tuning-Ansatzes bei dieser
Datenmenge/Label-Verteilung.

**Praktische Konsequenz:** Fuer multilabel werden die Sane-Default-Werte
aus Notebook 05 beibehalten (nicht die getunten) - dokumentierte,
begruendete Entscheidung gegen das eigene Tuning-Ergebnis, wenn dessen
Verlaesslichkeit selbst fraglich ist. Fuer binaer werden die getunten
Werte uebernommen (echter, robuster Verbesserungseffekt nachgewiesen).

Gespeichert: reports/tables/06_tuning_results.csv,
reports/tables/06_tuning_vorher_nachher.csv

Naechster Schritt: Abschluss-Markdown Notebook 06, AP 3.6 formal
abgeschlossen. Uebergang zu Modell B (Datengenerierung, EDA,
Preprocessing, Training - analog zum kompletten Weg von Modell A).

### Visualisierung: vier Overlay-Grafiken (Notebook 06, Zellen 08-13)

Die vier Analysegrafiken aus Notebook 05 wurden fuer Notebook 06 als
Overlays neu konzipiert - Default-Verteilung (Notebook 05) als
Referenz-Hintergrund, getunte Werte als goldene Stern-Marker darauf
projiziert. Bewusste Abweichung von reiner Wiederholung: Grafik 2/3
(Feature-Set-/Modelltyp-Effekt) waeren bei reiner Neuerstellung nicht
aussagekraeftig gewesen (kein Feature-Set-Vergleich mehr, da pro Modell
auf ein Set fixiert) - als Overlay auf der bestehenden Verteilung
dagegen sehr informativ (zeigt, wo sich das getunte Modell relativ zur
gesamten bisherigen Streuung einordnet).

- **Grafik 1** (Balkendiagramm Default vs. getunt, 3 Subplots je
  Zielgroesse, korrekte Metrik-Achsen): direktester Vorher-Nachher-Blick
- **Grafik 2** (Feature-Set-Boxplot-Overlay): getunte binaere Modelle
  liegen deutlich ueber allen Whiskern; continuous-Sterne (Ridge,
  RandomForest) liegen unterhalb aller Boxen inkl. Ausreisser
- **Grafik 3** (Modelltyp-Boxplot-Overlay, horizontal): bestaetigt
  dasselbe Muster aus der Modell- statt Feature-Set-Perspektive
- **Grafik 4** (Overfitting-Diagnose-Overlay): binaere getunte Modelle
  liegen im Idealbereich (hohe Guete, minimaler Gap) sogar noch praeziser
  gebuendelt als im Default-Zustand; continuous-Sterne liegen ausserhalb
  der gesamten Punktwolke (schlechter als jede Default-Kombination);
  multilabel-Sterne rutschen ins Mittelfeld, deutlich unter ihre
  urspruengliche Spitzenposition

Alle vier Grafiken bestaetigen konsistent: Tuning-Nutzen ist stark
zielgroessen-/datenmengenabhaengig, kein pauschaler Erfolg.

Gespeichert: reports/figures/06_grafik1_mit_tuning_overlay.png,
06_grafik2_overlay_feature_set.png, 06_grafik3_overlay_modelltyp.png,
06_grafik4_overlay_overfitting.png

---

## Notebook 07 – Evaluation Modell A (AP 3.7): Konzeptioneller Neuansatz
## + Einzelkriterien-Diagnosegueete

### Anlass: kritische Neubewertung des Geschaeftsprozessverstaendnisses

Vor Beginn dieses Notebooks wurde das zugrunde liegende Prozessverstaendnis
praezisiert (Extruder GmbH als Maschinenhersteller: Auftragseingang ->
konzeptionelle Freigabe -> Bau -> Inbetriebnahme mit iterativem Experten-
Tuning -> Auslieferung mit IO-Bericht). Ergebnis: die urspruengliche Rolle
von Modell A ("Filter fuer historische Massendaten vor Modell-B-Training")
passt nicht mehr zum praezisierten Geschaeftsmodell - da zu jeder
ausgelieferten Maschine bereits ein IO-Bericht vorliegt, ist die
Information "war die Einstellung gut" bereits bekannt, kein ML-Bedarf.

**Neue, praezisere Rolle fuer Modell A:** Unterstuetzung des iterativen
Korrekturschritts waehrend der Inbetriebnahme - konkret ueber die
bereits trainierte Multi-Label-Variante (WELCHES Kriterium ist verletzt,
z.B. "Ovalitaet") kombiniert mit SHAP (WELCHER Parameter traegt zur
Fehleinschaetzung bei, als Korrekturrichtungs-Hinweis). Modell B bleibt
fuer den ersten Startpunkt-Vorschlag zustaendig. Explizit dokumentiertes
Kernprinzip der Studie: eine ehrliche "machbar/nicht machbar"-Aussage ist
der eigentliche Wert, nicht eine moeglichst hohe Kennzahl.

### Einzelkriterien-Diagnosegueete (alle 3 Shortlist-Kandidaten)

Kritische Korrektur waehrend der Umsetzung: urspruenglicher Ansatz nutzte
nur EIN Modell (GaussianNB) mit einer nicht begruendeten Konfiguration -
korrigiert auf alle 3 Shortlist-Kandidaten (GaussianNB, LogisticRegression,
SVC) mit den bereits etablierten Sane-Default-Konfigurationen aus
Notebook 05 (NICHT die in Notebook 06 fuer multilabel verworfenen,
instabilen getunten Werte).

**Ergebnis (F1 je Einzelkriterium, bestes Modell):**

| Kriterium | Bestes F1 | Positivrate |
|---|---|---|
| y_nio_ovalitaet | 0.220 (LogReg) | 7.71% |
| y_nio_oberflaechenfehler | 0.157 (LogReg) | 6.14% |
| y_nio_wellhoehe | 0.151 (LogReg) | 4.14% |
| y_nio_wandstaerke | 0.145 (GaussianNB) | 3.71% |
| y_nio_od | 0.116 (LogReg) | 3.71% |
| y_nio_bindenaehte | 0.200 (SVC) | 0.71% |
| y_nio_delamination | 0.100 (SVC) | 0.86% |
| y_nio_blasenbildung | 0.071 | 2.00% |
| y_nio_risse | 0.076 (LogReg) | 1.14% |

### Theoretischer Bayes-Floor je Einzelkriterium (Monte-Carlo, wie Notebook 03)

Wichtige Ergaenzung: erreichtes F1 allein ist nicht interpretierbar ohne
die jeweilige Obergrenze - fuer die kombinierte io_nio-Zielgroesse war
diese bekannt (0.447), fuer Einzelkriterien bisher nicht separat
berechnet. Nachgeholt per Monte-Carlo-Simulation (2000 Wiederholungen,
analog Notebook 03 Zelle 14).

| Kriterium | Bayes-Floor | Erreichtes F1 | Ausschoepfung |
|---|---|---|---|
| **y_nio_wandstaerke** | **0.811** | 0.145 | ~18% - grosse ungenutzte Luecke |
| y_nio_oberflaechenfehler | 0.334 | 0.157 | ~47% |
| y_nio_wellhoehe | 0.208 | 0.151 | ~73% - nahe am Limit |
| y_nio_ovalitaet | 0.172 | 0.220 | uebertrifft den Floor (siehe unten) |
| y_nio_delamination | 0.115 | 0.100 | ~87% - nahe am Limit |
| y_nio_od | 0.126 | 0.116 | ~92% - nahe am Limit |
| y_nio_blasenbildung | 0.096 | 0.071 | ~74% - nahe am Limit |
| y_nio_risse | 0.095 | 0.076 | ~80% - nahe am Limit |
| y_nio_bindenaehte | 0.031 | 0.200 | **weit ueber dem Floor - statistisches Artefakt** |

**Zwei wichtige Einzelbefunde:**
- **y_nio_wandstaerke** ist theoretisch stark vorhersagbar (klare
  physikalische Formel: wandstaerke_ist = duesenspalt/die_swell_real),
  wird aber von den Modellen bei weitem nicht ausgeschoepft - konkreter,
  lohnender Ansatzpunkt fuer kuenftige Modellverbesserung
- **y_nio_bindenaehte und y_nio_ovalitaet** zeigen erreichtes F1 ueber
  dem berechneten Bayes-Floor - bei extrem wenigen positiven Faellen
  (bindenaehte: ~5 Faelle gesamt, ~1 pro Fold) ist das ein Symptom
  statistischer Unzuverlaessigkeit (einzelne zufaellig richtige
  Treffer verzerren F1 stark), kein echtes Signal

### Zentrale, ehrliche Gesamtaussage (Kernprinzip Machbarkeitsstudie)

Mit der aktuellen synthetischen Datenmenge (n=700) ist eine granulare
Einzelkriterien-Diagnose fuer KEINES der 9 Kriterien robust praxistauglich -
auch das beste Kriterium (Ovalitaet) erreicht nur F1≈0.22. Differenziertes
Bild statt Pauschalurteil: Wandstaerke zeigt grosses ungenutztes
Potenzial (Modellverbesserung lohnend), mehrere Kriterien liegen nahe an
ihrer jeweiligen Obergrenze (kein Datenproblem, sondern strukturelles
Limit), seltene Kriterien sind grundsaetzlich nicht robust diagnostizierbar
mit dieser Datenmenge - unabhaengig vom Modell.

Gespeichert: reports/tables/07_einzelkriterien_diagnose_guete.csv,
reports/tables/07_bayes_floor_je_kriterium.csv

Naechster Schritt: Konsequenzen fuer SHAP-Konzept (Notebook 07
Fortsetzung) und Modell-B-Planung basierend auf diesen ehrlichen
Machbarkeits-Erkenntnissen.

### SHAP-Konzeptentscheidung: binaeres Modell A statt Multi-Label

Nach der Einzelkriterien-Diagnose (F1≈0.15-0.22, deutlich unter
praxistauglichem Niveau) wurden zwei Alternativen fuer den SHAP-Teil
abgewogen:
- Alternative A: neuen, staerker kalibrierten Datensatz erzeugen, bis
  Multi-Label-SHAP aussagekraeftig wird - VERWORFEN, da dies dem
  Kernprinzip der Studie widersprochen haette (ehrliche Machbarkeits-
  aussage statt nachtraeglich passend gemachter Daten)
- **Alternative B (gewaehlt):** SHAP auf dem binaeren Modell A (F1=0.422
  auf echtem Test-Set, nahe Bayes-Floor 0.447) - nutzt das staerkste,
  bereits validierte Ergebnis, zeigt konzeptionell erklaerbare ML ohne
  Datenmanipulation

### Finales SHAP-Modell und Ergebnisse

LogisticRegression (C=1.0, l2, aus Notebook-06-Fold-Mehrheit abgeleitet),
Feature-Set "original", LinearExplainer (exakt, schnell). Erstmalige
Verwendung des seit Notebook 05 zurueckgehaltenen echten Test-Sets
(140 Zeilen) - Test-F1=0.422, konsistent mit CV-Schaetzung (0.423),
keine Ueberraschung, gute Bestaetigung der Generalisierungsfaehigkeit.

**Globale SHAP-Wichtigkeit (Summary-Plot):** mechanismus_Vakuum und
kalibrierdruck_mbar mit Abstand wichtigste Merkmale - bestaetigt
inhaltlich den fruehen Root-Cause-Fix (Formluft/Vakuum-Unterscheidung,
Notebook 02/03): genau die Variable, die urspruenglich fehlerhaft
modelliert und aufwendig korrigiert wurde, erweist sich als staerkster
Qualitaetstreiber. Schneckendrehzahl, Abzugsgeschwindigkeit, Duesenspalt
folgen (alle DN-korreliert), Kuehlwassertemperatur/MFR unwichtigst
(konsistent mit Generierungsdesign als "Rauschvariablen").

**Lokale Erklaerung (Waterfall-Plot, Einzelfall):** ein NIO-Testfall
korrekt vorhergesagt (63.7% NIO-Wahrscheinlichkeit), Hauptrisikofaktoren
identifiziert (niedrige Schneckendrehzahl, niedriger Duesenspalt). Mit
Klartext-Aufbereitung ergaenzt (echte statt standardisierte Werte) fuer
Demo-Verstaendlichkeit.

**Store44-Farbschema-Ausnahme (dritte, dokumentiert):** SHAP-Standard-
Farbskala (Rot/Blau fuer Merkmalswert hoch/niedrig) auf Store44-Gold/Blau
umgestellt - technisch aufwendiger als bei normalen matplotlib-Plots,
da SHAP eigene Rendering-Logik nutzt (rcParams allein unzureichend,
explizite Nachbearbeitung von Tick-Labels, Patches und Text-Objekten
noetig).

**Entscheidung gegen zusaetzliches IO-Beispiel:** weitere statische
Einzelfall-Demos im Notebook wurden bewusst nicht ergaenzt - die
interaktive Streamlit-Anwendung (fest zugesagtes Feature, AP 3.7/spaeter)
wird Live-Erklaerungen fuer beliebige Faelle bieten, ueberzeugender als
zusaetzliche statische Notebook-Plots.

Gespeichert: reports/tables/07_shap_globale_wichtigkeit.csv,
reports/figures/07_shap_summary_plot.png,
reports/figures/07_shap_waterfall_beispiel_nio.png

Naechster Schritt: Abschluss-Markdown Notebook 07, AP 3.7 fuer Modell A
abgeschlossen. Uebergang zu Modell B.

---

## Kritische Nachreflexion nach Notebook 07: Funktion von Modell A vs. Modell B

Nach Abschluss von AP 3.4-3.7 wurde die praktische Funktion von Modell A
im Geschaeftsprozess einer wiederholten, kritischen Pruefung unterzogen -
mit einem wichtigen, ehrlichen Ergebnis, das vor Beginn von Modell B
festgehalten wird.

### Gepruefte und verworfene Rollen fuer Modell A

Drei nacheinander vorgeschlagene praktische Rollen fuer Modell A wurden
jeweils kritisch hinterfragt und verworfen:
1. "Filter fuer historische Trainingsdaten von Modell B" - hinfaellig,
   da zu jeder ausgelieferten Maschine bereits ein IO-Bericht vorliegt
   (die Information liegt bereits vor, kein ML-Bedarf)
2. "Diagnose+Korrektur-Assistent waehrend der Inbetriebnahme" - hinfaellig,
   der Experte sieht einen Qualitaetsfehler (z.B. Ovalitaet) direkt am
   Werkstueck, braucht dafuer kein Vorhersagemodell
3. "Vorab-Check auf Modell-B-Vorschlaege" - hinfaellig, zirkulaerer
   Schluss: wenn Modell B bereits gelernt hat, gute Einstellungen
   vorherzusagen, liefert eine nachgeschaltete Pruefung durch Modell A
   keine neue Information

### Weitere waehrend der Reflexion aufgedeckte konzeptionelle Erkenntnis

Die grosse Nennweiten-Streuung in den Modell-A-Daten (DN50-DN315) deutet
vermutlich auf unterschiedliche MASCHINENKONFIGURATIONEN hin (verschiedene
Extrudergroessen/Korrugatoren je Baugroessenklasse), nicht auf
Einstellvarianten derselben Maschine - vermischt damit unbeabsichtigt
"Moment 1" (konzeptionelle Maschinenwahl bei Auftragseingang) und
"Moment 2" (Prozess-Feineinstellung bei Inbetriebnahme) in einem Modell.

**Entscheidung:** Modell A wird NICHT nachtraeglich ueberarbeitet oder neu
strukturiert (Datensatz-Vergroesserung sowie nachtraegliche Einteilung in
erfundene Maschinenklassen beide verworfen - letzteres würde unbegruendete
Annahmen einfuehren, ersteres loest das eigentliche Struktur-Problem
nicht). Stattdessen wird dies als dokumentierte LIMITATION festgehalten,
und als Lehre in die Modell-B-Konzeption uebernommen: Baugroesse/DN wird
dort von Anfang an explizit als X_B-Merkmal gefuehrt (Kunde gibt
Durchmesserbereich vor), statt nachtraeglich korrigiert werden zu muessen.

### Finale Funktionszuweisung beider Modelle

| | Modell A | Modell B |
|---|---|---|
| Frage | "Ist diese Einstellung gut?" | "Welche Einstellung soll ich waehlen?" |
| Praxisnutzen heute | Eingeschraenkt (Information oft bereits anderweitig vorhanden) | Hoch (loest das eigentliche Kernproblem) |
| Wert der Studie | Methodischer Nachweis, technische Infrastruktur, Prozesserkenntnisse | Eigentliches Produkt/Ziel |

**Wert von Modell A fuer die Gesamtstudie (trotz eingeschraenktem
eigenstaendigem Praxisnutzen):** vollstaendiger methodischer Nachweis
professioneller ML-Praxis (Root-Cause-Denken, Leakage-Vermeidung, Bayes-
Grenzen-Berechnung, Sane-Default-Kalibrierung, Nested-CV-Tuning, SHAP);
inhaltliche Prozesserkenntnisse (SHAP bestaetigt Formluft/Vakuum-
Mechanismus als staerksten Qualitaetstreiber); wiederverwendbare
technische Infrastruktur fuer Modell B (Pipeline-Builder, Metrik-
Funktionen, Bayes-Floor-Methode).

Diese ehrliche Neubewertung ist selbst ein Ergebnis im Sinne einer
Machbarkeitsstudie: nicht jede technisch saubere Komponente hat
automatisch eigenstaendigen Praxisnutzen - das explizit zu erkennen und
zu dokumentieren ist Teil des wissenschaftlichen Vorgehens, kein
Fehlschlag.

Naechster Schritt: X_B/Y_B-Struktur fuer Modell B konkret festlegen,
DN/Baugroesse explizit als X_B-Merkmal integrieren.

---

## Notebook [Modell B – wird ergaenzt, sobald Datengenerierung fuer Modell B beginnt]
