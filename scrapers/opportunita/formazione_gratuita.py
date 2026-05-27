"""
Scraper per Opportunità Giovani 18-35 — Trapani / Sicilia
Cerca:
- Corsi di formazione gratuiti finanziati da UE, Regione, privati
- Corsi di inglese gratuiti o finanziati
- Bandi e contributi per giovani (bonus studio, affitto, assunzioni)
- Opportunità UE finanziate (Erasmus+, Corpo Solidarietà, DiscoverEU)
- Tirocini formativi retribuiti
- Agevolazioni studio universitario

TUTTE le opportunità sono per DIPLOMATI / under 35 / senza requisiti di laurea
"""

import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger("JobHunter.Opportunita")


def scrape_opportunita() -> pd.DataFrame:
    """
    Genera un report di opportunità per giovani 18-35 da config.OPPORTUNITA_SITES.
    Ogni opportunità ha: nome, tipo (formazione/inglese/bando/ue/tirocinio/universita),
    descrizione breve, url per approfondire.
    """
    from config import OPPORTUNITA_SITES
    
    logger.info("=" * 60)
    logger.info("OPPORTUNITÀ GIOVANI 18-35 — Formazione gratuita, Inglese, Bandi, UE")
    logger.info("=" * 60)
    
    results = []
    
    for site in OPPORTUNITA_SITES:
        name = site["name"]
        tipo = site["tipo"]
        url = site["url"]
        descrizione = site.get("descrizione", "")
        
        # Categorizza
        tipo_label = {
            "formazione": "🎓 Formazione Gratuita Finanziata",
            "inglese": "🇬🇧 Inglese Gratuito / Finanziato",
            "bando": "💰 Bandi e Contributi per Giovani",
            "ue": "🌍 Opportunità Unione Europea",
            "tirocinio": "💼 Tirocini Retribuiti",
            "universita": "📚 Agevolazioni Studio Universitario",
        }.get(tipo, tipo)
        
        # Determina località
        if "sicilia" in descrizione.lower() or "sicilia" in name.lower() or "er su" in name.lower() or "unipa" in name.lower():
            location = "Sicilia"
        elif "ue" in tipo or "europe" in name.lower() or "erasmus" in name.lower() or "eu" in name.lower():
            location = "Europa"
        else:
            location = "Italia"
        
        results.append({
            "title": name,
            "company": tipo_label,
            "location": location,
            "search_country": location,
            "job_url": url,
            "official_url": url,
            "description": descrizione,
            "site": url.replace("https://", "").replace("http://", "").split("/")[0],
            "source_type": "opportunita_giovani",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
            "opportunita_tipo": tipo,
            "opportunita_tipo_label": tipo_label,
        })
        
        logger.info(f"  ✅ {tipo_label}: {name} - {url}")
    
    if not results:
        logger.info("Nessuna opportunità configurata")
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    logger.info(f"\n✅ TOTALE OPPORTUNITÀ: {len(df)}")
    
    # Statistiche per tipo
    for tipo in df["opportunita_tipo_label"].unique():
        count = (df["opportunita_tipo_label"] == tipo).sum()
        logger.info(f"   {tipo}: {count}")
    
    logger.info("=" * 60)
    return df