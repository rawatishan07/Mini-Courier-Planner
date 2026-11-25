# Mini-Courier Planner: Viva & Technical Interview Notes

**Course:** Design & Analysis of Algorithms (ETCCDA302)  
**Institution:** K.R. Mangalam University, Gurugram, Haryana  
**Faculty Evaluator:** Dr. Shweta Agarwal  
**Student Topic:** Mini-Courier Logistics Optimization System

---

## Part 1: Worked Numerical Trace of 0/1 Knapsack DP

During viva evaluation, you may be handed a piece of paper and asked to manually trace the Dynamic Programming table and explain backtracking. Here is the canonical small example matching the project's logic:

### Input Parameters
- **Van Payload Capacity ($W$):** $6\text{ kg}$
- **Parcels Available ($n = 4$):**
  1. **Item 1 ($P_1$):** Weight $w_1 = 2\text{ kg}$, Value $v_1 = 30$
  2. **Item 2 ($P_2$):** Weight $w_2 = 3\text{ kg}$, Value $v_2 = 40$
  3. **Item 3 ($P_3$):** Weight $w_3 = 4\text{ kg}$, Value $v_3 = 50$
  4. **Item 4 ($P_4$):** Weight $w_4 = 1\text{ kg}$, Value $v_4 = 25$

---

### Step-by-Step DP State Transitions
Recurrence:
$$dp[i][w] = \begin{cases} 
dp[i-1][w] & \text{if } w_i > w \\
\max(dp[i-1][w], \, dp[i-1][w - w_i] + v_i) & \text{if } w_i \le w 
\end{cases}$$

#### Row $i = 0$ (Base Case: 0 items)
$dp[0][w] = 0$ for all $w \in \{0, 1, 2, 3, 4, 5, 6\}$.

#### Row $i = 1$ ($P_1$: $w_1 = 2, v_1 = 30$)
- For $w < 2$: $dp[1][w] = dp[0][w] = 0$.
- For $w \ge 2$: $dp[1][w] = \max(dp[0][w], dp[0][w-2] + 30) = 30$.
  *Row 1:* `[0, 0, 30, 30, 30, 30, 30]`

#### Row $i = 2$ ($P_2$: $w_2 = 3, v_2 = 40$)
- $w = 0, 1$: $w_2 > w \implies dp[2][w] = dp[1][w] = 0$.
- $w = 2$: $w_2 > w \implies dp[2][2] = dp[1][2] = 30$.
- $w = 3$: $\max(dp[1][3], dp[1][0] + 40) = \max(30, 40) = 40$.
- $w = 4$: $\max(dp[1][4], dp[1][1] + 40) = \max(30, 40) = 40$.
- $w = 5$: $\max(dp[1][5], dp[1][2] + 40) = \max(30, 30 + 40) = 70$.
- $w = 6$: $\max(dp[1][6], dp[1][3] + 40) = \max(30, 30 + 40) = 70$.
  *Row 2:* `[0, 0, 30, 40, 40, 70, 70]`

#### Row $i = 3$ ($P_3$: $w_3 = 4, v_3 = 50$)
- $w = 0, 1$: $dp[3][w] = 0$.
- $w = 2$: $dp[3][2] = 30$.
- $w = 3$: $dp[3][3] = 40$.
- $w = 4$: $\max(dp[2][4], dp[2][0] + 50) = \max(40, 50) = 50$.
- $w = 5$: $\max(dp[2][5], dp[2][1] + 50) = \max(70, 50) = 70$.
- $w = 6$: $\max(dp[2][6], dp[2][2] + 50) = \max(70, 30 + 50) = 80$.
  *Row 3:* `[0, 0, 30, 40, 50, 70, 80]`

#### Row $i = 4$ ($P_4$: $w_4 = 1, v_4 = 25$)
- $w = 0$: $0$.
- $w = 1$: $\max(dp[3][1], dp[3][0] + 25) = 25$.
- $w = 2$: $\max(dp[3][2], dp[3][1] + 25) = \max(30, 25) = 30$.
- $w = 3$: $\max(dp[3][3], dp[3][2] + 25) = \max(40, 30 + 25) = 55$.
- $w = 4$: $\max(dp[3][4], dp[3][3] + 25) = \max(50, 40 + 25) = 65$.
- $w = 5$: $\max(dp[3][5], dp[3][4] + 25) = \max(70, 50 + 25) = 75$.
- $w = 6$: $\max(dp[3][6], dp[3][5] + 25) = \max(80, 70 + 25) = 95$.
  *Row 4:* `[0, 25, 30, 55, 65, 75, 95]`

