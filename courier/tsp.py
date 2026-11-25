"""
Mini-Courier Planner - Traveling Salesperson Problem (TSP) Module
Design & Analysis of Algorithms Capstone

Implements:
1. Metric Distance Matrix Construction: All-pairs shortest paths across stops via Dijkstra.
2. Nearest-Neighbour TSP Approximation: O(K^2) greedy tour starting & ending at depot 0.
3. 2-Opt Local Search Improvement: Iterative edge exchange to untangle crossing paths.
4. Brute-Force Exact TSP Solver: O(K!) exhaustive solver for small K (verification/ratio).
5. Road Path Expansion: Expands abstract stop-level TSP tours into concrete physical
   road junction sequences using Dijkstra's predecessor trees.
"""

import itertools
from typing import List, Dict, Tuple, Optional
from courier.graph import RoadGraph, dijkstra, reconstruct_path


def build_distance_matrix(
    graph: RoadGraph, stops: List[int]
) -> Tuple[Dict[Tuple[int, int], float], Dict[int, Dict[int, Optional[int]]]]:
    """
    Computes shortest path distances and predecessor trees between all delivery stops
    (including depot 0) by running Dijkstra from each stop.

    Complexity:
    - Time Complexity:  O(K * (|E| + |V| log |V|)) where K = len(stops).
    - Space Complexity: O(K * |V|) for distance and predecessor tables.

    Args:
        graph: The RoadGraph instance.
        stops: List of unique node IDs (must include 0 for depot).

    Returns:
        Tuple (dist_matrix, all_prev):
        - dist_matrix: Dict mapping (u, v) -> shortest distance from u to v.
        - all_prev: Dict mapping u -> prev dictionary from dijkstra(graph, u).
    """
    dist_matrix: Dict[Tuple[int, int], float] = {}
    all_prev: Dict[int, Dict[int, Optional[int]]] = {}

    for u in stops:
        dist_u, prev_u = dijkstra(graph, u)
        all_prev[u] = prev_u
        for v in stops:
            dist_matrix[(u, v)] = dist_u[v]

    return dist_matrix, all_prev


def compute_tour_length(
    tour: List[int], dist_matrix: Dict[Tuple[int, int], float]
) -> float:
    """
    Computes total round-trip distance of a given TSP tour.
    Tour must start and end at the same node: [0, s1, s2, ..., 0].
    """
    total = 0.0
    for i in range(len(tour) - 1):
        u = tour[i]
        v = tour[i + 1]
        dist = dist_matrix.get((u, v), float("inf"))
        total += dist
    return total


# ============================================================================
# 1. NEAREST-NEIGHBOUR TSP APPROXIMATION
# ============================================================================

def nearest_neighbour_tsp(
    stops: List[int],
    dist_matrix: Dict[Tuple[int, int], float],
    start_node: int = 0,
) -> Tuple[List[int], float]:
    """
    Computes a TSP tour using the Greedy Nearest-Neighbour heuristic.

    Algorithm Rationale:
    - Starts at depot (start_node = 0).
    - Iteratively selects the unvisited stop with the minimum shortest-path distance
      from the current stop.
    - Once all delivery destinations are visited, returns to the depot.
    - In metric graphs satisfying triangle inequality, NN provides an efficient
      O(K^2) approximation.

    Complexity:
    - Time Complexity:  O(K^2) where K = len(stops).
    - Space Complexity: O(K) for tour and visited tracking.

    Args:
        stops: List of unique node IDs to visit (must include start_node).
        dist_matrix: Shortest-path distances between all stop pairs.
        start_node: Starting and ending node (depot = 0).

    Returns:
        Tuple (tour, total_distance):
        - tour: Sequence of stops [0, s1, s2, ..., 0].
        - total_distance: Sum of shortest road distances along the tour.
    """
    if len(stops) <= 1:
        return [start_node, start_node], 0.0

    unvisited = set(stops)
    unvisited.remove(start_node)
    tour = [start_node]
    curr = start_node

    while unvisited:
        # Find closest unvisited node to curr
        next_node = None
        min_dist = float("inf")

        # Deterministic tie-breaking: sort unvisited candidates by node ID
        for candidate in sorted(unvisited):
            d = dist_matrix.get((curr, candidate), float("inf"))
            if d < min_dist:
                min_dist = d
                next_node = candidate

        if next_node is None:
            raise ValueError(f"Unreachable delivery stop encountered from node {curr}.")

        tour.append(next_node)
        unvisited.remove(next_node)
        curr = next_node

    # Complete the cycle by returning to the depot
    tour.append(start_node)
    total_dist = compute_tour_length(tour, dist_matrix)
    return tour, total_dist


# ============================================================================
# 2. 2-OPT LOCAL SEARCH IMPROVEMENT
# ============================================================================

