"""
Mini-Courier Planner - Comprehensive Benchmark Suite
Design & Analysis of Algorithms Capstone

Benchmarks and empirical complexity evaluations:
1. Sorting: Merge Sort vs Quick Sort (3-way) vs Bubble Sort across input sizes.
2. 0/1 Knapsack DP: Runtime scaling vs item count n and van capacity W.
3. Dijkstra's Algorithm: Runtime scaling vs road network size |V|.
4. TSP Tour Optimization:
   - Runtime: Nearest-Neighbour vs 2-Opt vs Exact Brute Force O(K!).
   - Approximation Quality: Heuristic Length / Optimal Length for K = 4..10 stops.
5. End-to-End Logistics Pipeline: Detailed profiling on Small, Medium, and Large datasets.

Outputs:
- results/runtime_charts.png (Multi-panel academic visualization)
- results/benchmark_results.csv (Raw tabular timings and metrics)

Usage:
    python benchmark.py
"""

import csv
import math
import os
import random
import sys
import tempfile
import time
from typing import Dict, List, Tuple, Any

# Ensure matplotlib uses temporary writable directory
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib_courier")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from courier.models import Parcel
from courier.sorting import merge_sort, quick_sort, bubble_sort
from courier.knapsack import knapsack_01_dp, knapsack_brute_force
from courier.graph import RoadGraph, dijkstra
from courier.tsp import (
    build_distance_matrix,
    nearest_neighbour_tsp,
    two_opt_improvement,
    exact_tsp_brute_force,
)
from courier.data_gen import (
    generate_connected_graph,
    generate_parcels,
    load_dataset,
)
from courier.planner import run_pipeline


def make_random_parcels(count: int, seed: int = 42) -> List[Parcel]:
    """Helper to create random parcels for benchmarking."""
    rng = random.Random(seed)
    return [
        Parcel(
            pid=f"B{i:04d}",
            dest=rng.randint(1, 100),
            weight=rng.randint(1, 15),
            priority=rng.randint(1, 5),
            deadline=rng.randint(2, 48),
        )
        for i in range(count)
    ]


# ============================================================================
# 1. SORTING BENCHMARK
# ============================================================================

def benchmark_sorting() -> Dict[str, Any]:
    print("\n[*] Running Sorting Benchmark (Merge vs Quick vs Bubble)...")
    sizes = [50, 100, 200, 500, 1000, 2000]
    merge_times = []
    quick_times = []
    bubble_times = []

    for n in sizes:
        parcels = make_random_parcels(n, seed=n + 10)

        # Merge Sort
        reps = 10 if n <= 500 else 3
        t0 = time.perf_counter()
        for _ in range(reps):
            merge_sort(parcels)
        t_merge = (time.perf_counter() - t0) / reps
        merge_times.append(t_merge * 1000.0)

        # Quick Sort
        t0 = time.perf_counter()
        for _ in range(reps):
            quick_sort(parcels)
        t_quick = (time.perf_counter() - t0) / reps
        quick_times.append(t_quick * 1000.0)

        # Bubble Sort (limit to n <= 1000 to avoid extreme delay)
        if n <= 1000:
            reps_b = 5 if n <= 200 else 1
            t0 = time.perf_counter()
            for _ in range(reps_b):
                bubble_sort(parcels)
            t_bubble = (time.perf_counter() - t0) / reps_b
            bubble_times.append(t_bubble * 1000.0)
        else:
            # Extrapolate quadratic for n=2000
            estimated = bubble_times[-1] * (n / sizes[-2]) ** 2
            bubble_times.append(estimated)

        print(f"    N={n:4d} | Merge: {merge_times[-1]:7.3f} ms | Quick: {quick_times[-1]:7.3f} ms | Bubble: {bubble_times[-1]:8.2f} ms")

    return {
        "sizes": sizes,
        "merge_times_ms": merge_times,
        "quick_times_ms": quick_times,
        "bubble_times_ms": bubble_times,
    }


# ============================================================================
# 2. KNAPSACK BENCHMARK
# ============================================================================