---

### Complete DP Matrix

| Item ($w_i, v_i$) | $w = 0$ | $w = 1$ | $w = 2$ | $w = 3$ | $w = 4$ | $w = 5$ | $w = 6$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0: Initial** | **0\*** | 0 | 0 | 0 | 0 | 0 | 0 |
| **1: $P_1$ (2kg, 30v)** | 0 | 0 | **30\*** | 30 | 30 | 30 | 30 |
| **2: $P_2$ (3kg, 40v)** | 0 | 0 | 30 | 40 | 40 | **70\*** | 70 |
| **3: $P_3$ (4kg, 50v)** | 0 | 0 | 30 | 40 | 50 | **70\*** | 80 |
| **4: $P_4$ (1kg, 25v)** | 0 | 25 | 30 | 55 | 65 | 75 | **95\*** |

*(Cells marked with \* trace the optimal backtracking path)*

### Backtracking Walkthrough:
1. Start at $(i = 4, w = 6)$: $dp[4][6] = 95 \ne dp[3][6] = 80 \implies \mathbf{P_4\text{ SELECTED}}$.  
   Next capacity: $w \leftarrow 6 - 1 = 5$.
2. At $(i = 3, w = 5)$: $dp[3][5] = 70 == dp[2][5] = 70 \implies \text{P}_3\text{ NOT selected}$.  
   Next capacity: $w \leftarrow 5$.
3. At $(i = 2, w = 5)$: $dp[2][5] = 70 \ne dp[1][5] = 30 \implies \mathbf{P_2\text{ SELECTED}}$.  
   Next capacity: $w \leftarrow 5 - 3 = 2$.
4. At $(i = 1, w = 2)$: $dp[1][2] = 30 \ne dp[0][2] = 0 \implies \mathbf{P_1\text{ SELECTED}}$.  
   Next capacity: $w \leftarrow 2 - 2 = 0$.
5. Final Selected Manifest: $\{P_1, P_2, P_4\}$  
   - Total Weight: $2 + 3 + 1 = 6\text{ kg} \le 6\text{ kg}$ (100% capacity utilization)
   - Total Value: $30 + 40 + 25 = 95\text{ points}$ (Matches $dp[4][6]$ exactly).

---

## Part 2: Rigorous Complexity Derivations

### 1. Merge Sort Complexity
- **Divide:** Finding middle index takes $O(1)$ time.
- **Conquer:** Two recursive subproblems of size $n/2$, yielding $2T(n/2)$.
- **Combine (Merge):** Merging two sorted subarrays takes linear time $c \cdot n$.
- **Recurrence:** $T(n) = 2T(n/2) + c \cdot n$.
- **Master Theorem:** $a = 2, b = 2, f(n) = n \implies n^{\log_b a} = n^1 = n = \Theta(f(n))$ (Case 2).  
  Therefore, $T(n) = \Theta(n \log n)$ across Best, Average, and Worst cases.
- **Space Complexity:** Auxiliary list needed to merge elements: $O(n)$ space.

### 2. 0/1 Knapsack DP Complexity
- **Time Complexity:** The table contains $(n + 1) \times (W + 1)$ cells. Each cell performs $O(1)$ constant-time arithmetic comparisons.  
  Hence, Time Complexity $= \Theta(n \cdot W)$.
  *Why is this "Pseudo-Polynomial"?* The input size of integer $W$ is the number of bits required to encode it: $k = \lceil \log_2 W \rceil$. In terms of input bit length $k$, the runtime is $\Theta(n \cdot 2^k)$, which is exponential in input size.
- **Space Complexity:** Storing the complete table requires $\Theta(n \cdot W)$ memory words.

