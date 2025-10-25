Projet Supply Chain - Analyse de la Satisfaction Client (Showroom Privé)

Auteur : Mamadou DIAKHABY
    
Formation : Data Engineer (JUL25_BDE)

Objectif du projet

Ce projet vise à analyser, modéliser et visualiser la satisfaction client à partir de données d’avis réels collectés sur Showroom Privé (~20 000 avis).

L’objectif est triple :

Ingestion et stockage des données brutes (MongoDB → MySQL)

Traitement et transformation via pipelines Airflow

Analyse et prédiction des sentiments avec un modèle de Machine Learning exposé via API FastAPI

Architecture

Flux de données :

┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   MongoDB   │─────▶│    Airflow   │─────▶│    MySQL    │
│  (Raw Data) │      │   (ETL/ELT)  │      │ (Analytics) │
└─────────────┘      └──────────────┘      └──────┬──────┘
                                                   │
                     ┌─────────────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │   FastAPI    │◀────── Prometheus
              │   + ML Model │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌─────────┐
   │Swagger │  │Grafana  │  │StatsD   │
   └────────┘  └─────────┘  └─────────┘

Structure commentée du projet
Projet_satisfaction/
├── Dockerfile                     # Image principale Python du projet
├── Dockerfile.airflow             # Image Docker dédiée à Airflow
├── Dockerfile.fastapi             # Image Docker dédiée à FastAPI
├── Makefile                       # Automatisation des commandes (build, tests, run)
├── main.py                        # Script exécutable principal
├── Ingestion_reviews.py           # Ingestion MongoDB -> MySQL
├── Ingestion_reviews_liaisons.py  # Liaison des avis aux sociétés
├── create_pipeline.py             # Construction du pipeline ML
├── Projet_analyse_sentiments2.ipynb # Notebook d’analyse exploratoire
│
├── app/                           # Application FastAPI + modèle ML
│   ├── main.py                    # API principale
│   ├── dashboard.py               # Dashboard Streamlit
│   ├── database.py                # Connexion MongoDB
│   ├── database_test.py           # Tests de connexion
│   ├── models.py                  # Modèles ML
│   ├── models_api.py              # Schémas de données pour l’API
│   ├── run_predictions.py         # Lancement des prédictions batch
│   ├── retrain_model.py           # Réentraînement du modèle
│   ├── analyze_sentiment_errors.py# Analyse des erreurs de prédiction
│   ├── create_pipeline.py         # Construction pipeline ML
│   ├── Projet_analyse_sentiments_ML.ipynb # Notebook ML
│   ├── data/                      # Données utilisées par FastAPI
│   ├── requirements-fastapi.txt   # Dépendances FastAPI
│   └── sentiment_pipeline.joblib  # Modèle ML enregistré
│
├── dags/                          # DAGs Airflow
│   └── satisfaction_dag.py        # Pipeline d’orchestration des traitements
│
├── data/                          # Données sources et transformées
│   ├── avis.json                  # Données brutes MongoDB
│   ├── avis_clean.json            # Données nettoyées
│   ├── avis_derive.csv            # Données enrichies
│   ├── avis_with_predictions.csv  # Avis avec prédiction de sentiment
│   ├── satisfaction_report.txt    # Rapport texte généré
│   └── sentiment_pipeline.joblib  # Modèle ML local
│
├── docker/                        # Configurations Docker spécifiques
│   └── docker-compose.yml         # Orchestration des conteneurs principaux
├── docker-compose.yml              # Compose global du projet
├── docker-compose.monitoring.yml   # Compose dédié au monitoring (Grafana/Prometheus)
│
├── docs/                          # Documentation
│   ├── ERD.md                     # Diagramme entité-relation MySQL
│   └── screenshots/               # Captures d’écran
│
├── logs/                          # Logs Airflow (scheduler, DAGs…)
│
├── mongo/                         # Scripts MongoDB
│   ├── 01_indexes.js              # Indexation MongoDB
│   └── 04_test_queries_Mongo.sql  # Requêtes de test
│
├── monitoring/                    # Stack de monitoring
│   ├── docker-compose.yml         # Monitoring Prometheus + Grafana
│   ├── grafana/                   # Dashboards Grafana
│   ├── prometheus/                # Config Prometheus
│   └── statsd/                    # Collecte des métriques
│
├── reports/                       # Résultats graphiques
│   ├── distribution_nombre_etoiles.png
│   └── distribution_pays.png
│
├── run_scripts/                   # Scripts utilitaires SQL & Python
│   ├── 01_schema.sql              # Création du schéma MySQL
│   ├── script_20_societes.py      # Insertion sociétés
│   └── script_showroom.py         # Pipeline Showroom Privé
│
├── scripts/                       # Scripts d’analyse et scraping
│   ├── derive_data.py             # Feature engineering
│   ├── scrape_data.py             # Scraping / récupération de données
│   └── test_societes.sql          # Tests SQL
│
├── sql/                           # Scripts SQL principaux
│   ├── 01_create_transform.sql    # Création du schéma MySQL
│   ├── 02_link_all_reviews_to_showroom.sql # Liaison Showroom
│   ├── 03_test_queries.sql        # Requêtes de validation
│   └── test_societes.sql          # Requêtes de test
│
├── src/                           # Code Python modulaire
│   ├── ingestion/                 # Ingestion MongoDB → MySQL
│   ├── storage/                   # Chargement en base
│   ├── transform/                 # Nettoyage et enrichissement
│   └── utils/                     # Fonctions auxiliaires
│
├── setup_monitoring.sh            # Installation du monitoring
├── test_db.py                     # Tests base de données
└── tests/                         # Tests unitaires
    └── utils/

