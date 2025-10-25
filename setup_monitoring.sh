#!/bin/bash

# ================================================================
# Script d'installation automatique du monitoring
# Projet : Satisfaction Client
# ================================================================

set -e  # Arrêt en cas d'erreur

echo " Installation du monitoring - Projet Satisfaction"
echo "=================================================="
echo ""

# ================================================================
# ÉTAPE 1 : Vérification de l'environnement
# ================================================================

echo " Vérification de l'environnement..."

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo " Docker n'est pas installé. Installez Docker avant de continuer."
    exit 1
fi

# Vérifier que docker-compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo " docker-compose n'est pas installé. Installez docker-compose avant de continuer."
    exit 1
fi

echo " Docker et docker-compose sont installés"

# Vérifier qu'on est à la racine du projet
if [ ! -f "docker-compose.yml" ]; then
    echo " Erreur : ce script doit être exécuté depuis la racine du projet (où se trouve docker-compose.yml)"
    exit 1
fi

echo " Vous êtes à la racine du projet"
echo ""

# ================================================================
# ÉTAPE 2 : Création de la structure des dossiers
# ================================================================

echo " Création de la structure des dossiers..."

mkdir -p monitoring/prometheus
mkdir -p monitoring/statsd
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards

echo " Structure créée :"
echo "   monitoring/"
echo "   ├── prometheus/"
echo "   ├── statsd/"
echo "   └── grafana/provisioning/"
echo "       ├── datasources/"
echo "       └── dashboards/"
echo ""

# ================================================================
# ÉTAPE 3 : Vérification des fichiers de configuration
# ================================================================

echo " Vérification des fichiers de configuration..."

MISSING_FILES=0

if [ ! -f "monitoring/docker-compose.yml" ]; then
    echo " monitoring/docker-compose.yml manquant"
    MISSING_FILES=$((MISSING_FILES + 1))
fi

if [ ! -f "monitoring/prometheus/prometheus.yml" ]; then
    echo " monitoring/prometheus/prometheus.yml manquant"
    MISSING_FILES=$((MISSING_FILES + 1))
fi

if [ ! -f "monitoring/statsd/statsd_mapping.yml" ]; then
    echo " monitoring/statsd/statsd_mapping.yml manquant"
    MISSING_FILES=$((MISSING_FILES + 1))
fi

if [ ! -f "monitoring/grafana/provisioning/datasources/datasource.yml" ]; then
    echo " monitoring/grafana/provisioning/datasources/datasource.yml manquant"
    MISSING_FILES=$((MISSING_FILES + 1))
fi

if [ ! -f "monitoring/grafana/provisioning/dashboards/dashboard.yml" ]; then
    echo " monitoring/grafana/provisioning/dashboards/dashboard.yml manquant"
    MISSING_FILES=$((MISSING_FILES + 1))
fi

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo " $MISSING_FILES fichier(s) de configuration manquant(s)"
    echo "   Veuillez copier tous les artifacts dans les bons emplacements avant de continuer"
    exit 1
fi

echo "Tous les fichiers de configuration sont présents"
echo ""

# ================================================================
# ÉTAPE 4 : Reconstruction du service FastAPI
# ================================================================

echo "Reconstruction du service FastAPI avec les nouvelles dépendances..."

# Arrêter le service FastAPI
docker-compose stop fastapi_service || true

# Reconstruire l'image
docker-compose build fastapi_service

# Redémarrer le service
docker-compose up -d fastapi_service

echo "Service FastAPI reconstruit et redémarré"
echo ""

# Attendre que FastAPI soit prêt
echo "Attente du démarrage de FastAPI (10 secondes)..."
sleep 10

# Vérifier que l'endpoint /metrics est accessible
if curl -s http://localhost:8000/metrics > /dev/null 2>&1; then
    echo "Endpoint /metrics accessible"
else
    echo "L'endpoint /metrics n'est pas encore accessible (peut prendre quelques secondes)"
fi
echo ""