### 3. Dijkstra's Algorithm Complexity
- **Operations:**
  - $|V|$ calls to `insert` into MinHeap: $|V| \cdot O(\log |V|)$.
  - $|V|$ calls to `extract_min` from MinHeap: $|V| \cdot O(\log |V|)$.
  - $|E|$ edge relaxations, each triggering an `insert` (or decrease-key): $|E| \cdot O(\log |V|)$.
- **Total Time:** $(|V| + |E|) \log |V| = O((V + E) \log V)$.
- **Space Complexity:** $O(|V|)$ memory for `dist`, `prev`, and MinHeap storage.

### 4. Nearest-Neighbour TSP & 2-Opt Complexity
- **Nearest-Neighbour:** From each stop, scanning all unvisited candidates takes $K, K-1, \dots, 1$ comparisons:  
  $\sum_{i=1}^K i = \frac{K(K+1)}{2} = \Theta(K^2)$ time.
- **2-Opt Local Search:** Each iteration evaluates all pairs of edges: $\binom{K}{2} = \frac{K(K-1)}{2} = O(K^2)$.  
  Total time $= O(\text{iterations} \cdot K^2)$.

---

## Part 3: Top 25 Viva Questions & Model Answers

### Q1: Why did you choose Merge Sort as the primary sorter over Quick Sort?
**Answer:** In courier logistics, order stability is essential. If two parcels have identical deadlines and priorities, a stable algorithm guarantees they preserve their original FIFO booking order. Merge Sort is inherently stable ($\le$ comparison during merge) and guarantees a predictable $O(n \log n)$ worst-case runtime, whereas Quick Sort is unstable and can degrade to $O(n^2)$.

### Q2: Why is 0/1 Knapsack NP-Complete while Fractional Knapsack is polynomial?
**Answer:** Fractional Knapsack exhibits the **Greedy Choice Property**: items can be split arbitrarily, allowing an optimal solution by greedily picking items in descending order of value-to-weight ratio in $O(n \log n)$ time. In 0/1 Knapsack, items are indivisible (all-or-nothing), which means a greedy choice can lead to suboptimal dead space. Hence, 0/1 Knapsack requires examining exponential combinations, making it NP-complete.

### Q3: What happens to 0/1 Knapsack DP if weights are floating-point numbers (e.g., 2.35 kg)?
**Answer:** The tabular DP approach relies on indexing array columns by discrete integer weights $w \in \{0, 1, \dots, W\}$. If weights are floating-point, this discretization breaks down. One can either:
1. Multiply all weights by $10^k$ (e.g., 100 for grams) to convert them to integers, which increases $W$ and table size.
2. Use Branch-and-Bound, Meet-in-the-Middle, or integer linear programming (MIP) solvers.

### Q4: Why does Dijkstra's algorithm fail if the graph has negative edge weights?
**Answer:** Dijkstra's algorithm relies on the **Greedy Choice Invariant**: once a vertex $u$ is extracted from the priority queue, its shortest path distance is permanently finalized. This assumes extending a path through any other vertex will only accumulate non-negative weight. If negative edges exist, a longer path could subsequently become shorter, violating this invariant and producing incorrect distances. Bellman-Ford must be used instead.

### Q5: How did you implement Dijkstra without using Python's `heapq` module?
**Answer:** We wrote a custom `MinHeap` class from scratch using an array representation where for index $i$, left child is $2i+1$, right child is $2i+2$, and parent is $\lfloor (i-1)/2 \rfloor$. We implemented `_sift_up` for inserts and `_sift_down` for `extract_min`, preserving the min-heap invariant ($A[\text{parent}] \le A[\text{child}]$) with zero external libraries.

### Q6: What is the Triangle Inequality and why is it guaranteed in your TSP implementation?
**Answer:** The Triangle Inequality states that $d(u, w) \le d(u, v) + d(v, w)$ for any three nodes. In our pipeline, the distance matrix between delivery stops is populated by running Dijkstra's shortest-path algorithm. Because $d(u, w)$ is defined as the *true shortest path* in the road network, it is impossible for an intermediate detour through $v$ to be strictly shorter than the shortest path itself. Therefore, the metric property holds unconditionally.

