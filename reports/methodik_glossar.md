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

## Bayes-Optimale Klassifikationsguete / Theoretischer Noise-Floor (Monte-Carlo)

**Definition:** Bei bekanntem Generierungsprozess (nicht nur einem
trainierten Modell) laesst sich per Monte-Carlo-Simulation die THEORETISCH
bestmoegliche Klassifikationsguete berechnen: fuer jede feste Eingabe X
wird der stochastische Teil der Zielgroessen-Generierung vielfach
wiederholt, daraus ergibt sich P(Y=1|X). Die Bayes-optimale Regel sagt
die wahrscheinlichere Klasse voraus; kein Modell kann im Mittel besser
werden als diese Grenze, unabhaengig von Modellguete oder Datenmenge.

**Berechnung:** Accuracy_Bayes = Mittelwert von max(P(Y=1|X), 1-P(Y=1|X))
ueber alle X. F1_Bayes wird analog ueber die erwartete Konfusionsmatrix
unter der Bayes-Entscheidungsregel berechnet, optional mit
schwellenwert-optimiertem Grenzwert statt Standard 0.5.

**Wichtiger Vergleichsanker:** erwartetes F1 eines reinen 50/50-
Zufallsklassifikators bei Zielgroessen-Basisrate π:
F1_Zufall = 2·π·0.5 / (π+0.5). Zeigt, ob eine gemessene/theoretische F1
tatsaechlich lernbares Signal enthaelt oder nahe am Zufallsniveau liegt.

**Projektbezug (Modell A, io_nio):** Bayes-optimales F1 = 0.447 (bei
optimalem Schwellenwert 0.22), gegenueber F1_Zufall = 0.343 bei
Nio-Basisrate 26%. Zeigt: echtes, aber moderates lernbares Signal.
92.7% aller Datenpunkte liegen im "unsicheren Bereich" (P(NIO) zwischen
10% und 90%) - die weit ueberwiegende Mehrheit der Faelle ist selbst bei
perfektem Modellwissen nicht sicher entscheidbar. Dient als objektiver
Referenzpunkt: ein spaeteres trainiertes Modell mit F1 nahe 0.40-0.45 gilt
als sehr gut (nahe am theoretischen Optimum); deutlich hoehere Werte
deuten auf Data Leakage oder Fehler hin, nicht auf ein besonders gutes
Modell.

---

## Dichotomisierung / Informationsverlust durch Binarisierung

**Definition:** Wird eine kontinuierliche oder mehrdimensionale Zielgroesse
kuenstlich in eine binaere Kategorie (z. B. IO/NIO) zusammengefasst, geht
Information verloren - insbesondere (a) wie WEIT ein Wert von der
Entscheidungsgrenze entfernt ist (Sicherheitsabstand) und (b) WELCHE
Kombination von Einzelursachen zum Ergebnis gefuehrt hat, wenn mehrere
unabhaengige Kriterien per ODER zur Zielgroesse zusammengefasst werden.
In der Statistik/ML-Literatur als "loss of information through
dichotomization" dokumentiert (u. a. MacCallum et al.).

**Gegenmassnahmen (State-of-Art-Praxis):**
- Regression auf die zugrunde liegende kontinuierliche Groesse statt
  binaerer Klassifikation, ggf. mit nachtraeglicher Schwellenwertanwendung
- Multi-Label-Klassifikation statt Aggregation zu einem einzelnen Bit,
  wenn mehrere unabhaengige Zielkriterien vorliegen

**Projektbezug:** Modell A (io_nio) entstand durch ODER-Verknuepfung von
8 Einzelkriterien. Empirisch bestaetigt: 15.3% der NIO-Faelle haben 2+
gleichzeitig erfuellte Kriterien - diese Kombinationsinformation geht in
der binaeren Zielgroesse vollstaendig verloren. Fuehrte zur Einfuehrung
von zwei zusaetzlichen Zielgroessen-Varianten (kontinuierlicher
Sicherheitsabstand; Multi-Label-Vektor) zum systematischen Vergleich in
Notebook 05/06.

---

## Multi-Label-Klassifikation

**Definition:** Klassifikationsproblem, bei dem jede Beobachtung mehrere,
gleichzeitig zutreffende Kategorien haben kann (Y ist ein binaerer Vektor,
nicht ein einzelnes Label) - im Unterschied zu Multi-Class (genau eine von
mehreren Kategorien) oder binaerer Klassifikation (genau ein Bit).

