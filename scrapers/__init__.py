"""Scrapers per il bot di ricerca lavoro — Profilo Back Office / Ragioneria Trapani"""
from scrapers.subito_it import scrape_subito
from scrapers.concorsi_pubblici import scrape_concorsi
from scrapers.agenzie_lavoro import scrape_agenzie_lavoro

__all__ = ["scrape_subito", "scrape_concorsi", "scrape_agenzie_lavoro"]