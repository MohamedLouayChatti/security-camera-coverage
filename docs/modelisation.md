# Modélisation Mathématique - Problème de Couverture Maximale

## Introduction

Le **Problème de Couverture Maximale (Maximal Covering Location Problem - MCLP)** est un problème classique de recherche opérationnelle visant à positionner un nombre limité d'installations (ici, des caméras de surveillance) de manière à maximiser la couverture d'un ensemble de points de demande (zones à surveiller).

## Application: Positionnement de Caméras de Surveillance

Dans notre contexte, nous cherchons à:
- Maximiser la surveillance des zones sensibles
- Respecter un budget limité
- Limiter le nombre de caméras installées
- Encourager la redondance pour les zones critiques
- Éviter l'installation de caméras inutiles

## Notations

### Ensembles

- **I**: Ensemble des emplacements potentiels de caméras (i ∈ I)
- **J**: Ensemble des zones à surveiller (j ∈ J)
- **T**: Ensemble des types de caméras (fixe, PTZ, thermique)

### Paramètres

- **c_i**: Coût d'installation de la caméra i (€)
- **r_i**: Portée de la caméra i (mètres)
- **θ_i**: Angle de vision de la caméra i (degrés)
- **t_i**: Type de la caméra i ∈ T
- **p_j**: Priorité de la zone j (1-10)
- **w_j**: Population/densité de la zone j
- **d_ij**: Distance euclidienne entre la caméra i et la zone j
- **B**: Budget maximal disponible (€)
- **K**: Nombre maximal de caméras à installer
- **P_min**: Priorité minimale pour exiger une redondance (par défaut: 5)

### Variables de Décision

- **x_i ∈ {0,1}**: Variable binaire
  - x_i = 1 si une caméra est installée à l'emplacement i
  - x_i = 0 sinon

- **y_j ∈ {0,1}**: Variable binaire
  - y_j = 1 si la zone j est couverte par au moins une caméra
  - y_j = 0 sinon

### Paramètre Dérivé: Matrice de Couverture

