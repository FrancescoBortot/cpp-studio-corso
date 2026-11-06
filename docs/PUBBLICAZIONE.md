# Confine della versione pubblica

Il repository pubblico è [FrancescoBortot/cpp-studio-corso](https://github.com/FrancescoBortot/cpp-studio-corso).
La sua cronologia nasce da una copia pulita del solo software: non deriva dal
commit della copia completa privata.

## Contenuti pubblicati

- Sorgenti del frontend, del server e del motore di compilazione.
- Spiegazioni e note editoriali originali, con riferimenti alle fonti.
- Strumenti di estrazione, ricostruzione e verifica.
- Test indipendenti e test eseguibili dopo la generazione locale dei materiali.
- Manuale, architettura, verifiche, diagrammi originali e istruzioni di configurazione.

## Contenuti non distribuiti

| Categoria | Percorso locale |
|---|---|
| Dispensa, slide e archivi del docente | `materiali/`, eccetto il README |
| Testi estratti e contesti che riproducono le fonti | `app/web/catalog.json`, `snippet-projects.json`, `course-content.json` |
| Anteprime delle pagine | `app/web/references/` |
| Schermate che riproducono le fonti | `docs/screenshots/` |
| Runtime ROOT e dati della macchina | `app/.runtime/` |
| Cache e report locali | `.local/` |
| Appunti e sessioni personali | Browser ed esportazioni conservate fuori dal repository |

I pattern di esclusione sono in `.gitignore`; per le esportazioni personali con
nomi personalizzati resta necessario scegliere una cartella esterna al repository.
La copia completa privata rimane separata: non va resa pubblica cambiandone
semplicemente la visibilità, perché la cronologia conserva i materiali.

## Riproducibilità

`make check` verifica il software senza richiedere le fonti del corso e segnala
esplicitamente i controlli non eseguibili. Dopo aver aggiunto le fonti e usato
`app/tools/build.py`, `make check-course` controlla la configurazione completa.
Il repository da solo non ricostruisce il percorso didattico integrale.

```sh
git ls-files
git check-ignore app/web/catalog.json app/web/references/prova.jpg materiali/prova.pdf docs/screenshots/prova.jpg
make check
```

Prima di pubblicare modifiche controlla anche l’elenco dei file aggiunti. Non
aggiungere materiali originali, cataloghi derivati, screenshot delle slide,
credenziali o dati personali degli studenti.

I materiali conservano i diritti dei rispettivi titolari. Le istruzioni per
aggiungerli localmente sono in [materiali/README.md](../materiali/README.md).
Non è stata attribuita una licenza open source al codice applicativo: una sua
adozione richiede una scelta esplicita del titolare.
