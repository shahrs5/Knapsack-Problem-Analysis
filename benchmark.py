import csv
from pathlib import Path
import random
import time


def generate_test_case(n, weight_range=(1, 50), value_range=(1, 100),
                       capacity_ratio=0.4, seed=42):
    """
    Deterministic test case. Fixed seed guarantees identical input across algorithms.
    capacity = 40% of total weight — creates a genuinely constrained problem.
    """
    random.seed(seed)
    weights = [random.randint(*weight_range) for _ in range(n)]
    values  = [random.randint(*value_range)  for _ in range(n)]
    capacity = max(1, int(capacity_ratio * sum(weights)))
    return weights, values, capacity


def time_algorithm(func, *args, repeats=3):
    """
    Runs func(*args) `repeats` times. Returns (result, min_elapsed_seconds).
    Minimum filters out OS scheduling noise better than the mean.
    """
    best = float('inf')
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = func(*args)
        best = min(best, time.perf_counter() - start)
    return result, best


def _fmt_time(seconds):
    if seconds < 1e-6:
        return f"{seconds*1e9:>8.2f} ns"
    if seconds < 1e-3:
        return f"{seconds*1e6:>8.2f} us"
    if seconds < 1.0:
        return f"{seconds*1e3:>8.2f} ms"
    return f"{seconds:>8.4f}  s"


def _fmt_optional_time(seconds):
    if seconds is None:
        return f"{'-':>8}"
    return _fmt_time(seconds)


def _fmt_optional_value(value, width):
    if value is None:
        return f"{'-':>{width}}"
    return f"{value:>{width}}"


def print_theory_table():
    sep = "=" * 74
    print(f"\n{sep}")
    print("  0/1 KNAPSACK ALGORITHM COMPARISON")
    print(sep)
    print("\nTHEORETICAL COMPLEXITY")
    print("-" * 74)
    header = f"{'Algorithm':<18} {'Design Technique':<22} {'Time':>10} {'Space':>8} {'Optimal?':>10}"
    print(header)
    print("-" * 74)
    rows = [
        ("Brute Force",    "Exhaustive Recursion", "O(2^n)",    "O(n)", "YES"),
        ("Dynamic Prog.",  "Bottom-up DP",          "O(n·W)",   "O(W)", "YES"),
        ("Greedy Approx.", "Ratio Sort + Greedy",   "O(n log n)","O(n)", "NO (approx.)"),
    ]
    for name, tech, time_, space, opt in rows:
        print(f"{name:<18} {tech:<22} {time_:>10} {space:>8} {opt:>10}")
    print("-" * 74)
    print("  * W = capacity; DP is pseudo-polynomial (depends on W, not just n)")
    print()


def print_shared_table(results):
    print("\nBENCHMARK — SHARED SIZES  (all 3 algorithms, identical inputs)")
    print("-" * 90)
    print(f"{'n':>4}  {'BF Time':>12}  {'DP Time':>12}  {'Greedy Time':>12}  "
          f"{'BF Val':>7}  {'DP Val':>7}  {'Greedy Val':>10}  {'Optimal?'}")
    print("-" * 90)
    for r in results:
        ratio_str = f"YES" if r['gr_optimal'] else f"NO  ({r['gr_ratio']:.1%})"
        print(f"{r['n']:>4}  {_fmt_optional_time(r['bf_time']):>12}  {_fmt_time(r['dp_time']):>12}  "
          f"{_fmt_time(r['gr_time']):>12}  {_fmt_optional_value(r['bf_val'], 7)}  {r['dp_val']:>7}  "
          f"{r['gr_val']:>10}  {ratio_str}")
    print()


def print_large_table(results):
    print("BENCHMARK — LARGE SIZES  (DP and Greedy only)")
    print("-" * 65)
    print(f"{'n':>5}  {'DP Time':>12}  {'Greedy Time':>12}  {'DP Val':>8}  "
          f"{'Greedy Val':>10}  {'Approx Ratio':>12}")
    print("-" * 65)
    for r in results:
        print(f"{r['n']:>5}  {_fmt_time(r['dp_time']):>12}  {_fmt_time(r['gr_time']):>12}  "
              f"{r['dp_val']:>8}  {r['gr_val']:>10}  {r['gr_ratio']:>11.1%}")
    print()


