"""
Scraper per Agenzie per il Lavoro — Ricerca annunci amministrativi part-time
Cerca su Adecco, Manpower, Randstad, Gi Group, Openjobmetis, Synergie, Humangest
con focus su Trapani, Sicilia e Smart Working.
"""

import logging
import re
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("JobHunter.Agenzie")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
}

# Configurazioni delle agenzie di lavoro da scrapare
AGENCY_CONFIGS = [
    {
        "name": "Adecco",
        "search_url_trapani": "https://www.adecco.it/ricerca-lavoro/trapani/",
        "search_url_smart": "https://www.adecco.it/ricerca-lavoro/smart-working/",
        "keywords": ["amministrativo", "contabilità", "back office", "impiegato", "segreteria", "part-time"],
        "site_domain": "adecco.it",
    },
    {
        "name": "Manpower",
        "search_url_trapani": "https://www.manpower.it/cerca-lavoro/trapani/",
        "search_url_smart": "https://www.manpower.it/cerca-lavoro/smart-working/",
        "keywords": ["amministrativo", "contabilità", "back office", "impiegato", "part-time"],
        "site_domain": "manpower.it",
    },
    {
        "name": "Randstad",
        "search_url_trapani": "https://www.randstad.it/trovare-lavoro/trapani/",
        "search_url_smart": "https://www.randstad.it/trovare-lavoro/smart-working/",
        "keywords": ["amministrativo", "contabilità", "back office", "impiegato", "segreteria", "part-time"],
        "site_domain": "randstad.it",
    },
    {
        "name": "Gi Group",
        "search_url_trapani": "https://www.gigroup.it/offerte-lavoro/trapani/",
        "search_url_smart": "https://www.gigroup.it/offerte-lavoro/remote/",
        "keywords": ["amministrativo", "contabilità", "back office", "impiegato", "part-time"],
        "site_domain": "gigroup.it",
    },
    {
        "name": "Openjobmetis",
        "search_url_trapani": "https://www.openjobmetis.it/offerte-lavoro/trapani/",
        "search_url_smart": "https://www.openjobmetis.it/offerte-lavoro/da-remoto/",
        "keywords": ["amministrativo", "contabilità", "back office", "impiegato", "part-time"],
        "site_domain": "openjobmetis.it",
    },
    {
        "name": "Synergie Italia",
        "search_url_trapani": "https://www.synergie-italia.it/offerte-di-lavoro/trapani/",
        "search_url_smart": "https://www.synergie-italia.it/offerte-di-lavoro/remote/",
        "keywords": ["amministrativo", "contabilità", "back office", "impiegato"],
        "site_domain": "synergie-italia.it",
    },
    {
        "name": "Humangest",
        "search_url_trapani": "https://www.humangest.it/cerca-lavoro/trapani/",
        "search_url_smart": "https://www.humangest.it/cerca-lavoro/remote/",
        "keywords": ["amministrativo", "contabilità", "back office", "impiegato", "segreteria"],
        "site_domain": "humangest.it",
    },
]

# Ruoli target per filtrare le descrizioni
TARGET_ROLE_KEYWORDS = [
    "amministrativo", "contabilità", "fatturazione", "back office", "segreteria",
    "impiegato", "ufficio", "commercialista", "contabile", "segreterio",
    "addetto", "assistente amministrativo", "praticante", "stage",
    "part-time", "tempo parziale", "mezza giornata",
    "customer service", "servizio clienti", "amministrazione",
    "ragioneria", "bilancio", "iva", "fatture", "ordini",
]

EXCLUDE_ROLE_KEYWORDS = [
    "operaio", "magazziniere", "cameriere", "barista", "cuoco",
    "pizzaiolo", "commesso", "venditore", "promoter", "autista",
    "elettricista", "idraulico", "manutenzione", "programmatore",
    "sviluppatore", "informatico", "tecnico informatico",
    "infermiere", "medico", "farmacista", "ingegnere",
]


