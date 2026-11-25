"""
Make Datasets - Seeded Benchmark Dataset Generator
Design & Analysis of Algorithms Capstone

Generates three reproducible JSON benchmark datasets in the data/ directory:
1. small.json:  10 nodes, 12 parcels, capacity 20 kg  (seed=101)
2. medium.json: 50 nodes, 200 parcels, capacity 60 kg (seed=202)
3. large.json:  300 nodes, 2000 parcels, capacity 150 kg (seed=303)

Usage:
    python make_datasets.py
"""

import os
from courier.data_gen import build_dataset_dict, save_dataset


def generate_all_datasets(output_dir: str = "data") -> None:
    os.makedirs(output_dir, exist_ok=True)

    configs = [
        {
            "filename": "small.json",
            "name": "Small (10 Nodes, 12 Parcels, 20kg Capacity)",
            "nodes": 10,
            "parcels": 12,
            "capacity": 20,
            "seed": 101,
            "grid_size": 100.0,
            "max_parcel_weight": 8,
        },
        {
            "filename": "medium.json",
            "name": "Medium (50 Nodes, 200 Parcels, 60kg Capacity)",
            "nodes": 50,
            "parcels": 200,
            "capacity": 60,
            "seed": 202,
            "grid_size": 200.0,
            "max_parcel_weight": 12,
        },
        {
            "filename": "large.json",
            "name": "Large (300 Nodes, 2000 Parcels, 150kg Capacity)",
            "nodes": 300,
            "parcels": 2000,
            "capacity": 150,
            "seed": 303,
            "grid_size": 500.0,
            "max_parcel_weight": 15,
        },
    ]

    print("=================================================================")
    print(" MINI-COURIER PLANNER - GENERATING BENCHMARK DATASETS")
    print("=================================================================")

    for cfg in configs:
        filepath = os.path.join(output_dir, cfg["filename"])
        print(f"[*] Generating {cfg['filename']} -> {cfg['nodes']} nodes, {cfg['parcels']} parcels, W={cfg['capacity']}kg...")
        dataset = build_dataset_dict(
            name=cfg["name"],
            num_nodes=cfg["nodes"],
            num_parcels=cfg["parcels"],
            capacity=cfg["capacity"],
            seed=cfg["seed"],
            grid_size=cfg["grid_size"],
            max_parcel_weight=cfg["max_parcel_weight"],
        )
        save_dataset(dataset, filepath)
        file_size_kb = os.path.getsize(filepath) / 1024.0
        print(f"    [+] Saved to {filepath} ({file_size_kb:.1f} KB)")

    print("\n[+] All datasets successfully created in:", os.path.abspath(output_dir))


if __name__ == "__main__":
    generate_all_datasets()