def print_summary(shared, large):
    all_results = shared + large

    # Brute force doubling ratio (from shared results)
    print("ANALYSIS SUMMARY")
    print("-" * 60)

    bf_times = [(r['n'], r['bf_time']) for r in shared if r['bf_time'] is not None and r['bf_time'] > 0]
    if len(bf_times) >= 2:
        ratios = []
        for i in range(1, len(bf_times)):
            n1, t1 = bf_times[i - 1]
            n2, t2 = bf_times[i]
            if t1 > 0:
                ratios.append(t2 / t1)
        avg_ratio = sum(ratios) / len(ratios) if ratios else 0
        print(f"  Brute force avg time ratio between consecutive n: {avg_ratio:.2f}x")
        print(f"  (Expected ~2x per +1 item for pure exponential growth)")

    dp_small  = next((r['dp_time'] for r in shared if r['n'] == shared[0]['n']),  None)
    dp_large  = next((r['dp_time'] for r in large  if r['n'] == large[-1]['n']),  None)
    gr_small  = next((r['gr_time'] for r in shared if r['n'] == shared[0]['n']),  None)
    gr_large  = next((r['gr_time'] for r in large  if r['n'] == large[-1]['n']),  None)

    if dp_large and dp_small:
        print(f"  DP time grew {dp_large/dp_small:.1f}x from n={shared[0]['n']} to n={large[-1]['n']}")
    if gr_large and gr_small:
        print(f"  Greedy time grew {gr_large/gr_small:.1f}x over same range (near-linear)")

    non_optimal = [r for r in shared if not r['gr_optimal']]
    if non_optimal:
        ratios = [r['gr_ratio'] for r in non_optimal]
        print(f"  Greedy missed optimal {len(non_optimal)}/{len(shared)} shared cases; "
              f"avg approx ratio {sum(ratios)/len(ratios):.1%}")

    large_ratios = [r['gr_ratio'] for r in large]
    if large_ratios:
        print(f"  Greedy approx ratio on large inputs: "
              f"min {min(large_ratios):.1%}, max {max(large_ratios):.1%}")

    print()
    print("  Recommendation:")
    print("    Use DP when optimality is required and capacity W is bounded.")
    print("    Use Greedy when speed matters and near-optimal is acceptable.")
    print("    Brute Force is only feasible for n <= ~20.")
    print()


def print_dataset_table(results, include_bruteforce=True):
    print("\nBENCHMARK — DATASET INSTANCES")
    print("-" * 110)
    if include_bruteforce:
        header = (
            f"{'Instance':<36}  {'n':>5}  {'Cap':>8}  {'BF Time':>12}  "
            f"{'DP Time':>12}  {'Greedy Time':>12}  {'Greedy Ratio':>13}"
        )
    else:
        header = (
            f"{'Instance':<36}  {'n':>5}  {'Cap':>8}  {'DP Time':>12}  "
            f"{'Greedy Time':>12}  {'Greedy Ratio':>13}"
        )
    print(header)
    print("-" * 110)
    for r in results:
        name = r['name']
        if len(name) > 36:
            name = "..." + name[-33:]
        ratio = r['gr_ratio']
        ratio_str = f"{ratio:>12.1%}" if ratio is not None else f"{'-':>12}"
        if include_bruteforce:
            print(
                f"{name:<36}  {r['n']:>5}  {r['capacity']:>8}  "
                f"{_fmt_optional_time(r['bf_time']):>12}  {_fmt_optional_time(r['dp_time']):>12}  "
                f"{_fmt_optional_time(r['gr_time']):>12}  {ratio_str}"
            )
        else:
            print(
                f"{name:<36}  {r['n']:>5}  {r['capacity']:>8}  "
                f"{_fmt_optional_time(r['dp_time']):>12}  {_fmt_optional_time(r['gr_time']):>12}  {ratio_str}"
            )
    print()


def _csv_value(value):
    if value is None:
        return ""
    return value


def write_dataset_csv(path, results, source_label=None, append=False):
    if not results:
        return

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or not append

    fieldnames = [
        "source",
        "name",
        "n",
        "capacity",
        "bf_time",
        "dp_time",
        "gr_time",
        "bf_val",
        "dp_val",
        "gr_val",
        "gr_ratio",
    ]

    mode = "a" if append else "w"
    with path.open(mode, newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for row in results:
            writer.writerow({
                "source": source_label or row.get("source", ""),
                "name": row.get("name", ""),
                "n": row.get("n", ""),
                "capacity": row.get("capacity", ""),
                "bf_time": _csv_value(row.get("bf_time")),
                "dp_time": _csv_value(row.get("dp_time")),
                "gr_time": _csv_value(row.get("gr_time")),
                "bf_val": _csv_value(row.get("bf_val")),
                "dp_val": _csv_value(row.get("dp_val")),
                "gr_val": _csv_value(row.get("gr_val")),
                "gr_ratio": _csv_value(row.get("gr_ratio")),
            })