def benchmark_knapsack() -> Dict[str, Any]:
    print("\n[*] Running 0/1 Knapsack DP Benchmark...")
    
    # Part A: Vary n with fixed W = 60
    fixed_W = 60
    n_values = [20, 50, 100, 200, 400, 800]
    times_vs_n = []
    for n in n_values:
        parcels = make_random_parcels(n, seed=n)
        reps = 5
        t0 = time.perf_counter()
        for _ in range(reps):
            knapsack_01_dp(parcels, fixed_W)
        t_avg = (time.perf_counter() - t0) / reps
        times_vs_n.append(t_avg * 1000.0)
        print(f"    Fixed W={fixed_W} | n={n:4d} -> {times_vs_n[-1]:7.3f} ms")

    # Part B: Vary W with fixed n = 100
    fixed_n = 100
    W_values = [20, 50, 100, 200, 400, 800]
    times_vs_w = []
    parcels_fixed = make_random_parcels(fixed_n, seed=77)
    for W in W_values:
        reps = 5
        t0 = time.perf_counter()
        for _ in range(reps):
            knapsack_01_dp(parcels_fixed, W)
        t_avg = (time.perf_counter() - t0) / reps
        times_vs_w.append(t_avg * 1000.0)
        print(f"    Fixed n={fixed_n} | W={W:4d} -> {times_vs_w[-1]:7.3f} ms")

    return {
        "n_values": n_values,
        "times_vs_n_ms": times_vs_n,
        "fixed_W": fixed_W,
        "W_values": W_values,
        "times_vs_w_ms": times_vs_w,
        "fixed_n": fixed_n,
    }


# ============================================================================
# 3. DIJKSTRA BENCHMARK
# ============================================================================

def benchmark_dijkstra() -> Dict[str, Any]:
    print("\n[*] Running Dijkstra Benchmark (varying graph size |V|)...")
    v_sizes = [20, 50, 100, 200, 350, 500]
    dijkstra_times = []

    for v in v_sizes:
        graph = generate_connected_graph(num_nodes=v, seed=v, grid_size=float(v * 2))
        reps = 10
        t0 = time.perf_counter()
        for _ in range(reps):
            dijkstra(graph, start=0)
        t_avg = (time.perf_counter() - t0) / reps
        dijkstra_times.append(t_avg * 1000.0)
        num_edges = len(graph.get_all_edges())
        print(f"    |V|={v:3d}, |E|={num_edges:4d} | Dijkstra: {dijkstra_times[-1]:7.3f} ms")

    return {
        "v_sizes": v_sizes,
        "dijkstra_times_ms": dijkstra_times,
    }


# ============================================================================
# 4. TSP BENCHMARK (Runtime & Approximation Ratio)
# ============================================================================

def benchmark_tsp() -> Dict[str, Any]:
    print("\n[*] Running TSP Benchmark (Nearest-Neighbour vs 2-Opt vs Exact Brute Force)...")
    # Generate a background road network of 50 nodes
    graph = generate_connected_graph(num_nodes=50, seed=888)
    
    stop_counts = [4, 5, 6, 7, 8, 9, 10]
    nn_times = []
    opt_times = []
    exact_times = []
    nn_ratios = []
    opt_ratios = []

    for k in stop_counts:
        stops = [0] + list(range(1, k))
        dist_matrix, _ = build_distance_matrix(graph, stops)

        # Nearest Neighbour
        t0 = time.perf_counter()
        for _ in range(50):
            nn_tour, nn_dist = nearest_neighbour_tsp(stops, dist_matrix, start_node=0)
        t_nn = (time.perf_counter() - t0) / 50

        # 2-Opt
        t0 = time.perf_counter()
        for _ in range(50):
            two_opt_tour, two_opt_dist = two_opt_improvement(nn_tour, dist_matrix)
        t_2opt = (time.perf_counter() - t0) / 50

        # Exact Brute Force
        t0 = time.perf_counter()
        exact_tour, exact_dist = exact_tsp_brute_force(stops, dist_matrix, start_node=0)
        t_exact = time.perf_counter() - t0

        ratio_nn = nn_dist / exact_dist if exact_dist > 0 else 1.0
        ratio_opt = two_opt_dist / exact_dist if exact_dist > 0 else 1.0

        nn_times.append(t_nn * 1000.0)
        opt_times.append((t_nn + t_2opt) * 1000.0)
        exact_times.append(t_exact * 1000.0)
        nn_ratios.append(ratio_nn)
        opt_ratios.append(ratio_opt)

        print(f"    Stops K={k:2d} | NN: {nn_times[-1]:7.4f} ms (Ratio: {ratio_nn:.3f}) | 2-Opt: {opt_times[-1]:7.4f} ms (Ratio: {ratio_opt:.3f}) | Exact: {exact_times[-1]:8.2f} ms")

    return {
        "stop_counts": stop_counts,
        "nn_times_ms": nn_times,
        "opt_times_ms": opt_times,
        "exact_times_ms": exact_times,
        "nn_ratios": nn_ratios,
        "opt_ratios": opt_ratios,
    }


