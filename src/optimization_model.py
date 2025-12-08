"""
Module de modélisation et résolution du problème de Couverture Maximale
pour le positionnement optimal de caméras de surveillance.

Ce module implémente un modèle PLNE (Programmation Linéaire en Nombres Entiers)
pour maximiser la couverture de zones à surveiller avec un budget limité de caméras.
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np
from typing import Dict, List, Tuple, Optional
import time


class MaximalCoveringLocationModel:
    """
    Modèle d'optimisation pour le problème de couverture maximale
    appliqué au positionnement de caméras de surveillance.
    """
    
    def __init__(self):
        """Initialise le modèle d'optimisation."""
        self.model = None
        self.x = {}  # Variables de décision pour l'installation de caméras
        self.y = {}  # Variables de décision pour la couverture des zones
        self.solution = {}
        self.objective_value = 0
        self.solve_time = 0
        
        # Paramètres du problème
        self.zones = []
        self.camera_locations = []
        self.zone_priorities = {}
        self.zone_populations = {}
        self.camera_costs = {}
        self.camera_ranges = {}
        self.camera_angles = {}
        self.max_cameras = 0
        self.max_budget = 0
        self.coverage_matrix = None
        self.time_windows = {}  # Fenêtres de temps pour surveillance prioritaire
        self.camera_types = {}  # Types de caméras (fixe, PTZ, thermique, etc.)
        
    def set_problem_data(self, 
                        zones: List[Tuple[float, float]],
                        camera_locations: List[Tuple[float, float]],
                        zone_priorities: Dict[int, float],
                        zone_populations: Dict[int, int],
                        camera_costs: Dict[int, float],
                        camera_ranges: Dict[int, float],
                        camera_angles: Dict[int, float],
                        max_cameras: int,
                        max_budget: float,
                        time_windows: Optional[Dict[int, List[int]]] = None,
                        camera_types: Optional[Dict[int, str]] = None):
        """
        Définit les données du problème d'optimisation.
        
        Args:
            zones: Liste de coordonnées (x, y) des zones à couvrir
            camera_locations: Liste de coordonnées possibles pour les caméras
            zone_priorities: Priorités de chaque zone (risque, valeur stratégique)
            zone_populations: Population ou densité de chaque zone
            camera_costs: Coût d'installation de chaque caméra
            camera_ranges: Portée de surveillance de chaque caméra (en mètres)
            camera_angles: Angle de vision de chaque caméra (en degrés)
            max_cameras: Nombre maximum de caméras à installer
            max_budget: Budget total disponible
            time_windows: Périodes de surveillance prioritaire par zone
            camera_types: Types de caméras (fixe, PTZ, thermique, etc.)
        """
        self.zones = zones
        self.camera_locations = camera_locations
        self.zone_priorities = zone_priorities
        self.zone_populations = zone_populations
        self.camera_costs = camera_costs
        self.camera_ranges = camera_ranges
        self.camera_angles = camera_angles
        self.max_cameras = max_cameras
        self.max_budget = max_budget
        self.time_windows = time_windows or {}
        self.camera_types = camera_types or {}
        
        # Calculer la matrice de couverture
        self._compute_coverage_matrix()
        
    def _compute_coverage_matrix(self):
        """
        Calcule la matrice de couverture indiquant quelles zones peuvent être
        surveillées par quelles caméras en fonction de la distance et de l'angle.
        """
        n_zones = len(self.zones)
        n_cameras = len(self.camera_locations)
        self.coverage_matrix = np.zeros((n_cameras, n_zones), dtype=int)
        
        for i, cam_pos in enumerate(self.camera_locations):
            cam_range = self.camera_ranges.get(i, 50.0)  # Par défaut 50m
            
            for j, zone_pos in enumerate(self.zones):
                # Calculer la distance euclidienne
                distance = np.sqrt(
                    (cam_pos[0] - zone_pos[0])**2 + 
                    (cam_pos[1] - zone_pos[1])**2
                )
                
                # Une zone est couverte si elle est dans la portée de la caméra
                if distance <= cam_range:
                    self.coverage_matrix[i, j] = 1
                    
    def build_model(self):
        """
        Construit le modèle d'optimisation Gurobi avec toutes les contraintes.
        
        Modèle PLNE:
        - Variables de décision:
            x_i ∈ {0,1}: 1 si une caméra est installée à l'emplacement i
            y_j ∈ {0,1}: 1 si la zone j est couverte
            
        - Fonction objectif:
            Maximiser Σ(priorité_j × population_j × y_j)
            
        - Contraintes:
            1. Budget: Σ(coût_i × x_i) ≤ Budget_max
            2. Nombre de caméras: Σ(x_i) ≤ Nombre_max_caméras
            3. Couverture: y_j ≤ Σ(couverture_ij × x_i) pour tout j
            4. Types de caméras: contraintes spécifiques par type
            5. Fenêtres de temps: contraintes de couverture temporelle
        """
        try:
            # Créer le modèle Gurobi
            self.model = gp.Model("MaximalCoveringLocationProblem")
            
            n_zones = len(self.zones)
            n_cameras = len(self.camera_locations)
            
            # Variables de décision
            # x_i: 1 si une caméra est installée à l'emplacement i
            self.x = {}
            for i in range(n_cameras):
                cam_type = self.camera_types.get(i, "fixe")
                self.x[i] = self.model.addVar(
                    vtype=GRB.BINARY, 
                    name=f"x_{i}_cam_{cam_type}"
                )
            
            # y_j: 1 si la zone j est couverte
            self.y = {}
            for j in range(n_zones):
                self.y[j] = self.model.addVar(
                    vtype=GRB.BINARY, 
                    name=f"y_{j}_zone"
                )
            
            # Fonction objectif: Maximiser la couverture pondérée
            objective = gp.quicksum(
                self.zone_priorities.get(j, 1.0) * 
                self.zone_populations.get(j, 1) * 
                self.y[j]
                for j in range(n_zones)
            )
            self.model.setObjective(objective, GRB.MAXIMIZE)
            
            # Contrainte 1: Budget maximal
            budget_constraint = gp.quicksum(
                self.camera_costs.get(i, 1000.0) * self.x[i]
                for i in range(n_cameras)
            )
            self.model.addConstr(
                budget_constraint <= self.max_budget,
                name="budget_constraint"
            )
            
            # Contrainte 2: Nombre maximum de caméras
            self.model.addConstr(
                gp.quicksum(self.x[i] for i in range(n_cameras)) <= self.max_cameras,
                name="max_cameras_constraint"
            )
            
            # Contrainte 3: Une zone n'est couverte que si au moins une caméra la couvre
            for j in range(n_zones):
                covering_cameras = gp.quicksum(
                    self.coverage_matrix[i, j] * self.x[i]
                    for i in range(n_cameras)
                )
                self.model.addConstr(
                    self.y[j] <= covering_cameras,
                    name=f"coverage_zone_{j}"
                )
            
            # Contraintes supplémentaires pour la complexité
            
            # Contrainte 4: Redondance de couverture pour les zones critiques
            # Les zones avec priorité >= 5 doivent être couvertes par au moins 2 caméras
            for j in range(n_zones):
                if self.zone_priorities.get(j, 1.0) >= 5.0:
                    redundant_coverage = gp.quicksum(
                        self.coverage_matrix[i, j] * self.x[i]
                        for i in range(n_cameras)
                    )
                    self.model.addConstr(
                        redundant_coverage >= 2 * self.y[j],
                        name=f"redundancy_critical_zone_{j}"
                    )
            
            # Contrainte 5: Contraintes sur les types de caméras
            # Au moins 30% des caméras installées doivent être PTZ (Pan-Tilt-Zoom)
            ptz_cameras = [i for i, t in self.camera_types.items() if t == "PTZ"]
            if ptz_cameras:
                self.model.addConstr(
                    gp.quicksum(self.x[i] for i in ptz_cameras) >= 
                    0.3 * gp.quicksum(self.x[i] for i in range(n_cameras)),
                    name="min_ptz_cameras"
                )
            
            # Contrainte 6: Limitation des caméras par zone géographique
            # (pour éviter la concentration excessive)
            zones_geo = self._create_geographic_clusters(4)
            for cluster_id, camera_indices in zones_geo.items():
                if len(camera_indices) > 0:
                    self.model.addConstr(
                        gp.quicksum(self.x[i] for i in camera_indices) <= 
                        max(2, self.max_cameras // 3),
                        name=f"geographic_distribution_cluster_{cluster_id}"
                    )
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la construction du modèle: {e}")
            return False
    
    def _create_geographic_clusters(self, n_clusters: int) -> Dict[int, List[int]]:
        """
        Crée des clusters géographiques de caméras pour la contrainte de distribution.
        
        Args:
            n_clusters: Nombre de clusters à créer
            
        Returns:
            Dictionnaire {cluster_id: [indices_caméras]}
        """
        if not self.camera_locations:
            return {}
        
        # Simple clustering basé sur les coordonnées
        positions = np.array(self.camera_locations)
        
        # Diviser l'espace en grille
        x_min, x_max = positions[:, 0].min(), positions[:, 0].max()
        y_min, y_max = positions[:, 1].min(), positions[:, 1].max()
        
        n_rows = int(np.sqrt(n_clusters))
        n_cols = (n_clusters + n_rows - 1) // n_rows
        
        x_step = (x_max - x_min) / n_cols if x_max > x_min else 1
        y_step = (y_max - y_min) / n_rows if y_max > y_min else 1
        
        clusters = {i: [] for i in range(n_clusters)}
        
        for idx, (x, y) in enumerate(self.camera_locations):
            col = min(int((x - x_min) / x_step) if x_step > 0 else 0, n_cols - 1)
            row = min(int((y - y_min) / y_step) if y_step > 0 else 0, n_rows - 1)
            cluster_id = row * n_cols + col
            if cluster_id < n_clusters:
                clusters[cluster_id].append(idx)
        
        return clusters
    
    def solve(self, time_limit: int = 300, gap: float = 0.01) -> bool:
        """
        Résout le modèle d'optimisation.
        
        Args:
            time_limit: Temps maximal de résolution (secondes)
            gap: Gap d'optimalité accepté (1% par défaut)
            
        Returns:
            True si une solution a été trouvée, False sinon
        """
        if self.model is None:
            print("Le modèle n'a pas été construit.")
            return False
        
        try:
            # Paramètres du solveur
            self.model.setParam('TimeLimit', time_limit)
            self.model.setParam('MIPGap', gap)
            self.model.setParam('OutputFlag', 1)
            
            # Résoudre
            start_time = time.time()
            self.model.optimize()
            self.solve_time = time.time() - start_time
            
            # Vérifier le statut de la solution
            if self.model.status == GRB.OPTIMAL:
                print(f"Solution optimale trouvée en {self.solve_time:.2f} secondes")
                self._extract_solution()
                return True
            elif self.model.status == GRB.TIME_LIMIT:
                print(f"Limite de temps atteinte. Meilleure solution trouvée.")
                if self.model.SolCount > 0:
                    self._extract_solution()
                    return True
                return False
            else:
                print(f"Aucune solution trouvée. Statut: {self.model.status}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de la résolution: {e}")
            return False
    
    def _extract_solution(self):
        """Extrait la solution du modèle résolu."""
        self.solution = {
            'cameras_installed': [],
            'zones_covered': [],
            'cameras_positions': [],
            'coverage_details': {},
            'total_cost': 0,
            'coverage_percentage': 0,
            'total_priority_coverage': 0
        }
        
        n_zones = len(self.zones)
        n_cameras = len(self.camera_locations)
        
        # Extraire les caméras installées
        for i in range(n_cameras):
            if self.x[i].X > 0.5:  # Variable binaire
                self.solution['cameras_installed'].append(i)
                self.solution['cameras_positions'].append(self.camera_locations[i])
                self.solution['total_cost'] += self.camera_costs.get(i, 1000.0)
        
        # Extraire les zones couvertes
        covered_zones = 0
        total_priority = 0
        for j in range(n_zones):
            if self.y[j].X > 0.5:
                self.solution['zones_covered'].append(j)
                covered_zones += 1
                priority = self.zone_priorities.get(j, 1.0)
                population = self.zone_populations.get(j, 1)
                total_priority += priority * population
                
                # Détails de couverture pour cette zone
                covering_cams = [
                    i for i in self.solution['cameras_installed']
                    if self.coverage_matrix[i, j] == 1
                ]
                self.solution['coverage_details'][j] = covering_cams
        
        self.solution['coverage_percentage'] = (covered_zones / n_zones * 100) if n_zones > 0 else 0
        self.solution['total_priority_coverage'] = total_priority
        self.objective_value = self.model.ObjVal
    
    def get_solution_summary(self) -> Dict:
        """
        Retourne un résumé de la solution.
        
        Returns:
            Dictionnaire contenant les informations principales de la solution
        """
        if not self.solution:
            return {}
        
        return {
            'objective_value': self.objective_value,
            'n_cameras_installed': len(self.solution['cameras_installed']),
            'n_zones_covered': len(self.solution['zones_covered']),
            'total_cost': self.solution['total_cost'],
            'budget_utilization': (self.solution['total_cost'] / self.max_budget * 100) if self.max_budget > 0 else 0,
            'coverage_percentage': self.solution['coverage_percentage'],
            'total_priority_coverage': self.solution['total_priority_coverage'],
            'solve_time': self.solve_time,
            'cameras_installed': self.solution['cameras_installed'],
            'zones_covered': self.solution['zones_covered'],
            'coverage_details': self.solution['coverage_details']
        }
    
    def get_detailed_solution(self) -> Dict:
        """Retourne la solution complète avec tous les détails."""
        summary = self.get_solution_summary()
        
        # Ajouter les détails des caméras
        camera_details = []
        for cam_id in self.solution['cameras_installed']:
            pos = self.camera_locations[cam_id]
            zones_covered = [j for j, cams in self.solution['coverage_details'].items() if cam_id in cams]
            
            camera_details.append({
                'id': cam_id,
                'position': pos,
                'type': self.camera_types.get(cam_id, 'fixe'),
                'cost': self.camera_costs.get(cam_id, 1000.0),
                'range': self.camera_ranges.get(cam_id, 50.0),
                'angle': self.camera_angles.get(cam_id, 360.0),
                'zones_covered': zones_covered,
                'n_zones_covered': len(zones_covered)
            })
        
        summary['camera_details'] = camera_details
        
        # Ajouter les détails des zones
        zone_details = []
        for j, zone_pos in enumerate(self.zones):
            is_covered = j in self.solution['zones_covered']
            covering_cams = self.solution['coverage_details'].get(j, [])
            
            zone_details.append({
                'id': j,
                'position': zone_pos,
                'priority': self.zone_priorities.get(j, 1.0),
                'population': self.zone_populations.get(j, 1),
                'is_covered': is_covered,
                'covering_cameras': covering_cams,
                'redundancy_level': len(covering_cams)
            })
        
        summary['zone_details'] = zone_details
        
        return summary
