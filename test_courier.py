"""
Mini-Courier Planner - Test Suite
Design & Analysis of Algorithms Capstone

Comprehensive verification of all algorithms against independent methods:
1. Sorting: Merge Sort, Quick Sort (3-way), Bubble Sort verified against Python's sorted().
   Stability verification for Merge Sort.
2. 0/1 Knapsack: DP + Backtracking verified against exhaustive O(2^n) brute-force.
3. Graph & Shortest Paths: Custom MinHeap verified; Dijkstra verified against Bellman-Ford O(V*E).
4. Path Reconstruction: Junction continuity and distance consistency checks.
5. TSP: Nearest-Neighbour tour validity and lower-bound check vs Exact Brute-Force O(K!).
   2-Opt improvement monotonicity check (length(2-opt) <= length(NN)).
6. End-to-End Pipeline: Full integration on seeded benchmark data.

Run directly via:
    python test_courier.py
"""

import math
import random
import unittest
from typing import List

from courier.models import Parcel, DeliveryPlan
from courier.sorting import merge_sort, quick_sort, bubble_sort, sort_parcels
from courier.knapsack import knapsack_01_dp, knapsack_brute_force
from courier.graph import (
    RoadGraph,
    MinHeap,
    dijkstra,
    bellman_ford,
    reconstruct_path,
)
from courier.tsp import (
    build_distance_matrix,
    nearest_neighbour_tsp,
    two_opt_improvement,
    exact_tsp_brute_force,
    expand_tour_to_road_path,
    compute_tour_length,
)
from courier.data_gen import (
    generate_connected_graph,
    generate_parcels,
    load_dataset,
)
from courier.planner import run_pipeline


class TestSortingAlgorithms(unittest.TestCase):
    """Verifies hand-crafted sorting algorithms against Python's built-in sorted()."""

    def setUp(self):
        # Reproducible random parcel generator
        self.rng = random.Random(12345)

    def _generate_random_parcels(self, count: int) -> List[Parcel]:
        parcels = []
        for i in range(count):
            p = Parcel(
                pid=f"P{i:03d}",
                dest=self.rng.randint(1, 20),
                weight=self.rng.randint(1, 15),
                priority=self.rng.randint(1, 5),
                deadline=self.rng.randint(2, 48),
            )
            parcels.append(p)
        return parcels

    def test_merge_sort_vs_python_sorted(self):
        """Verifies Merge Sort output matches Python's built-in sorted() on 200 random parcels."""
        parcels = self._generate_random_parcels(200)
        expected = sorted(parcels, key=lambda p: p.sort_key)
        actual = merge_sort(parcels)

        self.assertEqual(len(actual), len(expected))
        for exp, act in zip(expected, actual):
            self.assertEqual(exp.sort_key, act.sort_key)

    def test_merge_sort_stability(self):
        """
        Verifies that Merge Sort is STABLE: parcels with identical (deadline, -priority)
        must retain their relative insertion order.
        """
        # Create parcels where all have identical deadline=10, priority=3
        parcels = [
            Parcel(pid=f"ID_{i}", dest=1, weight=5, priority=3, deadline=10)
            for i in range(20)
        ]
        sorted_parcels = merge_sort(parcels)
        # Verify the sequence of PIDs did not change
        original_pids = [p.pid for p in parcels]
        sorted_pids = [p.pid for p in sorted_parcels]
        self.assertEqual(original_pids, sorted_pids, "Merge Sort failed stability guarantee!")

    def test_quick_sort_3way_correctness(self):
        """Verifies 3-way randomized Quick Sort against Python sorted() with heavy duplicates."""
        # Mix of random and identical parcels
        parcels = self._generate_random_parcels(100)
        # Inject 30 identical parcels to stress-test 3-way partitioning
        identical = [
            Parcel(pid=f"DUP_{i}", dest=2, weight=4, priority=4, deadline=12)
            for i in range(30)
        ]
        test_set = parcels + identical
        self.rng.shuffle(test_set)

        expected = sorted(test_set, key=lambda p: p.sort_key)
        actual = quick_sort(test_set)

        self.assertEqual(len(actual), len(expected))
        actual_keys = [p.sort_key for p in actual]
        expected_keys = [p.sort_key for p in expected]
        self.assertEqual(actual_keys, expected_keys)

    def test_bubble_sort_correctness(self):
        """Verifies Bubble Sort against Python sorted()."""
        parcels = self._generate_random_parcels(50)
        expected = sorted(parcels, key=lambda p: p.sort_key)
        actual = bubble_sort(parcels)

        actual_keys = [p.sort_key for p in actual]
        expected_keys = [p.sort_key for p in expected]
        self.assertEqual(actual_keys, expected_keys)

    def test_sort_edge_cases(self):
        """Verifies sorting behaves correctly on empty lists and single-element lists."""
        for sort_fn in [merge_sort, quick_sort, bubble_sort]:
            self.assertEqual(sort_fn([]), [])
            single = [Parcel(pid="P01", dest=1, weight=2, priority=3, deadline=5)]
            self.assertEqual(sort_fn(single), single)


