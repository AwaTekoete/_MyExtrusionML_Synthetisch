# Methodik-Glossar

Laufend gepflegtes Nachschlagewerk. Jede im Projekt verwendete statistische
oder methodische Konzeptidee wird hier bei erstmaliger Verwendung dokumentiert,
mit Definition, Wertebereich/Interpretation und Bezug zur konkreten
Anwendung im Projekt. Reihenfolge entspricht der chronologischen Einfuehrung.

---

## Skewness (Schiefe)

**Definition:** Misst die Asymmetrie einer Verteilung um ihren Mittelwert.

**Wertebereich/Interpretation:**
- ≈ 0: symmetrische Verteilung
- > 0: rechtsschief (lange Fahne nach rechts, viele niedrige Werte, wenige hohe)
- < 0: linksschief
- Faustregel: |Skew| < 0.5 = annaehernd symmetrisch, 0.5-1 = moderate Schiefe, > 1 = starke Schiefe

**Projektbezug:** Variablen mit starker Schiefe (z. B. schneckendrehzahl,
massedurchsatz, wellhoehe_ist) sind in Notebook 02 durchgaengig jene, die
von der latenten Nennweite (rohr_dn_latent) abhaengen - die Schiefe entsteht
durch Ueberlagerung mehrerer Groessenklassen zu einer Mischverteilung. Kein
Generierungsfehler, sondern erwartbares Verhalten bei geclusterten Daten.

---

## Kurtosis (Woelbung, Exzess-Kurtosis)

**Definition:** Misst, wie "schwer" die Raender (Tails) einer Verteilung im
Vergleich zur Normalverteilung sind. Referenzwert Normalverteilung = 0.

**Wertebereich/Interpretation:**
- ≈ 0: tail-Verhalten aehnlich Normalverteilung
- > 0: schwerere Tails, mehr Extremwerte (leptokurtisch)
- < 0: leichtere Tails

**Projektbezug:** kalibrierdruck_mbar zeigt sehr hohe Kurtosis (7.93), da die
Variable bimodal ist (Formluft-Ueberdruck positiv, Vakuum negativ gemischt).

---

## Shapiro-Wilk-Test

**Definition:** Statistischer Test auf Normalverteilung. Nullhypothese:
Daten sind normalverteilt.

**Interpretation:** p < 0.05 -> Normalverteilung wird verworfen. p > 0.05 ->
kein Beweis fuer Normalverteilung, nur kein Widerspruch dagegen (wichtige
Unterscheidung, keine Bestaetigung).

**Projektbezug:** massetemperatur (p=0.199) und mfr_charge (p=0.790) sind
mit Normalverteilung konsistent - beide wurden unabhaengig von der latenten
Nennweite mit einfachem Rauschen erzeugt. Die meisten uebrigen Variablen
verwerfen Normalverteilung (p<0.05), konsistent mit der Clusterstruktur.

**Konsequenz fuer Preprocessing:** baumbasierte Modelle (Random Forest,
Gradient Boosting) sind gegenueber fehlender Normalverteilung unempfindlich.
Bei linearen Baseline-Modellen koennten Transformationen (Box-Cox/
Yeo-Johnson) fuer stark schiefe Variablen relevant werden - Entscheidung
in Notebook 04 (Preprocessing).

---

## Shannon-Entropie

**Definition:** Quantifiziert den Informationsgehalt einer kategorialen
Variable. Formel fuer eine Variable mit Klassen-Wahrscheinlichkeiten p_i:
H = -Sum(p_i * log2(p_i)).

**Wertebereich (binaere Variable):**
- 0 Bit: eine Klasse kommt praktisch immer vor, keine Information
- 1 Bit: perfekt ausgeglichen 50/50, maximale Information

**Projektbezug:** io_nio (0.886 Bit) ist ausreichend informationsreich fuer
ein Klassifikationsmodell. Einzelne seltene Fehlermerkmale (bindenaehte
0.071 Bit, risse 0.090 Bit, blasenbildung 0.133 Bit) haben so niedrige
Entropie, dass sie bei n=700 kaum als eigenstaendige Zielgroessen
modellierbar sind (zu wenige positive Faelle) - das ist eine
Informationsgrenze, keine Modellierungsschwaeche. Rechtfertigt rueckwirkend
die Aggregationsentscheidung zu einer gemeinsamen io_nio-Zielgroesse.