**a_ij ∈ {0,1}**: Paramètre de couverture
- a_ij = 1 si la caméra i peut couvrir la zone j (c'est-à-dire si d_ij ≤ r_i)
- a_ij = 0 sinon

Calcul:
```
a_ij = 1  si  √[(x_i - x_j)² + (y_i - y_j)²] ≤ r_i
a_ij = 0  sinon
```

## Formulation Mathématique Complète

### Fonction Objectif

**Maximiser:**

```
Z = Σ(j∈J) p_j × w_j × y_j + 0.1 × Σ(j∈J, p_j≥7) Σ(i∈I) p_j × w_j × a_ij × x_i
```

Cette fonction maximise:
1. La couverture pondérée des zones (priorité × population)
2. Un bonus de redondance (10%) pour les zones critiques (priorité ≥ 7) couvertes par plusieurs caméras

### Contraintes

#### 1. Contrainte de Budget

```
Σ(i∈I) c_i × x_i ≤ B
```

Le coût total des caméras installées ne doit pas dépasser le budget disponible.

#### 2. Contrainte du Nombre de Caméras

```
Σ(i∈I) x_i ≤ K
```

Le nombre total de caméras installées ne peut excéder la limite K.

#### 3. Contraintes de Couverture

```
y_j ≤ Σ(i∈I) a_ij × x_i    ∀j ∈ J
```

Une zone j ne peut être considérée comme couverte (y_j = 1) que si au moins une caméra capable de la couvrir est installée.

**Équivalent logique:**
- Si aucune caméra ne couvre j: Σ a_ij × x_i = 0, donc y_j = 0
- Si au moins une caméra couvre j: Σ a_ij × x_i ≥ 1, donc y_j peut être 1

#### 4. Contrainte d'Utilité des Caméras

```
x_i = 0    ∀i ∈ I : Σ(j∈J) a_ij = 0
```

Une caméra ne peut être installée que si elle peut couvrir au moins une zone. Cela évite l'installation de caméras inutiles.

#### 5. Contraintes de Domaine

```
x_i ∈ {0, 1}    ∀i ∈ I
y_j ∈ {0, 1}    ∀j ∈ J
```

Toutes les variables de décision sont binaires.

## Modèle Complet Récapitulatif

```
Maximiser:   Z = Σ(j∈J) p_j × w_j × y_j

Sous contraintes:

(C1)  Σ(i∈I) c_i × x_i ≤ B

(C2)  Σ(i∈I) x_i ≤ K

(C3)  y_j ≤ Σ(i∈I) a_ij × x_i                     ∀j ∈ J

(C4)  Σ(i∈I) a_ij × x_i ≥ 2 × y_j                 ∀j ∈ J : p_j ≥ P_min

(C5)  Σ(i∈I_PTZ) x_i ≥ 0.3 × Σ(i∈I) x_i

(C6)  Σ(i∈I_c) x_i ≤ max(2, ⌊K/3⌋)                ∀c ∈ {1, ..., C}

(C7)  x_i ∈ {0, 1}                                  ∀i ∈ I

(C8)  y_j ∈ {0, 1}                                  ∀j ∈ J
```

## Modèle Complet Récapitulatif

```
Maximiser:   Z = Σ(j∈J) p_j × w_j × y_j + 0.1 × Σ(j∈J, p_j≥7) Σ(i∈I) p_j × w_j × a_ij × x_i

Sous contraintes:

(C1)  Σ(i∈I) c_i × x_i ≤ B

(C2)  Σ(i∈I) x_i ≤ K

(C3)  y_j ≤ Σ(i∈I) a_ij × x_i                     ∀j ∈ J

(C4)  x_i = 0                                      ∀i : Σ(j∈J) a_ij = 0

(C5)  x_i ∈ {0, 1}                                 ∀i ∈ I

La complexité de ce modèle est enrichie par:

1. **Multi-critères**: Fonction objectif pondérée (priorité × population)
2. **Contraintes mixtes**: Contraintes de ressources ET de couverture
3. **Bonus de redondance**: Incitation à couvrir les zones critiques avec plusieurs caméras
4. **Optimisation d'utilité**: Évite l'installation de caméras inutiles

Gurobi utilise des algorithmes avancés:
- **Branch-and-Bound**: Exploration de l'arbre de solutions
- **Coupes (Cuts)**: Renforcement de la relaxation linéaire
- **Heuristiques**: Recherche de bonnes solutions rapidement
- **Présolve**: Simplification du problème avant résolution

### Paramètres de Résolution

- **TimeLimit**: Temps maximal de calcul (300s par défaut)
- **MIPGap**: Gap d'optimalité accepté (1% par défaut)
- **OutputFlag**: Affichage des logs de résolution

## Interprétation de la Solution

### Variables Primales

- **x_i = 1**: Installer une caméra à l'emplacement i
- **y_j = 1**: La zone j est couverte

### Valeur Objectif

La valeur Z représente la **couverture pondérée totale**:
- Plus Z est élevé, meilleure est la couverture
- Prend en compte priorités ET populations

### Métriques de Performance

1. **Taux de couverture**: (Nombre de zones couvertes / Total zones) × 100%
2. **Utilisation du budget**: (Coût total / Budget max) × 100%
3. **Niveau de redondance moyen**: Nombre moyen de caméras par zone couverte
4. **Efficacité**: Zones couvertes par euro dépensé

## Extensions Possibles

Le modèle peut être enrichi avec:

1. **Fenêtres de temps**: Périodes de surveillance prioritaire
2. **Capacité limitée**: Nombre de zones qu'une caméra peut surveiller simultanément
3. **Obstacles**: Murs, bâtiments bloquant la ligne de vue
4. **Angles de vue**: Contraintes angulaires plus précises
5. **Maintenance**: Coûts opérationnels récurrents
6. **Qualité de surveillance**: Dégradation avec la distance

## Validation du Modèle

### Tests de Cohérence

1. **Budget insuffisant**: Si B < c_min, aucune caméra installée
2. **Couverture totale**: Si K et B suffisants, toutes zones couvertes
3. **Zones isolées**: Si aucune caméra ne peut couvrir une zone, y_j = 0
4. **Redondance**: Zones critiques couvertes par ≥2 caméras

### Analyse de Sensibilité

Étudier l'impact de:
- Variation du budget B
- Variation du nombre max K
- Modification des priorités p_j
- Changement des portées r_i