**Passende Verfahren:** Bestehende Klassifikatoren lassen sich ueber
Wrapper erweitern (z. B. scikit-learn MultiOutputClassifier: trainiert
einen unabhaengigen Klassifikator je Label; ClassifierChain: beruecksichtigt
zusaetzlich Abhaengigkeiten zwischen Labels), oder ueber ein neuronales
Netz mit mehreren Sigmoid-Ausgangsneuronen (ein Wert je Label).

**Wichtige Abgrenzung:** Convolutional Neural Networks (CNN) sind fuer
diese Aufgabe NICHT das passende Werkzeug - CNNs nutzen raeumliche/
sequenzielle Nachbarschaftsstruktur (Bilder, Zeitreihen), die bei
tabellarischen Prozessdaten nicht vorhanden ist. Multi-Label-Faehigkeit
und Netzwerkarchitektur (CNN vs. MLP vs. Baumverfahren) sind zwei
unabhaengige Entscheidungsdimensionen - Multi-Label ist ueber praktisch
jeden Modelltyp umsetzbar, nicht an eine bestimmte Architektur gebunden.

**Projektbezug:** Zielgroessen-Variante 3 fuer Modell A - 8 Einzelkriterien
(Wandstaerke-, Ovalitaets-, Aussendurchmesser-, Wellhoehe-Toleranz sowie
4 Fehlerflags) als gemeinsamer Vektor statt aggregiertem Einzelbit.

---

## Data Leakage in der explorativen Datenanalyse (EDA), nicht nur beim Training

**Definition (Erweiterung des Data-Leakage-Konzepts):** Data Leakage wird
meist nur im Kontext von Modelltraining diskutiert (z. B. Skalierung auf
dem Gesamtdatensatz statt nur Training-Fold). Es kann jedoch bereits in
der EDA entstehen: wenn eine Zielgroesse Y aus anderen, im selben
Datensatz gemessenen Merkmalen abgeleitet wurde, und diese
Herkunftsmerkmale unreflektiert als "Praediktoren" in Korrelations-,
Signifikanz- oder Dimensionsreduktionsanalysen gegen Y einfliessen,
entsteht ein naeherungsweise tautologischer Zusammenhang - die Analyse
zeigt dann nicht, wie gut Y aus tatsaechlich verfuegbaren Eingangsgroessen
vorhersagbar ist, sondern nur, dass Y aus sich selbst (bzw. seinen
Bestandteilen) berechenbar ist.

**Pruefmethode:** Vor jeder Praediktor-Analyse explizit klaeren, welche
Merkmale zum Zeitpunkt der Vorhersage tatsaechlich verfuegbar waeren
(X, meist zeitlich/kausal VOR dem Zielereignis) und welche nur zur
Konstruktion der Zielgroesse selbst dienten (Bestandteile von Y).

**Projektbezug:** Die urspruengliche EDA (Notebook 03) vermischte X_A-
Prozessparameter mit Y_A-Qualitaetsmesswerten, aus denen io_nio direkt
per Schwellenwert berechnet wird. Nach Korrektur (nur X_A_MERKMALE, 9
echte Prozessparameter): Kruskal-Wallis-Signifikanz sank von 10/14 auf
5/9 Merkmale, Silhouette-Score von 0.037 auf 0.017 - das ehrliche,
Leakage-freie Bild der Aufgabenschwierigkeit. Der unabhaengig berechnete
Bayes-Noise-Floor (F1=0.447) war von Anfang an korrekt nur auf X_A
basiert und blieb dadurch die zuverlaessigste Referenzgroesse waehrend
der gesamten EDA-Phase.

---

## KNN-Imputation vs. Median-Imputation

**Definition:** Median-Imputation ersetzt alle fehlenden Werte einer
Spalte durch denselben Wert (den Median) - einfach, aber erzeugt eine
kuenstliche Haeufung (Spike) an genau diesem Wert und reduziert die
Varianz der Spalte messbar. KNN-Imputation schaetzt fehlende Werte
stattdessen individuell je Zeile, basierend auf den Werten der k
aehnlichsten anderen Zeilen (gemessen ueber die uebrigen Merkmale) -
nutzt vorhandene Korrelationsstruktur, erhaelt die Verteilungsform besser.

**Entscheidungskriterium:** Vergleich der Std-Abweichung vor/nach
Imputation - je naeher am Original, desto weniger Informationsverlust.

**Projektbezug:** Median-Imputation reduzierte die Std-Abweichung um
-2.3%/-2.0% (kuehlwassertemperatur/mfr_charge) mit sichtbarem
Verteilungs-Spike; KNN-Imputation (n_neighbors=5) nur um -2.0%/-0.7%,
ohne kuenstlichen Spike. KNN gewaehlt. WICHTIG: KNNImputer darf im
spaeteren Pipeline-Aufbau (Notebook 05/06) nur auf Trainingsdaten
gefittet werden (Data-Leakage-Vermeidung, analog zu jedem anderen
Fit-Schritt einer Pipeline).

