"""
Mini-Courier Planner - Core Data Models
Design & Analysis of Algorithms Capstone

Defines the core data structures used across all phases of the pipeline:
- Parcel: Represents a customer package with delivery constraints.
- GraphNode: Represents a junction or delivery point in the road graph.
- Edge: Represents a directed/undirected weighted road connection.
- DeliveryPlan: Encapsulates the output of the full planning pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any


@dataclass
class Parcel:
    """
    Represents an individual parcel to be delivered.

    Attributes:
        pid: Unique identifier for the parcel (e.g., 'P001').
        dest: Destination node ID in the road graph (must be >= 1; node 0 is depot).
        weight: Parcel weight in integer kilograms (used in 0/1 Knapsack).
        priority: Urgency level on a 1-5 scale (5 = critical/same-day).
        deadline: Delivery deadline in hours from dispatch (e.g., 4 = within 4 hours).
    """
    pid: str
    dest: int
    weight: int
    priority: int
    deadline: int

    @property
    def value(self) -> int:
        """
        Computes the dynamic knapsack value of the parcel.
        Formula: value = (priority * 10) + max(0, 24 - deadline)

        Rationale:
        - Higher priority (1-5) scales directly by 10 (10 to 50 base value).
        - Deadlines under 24 hours add a bonus reflecting urgency (up to +23 for a 1h deadline).
        - Parcels with deadlines beyond 24 hours receive 0 bonus but retain their base priority value.
        """
        return (self.priority * 10) + max(0, 24 - self.deadline)

    @property
    def sort_key(self) -> Tuple[int, int]:
        """
        Primary sort criteria:
        1. deadline ASCENDING (earlier deadlines served first).
        2. priority DESCENDING (higher priority breaks deadline ties).
        
        Represented as a tuple (deadline, -priority) for standard comparisons.
        """
        return (self.deadline, -self.priority)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the parcel to a dictionary."""
        return {
            "pid": self.pid,
            "dest": self.dest,
            "weight": self.weight,
            "priority": self.priority,
            "deadline": self.deadline,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Parcel":
        """Deserializes a parcel from a dictionary."""
        return cls(
            pid=str(data["pid"]),
            dest=int(data["dest"]),
            weight=int(data["weight"]),
            priority=int(data["priority"]),
            deadline=int(data["deadline"]),
        )

    def __repr__(self) -> str:
        return (f"Parcel({self.pid}, dest={self.dest}, w={self.weight}kg, "
                f"pri={self.priority}, dline={self.deadline}h, val={self.value})")


@dataclass
class Edge:
    """Represents a weighted road segment between two graph nodes."""
    u: int
    v: int
    weight: float


@dataclass
class DeliveryPlan:
    """
    Encapsulates the end-to-end output of the Mini-Courier Planner pipeline.
    """
    dataset_name: str
    van_capacity: int
    total_parcels_available: int
    
    # Phase 2 outputs
    sorted_parcels: List[Parcel]
    chosen_parcels: List[Parcel]
    total_weight: int
    total_value: int
    capacity_utilization: float
    
    # Phase 3 outputs
    stops: List[int]                     # Distinct stops including depot 0
    distance_matrix: Dict[Tuple[int, int], float]
    tsp_tour: List[int]                  # High-level stop order: [0, s1, s2, ..., 0]
    road_path: List[int]                 # Expanded physical junction sequence
    total_distance: float                # Total road distance in km
    
    # Phase 4 performance profiling
    execution_times: Dict[str, float] = field(default_factory=dict)

