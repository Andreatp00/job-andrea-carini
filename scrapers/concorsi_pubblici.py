"""
Scraper per Concorsi Pubblici — PA, Enti Locali, Sicilia
CERCA SPECIFICAMENTE concorsi accessibili con DIPLOMA RAGIONERIA AFM.
Controlla:
- Categoria C e D (accessibili con diploma)
- Profili amministrativi / contabili
- Istruttore amministrativo, funzionario amministrativo (categoria D)
- NESSUN concorso che richiede laurea
"""

import logging
import re
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("JobHunter.Concorsi")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
}

# --- KEYWORD PER CONCORSI ADATTI A DIPLOMA RAGIONERIA ---
# Titoli di studio richiesti per accesso
TITOLI_RAGIONERIA = [
    "ragioneria", "perito commerciale", "afm", "amministrazione finanza marketing",
    "istituto tecnico commerciale", "istituto tecnico economico", "itc",
    "diploma", "diplomato", "maturità", "maturità commerciale",
    "scuola secondaria superiore", "istruzione secondaria superiore",
    "diploma di scuola media superiore",
]

# Categorie e profili accessibili con diploma
CATEGORIE_DIPLOMA = [
    "categoria c", "cat. c", "cat c", "categoria d", "cat. d", "cat d",
    "istruttore", "istruttore amministrativo", "istruttore contabile",
    "istruttore direttivo", "istruttore amministrativo contabile",
    "funzionario amministrativo", "funzionario contabile",
    "collaboratore amministrativo", "collaboratore contabile",
    "assistente amministrativo", "operatore amministrativo",
    "impiegato amministrativo", "impiegato contabile",
    "addetto amministrativo", "addetto contabile",
    "esecutore amministrativo", "esecutore contabile",
]

# Profili specifici ragioneria
PROFILI_RAGIONERIA = [
    "ragioneria", "contabile", "bilancio", "partita doppia", "iva",
    "imposte", "tributi", "economato", "economico finanziario",
    "finanziario", "amministrativo contabile", "fiscalità",
    "personale", "amministrazione del personale", "stipendi",
    "contabilità pubblica", "ragioneria comunale", "ragioneria provinciale",
]

# Esclusioni: concorsi NON accessibili con diploma
ESCLUSIONI = [
    "laurea", "laurea magistrale", "laurea triennale", "laurea specialistica",
    "dottorato", "phd", "master universitario",
    "ingegnere", "architetto", "medico", "infermiere", "veterinario",
    "farmacista", "biologo", "chimico", "geologo",
    "professore", "docente", "insegnante", "educatore professionale",
    "assistente sociale", "psicologo",
    "operaio", "autista", "autista di autobus", "idraulico", "elettricista",
    "militare", "polizia", "carabiniere", "vigile del fuoco",
    "agente di polizia", "agente di custodia", "sorvegliante",
    "cuoco", "cameriere", "addetto alle pulizie",
    "dirigente", "dirigente amministrativo",
]

# Requisiti specifici per diploma
REQUISITI_DIPLOMA = [
    "diploma di ragioneria", "diploma di perito commerciale",
    "diploma di istituto tecnico commerciale", "diploma afm",
    "diploma di maturità commerciale", "ragioneria programmatore",
    "diploma quinquennale", "maturità quinquennale",
    "diploma di scuola secondaria superiore",
    "titolo di studio non inferiore al diploma",
    "almeno il diploma di scuola superiore",
    "possono partecipare i diplomati",
    "è richiesto il diploma",
]

