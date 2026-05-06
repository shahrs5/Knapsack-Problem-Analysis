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

2) kplib (standard benchmarks)
   - Folder: kplib-master/
   - Format: .kp files with n, capacity, then profit weight pairs.
   - Use categories like 00Uncorrelated, 01WeaklyCorrelated, 02StronglyCorrelated.

3) Jooken hard instances (2022 EJOR)
   - Folder: knapsackProblemInstances/
   - If problemInstances/ is missing, use generator parameters.
   - Generator parameters: n, capacity, classes, fraction, eps, small.

4) Pisinger gen2 (Martello, Pisinger, Toth)
   - File: gen2.c, requires compiling a gen2 binary.
   - Supports multiple instance types (uncorrelated, weakly/strongly correlated, subset sum, etc.).

## Experiment details
- Measure time using min of multiple repeats to reduce noise.
- Use identical instances across algorithms for fair comparison.
- Use small n for brute force. Skip brute force when estimated time > 300 seconds.

## Empirical results
- Compare runtime scaling and solution quality (greedy ratio vs DP).
- Report per-instance tables and summary statistics (avg ratio, min/max).

## Conclusion
- Summarize when DP is feasible vs when greedy is necessary.
- Discuss the impact of instance type on difficulty and approximation quality.
