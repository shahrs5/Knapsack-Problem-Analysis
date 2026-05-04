"""
0/1 Knapsack — Three Algorithm Implementations

Design Techniques:
  Brute Force : Exhaustive recursion — O(2^n) time, O(n) space
  Dynamic Prog: Bottom-up DP tabulation — O(n*W) time, O(W) space
  Greedy      : Value/weight ratio sort — O(n log n) time, O(n) space
"""


def knapsack_brute_force(weights, values, capacity, n=None):
    """
    Exhaustive recursive search. No memoization — pure 2^n behaviour.
    Optimal: YES
    """
    if n is None:
        n = len(weights)
    if n == 0 or capacity == 0:
        return 0
    if weights[n - 1] > capacity:
        return knapsack_brute_force(weights, values, capacity, n - 1)
    exclude = knapsack_brute_force(weights, values, capacity, n - 1)
    include = values[n - 1] + knapsack_brute_force(
        weights, values, capacity - weights[n - 1], n - 1
    )
    return max(exclude, include)


def knapsack_dp(weights, values, capacity):
    """
    Bottom-up DP with space-optimized rolling array.
    Backwards traversal prevents an item from being counted twice.
    Optimal: YES
    """
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], values[i] + dp[w - weights[i]])
    return dp[capacity]


def knapsack_greedy(weights, values, capacity):
    """
    Greedy by value/weight ratio. Takes items in 0/1 fashion (no fractions).
    Optimal for fractional knapsack; approximation only for 0/1.
    Optimal: NO (approximation)
    """
    order = sorted(range(len(weights)),
                   key=lambda i: values[i] / weights[i],
                   reverse=True)
    total, remaining = 0, capacity
    for i in order:
        if weights[i] <= remaining:
            total += values[i]
            remaining -= weights[i]
    return total