# --- SITI CONCORSI DA MONITORARE CON URL SPECIFICI PER DIPLOMATI ---
CONCORSI_SITES_SPECIFIC = [
    {
        "name": "inPA - Categoria C",
        "url": "https://www.inpa.gov.it/bandi-e-avvisi/?q=categoria+C+istruttore+amministrativo",
        "query": "categoria C istruttore amministrativo",
        "site": "inpa.gov.it"
    },
    {
        "name": "inPA - Categoria D",
        "url": "https://www.inpa.gov.it/bandi-e-avvisi/?q=funzionario+amministrativo+diploma",
        "query": "funzionario amministrativo diploma",
        "site": "inpa.gov.it"
    },
    {
        "name": "inPA - Ragioneria",
        "url": "https://www.inpa.gov.it/bandi-e-avvisi/?q=ragioneria+contabile+amministrativo",
        "query": "ragioneria contabile amministrativo",
        "site": "inpa.gov.it"
    },
    {
        "name": "inPA - Trapani",
        "url": "https://www.inpa.gov.it/bandi-e-avvisi/?q=Trapani+istruttore+amministrativo",
        "query": "Trapani istruttore amministrativo",
        "site": "inpa.gov.it"
    },
    {
        "name": "inPA - Sicilia diplomati",
        "url": "https://www.inpa.gov.it/bandi-e-avvisi/?q=Sicilia+diplomati+categoria+C",
        "query": "Sicilia diplomati categoria C",
        "site": "inpa.gov.it"
    },
    {
        "name": "Concorsi.it - Categoria C",
        "url": "https://www.concorsi.it/ricerca?keyword=categoria+C+istruttore+amministrativo&area_geografica=Sicilia",
        "query": "categoria C istruttore amministrativo Sicilia",
        "site": "concorsi.it"
    },
    {
        "name": "Concorsi.it - Diplomati",
        "url": "https://www.concorsi.it/ricerca?keyword=diplomati+ragioneria+amministrativo",
        "query": "diplomati ragioneria amministrativo",
        "site": "concorsi.it"
    },
    {
        "name": "Sicilia Concorsi - Categoria C",
        "url": "https://www.siciliaconcorsi.it/ricerca/?q=categoria+c+istruttore",
        "query": "categoria c istruttore",
        "site": "siciliaconcorsi.it"
    },
    {
        "name": "Sicilia Concorsi - Diplomati",
        "url": "https://www.siciliaconcorsi.it/ricerca/?q=diplomati+ragioneria",
        "query": "diplomati ragioneria",
        "site": "siciliaconcorsi.it"
    },
    {
        "name": "ASL Trapani - Concorsi",
        "url": "https://www.asptrapani.it/concorsi/",
        "query": "concorsi diplomati amministrativi",
        "site": "asptrapani.it"
    },
    {
        "name": "Gazzetta Ufficiale - Concorsi",
        "url": "https://www.gazzettaufficiale.it/concorsi/cerca",
        "query": "diploma istituto tecnico commerciale",
        "site": "gazzettaufficiale.it"
    },
    {
        "name": "Agenzia Entrate - Concorsi",
        "url": "https://www.agenziaentrate.gov.it/wps/content/Nsilib/Nsi/Concorsi/",
        "query": "diplomati funzionario amministrativo",
        "site": "agenziaentrate.gov.it"
    },
    {
        "name": "INPS Concorsi",
        "url": "https://www.inps.it/it/it/concorsi.html",
        "query": "diplomati istruttore amministrativo INPS",
        "site": "inps.it"
    },
    {
        "name": "Regione Sicilia - Concorsi",
        "url": "https://pit.regione.sicilia.it/concorsi/",
        "query": "diplomati categoria C Regione Sicilia",
        "site": "regione.sicilia.it"
    },
    {
        "name": "Comune Trapani - Bandi",
        "url": "https://www.comune.trapani.it/bandi-di-concorso/",
        "query": "concorso diplomati istruzione pubblica Trapani",
        "site": "comune.trapani.it"
    },
    {
        "name": "InPA - Part-time PA",
        "url": "https://www.inpa.gov.it/bandi-e-avvisi/?q=part+time+diplomati+amministrativo",
        "query": "part time diplomati amministrativo",
        "site": "inpa.gov.it"
    },
]