def _parse_agency_page(html: str, agency_name: str, site_domain: str, location: str) -> list[dict]:
    """
    Parsa una pagina di agenzia di lavoro e cerca annunci pertinenti.
    Funzione generica adattabile a diverse strutture HTML.
    """
    results = []
    soup = BeautifulSoup(html, "html.parser")
    
    # Strategia 1: Cerca link con job title
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(" ", strip=True)
        
        if not text or len(text) < 10:
            continue
        
        text_lower = text.lower()
        
        # Deve contenere almeno un keyword target
        if not any(kw in text_lower for kw in TARGET_ROLE_KEYWORDS):
            continue
        
        # Non deve contenere keyword escluse
        if any(kw in text_lower for kw in EXCLUDE_ROLE_KEYWORDS):
            continue
        
        # Completa URL
        if href.startswith("/"):
            href = f"https://www.{site_domain}{href}"
        elif not href.startswith("http"):
            continue
        
        results.append({
            "title": text[:200],
            "company": agency_name,
            "location": location,
            "search_country": location,
            "job_url": href,
            "official_url": href,
            "description": f"{agency_name} | {text[:200]}",
            "site": site_domain,
            "source_type": "agenzia_lavoro",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
        })
    
    # Strategia 2: Cerca in articoli o card
    for item in soup.select("article, div[class*='job'], div[class*='card'], li[class*='job'], tr[class*='job'], div[class*='offerta']"):
        title_el = item.find(["h2", "h3", "h4", "a", "p", "span"])
        link_el = item.find("a", href=True)
        
        if not title_el or not link_el:
            continue
        
        title = title_el.get_text(" ", strip=True)
        href = link_el.get("href", "")
        
        if not title or len(title) < 10:
            continue
        
        title_lower = title.lower()
        
        if not any(kw in title_lower for kw in TARGET_ROLE_KEYWORDS):
            continue
        if any(kw in title_lower for kw in EXCLUDE_ROLE_KEYWORDS):
            continue
        
        if href.startswith("/"):
            href = f"https://www.{site_domain}{href}"
        elif not href.startswith("http"):
            continue
        
        # Deduplica
        existing_titles = {r["title"] for r in results}
        if title[:200] in existing_titles:
            continue
        
        results.append({
            "title": title[:200],
            "company": agency_name,
            "location": location,
            "search_country": location,
            "job_url": href,
            "official_url": href,
            "description": f"{agency_name} | {title[:200]}",
            "site": site_domain,
            "source_type": "agenzia_lavoro",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
        })
    
    return results


def scrape_agenzie_lavoro() -> pd.DataFrame:
    """
    Scraping di tutte le agenzie per il lavoro configurate.
    Cerca annunci a Trapani e Smart Working.
    """
    logger.info("=== SCRAPING AGENZIE PER IL LAVORO ===")
    all_results = []
    
    for agency in AGENCY_CONFIGS:
        name = agency["name"]
        
        # Cerca a Trapani
        logger.info(f"Agenzia: {name} - Trapani")
        try:
            response = requests.get(agency["search_url_trapani"], headers=HEADERS, timeout=20)
            if response.status_code == 200:
                items = _parse_agency_page(response.text, name, agency["site_domain"], "Trapani")
                all_results.extend(items)
                logger.info(f"  -> Trapani: {len(items)} annunci")
            else:
                logger.warning(f"  -> HTTP {response.status_code}")
        except Exception as exc:
            logger.warning(f"  -> Errore Trapani: {exc}")
        
        time.sleep(1.5)
        
        # Cerca Smart Working
        logger.info(f"Agenzia: {name} - Smart Working")
        try:
            response = requests.get(agency["search_url_smart"], headers=HEADERS, timeout=20)
            if response.status_code == 200:
                items = _parse_agency_page(response.text, name, agency["site_domain"], "Italia (Smart Working)")
                all_results.extend(items)
                logger.info(f"  -> Smart Working: {len(items)} annunci")
            else:
                logger.warning(f"  -> HTTP {response.status_code}")
        except Exception as exc:
            logger.warning(f"  -> Errore Smart Working: {exc}")
        
        time.sleep(1.5)
    
    if not all_results:
        logger.info("Nessun annuncio trovato dalle agenzie per il lavoro")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_results)
    df = df.drop_duplicates(subset=["title", "company", "job_url"])
    logger.info(f"Agenzie lavoro: totale {len(df)} annunci unici")
    return df