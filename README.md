Projet Supply Chain — Analyse de la Satisfaction Client (Showroom Privé)

Auteur : Mamadou DIAKHABY
Contact : diakhaby14@gmail.com

Dépôt : GitHub – Projet_satisfaction

Objectif du projet

Ce projet vise à analyser, modéliser et visualiser la satisfaction client à partir de plus de 20 000 avis réels collectés sur Showroom Privé.

Objectifs principaux

Ingestion et stockage des données brutes (MongoDB --> MySQL)

Orchestration des traitements via Airflow

Analyse et prédiction des sentiments clients grâce à un modèle de Machine Learning déployé sur FastAPI

Architecture globale

Flux de données complet (Data --> API --> Monitoring) :

┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│   MongoDB    │──▶  │   Airflow    │──▶  │    MySQL    │
│ Données brutes│    │  ETL/ELT     │     │  Stockage   │
└──────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │   FastAPI    │◀── Prometheus
                                          │ + Modèle ML  │
                                          └──────┬───────┘
                                                 │
                           ┌──────────────┬─────────────┬─────────────┐
                           ▼              ▼             ▼
                        Swagger        Grafana        StatsD


L’architecture combine ingestion, orchestration, déploiement et monitoring complet.

Structure du projet
Projet_satisfaction/
├── app/                      # API FastAPI + modèle ML
│   ├── main.py               # API principale
│   ├── models.py             # Modèles ML
│   ├── models_api.py         # Schémas de données
│   ├── retrain_model.py      # Réentraînement du modèle
│   ├── run_predictions.py    # Prédictions batch
│   ├── analyse_sentiment_errors.py
│   └── sentiment_pipeline.joblib
│
├── dags/                     # DAGs Airflow
│   └── satisfaction_dag.py
│
├── docker/                   # Configurations Docker
│   ├── docker-compose.yml
│   └── Dockerfile.fastapi
│
├── monitoring/               # Stack Prometheus + Grafana + StatsD
│
├── sql/                      # Scripts MySQL
│   ├── 01_create_transform.sql
│   ├── 02_link_all_reviews_to_showroom.sql
│   └── 03_test_queries.sql
│
├── src/                      # Code Python modulaire
│   ├── ingestion/            # Ingestion MongoDB → MySQL
│   ├── transform/            # Nettoyage et enrichissement
│   └── utils/                # Fonctions auxiliaires
│
├── docs/                     # Documentation et visuels
│   ├── ERD.md
│   └── architecture.png
│
└── tests/                    # Tests unitaires


Une documentation technique détaillée est disponible dans docs/.

Installation et exécution
1️ - Cloner le dépôt
git clone https://github.com/Diakhaby-data/Projet_satisfaction.git
cd Projet_satisfaction

2️ - Créer l’environnement Python
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt

3️ - Lancer les services Docker
docker compose -f docker/docker-compose.yml up -d

4️ - Initialiser la base MySQL
mysql -h 127.0.0.1 -P 3307 -u <USER> -p < sql/01_create_transform.sql

Pipeline de traitement
1. Ingestion MongoDB --> MySQL
python src/ingestion/ingest_reviews_from_mongo.py

2. Liaison des avis à Showroom Privé
mysql -h 127.0.0.1 -P 3307 -u <USER> -p < sql/02_link_all_reviews_to_showroom.sql

3. Vérification
mysql -h 127.0.0.1 -P 3307 -u <USER> -p < sql/03_test_queries.sql

Modélisation & Machine Learning

Modèle de base : TF-IDF + Régression Logistique

Modèles avancés : RandomForest, SVM, CamemBERT

Réentraînement automatique : app/retrain_model.py

Analyse d’erreurs : app/analyse_sentiment_errors.py

Le modèle est sérialisé sous :
app/sentiment_pipeline.joblib

API FastAPI

Documentation Swagger : http://localhost:8001/docs

Endpoints principaux
Méthode	Endpoint	Description
GET	/	Bilan de santé
POST	/predict	Prédiction du sentiment
GET	/stats	Statistiques agrégées

Monitoring et observabilité

Prometheus --> collecte des métriques API et système

Grafana --> visualisation des métriques

StatsD --> collecte des métriques internes

Lancer le monitoring :

docker compose -f docker-compose.monitoring.yml up -d

Sauvegarde et restauration
MySQL
mysqldump -h 127.0.0.1 -P 3307 -u <USER> -p projet > backup_mysql.sql

MongoDB
mongodump --host localhost --port 27017 -u <USER> -p <PASSWORD> \
  --authenticationDatabase admin --db projet


Les fichiers de sauvegarde sont exclus du Git (backups/ dans .gitignore).

Normes de développement

Formatage du code : black

Linting : flake8

Tests unitaires : pytest

CI/CD : GitHub Actions (build, tests, staging)

Documentation automatique : OpenAPI/Swagger

Contribution

Forker le dépôt

Créer une branche :

git checkout -b feat/your-feature


Commit clair :

git commit -m "feat: ajout pipeline d’ingestion"


Push et Pull Request

Pour toute question technique ou contribution : créez une issue GitHub ou contactez Mamadou Diakhaby.

Licence

Projet académique et open-source à but pédagogique.
Usage libre pour la recherche, l’apprentissage et la démonstration de compétences en Data Engineering / MLOps / Machine Learning appliqué.
