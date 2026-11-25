"""
Mini-Courier Planner - Synthetic Dataset Generator
Design & Analysis of Algorithms Capstone

Generates reproducible, seeded benchmark datasets matching academic specifications:
1. Small:  10 nodes, 12 parcels, van capacity = 20 kg
2. Medium: 50 nodes, 200 parcels, van capacity = 60 kg
3. Large:  300 nodes, 2000 parcels, van capacity = 150 kg

Graph Connectivity Guarantee:
- Nodes are assigned random 2D spatial coordinates (x, y).
- Node 0 is designated as the Central Logistics Depot.
- A randomized Euclidean Spanning Tree is constructed first, guaranteeing 100% connectivity.
- Additional k-nearest neighbor edges are added to emulate real-world road networks.
"""

import json
import math
import random
from typing import Dict, List, Tuple, Any
from courier.models import Parcel
from courier.graph import RoadGraph


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculates Euclidean distance between two 2D points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def generate_connected_graph(
    num_nodes: int,
    seed: int = 42,
    grid_size: float = 100.0,
    extra_neighbor_k: int = 3,
) -> RoadGraph:
    """
    Constructs a guaranteed-connected undirected road graph with 2D coordinates.

    Steps:
    1. Place node 0 at center (grid_size/2, grid_size/2).
    2. Randomly scatter nodes 1..V-1 across the bounding box.
    3. Generate a Minimum Spanning Tree (MST-style) ensuring single-component connectivity.
    4. Connect each node to its nearest spatial neighbors to model road density.
    """
    rng = random.Random(seed)
    graph = RoadGraph(num_nodes)

    # 1. Place coordinates
    depot_x = grid_size / 2.0
    depot_y = grid_size / 2.0
    graph.add_node(0, depot_x, depot_y)

    for i in range(1, num_nodes):
        x = round(rng.uniform(5.0, grid_size - 5.0), 2)
        y = round(rng.uniform(5.0, grid_size - 5.0), 2)
        graph.add_node(i, x, y)

    # 2. Spanning Tree to guarantee 100% graph connectivity
    connected_nodes = [0]
    unconnected_nodes = list(range(1, num_nodes))
    rng.shuffle(unconnected_nodes)

    existing_edges = set()

    for v in unconnected_nodes:
        # Connect v to the spatially closest node in connected_nodes
        v_coord = graph.coordinates[v]
        closest_u = min(
            connected_nodes,
            key=lambda u: euclidean_distance(v_coord, graph.coordinates[u]),
        )
        dist = max(1.0, round(euclidean_distance(v_coord, graph.coordinates[closest_u]), 1))
        
        graph.add_edge(closest_u, v, dist)
        existing_edges.add(tuple(sorted((closest_u, v))))
        connected_nodes.append(v)

    # 3. Add extra edges to k-nearest neighbors to form realistic road meshes
    for u in range(num_nodes):
        u_coord = graph.coordinates[u]
        # Sort all other nodes by distance
        neighbors = sorted(
            [v for v in range(num_nodes) if v != u],
            key=lambda v: euclidean_distance(u_coord, graph.coordinates[v]),
        )
        for v in neighbors[:extra_neighbor_k]:
            edge_key = tuple(sorted((u, v)))
            if edge_key not in existing_edges:
                dist = max(1.0, round(euclidean_distance(u_coord, graph.coordinates[v]), 1))
                graph.add_edge(u, v, dist)
                existing_edges.add(edge_key)

    return graph


def generate_parcels(
    num_parcels: int,
    num_nodes: int,
    seed: int = 42,
    max_weight: int = 15,
) -> List[Parcel]:
    """
    Generates a deterministic, seeded list of customer parcels.

    Attributes:
    - pid: Formatted as P001, P002, etc.
    - dest: Node ID uniformly distributed in [1, num_nodes - 1] (never depot 0).
    - weight: Integer kilograms in [1, max_weight].
    - priority: Integer urgency in [1, 5].
    - deadline: Integer hours in [2, 48].
    """
    rng = random.Random(seed)
    parcels: List[Parcel] = []

    for i in range(1, num_parcels + 1):
        pid = f"P{i:04d}"
        dest = rng.randint(1, num_nodes - 1)
        weight = rng.randint(1, max_weight)
        priority = rng.randint(1, 5)
        deadline = rng.randint(2, 48)

        parcels.append(
            Parcel(
                pid=pid,
                dest=dest,
                weight=weight,
                priority=priority,
                deadline=deadline,
            )
        )

    return parcels


def build_dataset_dict(
    name: str,
    num_nodes: int,
    num_parcels: int,
    capacity: int,
    seed: int = 42,
    grid_size: float = 100.0,
    max_parcel_weight: int = 15,
) -> Dict[str, Any]:
    """Assembles a full dataset configuration dictionary ready for JSON serialization."""
    graph = generate_connected_graph(num_nodes, seed=seed, grid_size=grid_size)
    parcels = generate_parcels(num_parcels, num_nodes, seed=seed, max_weight=max_parcel_weight)

    return {
        "dataset_name": name,
        "description": f"Seeded benchmark dataset: {num_nodes} nodes, {num_parcels} parcels, {capacity}kg capacity",
        "capacity": capacity,
        "graph": graph.to_dict(),
        "parcels": [p.to_dict() for p in parcels],
    }


def save_dataset(data: Dict[str, Any], filepath: str) -> None:
    """Saves a dataset dictionary to a formatted JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_dataset(filepath: str) -> Tuple[RoadGraph, List[Parcel], int, str]:
    """
    Loads and reconstructs RoadGraph, Parcel list, and van capacity from a JSON file.

    Returns:
        Tuple (graph, parcels, capacity, dataset_name)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    graph = RoadGraph.from_dict(data["graph"])
    parcels = [Parcel.from_dict(p) for p in data["parcels"]]
    capacity = int(data["capacity"])
    name = data.get("dataset_name", "custom")

    return graph, parcels, capacity, name

