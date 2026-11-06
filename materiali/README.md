# Aggiungere le fonti localmente

Il repository pubblico non contiene dispensa, slide, archivi degli esempi,
trascrizioni o anteprime del materiale del corso. Per ricostruire il percorso
completo aggiungi una copia delle fonti ottenuta legittimamente, senza modificarne
il contenuto, nella seguente struttura:

```text
materiali/
|-- dispensa_cpp_unipd_2025_26_stile_compatto (1).pdf
`-- materiali_corso_2025_26/
    `-- lectures/
        |-- index.html
        |-- intro/          intro.pdf, examples.tgz se presente, exa_list se presente
        |-- basics/         basics.pdf, examples.tgz, exa_list
        |-- preproc/
        |-- slspec/
        |-- composite/
        |-- functions/
        |-- objcopy/
        |-- template/
        |-- stl/
        |-- inhpol/
        |-- pattern/
        |-- conclusions/
        |-- rvalue/
        `-- thread/
```

Ogni cartella di lezione deve conservare i nomi originali dei relativi PDF,
archivi e indici. La pipeline è configurata per la raccolta 2025/26 e per la
dispensa indicata, con la sua paginazione: non è un importatore generico di corsi.

Riferimento della raccolta: [sito del corso di P. Ronchese](https://userswww.pd.infn.it/~ronchese/cxx/y2526/).
La disponibilità del materiale sul sito non attribuisce una licenza di
redistribuzione. La dispensa va fornita separatamente dalla propria copia.

Dalla radice del progetto, con Python, Clang e `pdftoppm` disponibili:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-build.txt
python3 app/tools/build.py
python3 app/server.py
```

La ricostruzione genera `catalog.json`, `snippet-projects.json`,
`course-content.json` e le immagini in `app/web/references/`. Questi file sono
esclusi da Git insieme alle fonti. Non aggiungere a un commit i cataloghi generati:
contengono riproduzioni del materiale locale.

Le sezioni generali Examples, Exercises e Utilities dell’archivio non sono
necessarie per il percorso interattivo di questa versione. I programmi usati
dall’applicazione provengono dalla sezione Lectures.
