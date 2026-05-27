# 📖 GUIDA COMPLETA ALLA CONFIGURAZIONE — Job Hunter Bot

## Profilo: Back Office / Ragioneria — Diplomato AFM — Trapani

---

## 📋 SOMMARIO

1. [Cos'è questo bot](#1-cosè-questo-bot)
2. [Come attivare il Bot Telegram](#2-come-attivare-il-bot-telegram)
3. [Installazione locale (sul tuo PC)](#3-installazione-locale-sul-tuo-pc)
4. [Configurazione GitHub Actions (automatico ogni giorno)](#4-configurazione-github-actions-automatico-ogni-giorno)
5. [Aggiungere la chiave API Mistral (opzionale ma consigliato)](#5-aggiungere-la-chiave-api-mistral-opzionale-ma-consigliato)
6. [Test manuale del bot](#6-test-manuale-del-bot)
7. [Personalizzare il bot](#7-personalizzare-il-bot)
8. [Risoluzione problemi](#8-risoluzione-problemi)

---

## 1. COS'È QUESTO BOT

Questo bot cerca automaticamente **lavoro per te** ogni giorno alle 08:00 su:

| Fonte | Cosa cerca |
|---|---|
| ✅ **Subito.it** | Annunci a Trapani e provincia (massima priorità) |
| ✅ **LinkedIn** | Offerte back office, contabilità, part-time |
| ✅ **Indeed** | Offerte in tutta Italia |
| ✅ **Google Jobs** | Offerte smart working e remote |
| ✅ **Adecco, Manpower, Randstad, Gi Group, Openjobmetis, Synergie, Humangest** | Annunci a Trapani e Smart Working |
| ✅ **Concorsi Pubblici** | Solo quelli accessibili con Diploma Ragioneria AFM (cat. C/D) |
| ✅ **Opportunità Giovani** | Formazione gratuita, corsi inglese gratis, bandi, Erasmus+ |

Alla fine ti invia un **report su Telegram** con le migliori offerte + un **file Excel** completo.

---

## 2. COME ATTIVARE IL BOT TELEGRAM

### Passo 1: Apri Telegram e cerca @BotFather

1. Apri Telegram
2. Cerca **@BotFather** (è il bot ufficiale di Telegram per creare bot)
3. Avvia la chat con **Avvia** / **Start**

### Passo 2: Crea il tuo bot

Scrivi questo comando a @BotFather:

```
/newbot
```

Ti chiederà:

- **Nome del bot**: scrivi un nome a piacere, ad esempio `Job Hunter Trapani`
- **Username del bot**: deve finire con `bot`, ad esempio `JobHunterTrapaniBot`

@BotFather ti risponderà con un messaggio che contiene il tuo **token** personale.

✅ **Quello è il tuo TELEGRAM_BOT_TOKEN** — dovrai inserirlo nei Secrets di GitHub!

### Passo 3: Ottieni il tuo Chat ID

1. Cerca il tuo bot su Telegram (es. `@JobHunterTrapaniBot`)
2. Avvia il bot con **Avvia** / **Start**
3. Scrivi un messaggio qualsiasi (es. "ciao")
4. Poi apri nel browser questo link (cambia `IL_TUO_TOKEN` con quello del tuo bot):

```
https://api.telegram.org/botIL_TUO_TOKEN/getUpdates
```

5. Nel risultato cerca `"chat":{"id":` — il numero dopo è il **TELEGRAM_CHAT_ID**

Esempio di risposta:
```json
{"ok":true,"result":[{"update_id":123,"message":{"message_id":1,"from":{"id":6239270170,...},"chat":{"id":6239270170,...}}}]}
```

✅ **Chat ID** in questo esempio: `6239270170`

### Passo 4: Inserisci il Chat ID in config.py

Apri `config.py` e verifica che sia vuoto (i token NON vanno scritti qui per sicurezza):

```python
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")   # Vuoto di default
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")       # Inserisci nei Secrets
```

---

## 3. INSTALLAZIONE LOCALE (sul tuo PC)

### Passo 1: Installa Python

1. Vai su https://www.python.org/downloads/
2. Scarica **Python 3.10 o superiore**
3. Durante l'installazione, **spunta** ✅ "Add Python to PATH"
4. Verifica aprire CMD e digitare:
```bash
python --version
```
Dovresti vedere: `Python 3.10.x`

### Passo 2: Scarica il progetto

Se non l'hai già fatto, clona o scarica il progetto in una cartella.

### Passo 3: Installa le dipendenze

Apri CMD/Terminale nella cartella del progetto ed esegui:

```bash
pip install -r requirements.txt
```

### Passo 4: Avvia il bot manualmente

```bash
python job_hunter.py
```

Vedrai i log scorrere mentre cerca offerte. Alla fine riceverai il report su Telegram.

---

## 4. CONFIGURAZIONE GITHUB ACTIONS (AUTOMATICO OGNI GIORNO)

Così il bot gira **da solo ogni mattina alle 08:00** senza che tu debba fare nulla.

### Passo 1: Carica il progetto su GitHub

Se non hai un account GitHub: https://github.com/signup → registrati (gratis)

Poi:
1. Vai su https://github.com/new
2. Crea un nuovo repository (es. `job-hunter-bot`)
3. Carica tutto il progetto (già fatto ✅):
```bash
git remote add origin https://github.com/Andreatp00/job-andrea-carini.git
git push -u origin master
```

🔗 **URL repository**: https://github.com/Andreatp00/job-andrea-carini

### Passo 2: Aggiungi i Secrets su GitHub

I Secrets sono come "password segrete" che il bot usa per funzionare su GitHub.

1. Vai sul tuo repository su GitHub
2. Clicca su **Settings** (in alto)
3. Nel menu a sinistra, clicca su **Secrets and variables → Actions**
4. Clicca su **New repository secret**

Aggiungi TUTTI questi secrets (uno alla volta):

| Nome Secret | Valore | Obbligatorio? |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Il token che ti ha dato @BotFather | ✅ SÌ |
| `TELEGRAM_CHAT_ID` | Il tuo chat ID (es. `6239270170`) | ✅ SÌ |
| `OPENAI_API_KEY` | La tua chiave Mistral/OpenAI (se ce l'hai) | ❌ No (opzionale) |
| `EMAIL_SENDER` | La tua email Gmail | ❌ No (opzionale) |
| `EMAIL_APP_PASSWORD` | Password app Gmail | ❌ No (opzionale) |
| `EMAIL_RECIPIENT` | La tua email dove ricevere il report | ❌ No (opzionale) |
| `MISTRAL_MODEL` | `open-mixtral-8x7b` (o altro modello) | ❌ No (opzionale) |

### Passo 3: Attiva GitHub Actions

1. Vai sulla tab **Actions** del tuo repository: https://github.com/Andreatp00/job-andrea-carini/actions
2. Clicca su **"I understand my workflows, go ahead and enable them"**
3. Vedrai il workflow `Job Hunter Bot - Ricerca Giornaliera`

✅ **Ora il bot girerà automaticamente ogni giorno alle 08:00 UTC (09:00 ora italiana) o alle 08:00 in inverno**

### Passo 4: Test manuale

Per testare SUBITO se funziona:
1. Vai su **Actions → Job Hunter Bot → Run workflow** (pulsante a destra)
2. Clicca **Run workflow** → **Run**
3. Aspetta che finisca (ci mette qualche minuto)
4. Controlla Telegram: riceverai il report!

---

## 5. AGGIUNGERE LA CHIAVE API MISTRAL (OPZIONALE MA CONSIGLIATO)

Se vuoi che il bot usi l'AI per ordinare meglio le offerte, ti serve una chiave API Mistral.

### Passo 1: Configura la chiave nei Secrets

La chiave API Mistral **NON va scritta in config.py** per sicurezza, ma va inserita nei Secrets di GitHub:

```python
MISTRAL_API_KEY = os.environ.get("OPENAI_API_KEY", "")   # Vuoto di default, viene dai Secrets
```

### Passo 2: Ottieni una chiave Mistral (solo se ne vuoi una nuova)

1. Vai su https://console.mistral.ai/
2. Registrati (gratis, ricevi crediti iniziali)
3. Vai su **API Keys** → **Create new key**
4. Copia la chiave (inizia con `sk-...`)

### Passo 3: Aggiungila su GitHub (SENZA committare il file config.py)

⚠️ **ATTENZIONE**: La chiave in `config.py` funziona per esecuzione locale, ma per GitHub Actions devi usare i Secrets per sicurezza.

1. Vai su **Settings → Secrets and variables → Actions**
2. Aggiungi:
   - **OPENAI_API_KEY** = La tua chiave Mistral (es. ``)
   - **MISTRAL_MODEL** = `open-mixtral-8x7b` (o `mistral-small-latest`)

### Passo 4: Test

Riavvia il workflow su GitHub Actions. Il bot userà l'AI per riordinare le migliori offerte per te.

Il bot userà il modello Mistral per analizzare e riordinare le offerte secondo questi criteri:
- ✅ **Pertinenza** per il tuo profilo di diplomato Ragioneria AFM
- ✅ **Zona geografica** (Trapani > Sicilia > Smart Working)
- ✅ **Tipo di contratto** (part-time, stage, tempo determinato)
- 🏆 **Score finale** combinato: 60% regole manuali + 40% AI ranking

---

## 6. TEST MANUALE DEL BOT

### Test rapido locale (sul tuo PC)
```bash
cd "C:\Users\carin\Desktop\job-2.0--main"
python job_hunter.py
```

### Test su GitHub Actions
1. Vai sul repository su GitHub
2. Tab **Actions** → **Job Hunter Bot** → **Run workflow**
3. Aspetta il completamento (5-10 minuti)
4. Controlla Telegram

---

## 7. PERSONALIZZARE IL BOT

### Apri `config.py` e modifica:

#### ✅ Il tuo nome (riga ~20)
```python
PROFILE = {
    "name": "IL TUO NOME",   # ← Inserisci qui il tuo nome
    ...
}
```

#### ✅ Le tue competenze (se vuoi aggiungerne)
Trova `"soft_skills"` e aggiungi le tue.

#### ✅ I termini di ricerca
Trova `SEARCH_TERMS` e aggiungi/modifica le ricerche.

#### ✅ I siti da cui cercare
Trova `COMPANY_CAREER_SITES` e aggiungi altri datori di lavoro.

#### ✅ Le opportunità giovani
Trova `OPPORTUNITA_SITES` e aggiungi altre opportunità che conosci.

---

## 8. RISOLUZIONE PROBLEMI

### ❌ Non ricevo il messaggio su Telegram
- Controlla che `TELEGRAM_CHAT_ID` sia corretto
- Controlla che il bot sia stato avviato (manda un messaggio al bot prima)
- Controlla i log su GitHub Actions

### ❌ Il bot non trova offerte
- Assicurati di avere installato `jobspy`: `pip install -r requirements.txt`
- Prova a eseguirlo localmente per vedere gli errori nei log
- Controlla la connessione internet

### ❌ GitHub Actions fallisce
- Controlla la tab **Actions** → clicca sul workflow fallito → vedi i log
- Assicurati di aver aggiunto TUTTI i secrets necessari
- Almeno `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` devono essere presenti

### ❌ Errore "Python non trovato"
- Hai installato Python? Scarica da python.org
- Hai spuntato "Add Python to PATH" durante l'installazione?

---

## 📊 COSA RICEVERAI OGNI GIORNO

1. **Messaggio Telegram** con le prime 10 offerte migliori
2. **File Excel** (inviato su Telegram) con:
   - **Top_Match** — offerte migliori (score ≥ 70)
   - **All_Relevant** — tutte le offerte valide
   - **Borderline** — offerte da valutare (score 35-69)
   - **Esclusi_Audit** — offerte escluse con motivo
   - **Tracker_Candidature** — tabella per tracciare a cosa ti sei candidato
3. **Opportunità Giovani** — formazione gratuita, corsi inglese, bandi

---

## 🔐 INFORMAZIONI SENSIBILI

⚠️ **NON condividere MAI**:
- Il token del bot Telegram
- Il tuo Chat ID
- Le chiavi API

Questi dati sono già nel file `.gitignore` e non vengono caricati su GitHub (vengono passati come Secrets).

---

## 💬 SUPPORTO

Se hai problemi:
1. Controlla i log nella cartella `logs/`
2. Esegui localmente e guarda gli errori
3. Rileggi questa guida

---

🎉 **Ora il bot è pronto! Ogni mattina riceverai le migliori offerte di lavoro per te!**

*Buona ricerca! 🚀*