def _check_diploma_compatibile(title: str, full_text: str) -> tuple[bool, str]:
    """
    Verifica se un concorso è ACCESSIBILE con DIPLOMA RAGIONERIA AFM.
    Restituisce (compatibile, motivazione).
    """
    text = f"{title} {full_text}".lower()
    
    # 1. ESCLUDI se richiede LAUREA
    # Pattern: "laurea ... richiesta", "titolo di studio: laurea", "laurea in ..."
    if re.search(r"\blaurea\b.{0,40}\b(richiest[ao]|necessari[ao]|obbligatori[ao]|indispensabile|requisito)\b", text):
        return (False, "richiede_laurea")
    
    # Se dice "laurea triennale" o "laurea magistrale" senza eccezioni
    if re.search(r"\blaurea\s*(triennale|magistrale|specialistica)\b", text):
        return (False, "richiede_laurea_triennale_magistrale")
    
    # "titolo di studio: laurea" (non seguito da "o diploma")
    if re.search(r"titolo\s+di\s+studio\s*[:;]\s*laurea\b", text) and not re.search(r"titolo\s+di\s+studio\s*[:;].{0,30}(diploma|maturità)", text):
        return (False, "titolo_di_studio_laurea")
    
    # 2. VERIFICA se il concorso è per diploma
    # Cerca "categoria C" o "categoria D" (tipiche per diplomati)
    cat_c_d = re.search(r"\bcategoria\s*[cd]\b|\bcat\.?\s*[cd]\b", text)
    
    # Cerca profili specifici ragioneria
    profilo_ragioneria = any(p in text for p in PROFILI_RAGIONERIA)
    
    # Cerca "istruttore amministrativo" e simili
    profilo_amm = any(p in text for p in CATEGORIE_DIPLOMA)
    
    # Cerca titolo di studio richiesto: diploma
    richiede_diploma = any(t in text for t in REQUISITI_DIPLOMA)
    
    # Cerca esclusioni
    escluso = any(e in text for e in ESCLUSIONI)
    if escluso:
        return (False, "ruolo_escluso")
    
    # 3. DECISIONE
    if cat_c_d and not escluso:
        return (True, "categoria_C_D_diploma")
    
    if (profilo_ragioneria or profilo_amm) and not escluso and not re.search(r"\blaurea\b", text):
        return (True, "profilo_amministrativo")
    
    if richiede_diploma and not escluso and not re.search(r"\blaurea\b", text):
        return (True, "richiede_diploma")
    
    # Se non c'è menzione né di laurea né di diploma né di categoria C/D
    # ma il titolo sembra amministrativo e non esclude diplomati
    if not escluso and not re.search(r"\blaurea\b", text) and not re.search(r"\bdottorato\b|\bphd\b", text):
        if any(t in text for t in ["amministrativo", "contabile", "ragioneria", "bilancio", "tributi", "imposte", "economato"]):
            return (True, "probabile_per_diplomati")
    
    return (False, "non_chiaro_o_non_compatibile")


def _parse_concorso_element(el, base_url: str, site_name: str, query: str) -> dict | None:
    """
    Estrae informazioni da un elemento HTML di un concorso.
    """
    # Estrai titolo
    title_el = el.find(["h2", "h3", "h4", "a", "p", "span", "strong"], class_=re.compile(r"title|titolo|name|nome|heading"))
    if not title_el:
        title_el = el.find(["a", "h2", "h3", "h4"])
    if not title_el:
        return None
    
    title = title_el.get_text(" ", strip=True)
    if not title or len(title) < 15:
        # Prova con tutto il testo dell'elemento
        title = el.get_text(" ", strip=True)
        if not title or len(title) < 15:
            return None
    
    # Estrai link
    link = el if el.name == "a" and el.get("href") else el.find("a", href=True)
    href = ""
    if link and hasattr(link, "get"):
        href = link.get("href", "")
        if href and not href.startswith("http"):
            if href.startswith("/"):
                # Estrai dominio base
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                href = f"{parsed.scheme}://{parsed.netloc}{href}"
            else:
                href = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
    
    # Testo completo dell'elemento per analisi
    full_text = el.get_text(" ", strip=True)
    
    # Verifica compatibilità con diploma ragioneria
    compatibile, motivo = _check_diploma_compatibile(title, full_text)
    if not compatibile:
        return None
    
    # Estrai località
    location_guess = "Italia"
    full_lower = full_text.lower()
    
    # Cerca città siciliane / Trapani
    for city in ["trapani", "palermo", "catania", "messina", "siracusa", "ragusa", "agrigento", "enna", "caltanissetta"]:
        if city in full_lower:
            location_guess = city.title()
            break
    
    if location_guess == "Italia" and "sicilia" in full_lower:
        location_guess = "Sicilia"
    if location_guess == "Italia":
        # Cerca città italiane non siciliane
        italian_cities = ["roma", "milano", "napoli", "torino", "bari", "firenze", "bologna", "venezia", "genova", "verona", "padova", "trieste", "perugia", "l'aquila", "cagliari", "ancona", "potenza", "campobasso"]
        for city in italian_cities:
            if city in full_lower:
                location_guess = city.title()
                break
    
    # Determina la zona per il report
    if location_guess in ["Trapani", "Palermo", "Catania", "Messina", "Siracusa", "Ragusa", "Agrigento", "Enna", "Caltanissetta"]:
        search_country = "Sicilia"
    elif location_guess in ["Roma", "Milano", "Napoli"]:
        search_country = "Italia"
    else:
        search_country = "Italia"
    
    # Estrai ente
    ente = site_name
    ente_match = re.search(r"(comune|provincia|regione|asl|inps|agenzia|ministero|azienda sanitaria|consiglio|autorità|camera|corte)\s+(?:di\s+|della\s+|dell[' ])?([a-zàèéìòù\s]+?)(?:\s|,|\.|–|-|$)", full_lower)
    if ente_match:
        ente = f"{ente_match.group(1).title()} {ente_match.group(2).title()}".strip()
    
    return {
        "title": title[:300],
        "company": ente,
        "location": location_guess,
        "search_country": search_country,
        "job_url": href or base_url,
        "official_url": href or base_url,
        "description": f"Concorso Pubblico | {site_name} | compatibile: diploma ragioneria AFM | {full_text[:300]}",
        "site": base_url.replace("https://", "").replace("http://", "").split("/")[0],
        "source_type": "concorso_pubblico",
        "date_posted": datetime.now().strftime("%Y-%m-%d"),
        "concorso_motivo": motivo,
    }


