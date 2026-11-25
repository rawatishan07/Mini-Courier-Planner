"""
Mini-Courier Planner - 0/1 Knapsack Dynamic Programming Module
Design & Analysis of Algorithms Capstone

Implements the 0/1 Knapsack problem using Bottom-Up Dynamic Programming:
- Weight constraint: Courier van payload capacity W (integer kg).
- Item weight: Parcel weight (integer kg).
- Item value: priority * 10 + max(0, 24 - deadline).
- Stores the complete (n + 1) x (W + 1) DP table.
- Backtracks to recover the exact subset of chosen parcels.
- Formats and displays the DP table for small datasets.
- Includes an exhaustive brute-force solver for formal correctness verification.
"""

from typing import List, Tuple, Optional
from courier.models import Parcel


def knapsack_01_dp(
    parcels: List[Parcel], capacity: int
) -> Tuple[List[Parcel], int, int, List[List[int]]]:
    """
    Solves the 0/1 Knapsack problem using bottom-up Dynamic Programming.

    Mathematical Formulation:
    - Let n = len(parcels), W = capacity.
    - Let w_i = parcels[i-1].weight, v_i = parcels[i-1].value.
    - State definition:
        dp[i][w] = Maximum value obtainable using a subset of the first i parcels
                   such that the total weight does not exceed w kg.
    - Base Cases:
        dp[0][w] = 0   for all 0 <= w <= W (no parcels available)
        dp[i][0] = 0   for all 0 <= i <= n (zero carrying capacity)
    - Bellman Optimality Recurrence:
        dp[i][w] = dp[i-1][w]                                    if w_i > w
        dp[i][w] = max(dp[i-1][w], dp[i-1][w - w_i] + v_i)        if w_i <= w

    Complexity:
    - Time Complexity:  O(n * W) pseudo-polynomial time.
    - Space Complexity: O(n * W) auxiliary table space.

    Args:
        parcels: List of candidate parcels.
        capacity: Maximum weight capacity of the courier van (integer kg).

    Returns:
        Tuple containing:
        1. chosen_parcels (List[Parcel]): Parcels selected for the delivery trip.
        2. total_weight (int): Total weight of the selected parcels.
        3. total_value (int): Total priority value achieved (equals dp[n][W]).
        4. dp_table (List[List[int]]): The full (n+1) x (W+1) DP matrix.
    """
    n = len(parcels)
    W = max(0, capacity)

    # Initialize (n + 1) x (W + 1) DP table with zeros
    dp: List[List[int]] = [[0] * (W + 1) for _ in range(n + 1)]

    # Populate DP table row by row (Bottom-Up)
    for i in range(1, n + 1):
        parcel = parcels[i - 1]
        p_weight = parcel.weight
        p_value = parcel.value

        for w in range(W + 1):
            if p_weight > w:
                # Cannot include parcel: weight exceeds current capacity limit
                dp[i][w] = dp[i - 1][w]
            else:
                # Choose optimal between excluding or including the parcel
                exclude_val = dp[i - 1][w]
                include_val = dp[i - 1][w - p_weight] + p_value
                dp[i][w] = exclude_val if exclude_val >= include_val else include_val

    # Backtracking to reconstruct the optimal set of chosen parcels
    chosen_parcels: List[Parcel] = []
    curr_w = W
    for i in range(n, 0, -1):
        # If the value changed from the row above, parcel i-1 was included
        if dp[i][curr_w] != dp[i - 1][curr_w]:
            selected_parcel = parcels[i - 1]
            chosen_parcels.append(selected_parcel)
            curr_w -= selected_parcel.weight

    # Reverse to maintain original sorted priority order
    chosen_parcels.reverse()

    total_weight = sum(p.weight for p in chosen_parcels)
    total_value = dp[n][W]

    return chosen_parcels, total_weight, total_value, dp


def format_dp_table(
    parcels: List[Parcel],
    capacity: int,
    dp_table: List[List[int]],
    highlight_backtrack: bool = True,
) -> str:
    """
    Formats the 0/1 Knapsack DP table into a readable ASCII representation.
    Ideal for academic demonstration, lab reports, and viva evaluation.

    Marks cells along the optimal backtracking trace with an asterisk (*).
    """
    n = len(parcels)
    W = capacity

    # Identify backtracking path coordinates
    backtrack_cells = set()
    if highlight_backtrack:
        curr_w = W
        for i in range(n, 0, -1):
            backtrack_cells.add((i, curr_w))
            if dp_table[i][curr_w] != dp_table[i - 1][curr_w]:
                curr_w -= parcels[i - 1].weight
        backtrack_cells.add((0, curr_w))

    lines = []
    # Table header
    header_col0 = "Item (w, v)"
    col_width = 6
    hdr = f"{header_col0:<18} | " + " | ".join(f"w={w:>{col_width-3}}" for w in range(W + 1))
    separator = "-" * len(hdr)
    lines.append(separator)
    lines.append(hdr)
    lines.append(separator)

    # Row 0: Base case (0 items)
    row0_label = "0: [Initial]"
    row0_vals = []
    for w in range(W + 1):
        marker = "*" if (0, w) in backtrack_cells else " "
        row0_vals.append(f"{dp_table[0][w]:>{col_width-2}}{marker}")
    lines.append(f"{row0_label:<18} | " + " | ".join(row0_vals))

    # Rows 1..n: Each parcel
    for i in range(1, n + 1):
        p = parcels[i - 1]
        label = f"{i}: {p.pid} ({p.weight}k,{p.value}v)"
        row_vals = []
        for w in range(W + 1):
            marker = "*" if (i, w) in backtrack_cells else " "
            row_vals.append(f"{dp_table[i][w]:>{col_width-2}}{marker}")
        lines.append(f"{label:<18} | " + " | ".join(row_vals))

    lines.append(separator)
    lines.append("(* denotes cells along the optimal backtracking path)")
    return "\n".join(lines)


def knapsack_brute_force(
    parcels: List[Parcel], capacity: int
) -> Tuple[List[Parcel], int, int]:
    """
    Exhaustive 2^n solver for the 0/1 Knapsack problem.
    Used exclusively as an independent verification benchmark in test suites.

    Complexity:
    - Time Complexity:  O(2^n * n)
    - Space Complexity: O(n) for recursion stack.
    """
    n = len(parcels)
    best_value = 0
    best_weight = 0
    best_subset: List[Parcel] = []

    # Iterate through all 2^n binary bitmasks
    total_subsets = 1 << n
    for mask in range(total_subsets):
        curr_weight = 0
        curr_value = 0
        current_subset = []
        possible = True

        for i in range(n):
            if (mask >> i) & 1:
                p = parcels[i]
                curr_weight += p.weight
                curr_value += p.value
                current_subset.append(p)
                if curr_weight > capacity:
                    possible = False
                    break

        if possible and curr_value > best_value:
            best_value = curr_value
            best_weight = curr_weight
            best_subset = current_subset

    return best_subset, best_weight, best_value

