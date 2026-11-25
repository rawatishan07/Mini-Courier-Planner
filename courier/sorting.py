"""
Mini-Courier Planner - Sorting Algorithms Module
Design & Analysis of Algorithms Capstone

Implements hand-crafted sorting algorithms with zero library shortcuts:
1. Merge Sort: Stable divide-and-conquer algorithm. Used as the PRIMARY sorter.
2. Quick Sort: Randomized pivot with 3-way (Dutch National Flag) partitioning.
   Serves as an empirical baseline.
3. Bubble Sort: O(n^2) exchange sort with early termination flag.
   Serves as an empirical baseline.

Sorting Criteria for Parcels:
- Primary key: Deadline ASCENDING (urgent delivery deadlines served first).
- Secondary key: Priority DESCENDING (higher priority breaks deadline ties).
- Stable sorting guarantees that parcels with equal deadline and priority retain
  their original FIFO registration order.
"""

import random
from typing import List, Callable, Any, TypeVar

T = TypeVar("T")


def _default_key(item: Any) -> Any:
    """Default key extractor: uses the item's sort_key if present, else item."""
    if hasattr(item, "sort_key"):
        return item.sort_key
    return item


# ============================================================================
# 1. MERGE SORT (Stable, Primary Algorithm)
# ============================================================================

def merge_sort(items: List[T], key: Callable[[T], Any] = _default_key) -> List[T]:
    """
    Sorts a list of items using stable Merge Sort.

    Algorithm Rationale:
    - Divide-and-Conquer strategy: recursively splits list into halves until
      base case (size <= 1), then merges sorted sublists.
    - Stability: When comparing elements with equal keys, the element from
      the left sublist is always placed first (<= comparison).
    - Crucial for courier logistics: preserves FIFO registration order for
      parcels with identical deadlines and priorities.

    Complexity:
    - Time Complexity:
        * Best Case:    O(n log n)
        * Average Case: O(n log n)
        * Worst Case:   O(n log n)
    - Space Complexity: O(n) auxiliary memory for merging buffers.

    Args:
        items: List of items to be sorted.
        key: Function to extract a comparison key from each item.

    Returns:
        A new list containing the items in sorted order.
    """
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left_sorted = merge_sort(items[:mid], key=key)
    right_sorted = merge_sort(items[mid:], key=key)

    return _merge(left_sorted, right_sorted, key=key)


def _merge(left: List[T], right: List[T], key: Callable[[T], Any]) -> List[T]:
    """
    Merges two sorted lists into a single sorted list while maintaining stability.
    """
    merged: List[T] = []
    i = 0
    j = 0
    len_left = len(left)
    len_right = len(right)

    while i < len_left and j < len_right:
        # Crucial for stability: '<=' ensures left element precedes right on equality
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append remaining elements
    if i < len_left:
        merged.extend(left[i:])
    if j < len_right:
        merged.extend(right[j:])

    return merged


# ============================================================================
# 2. QUICK SORT (Randomized Pivot + 3-Way Partitioning, Baseline)
# ============================================================================

def quick_sort(items: List[T], key: Callable[[T], Any] = _default_key) -> List[T]:
    """
    Sorts a list of items using Randomized 3-Way Quick Sort (Dutch National Flag).

    Algorithm Rationale:
    - Randomized Pivot: Prevents O(n^2) worst-case degradation on pre-sorted or
      adversarial inputs.
    - 3-Way Partitioning: Groups elements into (< pivot), (== pivot), (> pivot).
      Handles massive datasets with redundant deadline/priority values in linear
      time O(n) for the identical segment.
    - Note: Standard Quick Sort is NOT stable.

    Complexity:
    - Time Complexity:
        * Best Case:    O(n log n) [or O(n) if all elements are identical]
        * Average Case: O(n log n)
        * Worst Case:   O(n^2) [vanishingly rare with random pivots]
    - Space Complexity: O(log n) auxiliary stack space for recursion.

    Args:
        items: List of items to sort.
        key: Function to extract comparison key.

    Returns:
        A new list containing the items in sorted order.
    """
    arr = list(items)
    _quick_sort_in_place(arr, 0, len(arr) - 1, key)
    return arr


def _quick_sort_in_place(arr: List[T], low: int, high: int, key: Callable[[T], Any]) -> None:
    """In-place recursive quick sort driver using 3-way partitioning."""
    if low >= high:
        return

    # Randomized pivot selection to guard against O(n^2) degenerate cases
    pivot_idx = random.randint(low, high)
    arr[low], arr[pivot_idx] = arr[pivot_idx], arr[low]
    pivot_val = key(arr[low])

    # Dutch National Flag 3-way partitioning:
    # arr[low .. lt-1]   < pivot
    # arr[lt .. i-1]     == pivot
    # arr[gt+1 .. high]  > pivot
    lt = low
    gt = high
    i = low + 1

    while i <= gt:
        item_val = key(arr[i])
        if item_val < pivot_val:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif item_val > pivot_val:
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:
            i += 1

    # Recursively sort the strict partitions
    _quick_sort_in_place(arr, low, lt - 1, key)
    _quick_sort_in_place(arr, gt + 1, high, key)


# ============================================================================
# 3. BUBBLE SORT (Baseline)
# ============================================================================

def bubble_sort(items: List[T], key: Callable[[T], Any] = _default_key) -> List[T]:
    """
    Sorts a list of items using optimized Bubble Sort with an early-exit flag.

    Algorithm Rationale:
    - Repeatedly steps through the list, compares adjacent elements, and swaps
      them if they are out of order.
    - Early exit: If no swaps occur in a full pass, the list is already sorted.
    - Serves as the elementary quadratic benchmark for university evaluation.

    Complexity:
    - Time Complexity:
        * Best Case:    O(n) [already sorted, 1 pass]
        * Average Case: O(n^2)
        * Worst Case:   O(n^2) [reverse sorted]
    - Space Complexity: O(1) auxiliary space (in-place on a shallow copy).

    Args:
        items: List of items to sort.
        key: Function to extract comparison key.

    Returns:
        A new list containing the items in sorted order.
    """
    arr = list(items)
    n = len(arr)

    for i in range(n):
        swapped = False
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            if key(arr[j]) > key(arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break

    return arr


# ============================================================================
# UNIFIED INTERFACE
# ============================================================================

def sort_parcels(parcels: List[Any], algorithm: str = "merge") -> List[Any]:
    """
    Dispatches parcel sorting to the requested algorithm.

    Supported algorithms:
    - 'merge' (default, stable, recommended for courier pipeline)
    - 'quick' (randomized 3-way quicksort baseline)
    - 'bubble' (elementary baseline)
    """
    algo = algorithm.lower().strip()
    if algo == "merge":
        return merge_sort(parcels, key=_default_key)
    elif algo == "quick":
        return quick_sort(parcels, key=_default_key)
    elif algo == "bubble":
        return bubble_sort(parcels, key=_default_key)
    else:
        raise ValueError(f"Unknown sorting algorithm '{algorithm}'. Choose 'merge', 'quick', or 'bubble'.")