# ================================================================
# ÉTAPE 5 : Redémarrage d'Airflow (pour activer StatsD)
# ================================================================

echo "Redémarrage d'Airflow pour activer les métriques StatsD..."

docker-compose restart airflow_webserver airflow_scheduler

echo "Airflow redémarré"
echo ""

# ================================================================
# ÉTAPE 6 : Démarrage de la stack de monitoring
# ================================================================

echo "Démarrage de la stack de monitoring..."

cd monitoring

# Démarrer tous les services
docker-compose up -d

echo " Stack de monitoring démarrée"
echo ""

# Attendre que les services démarrent
echo " Attente du démarrage des services (15 secondes)..."
sleep 15

# ================================================================
# ÉTAPE 7 : Vérification du déploiement
# ================================================================

echo " Vérification du déploiement..."
echo ""

# Vérifier l'état des conteneurs
echo " État des conteneurs de monitoring :"
docker-compose ps
echo ""

# Vérifier Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo " Prometheus : UP (http://localhost:9090)"
else
    echo " Prometheus : DOWN"
fi

# Vérifier Grafana
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo " Grafana : UP (http://localhost:3000)"
else
    echo " Grafana : DOWN"
fi

# Vérifier MongoDB Exporter
if curl -s http://localhost:9216/metrics > /dev/null 2>&1; then
    echo " MongoDB Exporter : UP (http://localhost:9216)"
else
    echo " MongoDB Exporter : DOWN"
fi

# Vérifier StatsD Exporter
if curl -s http://localhost:9102/metrics > /dev/null 2>&1; then
    echo " StatsD Exporter : UP (http://localhost:9102)"
else
    echo " StatsD Exporter : DOWN"
fi

# Vérifier Node Exporter
if curl -s http://localhost:9100/metrics > /dev/null 2>&1; then
    echo " Node Exporter : UP (http://localhost:9100)"
else
    echo "❌ Node Exporter : DOWN"
fi

echo ""

# ================================================================
# ÉTAPE 8 : Affichage des informations de connexion
# ================================================================

echo "=================================================="
echo " Installation terminée avec succès !"
echo "=================================================="
echo ""
echo " Accès aux interfaces :"
echo ""
echo "   🔹 Prometheus : http://localhost:9090"
echo "      - Vérifier les targets : http://localhost:9090/targets"
echo ""
echo "   🔹 Grafana : http://localhost:3000"
echo "      - Login : admin"
echo "      - Password : admin (changez-le à la première connexion)"
echo ""
echo "   🔹 FastAPI Metrics : http://localhost:8000/metrics"
echo ""
echo "   🔹 Airflow : http://localhost:8080"
echo "      - Login : admin"
echo "      - Password : admin"
echo ""
echo "=================================================="
echo " Prochaines étapes :"
echo "=================================================="
echo ""
echo "1. Ouvrez Grafana : http://localhost:3000"
echo "2. Importez des dashboards préconfigurés :"
echo "   - ID 14282 : FastAPI Dashboard"
echo "   - ID 2583 : MongoDB Dashboard"
echo "   - ID 1860 : Node Exporter Full"
echo ""
echo "3. Vérifiez que Prometheus collecte bien les métriques :"
echo "   http://localhost:9090/targets"
echo "   → Tous les targets doivent être en vert (UP)"
echo ""
echo "4. Consultez les logs si nécessaire :"
echo "   cd monitoring"
echo "   docker-compose logs -f prometheus"
echo "   docker-compose logs -f grafana"
echo ""
echo "=================================================="
echo " Commandes utiles :"
echo "=================================================="
echo ""
echo "   # Voir les logs"
echo "   cd monitoring && docker-compose logs -f"
echo ""
echo "   # Redémarrer un service"
echo "   cd monitoring && docker-compose restart prometheus"
echo ""
echo "   # Arrêter le monitoring"
echo "   cd monitoring && docker-compose down"
echo ""
echo "   # Voir l'utilisation des ressources"
echo "   docker stats"
echo ""
echo "=================================================="