# Ambito delle verifiche pubblicate

Questo documento conserva i risultati della configurazione di sviluppo completa.
Il repository pubblico non contiene le fonti del corso, i cataloghi derivati, le
anteprime o il runtime ROOT. I risultati riferiti a quel materiale sono documentati,
ma per ripeterli occorre aggiungere le fonti localmente. `make check` verifica il
software senza le fonti; `make check-course` verifica la configurazione completa.

# Collaudo del progetto

## Materiale e interfaccia

- 14 unità, 309 slide e 132 pagine didattiche della dispensa.
- 192 programmi main dagli archivi delle sole lezioni; nessuna importazione da Exercises o Examples generali.
- 480 file testuali originali confrontati nuovamente con gli archivi: invariati.
- 62 note originali degli archivi e 2 allegati binari integrati.
- 441 anteprime mantengono diagrammi, formule e tabelle.
- UI ibrida tra web app e notebook, con indice, celle, output inline e colori blu-viola / bianco / grigio-lilla.

## Seconda verifica

- Programmi degli archivi: 190 compilazioni riuscite, 2 errori didattici di copia vietata attesi. Le 27 varianti con correzioni sono documentate e separate dagli originali.
- Motore e API: 20 test passati, inclusi annullamento anticipato, processo bloccato, standard rigorosi, file di dati, risultati scaricabili e progetti su più sorgenti.
- Esecuzione: 18 esempi con input controllati; istogramma ROOT esportato e riletto, con 100 ingressi verificati.
- Frammenti PDF: 601 estratti, 599 contesti distinti. Ricompilati nuovamente i 110 programmi completi e i 163 contesti di supporto verificati: zero errori.
- Browser: tutte le 14 lezioni; output cambiato correttamente modificando un riferimento in copia; salvataggio dopo reload e ripristino; recupero di una cella personale; arresto reale; cambio lezione durante compilazione senza risultato attribuito alla nuova cella; macro; ROOT e download.
- Listato FloatArray ricomposto dalle pagine 80–82 eseguito nel browser: copie indipendenti e diagnostica dell’indice fuori intervallo osservate.
- Anteprima originale caricata correttamente; indice e lettura controllati anche a 390×844.

## Correzioni emerse durante il collaudo

- Il pulsante di una slide ora apre il codice effettivo estratto, con contesto verificato quando disponibile.
- Annullamento reale del processo; gestione anche della cancellazione che precede la registrazione della richiesta.
- Identità e generazione della richiesta impediscono risultati associati a una cella o lezione successiva.
- Ripristino delle impostazioni di compilazione e dei file della ricetta originale.
- Persistenza e recupero dei tentativi personali tra lezioni e ricaricamenti.
- Standard rigorosi: gli errori non sono nascosti da estensioni accettate dal compilatore.
- ROOT: runtime locale, compatibilità del modulemap con il SDK, cache accessibile, adattatore batch e chiusura del ciclo eventi per il notebook.
- Dati originali, input e argomenti allegati agli esempi che li richiedono.

## Limiti dichiarati

326 contesti PDF restano concettuali e richiedono completamento: non sono etichettati come programmi autonomi verificati. Sono comunque modificabili e compilabili per osservare le diagnostiche reali.

I programmi intenzionalmente indefiniti o con data race non vengono certificati attraverso un singolo output osservato. Non è stata validata l’esecuzione di tutti i 192 programmi con ogni input possibile.

Il fit ROOT originale segnala un avviso di convergenza del minimizzatore. La verifica conferma esecuzione e produzione di parametri finiti, non la validità scientifica del fit.

L’ambiente è personale, locale e specifico per macOS. Non è stato trasformato in servizio multiutente.

## Riordino per il futuro repository

Applicazione, materiali originali e documentazione raccolti nella cartella `cpp-studio-corso/`. Report e cache spostati in `.local/`; runtime ROOT conservato localmente in `app/.runtime/`. Aggiornati i percorsi di server e strumenti.

Ricontrollati 164 file del materiale originale tramite SHA-256: invariati. Verificate 14 lezioni e 441 anteprime nella nuova struttura. Ripetuti i 20 test di motore e API: passati. Verificati anche compilazione, esecuzione e file di istogrammi ROOT dopo lo spostamento. Controllate le regole Git con un repository temporaneo, senza inizializzare o pubblicare il progetto.