# ============================================================================
# 5. DATASETS PIPELINE BENCHMARK
# ============================================================================

def benchmark_datasets_pipeline() -> List[Dict[str, Any]]:
    print("\n[*] Running End-to-End Pipeline on Standard Seeded Datasets...")
    datasets = ["data/small.json", "data/medium.json", "data/large.json"]
    results = []

    for path in datasets:
        if not os.path.exists(path):
            from make_datasets import generate_all_datasets
            generate_all_datasets()
            break

    for path in datasets:
        graph, parcels, capacity, name = load_dataset(path)
        # Execute pipeline
        plan, dp_table, exact_res = run_pipeline(
            graph=graph,
            parcels=parcels,
            capacity=capacity,
            sort_algo="merge",
            use_2opt=True,
            run_exact_tsp=False,
            dataset_name=name,
        )

        entry = {
            "dataset": os.path.basename(path),
            "nodes": graph.num_nodes,
            "edges": len(graph.get_all_edges()),
            "parcels_available": len(parcels),
            "capacity_kg": capacity,
            "parcels_chosen": len(plan.chosen_parcels),
            "payload_utilization_pct": plan.capacity_utilization,
            "total_value": plan.total_value,
            "unique_stops": len(plan.stops),
            "tour_distance_km": plan.total_distance,
            "road_path_hops": len(plan.road_path) - 1,
            "sort_time_ms": plan.execution_times.get("sort_time", 0) * 1000.0,
            "knapsack_time_ms": plan.execution_times.get("knapsack_time", 0) * 1000.0,
            "dijkstra_time_ms": plan.execution_times.get("dijkstra_time", 0) * 1000.0,
            "tsp_time_ms": plan.execution_times.get("tsp_time", 0) * 1000.0,
            "expansion_time_ms": plan.execution_times.get("expansion_time", 0) * 1000.0,
            "total_time_ms": plan.execution_times.get("total_time", 0) * 1000.0,
        }
        results.append(entry)

        print(f"\n    Dataset: {entry['dataset']}")
        print(f"      Graph: {entry['nodes']} nodes, {entry['edges']} edges | Capacity: {entry['capacity_kg']} kg")
        print(f"      Packed: {entry['parcels_chosen']} parcels ({entry['payload_utilization_pct']}%) -> Value: {entry['total_value']}")
        print(f"      Route: {entry['unique_stops']} stops, {entry['tour_distance_km']:.1f} km, {entry['road_path_hops']} road hops")
        print(f"      Times: Sort={entry['sort_time_ms']:.2f}ms, DP={entry['knapsack_time_ms']:.2f}ms, Dijkstra={entry['dijkstra_time_ms']:.2f}ms, TSP={entry['tsp_time_ms']:.2f}ms, Total={entry['total_time_ms']:.2f}ms")

    return results


# ============================================================================
# EXPORT AND PLOTTING
# ============================================================================

