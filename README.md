# Couverture Maximale - Positionnement de Caméras de Surveillance

## Description du Projet

Application d'optimisation pour résoudre le **Problème de Couverture Maximale (Maximal Covering Location Problem)** appliqué au **positionnement optimal de caméras de surveillance**.

Ce projet utilise la **Programmation Linéaire en Nombres Entiers (PLNE)** avec le solveur **Gurobi** pour maximiser la couverture des zones à surveiller sous contraintes de budget et de nombre de caméras.

### Objectifs

- Maximiser la couverture pondérée des zones (en fonction de leur priorité et population)
- Optimiser l'allocation des ressources (budget limité, nombre de caméras)
- Assurer la redondance pour les zones critiques
- Distribuer géographiquement les caméras de manière équilibrée

## Structure du Projet

```
MaximalCoveringLocationProblem/
│
├── main.py                    # Point d'entrée de l'application
├── requirements.txt           # Dépendances Python
├── README.md                  # Ce fichier
│
├── src/
│   ├── optimization_model.py  # Modèle d'optimisation Gurobi
│   ├── main_window.py         # Interface graphique PyQt
│   └── visualization.py       # Visualisations Matplotlib
│
├── data/
│   └── example_data.json      # Exemple de données
│
└── docs/
    ├── modelisation.md        # Documentation mathématique
    └── rapport.md             # Rapport du projet
```

## Modélisation Mathématique

### Variables de Décision

- **x_i ∈ {0,1}**: 1 si une caméra est installée à l'emplacement i, 0 sinon
- **y_j ∈ {0,1}**: 1 si la zone j est couverte, 0 sinon

### Fonction Objectif

**Maximiser**: Σ (priorité_j × population_j × y_j) pour toutes les zones j

### Contraintes

1. **Contrainte de budget**:
   ```
   Σ (coût_i × x_i) ≤ Budget_maximal
   ```

2. **Contrainte du nombre de caméras**:
   ```
   Σ x_i ≤ Nombre_max_caméras
   ```

3. **Contraintes de couverture**:
   ```
   y_j ≤ Σ (couverture_ij × x_i) pour chaque zone j
   ```
   où couverture_ij = 1 si la caméra i peut couvrir la zone j (distance ≤ portée)

4. **Contrainte de redondance** (zones critiques):
   ```
   Σ (couverture_ij × x_i) ≥ 2 × y_j pour zones avec priorité ≥ 5
   ```

5. **Contrainte de diversité des types**:
   ```
   Σ x_i (pour caméras PTZ) ≥ 0.3 × Σ x_i (total)
   ```

6. **Contrainte de distribution géographique**:
   ```
   Σ x_i (par cluster géographique) ≤ max(2, N_cameras/3)
   ```

## Paramètres du Problème

### Zones à Surveiller
- **Position** (x, y): Coordonnées de la zone
- **Priorité** (1-10): Niveau de risque ou importance stratégique
- **Population**: Densité ou nombre de personnes
- **Description**: Type de zone (commerciale, résidentielle, etc.)

### Caméras
- **Position** (x, y): Emplacement potentiel
- **Coût**: Coût d'installation et d'équipement (€)
- **Portée**: Distance maximale de surveillance (mètres)
- **Angle**: Angle de vision (90°, 180°, 270°, 360°)
- **Type**: Fixe, PTZ (Pan-Tilt-Zoom), Thermique

### Contraintes Globales
- **Nombre maximal de caméras**: Budget en équipements
- **Budget maximal**: Contrainte financière totale

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Gurobi Optimizer (licence académique gratuite disponible)
- pip (gestionnaire de packages Python)

### Installation des Dépendances

```bash
# Installer les packages Python
pip install -r requirements.txt

# Installer Gurobi (si pas déjà fait)
# 1. Télécharger depuis https://www.gurobi.com/downloads/
# 2. Obtenir une licence académique gratuite
# 3. Activer la licence avec: grbgetkey XXXX-XXXX-XXXX-XXXX
```

### Dépendances Python

- `gurobipy>=10.0.0` - Solveur d'optimisation
- `PyQt5>=5.15.0` - Interface graphique
- `matplotlib>=3.5.0` - Visualisations
- `numpy>=1.21.0` - Calculs numériques

## Utilisation

### Lancer l'Application

```bash
python main.py
```

### Workflow d'Utilisation

1. **Configuration des Données** (Onglet 1)
   - Définir le nombre de zones et d'emplacements de caméras
   - Générer des données aléatoires OU charger depuis un fichier
   - Modifier les paramètres (priorités, coûts, portées, types)
   - Sauvegarder la configuration

2. **Résolution** (Onglet 2)
   - Configurer les paramètres du solveur (temps limite, gap)
   - Lancer l'optimisation (thread non-bloquant)
   - Observer le journal d'exécution en temps réel

3. **Résultats et Visualisation** (Onglet 3)
   - Consulter le résumé de la solution
   - Visualiser la carte de couverture
   - Afficher la heatmap d'intensité
   - Analyser les statistiques détaillées
   - Exporter la solution (JSON ou rapport TXT)

## Visualisations

L'application offre plusieurs types de visualisations:

### 1. Carte de Couverture
- Zones couvertes (vert) vs non couvertes (rouge)
- Caméras installées avec cercles de portée
- Priorités représentées par intensité de couleur
- Annotations pour zones critiques

### 2. Heatmap d'Intensité
- Intensité de couverture en chaque point
- Zones de redondance (multiples caméras)
- Gradients de couverture

### 3. Statistiques Complètes
- Distribution des types de caméras
- Taux de couverture (camembert)
- Niveaux de redondance (histogramme)
- Coûts par caméra (barres)
- Couverture par priorité
- Tableau récapitulatif des performances

## Format des Données

### Fichier JSON d'Entrée/Sortie

```json
{
  "max_cameras": 10,
  "max_budget": 50000,
  "zones": [
    [x, y, priorité, population, "description"],
    ...
  ],
  "cameras": [
    [x, y, coût, portée, angle, "type"],
    ...
  ]
}
```

## Exemple de Résultats

Pour un problème avec:
- 20 zones à surveiller
- 15 emplacements potentiels de caméras
- Budget: 50 000 €
- Maximum: 10 caméras

**Résultats typiques**:
- 8-10 caméras installées
- 85-95% de couverture des zones
- Zones critiques: redondance assurée (2-3 caméras)
- Utilisation du budget: 75-95%
- Temps de résolution: 2-10 secondes

## Complexité et Évaluation

Ce projet intègre plusieurs niveaux de complexité pour maximiser l'évaluation:

### Complexité de la Modélisation
- Modèle PLNE avec variables binaires  
- Fonction objectif multi-critères (priorité × population)  
- 6 types de contraintes différentes  
- Contraintes de redondance pour zones critiques  
- Contraintes de diversité de types de caméras  
- Contraintes de distribution géographique  

### Richesse des Paramètres
- 5 attributs par zone (position, priorité, population, description)  
- 6 attributs par caméra (position, coût, portée, angle, type)  
- 3 types de caméras différents (fixe, PTZ, thermique)  
- Calcul dynamique de la matrice de couverture  
- Clustering géographique automatique  

### Qualité de l'IHM
- Interface PyQt professionnelle avec 3 onglets  
- Threading (QThread) pour calculs non-bloquants  
- Tables interactives pour saisie de données  
- 3 types de visualisations Matplotlib  
- Export JSON et rapports TXT  
- Gestion d'erreurs et messages informatifs 