class TestKnapsackDP(unittest.TestCase):
    """Verifies 0/1 Knapsack DP against exhaustive O(2^n) Brute Force."""

    def test_dp_vs_brute_force_on_random_cases(self):
        """Compares DP solution with 2^n exhaustive brute force across 10 random small scenarios."""
        rng = random.Random(42)

        for case_idx in range(10):
            n_items = rng.randint(5, 11)  # 2^11 = 2048 operations, very fast
            capacity = rng.randint(15, 30)

            parcels = []
            for i in range(n_items):
                parcels.append(
                    Parcel(
                        pid=f"P{i}",
                        dest=1,
                        weight=rng.randint(1, 10),
                        priority=rng.randint(1, 5),
                        deadline=rng.randint(2, 40),
                    )
                )

            chosen_dp, weight_dp, val_dp, _ = knapsack_01_dp(parcels, capacity)
            chosen_bf, weight_bf, val_bf = knapsack_brute_force(parcels, capacity)

            self.assertEqual(
                val_dp,
                val_bf,
                f"Case {case_idx}: DP value {val_dp} != BF value {val_bf}",
            )
            self.assertLessEqual(
                weight_dp,
                capacity,
                f"Case {case_idx}: DP weight {weight_dp} exceeds capacity {capacity}",
            )
            # Verify sum of chosen weights and values match
            self.assertEqual(sum(p.weight for p in chosen_dp), weight_dp)
            self.assertEqual(sum(p.value for p in chosen_dp), val_dp)

    def test_knapsack_boundary_cases(self):
        """Verifies capacity=0, empty parcels, and items larger than capacity."""
        parcels = [
            Parcel(pid="P1", dest=1, weight=10, priority=5, deadline=5),
            Parcel(pid="P2", dest=2, weight=15, priority=4, deadline=10),
        ]
        # Zero capacity
        chosen, w, v, dp = knapsack_01_dp(parcels, 0)
        self.assertEqual(chosen, [])
        self.assertEqual(w, 0)
        self.assertEqual(v, 0)

        # Empty items list
        chosen, w, v, dp = knapsack_01_dp([], 20)
        self.assertEqual(chosen, [])
        self.assertEqual(w, 0)
        self.assertEqual(v, 0)

        # Items all larger than capacity
        chosen, w, v, dp = knapsack_01_dp(parcels, 5)
        self.assertEqual(chosen, [])
        self.assertEqual(w, 0)
        self.assertEqual(v, 0)


class TestGraphAndDijkstra(unittest.TestCase):
    """Verifies hand-crafted MinHeap and Dijkstra vs Bellman-Ford."""

    def test_min_heap_invariant(self):
        """Verifies custom MinHeap extracts elements in non-decreasing priority order."""
        heap = MinHeap()
        self.assertTrue(heap.is_empty())
        self.assertEqual(len(heap), 0)

        rng = random.Random(999)
        values = [rng.uniform(-100, 100) for _ in range(150)]
        for v in values:
            heap.insert(v, f"val_{v}")

        self.assertEqual(len(heap), 150)
        extracted = []
        while not heap.is_empty():
            k, val = heap.extract_min()
            extracted.append(k)

        # Assert extracted order is monotonically sorted
        self.assertEqual(extracted, sorted(values))

        # Test empty extract raises IndexError
        with self.assertRaises(IndexError):
            heap.extract_min()

    def test_dijkstra_vs_bellman_ford(self):
        """
        Tests Dijkstra (custom MinHeap) against Bellman-Ford on multiple random connected graphs.
        Both algorithms must return identical shortest-path distances for every reachable vertex.
        """
        for seed in [111, 222, 333]:
            # Generate connected graph with 25 nodes
            graph = generate_connected_graph(num_nodes=25, seed=seed, grid_size=100.0)

            # Test from depot 0 and another arbitrary node
            for start_node in [0, 7, 18]:
                dijk_dist, dijk_prev = dijkstra(graph, start_node)
                bf_dist, bf_prev = bellman_ford(graph, start_node)

                for node in range(25):
                    self.assertAlmostEqual(
                        dijk_dist[node],
                        bf_dist[node],
                        places=4,
                        msg=f"Discrepancy at node {node} starting from {start_node} (Seed {seed})",
                    )

    def test_path_reconstruction(self):
        """Verifies reconstruct_path yields valid contiguous edges matching total distance."""
        graph = generate_connected_graph(num_nodes=15, seed=555)
        dist, prev = dijkstra(graph, 0)

        for target in range(1, 15):
            path = reconstruct_path(prev, 0, target)
            self.assertEqual(path[0], 0)
            self.assertEqual(path[-1], target)

            # Sum edge weights along the reconstructed path
            calculated_dist = 0.0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                # Find edge weight in graph
                w = next(weight for neighbor, weight in graph.get_neighbors(u) if neighbor == v)
                calculated_dist += w

            self.assertAlmostEqual(calculated_dist, dist[target], places=4)


