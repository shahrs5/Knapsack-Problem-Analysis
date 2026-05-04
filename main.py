from algorithms import knapsack_brute_force, knapsack_dp, knapsack_greedy
from benchmark import (
    generate_test_case, time_algorithm,
    print_theory_table, print_shared_table, print_large_table, print_summary,
)

SHARED_SIZES = [5, 8, 10, 12, 15, 18, 20]
LARGE_SIZES  = [50, 100, 200, 300, 500, 750, 1000]


def run_shared_benchmarks():
    results = []
    for n in SHARED_SIZES:
        w, v, cap = generate_test_case(n)
        bf_val, bf_time = time_algorithm(knapsack_brute_force, w, v, cap)
        dp_val, dp_time = time_algorithm(knapsack_dp, w, v, cap)
        gr_val, gr_time = time_algorithm(knapsack_greedy, w, v, cap)
        results.append({
            'n':         n,
            'bf_time':   bf_time,
            'dp_time':   dp_time,
            'gr_time':   gr_time,
            'bf_val':    bf_val,
            'dp_val':    dp_val,
            'gr_val':    gr_val,
            'gr_optimal': gr_val == dp_val,
            'gr_ratio':  gr_val / dp_val if dp_val > 0 else 1.0,
        })
    return results


def run_large_benchmarks():
    results = []
    for n in LARGE_SIZES:
        w, v, cap = generate_test_case(n)
        dp_val, dp_time = time_algorithm(knapsack_dp, w, v, cap)
        gr_val, gr_time = time_algorithm(knapsack_greedy, w, v, cap)
        results.append({
            'n':       n,
            'dp_time': dp_time,
            'gr_time': gr_time,
            'dp_val':  dp_val,
            'gr_val':  gr_val,
            'gr_ratio': gr_val / dp_val if dp_val > 0 else 1.0,
        })
    return results


if __name__ == '__main__':
    print_theory_table()

    print("Running shared benchmarks (Brute Force + DP + Greedy)...")
    shared = run_shared_benchmarks()
    print_shared_table(shared)

    print("Running large-input benchmarks (DP + Greedy)...")
    large = run_large_benchmarks()
    print_large_table(large)

    print_summary(shared, large)
