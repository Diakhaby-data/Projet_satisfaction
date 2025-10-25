 # a) Importation des librairies
import re
import json
import time
import math
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup

SESSION = requests.Session()
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"
}

# Dictionnaire des domaines d'activité connus
DOMAINES = {
    "Mondial Relay": "Distribution de colis aux particuliers (Points Relais, lockers, livraison à domicile)",
    "Chronopost": "Transport express de colis, messagerie, livraison sous température dirigée",
    "DPD": "Transport routier de marchandises, commissionnaire de transport",
    "Colicoli": "Logistique du dernier kilomètre, affrètement, organisation transport, stockage, livraison à domicile",
    "COLIS PRIVE": "Livraison B2C du dernier kilomètre, relais, distribution de colis, marketing direct",
    "AR24": "Lettres recommandées électroniques qualifiées — solution numérique de confiance",
    "Colissimo - La Poste": "Livraison de colis Courrier & Express, logistique du dernier kilomètre, e-commerce",
    "Chronofresh": "Livraison express de produits alimentaires réfrigérés, commissionnaire de transport",
    "Shop2Shop by Chronopost": "Livraison en relais colis via Chronopost (alternative économique B2C)",
    "Carton Market": "Vente en ligne de cartons et emballages pour expédition et déménagement",
    "UPS": "Transport et logistique internationale, messagerie express et fret",
    "Shopopop": "Livraison collaborative entre particuliers (crowdshipping dernier kilomètre)",
    "DHL": "Transport et logistique internationale, fret aérien, maritime, routier",
    "Relais Colis": "Livraison de colis aux particuliers via un réseau de relais commerçants",
    "papernest": "Gestion administrative et contrats (énergie, internet, assurance, logement)",
    "La Poste": "Services postaux, courrier, colis, logistique, services financiers",
    "CartonsDeDemenagement.com": "Vente en ligne de cartons et fournitures de déménagement",
    "ColisExpat": "Réexpédition internationale de colis et achats en ligne français",
    "Cubyn": "Logistique e-commerce, préparation et expédition automatisée",
    "LOCABOX": "Location de box de stockage sécurisés et garde-meubles",
}

# Liste des 20 URLs avec le nom cible
URLS = [
    ("https://fr.trustpilot.com/review/mondialrelay.fr", "Mondial Relay"),
    ("https://fr.trustpilot.com/review/www.chronopost.fr", "Chronopost"),
    ("https://fr.trustpilot.com/review/dpd.fr", "DPD"),
    ("https://fr.trustpilot.com/review/colicoli.fr", "Colicoli"),
    ("https://fr.trustpilot.com/review/colispriv%C3%A9.fr", "COLIS PRIVE"),
    ("https://fr.trustpilot.com/review/ar24.fr", "AR24"),
    ("https://fr.trustpilot.com/review/www.colissimo.fr", "Colissimo - La Poste"),
    ("https://fr.trustpilot.com/review/chronofresh.fr", "Chronofresh"),
    ("https://fr.trustpilot.com/review/www.chronoshop2shop.fr", "Shop2Shop by Chronopost"),
    ("https://fr.trustpilot.com/review/cartonmarket.fr", "Carton Market"),
    ("https://fr.trustpilot.com/review/www.ups.fr", "UPS"),
    ("https://fr.trustpilot.com/review/www.shopopop.com", "Shopopop"),
    ("https://fr.trustpilot.com/review/www.dhl.com", "DHL"),
    ("https://fr.trustpilot.com/review/www.relaiscolis.com", "Relais Colis"),
    ("https://fr.trustpilot.com/review/papernest.com", "papernest"),
    ("https://fr.trustpilot.com/review/www.laposte.fr", "La Poste"),
    ("https://fr.trustpilot.com/review/www.cartonsdedemenagement.com", "CartonsDeDemenagement.com"),
    ("https://fr.trustpilot.com/review/www.colisexpat.com", "ColisExpat"),
    ("https://fr.trustpilot.com/review/cubyn.com", "Cubyn"),
    ("https://fr.trustpilot.com/review/locabox.fr", "LOCABOX"),
]

def _req(url, tries=3, backoff=1.4):
    err = None
    for i in range(tries):
        try:
            r = SESSION.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                return r
            err = Exception(f"HTTP {r.status_code}")
        except Exception as e:
            err = e
        time.sleep((backoff ** i) + random.uniform(0, 0.5))
    raise err

def _to_float_safe(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x)
    s = s.replace("\u202f", "").replace("\xa0", "").replace(" ", "")
    s = s.replace(",", ".")
    m = re.search(r"[-+]?\d*\.?\d+", s)
    return float(m.group(0)) if m else None