### Q7: What is the theoretical approximation factor of Nearest-Neighbour TSP?
**Answer:** For general metric graphs, the Nearest-Neighbour heuristic has an approximation ratio of:
$$\frac{\text{Cost}(NN)}{\text{Cost}(OPT)} \le \frac{1}{2}\lceil\log_2 K\rceil + \frac{1}{2} = O(\log K)$$
In practice on planar road networks, NN typically achieves within $1.10\times$ to $1.25\times$ of the optimal tour, which 2-Opt frequently improves to within $1.00\times$ to $1.03\times$.

### Q8: How does 2-Opt improve the Nearest-Neighbour tour?
**Answer:** 2-Opt is a local search heuristic that iteratively tests replacing two non-adjacent edges $(u_1, v_1)$ and $(u_2, v_2)$ with $(u_1, u_2)$ and $(v_1, v_2)$. In 2D space, this effectively reverses the intermediate sequence of stops, untangling geometric crossings where roads intersect inefficiently. It continues until no further distance reduction ($\Delta < 0$) is possible.

### Q9: How does road path expansion work?
**Answer:** The TSP tour gives a sequence of delivery stops (e.g., $[0, 8, 3, 0]$). However, stops are not necessarily directly connected by a single road. During the Dijkstra phase, we save the predecessor tree `prev` for each stop. For each leg $(u \to v)$, we trace back pointers using `reconstruct_path(prev_u, u, v)` to get intermediate road junctions (e.g., $[0, 1, 4, 8]$) and concatenate them into an unbroken physical route.

### Q10: How does your 3-way Quick Sort handle arrays with many duplicate elements?
**Answer:** Standard Quick Sort with 2-way partitioning degrades towards $O(n^2)$ when keys are identical because all elements fall on one side of the pivot. Our 3-way Quick Sort (Dutch National Flag) partitions the array into three regions: strictly less than pivot, strictly equal to pivot, and strictly greater than pivot. It then only recurses on the less-than and greater-than partitions, processing identical elements in $O(n)$ linear time.

---

## Part 4: Code Modification Scenarios (Viva Coding Challenges)

### Challenge 1: "Modify the Knapsack code so each parcel has a volume limit $V_{max}$ in addition to weight $W$."
**Answer:** This transforms the problem into a 2D-Knapsack:
- DP table becomes 3-dimensional: `dp[i][w][v]`.
- Size: $(n+1) \times (W+1) \times (V_{max}+1)$.
- Recurrence:
  ```python
  if parcel.weight > w or parcel.volume > v:
      dp[i][w][v] = dp[i-1][w][v]
  else:
      dp[i][w][v] = max(dp[i-1][w][v], dp[i-1][w - parcel.weight][v - parcel.volume] + parcel.value)
  ```
- Time Complexity: $O(n \cdot W \cdot V_{max})$.

### Challenge 2: "How would you handle a real-time parcel cancellation after packing?"
**Answer:**
- Remove the canceled parcel from `chosen_parcels`.
- Recalculate `stops = {0} ∪ {p.dest for p in remaining_chosen_parcels}`.
- If the canceled parcel was the only delivery at that destination node, simply remove that stop from `stops` and re-run TSP Nearest-Neighbour and 2-Opt on the cached distance matrix.
- Because the distance matrix is pre-computed, re-routing takes $< 1\text{ ms}$ without needing to re-run Dijkstra!

### Challenge 3: "How would you incorporate Electric Vehicle (EV) battery constraints?"
**Answer:**
- Let van battery capacity allow at most $D_{max}$ km per charge.
- If the TSP tour length exceeds $D_{max}$, identify charging stations in the road graph.
- Using Dijkstra, find the charging station that minimizes detour cost when remaining range drops below a threshold $\tau$, inserting the recharge stop into the tour.

### Challenge 4: "How would you scale this to multiple delivery vans (Vehicle Routing Problem - VRP)?"
**Answer:**
- Apply the **Cluster-First, Route-Second** paradigm:
  1. Solve multiple 0/1 knapsacks or use K-Means clustering to partition parcels among $M$ vans based on capacity and spatial proximity.
  2. Run Dijkstra and Nearest-Neighbour + 2-Opt independently for each van's designated stops.

