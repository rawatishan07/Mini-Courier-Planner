"""
Mini-Courier Planner - Main CLI Driver
Design & Analysis of Algorithms Capstone

University: K.R. Mangalam University
Course: Design & Analysis of Algorithms (ETCCDA302)

CLI Options:
  --data PATH         Path to dataset JSON file (default: data/small.json)
  --sort-algo ALGO    Sorting algorithm: merge | quick | bubble (default: merge)
  --show-table        Force printing of full 0/1 Knapsack DP table
  --no-two-opt        Disable 2-opt TSP local search improvement
  --exact-tsp         Run brute-force exact TSP solver for comparison (stops <= 10)
  --plot              Render and save delivery route map PNG (results/)
  --plot-output PATH  Custom output path for the route map PNG
"""

import argparse
import os
import sys
import tempfile

# Configure Matplotlib writable cache before importing pyplot
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib_courier")

from courier.data_gen import load_dataset
from courier.planner import run_pipeline
from courier.knapsack import format_dp_table


def render_route_plot(graph, plan, output_path: str) -> None:
    """
    Renders an academic visual plot of the road graph, depot, stops, and delivery tour.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # Headless backend for terminal/server execution
        import matplotlib.pyplot as plt
    except ImportError:
        print("[!] Matplotlib not installed. Skipping plot generation.")
        return

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

    # 1. Draw all road graph edges
    coords = graph.coordinates
    edges = graph.get_all_edges()
    for u, v, w in edges:
        if u in coords and v in coords:
            xu, yu = coords[u]
            xv, yv = coords[v]
            ax.plot([xu, xv], [yu, yv], color="#D0D5DD", linewidth=1.0, zorder=1)

    # 2. Draw all intermediate road junctions
    for node, (x, y) in coords.items():
        if node != 0 and node not in plan.stops:
            ax.scatter(x, y, color="#98A2B3", s=25, zorder=2)

    # 3. Highlight full expanded road path
    road_path = plan.road_path
    if road_path and len(road_path) > 1:
        rx = [coords[n][0] for n in road_path if n in coords]
        ry = [coords[n][1] for n in road_path if n in coords]
        ax.plot(rx, ry, color="#1570EF", linewidth=2.5, alpha=0.85, label="Actual Road Path", zorder=3)

    # 4. Highlight delivery stops
    stop_nodes = [s for s in plan.stops if s != 0]
    if stop_nodes:
        sx = [coords[s][0] for s in stop_nodes]
        sy = [coords[s][1] for s in stop_nodes]
        ax.scatter(sx, sy, color="#F04438", s=110, edgecolor="black", linewidth=1.5,
                   label=f"Delivery Stops ({len(stop_nodes)})", zorder=4)
        for s in stop_nodes:
            ax.annotate(f"Stop {s}", (coords[s][0] + 1.0, coords[s][1] + 1.0),
                        fontsize=8, weight="bold", color="#7A271A")

    # 5. Highlight central depot (Node 0)
    if 0 in coords:
        dx, dy = coords[0]
        ax.scatter(dx, dy, color="#12B76A", s=220, marker="*", edgecolor="black",
                   linewidth=1.5, label="Depot (Node 0)", zorder=5)
        ax.annotate("DEPOT (0)", (dx + 1.2, dy - 2.0),
                    fontsize=9, weight="bold", color="#054F31")

    # Titles and styling
    tour_str = " -> ".join(str(s) for s in plan.tsp_tour)
    ax.set_title(
        f"Mini-Courier Route Map: {plan.dataset_name}\n"
        f"Capacity: {plan.van_capacity}kg | Parcels: {len(plan.chosen_parcels)} | Distance: {plan.total_distance:.1f} km",
        fontsize=11, weight="bold", pad=12
    )
    ax.set_xlabel("X Coordinate (km)")
    ax.set_ylabel("Y Coordinate (km)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", framealpha=0.9)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"\n[+] Route visualization saved to: {output_path}")


def print_banner(text: str) -> None:
    line = "=" * 78
    print(f"\n{line}\n {text.upper()}\n{line}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mini-Courier Planner - University DAA Capstone Project",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--data", type=str, default="data/small.json", help="Path to JSON dataset")
    parser.add_argument("--sort-algo", type=str, choices=["merge", "quick", "bubble"], default="merge",
                        help="Sorting algorithm: merge (stable primary), quick, or bubble")
    parser.add_argument("--show-table", action="store_true", help="Force display of complete DP table")
    parser.add_argument("--no-two-opt", action="store_true", help="Disable 2-opt TSP improvement")
    parser.add_argument("--exact-tsp", action="store_true", help="Run brute-force exact TSP (stops <= 10)")
    parser.add_argument("--plot", action="store_true", help="Generate and save route map PNG")
    parser.add_argument("--plot-output", type=str, default="results/route_map.png", help="Path for route map image")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"[!] Dataset file '{args.data}' not found. Generating default datasets first...")
        from make_datasets import generate_all_datasets
        generate_all_datasets()

    graph, parcels, capacity, dataset_name = load_dataset(args.data)
    use_2opt = not args.no_two_opt

    print("*" * 78)
    print("       MINI-COURIER PLANNER: ALGORITHMIC OPTIMIZATION SYSTEM")
    print("      Design & Analysis of Algorithms Capstone - ETCCDA302")
    print("*" * 78)

    # -------------------------------------------------------------------------
    # PHASE 1: Courier Problem Design and Planning
    # -------------------------------------------------------------------------
    print_banner("PHASE 1: Courier Problem Design & Planning")
    print(f"Dataset:            {dataset_name}")
    print(f"Road Network:       {graph.num_nodes} Junctions, {len(graph.get_all_edges())} Road Segments")
    print(f"Central Depot:      Junction 0 (Coordinates: {graph.coordinates.get(0, ('N/A', 'N/A'))})")
    print(f"Total Parcels:      {len(parcels)} pending delivery")
    print(f"Courier Van Limit:  {capacity} kg payload capacity")
    print(f"Selected Sorter:    {args.sort_algo.upper()} SORT (Criteria: deadline ASC, priority DESC)")
    print(f"TSP Optimizer:      Nearest-Neighbour Heuristic {'+ 2-Opt Local Search' if use_2opt else ''}")

    # -------------------------------------------------------------------------
    # EXECUTE PIPELINE
    # -------------------------------------------------------------------------
    plan, dp_table, exact_res = run_pipeline(
        graph=graph,
        parcels=parcels,
        capacity=capacity,
        sort_algo=args.sort_algo,
        use_2opt=use_2opt,
        run_exact_tsp=args.exact_tsp,
        dataset_name=dataset_name,
    )

    # -------------------------------------------------------------------------
    # PHASE 2: Package Prioritization and Box Filling
    # -------------------------------------------------------------------------
    print_banner("PHASE 2: Package Prioritization & Knapsack Packing")
    
    print(f"[*] Parcels sorted using {args.sort_algo.upper()} SORT (Top 10 shown):")
    hdr_p = f"{'Rank':<5} | {'PID':<6} | {'Dest':<5} | {'Weight':<7} | {'Priority':<9} | {'Deadline':<9} | {'DP Value':<8}"
    print("-" * len(hdr_p))
    print(hdr_p)
    print("-" * len(hdr_p))
    for idx, p in enumerate(plan.sorted_parcels[:10], start=1):
        print(f"{idx:<5} | {p.pid:<6} | {p.dest:<5} | {p.weight:>4} kg | {p.priority:>8}/5 | {p.deadline:>6} hrs | {p.value:>7} pts")
    if len(plan.sorted_parcels) > 10:
        print(f"... and {len(plan.sorted_parcels) - 10} more parcels.")

    # DP Table Display
    should_show_table = args.show_table or (len(parcels) <= 15 and capacity <= 25)
    if should_show_table:
        print("\n[*] 0/1 Knapsack Dynamic Programming Matrix:")
        print(format_dp_table(plan.sorted_parcels, capacity, dp_table, highlight_backtrack=True))
    else:
        print(f"\n[*] DP Table dimensions: ({len(parcels)+1} rows x {capacity+1} columns = {(len(parcels)+1)*(capacity+1)} states computed).")
        print("    [Pass --show-table to display the full ASCII matrix on larger inputs]")

    print("\n[+] OPTIMAL KNAPSACK PACKING SELECTION (via Backtracking):")
    print(f"    Parcels Loaded:       {len(plan.chosen_parcels)} / {len(parcels)} available")
    print(f"    Payload Utilized:     {plan.total_weight} kg / {capacity} kg ({plan.capacity_utilization}%)")
    print(f"    Total Value Achieved: {plan.total_value} points")
    print("    Selected Manifest:")
    for p in plan.chosen_parcels:
        print(f"      - {p.pid}: Dest Node {p.dest:2d} | Weight: {p.weight:2d}kg | Priority: {p.priority}/5 | Deadline: {p.deadline:2d}h | Value: {p.value}")

    # -------------------------------------------------------------------------
    # PHASE 3: Route Maker and Graph Processing
    # -------------------------------------------------------------------------
    print_banner("PHASE 3: Route Maker & Graph Processing")
    print(f"Distinct Delivery Stops: {plan.stops} (Total {len(plan.stops)} nodes including Depot 0)")
    
    # Distance Matrix Preview
    print("\n[*] Dijkstra All-Pairs Distance Matrix (km) between Stops:")
    col_w = 7
    dmat_hdr = f"{'From/To':<8} | " + " | ".join(f"{s:>{col_w}}" for s in plan.stops)
    print("-" * len(dmat_hdr))
    print(dmat_hdr)
    print("-" * len(dmat_hdr))
    for u in plan.stops:
        row_str = " | ".join(f"{plan.distance_matrix[(u, v)]:>{col_w}.1f}" for v in plan.stops)
        print(f"Node {u:<3} | {row_str}")
    print("-" * len(dmat_hdr))

    # TSP Tour
    print(f"\n[+] High-Level TSP Stop Tour ({'Nearest-Neighbour + 2-Opt' if use_2opt else 'Nearest-Neighbour'}):")
    print("    " + " -> ".join(str(s) for s in plan.tsp_tour))
    print(f"    Total Road Route Length: {plan.total_distance:.2f} km")

    if exact_res is not None:
        exact_tour, exact_dist = exact_res
        ratio = plan.total_distance / exact_dist if exact_dist > 0 else 1.0
        print(f"\n[*] Brute-Force Exact TSP Verification (Permutation Search):")
        print(f"    Optimal Tour:     {' -> '.join(str(s) for s in exact_tour)}")
        print(f"    Optimal Distance: {exact_dist:.2f} km")
        print(f"    Approximation Ratio (Heuristic / OPT): {ratio:.4f} (1.000 = Provably Optimal)")

    # Expanded Road Junctions
    print("\n[+] Detailed Physical Road Path (Expanded via Dijkstra Predecessor Pointers):")
    path_chunks = [str(n) for n in plan.road_path]
    # Wrap path into readable lines
    chunk_size = 15
    for i in range(0, len(path_chunks), chunk_size):
        prefix = "    Route: " if i == 0 else "           "
        print(prefix + " -> ".join(path_chunks[i:i + chunk_size]))
    print(f"    Total Road Junction Hops: {len(plan.road_path) - 1} edges traversed")

    # -------------------------------------------------------------------------
    # PHASE 4: Performance Testing and Optimization
    # -------------------------------------------------------------------------
    print_banner("PHASE 4: Algorithmic Runtime Profiling")
    print(f"{'Pipeline Stage':<30} | {'Algorithm Used':<28} | {'Execution Time':<12}")
    print("-" * 78)
    p_times = plan.execution_times
    print(f"{'1. Parcel Prioritization':<30} | {args.sort_algo.capitalize() + ' Sort':<28} | {p_times.get('sort_time', 0)*1000:>9.3f} ms")
    print(f"{'2. Knapsack Packing':<30} | {'0/1 Dynamic Programming':<28} | {p_times.get('knapsack_time', 0)*1000:>9.3f} ms")
    print(f"{'3. Shortest Paths':<30} | {'Dijkstra (Custom MinHeap)':<28} | {p_times.get('dijkstra_time', 0)*1000:>9.3f} ms")
    print(f"{'4. Tour Optimization':<30} | {'Nearest-Neighbour + 2-Opt':<28} | {p_times.get('tsp_time', 0)*1000:>9.3f} ms")
    if "exact_tsp_time" in p_times:
        print(f"{'   [Exact TSP Baseline]':<30} | {'Permutation Search O(K!)':<28} | {p_times.get('exact_tsp_time', 0)*1000:>9.3f} ms")
    print(f"{'5. Road Path Reconstruction':<30} | {'Predecessor Backtracking':<28} | {p_times.get('expansion_time', 0)*1000:>9.3f} ms")
    print("-" * 78)
    print(f"{'TOTAL PIPELINE LATENCY':<30} | {'End-to-End':<28} | {p_times.get('total_time', 0)*1000:>9.3f} ms")
    print("=" * 78)

    # -------------------------------------------------------------------------
    # PHASE 5: Visual Map Demonstration
    # -------------------------------------------------------------------------
    if args.plot:
        render_route_plot(graph, plan, args.plot_output)
    else:
        print("\n[Tip] Pass --plot to render the visual delivery route map into results/.")


if __name__ == "__main__":
    main()

