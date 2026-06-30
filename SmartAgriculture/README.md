# 🌾 Smart Agriculture IoT Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Plateforme IoT intelligente pour l'agriculture moderne** - Une architecture multicouche complète pour la collecte, le traitement, l'analyse et la visualisation de données agricoles en temps réel.

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Technologies](#technologies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du Projet](#structure-du-projet)
- [Documentation](#documentation)
- [Tests](#tests)
- [Contribution](#contribution)
- [Équipe](#équipe)

## 🎯 Vue d'ensemble

Cette plateforme IoT agricole intègre une architecture complète pour :

- **Collecte de données** : Capteurs IoT multiples (température, humidité, pH, GPS, etc.)
- **Ingestion temps réel** : MQTT et Kafka pour le streaming de données
- **Traitement ETL** : Pipeline de nettoyage, validation et transformation
- **Stockage multidatabase** : PostgreSQL, TimescaleDB, MongoDB, Neo4j
- **Intelligence Artificielle** : Modèles ML/DL pour prédictions et détection d'anomalies
- **API REST** : Exposition des données et prédictions via FastAPI
- **Dashboard temps réel** : Visualisation avec Streamlit et Dash
- **Évaluation complète** : Benchmarking et validation statistique

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Smart Agriculture Platform                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Capteurs │  │   MQTT  │  │  Kafka   │  │   API    │  │
│  │   IoT    │→│ Broker  │→│ Streams  │→│ REST     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       │              │            │            │            │
│       └──────────────┴────────────┴────────────┘            │
│                        │                                     │
│                        ▼                                     │
│              ┌─────────────────┐                            │
│              │  Pipeline ETL   │                            │
│              │  + Preprocessing│                            │
│              └─────────────────┘                            │
│                        │                                     │
│       ┌────────────────┼────────────────┐                   │
│       │                │                │                   │
│       ▼                ▼                ▼                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │PostgreSQL│   │TimescaleDB│  │ MongoDB  │               │
│  │(Relationnel)│ │(Temporel)│ │(Documents)│               │
│  └──────────┘   └──────────┘   └──────────┘               │
│       │                │                │                   │
│       └────────────────┼────────────────┘                   │
│                        │                                     │
│                        ▼                                     │
│              ┌─────────────────┐                            │
│              │  Modèles IA     │                            │
│              │  (ML/DL)        │                            │
│              └─────────────────┘                            │
│                        │                                     │
│         ┌──────────────┴──────────────┐                    │
│         │                             │                    │
│         ▼                             ▼                    │
│  ┌──────────────┐           ┌──────────────┐              │
│  │   FastAPI    │           │  Dashboard   │              │
│  │   REST API   │           │  (Streamlit) │              │
│  └──────────────┘           └──────────────┘              │
│         │                             │                    │
│         └──────────────┬──────────────┘                    │
│                        │                                     │
│                        ▼                                     │
│              ┌─────────────────┐                            │
│              │   Utilisateurs  │                            │
│              └─────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Fonctionnalités

### 📡 Capteurs IoT
- **Température** : Surveillance en temps réel
- **Humidité** : Contrôle de l'humidité ambiante
- **Sol** : Humidité du sol, pH, température
- **Environnement** : Pluviométrie, luminosité, vent
- **Eau** : Qualité de l'eau (pH, turbidité, oxygène)
- **GPS** : Localisation des capteurs
- **Animaux** : Surveillance du bétail (si applicable)

### 🔄 Pipeline de Données
- **MQTT Broker** : Communication temps réel avec les capteurs
- **Kafka Streams** : Traitement de flux de données à haute vitesse
- **ETL Pipeline** : Extraction, Transformation, Chargement
- **Prétraitement** : Validation, nettoyage, normalisation
- **Feature Engineering** : Création de features avancées

### 🗄️ Bases de Données
- **PostgreSQL** : Données relationnelles (capteurs, utilisateurs)
- **TimescaleDB** : Séries temporelles haute performance
- **MongoDB** : Documents flexibles (données brutes, logs)
- **Neo4j** : Graphes sémantiques (relations entre capteurs)

### 🤖 Intelligence Artificielle
- **Random Forest** : Classification et régression
- **XGBoost** : Prédictions haute performance
- **LSTM** : Séries temporelles profondes
- **SVM** : Classification support vector
- **Isolation Forest** : Détection d'anomalies
- **Autoencoder** : Détection d'anomalies deep learning

### 📊 API REST
- Endpoints pour capteurs, observations, prédictions
- Authentification HTTP Basic et JWT
- Documentation automatique (Swagger/OpenAPI)
- Export de données (CSV, JSON)

### 📈 Dashboard
- **Streamlit** : Interface temps réel
- **Dash** : Dashboard alternatif avancé
- Visualisations Plotly interactives
- Alertes automatiques (température, humidité, irrigation)
- Cartes GPS des capteurs
- Métriques KPI en temps réel

### 🧪 Évaluation et Benchmarking
- Benchmark pipeline (throughput, latence)
- Benchmark bases de données
- Benchmark modèles IA
- Monitoring ressources (CPU, RAM, disque)
- Tests de scalabilité
- Validation statistique (Wilcoxon, ANOVA, etc.)
- Génération de rapports automatiques
- Figures publication-ready

## 🛠️ Technologies

### Backend
- **Python 3.9+**
- **FastAPI** - Framework API REST
- **SQLAlchemy 2.0** - ORM base de données
- **Pydantic** - Validation des données

### Data & ML
- **Pandas** - Manipulation de données
- **NumPy** - Calcul scientifique
- **Scikit-learn** - Machine Learning
- **XGBoost** - Gradient Boosting
- **TensorFlow/Keras** - Deep Learning (LSTM)

### Databases
- **PostgreSQL** - Base relationnelle
- **TimescaleDB** - Extension time-series
- **MongoDB** - Base documentaire
- **Neo4j** - Base graphe

### Messaging
- **MQTT** (Mosquitto) - IoT messaging
- **Kafka** - Streaming de données

### Dashboard & Viz
- **Streamlit** - Dashboard interactif
- **Dash** - Dashboard avancé
- **Plotly** - Visualisations interactives
- **Matplotlib/Seaborn** - Figures statiques

### DevOps
- **Docker & Docker Compose** - Containerisation
- **Uvicorn** - Serveur ASGI

## 🚀 Installation

### Prérequis
- Python 3.9 ou supérieur
- Docker et Docker Compose
- Git

### Installation locale

```bash
# Cloner le repository
git clone https://github.com/username/smart-agriculture.git
cd smart-agriculture

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Installer les dépendances des modules
pip install -r api/requirements.txt
pip install -r dashboard/requirements.txt
pip install -r evaluation/requirements.txt
pip install -r ingestion/requirements.txt
pip install -r models/requirements.txt
pip install -r preprocessing/requirements.txt
pip install -r semantic/requirements.txt
pip install -r sensors/requirements.txt
```

### Installation avec Docker

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Voir les logs
docker-compose logs -f
```

## ⚙️ Configuration

### Variables d'environnement

Copier le fichier `.env.example` vers `.env` et configurer :

```bash
# Base de données PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agriculture
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123

# TimescaleDB
TIMESCALE_HOST=localhost
TIMESCALE_PORT=5433
TIMESCALE_DB=agriculture_ts

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# MQTT
MQTT_HOST=localhost
MQTT_PORT=1883

# Kafka
KAFKA_HOST=localhost:9092
```

### Initialisation des bases de données

```bash
# PostgreSQL
docker-compose exec postgres psql -U admin -d agriculture -f /app/database/init_postgres.sql

# TimescaleDB
docker-compose exec timescaledb psql -U admin -d agriculture_ts -f /app/database/init_timescaledb.sql

# MongoDB
docker-compose exec mongodb mongosh < database/mongodb/init.js

# Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p password < database/neo4j/init.cypher
```

## 📖 Utilisation

### Démarrer les services

```bash
# Terminal 1: Démarrer l'infrastructure (bases de données, brokers)
docker-compose up -d postgres timescaledb mongodb neo4j mosquitto kafka zookeeper

# Terminal 2: Démarrer les capteurs
python sensors/run_all_sensors.py

# Terminal 3: Démarrer le pipeline d'ingestion
python ingestion/pipeline.py

# Terminal 4: Démarrer l'API REST
uvicorn api.app:app --reload --port 8000

# Terminal 5: Démarrer le dashboard
streamlit run dashboard/streamlit_app.py
# ou
python dashboard/dash_app.py
```

### Accéder aux services

- **API REST** : http://localhost:8000
  - Documentation : http://localhost:8000/docs
  - OpenAPI : http://localhost:8000/openapi.json

- **Dashboard Streamlit** : http://localhost:8501

- **Dashboard Dash** : http://localhost:8050

### Exemples d'utilisation

```python
# Exemple 1: Récupérer les capteurs
import requests
response = requests.get('http://localhost:8000/api/v1/sensors')
sensors = response.json()

# Exemple 2: Faire une prédiction
prediction_data = {
    "features": [25.0, 70.0, 45.0, 6.5, 10.0, 5000.0],
    "model_type": "random_forest"
}
response = requests.post('http://localhost:8000/api/v1/predict', json=prediction_data)
result = response.json()
```

## 📁 Structure du Projet

```
SmartAgriculture/
├── api/                      # API REST FastAPI
│   ├── app.py               # Application principale
│   ├── database.py          # Connexions bases de données
│   ├── models.py            # Modèles Pydantic
│   ├── prediction.py        # Moteur de prédiction ML
│   ├── routes.py            # Routes API
│   ├── auth.py              # Authentification
│   └── requirements.txt
│
├── dashboard/               # Dashboards
│   ├── streamlit_app.py     # Dashboard Streamlit
│   ├── dash_app.py          # Dashboard Dash
│   ├── charts.py            # Génération de graphiques
│   ├── alerts.py            # Système d'alertes
│   └── requirements.txt
│
├── evaluation/              # Évaluation et benchmarking
│   ├── metrics.py           # Métriques d'évaluation
│   ├── evaluation_pipeline.py
│   ├── benchmark_*.py       # Modules de benchmark
│   ├── statistical_validation.py
│   ├── final_report.py      # Génération de rapports
│   └── requirements.txt
│
├── ingestion/               # Pipeline ETL
│   ├── pipeline.py          # Pipeline principal
│   ├── mqtt_subscriber.py   # Subscriber MQTT
│   ├── kafka_producer.py    # Producer Kafka
│   ├── etl.py               # Extract Transform Load
│   ├── postgres_loader.py   # Loader PostgreSQL
│   ├── timescaledb_loader.py
│   ├── mongodb_loader.py
│   ├── neo4j_loader.py
│   └── requirements.txt
│
├── preprocessing/           # Prétraitement des données
│   ├── validator.py         # Validation
│   ├── cleaner.py           # Nettoyage
│   ├── normalizer.py        # Normalisation
│   ├── outlier_detector.py  # Détection d'outliers
│   ├── feature_engineering.py
│   └── requirements.txt
│
├── semantic/                # Couche sémantique
│   ├── ontology.py          # Ontologie agricole
│   ├── sosa_mapper.py        # Mapping SOSA/SSN
│   ├── jsonld_converter.py   # Conversion JSON-LD
│   ├── rdf_converter.py      # Conversion RDF
│   ├── neo4j_graph.py        # Graphe Neo4j
│   └── requirements.txt
│
├── models/                  # Modèles IA
│   ├── random_forest.py
│   ├── xgboost_model.py
│   ├── lstm_model.py
│   ├── isolation_forest.py
│   ├── autoencoder.py
│   ├── training_pipeline.py
│   └── requirements.txt
│
├── sensors/                 # Capteurs IoT
│   ├── config.py            # Configuration
│   ├── publisher.py         # Publication MQTT
│   ├── temperature_sensor.py
│   ├── humidity_sensor.py
│   ├── soil_moisture_sensor.py
│   ├── ph_sensor.py
│   ├── gps_sensor.py
│   └── requirements.txt
│
├── database/                # Scripts SQL
│   ├── postgres/
│   │   ├── schema.sql
│   │   ├── indexes.sql
│   │   └── constraints.sql
│   ├── timescaledb/
│   │   └── schema.sql
│   ├── mongodb/
│   │   └── collections.py
│   └── neo4j/
│       └── graph.cypher
│
├── docker/                  # Configuration Docker
│   ├── docker-compose.yml
│   └── mosquitto/
│       └── mosquitto.conf
│
├── tests/                   # Tests unitaires
│   ├── test_postgres.py
│   ├── test_mongodb.py
│   ├── test_neo4j.py
│   └── test_*.py
│
├── data/                    # Données
│   ├── models/              # Modèles entraînés
│   └── raw/                 # Données brutes
│
├── results/                 # Résultats d'évaluation
│   ├── figures/            # Graphiques générés
│   └── *.json              # Résultats de benchmark
│
├── .env                     # Variables d'environnement
├── .gitignore
├── requirements.txt         # Dépendances principales
├── docker-compose.yml       # Orchestration Docker
├── EXECUTION_GUIDE.md       # Guide d'exécution
└── README.md                # Ce fichier
```

## 📚 Documentation

### Guides disponibles
- **[EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)** - Guide d'exécution complet
- **[evaluation/README.md](evaluation/README.md)** - Documentation du package d'évaluation
- **[api/README.md](api/README.md)** - Documentation de l'API REST
- **[dashboard/README.md](dashboard/README.md)** - Documentation des dashboards
- **[sensors/README.md](sensors/README.md)** - Documentation des capteurs

### Documentation API
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI JSON** : http://localhost:8000/openapi.json

## 🧪 Tests

```bash
# Exécuter tous les tests
pytest tests/

# Tests avec couverture
pytest tests/ --cov=.

# Tests spécifiques
pytest tests/test_postgres.py -v
pytest tests/test_mqtt.py -v
pytest tests/test_neo4j.py -v

# Tests d'intégration
pytest tests/integration/ -v
```

## 🤝 Contribution

Voir **[CONTRIBUTING.md](CONTRIBUTING.md)** pour les détails sur la contribution au projet.

### Workflow de développement

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards de code

- **PEP 8** : Style de code Python
- **Type Hints** : Utiliser les annotations de type
- **Docstrings** : Documenter toutes les fonctions/classes
- **Tests** : Écrire des tests pour les nouvelles fonctionnalités
- **Commits** : Messages de commit clairs et descriptifs

## 👥 Équipe

### Développeurs
- **Chef de Projet** : [Nom]
- **Architecte** : [Nom]
- **Développeur Backend** : [Nom]
- **Développeur Frontend** : [Nom]
- **Data Scientist** : [Nom]
- **DevOps** : [Nom]

### Contact
- **Email** : team@smartagriculture.com
- **Slack** : #smart-agriculture
- **Wiki** : https://wiki.smartagriculture.com

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **FastAPI** - Framework web moderne et rapide
- **Streamlit** - Dashboard interactif facile
- **Plotly** - Visualisations interactives
- **Scikit-learn** - Outils ML accessibles
- **Docker** - Containerisation simplifiée

---

**Dernière mise à jour** : Juin 2024  
**Version** : 1.0.0  
**Statut** : ✅ Production Ready