## Lettore completo e appunti — 6 novembre 2026

Copertura del nuovo generatore: **14 lezioni, 309 slide, 322 argomenti, 1.431 blocchi principali della dispensa**. I **125 blocchi di approfondimento** sono classificati ed esclusi dal percorso. Tutte le slide restano incluse anche quando trattano punti presenti nella dispensa fra gli approfondimenti. Rvalue e thread hanno **28 spiegazioni aggiunte**. I punti originali inglesi sono mantenuti insieme alle spiegazioni italiane: non si dichiara una traduzione integrale.

**24 test Python + 6 JavaScript passati**. La prima esecuzione dei test del motore nella sandbox annidata impediva avvio del server ed esecuzione dei programmi; la suite è stata rieseguita fuori dalla sandbox dell’agente, con tutte le protezioni dell’applicazione attive, e si è conclusa senza errori. Controlli: partizione completa dei blocchi, testo delle slide, immagini e impronte, identità uniche, contesto delle note al codice, quote ambigue, coordinate normalizzate, backup e importazione con duplicati/conflitti, rifiuto di importazioni malformate e Markdown.

Nel browser: tutte le 14 lezioni aperte; ricerca «mutex» con accesso diretto; nota su argomento e selezione testuale persistenti dopo reload; evidenziazione ripristinata; zona di una slide salvata e riaperta dopo reload; annullamento zona con Esc; preferiti, ricerca, cestino e ripristino; nota su file con recupero della cella e compilazione/esecuzione riuscita; importazione JSON con aggiunta della nota. Nessun errore console osservato. A 390×844 la pagina è larga 390 px e il pannello resta nel viewport; la viewport è stata ripristinata.

Gli appunti sono locali al browser, senza sincronizzazione cloud. Il backup JSON è separato dall’esportazione dei sorgenti delle celle. La verifica dimostra la conservazione del materiale estratto e delle immagini originali; non è una certificazione esterna di ogni affermazione delle fonti. I collegamenti fra sezioni e slide usano rimandi espliciti quando presenti, altrimenti prossimità o corrispondenza testuale; le due viste rendono sempre consultabile l’intero contenuto. Report in `.local/reports/content-coverage.json`.

## Lettura continua — revisione del 6 novembre 2026

La lettura per singole schermate è sostituita dal capitolo completo. Nel browser sono stati verificati tutti i 322 argomenti delle 14 lezioni, con altrettante voci nell’indice e senza ID duplicati. Il testo principale non contiene selettori o pannelli da espandere. Le celle personali sono visibili in fondo alla lezione. La vista slide mostra tutte le pagine già aperte; le spiegazioni della stessa sezione sono inserite una sola volta e richiamate con collegamenti nelle slide successive, conservando riferimenti univoci per gli appunti.

Controlli effettuati: indice desktop, passaggio da argomento a slide con posizione corretta, ritorno dalla nota al testo, apertura del laboratorio da un blocco della dispensa, esempio originale `dataRace/lgua.cc` compilato ed eseguito con risultato `0 errors found`; listati della lezione Funzioni tutti aperti (19); nessun errore console osservato. Su viewport 390×844: larghezza pagina 390 px, indice compreso tra y=108 e y=844 con scorrimento interno, chiusura automatica dopo scelta della voce. Viewport poi ripristinata. Passati nuovamente i 4 test di copertura e i 6 test delle regole degli appunti; sintassi JavaScript e struttura dei contenuti verificate. Il motore di compilazione e i materiali non sono stati modificati.

## Programmi completi, sessioni e lettura affiancata — 6 novembre 2026

Nuove verifiche nel browser: apertura diretta del programma nell’area completa senza spostare la pagina; schede di 5 file (main, due sorgenti, due header) conservate; esempio `simple/testPoint.cc` compilato ed eseguito; selezione del codice evidenziata, ancora presente dopo ricaricamento e riapertura; header attivo conservato. Esportazione sessione reale riuscita: 21 progetti e 6 appunti. Importazione di una sessione di prova a due file riuscita dopo correzione della conservazione del nodo del laboratorio durante il cambio lezione: `helper.h` attivo, `main.cc` compilato ed eseguito con output `42`, appunti esistenti conservati.

