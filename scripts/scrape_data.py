# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import time
import os

headers = {"User-Agent": "Mozilla/5.0"}

country_urls = {
    "France": "https://fr.trustpilot.com/review/www.showroomprive.com?page={}",
    "Spain": "https://es.trustpilot.com/review/www.showroomprive.com?page={}",
    "Italy": "https://it.trustpilot.com/review/www.showroomprive.com?page={}"
}

NUM_PAGES = 5  # réduire pour tester rapidement
all_reviews = []

# Chemin de sortie partagé avec Airflow
output_path = "/opt/airflow/data/avis.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

for country, template in country_urls.items():
    stop_country = False

    for page in range(1, NUM_PAGES + 1):
        if stop_country:
            break

        url = template.format(page)
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"Erreur {resp.status_code} sur {url}")
                break
        except Exception as e:
            print(f"Erreur réseau : {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            print(f"pas de script JSON trouvé à la page {page}")
            stop_country = True
            break

        try:
            data = json.loads(script.string)
            page_props = data.get("props", {}).get("pageProps", {})
            reviews = page_props.get("reviews", [])

            if not reviews:
                print(f"pas d'avis trouvés à la page {page}, arrêt pour {country}")
                stop_country = True
                break

            for rev in reviews:
                reply = rev.get("reply") or {}
                texte = reply.get("message", "")
                date = reply.get("publishedDate", "")

                all_reviews.append({
                    "titre_avis": rev.get("title", ""),
                    "contenu": rev.get("text", ""),
                    "nombre_etoile": rev.get("rating"),
                    "date_avis": rev.get("dates", {}).get("publishedDate", ""),
                    "pays": country,
                    "langue": rev.get("language", ""),
                    "reponse_entreprise": "OUI" if texte else "NON",
                    "texte_entreprise": texte,
                    "date_reponse_entreprise": date
                })

        except Exception as e:
            print(f"erreur JSON à la page {page}: {e}")
            stop_country = True
            break

        time.sleep(2)

# Sauvegarde finale
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_reviews, f, ensure_ascii=False, indent=2)

print(f"\n{len(all_reviews)} avis extraits et enregistrés dans '{output_path}'")