---

## MCAR vs. MNAR (Missing-Value-Mechanismen)

**Definition:**
- MCAR (Missing Completely At Random): Fehlen ist rein zufaellig, haengt
  weder von beobachteten noch unbeobachteten Groessen ab
- MAR (Missing At Random): Fehlen haengt von anderen BEOBACHTETEN Groessen ab
- MNAR (Missing Not At Random): Fehlen haengt systematisch/strukturell mit
  der fehlenden Groesse selbst zusammen (z. B. Merkmal ist gar nicht anwendbar)

**Pruefmethode:** Kreuztabellen/Chi2-Tests bzw. t-Tests zwischen
"Wert fehlt" (boolesche Hilfsvariable) und anderen Merkmalen.

**Projektbezug:** delamination fehlt zu 71% - vollstaendig erklaerbar durch
wandtyp (100% Uebereinstimmung, MNAR: bei einwandigen Rohren ist das Merkmal
nicht anwendbar, nicht "verloren gegangen"). Die 4 uebrigen Luecken
(kuehlwassertemperatur, mfr_charge, wellteilung_ist, aussendurchmesser_ist)
zeigen keine Systematik gegenueber io_nio oder massedruck (alle p>0.05) -
konsistent mit MCAR. Konsequenz: delamination sollte NICHT imputiert werden
(methodisch falsch), die uebrigen 4 Spalten sind fuer Standard-Imputation
geeignet (Entscheidung folgt in Notebook 04).

---

## Standardabweichung der Zielgroesse als Genauigkeitsgrenze
## (Noise-Floor / Bayes-Error-Rate)

**Konzept:** Gilt unterschiedlich fuer Regression und Klassifikation.

**Regression (kontinuierliche Zielgroesse):** Wenn im Datengenerierungs-
prozess bekanntes Rauschen eingebaut ist (z. B. rng.normal(0, sigma, N)),
definiert dieses Rauschen eine untere Fehlergrenze (Noise-Floor). Kein
Modell kann im Mittel praeziser werden als dieses eingebaute Rauschen -
unabhaengig von Modellguete. Relevant fuer Modell B (kontinuierliche
Empfehlungswerte).

**Klassifikation (kategoriale Zielgroesse, z. B. io_nio):** Standard-
abweichung ist hier nicht direkt anwendbar. Das analoge Konzept ist die
Bayes-Error-Rate ueber die Klassenueberlappung im Merkmalsraum - wie stark
ueberschneiden sich die X-Verteilungen von IO- und NIO-Faellen? Abschaetzung
z. B. ueber Silhouette-Score oder Klassentrennbarkeit in PCA/t-SNE-
Projektionen (vorgesehen in AP 3.2.9, Notebook 03).

**Projektbezug:** Modell A (io_nio) -> Genauigkeitsgrenze ueber
Klassenueberlappung/Bayes-Error-Rate. Modell B (Empfehlungswerte) ->
Genauigkeitsgrenze ueber Standardabweichung des eingebauten Rauschens.
Beide Konzepte werden im Projekt an unterschiedlichen Stellen verwendet.

---

## SOTA (State-of-the-Art) - Projektspezifische Definition

**Einordnung:** Klassischer SOTA-Vergleich (Leaderboard-Logik wie bei
oeffentlichen Benchmark-Datensaetzen) ist fuer dieses Projekt NICHT
anwendbar, da die Daten synthetisch und projektspezifisch sind - kein
oeffentlicher Vergleichsdatensatz existiert.

**Stattdessen zwei projektinterne SOTA-Bedeutungen:**
1. SOTA als Methodik: Verwendung aktueller Best-Practice-Verfahren
   (Nested CV, SHAP, Bayessche Optimierung, saubere Leakage-Vermeidung)
2. SOTA als interner Referenzpunkt: Abstand zum bekannten Noise-Floor des
   selbst konstruierten Datengenerators (siehe Eintrag oben) - staerkerer,
   ehrlicherer Vergleichswert als ein externer, nicht direkt vergleichbarer
   Literaturwert.

---

## Overfitting / Curse of Dimensionality (Konzept, fruehe Projektphase)