class TestTSP(unittest.TestCase):
    """Verifies Nearest-Neighbour TSP approximation, 2-Opt improvement, and exact comparison."""

    def test_nearest_neighbour_validity(self):
        """Verifies NN tour starts at depot 0, ends at depot 0, and visits all stops."""
        graph = generate_connected_graph(num_nodes=15, seed=777)
        stops = [0, 2, 5, 8, 11]
        dist_matrix, all_prev = build_distance_matrix(graph, stops)

        tour, length = nearest_neighbour_tsp(stops, dist_matrix, start_node=0)

        self.assertEqual(tour[0], 0)
        self.assertEqual(tour[-1], 0)
        # All stops in set must be visited
        self.assertEqual(set(tour), set(stops))
        # Total stops in tour is len(stops) + 1 (cycle closing)
        self.assertEqual(len(tour), len(stops) + 1)
        self.assertGreater(length, 0.0)

    def test_nearest_neighbour_vs_brute_force_optimum(self):
        """
        Verifies that NN tour length is NEVER shorter than the exact brute-force optimum,
        and computes the approximation ratio (must be >= 1.0).
        """
        graph = generate_connected_graph(num_nodes=20, seed=888)

        # Test varying stop counts: 4, 6, 7
        for k in [4, 6, 7]:
            stops = [0] + list(range(1, k))
            dist_matrix, _ = build_distance_matrix(graph, stops)

            nn_tour, nn_dist = nearest_neighbour_tsp(stops, dist_matrix, start_node=0)
            exact_tour, exact_dist = exact_tsp_brute_force(stops, dist_matrix, start_node=0)

            # Heuristic tour length can never be strictly less than global optimum
            self.assertGreaterEqual(
                nn_dist,
                exact_dist - 1e-9,
                f"NN distance {nn_dist} was lower than exact optimal distance {exact_dist}!",
            )
            ratio = nn_dist / exact_dist
            self.assertGreaterEqual(ratio, 0.9999)
            # Typically for small planar metric TSP, NN is within 1.5x of optimum
            self.assertLess(ratio, 2.0)

    def test_two_opt_monotonic_improvement(self):
        """Verifies that 2-Opt local search never increases the tour length."""
        graph = generate_connected_graph(num_nodes=25, seed=999)
        stops = [0, 3, 6, 9, 12, 15, 18, 21]
        dist_matrix, _ = build_distance_matrix(graph, stops)

        nn_tour, nn_dist = nearest_neighbour_tsp(stops, dist_matrix, start_node=0)
        opt_tour, opt_dist = two_opt_improvement(nn_tour, dist_matrix)

        # Monotonic improvement guarantee
        self.assertLessEqual(
            opt_dist,
            nn_dist + 1e-9,
            f"2-Opt distance {opt_dist} increased relative to NN {nn_dist}!",
        )
        self.assertEqual(opt_tour[0], 0)
        self.assertEqual(opt_tour[-1], 0)
        self.assertEqual(set(opt_tour), set(stops))

    def test_road_path_expansion_integrity(self):
        """Verifies that expanded road paths form unbroken physical edge sequences."""
        graph = generate_connected_graph(num_nodes=15, seed=444)
        stops = [0, 4, 7, 12]
        dist_matrix, all_prev = build_distance_matrix(graph, stops)
        tour, tour_len = nearest_neighbour_tsp(stops, dist_matrix, start_node=0)

        road_path = expand_tour_to_road_path(tour, all_prev)

        # Verify contiguous edges in graph
        expanded_len = 0.0
        for i in range(len(road_path) - 1):
            u = road_path[i]
            v = road_path[i + 1]
            neighbors = dict(graph.get_neighbors(u))
            self.assertIn(v, neighbors, f"Edge ({u}, {v}) in expanded road path does not exist in graph!")
            expanded_len += neighbors[v]

        self.assertAlmostEqual(expanded_len, tour_len, places=3)


class TestFullPipeline(unittest.TestCase):
    """End-to-End integration test on small seeded dataset."""

    def test_pipeline_on_small_dataset(self):
        graph, parcels, capacity, name = load_dataset("data/small.json")
        plan, dp_table, exact_res = run_pipeline(
            graph=graph,
            parcels=parcels,
            capacity=capacity,
            sort_algo="merge",
            use_2opt=True,
            run_exact_tsp=True,
            dataset_name=name,
        )

        self.assertIsInstance(plan, DeliveryPlan)
        self.assertEqual(plan.van_capacity, 20)
        self.assertLessEqual(plan.total_weight, 20)
        self.assertGreater(plan.total_value, 0)
        self.assertGreater(len(plan.chosen_parcels), 0)
        self.assertEqual(plan.tsp_tour[0], 0)
        self.assertEqual(plan.tsp_tour[-1], 0)
        self.assertGreater(plan.total_distance, 0.0)
        self.assertTrue(all(k in plan.execution_times for k in ["sort_time", "knapsack_time", "dijkstra_time", "tsp_time"]))


def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromModule(unittest.importorskip("__main__"))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        exit(1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

