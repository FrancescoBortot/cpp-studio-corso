# Architettura

C++ Studio è una webapp locale senza framework JavaScript o backend esterni.
Il browser presenta il corso e conserva i dati personali; Python serve i file e
coordina il compilatore installato sulla macchina.

## Componenti

| Componente | Responsabilità |
|---|---|
| `app/server.py` | Server HTTP su loopback, token per le richieste, limite di concorrenza e API di cancellazione |
| `app/engine.py` | Validazione del progetto, compilazione, standard, dipendenze, output e artefatti |
| `app/runner.py` | Esecuzione dei processi, timeout e profilo di isolamento |
| `app/web/app.js` | Navigazione, celle, file, input, compilazione e risultati |
| `app/web/course-view.js` | Lettore continuo, spiegazioni per slide, commenti contestuali e banner degli esempi |
| `app/web/annotations.js` | Selezioni, evidenziazioni, note e collegamenti alle fonti |
| `app/web/study-store.js` | Validazione degli appunti, quote, coordinate normalizzate, IndexedDB e importazione |
| `app/web/session-store.js` | Validazione del file sessione e ripristino delle chiavi applicative |
| `app/web/session.js` | Salvataggio, anteprima e ripristino della sessione tramite interfaccia |

## Dal materiale all’interfaccia

```text
materiali/                 fonti originali
    |
    v
app/tools/                estrazione, ricette, anteprime e guide
    |
    v
app/web/*.json            cataloghi e contesti
app/web/references/       anteprime delle pagine
    |
    v
browser                   lettura, codice e dati personali
```

`build.py` esegue la pipeline in ordine. `build_course.py` separa il testo
principale della dispensa dalle sezioni di approfondimento.
`build_slide_guides.py` associa spiegazioni e listati alle slide e ricava dal PDF
le coordinate dei commenti. `app/content/` conserva i contributi editoriali.
I file originali e le varianti corrette documentate rimangono distinti.

## Compilazione

1. Il browser invia file, sorgenti, standard, input e opzioni all’API locale.
2. Il server controlla host, origine e token della richiesta.
3. Il motore valida i percorsi e prepara una cartella temporanea.
4. Il compilatore produce diagnostiche e, quando richiesto, un eseguibile.
5. Il programma viene eseguito con limiti e isolamento applicativo su macOS.
6. Risultati e file prodotti vengono restituiti alla cella proprietaria della richiesta.

La cancellazione termina i processi della richiesta. Cambiare cella o vista non
deve attribuire il risultato del programma precedente al progetto successivo.
Il servizio ascolta soltanto su `127.0.0.1`; non è progettato come compilatore
pubblico o piattaforma multiutente.

## Dati personali

- `localStorage`: progetti modificati, input, opzioni, posizione e preferenze di lettura.
- `IndexedDB`: appunti, evidenziazioni, tag, riferimenti e cestino.
- File sessione JSON: copia trasferibile dei dati applicativi, caricata dopo un riepilogo.

Una selezione testuale conserva citazione e contesto; una zona della slide usa
coordinate proporzionali all’immagine. Le impronte delle fonti permettono di
segnalare riferimenti cambiati. Le importazioni degli appunti conservano i
conflitti come copie. Le sessioni non contengono processi, compilatore o materiali.
Questi dati personali non vengono aggiunti al repository.
