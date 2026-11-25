"""
Mini-Courier Planner - Road Graph & Dijkstra Module
Design & Analysis of Algorithms Capstone

Implements:
1. MinHeap: A hand-crafted binary min-heap priority queue with zero library shortcuts.
2. RoadGraph: Adjacency-list undirected weighted graph representation.
3. Dijkstra's Algorithm: Single-source shortest path using the hand-crafted MinHeap.
4. Path Reconstruction: Recovers explicit road junction sequences from prev pointers.
5. Bellman-Ford Algorithm: O(V * E) independent verifier for correctness testing.
"""

from typing import List, Dict, Tuple, Optional, Any
import math


# ============================================================================
# 1. HAND-CRAFTED BINARY MIN-HEAP (Zero Library Shortcuts)
# ============================================================================

class MinHeap:
    """
    Binary Min-Heap Priority Queue implemented from scratch.
    Maintains min-heap property: parent <= children.

    Time Complexities:
    - Insert:      O(log N)
    - Extract-Min: O(log N)
    - Peek:        O(1)
    - Is-Empty:    O(1)
    Space Complexity: O(N)
    """

    def __init__(self) -> None:
        # Each entry is a tuple: (priority_key, value)
        self._heap: List[Tuple[float, Any]] = []

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def insert(self, key: float, value: Any) -> None:
        """Inserts a new element (key, value) and restores the heap property."""
        self._heap.append((key, value))
        self._sift_up(len(self._heap) - 1)

    def extract_min(self) -> Tuple[float, Any]:
        """Removes and returns the minimum element (key, value)."""
        if self.is_empty():
            raise IndexError("extract_min called on an empty MinHeap.")
        
        # Swap root with the last element
        min_elem = self._heap[0]
        last_elem = self._heap.pop()

        if not self.is_empty():
            self._heap[0] = last_elem
            self._sift_down(0)

        return min_elem

    def peek(self) -> Tuple[float, Any]:
        """Returns the minimum element without removing it."""
        if self.is_empty():
            raise IndexError("peek called on an empty MinHeap.")
        return self._heap[0]

    def _sift_up(self, idx: int) -> None:
        """Bubbles an element up until the min-heap property is satisfied."""
        while idx > 0:
            parent_idx = (idx - 1) // 2
            if self._heap[idx][0] < self._heap[parent_idx][0]:
                self._heap[idx], self._heap[parent_idx] = self._heap[parent_idx], self._heap[idx]
                idx = parent_idx
            else:
                break

    def _sift_down(self, idx: int) -> None:
        """Pushes an element down until the min-heap property is satisfied."""
        n = len(self._heap)
        while True:
            left_child = 2 * idx + 1
            right_child = 2 * idx + 2
            smallest = idx

            if left_child < n and self._heap[left_child][0] < self._heap[smallest][0]:
                smallest = left_child
            if right_child < n and self._heap[right_child][0] < self._heap[smallest][0]:
                smallest = right_child

            if smallest != idx:
                self._heap[idx], self._heap[smallest] = self._heap[smallest], self._heap[idx]
                idx = smallest
            else:
                break


# ============================================================================
# 2. ROAD GRAPH REPRESENTATION
# ============================================================================

