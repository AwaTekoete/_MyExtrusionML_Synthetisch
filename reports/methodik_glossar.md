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

*(Ende des aktuellen Stands - wird bei jedem neuen methodischen Konzept
im Projekt ergaenzt.)*