---

## Maskierter Ansatz bei partiell anwendbaren Zielgroessen (MNAR)

**Problem:** Wenn eine Zielgroesse fuer eine Teilmenge der Daten
strukturell nicht anwendbar ist (z. B. Delamination nur bei doppel-
wandigen Rohren), ist eine kuenstliche dritte Kategorie ("nicht
anwendbar") als Klassifikationslabel methodisch problematisch: fuer ein
Modell ist sie nur ein drittes beliebiges Label ohne semantische
Sonderstellung. Wenn die "nicht anwendbar"-Kategorie zudem stark mit
einem anderen, leicht verfuegbaren Merkmal korreliert (hier: perfekt mit
wandtyp), wird die Klassifikationsaufgabe trivial loesbar und die
Gesamtmetrik kuenstlich aufgeblaeht, ohne dass das Modell etwas
Sinnvolles ueber das eigentliche Zielmerkmal gelernt haette.

**Loesung:** Zielgroesse bleibt in ihrer urspruenglichen Form (binaer/
numerisch), fehlende/nicht-anwendbare Werte bleiben als echte NaN
erhalten. Zusaetzliche binaere Anwendbarkeits-Flag-Spalte wird ergaenzt.
Training und Auswertung dieses spezifischen Labels erfolgen nur auf den
Zeilen, wo die Flag "anwendbar" anzeigt (Maskierung) - Standardtechnik
bei partiell anwendbaren Labels, insbesondere im Multi-Label-Learning.

**Projektbezug:** delamination bleibt binaer mit NaN bei einwandigen
Rohren, zusaetzliche Spalte delamination_anwendbar (0/1) ergaenzt.

---

## Cramer's V (Assoziationsstaerke bei kategorial-kategorialen Variablen)

**Definition:** Analog zum Pearson-Korrelationskoeffizienten fuer
numerische Variablen, aber fuer zwei kategoriale Variablen. Basiert auf
dem Chi2-Test, aber normiert auf einen Wertebereich 0 bis 1 (0=kein
Zusammenhang, 1=perfekter Zusammenhang), unabhaengig von der
Stichprobengroesse - wichtig, weil ein Chi2-Test allein nur die
statistische Signifikanz zeigt, nicht die praktische Effektstaerke.

**Wichtige Unterscheidung:** ein Chi2-Test kann bei grossen Stichproben
signifikant werden, obwohl der praktische Zusammenhang (Cramer's V)
verschwindend klein ist - beide Kennzahlen sollten gemeinsam betrachtet
werden.

**Projektbezug:** wandtyp vs. io_nio: Chi2 p=0.343 (nicht signifikant),
Cramer's V=0.036 (praktisch kein Zusammenhang). Erwartungskonform, da
wandtyp in der Generierungslogik nur den seltenen Delamination-
Mechanismus (6 Faelle) beeinflusst, nicht die anderen 7 NIO-Kriterien.

---

## Residualisierung (Baugroessenbereinigung ueber Regression)

**Definition:** Technik, um den Anteil einer Variable zu isolieren, der
NICHT durch eine andere (Confounder-)Variable erklaert wird: Regression
der Zielvariable auf den Confounder, das Residuum (beobachteter Wert
minus vorhergesagter Wert) enthaelt nur noch die vom Confounder
unabhaengige Variation. Das Bestimmtheitsmass R² der Hilfsregression
zeigt, wie stark eine Variable vom Confounder dominiert wird (hohes R²
= Confounder erklaert viel, Residuum traegt viel neue Information;
niedriges R² = Variable ist schon weitgehend confounder-unabhaengig,
Residuum ≈ Original).

**Wichtige Voraussetzung fuer Leakage-Freiheit:** der Confounder-Proxy
muss selbst aus zulaessigen Eingangsgroessen (X) berechnet werden, nicht
aus der eigentlichen, ggf. nicht verfuegbaren Zielgroesse oder aus
Merkmalen, die erst nach der Zielgroessen-Entstehung bekannt sind.

**Projektbezug:** DN-Proxy (PC1 aus 9 X_A-Merkmalen, r=0.984 zur
tatsaechlichen latenten Nennweite laut Notebook 03) als Confounder fuer
die Baugroesse. Residual-Features fuer alle X_A-Merkmale erzeugt. R²
zeigte klare Zweiteilung: 5 Merkmale stark baugroessengetrieben (R²
0.57-0.97), 4 Merkmale praktisch baugroessenunabhaengig (R²<0.03).
Trennbarkeitsgewinn (Kruskal-Wallis, Silhouette) durch diese einfache
lineare Residualisierung blieb gering - Hypothese nicht in dieser Form
bestaetigt, aber Residuen bleiben als zusaetzliche Feature-Option
sinnvoll (siehe generation_summary.md).

---

## Yeo-Johnson-Transformation - Wirkungsgrenze bei Multimodalitaet

**Definition:** Power-Transformation (Verallgemeinerung von Box-Cox,
funktioniert auch mit negativen/Null-Werten), zielt darauf ab, schiefe
Verteilungen naeher an eine Normalverteilung heranzufuehren durch eine
monotone, datenabhaengig parametrisierte Funktion.

**Wichtige Wirkungsgrenze:** Yeo-Johnson korrigiert Schiefe (Asymmetrie)
einer EINGIPFLIGEN Verteilung. Ist die Nicht-Normalitaet stattdessen
durch MULTIMODALITAET verursacht (mehrere ueberlagerte Teilpopulationen/
Cluster in denselben Daten), kann eine monotone Einzelvariablen-
Transformation dies grundsaetzlich nicht beheben - die Mischungsstruktur
bleibt nach der Transformation erhalten, nur auf einer anderen Skala.

**Pruefmethode:** Q-Q-Plots und Shapiro-Wilk-Test vor/nach Transformation
vergleichen; charakteristische "Stufenform" im Q-Q-Plot deutet auf
Multimodalitaet statt reiner Schiefe hin.

**Projektbezug:** 7 von 9 X_A-Merkmalen blieben nach Yeo-Johnson-
Transformation signifikant nicht-normalverteilt (Shapiro-Wilk p<0.05
vorher UND nachher) - konsistent mit der bereits identifizierten
Multimodalitaet durch ueberlagerte DN-Baugroessenklassen (siehe PCA/
Ground-Truth-Validierung, Notebook 03). Bestaetigt indirekt, dass die
DN-Residualisierung methodisch der passendere Ansatz gegen diese
spezifische Nicht-Normalitaetsursache ist. Yeo-Johnson nicht in die
finale Pipeline uebernommen.

---

## Dummy Variable Trap (Perfekte Multikollinearitaet bei One-Hot-Encoding)

**Definition:** Wird eine kategoriale Variable mit k Kategorien vollstaendig
in k One-Hot-Spalten kodiert (ohne eine Referenzkategorie wegzulassen),
sind diese Spalten perfekt linear abhaengig (Summe je Zeile = 1 =
Konstante) - fuehrt bei linearen Modellen zu einer singulaeren
Designmatrix (Dummy Variable Trap): Koeffizienten werden instabil und
nicht mehr eindeutig interpretierbar, der Effekt wird beliebig zwischen
den redundanten Spalten aufgeteilt.

**Pruefmethode:** Korrelation zwischen den One-Hot-Spalten einer
Kategorie berechnen - bei binaerer Kategorie exakt r=-1.0 als Beleg fuer
perfekte Redundanz.

**Loesung:** drop_first=True (bzw. drop='first' bei OneHotEncoder) -
eine Spalte je Kategorie weglassen, die verbleibenden Spalten kodieren
die volle Information verlustfrei (0 in allen Spalten = implizite
Referenzkategorie).

**Konsequenzen je Modelltyp:**
- Lineare/logistische Regression: PROBLEMATISCH, muss behoben werden
- Baumbasierte Modelle (Random Forest, Gradient Boosting): technisch
  unschaedlich, aber unnoetige Dimensionalitaet ohne Mehrwert
- Distanzbasierte Verfahren (KNN-Imputation, PCA, Silhouette-Score):
  redundante Spalten werden in der Distanzberechnung doppelt gewichtet,
  verzerrt Ergebnisse leicht

**Projektbezug:** wandtyp (doppelwandig/einwandig) und kalibriermechanismus
(Formluft/Vakuum) wurden zunaechst ohne drop_first kodiert (r=-1.0
rechnerisch bestaetigt), korrigiert auf je eine Spalte
(wandtyp_einwandig, mechanismus_Vakuum). Betraf rueckwirkend auch die
bereits durchgefuehrte KNN-Imputation und PCA in Notebook 04 (leicht,
da nur 2 redundante Spalten von vielen).

---

## Grenzen der Imputation bei individuellen Ausreisserwerten

**Konzept:** Imputationsmethoden (Median, KNN, etc.) schaetzen einen
plausiblen, typischen Wert basierend auf der Verteilung bzw. aehnlichen
Beobachtungen. Sie koennen grundsaetzlich KEINEN individuellen
Zufalls-Ausreisser korrekt rekonstruieren, der zufaellig genau an dieser
Stelle aufgetreten waere - die Schaetzung tendiert stattdessen zu einem
"typischen" Wert (verwandtes Phaenomen: Regression zur Mitte). Das ist
keine Fehlfunktion der Imputationsmethode, sondern eine inhaerente
Grenze: fehlende Information kann durch Schaetzung angenaehert, nicht
zuverlaessig exakt rekonstruiert werden.

**Praktische Konsequenz:** wenn eine von einer imputierten Groesse
abgeleitete binaere Entscheidung (z.B. Toleranzgrenze ueberschritten
ja/nein) in einzelnen Faellen von einem unabhaengig berechneten,
korrekten Referenzwert abweicht, ist das nicht zwingend ein Fehler in
der Ableitungslogik, sondern kann eine erwartbare Konsequenz der
Imputationsgrenze sein - insbesondere wenn der wahre, fehlende Wert ein
Ausreisser war. Empfehlung: betroffene Faelle nicht loeschen (Verlust
anderer, korrekter Information), sondern ueber eine Zuverlaessigkeits-
Flag markieren und bei Bedarf gezielt maskieren (siehe auch: Maskierter
Ansatz bei partiell anwendbaren Zielgroessen, oben im Glossar).

**Projektbezug:** 2 von 700 Zeilen zeigten nach Imputation eine
Diskrepanz zwischen rekonstruierter Multi-Label-Zielgroesse und
urspruenglichem binaeren Label - Diagnose ergab, dass die imputierten
Werte NICHT nahe der Toleranzgrenze lagen, sondern die echten
(geloeschten) Werte vermutlich Ausreisser waren. Zeilen wurden behalten,
Zuverlaessigkeits-Flag (y_od_komponente_zuverlaessig) grundsaetzlich
fuer alle 32 Zeilen mit imputiertem aussendurchmesser_ist gesetzt.

---

## Custom sklearn-Transformer (BaseEstimator, TransformerMixin)

**Definition:** Eigene Transformationen, die aus Daten lernende Parameter
ableiten (z.B. eine gelernte Achse, Regressionskoeffizienten), lassen sich
als eigene Klasse mit fit()/transform()-Schnittstelle implementieren
(Vererbung von sklearn.base.BaseEstimator und TransformerMixin). Dadurch
verhaelt sich die Transformation wie jeder eingebaute sklearn-Baustein
(StandardScaler, SimpleImputer, ...) und kann in eine sklearn.Pipeline
eingereiht werden - Cross-Validation-Infrastruktur (cross_validate,
GridSearchCV, manuelle Fold-Schleifen mit .fit_transform()/.transform())
sorgt dann automatisch dafuer, dass fit() nur auf Trainingsdaten laeuft,
transform() auf beliebige neue Daten angewendet wird. Strukturell
leakage-sicher, ohne manuellen Eingriff pro Fold.

**Projektbezug:** DNResidualizer (src/preprocessing.py) kapselt PCA +
9 Merkmal-Regressionen als custom Transformer, ersetzt die vorher
explorativ auf dem Gesamtdatensatz berechneten *_dn_bereinigt-Spalten
fuer den Trainingskontext.

---

## Gemeinsame Rueckfallmetrik bei unterschiedlichen Zielgroessentypen

**Problem:** Klassifikation (F1), Regression (RMSE/R²) und Multi-Label
(Macro-F1) nutzen jeweils eigene, nicht direkt vergleichbare Metriken -
"F1=0.40" ist nicht direkt mit "RMSE=0.15" vergleichbar.

**Loesung:** Eine gemeinsame Rueckfallmetrik definieren, auf die alle
Varianten zurueckgerechnet werden koennen. Bei kontinuierlichen/Multi-
Label-Vorhersagen: Rueckuebersetzung in dieselbe binaere Zielgroesse wie
die Referenzvariante (hier: Schwellenwert bzw. "irgendein Label=1" ->
IO/NIO), dort dieselbe Metrik (F1) berechnen wie fuer die binaere
Variante direkt. Ermoeglicht fairen Vergleich UND Einordnung gegen
denselben Referenzwert (hier: Bayes-Noise-Floor).

**Projektbezug:** f1_rueckuebersetzt als zusaetzliche Metrik fuer
"continuous" (Schwelle 0 am Sicherheitsabstand) und "multilabel"
(Summe der 9 Label-Vorhersagen > 0), neben den jeweils nativen Metriken.

---

## Praktische Modell-Eigenheiten: Label-Encoding-Anforderungen (XGBoost)

**Konzept:** Nicht alle ML-Bibliotheken kodieren kategoriale Zielgroessen-
Labels automatisch intern. Die meisten sklearn-Klassifikatoren akzeptieren
String-Labels direkt (z.B. "IO"/"NIO") und verwalten die interne
0/1-Kodierung selbst. XGBoost (bei binaerer Klassifikation) erwartet
dagegen explizit numerisch kodierte Klassen (0/1) und wirft sonst einen
ValueError. Kein Bug, sondern eine bibliotheksspezifische Anforderung,
die vor der Verwendung in einer generischen Modell-Schleife geprueft
werden muss.

**Loesungsmuster:** lokale Kodierung nur fuer die betroffene Modell-
/Zielgroessen-Kombination (nicht global), Vorhersage vor der eigentlichen
Metrik-Berechnung zurueckuebersetzen - haelt den Rest der Pipeline/
Metrik-Funktionen unveraendert und wiederverwendbar fuer alle anderen
Modelle.

**Projektbezug:** 4 von 104 Ablationskombinationen (XGBoost + binaere
Zielgroesse, alle 4 Feature-Sets) schlugen initial fehl, durch lokale
Label-Kodierung behoben.

---

## Robustheitsmuster fuer grosse Ablationsstudien

**Konzept:** Bei Schleifen mit vielen (hier: >100) unabhaengigen Modell-
Trainingsdurchlaeufen sollte ein einzelner Fehlschlag (Exception,
Konvergenzproblem, inkompatibler Datentyp) nicht die gesamte Studie
abbrechen. Standardmuster: Try/Except um jede Einzelkombination, Status
und Fehlermeldung dokumentieren statt zu crashen; Zwischenspeicherung
der Ergebnistabelle nach jeder Kombination (nicht erst am Ende), sodass
bei Abbruch keine bereits berechneten Ergebnisse verloren gehen.

**Projektbezug:** Ablationsschleife (Notebook 05) mit Try/Except je
Kombination + Speicherung nach jeder Zeile in
reports/tables/05_ablation_results.csv umgesetzt.

---

## Bayes-Floor als Referenzlinie in Ergebnisgrafiken

**Definition:** Die in Notebook 03 berechnete theoretische Obergrenze
(F1=0.447) wird in Modellvergleichsgrafiken als horizontale Referenzlinie
eingezeichnet - nicht 1.0 (perfekte Klassifikation), sondern dieser Wert
ist der korrekte Massstab, an dem jedes Modellergebnis gemessen werden
sollte, da er die durch Datenrauschen bedingte, unerreichbare Grenze
markiert.

**Abhaengigkeit von Zielgroessen-/Feature-Definition:** Der Bayes-Floor
ist NICHT unveraenderlich - er wurde spezifisch fuer die binaere
Zielgroesse io_nio UND unter der Annahme berechnet, dass nur X_A-
Merkmale als Eingabe zur Verfuegung stehen (kein Zugriff auf Y_A-
Qualitaetsmesswerte). Eine andere Zielgroessen-Definition (z.B.
kontinuierlicher Sicherheitsabstand) hat eine ANDERE theoretische
Obergrenze - fuer Regression gilt statt Bayes-Error die Rausch-
Standardabweichung als Grenze (siehe Glossar-Eintrag "Bayes-optimale
Klassifikationsguete"). Ebenso wuerden zusaetzliche, informativere
Features (die den irreduziblen Rauschanteil verringern wuerden) den
Bayes-Floor selbst nach oben verschieben - er ist eine Eigenschaft der
KOMBINATION aus Datengenerierungsprozess UND verfuegbaren Eingabegroessen,
nicht eine feste Konstante des Problems an sich.

---

## Multi-Label vs. binaer: Aufgabenschwierigkeit nicht gleichzusetzen mit Informationsgehalt

**Klarstellung (haeufiges Missverstaendnis):** Dass ein binaeres Modell
und ein Multi-Label-Modell (nach Rueckuebersetzung) aehnlich gut
abschneiden, widerspricht NICHT der Informationsverlust-Theorie bei
Dichotomisierung. Das binaere Modell trifft eine einzelne Entscheidung;
das Multi-Label-Modell muss NEUN unabhaengige Einzelentscheidungen
treffen (von denen mehrere extrem seltene Ereignisse betreffen, siehe
Shannon-Entropie-Diskussion) und wird erst danach zu einem einzelnen
Label aggregiert - das ist eine schwerere Aufgabe mit mehr
Fehlerquellen, kein Informationsvorteil gegenueber binaer. Die eigentliche
Bestaetigung des Informationsverlust-Arguments liegt in der kontinuierlichen
Variante: sie enthaelt nachweislich mehr Information als binaer
(Korrelation -0.604 statt ±1.0 zum binaeren Label), verliert diesen
Vorteil aber teilweise wieder durch die notwendige Rueckuebersetzung
ueber einen Schwellenwert.

---

## Schwellenwert-Abhaengigkeit bei binaerer Klassifikation

**Konzept:** Auch bei "binaeren" Klassifikatoren gibt es intern meist
einen kontinuierlichen Score (Wahrscheinlichkeit bei LogReg/GaussianNB/
Baummodellen, Distanz zur Trennebene bei SVM), der erst durch einen
Schwellenwert (Standard: 0.5 bei Wahrscheinlichkeiten) in eine finale
Klassenzuordnung uebersetzt wird. Dieser Schwellenwert ist eine
DESIGNENTSCHEIDUNG, keine feste Eigenschaft des Modells - eine
Verschiebung veraendert Precision/Recall-Tradeoff und damit F1.
sklearn verwendet 0.5 als Default fuer .predict(), waehrend
.predict_proba() den zugrunde liegenden Score liefert, auf den ein
beliebiger anderer Schwellenwert angewendet werden kann.

**Projektbezug:** Bei "continuous" wird analog ein Schwellenwert (aktuell
0 am Sicherheitsabstand) fuer die Rueckuebersetzung verwendet - auch
dieser ist nicht zwingend optimal und koennte wie beim Bayes-Floor
(Notebook 03) ueber eine Schwellenwert-Optimierung verbessert werden
(vorgemerkt fuer spaetere Vertiefung, z.B. AP 3.6).

**Warum GaussianNB im Regressionsvergleich ("continuous") fehlt:**
GaussianNB ist ein Klassifikationsverfahren (schaetzt P(Klasse|Merkmale)
ueber Normalverteilungsannahmen je Klasse) und hat kein direktes
Aequivalent fuer kontinuierliche Zielgroessen-Vorhersage (Regression) -
daher bewusst nicht in MODELLE_KONTINUIERLICH registriert, nicht durch
einen Schwellenwert-Effekt bedingt.

---

## GaussianNB (Naive Bayes) - mathematisches Grundprinzip

**Definition:** Klassifikationsverfahren auf Basis des Satzes von Bayes:
P(Klasse|X) proportional zu P(X|Klasse)*P(Klasse). Die "naive" Annahme:
alle Merkmale werden als UNABHAENGIG voneinander behandelt, wodurch sich
die gemeinsame Wahrscheinlichkeit P(X|Klasse) als Produkt der
Einzelwahrscheinlichkeiten je Merkmal berechnen laesst - macht das
Verfahren rechnerisch trivial (kein Optimierungsverfahren, keine
Iteration). "Gaussian": jedes Merkmal wird innerhalb jeder Klasse als
normalverteilt angenommen, geschaetzt werden nur Mittelwert und Varianz
je Merkmal und Klasse (bei 10 Merkmalen, 2 Klassen: 40 Parameter
gesamt).

**Warum GaussianNB trotz verletzter Unabhaengigkeitsannahme gut
funktionieren kann:** Bias-Variance-Tradeoff bei kleiner, stark
verrauschter Datenmenge - ein Modell mit sehr geringer Kapazitaet (wenige
Parameter) hat entsprechend geringe Varianz und kann kaum Rauschstrukturen
mitlernen. Bei einem Bayes-Floor, der zeigt, dass der Grossteil der Faelle
strukturell unsicher ist (92.7% im "unsicheren Bereich"), gewinnt ein
einfaches, robustes Modell gegen komplexere Modelle, die trotz
Regularisierung noch Rauschen aufgreifen. Bekanntes Phaenomen: Naive
Bayes ist fuer reine Klassifikationsentscheidungen oft robuster als der
Name/die vereinfachte Annahme vermuten laesst, solange die
Randverteilungen je Merkmal zwischen den Klassen noch unterscheidbar
sind - auch wenn die Korrelationsstruktur zwischen Merkmalen ignoriert
wird.

**Projektbezug:** GaussianNB gewinnt bei binaerer und Multi-Label-
Zielgroesse trotz hoher, nachgewiesener Korrelation zwischen den
Prozessparametern (Notebook 03). Mit Abstand schnellste Trainingszeit
aller 9 Modelle (~0.0006s), liegt zudem im Idealbereich der Overfitting-
Diagnose (hohe Guete, minimaler Train-CV-Gap).

---

## Store44-Farbschema: Grenzen bei vielen gleichrangigen Kategorien

**Konzept:** Das Store44-Farbschema definiert bewusst nur 3
bedeutungstragende Akzentfarben (Gold=wichtigste Zahl, Blau=Vergleichswert,
Gruen=Champion/Loesung) - funktioniert gut fuer 2-3 Kategorien, fuehrt
aber bei mehr gleichrangigen, individuell zu unterscheidenden Kategorien
(hier: 9 Modelltypen) zwangslaeufig zu Mehrfachbelegung derselben Farbe
und damit Verlust der Unterscheidbarkeit.

**Vorgehen bei begruendeter Ausnahme:** wenn eine Visualisierung mehr
eindeutig zu unterscheidende Kategorien braucht, als das Kernschema
hergibt, ist eine erweiterte, aber weiterhin dezente Palette
gerechtfertigt - MUSS aber explizit als bewusste Abweichung dokumentiert
werden (im Code-Kommentar und in der finalen Projektdokumentation), um
nicht wie eine unbeabsichtigte Inkonsistenz zu wirken.

**Projektbezug:** Notebook 05, Grafik 4 (Overfitting-Diagnose, 9 Modelle)
nutzt eine erweiterte Farbpalette statt der 3 Store44-Kernfarben.

---

## Sane-Default-Kalibrierungszyklus (Konzept, verallgemeinert)

**Definition:** Ein strukturiertes Vorgehen, um Modell-Standardwerte
sinnvoll an die konkrete Datenlage anzupassen, OHNE in systematisches
Hyperparameter-Tuning zu wechseln:
1. Baseline-Defaults nach bestem Wissen festlegen
2. Messen (vollstaendiger Modellvergleich)
3. Analysieren, systematische Schwaechen identifizieren (nicht einzelne
   Zufallsausreisser, sondern wiederkehrende Muster)
4. Neue, einzeln BEGRUENDETE Sane-Defaults ableiten (aus dem beobachteten
   Muster, nicht durch Ausprobieren mehrerer Werte)
5. Erneut messen, Wirksamkeit explizit im Vorher-Nachher-Vergleich
   bestaetigen (nicht nur "sieht besser aus")
6. Dokumentieren als abgeschlossenen Kalibrierungszyklus

**Abgrenzung zu Tuning:** Jede Korrektur ist eine einzelne, klar
begruendbare Antwort auf ein beobachtetes Fehlermuster (z.B. Overfitting-
Indikator, Klassenungleichgewichts-Versagen) - keine Suche ueber mehrere
Kandidatenwerte je Parameter. Sobald eine Korrektur mehrfach iterativ
nachjustiert werden muesste, um "besser zu werden", ist die Grenze zu
Tuning ueberschritten.

**Projektbezug:** Zwei Iterationen in Notebook 05 durchlaufen: Iteration 1
(Baumtiefe/Ensemble-Kapazitaet gegen Overfitting), Iteration 2
(class_weight gegen Klassenungleichgewichts-Versagen). Beide mit
expliziter Vorher-Nachher-Messung dokumentiert, klar getrennt von AP 3.6
(systematisches Tuning).

---

## Selbstkorrektur: vorschnelle Interpretation durch fehlende Kontrolle

**Wichtige methodische Lehre:** Der erste Befund "GaussianNB gewinnt
trotz verletzter Unabhaengigkeitsannahme, weil einfache Modelle bei viel
Rauschen robuster sind" war eine plausible, aber VORSCHNELLE Erklaerung -
sie beruecksichtigte nicht, dass mehrere Konkurrenzmodelle schlicht
fehlkonfiguriert waren (Klassenungleichgewicht nicht behandelt). Erst
nach der Sane-Default-Korrektur und erneuter Messung zeigte sich: der
Vorsprung war GROESSTENTEILS ein Artefakt der Konkurrenzschwaeche, nicht
ausschliesslich eine besondere Eignung von Naive Bayes.

**Verallgemeinerbare Lehre:** Ein Modellvergleich ist nur so aussagekraeftig
wie die Fairness der Ausgangsbedingungen aller verglichenen Modelle. Bevor
eine Erklaerung fuer "warum gewinnt Modell X" formuliert wird, sollte
geprueft werden, ob alle Konkurrenten unter vergleichbar sinnvollen
Bedingungen antraten - sonst wird ein Konfigurationsartefakt faelschlich
als methodischer Befund interpretiert.

---

*(Ende des aktuellen Stands - wird bei jedem neuen methodischen Konzept
im Projekt ergaenzt.)*