**Definition:** Bei vielen Merkmalen (Dimensionen) im Verhaeltnis zur
Datenmenge werden Datenpunkte im Merkmalsraum zunehmend duenn verteilt
("sparse"). Modelle mit hoher Kapazitaet (z. B. k-NN/Lookup-artige Modelle)
laufen dann Gefahr, einzelne Trainingsfaelle zu "merken" statt die
zugrunde liegende Funktion zu lernen (Overfitting) - unabhaengig davon, ob
die einzelnen Merkmale kontinuierlich oder diskret sind.

**Pruefmethode:** Train/Test-Split bzw. Cross-Validation; grosse Differenz
zwischen Trainings- und Validierungsguete deutet auf Overfitting hin.

**Projektbezug:** Bewusst schlanke Variablenauswahl (finale Parametertabelle,
46 statt urspruenglich diskutierter 80-150 Parameter) als Gegenmassnahme,
begruendet in `reports/tables/01_parameter_final.csv`.

---

## Kruskal-Wallis-Test

**Definition:** Nichtparametrischer Test (kein Normalverteilungs-erfordernis)
zur Pruefung, ob sich die Verteilung eines numerischen Merkmals zwischen
zwei oder mehr Gruppen signifikant unterscheidet. Nichtparametrisches
Gegenstueck zur einfaktoriellen ANOVA.

**Projektbezug:** Auf dem urspruenglichen (fehlerhaften) Datensatz zeigte
nur 1 von 14 Merkmalen einen signifikanten IO/NIO-Unterschied. Nach
Behebung der Saettigungsfehler (siehe generation_summary.md) zeigten 10
von 14 Merkmale einen signifikanten Unterschied.

**Wichtige methodische Falle - "verduenntes Signal bei ODER-verknuepften
Zielgroessen":** Wenn eine binaere Zielgroesse (hier io_nio) aus MEHREREN
unabhaengigen Kriterien per ODER-Verknuepfung entsteht (z. B. Wandstaerke-
Toleranz ODER Ovalitaet-Toleranz ODER ...), verduennt sich das Signal
eines Einzelmerkmals im univariaten Test: ein Grossteil der "NIO"-Gruppe
hat bei diesem Merkmal ganz normale Werte, weil ein ANDERES Kriterium
das NIO ausgeloest hat. Univariate Tests sind bei solchen zusammengesetzten
Zielgroessen nur ein grober erster Filter, kein verlaessliches Kriterium
fuer Feature-Auswahl - multivariate Verfahren (PCA, Feature Importance
eines trainierten Modells) sind hier aussagekraeftiger.

---

## Mehrfachtest-Problem (Multiple Testing) / Bonferroni-Korrektur

**Definition:** Bei n unabhaengigen statistischen Tests mit Signifikanz-
niveau α=0.05 steigt die Wahrscheinlichkeit, rein zufaellig mindestens
einen falsch-positiven ("signifikanten") Befund zu erhalten, mit der
Anzahl der Tests. Erwartete Anzahl falsch-positiver Ergebnisse bei
Nullhypothese fuer alle Tests: n × α.

**Bonferroni-Korrektur:** konservative Gegenmassnahme - angepasste
Signifikanzschwelle α_korrigiert = α / n.

**Projektbezug:** Bei 8 Missing-Value-Systematik-Tests (4 Chi2 + 4 t-Tests)
zeigte aussendurchmesser_ist einen Chi2-p-Wert von 0.012. Bei erwarteten
8×0.05=0.4 falsch-positiven Ergebnissen und einer Bonferroni-Schwelle von
0.05/8=0.00625 gilt dieser Einzelbefund NICHT als robust signifikant -
zusammen mit dem nicht-signifikanten zugehoerigen t-Test (p=0.098) wurde
die Einordnung als MCAR beibehalten.

---

## Pearson-Korrelation bei bimodalen/regime-wechselnden Variablen (Fallstrick)

**Problem:** Eine einzelne Pearson-Korrelation ueber eine Variable, die aus
zwei strukturell unterschiedlichen Teilbereichen (Regimen) besteht, kann
irrefuehrend sein - sie misst dann primaer den Sprung/Bruch zwischen den
Regimen, nicht den tatsaechlichen Zusammenhang innerhalb eines Regimes.

**Pruefmethode:** Korrelation getrennt je Subgruppe/Regime berechnen und
mit der Gesamtkorrelation vergleichen.

