# Guide d'Installation et d'Utilisation

## Installation Rapide

### 1. Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de packages)
- Git (optionnel)

### 2. Installation de Gurobi

#### Étape 1: Téléchargement
Visitez: https://www.gurobi.com/downloads/

#### Étape 2: Installation
- Windows: Exécuter le fichier `.msi`
- macOS: Utiliser le fichier `.pkg`
- Linux: `tar xvfz gurobi.tar.gz`

#### Étape 3: Licence Académique (Gratuite)
1. Créer un compte sur https://www.gurobi.com/
2. Aller sur la page des licences académiques
3. Générer une licence
4. Exécuter: `grbgetkey XXXX-XXXX-XXXX-XXXX`

### 3. Installation des Dépendances Python

```bash
cd MaximalCoveringLocationProblem
pip install -r requirements.txt
```

### 4. Lancement de l'Application

```bash
python main.py
```

## Utilisation Pas-à-Pas

### Étape 1: Configuration des Données
1. Ouvrir l'onglet "Configuration des Données"
2. Définir les paramètres (budget, nombre de caméras)
3. Cliquer sur "Générer Données Aléatoires" OU charger un fichier JSON

### Étape 2: Personnalisation (Optionnel)
- Modifier les priorités des zones dans la table
- Ajuster les coûts et portées des caméras
- Changer les types de caméras

### Étape 3: Résolution
1. Ouvrir l'onglet "Résolution"
2. Configurer les paramètres du solveur (temps limite, gap)
3. Cliquer sur "🚀 Lancer l'Optimisation"
4. Observer les logs en temps réel

### Étape 4: Analyse des Résultats
1. Ouvrir l'onglet "Résultats et Visualisation"
2. Consulter le résumé et les détails
3. Cliquer sur les boutons de visualisation:
   - "Afficher Carte de Couverture"
   - "Afficher Heatmap"
   - "Afficher Statistiques"

### Étape 5: Export (Optionnel)
- "Exporter Solution (JSON)": Sauvegarder les résultats
- "Générer Rapport (TXT)": Créer un rapport textuel

## Dépannage

### Erreur: "No module named 'gurobipy'"
```bash
pip install gurobipy
```
Puis obtenir une licence académique.

### Erreur: "Model is infeasible"
- Augmenter le budget
- Augmenter le nombre de caméras
- Vérifier que les portées sont suffisantes

### Interface ne répond pas
- Vérifier que PyQt5 est installé
- Redémarrer l'application
- Vérifier les logs dans l'onglet Résolution

## Contact

Pour toute question: [votre_email@insat.u-carthage.tn]