Verificati i richiami alla dispensa, la persistenza della vista compatta e le due colonne per slide e spiegazione (560 px ciascuna sulla viewport desktop usata). Su 390×844: pagina larga 390 px, programma tra y=108 e y=844, editor con scorrimento interno; le slide tornano verticali. Viewport ripristinata. Nessun errore console osservato nella verifica finale.

Aggiunti 5 test per sessioni: conservazione di tutti i file/opzioni e dell’header attivo, esclusione di chiavi estranee dell’archivio locale, rifiuto di dati e percorsi non validi, rollback in caso di quota esaurita, ripristino delle sole chiavi coinvolte. Insieme ai 6 test appunti: 11 test JavaScript passati. La sessione esportata non include processi, risultati temporanei, materiali originali o runtime; richiede la stessa applicazione con un ambiente compatibile. Il caricamento presenta un riepilogo prima di sostituire i progetti omonimi e unisce gli appunti senza eliminarli.

Audit finale di questa revisione: tutti i **24 test Python** (motore, HTTP e copertura) e gli **11 test JavaScript** (appunti e sessioni) sono passati: **35 test complessivi**. Le nuove risorse delle sessioni sono incluse anche nel controllo HTTP. Sintassi dei cinque moduli modificati e struttura delle risorse controllate senza errori.

## Slide guidate e commenti contestuali — 6 novembre 2026

Tutte le **309 slide** hanno una spiegazione associata; la vista iniziale è Slide e spiegazioni. La struttura «I punti originali» è rimossa dalla vista di studio, mantenendo immagini e fonti integrali. I listati visibili hanno una lettura delle istruzioni; l’estrazione per i commenti usa le coordinate dei caratteri nel PDF originale. Sono esclusi dagli indicatori gli oggetti PDF posizionati fuori pagina: durante il controllo sono stati trovati caratteri di vecchi esempi non visibili nella pagina, che altrimenti avrebbero generato riferimenti errati. Le fonti estratte rimangono conservate nel catalogo.

Il report `.local/reports/slide-guides.json` registra **302 commenti in 198 slide**, **204 slide con listati o frammenti monospaziati visibili** e **110 banner** associati alle indicazioni esplicite del docente. Alcuni blocchi monospaziati sono tabelle o nomi isolati, per i quali non è inserito un indicatore esecutivo. Per FloatArray le note sono riviste specificamente: passaggio per valore, shallow/deep copy, test di autoassegnazione, rischio in caso di fallimento dell’allocazione, stato della sorgente dopo move e restituzione per riferimento.

Controlli browser: tutte le 14 lezioni, 309 spiegazioni non vuote, nessuna struttura dei punti originali nella vista slide e nessun ID duplicato. Commenti attivati e disattivati dalla barra, preferenza conservata dopo reload; commenti apribili sulle righe e contenuti anche nel viewport mobile 390×844 (pagina larga 390 px). Verificati banner dopo la slide 10 di FloatArray, apertura della cella nello stesso banner e compilazione/esecuzione con output degli indici 0–4 e valori 0, 3.2, 6.4, 9.6, 12.8. Corretto l’abbinamento del frame 13 al solo `dumb/testFloatArrayPrint.cc`, evitando la precedente corrispondenza parziale col nome del test semplice. Nessun errore console osservato.

Aggiunti 5 test per spiegazioni complete, fedeltà dei listati alle fonti, riferimenti a righe reali, coordinate entro pagina, collegamenti agli esempi e correttezza delle note specifiche di FloatArray, incluso const scritto su una riga separata dal riferimento restituito. Un ulteriore test verifica i tipi delle nuove preferenze nel file sessione.

Audit finale: **29 test Python e 12 test JavaScript passati (41 complessivi)**. Verificate nuovamente sintassi JavaScript, disponibilità HTTP dei cataloghi e invarianti del compilatore. Il codice dei programmi e i materiali originali non sono stati modificati.
