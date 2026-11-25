"""
Mini-Courier Planner - Integrated Planning Pipeline
Design & Analysis of Algorithms Capstone

Orchestrates the multi-phase logistics pipeline:
Step 1: Stable Parcel Sorting (Merge Sort primary, or Quick/Bubble baseline).
Step 2: Optimal Box Packing (0/1 Knapsack via Dynamic Programming & Backtracking).
Step 3: Graph Shortest Paths (Dijkstra via hand-crafted MinHeap across chosen stops).
Step 4: Route Optimization (Nearest-Neighbour TSP Approximation + optional 2-Opt).
Step 5: Road Path Expansion (Reconstructing complete physical junction sequences).
Step 6: Empirical Profiling (High-resolution per-phase execution timing).
"""

import time
from typing import List, Dict, Tuple, Optional, Any
from courier.models import Parcel, DeliveryPlan
from courier.graph import RoadGraph
from courier.sorting import sort_parcels
from courier.knapsack import knapsack_01_dp
from courier.tsp import (
    build_distance_matrix,
    nearest_neighbour_tsp,
    two_opt_improvement,
    exact_tsp_brute_force,
    expand_tour_to_road_path,
    compute_tour_length,
)


def run_pipeline(
    graph: RoadGraph,
    parcels: List[Parcel],
    capacity: int,
    sort_algo: str = "merge",
    use_2opt: bool = True,
    run_exact_tsp: bool = False,
    dataset_name: str = "dataset",
) -> Tuple[DeliveryPlan, List[List[int]], Optional[Tuple[List[int], float]]]:
    """
    Executes the complete Mini-Courier Planner pipeline.

    Args:
        graph: Undirected RoadGraph of the delivery region.
        parcels: List of all parcels currently waiting at the depot.
        capacity: Carrying capacity of the courier van in kg.
        sort_algo: Sorting algorithm to apply ('merge', 'quick', or 'bubble').
        use_2opt: Whether to refine the Nearest-Neighbour tour using 2-Opt.
        run_exact_tsp: Whether to run exhaustive TSP (only if stops <= 10).
        dataset_name: Human-readable identifier for reporting.

    Returns:
        Tuple of:
        1. plan (DeliveryPlan): Complete structured delivery plan.
        2. dp_table (List[List[int]]): The full DP matrix from Phase 2.
        3. exact_tsp_res (Optional[Tuple[List[int], float]]): Exact tour & cost if evaluated.
    """
    times: Dict[str, float] = {}
    t_start_total = time.perf_counter()

    # =========================================================================
    # STEP 1: PARCEL SORTING
    # =========================================================================
    t0 = time.perf_counter()
    sorted_parcels = sort_parcels(parcels, algorithm=sort_algo)
    times["sort_time"] = time.perf_counter() - t0

    # =========================================================================
    # STEP 2: 0/1 KNAPSACK DYNAMIC PROGRAMMING
    # =========================================================================
    t0 = time.perf_counter()
    chosen_parcels, total_weight, total_val, dp_table = knapsack_01_dp(
        sorted_parcels, capacity
    )
    times["knapsack_time"] = time.perf_counter() - t0

    # =========================================================================
    # STEP 3: STOP IDENTIFICATION & DIJKSTRA DISTANCE MATRIX
    # =========================================================================
    t0 = time.perf_counter()
    # Distinct delivery destinations + depot 0
    stops_set = {0}
    for p in chosen_parcels:
        stops_set.add(p.dest)
    stops = sorted(list(stops_set))

    dist_matrix, all_prev = build_distance_matrix(graph, stops)
    times["dijkstra_time"] = time.perf_counter() - t0

    # =========================================================================
    # STEP 4: TSP ROUTE APPROXIMATION (+ OPTIONAL 2-OPT / EXACT)
    # =========================================================================
    t0 = time.perf_counter()
    nn_tour, nn_dist = nearest_neighbour_tsp(stops, dist_matrix, start_node=0)
    
    final_tour = nn_tour
    final_dist = nn_dist

    if use_2opt and len(stops) > 2:
        opt_tour, opt_dist = two_opt_improvement(nn_tour, dist_matrix)
        final_tour = opt_tour
        final_dist = opt_dist

    times["tsp_time"] = time.perf_counter() - t0

    exact_tsp_res = None
    if run_exact_tsp and len(stops) <= 10:
        t_exact = time.perf_counter()
        exact_tour, exact_dist = exact_tsp_brute_force(stops, dist_matrix, start_node=0)
        times["exact_tsp_time"] = time.perf_counter() - t_exact
        exact_tsp_res = (exact_tour, exact_dist)

    # =========================================================================
    # STEP 5: ROAD PATH EXPANSION (PHYSICAL JUNCTIONS)
    # =========================================================================
    t0 = time.perf_counter()
    road_path = expand_tour_to_road_path(final_tour, all_prev)
    times["expansion_time"] = time.perf_counter() - t0

    times["total_time"] = time.perf_counter() - t_start_total

    # =========================================================================
    # ASSEMBLE DELIVERY PLAN
    # =========================================================================
    capacity_utilization = (total_weight / capacity * 100.0) if capacity > 0 else 0.0

    plan = DeliveryPlan(
        dataset_name=dataset_name,
        van_capacity=capacity,
        total_parcels_available=len(parcels),
        sorted_parcels=sorted_parcels,
        chosen_parcels=chosen_parcels,
        total_weight=total_weight,
        total_value=total_val,
        capacity_utilization=round(capacity_utilization, 2),
        stops=stops,
        distance_matrix=dist_matrix,
        tsp_tour=final_tour,
        road_path=road_path,
        total_distance=round(final_dist, 2),
        execution_times=times,
    )

    return plan, dp_table, exact_tsp_res

