# Contribuire

Prima di modificare l’applicazione, leggi il [README](README.md),
[l’architettura](docs/ARCHITETTURA.md) e le [verifiche](docs/VERIFICHE.md).

## Ambiente e controlli

La configurazione di riferimento usa macOS, Python 3.9+, Clang e Node.js 18+ per i
test JavaScript. Il frontend non richiede installazioni npm.

```sh
make check
# Dopo aver configurato i materiali locali:
make serve
```

Per cambiare l’estrazione dei PDF o rigenerare le anteprime installa
`requirements-build.txt` in un ambiente virtuale e rendi disponibile `pdftoppm`.
La pipeline completa è `make rebuild`.

## Organizzazione delle modifiche

- Conserva il materiale originale; documenta le correzioni in ricette o note editoriali.
- Mantieni i riferimenti degli appunti stabili e conserva il testo delle note anche se una fonte cambia.
- Tratta appunti e sessioni come dati locali: non introdurre sincronizzazioni o trasmissioni implicite.
- Verifica che una compilazione precedente non venga attribuita a una cella diversa.
- Controlla le modifiche visuali su computer e telefono, compresi selezioni e riferimenti alle slide.
- Aggiungi test per regole di importazione, trasformazioni dei dati o comportamento esecutivo; evita test che ripetano soltanto il markup.

Non aggiungere runtime, cache, credenziali, report personali o sessioni degli
studenti. I materiali del corso conservano i diritti dei rispettivi titolari;
qualsiasi modifica di visibilità del repository deve considerare il perimetro
indicato in [Pubblicazione](docs/PUBBLICAZIONE.md).

Le fonti didattiche e i cataloghi non sono distribuiti: i relativi controlli
sono segnalati come saltati finché non sono presenti. Dopo la generazione locale
usa `make check-course` per includerli.
