# Mini-Courier Planner: Algorithmic Logistics Optimization

### Student Information

- **Name:** Ishan Rawat
- **Course:** B.Tech CSE Core
- **Section:** A
- **Roll Number:** 2501010153

---

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**Institution:** K.R. Mangalam University, Gurugram, Haryana  
**Assessment:** Capstone Project (100 Marks scaled down to 10 Marks)  
**Faculty Evaluator:** Dr. Shweta Agarwal  
**Implementation:** Pure Python (Zero external library shortcuts for core algorithms)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: Passing](https://img.shields.io/badge/tests-15%2F15%20passed-brightgreen.svg)]()

---

## 1. Project Overview

A courier delivery van starts at a central depot (Node 0) with more customer parcels than its payload capacity can carry. Given a waiting backlog of customer parcels with varying weights, urgency priorities, and deadlines, along with an undirected road network graph, the **Mini-Courier Planner** generates:

1. **A prioritized parcel manifest** sorted stably by urgency and service level.
2. **An optimal parcel packing selection** for one delivery trip maximizing value within payload constraints.
3. **Shortest road distances and predecessor trees** between all relevant stops.
4. **An optimized, seamless delivery route** starting from the depot, visiting all delivery destinations, and returning to the depot, expanded into real road junctions.

### Zero Library Shortcuts

All core algorithms are implemented **entirely by hand from first principles**:

- **Sorting:** Stable Merge Sort, plus 3-way Dutch National Flag Quick Sort and Bubble Sort baselines.
- **Payload Selection:** 0/1 Knapsack Dynamic Programming with complete $(n+1) \times (W+1)$ matrix allocation and backtracking.
- **Shortest Paths:** Dijkstra's Algorithm with a hand-crafted Binary Min-Heap Priority Queue (no `heapq`).
- **Tour Scheduling:** Metric TSP Nearest-Neighbour ($O(K^2)$) approximation, 2-Opt local search refinement, and exact brute-force permutation solver ($O(K!)$) for quality assessment.

---

## 2. Algorithmic Complexity Table

| Component    | Hand-Crafted Algorithm          |      Time (Best)      |       Time (Average)       |        Time (Worst)        |   Auxiliary Space   | Theoretical Guarantee                              |
| :----------- | :------------------------------ | :-------------------: | :------------------------: | :------------------------: | :-----------------: | :------------------------------------------------- |
| **Phase 2A** | **Merge Sort** _(Primary)_      |  $\Omega(n \log n)$   |     $\Theta(n \log n)$     |       $O(n \log n)$        |       $O(n)$        | **Stable**, Optimal                                |
| **Phase 2A** | Quick Sort (3-way) _(Baseline)_ |      $\Omega(n)$      |     $\Theta(n \log n)$     |          $O(n^2)$          |     $O(\log n)$     | Randomized, Unstable                               |
| **Phase 2A** | Bubble Sort _(Baseline)_        |      $\Omega(n)$      |       $\Theta(n^2)$        |          $O(n^2)$          |       $O(1)$        | Quadratic Baseline                                 |
| **Phase 2B** | **0/1 Knapsack DP**             |  $\Theta(n \cdot W)$  |    $\Theta(n \cdot W)$     |    $\Theta(n \cdot W)$     | $\Theta(n \cdot W)$ | **Globally Optimal**                               |
| **Phase 2B** | Knapsack Brute Force _(Test)_   | $\Theta(2^n \cdot n)$ |   $\Theta(2^n \cdot n)$    |   $\Theta(2^n \cdot n)$    |       $O(n)$        | Exponential Verifier                               |
| **Phase 3A** | **Binary MinHeap**              |      $O(1)$ peek      |        $O(\log V)$         |        $O(\log V)$         |       $O(V)$        | Strict Min-Heap Invariant                          |
| **Phase 3A** | **Dijkstra's Algorithm**        |   $O((V+E)\log V)$    |      $O((V+E)\log V)$      |      $O((V+E)\log V)$      |       $O(V)$        | **Shortest Paths**                                 |
| **Phase 3A** | Bellman-Ford _(Test Verifier)_  |    $O(V \cdot E)$     |       $O(V \cdot E)$       |       $O(V \cdot E)$       |       $O(V)$        | Independent Verifier                               |
| **Phase 3B** | **Nearest-Neighbour TSP**       |     $\Theta(K^2)$     |       $\Theta(K^2)$        |       $\Theta(K^2)$        |       $O(K)$        | Metric Bound $\le \frac{1}{2}\lceil\log_2 K\rceil$ |
| **Phase 3C** | **2-Opt Local Search**          |       $O(K^2)$        | $O(\text{iter} \cdot K^2)$ | $O(\text{iter} \cdot K^2)$ |       $O(K)$        | Monotonic Improvement                              |
| **Phase 3C** | Exact TSP Brute Force _(Test)_  |     $\Theta(K!)$      |        $\Theta(K!)$        |        $\Theta(K!)$        |       $O(K)$        | Global Metric Optimum                              |
| **Phase 3D** | **Road Path Expansion**         |        $O(H)$         |           $O(H)$           |           $O(H)$           |       $O(H)$        | Unbroken Road Sequence                             |

_(Where $n$ = parcels, $W$ = van payload capacity in kg, $V$ = road network nodes, $E$ = road segments, $K$ = delivery stops, $H$ = road junction hops)._

---

## 3. Project Directory Structure

```
Mini-courier planner daa/
│
├── courier/                        # Core Algorithmic Engine (No Library Shortcuts)
│   ├── __init__.py                 # Public module exports
│   ├── models.py                   # Parcel, Edge, and DeliveryPlan dataclasses
│   ├── sorting.py                  # Hand-crafted Merge Sort, Quick Sort (3-way), Bubble Sort
│   ├── knapsack.py                 # 0/1 Knapsack DP, Backtracking, Table Formatter, Brute Force
│   ├── graph.py                    # RoadGraph, Hand-Crafted MinHeap, Dijkstra, Path Reconstruction
│   ├── tsp.py                      # Nearest-Neighbour TSP, 2-Opt Optimizer, Exact Brute Force, Expansion
│   ├── planner.py                  # End-to-end multi-phase logistics pipeline orchestrator
│   └── data_gen.py                 # Connected road network & parcel generator (MST + KNN)
│
├── data/                           # Standard Seeded Benchmark Datasets
│   ├── small.json                  # 10 nodes, 12 parcels, 20 kg capacity
│   ├── medium.json                 # 50 nodes, 200 parcels, 60 kg capacity
│   └── large.json                  # 300 nodes, 2000 parcels, 150 kg capacity
│
├── results/                        # Generated Artifacts, Charts & Metrics
│   ├── runtime_charts.png          # 6-panel academic benchmark visualization
│   ├── benchmark_results.csv       # Tabular empirical performance logs
│   ├── route_map_small.png         # Visual road map of small delivery circuit
│   ├── route_map_medium.png        # Visual road map of medium delivery circuit
│   └── route_map_large.png         # Visual road map of large delivery circuit
│
├── docs/                           # University Capstone Documentation
│   ├── DESIGN.md                   # Formal architectural specifications & recurrence relations
│   └── VIVA_NOTES.md               # 25+ viva questions, derivations & worked DP numerical trace
│
├── main.py                         # Interactive CLI driver with phase-by-phase reporting
├── make_datasets.py                # Dataset builder for reproducible benchmarks
├── benchmark.py                    # Profiling suite generating runtime_charts.png and CSV
├── test_courier.py                 # 15-test suite validating algorithms against independent methods
└── README.md                       # This file
```

---

## 4. Quickstart & Execution Guide

### Prerequisites

- Python 3.8 or higher.
- `matplotlib` (used only for saving visual charts and route maps in `results/`).
  ```bash
  pip install matplotlib
  ```

### Step 1: Generate Benchmark Datasets

Create the three seeded benchmark datasets in `data/`:

```bash
python make_datasets.py
```

### Step 2: Run the Full System on Sample Datasets

Run `main.py` to see phase-by-phase evidence, ASCII DP table, distance matrix, and route sequence:

```bash
# Small Dataset (Shows ASCII DP table, verification, and saves route map)
python main.py --data data/small.json --exact-tsp --plot --plot-output results/route_map_small.png

# Medium Dataset (50 nodes, 200 parcels, 60 kg)
python main.py --data data/medium.json --plot --plot-output results/route_map_medium.png

# Large Dataset (300 nodes, 2000 parcels, 150 kg)
python main.py --data data/large.json --plot --plot-output results/route_map_large.png
```

### Step 3: Run the Test Suite

Execute the 15 independent unit and integration tests:

```bash
python test_courier.py
```

_(All 15 tests execute and pass in $< 0.05$ seconds)._

### Step 4: Run Empirical Benchmarks

Generate runtime charts and CSV metrics across all input sizes:

```bash
python benchmark.py
```

---

## 5. CLI Command-Line Reference

`main.py` provides complete control over execution parameters:

```bash
usage: main.py [-h] [--data PATH] [--sort-algo {merge,quick,bubble}]
               [--show-table] [--no-two-opt] [--exact-tsp] [--plot]
               [--plot-output PATH]

Mini-Courier Planner - University DAA Capstone Project

options:
  -h, --help            Show this help message and exit
  --data PATH           Path to JSON dataset (default: data/small.json)
  --sort-algo ALGO      Sorting algorithm: merge | quick | bubble (default: merge)
  --show-table          Force display of complete DP table
  --no-two-opt          Disable 2-opt TSP local search improvement
  --exact-tsp           Run brute-force exact TSP solver for comparison (stops <= 10)
  --plot                Render and save delivery route map PNG to results/
  --plot-output PATH    Custom output path for the route map PNG
```

---

## 6. Demonstration & Phase Output Evidence

When `main.py` executes, it outputs clear evidence across all 5 evaluation phases:

### Phase 1: Courier Problem Design & Planning

- Summarizes road graph topology (junctions, edges, depot coordinates at Node 0).
- Reports parcel backlog and courier van payload capacity.

### Phase 2: Package Prioritization & Knapsack Packing

- **Sorted Manifest:** Parcels ordered by deadline ascending, priority descending.
- **0/1 Knapsack DP Table:** Beautifully formatted ASCII table with asterisks `*` tracking the optimal backtracking path from $(n, W)$ to $(0, 0)$:

```
Item (w, v)        | w=  0 | w=  1 | w=  2 | w=  3 | ... | w= 20
------------------------------------------------------------------
0: [Initial]       |    0* |    0  |    0  |    0  | ... |    0
1: P0001 (6k,59v)  |    0* |    0  |    0  |    0  | ... |   59
2: P0004 (2k,40v)  |    0  |    0  |   40* |   40  | ... |   99
3: P0007 (7k,49v)  |    0  |    0  |   40* |   40  | ... |  148
4: P0012 (1k,49v)  |    0  |   49  |   49  |   89* | ... |  197
...
```

- **Selected Manifest:** 100% capacity utilization with maximum priority score achieved.

### Phase 3: Route Maker & Graph Processing

- **Dijkstra Distance Matrix:** All-pairs shortest path table across $\{0\} \cup \text{stops}$.
- **TSP Circuit:** High-level stop sequence (Depot $\to \dots \to$ Depot).
- **Exact Verification:** Brute-force optimal distance comparison confirming an approximation ratio of **1.0000 (Provably Optimal)**.
- **Physical Road Path:** Expanded unbroken chain of street intersections tracing Dijkstra `prev` pointers:

```
Route: 0 -> 3 -> 6 -> 8 -> 5 -> 9 -> 4 -> 7 -> 9 -> 0
Total Road Junction Hops: 9 edges traversed
```

### Phase 4: Algorithmic Runtime Profiling

High-resolution microsecond latency breakdown per stage:

```
Pipeline Stage                 | Algorithm Used               | Execution Time
------------------------------------------------------------------------------
1. Parcel Prioritization       | Merge Sort                   |     0.048 ms
2. Knapsack Packing            | 0/1 Dynamic Programming      |     0.058 ms
3. Shortest Paths              | Dijkstra (Custom MinHeap)    |     0.216 ms
4. Tour Optimization           | Nearest-Neighbour + 2-Opt    |     0.058 ms
   [Exact TSP Baseline]        | Permutation Search O(K!)     |     1.610 ms
5. Road Path Reconstruction    | Predecessor Backtracking     |     0.014 ms
------------------------------------------------------------------------------
TOTAL PIPELINE LATENCY         | End-to-End                   |     2.009 ms
```

### Phase 5: Visual Route Map

Pass `--plot` to generate publication-quality visual plots highlighting depot, delivery stops, road network edges, and the exact delivery circuit in `results/route_map_small.png`.

---

## 7. Empirical Benchmark Results

### Benchmark Summary on Seeded Datasets

Data extracted from `results/benchmark_results.csv`:

| Dataset    | Road Nodes | Road Edges | Parcels Available | Van Capacity | Parcels Loaded | Payload Utilized | Delivery Stops | Route Length | Road Hops | Pipeline Latency |
| :--------- | :--------: | :--------: | :---------------: | :----------: | :------------: | :--------------: | :------------: | :----------: | :-------: | :--------------: |
| **Small**  |     10     |     21     |        12         |    20 kg     |       7        |      100.0%      |       7        |   201.0 km   |  9 hops   |   **2.55 ms**    |
| **Medium** |     50     |    107     |        200        |    60 kg     |       32       |      100.0%      |       23       |  1018.0 km   |  33 hops  |   **26.46 ms**   |
| **Large**  |    300     |    633     |       2000        |    150 kg    |      121       |      100.0%      |      101       |  5346.2 km   | 190 hops  |  **382.24 ms**   |

### Algorithmic Scaling Observations

The 6-panel chart in `results/runtime_charts.png` demonstrates:

1. **Sorting:** Bubble Sort explodes quadratically ($2073\text{ ms}$ at $N=2000$), whereas Merge Sort ($44\text{ ms}$) and Quick Sort ($16\text{ ms}$) scale cleanly as $O(N \log N)$.
2. **0/1 Knapsack DP:** Confirms pseudo-polynomial behavior $\Theta(n \cdot W)$, scaling linearly with $n$ when $W$ is fixed, and linearly with $W$ when $n$ is fixed.
3. **Dijkstra:** Scaled efficiently from $0.11\text{ ms}$ ($|V|=20$) to $4.01\text{ ms}$ ($|V|=500$) using our hand-crafted MinHeap.
4. **TSP Runtime:** Exact Brute Force exploded factorially ($2190\text{ ms}$ at $K=10$), while Nearest-Neighbour + 2-Opt finished in just $0.11\text{ ms}$.
5. **Approximation Quality:** Across $K = 4$ to $10$ stops, 2-Opt achieved an approximation ratio of **$1.000$ to $1.024$**, finding the globally optimal tour in almost every case.

---

## 8. Optimization Ideas & Practical Limitations

### Practical Limitations

1. **Integer Weights in 0/1 Knapsack:** Tabular DP requires discrete integer weights. Continuous fractional weights (e.g., $3.45\text{ kg}$) require discretization scaling or Branch-and-Bound algorithms.
2. **Single Van Assumption:** Currently plans routes for a single delivery vehicle.
3. **Static Traffic Conditions:** Edge weights are assumed static during the delivery run.

### Optimization Ideas for Industrial Extension

1. **Multi-Vehicle Routing Problem (VRP):** Cluster parcels into vehicle zones using K-Means or capacitated clustering, then solve TSP for each van independently.
2. **Time Windows (VRPTW):** Incorporate customer availability intervals $[e_i, l_i]$ as penalty constraints in the TSP objective.
3. **A\* Search / Contraction Hierarchies:** Replace Dijkstra with landmark-based A\* heuristics or Contraction Hierarchies for continental-scale road networks with millions of nodes.
4. **Dynamic Re-Routing:** If a customer cancels after dispatch, the pre-computed Dijkstra distance matrix allows instantaneous TSP re-optimization without re-running graph searches.

---

## 9. Academic Integrity & Verification

This project was authored from scratch for K.R. Mangalam University's ETCCDA302 Capstone. All sorting algorithms, binary min-heaps, dynamic programming solvers, and graph search routines are original pure Python implementations with zero black-box dependencies.
