# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer au projet **Smart Agriculture IoT Platform** ! Ce document vous guidera à travers le processus de contribution.

## 📋 Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Workflow de Développement](#workflow-de-développement)
- [Standards de Code](#standards-de-code)
- [Tests](#tests)
- [Documentation](#documentation)
- [Processus de Review](#processus-de-review)
- [Rapport de Bugs](#rapport-de-bugs)
- [Suggestions d'Amélioration](#suggestions-damélioration)

## 📜 Code de Conduite

Ce projet a adopté un code de conduite pour garantir une expérience positive pour tous. En participant, vous vous engagez à :

- ✅ Être respectueux et inclusif
- ✅ Accepter les critiques constructives
- ✅ Se concentrer sur ce qui est meilleur pour la communauté
- ✅ Montrer de l'empathie envers les autres membres

## 🚀 Comment Contribuer

### Types de Contributions

Nous accueillons plusieurs types de contributions :

1. **🐛 Corrections de bugs** : Signaler et corriger des bugs
2. **✨ Nouvelles fonctionnalités** : Proposer et implémenter de nouvelles fonctionnalités
3. **📚 Documentation** : Améliorer la documentation existante
4. **🧪 Tests** : Ajouter ou améliorer les tests
5. **🎨 Design** : Améliorer l'interface utilisateur
6. **🔧 Optimisation** : Améliorer les performances
7. **🌍 Traduction** : Traduire la documentation

### Avant de Commencer

1. **Vérifiez les issues existantes** : Assurez-vous qu'aucune issue similaire n'existe
2. **Créez une issue** : Discutez de votre idée avant de coder
3. **Attendez la validation** : Obtenez l'accord d'un mainteneur

## 🔄 Workflow de Développement

### 1. Fork et Clone

```bash
# Fork le projet sur GitHub, puis clonez votre fork
git clone https://github.com/VOTRE_USERNAME/smart-agriculture.git
cd smart-agriculture

# Ajoutez le repository upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/smart-agriculture.git
```

### 2. Créez une Branche

```bash
# Mettez à jour votre branche main
git checkout main
git pull upstream main

# Créez une nouvelle branche pour votre fonctionnalité
git checkout -b feature/nom-de-la-fonctionnalite

# Pour les corrections de bugs
git checkout -b fix/nom-du-bug

# Pour la documentation
git checkout -b docs/nom-de-la-doc
```

**Conventions de nommage des branches :**
- `feature/` : Nouvelles fonctionnalités
- `fix/` : Corrections de bugs
- `docs/` : Documentation
- `refactor/` : Refactoring de code
- `test/` : Ajout de tests
- `perf/` : Optimisations de performance

### 3. Développement

```bash
# Activez l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installez les dépendances de développement
pip install -r requirements-dev.txt

# Faites vos modifications...
# Suivez les standards de code (voir ci-dessous)
```

### 4. Commits

Utilisez des messages de commit clairs et descriptifs :

```bash
# Format : type(scope): description

# Types :
# feat: Nouvelle fonctionnalité
# fix: Correction de bug
# docs: Documentation
# style: Formatage, pas de changement de code
# refactor: Refactoring de code
# test: Ajout de tests
# chore: Tâches de maintenance

# Exemples :
git commit -m "feat(api): ajout endpoint pour récupérer les alertes"
git commit -m "fix(sensors): correction fuite mémoire dans temperature_sensor"
git commit -m "docs(readme): mise à jour instructions d'installation"
git commit -m "test(evaluation): ajout tests unitaires pour benchmark_pipeline"
```

**Règles pour les commits :**
- ✅ Message en anglais de préférence
- ✅ Premier lettre minuscule
- ✅ Pas de point à la fin
- ✅ Soyez descriptif mais concis
- ✅ Référencez les issues : `#123`

### 5. Push et Pull Request

```bash
# Push vers votre fork
git push origin feature/nom-de-la-fonctionnalite

# Créez une Pull Request sur GitHub
# Remplissez le template de PR
# Attendez la review
```

## 🎨 Standards de Code

### Python Style Guide

Suivez **PEP 8** avec ces spécifications :

```python
# ✅ BON
def calculate_average(values: List[float]) -> float:
    """
    Calculate the average of a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        Average value
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


# ❌ MAUVAIS
def calc(v):
    return sum(v)/len(v) if v else 0
```

### Règles Principales

#### 1. **Type Hints** (Obligatoire)

```python
# ✅ BON
def process_sensor_data(
    sensor_id: str,
    timestamp: datetime,
    value: float,
    unit: str = "celsius"
) -> Dict[str, Any]:
    ...

# ❌ MAUVAIS
def process_sensor_data(sensor_id, timestamp, value, unit="celsius"):
    ...
```

#### 2. **Docstrings** (Obligatoire)

Utilisez le format **Google Style** :

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Description courte de la fonction.
    
    Description plus détaillée si nécessaire.
    
    Args:
        param1: Description du premier paramètre
        param2: Description du deuxième paramètre
        
    Returns:
        Description de la valeur de retour
        
    Raises:
        ValueError: Description de l'exception
        
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

#### 3. **Nommage**

```python
# Classes : PascalCase
class SensorManager:
    pass

# Fonctions et variables : snake_case
def get_sensor_data():
    sensor_id = "TEMP_001"
    pass

# Constantes : UPPER_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Méthodes privées : underscore préfixe
def _internal_helper():
    pass
```

#### 4. **Longueur des Lignes**

- Maximum **88 caractères** (Black formatter)
- Utilisez des parenthèses pour les lignes multiples

```python
# ✅ BON
result = (
    sensor_data
    .filter_by(active=True)
    .order_by(SensorData.timestamp.desc())
    .limit(100)
    .all()
)

# ❌ MAUVAIS
result = sensor_data.filter_by(active=True).order_by(SensorData.timestamp.desc()).limit(100).all()
```

#### 5. **Imports**

Organisez les imports dans cet ordre :

```python
# 1. Standard library
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# 2. Third-party
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine

# 3. Local modules
from api.database import get_db
from models.sensor import Sensor
from utils.helpers import format_timestamp
```

Utilisez `isort` pour automatiser :

```bash
isort .
```

### Outils de Vérification

```bash
# Installation des outils de développement
pip install black isort flake8 mypy pytest pytest-cov

# Formatage automatique
black .
isort .

# Vérification du style
flake8 .

# Vérification des types
mypy .

# Tests avec couverture
pytest --cov=. --cov-report=html
```

### Configuration des Outils

**`.flake8`** :
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    venv,
    .venv
```

**`pyproject.toml`** :
```toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
```

## 🧪 Tests

### Structure des Tests

```
tests/
├── unit/                   # Tests unitaires
│   ├── test_sensors.py
│   ├── test_preprocessing.py
│   └── test_models.py
├── integration/            # Tests d'intégration
│   ├── test_pipeline.py
│   └── test_api.py
├── benchmark/              # Tests de performance
│   ├── test_latency.py
│   └── test_throughput.py
└── conftest.py            # Configuration pytest
```

### Écrire des Tests

```python
# tests/unit/test_sensor.py
import pytest
from sensors.temperature_sensor import TemperatureSensor

def test_temperature_sensor_creation():
    """Test temperature sensor initialization."""
    sensor = TemperatureSensor(
        sensor_id="TEMP_001",
        location="Field A"
    )
    assert sensor.sensor_id == "TEMP_001"
    assert sensor.location == "Field A"

def test_temperature_reading():
    """Test temperature reading generation."""
    sensor = TemperatureSensor(sensor_id="TEMP_001")
    reading = sensor.read()
    
    assert "value" in reading
    assert "timestamp" in reading
    assert -50 <= reading["value"] <= 100  # Celsius range
```

### Exécuter les Tests

```bash
# Tous les tests
pytest tests/

# Tests spécifiques
pytest tests/unit/test_sensor.py -v

# Tests avec couverture
pytest --cov=. --cov-report=html

# Tests en parallèle
pytest -n auto

# Tests avec marqueurs
pytest -m "not slow"
```

### Bonnes Pratiques

- ✅ Un test par fonctionnalité
- ✅ Noms de tests descriptifs
- ✅ Utilisez des fixtures pour le setup
- ✅ Mock les dépendances externes
- ✅ Tests indépendants et isolés
- ✅ Couverture minimum : 80%

## 📚 Documentation

### Documentation du Code

- **Docstrings** : Toutes les fonctions/classes publiques
- **Commentaires** : Expliquez le "pourquoi", pas le "quoi"
- **Exemples** : Ajoutez des exemples d'utilisation

### Documentation du Projet

- **README.md** : Vue d'ensemble du projet
- **CONTRIBUTING.md** : Ce fichier
- **EXECUTION_GUIDE.md** : Guide d'exécution
- **Module READMEs** : Documentation spécifique par module

### Mettre à Jour la Documentation

```bash
# Si vous modifiez une fonctionnalité, mettez à jour :
# 1. La docstring de la fonction
# 2. Le README du module concerné
# 3. Le README principal si nécessaire
# 4. Le guide d'exécution si nécessaire
```

## 🔍 Processus de Review

### Pour les Contributeurs

1. **Auto-review** : Vérifiez votre code avant de soumettre
2. **Tests** : Assurez-vous que tous les tests passent
3. **Documentation** : Mettez à jour la documentation
4. **Description** : Remplissez le template de PR

### Pour les Reviewers

1. **Code Quality** : Vérifiez la qualité du code
2. **Tests** : Vérifiez la couverture de tests
3. **Documentation** : Vérifiez la documentation
4. **Performance** : Vérifiez les impacts sur les performances
5. **Security** : Vérifiez les aspects sécurité

### Template de Pull Request

```markdown
## Description
Brève description des changements.

## Type de Changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Tests Effectués
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] Tests manuels

## Checklist
- [ ] Code formaté avec Black
- [ ] Imports organisés avec isort
- [ ] Tests ajoutés/mis à jour
- [ ] Documentation mise à jour
- [ ] Commit messages conventionnels

## Issues Liées
Ferme #123

## Screenshots (si applicable)
[Ajoutez des captures d'écran]
```

## 🐛 Rapport de Bugs

### Avant de Signaler un Bug

1. Vérifiez que le bug n'a pas déjà été signalé
2. Vérifiez que vous utilisez la dernière version
3. Rassemblez les informations nécessaires

### Template de Bug Report

```markdown
## Description du Bug
Description claire et concise du bug.

## Étapes pour Reproduire
1. Allez à '...'
2. Cliquez sur '....'
3. Voyez l'erreur

## Comportement Attendu
Ce qui devrait se passer.

## Comportement Actuel
Ce qui se passe réellement.

## Screenshots
[Si applicable, ajoutez des captures d'écran]

## Environnement
- OS: [ex: Ubuntu 20.04]
- Python Version: [ex: 3.9.7]
- Version du projet: [ex: 1.0.0]

## Logs
```
[Collez les logs pertinents]
```

## Contexte Supplémentaire
Tout autre information pertinente.
```

## 💡 Suggestions d'Amélioration

### Template de Feature Request

```markdown
## Problème
Quel problème cette fonctionnalité résout-elle ?

## Solution Proposée
Description de la solution souhaitée.

## Alternatives Considérées
Autres solutions que vous avez envisagées.

## Bénéfices
Comment cette fonctionnalité bénéficie-t-elle au projet ?

## Implémentation
Si vous avez des idées d'implémentation, décrivez-les ici.
```

## 📞 Contact

### Questions Générales

- **Email** : dev@smartagriculture.com
- **Slack** : #smart-agriculture-dev
- **Discord** : [Lien Discord]

### Mainteneurs

- **@maintainer1** - Core Backend
- **@maintainer2** - Data & ML
- **@maintainer3** - Frontend & Dashboard
- **@maintainer4** - DevOps

## 🎓 Ressources

### Documentation Technique

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Neo4j Documentation](https://neo4j.com/docs/)

### Tutoriels

- [MQTT Tutorial](https://mqtt.org/)
- [Kafka Tutorial](https://kafka.apache.org/documentation/)
- [Scikit-learn Tutorial](https://scikit-learn.org/stable/tutorial/)
- [Streamlit Tutorial](https://docs.streamlit.io/)

## 🏆 Reconnaissance

Les contributeurs seront reconnus dans :

- Le fichier **CONTRIBUTORS.md**
- La section **Équipe** du README
- Les notes de version

### Niveaux de Contribution

- **🥉 Bronze** : 1-5 contributions
- **🥈 Silver** : 6-20 contributions
- **🥇 Gold** : 21+ contributions
- **💎 Diamond** : Contributions majeures (architecture, fonctionnalités clés)

## 📄 License

En contribuant, vous acceptez que vos contributions soient sous la même licence [MIT](LICENSE) que le projet.

---

## ✅ Checklist Rapide

Avant de soumettre une contribution :

- [ ] J'ai lu ce guide
- [ ] J'ai créé/vérifié une issue
- [ ] Mon code suit PEP 8
- [ ] J'ai ajouté des tests
- [ ] Tous les tests passent
- [ ] J'ai mis à jour la documentation
- [ ] J'ai formaté le code (black, isort)
- [ ] Mon commit respecte les conventions
- [ ] J'ai rempli le template de PR

---

**Merci de contribuer à Smart Agriculture IoT Platform ! 🌾**

*Dernière mise à jour : Juin 2024*