def two_opt_improvement(
    initial_tour: List[int],
    dist_matrix: Dict[Tuple[int, int], float],
    max_iterations: int = 1000,
) -> Tuple[List[int], float]:
    """
    Applies the 2-Opt local search heuristic to optimize an initial TSP tour.

    Algorithm Rationale:
    - 2-Opt systematically tests whether swapping two edges reduces tour length.
    - Effectively reverses sub-segments of the tour: [t_0, ..., t_i-1, t_i, ..., t_j, t_j+1, ...]
      becomes [t_0, ..., t_i-1, t_j, ..., t_i, t_j+1, ...].
    - Untangles self-intersecting or sub-optimal detours.
    - Guaranteed to never worsen the initial tour: length(2-Opt) <= length(NN).

    Complexity:
    - Time Complexity:  O(iterations * K^2)
    - Space Complexity: O(K)

    Args:
        initial_tour: Valid TSP tour [0, s1, ..., 0].
        dist_matrix: Metric distance lookup table.
        max_iterations: Maximum search passes to prevent infinite cycles.

    Returns:
        Tuple (improved_tour, improved_distance).
    """
    tour = list(initial_tour)
    best_dist = compute_tour_length(tour, dist_matrix)
    n = len(tour)
    
    # If 3 or fewer elements (e.g. [0, 0] or [0, s, 0]), 2-opt is not applicable
    if n <= 3:
        return tour, best_dist

    improved = True
    iterations = 0

    while improved and iterations < max_iterations:
        improved = False
        iterations += 1

        # Check all candidate pairs of non-adjacent edges
        # tour has n vertices (indices 0 to n-1 where tour[0] == tour[-1])
        # Edge 1: (tour[i-1], tour[i]), Edge 2: (tour[j], tour[j+1])
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                u1 = tour[i - 1]
                v1 = tour[i]
                u2 = tour[j]
                v2 = tour[j + 1]

                current_cost = dist_matrix[(u1, v1)] + dist_matrix[(u2, v2)]
                new_cost = dist_matrix[(u1, u2)] + dist_matrix[(v1, v2)]

                # If the proposed swap strictly shortens the tour
                if new_cost < current_cost - 1e-9:
                    # Reverse the segment from index i to j inclusive
                    tour[i : j + 1] = reversed(tour[i : j + 1])
                    best_dist = compute_tour_length(tour, dist_matrix)
                    improved = True
                    break
            if improved:
                break

    return tour, best_dist


# ============================================================================
# 3. BRUTE-FORCE EXACT TSP SOLVER (Baseline for Approximation Ratio)
# ============================================================================

def exact_tsp_brute_force(
    stops: List[int],
    dist_matrix: Dict[Tuple[int, int], float],
    start_node: int = 0,
) -> Tuple[List[int], float]:
    """
    Computes the globally optimal TSP tour via exhaustive permutation search.
    Strictly intended for small instances (K <= 10 stops) to calculate the
    exact approximation ratio alpha = NN_length / OPT_length.

    Complexity:
    - Time Complexity:  O((K - 1)! * K)
    - Space Complexity: O(K)

    Args:
        stops: List of stops including start_node.
        dist_matrix: Distance lookup table.
        start_node: Depot node (0).

    Returns:
        Tuple (optimal_tour, optimal_distance).
    """
    other_stops = [s for s in stops if s != start_node]
    if not other_stops:
        return [start_node, start_node], 0.0

    best_dist = float("inf")
    best_tour: List[int] = []

    for perm in itertools.permutations(other_stops):
        candidate_tour = [start_node] + list(perm) + [start_node]
        dist = compute_tour_length(candidate_tour, dist_matrix)
        if dist < best_dist:
            best_dist = dist
            best_tour = candidate_tour

    return best_tour, best_dist


# ============================================================================
# 4. ROAD PATH EXPANSION
# ============================================================================

def expand_tour_to_road_path(
    tour: List[int],
    all_prev: Dict[int, Dict[int, Optional[int]]],
) -> List[int]:
    """
    Expands an abstract stop-level TSP tour into a seamless, unbroken sequence
    of physical road junctions using Dijkstra's shortest-path predecessor trees.

    For example, if the tour visits [0, 4, 2, 0]:
    - Leg 0 -> 4 expands to [0, 1, 4]
    - Leg 4 -> 2 expands to [4, 7, 2]
    - Leg 2 -> 0 expands to [2, 3, 0]
    Resulting detailed route: [0, 1, 4, 7, 2, 3, 0].

    Complexity:
    - Time Complexity:  O(H) where H is the total road hop count (sum of leg hops).
    - Space Complexity: O(H) for the expanded road path list.

    Args:
        tour: Stop-level TSP tour [0, s1, s2, ..., 0].
        all_prev: Dictionary containing Dijkstra predecessor trees for every stop.

    Returns:
        List of intermediate road junctions representing the exact driving route.
    """
    if len(tour) <= 1:
        return list(tour)

    full_path: List[int] = []

    for i in range(len(tour) - 1):
        u = tour[i]
        v = tour[i + 1]

        prev_u = all_prev.get(u)
        if prev_u is None:
            raise KeyError(f"Missing predecessor tree for stop {u}.")

        leg_path = reconstruct_path(prev_u, u, v)
        if not leg_path:
            raise ValueError(f"No valid road path found between stops {u} and {v}.")

        # On the first leg, include start node u; on subsequent legs, omit u
        # to prevent duplicate junction reporting
        if i == 0:
            full_path.extend(leg_path)
        else:
            full_path.extend(leg_path[1:])

    return full_path