class RoadGraph:
    """
    Represents an undirected weighted road network using adjacency lists.
    Node 0 is permanently designated as the central logistics depot.
    """

    def __init__(self, num_nodes: int = 0) -> None:
        self.num_nodes = num_nodes
        # Adjacency list: node_id -> List of (neighbor_id, weight)
        self.adj: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(num_nodes)}
        # Spatial 2D coordinates for visual plotting: node_id -> (x, y)
        self.coordinates: Dict[int, Tuple[float, float]] = {}

    def add_node(self, node_id: int, x: float = 0.0, y: float = 0.0) -> None:
        """Adds or updates a node with optional 2D coordinates."""
        if node_id not in self.adj:
            self.adj[node_id] = []
            if node_id >= self.num_nodes:
                self.num_nodes = node_id + 1
        self.coordinates[node_id] = (x, y)

    def add_edge(self, u: int, v: int, weight: float) -> None:
        """
        Adds an undirected road segment between junction u and junction v.
        Weight must be non-negative (road distance or transit time).
        """
        if weight < 0:
            raise ValueError(f"Dijkstra requires non-negative weights; got {weight}.")
        
        # Ensure nodes exist
        if u not in self.adj:
            self.add_node(u)
        if v not in self.adj:
            self.add_node(v)

        self.adj[u].append((v, float(weight)))
        self.adj[v].append((u, float(weight)))

    def get_neighbors(self, u: int) -> List[Tuple[int, float]]:
        """Returns list of (neighbor, weight) for node u."""
        return self.adj.get(u, [])

    def get_all_edges(self) -> List[Tuple[int, int, float]]:
        """Returns unique undirected edges (u < v)."""
        edges = []
        for u in self.adj:
            for v, w in self.adj[u]:
                if u < v:
                    edges.append((u, v, w))
        return edges

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the graph for JSON persistence."""
        edges_list = [
            {"u": u, "v": v, "weight": round(w, 2)}
            for u, v, w in self.get_all_edges()
        ]
        coords_dict = {
            str(k): [round(v[0], 2), round(v[1], 2)]
            for k, v in self.coordinates.items()
        }
        return {
            "num_nodes": self.num_nodes,
            "edges": edges_list,
            "coordinates": coords_dict,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoadGraph":
        """Instantiates a RoadGraph from JSON dictionary."""
        num_nodes = data.get("num_nodes", 0)
        graph = cls(num_nodes)
        
        coords = data.get("coordinates", {})
        for node_str, pt in coords.items():
            graph.coordinates[int(node_str)] = (float(pt[0]), float(pt[1]))
            
        for edge in data.get("edges", []):
            graph.add_edge(int(edge["u"]), int(edge["v"]), float(edge["weight"]))
            
        return graph


# ============================================================================
# 3. DIJKSTRA'S ALGORITHM (Hand-Crafted MinHeap)
# ============================================================================

def dijkstra(
    graph: RoadGraph, start: int
) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    """
    Computes single-source shortest paths from `start` to all reachable nodes
    using Dijkstra's algorithm with our hand-crafted MinHeap priority queue.

    Theoretical Properties:
    - Optimal Substructure: Subpaths of shortest paths are shortest paths.
    - Greedy Choice Property: The node with the smallest tentative distance in
      the heap is guaranteed to have reached its optimal shortest distance.
    - Requires all edge weights >= 0.

    Complexity:
    - Time Complexity:  O((|V| + |E|) * log |V|)
        * Each vertex extracted from MinHeap at most once: O(|V| log |V|)
        * Each edge relaxed at most once: O(|E| log |V|)
    - Space Complexity: O(|V|) for dist and prev maps, O(|V|) for MinHeap.

    Args:
        graph: The RoadGraph instance.
        start: Starting source node (junction / depot).

    Returns:
        Tuple (dist, prev):
        - dist: Dict mapping node -> shortest road distance from start.
        - prev: Dict mapping node -> predecessor node on shortest path (None for start).
    """
    dist: Dict[int, float] = {node: float("inf") for node in graph.adj}
    prev: Dict[int, Optional[int]] = {node: None for node in graph.adj}

    dist[start] = 0.0
    heap = MinHeap()
    heap.insert(0.0, start)

    # Track finalized vertices to avoid redundant re-relaxations
    visited = set()

    while not heap.is_empty():
        d_u, u = heap.extract_min()

        # If already visited at an equal or shorter distance, skip stale heap entries
        if u in visited:
            continue
        visited.add(u)

        # Relax all outgoing edges from u
        for v, weight in graph.get_neighbors(u):
            if v in visited:
                continue
            new_dist = d_u + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heap.insert(new_dist, v)

    return dist, prev


def reconstruct_path(
    prev: Dict[int, Optional[int]], start: int, end: int
) -> List[int]:
    """
    Reconstructs the full sequence of intermediate road junctions from `start`
    to `end` by tracing back predecessor pointers from Dijkstra's result.

    Complexity:
    - Time Complexity:  O(H) where H is the hop length of the shortest path (<= |V|).
    - Space Complexity: O(H) for the path list.

    Returns:
        List of nodes [start, j1, j2, ..., end].
        Returns empty list [] if end is unreachable from start.
    """
    if start == end:
        return [start]
    
    path: List[int] = []
    curr: Optional[int] = end

    while curr is not None:
        path.append(curr)
        if curr == start:
            break
        curr = prev.get(curr, None)

    # If the trace did not reach start, the destination is unreachable
    if not path or path[-1] != start:
        return []

    path.reverse()
    return path


# ============================================================================
# 4. BELLMAN-FORD INDEPENDENT VERIFIER
# ============================================================================

def bellman_ford(
    graph: RoadGraph, start: int
) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    """
    Bellman-Ford single-source shortest path algorithm.
    Used exclusively as an independent verification benchmark in test suites.

    Complexity:
    - Time Complexity:  O(|V| * |E|)
    - Space Complexity: O(|V|)
    """
    dist: Dict[int, float] = {node: float("inf") for node in graph.adj}
    prev: Dict[int, Optional[int]] = {node: None for node in graph.adj}
    dist[start] = 0.0

    nodes = list(graph.adj.keys())
    num_nodes = len(nodes)
    edges = graph.get_all_edges()

    # Relax all edges |V| - 1 times
    for _ in range(num_nodes - 1):
        updated = False
        for u, v, w in edges:
            # Undirected graph: relax both directions
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                updated = True
            if dist[v] != float("inf") and dist[v] + w < dist[u]:
                dist[u] = dist[v] + w
                prev[u] = v
                updated = True
        if not updated:
            break

    return dist, prev