def _to_int_safe(x):
    if x is None:
        return None
    if isinstance(x, (int, float)) and not math.isnan(x):
        return int(x)
    s = str(x)
    s = s.replace("\u202f", "").replace("\xa0", "").replace(" ", "")
    m = re.findall(r"\d+", s)
    return int("".join(m)) if m else None

def _find_first(d, key):
    """Recherche récursive d’une clé dans un JSON imbriqué."""
    if isinstance(d, dict):
        if key in d:
            return d[key]
        for v in d.values():
            res = _find_first(v, key)
            if res is not None:
                return res
    elif isinstance(d, list):
        for v in d:
            res = _find_first(v, key)
            if res is not None:
                return res
    return None

def _json_from_page(soup):
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None
    try:
        return json.loads(tag.string)
    except Exception:
        return None

def _percentages_from_json(breakdown):
    # breakdown attendu: {excellent, great, average, poor, bad} → valeurs = comptes
    total = sum(breakdown.values()) or 1
    return {
        "excellent_%": round(breakdown.get("excellent", 0) * 100 / total, 2),
        "tres_bon_%": round(breakdown.get("great", 0) * 100 / total, 2),
        "moyen_%": round(breakdown.get("average", 0) * 100 / total, 2),
        "mediocre_%": round(breakdown.get("poor", 0) * 100 / total, 2),
        "horrible_%": round(breakdown.get("bad", 0) * 100 / total, 2),
    }

def _percentages_from_html(soup):
    # On lit la table latérale : <label ... data-star-rating="five|four|three|two|one">
    rows = soup.select("label.styles_row__4BwV6")
    mapping = {"five": "excellent_%", "four": "tres_bon_%", "three": "moyen_%", "two": "mediocre_%", "one": "horrible_%"}
    perc = {v: None for v in mapping.values()}

    for row in rows:
        star = row.get("data-star-rating", "").strip()
        pct_tag = row.select_one("p[data-rating-distribution-row-percentage-typography='true']")
        if star in mapping and pct_tag:
            perc[mapping[star]] = _to_float_safe(pct_tag.get_text(strip=True))
    return perc

def scrape_company(url: str, nom_cible: str):
    r = _req(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # 1) Tentative JSON (plus fiable et stable)
    data = _json_from_page(soup)
    trustscore = None
    nombre_avis = None
    pourcentages = None

    if data:
        # businessUnit peut se trouver dans props.pageProps.businessUnit ou ailleurs
        bu = _find_first(data, "businessUnit")
        if isinstance(bu, dict):
            trustscore = _to_float_safe(bu.get("trustScore"))
            nombre_avis = _to_int_safe(bu.get("numberOfReviews"))
            rd = bu.get("ratingDistribution")
            if isinstance(rd, dict) and any(k in rd for k in ("excellent", "great", "average", "poor", "bad")):
                pourcentages = _percentages_from_json(rd)

    # 2) Fallback HTML si besoin
    if pourcentages is None:
        pourcentages = _percentages_from_html(soup)
    if trustscore is None:
        ts_tag = soup.select_one("div.styles_trustscoreContainer__P5RMx span")
        trustscore = _to_float_safe(ts_tag.get_text(strip=True)) if ts_tag else None
    if nombre_avis is None:
        avis_tag = soup.select_one("p[data-reviews-count-typography='true']")
        nombre_avis = _to_int_safe(avis_tag.get_text(strip=True)) if avis_tag else None

    # Domaine
    domaine = DOMAINES.get(nom_cible, "Non spécifié")

    # Sortie exactement au format attendu
    info = {
        "nom": nom_cible,
        "domaine_activite": domaine,
        "trustscore": trustscore,
        "nombre_avis": nombre_avis,
        **{k: (None if v is None else round(float(v), 2)) for k, v in pourcentages.items()}
    }
    return info

def main():
    results = []
    for url, nom in URLS:
        try:
            print(f"→ {nom} …")
            info = scrape_company(url, nom)
            results.append(info)
            time.sleep(random.uniform(0.6, 1.2))  # tiny polite pause
        except Exception as e:
            print(f"   !! Échec {nom}: {e}")
            # On met une ligne vide mais structurée pour garder l’alignement du tableau
            results.append({
                "nom": nom,
                "domaine_activite": DOMAINES.get(nom, "Non spécifié"),
                "trustscore": None,
                "nombre_avis": None,
                "excellent_%": None,
                "tres_bon_%": None,
                "moyen_%": None,
                "mediocre_%": None,
                "horrible_%": None,
            })

    df = pd.DataFrame(results, columns=[
        "nom", "domaine_activite", "trustscore", "nombre_avis",
        "excellent_%", "tres_bon_%", "moyen_%", "mediocre_%", "horrible_%"
    ])
    df.to_csv("trustpilot_20_societes.csv", index=False, encoding="utf-8")
    print("Fichier CSV enregistré : societes.csv")

if __name__ == "__main__":
    main()