Installation
1. Cloner le dépôt
git clone https://github.com/DataScientest-Studio/JUIL25-BDE-SATISFACTION.git
cd Projet_satisfaction

2. Créer l’environnement Python
python -m venv venv
source venv/bin/activate      # Linux/macOS
.\venv\Scripts\activate       # Windows
pip install -r requirements.txt

3. Lancer les services Docker
docker compose -f docker/docker-compose.yml up -d

4. Initialiser la base MySQL
mysql -h 127.0.0.1 -P 3307 -u [USER] -p < sql/01_create_transform.sql

Exécution du pipeline d’ingestion

Importer les avis de MongoDB

python src/ingestion/ingest_reviews_from_mongo.py

Lier les avis à Showroom Privé

mysql -h 127.0.0.1 -P 3307 -u [USER] -p < sql/02_link_all_reviews_to_showroom.sql


Vérifier la cohérence

mysql -h 127.0.0.1 -P 3307 -u [USER] -p < sql/03_test_queries.sql

Machine Learning

Modèle de base : TF-IDF + Régression Logistique

Modèles avancés : RandomForest, SVM, CamemBERT

Réentraînement : app/retrain_model.py

Analyse d’erreur : app/analyze_sentiment_errors.py

API FastAPI

Documentation Swagger : http://localhost:8001/docs

Endpoints principaux :

GET / → health check

POST /predict → prédiction du sentiment

GET /stats → statistiques agrégées

Monitoring et Observabilité

Prometheus → métriques système et API

Grafana → tableaux de bord et visualisations

StatsD → collecte de métriques internes

Lancer le monitoring :

docker compose -f docker-compose.monitoring.yml up -d

Sauvegarde et restauration

MySQL

mysqldump -h 127.0.0.1 -P 3307 -u [USER] -p projet > backup_mysql.sql


MongoDB

mongodump --host localhost --port 27017 -u [USER] -p [PASSWORD] --authenticationDatabase admin --db projet


Les sauvegardes sont à exclure du Git (backups/ dans .gitignore).

Standards de développement

Code formaté avec black et vérifié avec flake8

Tests unitaires via pytest

CI/CD GitHub Actions : build, test, déploiement staging

Documentation automatique via OpenAPI/Swagger

Contribution

Fork du dépôt

Créer une branche : git checkout -b feat/your-feature

Commit clair : git commit -m "feat: ajout pipeline d’ingestion"

Push & Pull Request

Contact : diakhaby14@gmail.com

Pour toute question technique ou contribution :
Créez une issue GitHub ou contactez directement Mamadou Diakhaby.