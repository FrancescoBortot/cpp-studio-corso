# C++ Studio

Questa è la documentazione della versione pubblica del software. Prima del primo
avvio occorre aggiungere le fonti locali e generare i contenuti seguendo il
[README principale](../README.md#avvio-locale). Materiali, cataloghi e runtime ROOT
non sono inclusi nel repository pubblico. Le funzioni descritte sotto si riferiscono
alla configurazione completa dopo questi passaggi.

Notebook locale per la dispensa, le slide e gli esempi associati alle lezioni del corso 2025/26. Gli esercizi e i progetti della sezione generale Examples sono esclusi.

## Avvio

Su macOS apri **Avvia Studio.command**, oppure esegui dalla radice del progetto:

```sh
python3 app/server.py
```

Apri http://127.0.0.1:8765 . Mantieni la cartella `materiali_corso_2025_26` e la dispensa dentro `materiali/`, nella radice del progetto.

Servono Python 3.9+ e Clang/GCC. Il frontend non richiede installazioni o servizi esterni. Per eseguire il codice su macOS viene usato sandbox-exec. Nella configurazione di sviluppo verificata, il runtime ROOT è conservato in `app/.runtime/root`, separato dal sistema. I binari non sono inclusi nel repository pubblico.

## Uso

- **Lezione**: usa il lettore completo descritto nella sezione finale di questo manuale. Offre percorsi per argomento e per slide, con codice modificabile e appunti collegati.
- **Esempi e laboratori**: tutti i programmi delle lezioni, tutti i file testuali degli archivi, listati della dispensa e delle slide. Le note originali del docente sono consultabili nella cella e nelle Fonti.
- **Fonti originali**: slide e PDF, con testo ricercabile e anteprime delle pagine.
- **▶** compila ed esegue la cella; **Solo compilazione** mostra le diagnostiche senza eseguire. L’output compare sotto il codice.
- **Input e argomenti**: input consegnato prima dell’avvio e argomenti uno per riga. Questo ambiente non è un terminale interattivo durante l’esecuzione.
- **Opzioni**: standard, modalità rigorosa, macro, ROOT e gestione dei file. Gli header non sono unità di traduzione da compilare separatamente.
- **Arresta** ferma realmente compilazione o esecuzione. Cambiando vista, la richiesta precedente viene annullata e non può attribuire il risultato alla cella successiva.
- **+ Cella di codice** aggiunge un tentativo personale. Le celle personali sono recuperabili nella lezione anche dopo un cambio vista o un ricaricamento.
- Modifiche, appunti, segnalibri e avanzamento sono salvati nel browser. Scarica file esporta il file attivo; i risultati generati dal programma sono scaricabili nell’output.

## Originali e varianti

I 480 file testuali importati dagli archivi sono conservati senza modifiche. I file aggiuntivi di input, gli header di supporto e i listati ricomposti sono visibili nel laboratorio.

Le correzioni dei refusi e delle incompatibilità sono conservate in `patches`. Per i programmi che le richiedono, una nuova cella apre la variante documentata; **Ripristina** mostra il codice originale del docente. **Applica correzione documentata** consente di riapplicarla. I tentativi già salvati non sono sovrascritti automaticamente.

Esempi di correzioni: parametro del costruttore delegante, dichiarazione anticipata di Node, comparatore const, header prima di `using namespace std`. Il confronto tra originale e variante fa parte della spiegazione. I due esempi di copia vietata rimangono intenzionalmente non compilabili.

## Frammenti dei PDF

Sono classificati 601 estratti. Dopo la verifica con compilatore:

- 110 progetti completi, inclusi listati ricomposti da più pagine;
- 163 contesti compilabili con un file di supporto esplicito;
- 326 progetti concettuali da completare, con omissioni, dichiarazioni isolate o dipendenze non ricostruibili automaticamente.

Due estratti identici condividono il contesto nella stessa pagina: i progetti distinti sono 599. Un contesto minimo che verifica dichiarazioni non dimostra il comportamento di una classe: aggiungi chiamate al main per sperimentarlo. I frammenti da completare non sono presentati come programmi autonomi già validati.

## ROOT

Nella configurazione di sviluppo verificata è stata usata la distribuzione ufficiale ROOT 6.40.04 per macOS 26.6 arm64 / Clang 21. Il relativo URL e SHA-256 sono registrati in `app/.runtime/root-download.json`.

Il modulemap della libreria standard è adattato al SDK Apple installato con `app/tools/configure_root.py`; il file originale è conservato accanto alla versione adattata. Questa configurazione evita riferimenti a header assenti nel SDK disponibile. Il launcher la controlla all’avvio.

Il runtime richiede C++23. La compilazione mostra gli effettivi flag e librerie. Un adattatore di esecuzione imposta la modalità batch e chiude il ciclo eventi quando TApplication entra in Run, lasciando invariati i sorgenti del docente. I processi ausiliari di ROOT e le scritture nella cache del runtime sono abilitati; i file prodotti sono restituiti come download.

Il fit dell’esempio originale può terminare con un avviso di mancata convergenza del minimizzatore: questa diagnostica rimane visibile. La produzione dei parametri non viene presentata come prova della loro validità scientifica.

## Verifiche effettuate

- **192 programmi degli archivi**: 190 compilazioni riuscite con le ricette/varianti documentate; 2 errori didattici attesi. Sono inclusi i 5 programmi ROOT.
- **20 test** di motore e API: input, standard rigorosi, più sorgenti, macro, dati binari, risultati scaricabili, cancellazione anche anticipata, limiti, errori e accessi ai file.
- **18 esempi eseguiti** con input e risultati controllati; ulteriore rilettura di un istogramma ROOT esportato, verificandone i 100 ingressi.
- **273 progetti PDF** ricompilati nuovamente durante l’audit finale, senza errori.
- **441 anteprime originali** verificate; **480 file testuali originali** confrontati con gli archivi, senza modifiche.
- Browser: tutte le 14 lezioni, modifica/input/output, salvataggio e ripristino, recupero celle personali, cambio lezione durante un’esecuzione, arresto reale, ROOT e download, listato della dispensa ricomposto su più pagine, anteprime e navigazione mobile.

I programmi con comportamento indefinito o data race intenzionali vengono compilati ma non hanno un output deterministico garantito. Per il test del riempimento ROOT sincronizzato il numero di iterazioni è stato ridotto esplicitamente a 1000; il risultato atteso è 2000.

Dettagli riproducibili: `.local/reports/verification.json`, `.local/reports/runtime-verification.json`, `.local/reports/snippet-verification.json`, `.local/reports/final-audit.json` e `docs/VERIFICHE.md`.

## Ambiente di esecuzione

Il servizio è personale e ascolta solo su 127.0.0.1. Non è una piattaforma per utenti non fidati. Le esecuzioni hanno rete bloccata, lettura dei dati personali limitata e scritture nella cartella temporanea; per ROOT è accessibile anche il runtime locale e la sua cache. La compilazione usa i privilegi dell’utente locale.

Limiti: 8 secondi CPU, 8 secondi di attesa per il programma, 25 per compilare, 8 MiB per file prodotto e massimo due richieste contemporanee. L’output visualizzato è limitato a 200 kB per stream, con indicazione di troncamento. Sono scaricabili file generati fino a 1 MiB ciascuno, per un massimo totale di 4 MiB.

## Rigenerazione

Per rigenerare testo e anteprime servono pypdf, pdfplumber e pdftoppm; non servono per il normale utilizzo dell’applicazione.

```sh
python3 app/tools/catalog.py
python3 app/tools/enrich.py
python3 app/tools/configure.py
python3 app/tools/enrich_assets.py
python3 app/tools/prepare_snippets.py
python3 app/tools/render_references.py
python3 app/tools/verify.py
python3 app/tools/verify_runtime.py
python3 app/tools/audit.py
python3 -m unittest discover -s app/tests -v
```

Per la distribuzione ROOT di questa macchina, gli script `download_root.py` e `configure_root.py` mantengono l’installazione dentro il progetto. Su altri sistemi va predisposto un runtime compatibile; il server cerca anche root-config nel PATH.

## Lettore completo e appunti

Il percorso aggiornato contiene tutte le **309 slide**, divise nelle 14 lezioni, e **1.431 blocchi della dispensa principale**, organizzati in 322 argomenti. Le sezioni esplicitamente marcate «Approfondimento» sono escluse dal percorso principale; gli originali restano disponibili nelle Fonti. Anche i listati di approfondimento sono esclusi dalla lista principale degli esempi.

**Lezione continua** presenta il testo completo e le slide collegate. **Slide e spiegazioni** mostra ogni pagina originale con spiegazioni e punti testuali, mantenendo diagrammi e formule. I punti originali in inglese sono conservati: non si tratta di una traduzione integrale delle slide. Rvalue e thread, assenti dalla dispensa, hanno 28 spiegazioni specifiche aggiunte.

La ricerca nel corso comprende anche il corpo degli argomenti, i titoli delle slide e i nomi degli esempi. I risultati aprono il contenuto corrispondente. In **Lettura** puoi scegliere la dimensione del testo e la modalità concentrazione. Posizione e stato «Ho letto e verificato» sono salvati per argomento o slide.

Seleziona un passaggio e usa **Aggiungi nota** o **Evidenzia**. **Alt+N** apre una nota sulla selezione. Nel codice puoi selezionare un frammento o usare **Annota file**. Ogni nota conserva testo, contesto e riferimento alla fonte. **Nota sulla slide** collega un appunto alla pagina; **Annota zona** permette di trascinare un rettangolo su una figura, una formula o un diagramma. Le coordinate sono proporzioni dell’immagine e si adattano allo schermo. **Esc** annulla la selezione.

Il pannello **Appunti** offre ricerca nel testo e nei tag, filtro per lezione, preferiti, modifica, cestino e ripristino. Le note si salvano automaticamente; **Salva e chiudi** attende il salvataggio. **Apri riferimento** torna all’argomento, alla slide o al file della cella. Gli appunti generali precedenti vengono importati senza eliminare l’originale.

Le note conservano un’impronta della fonte: quando il materiale cambia, il riferimento non viene spostato silenziosamente. Il testo resta disponibile e l’interfaccia richiede di verificarlo. Una selezione ambigua non viene evidenziata automaticamente. Se la cella non esiste in un altro browser, il frammento resta nella nota.

**Backup JSON** conserva note, colori, tag, riferimenti, preferiti, cestino e stato di lettura. **Importa backup** aggiunge gli appunti; i conflitti vengono conservati come copie, senza sostituire note esistenti. **Esporta Markdown** produce un testo leggibile degli appunti attivi. I sorgenti modificati delle celle vanno esportati separatamente.

Gli appunti strutturati sono salvati in IndexedDB e non sono sincronizzati in cloud. Un altro browser, una diversa porta del server o la cancellazione dei dati del sito richiedono un backup per il recupero.

Per rigenerare anche il lettore, usa la pipeline completa:

```sh
python3 app/tools/build.py
```

Oppure, dopo aver generato catalogo e anteprime:

```sh
python3 app/tools/build_course.py
```

I test aggiornati comprendono 24 test Python e 6 JavaScript:

```sh
python3 -m unittest discover -s app/tests -v
node --test app/tests/test_study_store.js
```

### Lettura continua e indice

La lezione ora è una pagina unica: tutti gli argomenti si leggono in sequenza, senza selezionare un capitolo da un menu. La vista **Slide e spiegazioni** presenta tutte le slide della lezione già aperte, con il relativo testo. Anche i listati degli esempi e le pagine delle Fonti sono visibili senza espandere pannelli.

Sul computer trovi **In questa lezione** accanto al testo: scegli una voce per raggiungerla senza cambiare pagina. Sul telefono, in modalità concentrazione o con il quaderno aperto, usa **Indice lezione** nella barra superiore; scegliendo una voce l’indice si chiude. Il punto corrente è evidenziato e conservato per riprendere la lettura. **A−/A+** cambiano la dimensione senza menu aggiuntivi. Le opzioni tecniche del compilatore restano raggruppate nel laboratorio.

### Programmi, evidenziatore e sessioni personali

In **Esempi e laboratori**, **Apri laboratorio** apre subito il programma nell’area di lavoro completa. Le schede di main, sorgenti e header restano affiancate. Su computer ampi l’output è a destra dell’editor; **×** chiude il programma e torna all’elenco. Per sorgenti lunghi rimane lo scorrimento interno dell’editor.

**Evidenzia** nella barra superiore attiva il marcatore: seleziona testo o codice per evidenziarlo. Puoi anche selezionare prima un passaggio e attivare il pulsante, oppure usare **Evidenzia** nella barra che compare sulla selezione. Le evidenziazioni sono conservate negli Appunti e nelle sessioni. Nel codice restano sullo stesso file e vengono ricollegate al testo quando la corrispondenza è univoca. Premi nuovamente il pulsante per disattivare il marcatore.

**Sessione → Salva sessione** scarica un file JSON con tutti i progetti modificati, i file e l’header attivo, le celle personali, input, argomenti, macro, standard, opzioni ROOT, appunti ed evidenziazioni, avanzamento e preferenze di lettura. Non serve un account. È distinto da **Backup JSON** nel quaderno, che continua a esportare soltanto gli appunti e lo stato di lettura.

Per riprendere il lavoro in un altro browser, apri la stessa applicazione e scegli **Sessione → Carica sessione**. Controlla il riepilogo e premi **Ripristina questa sessione**. I progetti con lo stesso identificatore vengono sostituiti da quelli del file: salva prima la sessione corrente per conservarne una copia. Gli appunti vengono uniti senza eliminare quelli presenti; i conflitti sono conservati come copie. Se la scrittura delle impostazioni fallisce, viene ripristinato lo stato precedente delle chiavi coinvolte. Dimensione massima di importazione: 50 MiB. La sessione non contiene la dispensa, le slide o il runtime del compilatore: l’altro computer deve avere l’applicazione con il materiale del corso e un compilatore compatibile. I processi in esecuzione e i risultati temporanei non vengono ripresi.

Nella **Lezione continua**, **Vista compatta** allarga lo spazio di lettura e riduce margini, interlinea e dimensione di base del testo. Le pagine della **Dispensa** sono richiamate al termine di ciascun argomento, accanto ai riferimenti alle slide. **Slide e spiegazioni** mostra la slide a sinistra e spiegazione e punti originali a destra; la slide rimane visibile mentre scorri una spiegazione lunga. Su telefono le colonne tornano verticali.

### Slide guidate e commenti sul codice

**Slide e spiegazioni** è ora la vista iniziale del corso. La scelta manuale della Lezione continua resta memorizzata come preferenza. La colonna destra mostra la spiegazione pertinente alla singola slide, seguita dalla lettura del codice; non contiene più la sezione separata «I punti originali». I PDF e i testi originali rimangono consultabili nelle Fonti.

Nei listati, **Come funziona il codice** evidenzia istruzioni, parametri, valori restituiti e gestione delle risorse. Per FloatArray sono aggiunte note specifiche su copia nascosta, puntatori pendenti, allocazione e rilascio, copia profonda e trasferimento delle risorse, con le precisazioni sui commenti imprecisi delle slide.

**Commenti codice**, nella barra in alto, attiva gli indicatori numerati sulle righe della slide. Le etichette brevi occupano lo spazio libero, quando disponibile; clicca su un numero o toccalo per aprire il commento completo. Il pulsante sul numero e **Esc** permettono di chiudere il commento. La preferenza è conservata anche nel file sessione. In modalità «Annota zona» gli indicatori del codice sono temporaneamente nascosti per lasciare libera la selezione personale.

I banner **Ora provalo nel codice** si trovano fra le slide per le quali il docente indica un esempio. **Apri il codice** apre la cella direttamente nel banner, con file, input, compilazione e risultati. I collegamenti usano le corrispondenze esplicite fra frame e file del docente. I programmi con errori didattici restano identificati come tali.

Per rigenerare anche spiegazioni e coordinate dei commenti, usa `python3 app/tools/build.py`. La pipeline esegue `build_course.py` e poi `build_slide_guides.py`; quest’ultimo richiede pdfplumber, già compreso nelle dipendenze di ricostruzione. I contenuti editoriali specifici sono in `app/content/code-notes.json`, mentre le regole di lettura dei costrutti sono in `app/tools/slide_guidance.py`. Non serve alcun servizio esterno durante l’utilizzo.