def export_results_to_csv(dataset_results: List[Dict[str, Any]], filepath: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    if not dataset_results:
        return
    keys = list(dataset_results[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(dataset_results)
    print(f"\n[+] Tabular benchmark metrics exported to: {filepath}")


def plot_benchmark_charts(
    sort_data: Dict[str, Any],
    knap_data: Dict[str, Any],
    dijk_data: Dict[str, Any],
    tsp_data: Dict[str, Any],
    filepath: str,
) -> None:
    """
    Renders a 6-panel comprehensive academic performance chart.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    fig, axs = plt.subplots(2, 3, figsize=(18, 11), dpi=160)
    fig.suptitle(
        "Mini-Courier Planner: Algorithmic Performance Benchmarking\n"
        "Design & Analysis of Algorithms Capstone - ETCCDA302",
        fontsize=14, weight="bold", y=0.98
    )

    # 1. Sorting Algorithms
    ax = axs[0, 0]
    ax.plot(sort_data["sizes"], sort_data["bubble_times_ms"], "o--", color="#D92D20", label="Bubble Sort O(n²)", linewidth=2)
    ax.plot(sort_data["sizes"], sort_data["merge_times_ms"], "s-", color="#1570EF", label="Merge Sort O(n log n)", linewidth=2)
    ax.plot(sort_data["sizes"], sort_data["quick_times_ms"], "^-", color="#099250", label="Quick Sort (3-way)", linewidth=2)
    ax.set_title("1. Sorting Algorithms: Runtime vs Input Size", fontsize=11, weight="bold")
    ax.set_xlabel("Number of Parcels (n)")
    ax.set_ylabel("Execution Time (ms)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    # 2. Knapsack vs n
    ax = axs[0, 1]
    ax.plot(knap_data["n_values"], knap_data["times_vs_n_ms"], "s-", color="#7A5AF8", linewidth=2, label=f"W = {knap_data['fixed_W']} kg")
    ax.set_title("2. 0/1 Knapsack DP: Runtime vs Item Count (n)", fontsize=11, weight="bold")
    ax.set_xlabel("Number of Candidate Parcels (n)")
    ax.set_ylabel("Execution Time (ms)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    # 3. Knapsack vs W
    ax = axs[0, 2]
    ax.plot(knap_data["W_values"], knap_data["times_vs_w_ms"], "d-", color="#EE46BC", linewidth=2, label=f"n = {knap_data['fixed_n']} parcels")
    ax.set_title("3. 0/1 Knapsack DP: Runtime vs Van Capacity (W)", fontsize=11, weight="bold")
    ax.set_xlabel("Van Capacity (W in kg)")
    ax.set_ylabel("Execution Time (ms)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    # 4. Dijkstra vs |V|
    ax = axs[1, 0]
    ax.plot(dijk_data["v_sizes"], dijk_data["dijkstra_times_ms"], "o-", color="#F79009", linewidth=2, label="Dijkstra (Custom MinHeap)")
    ax.set_title("4. Dijkstra Shortest Paths: Runtime vs Graph Size", fontsize=11, weight="bold")
    ax.set_xlabel("Road Graph Vertices |V|")
    ax.set_ylabel("Execution Time (ms)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    # 5. TSP Runtimes (Log Scale)
    ax = axs[1, 1]
    ax.semilogy(tsp_data["stop_counts"], tsp_data["exact_times_ms"], "o--", color="#D92D20", label="Exact Brute-Force O(K!)", linewidth=2)
    ax.semilogy(tsp_data["stop_counts"], tsp_data["opt_times_ms"], "^-", color="#1570EF", label="Nearest-Neighbour + 2-Opt", linewidth=2)
    ax.semilogy(tsp_data["stop_counts"], tsp_data["nn_times_ms"], "s-", color="#099250", label="Nearest-Neighbour O(K²)", linewidth=2)
    ax.set_title("5. TSP Runtime Comparison (Log Scale)", fontsize=11, weight="bold")
    ax.set_xlabel("Number of Delivery Stops (K)")
    ax.set_ylabel("Execution Time (ms) - Log10")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    # 6. TSP Approximation Quality
    ax = axs[1, 2]
    ax.plot(tsp_data["stop_counts"], tsp_data["nn_ratios"], "s--", color="#F79009", label="NN Ratio (Length / OPT)", linewidth=2)
    ax.plot(tsp_data["stop_counts"], tsp_data["opt_ratios"], "o-", color="#12B76A", label="2-Opt Ratio (Length / OPT)", linewidth=2)
    ax.axhline(1.0, color="#1D2939", linestyle=":", linewidth=1.5, label="Optimal Tour Baseline (1.00)")
    ax.set_title("6. TSP Approximation Ratio vs Global Optimum", fontsize=11, weight="bold")
    ax.set_xlabel("Number of Delivery Stops (K)")
    ax.set_ylabel("Approximation Ratio (Tour Cost / OPT)")
    ax.set_ylim(0.95, 1.45)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right")

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(filepath)
    plt.close()
    print(f"[+] Multi-panel benchmark visualization saved to: {filepath}")


def main() -> None:
    print("=================================================================")
    print(" MINI-COURIER PLANNER - COMPREHENSIVE BENCHMARK RUNNER")
    print("=================================================================")

    # Run individual benchmarks
    sort_res = benchmark_sorting()
    knap_res = benchmark_knapsack()
    dijk_res = benchmark_dijkstra()
    tsp_res = benchmark_tsp()

    # Run dataset benchmarks
    pipe_res = benchmark_datasets_pipeline()

    # Generate charts and CSV
    chart_path = "results/runtime_charts.png"
    csv_path = "results/benchmark_results.csv"

    plot_benchmark_charts(sort_res, knap_res, dijk_res, tsp_res, chart_path)
    export_results_to_csv(pipe_res, csv_path)

    print("\n[+] Benchmark suite finished successfully!")


if __name__ == "__main__":
    main()