**Projektbezug:** abzugsgeschwindigkeit vs. kalibrierdruck_mbar zeigte
Gesamtkorrelation von -0.678 (irrefuehrend negativ). Getrennt nach
Kalibriermechanismus: Formluft r=+0.873, Vakuum r=-0.853 (beide im
jeweiligen Regime dem Betrag nach positiv steigend mit Nennweite, aber
durch die Vorzeichenkonvention von kalibrierdruck_mbar - positiv=Formluft,
negativ=Vakuum - entsteht rechnerisch eine negative Korrelation ueber
beide Regime hinweg trotz konsistentem physikalischen Zusammenhang).

---

## Range Restriction / Deckeneffekt

**Definition:** Wenn eine Variable durch eine feste Ober-/Untergrenze
(Clipping/Sensor-Saettigung) auf einen engen Wertebereich beschraenkt wird,
geht innerhalb dieses gestauchten Bereichs die urspruengliche Information
verloren - uebrig bleibt vorwiegend Rauschen. Korrelationen, die auf dem
gestauchten Bereich berechnet werden, koennen dadurch stark abgeschwaecht
oder sogar im Vorzeichen verfaelscht werden.

**Projektbezug:** abzugsgeschwindigkeit war bei DN315 zu 100% an der oberen
Clip-Grenze (15 m/min) gesaettigt (Notebook 02, vor Korrektur). Die
resultierende scheinbare negative Korrelation zur Kalibrierdruck-Variable
innerhalb der Vakuum-Gruppe war teilweise auf diesen Deckeneffekt
zurueckzufuehren (behoben durch Neukalibrierung der Formel, siehe
generation_summary.md, zweite Root-Cause-Korrektur).

---

## PCA (Principal Component Analysis) - erklaerte Varianz, Scree-Plot, Loadings

**Definition:** Lineare Dimensionsreduktion, die die Richtungen maximaler
Varianz in den (standardisierten) Daten findet. Jede Hauptkomponente (PC)
ist eine Linearkombination der urspruenglichen Merkmale.

**Scree-Plot:** zeigt erklaerte Varianz je Komponente - hilft zu
entscheiden, wie viele Komponenten die Datenstruktur ausreichend erfassen.

**Loadings:** Gewichte der urspruenglichen Merkmale in einer Komponente -
zeigen, welche Merkmale eine Komponente inhaltlich treiben.

**Projektbezug:** PC1 (58.4% Varianz) laed fast einheitlich auf alle
geometrie-/prozessbezogenen Merkmale (Aussendurchmesser, Wellteilung,
Massedurchsatz, ...) - interpretiert als "Baugroessen-Faktor". PC2 (13.9%)
laedt auf MFR/Massetemperatur/Massedruck - "Material-/Prozessfuehrungs-
Faktor", unabhaengig von der Baugroesse. ~5 Komponenten erklaeren 92%
der Gesamtvarianz - effektiv deutlich weniger Freiheitsgrade als die
14 numerischen Rohmerkmale nahelegen.

---

## Silhouette-Score

**Definition:** Misst, wie gut Datenpunkte einer vorgegebenen Gruppierung
(hier: IO/NIO) im Merkmalsraum getrennt sind. Wertebereich -1 bis +1:
>0.5 starke Trennung, 0.25-0.5 schwache/moderate Struktur, ~0 ueberlappende
Gruppen, <0 Punkte im Mittel naeher am falschen Cluster.

**Projektbezug:** Silhouette-Score fuer IO/NIO auf 5 PCA-Komponenten
(92% Varianz) betraegt 0.037 - nahezu keine Trennbarkeit im Merkmalsraum.
Konsistent mit dem Generierungsdesign: io_nio haengt von LOKALEN
Abweichungen vom DN-spezifischen Sollwert ab, nicht von der Baugroesse
selbst (die PC1 dominiert) - die schwache Gesamttrennbarkeit ist daher
erwartungskonform, kein Hinweis auf ein Datenproblem.

---

## t-SNE (t-distributed Stochastic Neighbor Embedding)

**Definition:** Nichtlineare Dimensionsreduktion fuer 2D/3D-Visualisierung,
erhaelt lokale Nachbarschaftsstrukturen, verzerrt aber globale Abstaende.

**Wichtige methodische Regel:** t-SNE-Koordinaten sind NICHT fuer
quantitative Distanzmasse (z. B. Silhouette-Score) geeignet, da die
Achsen keine einheitliche, interpretierbare Skala haben. Nur zur
visuellen Exploration nutzen; quantitative Kennzahlen auf einer anderen
Grundlage (z. B. PCA-Komponenten) berechnen.