def scrape_concorsi() -> pd.DataFrame:
    """
    Scraping dei principali portali di concorsi pubblici.
    CERCA SOLO CONCORSI ACCESSIBILI CON DIPLOMA RAGIONERIA AFM.
    """
    logger.info("=" * 60)
    logger.info("SCRAPING CONCORSI PUBBLICI — Solo per Diplomati Ragioneria AFM")
    logger.info("=" * 60)
    
    all_results = []
    
    for site_cfg in CONCORSI_SITES_SPECIFIC:
        site_name = site_cfg["name"]
        url = site_cfg["url"]
        query = site_cfg.get("query", "")
        
        logger.info(f"🔍 {site_name}: {query}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=25)
            if response.status_code != 200:
                logger.warning(f"  ❌ HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Cerca elementi che sembrano bandi/concorsi
            # Prova vari selettori CSS comuni
            selectors = [
                "a[href*='bando']", "a[href*='concorso']", "a[href*='avviso']",
                "div[class*='bando']", "div[class*='concorso']", "div[class*='avviso']",
                "article[class*='bando']", "article[class*='concorso']",
                "tr[class*='bando']", "tr[class*='concorso']",
                "div.card", "div.item", "li.list-item",
                "div[class*='risultato']", "div[class*='result']",
                "table tr", ".listing tr",
            ]
            
            found_elements = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    found_elements = elements
                    logger.info(f"  📦 Selettore '{selector}': {len(elements)} elementi")
                    break
            
            if not found_elements:
                # Fallback: cerca tutti i link
                found_elements = soup.find_all("a", href=True)
                logger.info(f"  📦 Fallback: {len(found_elements)} link totali")
            
            batch_results = []
            for el in found_elements:
                parsed = _parse_concorso_element(el, url, site_name, query)
                if parsed:
                    batch_results.append(parsed)
            
            # Deduplica per titolo + url
            seen_keys = set()
            unique_results = []
            for item in batch_results:
                key = f"{item['title'][:100]}|{item['job_url']}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    unique_results.append(item)
            
            all_results.extend(unique_results)
            logger.info(f"  ✅ {len(unique_results)} concorsi compatibili con Diploma Ragioneria AFM")
            
        except Exception as exc:
            logger.warning(f"  ❌ Errore {site_name}: {exc}")
        
        time.sleep(2)
    
    if not all_results:
        logger.info("⚠️ Nessun concorso pubblico trovato per Diploma Ragioneria AFM")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_results)
    # Deduplica finale
    df = df.drop_duplicates(subset=["title", "job_url"])
    
    logger.info(f"\n{'=' * 60}")
    logger.info(f"✅ TOTALE CONCORSI COMPATIBILI: {len(df)}")
    
    # Statistiche per località
    for loc in df["search_country"].value_counts().index:
        count = (df["search_country"] == loc).sum()
        logger.info(f"   {loc}: {count}")
    
    # Statistiche per motivo compatibilità
    for motivo in df["concorso_motivo"].value_counts().index:
        count = (df["concorso_motivo"] == motivo).sum()
        logger.info(f"   Tipo '{motivo}': {count}")
    
    logger.info(f"{'=' * 60}")
    return df