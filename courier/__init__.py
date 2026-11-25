"""
Mini-Courier Planner Package
Design & Analysis of Algorithms Capstone

Modules:
- models: Parcel, Edge, DeliveryPlan dataclasses
- sorting: Merge Sort, Quick Sort (3-way), Bubble Sort
- knapsack: 0/1 Knapsack DP, Backtracking, DP table formatter, Brute Force
- graph: RoadGraph, custom MinHeap, Dijkstra, Path Reconstruction, Bellman-Ford
- tsp: Nearest-Neighbour TSP, 2-Opt Improvement, Exact TSP Brute Force, Road Path Expansion
- planner: Multi-phase logistics pipeline orchestrator
- data_gen: Synthetic dataset and road network generator
"""

from courier.models import Parcel, Edge, DeliveryPlan
from courier.sorting import merge_sort, quick_sort, bubble_sort, sort_parcels
from courier.knapsack import knapsack_01_dp, format_dp_table, knapsack_brute_force
from courier.graph import RoadGraph, MinHeap, dijkstra, reconstruct_path, bellman_ford
from courier.tsp import (
    build_distance_matrix,
    nearest_neighbour_tsp,
    two_opt_improvement,
    exact_tsp_brute_force,
    expand_tour_to_road_path,
    compute_tour_length,
)
from courier.planner import run_pipeline
from courier.data_gen import (
    generate_connected_graph,
    generate_parcels,
    build_dataset_dict,
    save_dataset,
    load_dataset,
)

__all__ = [
    "Parcel",
    "Edge",
    "DeliveryPlan",
    "merge_sort",
    "quick_sort",
    "bubble_sort",
    "sort_parcels",
    "knapsack_01_dp",
    "format_dp_table",
    "knapsack_brute_force",
    "RoadGraph",
    "MinHeap",
    "dijkstra",
    "reconstruct_path",
    "bellman_ford",
    "build_distance_matrix",
    "nearest_neighbour_tsp",
    "two_opt_improvement",
    "exact_tsp_brute_force",
    "expand_tour_to_road_path",
    "compute_tour_length",
    "run_pipeline",
    "generate_connected_graph",
    "generate_parcels",
    "build_dataset_dict",
    "save_dataset",
    "load_dataset",
]

