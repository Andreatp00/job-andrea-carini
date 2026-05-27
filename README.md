# 🔍 Job Hunter Bot — Back Office / Ragioneria Trapani

Bot automatico di ricerca lavoro per profilo **Diplomato Ragioneria AFM | 4 anni esperienza amministrativa | 25 anni | Trapani**.

Cerca ogni giorno alle **08:00** su:
- **Subito.it** (molto usato a Trapani) — priorità massima
- **LinkedIn, Indeed, Google Jobs**
- **Agenzie per il Lavoro** — Adecco, Manpower, Randstad, Gi Group, Openjobmetis, Synergie, Humangest
- **Siti Aziendali** — studi commercialisti Trapani, enti locali
- **Concorsi Pubblici** — inPA, Concorsi.it, Gazzetta Ufficiale, Sicilia Concorsi, ASL Trapani, Agenzia Entrate, INPS

Filtra per:
- ✅ **Back office / Amministrativo / Contabilità / Segreteria**
- ✅ **Part-time** (perché studi all'università)
- ✅ **Smart Working / Remoto**
- ✅ **Solo diploma richiesto** (nessuna laurea)
- ✅ **Stage e tirocinio** inclusi (per fare esperienza in studi commercialisti)
- ✅ **Concorsi pubblici categoria C/D** per diplomati

Priorità geografica:
1. 🔴 **Trapani e provincia** (massima priorità)
2. 🟠 **Sicilia**
3. 🟢 **Smart Working / Remoto Italia**

## Setup (una volta sola)

### 1. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Aggiungi i Secrets su GitHub (se usi GitHub Actions)

Vai su **Settings → Secrets and variables → Actions → New repository secret** e aggiungi:

| Nome Secret | Valore |
|---|---|
| `TELEGRAM_BOT_TOKEN` | *(il tuo token bot Telegram)* |
| `TELEGRAM_CHAT_ID` | *(il tuo chat ID Telegram)* |
| `EMAIL_SENDER` | *(email mittente)* |
| `EMAIL_APP_PASSWORD` | *(password app Gmail)* |
| `EMAIL_RECIPIENT` | *(email destinatario report)* |
| `OPENAI_API_KEY` | *(opzionale - per ranking AI Mistral)* |

### 3. Configura il profilo

Apri `config.py` e personalizza `PROFILE` con i tuoi dati.

### 4. Avvia il bot

```bash
python job_hunter.py
```

## Struttura del progetto

```
job-2.0--main/
├── config.py                     # Profilo candidato, keyword, siti, punteggi
├── job_hunter.py                 # Motore principale del bot
├── scrapers/
│   ├── __init__.py
│   ├── subito_it.py              # ✅ Scraper Subito.it (Trapani)
│   ├── concorsi_pubblici.py      # ✅ Scraper concorsi pubblici PA
│   └── agenzie_lavoro.py         # ✅ Scraper agenzie interinali
├── data/
│   └── reports/                  # Report Excel/CSV generati
├── logs/                         # Log giornalieri
├── requirements.txt
└── README.md
```

## Funzionamento

1. **Raccolta**: cerca su Subito.it, LinkedIn, Indeed, Google Jobs, agenzie lavoro, siti aziendali e portali concorsi
2. **Normalizzazione**: standardizza e deduplica le offerte
3. **Filtraggio**: esclude ruoli non amministrativi, quelli che richiedono laurea o troppa esperienza
4. **Scoring**: assegna punteggio basato su keyword, localizzazione, part-time/smart working
5. **Ranking AI** (opzionale): se configurata API Mistral, riordina con AI
6. **Report**: genera file Excel con Top_Match, All_Relevant, Borderline, Esclusi_Audit e Tracker Candidature
7. **Notifica**: invia report su Telegram e/o email con allegato Excel

## Siti monitorati

### 🔴 Trapani e provincia (Subito.it)
- Ricerche: back office, impiegato amministrativo, contabilità, fatturazione, segreteria, commercialista, ragioneria, praticante, part-time

### 🟠 Portali classici (LinkedIn, Indeed, Google Jobs)
- Ricerche geografiche: Trapani, Sicilia, Italia (smart working)

### 🟢 Agenzie per il Lavoro
- Adecco, Manpower, Randstad, Gi Group, Openjobmetis, Synergie, Humangest
- Ricerche a Trapani e Smart Working

### 🔵 Concorsi Pubblici
- inPA (Portale Unico PA), Concorsi.it, Gazzetta Ufficiale
- Sicilia Concorsi, PA Sicilia, ASL Trapani
- Comune Trapani, Agenzia delle Entrate, INPS

### 🟣 Siti Aziendali
- Studi commercialisti Trapani, Ordine Commercialisti Trapani
- Siti remoti: Remote.co, Working Nomads, We Work Remotely, FlexJobs

## Personalizzazione

Modifica `config.py` per:
- `PROFILE`: i tuoi dati personali
- `SEARCH_TERMS`: termini di ricerca su LinkedIn/Indeed
- `GOOGLE_SEARCH_TERMS`: termini per Google Jobs
- `SUBITO_SEARCHES`: ricerche su Subito.it (in `scrapers/subito_it.py`)
- `CONCORSI_SITES`: portali concorsi da monitorare
- `PROFILE_KEYWORDS_SCORES`: keyword e punteggi per lo scoring
- `EXCLUDE_KEYWORDS_TITLE/TEXT`: cosa escludere