**Projektbezug:** t-SNE-Plot in Notebook 03 zur Visualisierung der
IO/NIO-Durchmischung genutzt, Silhouette-Score separat auf den ersten 5
PCA-Komponenten berechnet (nicht auf den t-SNE-Koordinaten).

---

## Erwartete vs. tatsaechliche Missing-Quote bei Unabhaengigkeit

**Konzept:** Bei m unabhaengigen (MCAR) Merkmalen mit Einzel-Missing-Raten
p_1...p_m ist die Wahrscheinlichkeit, dass eine Zeile in MINDESTENS einer
Spalte einen fehlenden Wert hat: 1 - Produkt(1-p_i) - deutlich hoeher als
die einzelnen Raten selbst vermuten lassen, da sich die "Nicht-Fehl"-
Wahrscheinlichkeiten multiplikativ verringern.

**Pruefmethode:** Beobachtete Quote "mindestens 1 fehlend" mit der
rechnerisch erwarteten Quote unter Unabhaengigkeitsannahme vergleichen;
zusaetzlich paarweise Ko-Auftretens-Matrix pruefen.

**Projektbezug:** 4 Spalten mit je ~4.3% Einzel-Missing-Rate ergaben einen
Zeilenverlust von 16.3% bei dropna() - exakt konsistent mit der
rechnerisch erwarteten Quote von 16.1% bei Unabhaengigkeit. Ko-Auftretens-
Matrix zeigte keine ungewoehnliche Haeufung (0-3 Faelle auf den
Nebendiagonalen). Bestaetigt: reiner MCAR-Kombinationseffekt, keine
versteckte Systematik. Konsequenz: dropna() fuer finale Modellierung
ungeeignet (zu hoher Datenverlust bei n=700), Imputation methodisch
gut begruendbar (kein MAR/MNAR-Verzerrungsrisiko).

---

## Adjusted Rand Index (ARI)

**Definition:** Misst die Uebereinstimmung zwischen einer gefundenen
Clusterzuordnung (z. B. KMeans) und einer bekannten wahren Gruppierung,
korrigiert um zufaellige Uebereinstimmung. Wertebereich: 1.0 = perfekte
Uebereinstimmung, 0.0 = Zufallsniveau, <0 = schlechter als Zufall.

**Unterschied zu einfacher Korrelation:** Korrelation prueft einen
KONTINUIERLICHEN linearen Zusammenhang; ARI prueft, ob DISKRETE
Clustergrenzen exakt getroffen werden - eine deutlich haertere
Anforderung, besonders bei unbalancierten, ungleich verteilten Klassen.

**Projektbezug:** PC1 korrelierte mit r=0.993 mit der latenten Nennweite
(starker kontinuierlicher Zusammenhang), aber KMeans-Clustering auf 5
PCA-Komponenten erreichte nur ARI=0.214 gegen die 10 echten, unbalancierten
DN-Klassen. Nach Fokussierung des Clusterings auf nur PC1 (Ausschluss des
Material-/Prozessfuehrungs-Rauschens aus PC2-PC5): ARI=0.694 - deutliche
Verbesserung, bestaetigt dass PC1 die DN-Struktur praezise traegt und die
zusaetzlichen Komponenten das Clustering-Ergebnis nur verwaessert hatten.

---

## Ground-Truth-Validierung (projektspezifisches Methodikprinzip)

**Konzept:** Bei synthetisch generierten Daten mit bekannter latenter
Struktur kann diese Struktur bewusst separat gespeichert (hier:
model_a_latent_reference.csv) und NACH Abschluss einer "blind"
durchgefuehrten Analyse zum Abgleich herangezogen werden. Dient als
objektiver Nachweis, ob die verwendete Analysemethodik echte Strukturen
zuverlaessig aufdeckt - unabhaengig von Modellwissen ueber den Generator.

**Projektbezug:** PCA/Clustering-Ergebnisse aus der blinden EDA (Notebook
03) wurden gegen rohr_dn_latent geprueft (r=0.993, ARI=0.694 bei PC1-
Clustering) - starker Beleg fuer die Verlaesslichkeit der Analysemethodik
in diesem Projekt.

---

*(Ende des aktuellen Stands - wird bei jedem neuen methodischen Konzept
im Projekt ergaenzt.)*
