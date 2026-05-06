# Report Notes and Experiment Design

## Problem statement
Given n items with profits p_i and weights w_i, select a subset that maximizes total profit while keeping total weight <= capacity.

## Algorithms used
- Brute Force (exact, exponential)
- Dynamic Programming (exact, pseudo-polynomial)
- Greedy by value/weight ratio (approximate)

## Data sources and how to use them
1) Synthetic (uncorrelated)
   - Generated in memory from uniform ranges for weights and values.
   - Use for sanity checks and small-n behavior.
   - Current synthetic sizes in main.py: n = 5, 8, 10, 12, 15, 18, 20, then large n = 50..1000.
   - Capacity is 40% of total weight, so it does not include very small or very large capacity edge cases.

2) kplib (standard benchmarks)
   - Folder: kplib-master/
   - Format: .kp files with n, capacity, then profit weight pairs.
   - Use categories like 00Uncorrelated, 01WeaklyCorrelated, 02StronglyCorrelated.
   - Current benchmark subset: sizes 50, 100, 200; ratio R01000; seeds 0..2.
   - kplib ratio: R01000 refers to the coefficient range used by the generator (smaller range keeps W and values moderate, so DP is feasible). Larger ratios like R10000 typically yield larger weights/values and capacities.
   - Family meanings:
     - 00Uncorrelated: profits and weights are independent.
     - 01WeaklyCorrelated: profits are roughly weight plus small noise.
     - 02StronglyCorrelated: profits are tightly tied to weights.
   - Why only these families: they are the standard baseline trio and show how correlation affects greedy vs DP without exploding runtime on this machine.

3) Jooken hard instances (2022 EJOR)
   - Folder: knapsackProblemInstances/
   - If problemInstances/ is missing, use generator parameters.
   - Generator parameters: n, capacity, classes, fraction, eps, small.
   - Current benchmark subset: 100 instances from preliminaryExperiment100Names.txt.
   - n values used: 400, 600, 800, 1000, 1200.
   - capacity values used: 1e6, 1e8, 1e10.
   - Purpose: stress-test behavior on hard instances with large n and very large capacities; DP is skipped when cap exceeds the configured limit.


## Experiment details
- Measure time using min of multiple repeats to reduce noise.
- Use identical instances across algorithms for fair comparison.
- Use small n for brute force. Skip brute force when estimated time > 300 seconds.
- Skip DP when capacity > 2,000,000 to avoid O(W) memory blowups on 8GB machines.

## Empirical results
- Compare runtime scaling and solution quality (greedy ratio vs DP).
- Report per-instance tables and summary statistics (avg ratio, min/max).

## Results summary (from results/all_results.csv)
- Total rows: 127 (kplib 27, Jooken 100).
- kplib greedy ratio overall: min 0.9568, avg 0.9943, max 1.0000.
   - 00Uncorrelated: min 0.9963, avg 0.9993, max 1.0000.
   - 01WeaklyCorrelated: min 0.9939, avg 0.9980, max 0.99996.
   - 02StronglyCorrelated: min 0.9568, avg 0.9858, max 0.9960.
- Jooken DP coverage: 37/100 instances have DP results (capacity <= 2,000,000), 63/100 skipped.
- Jooken greedy ratio (for DP-available cases): min 0.9419, avg 0.9943, max 1.0000.
- DP time ranges:
   - kplib: min 0.0448s, avg 0.343s, max 0.812s.
   - Jooken (cap = 1e6 only): min 19.5s, avg 49.5s, max 93.3s.

## Coverage summary (what we covered)
- kplib: uncorrelated, weakly correlated, strongly correlated families; n = 50, 100, 200; ratio R01000; 3 seeds each.
- Jooken: hard instances with n = 400..1200 and very large capacities (1e6 to 1e10).
- Greedy and DP results are available for kplib and for Jooken where capacity <= 2,000,000.
- Brute force only runs on very small n (synthetic sizes) and is skipped when ETA exceeds 300s.
- Edge-case suite (synthetic): tiny n, capacity = 0, capacity < min weight, capacity = sum weights, and a known greedy-failure instance.

## Edge-case mapping (where each edge case is covered)
- Tiny n (n=1..4), capacity = 0, capacity < min weight, capacity = sum(weights), multiple optimal solutions, classic greedy failure -> EDGE_CASES in main.py (synthetic edge-case suite).
- Correlation structure (uncorrelated/weakly/strongly correlated) -> kplib subset (00/01/02 families).
- Very large capacities and large n stress -> Jooken instances (cap up to 1e10, n up to 1200).

## Coverage gaps (what we did not cover)
- Full kplib catalog: inverse/strongly correlated, subset-sum, similar weights, spanner, profit ceiling, circle, and larger sizes (500..10000).
- kplib ratios beyond R01000 (e.g., R10000).
- Full Jooken dataset (3240 folders). We used the 100-instance preliminary list to keep runtime manageable.

## Rationale for coverage limits
- Brute force is exponential and becomes infeasible beyond small n; we use it only for correctness sanity checks.
- DP is O(W) in memory/time, so very large capacities (1e8 to 1e10) are not feasible.
- We choose representative subsets (kplib 3 families and Jooken 100 instances) to balance coverage and runtime.

## Conclusion
- Summarize when DP is feasible vs when greedy is necessary.
- Discuss the impact of instance type on difficulty and approximation quality.
