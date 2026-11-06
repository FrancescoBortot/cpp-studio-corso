"""Conservative reading notes for syntactic constructs actually present in a listing.

These are reading aids, not a C++ parser or proof that an example is correct.
Specific course examples can override these notes with reviewed editorial text.
"""
import re

def explain_line(line):
    s=line.strip()
    if not s or s in ('{','}','};','...') or s.startswith('//'):return None
    if re.search(r'\bdelete\s*\[\s*\]',s):return ('Rilascio dell’array','delete[] rilascia un array ottenuto con new[]. Il puntatore non viene azzerato e le altre copie dell’indirizzo non vengono aggiornate.')
    if re.search(r'\bdelete\s+',s):return ('Rilascio dell’oggetto','delete conclude il lifetime dell’oggetto e libera la memoria ottenuta con new; richiede un puntatore valido per questa operazione.')
    if 'std::move(' in s or re.search(r'(?<!\w)move\(',s):return ('Possibile trasferimento','std::move cambia la categoria dell’espressione: il trasferimento concreto dipende dal costruttore o dall’assegnazione selezionati.')
    if 'std::forward<' in s or re.search(r'(?<!\w)forward<',s):return ('Inoltro dell’argomento','std::forward<T> preserva la categoria dell’argomento nel contesto di deduzione mostrato; il parametro nominato, usato da solo, è un lvalue.')
    if '.c_str()' in s:return ('Vista C della stringa','c_str() restituisce un puntatore al buffer terminato da zero della stringa. Non trasferisce la proprietà e la validità dipende dal lifetime e dalle modifiche della stringa.')
    if '.emplace_back(' in s:return ('Costruzione nel contenitore','Gli argomenti vengono inoltrati al costruttore dell’elemento aggiunto in fondo. Una riallocazione può comunque spostare gli elementi già presenti.')
    if 'lower_bound(' in s or 'upper_bound(' in s:return ('Ricerca su un intervallo ordinato','Il confronto deve essere coerente con l’ordinamento dell’intervallo. lower_bound cerca il primo elemento non minore, upper_bound il primo strettamente maggiore secondo quel confronto.')
    if '.begin()' in s or '.end()' in s:return ('Limiti dell’intervallo','begin() individua l’inizio ed end() la posizione successiva all’ultimo elemento: end() non identifica un elemento da dereferenziare.')
    if '.insert(' in s:return ('Inserimento nel contenitore','Controlla l’overload: può inserire un valore o un intervallo. La validità di iteratori e riferimenti dopo l’operazione dipende dal contenitore.')
    if '.erase(' in s:return ('Rimozione dal contenitore','Controlla se l’overload riceve un iteratore, un intervallo o una chiave. Dopo la rimozione non usare riferimenti agli elementi eliminati.')
    if 'std::flush' in s:return ('Svuotamento del buffer','flush richiede di trasferire i dati in attesa allo stream sottostante. Il solo carattere di nuova riga non equivale in generale a questa richiesta.')
    if re.search(r'^\s*c\+\+\s',s):return ('Fase di compilazione','Leggi le opzioni del comando: -E si ferma al preprocessing, -c produce file oggetto, mentre la costruzione dell’eseguibile richiede il collegamento delle definizioni.')
    if 'operator[]' in s:
        if re.search(r'const\s+(?:float|double|int|T)\s*&',s):return ('Accesso in lettura','Il risultato è un riferimento a const: si osserva l’elemento senza copiarlo e senza modificarlo attraverso questo riferimento.')
        if '&' in s:return ('Accesso per riferimento','Il riferimento restituito può identificare l’elemento originale: un’assegnazione al risultato modifica quell’elemento se l’accesso è valido.')
    if re.search(r'\bnew\s+[^;]+\[',s):return ('Allocazione dell’array','new[] crea un array dinamico. La sua memoria richiede un rilascio coerente; copiare soltanto l’indirizzo non crea un secondo array indipendente.')
    if re.search(r'\bnew\s+',s):return ('Allocazione dinamica','new costruisce un oggetto in memoria dinamica e restituisce il puntatore. Occorre stabilire chi ne gestisce il rilascio.')
    if '= delete' in s:return ('Operazione vietata','La funzione è dichiarata deleted: un tentativo di usarla è un errore diagnosticato dal compilatore.')
    if '= default' in s:return ('Implementazione predefinita','= default richiede la versione generata dal compilatore; può risultare non utilizzabile se le operazioni sui membri non sono ammesse.')
    if re.search(r'\breturn\s+\*this',s):return ('Risultato dell’assegnazione','Restituisce l’oggetto corrente. Se la firma restituisce un riferimento, permette di concatenare le assegnazioni senza copiare il risultato.')
    if re.search(r'\breturn\b',s):return ('Valore restituito','return conclude questa chiamata e fornisce il risultato indicato; per capire se viene copiato un valore o restituito un riferimento, controlla la firma.')
    if re.search(r'\bthrow\b',s):return ('Segnalazione dell’errore','throw avvia la propagazione di un’eccezione. Il controllo passa al gestore catch compatibile, con le regole di distruzione degli oggetti automatici.')
    if re.search(r'\bcatch\s*\(',s):return ('Gestione dell’eccezione','Il gestore viene selezionato in base al tipo dell’eccezione. Un parametro per riferimento evita di creare una copia del suo oggetto.')
    if re.search(r'\bif\s*\(',s):
        if re.search(r'\bthis\s*==|==\s*this\b',s):return ('Controllo dell’identità','Confronta l’indirizzo dell’oggetto corrente con quello della sorgente: riconosce il caso in cui entrambi indicano lo stesso oggetto.')
        return ('Scelta del percorso','Il corpo associato viene eseguito soltanto se la condizione è vera. Valuta questa condizione prima di seguire le istruzioni del ramo.')
    if re.search(r'\b(for|while)\s*\(',s):return ('Ripetizione','Il ciclo ripete il corpo secondo la condizione mostrata. Segui separatamente inizializzazione, controllo e aggiornamento degli indici o dello stato.')
    if 'lock_guard<' in s or 'unique_lock<' in s:return ('Lock legato allo scope','L’oggetto gestisce il lock tramite il proprio lifetime: il rilascio avviene all’uscita dallo scope secondo il tipo di lock utilizzato.')
    if '.lock()' in s:return ('Acquisizione del mutex','Richiede il possesso del mutex prima di entrare nella regione protetta; tutti gli accessi condivisi devono seguire lo stesso protocollo.')
    if '.unlock()' in s:return ('Rilascio del mutex','Rilascia il mutex posseduto. Con lock e unlock manuali occorre gestire anche le uscite anticipate e le eccezioni.')
    if '.join()' in s:return ('Attesa del thread','join attende la conclusione del thread. Non rende automaticamente corretti gli accessi concorrenti avvenuti prima dell’attesa.')
    if 'atomic<' in s:return ('Oggetto atomico','Il tipo offre operazioni atomiche; una sequenza composta da più operazioni non diventa automaticamente una singola operazione atomica.')
    if 'set_value(' in s:return ('Consegna del risultato','Completa lo stato condiviso con un valore, rendendolo disponibile al future associato.')
    if '.get()' in s:return ('Recupero del risultato','Per un future, get attende il risultato se necessario e può rilanciare l’eccezione del produttore. Per altri tipi, il significato dipende dall’interfaccia.')
    if re.search(r'\b(?:cout|cerr)\s*<<',s):return ('Output osservabile','Gli operatori << inseriscono valori nello stream, da sinistra a destra. L’output permette di osservare il percorso o i valori raggiunti dal programma.')
    if re.search(r'\bcin\s*>>',s):return ('Input nei dati','Gli operatori >> leggono valori dallo stream e li scrivono negli oggetti indicati. Il formato e il tipo delle destinazioni determinano la lettura.')
    if re.search(r'^\s*#\s*include',s):return ('Dichiarazioni incluse','L’header rende disponibili le dichiarazioni usate nel sorgente. La definizione delle funzioni non inline può richiedere anche un file da collegare.')
    if re.search(r'^\s*#\s*define',s):return ('Sostituzione del preprocessore','La macro sostituisce token prima della compilazione: non è una funzione e può ripetere la valutazione apparente di un argomento.')
    if re.search(r'^\s*#\s*(ifn?def|if|else|endif)',s):return ('Compilazione condizionata','La direttiva decide quali parti del sorgente arrivano al compilatore in base alle condizioni del preprocessore.')
    if 'template' in s and '<' in s:return ('Parametro del template','Il parametro rappresenta un tipo o un valore utilizzato nella definizione. Le operazioni devono essere valide per l’istanziazione richiesta.')
    if re.search(r'\bvirtual\b',s):return ('Interfaccia polimorfa','La dichiarazione introduce una funzione virtuale. L’override selezionato dipende dal tipo dinamico quando la chiamata usa il meccanismo virtuale.')
    if re.search(r'\bfriend\b',s):return ('Accesso concesso esplicitamente','La dichiarazione concede al soggetto indicato accesso ai membri non pubblici; l’amicizia non si estende automaticamente ad altri soggetti.')
    if re.search(r'\bstatic\b',s):return ('Entità condivisa o durata statica','Leggi static nel suo contesto: un membro statico appartiene alla classe; una variabile locale statica conserva lo stato tra le chiamate.')
    if re.search(r'\bnoexcept\b',s):return ('Contratto sulle eccezioni','Un’eccezione che esce da una funzione noexcept causa std::terminate: noexcept non la intercetta automaticamente.')
    if re.search(r'~\w+\s*\(',s):return ('Distruttore','Questa funzione termina la gestione delle risorse dell’oggetto. Occorre coordinarla con le operazioni di copia e di movimento.')
    if re.search(r'^\s*(class|struct)\s+\w+',s):return ('Definizione del tipo','Il tipo raccoglie membri e operazioni. Le sezioni public e private definiscono quali parti possono essere usate dal codice cliente.')
    if re.search(r'\b(?:int|void)\s+main\s*\(',s):return ('Ingresso del programma','Da main parte il percorso del programma mostrato. Segui l’ordine delle istruzioni e le chiamate che costruiscono o modificano gli oggetti.')
    if re.search(r'^\s*(?:[\w:<>]+\s+)*\w+\s*\([^;]*\)\s*(?:const)?\s*[;{]?',s):return ('Firma e parametri','Distingui parametri per valore, puntatore e riferimento. const può qualificare il dato, l’accesso attraverso il parametro o la funzione membro.')
    return None

def code_steps(code):
    result=[];seen=set()
    for number,line in enumerate(code.splitlines(),1):
        note=explain_line(('const ' if number>1 and code.splitlines()[number-2].strip()=='const' else '')+line)
        if note and note[0] not in seen:
            seen.add(note[0]);result.append(dict(line=number,code=line.strip(),title=note[0],text=note[1]))
    return result
