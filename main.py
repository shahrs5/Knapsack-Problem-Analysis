import argparse
from pathlib import Path
import time
from algorithms import knapsack_brute_force, knapsack_dp, knapsack_greedy
from benchmark import (
    generate_test_case, time_algorithm,
    print_theory_table, print_shared_table, print_large_table, print_summary,
    print_dataset_table,
    write_dataset_csv,
)
from datasets import (
    load_kplib_instances,
    load_jooken_instances,
    generate_jooken_instance,
    generate_pisinger_gen2,
    Instance,
)

SHARED_SIZES = [5, 8, 10, 12, 15, 18, 20]
LARGE_SIZES = [50, 100, 200, 300, 500, 750, 1000]

EDGE_CASES = [
    ("n1_cap0", [5], [10], 0, "capacity=0"),
    ("n1_exact", [5], [10], 5, "capacity equals weight"),
    ("cap_less_than_min", [5, 6, 7], [10, 11, 12], 4, "capacity < min weight"),
    ("cap_equals_sum", [5, 6, 7], [10, 11, 12], 18, "capacity = sum weights"),
    ("many_equal_items", [1, 1, 1, 1], [1, 1, 1, 1], 2, "multiple optimal solutions"),
    ("greedy_failure_classic", [10, 20, 30], [60, 100, 120], 50, "greedy suboptimal"),
]

# Edge-case coverage by dataset:
# - EDGE_CASES: tiny n, tiny capacity, exact-fit, capacity=sum(weights), greedy failure.
# - kplib: correlation families (uncorrelated/weakly/strongly) at moderate n and capacities.
# - Jooken: hard instances with large n and very large capacities (stress DP).

BF_MAX_SECONDS_DEFAULT = 9000000000000000000
DP_MAX_CAPACITY_DEFAULT = 2_000_000


def _parse_int_list(text):
    if text is None:
        return None
    items = [part.strip() for part in text.split(",") if part.strip()]
    if not items:
        return None
    return [int(part) for part in items]


def _parse_str_list(text):
    if text is None:
        return None
    items = [part.strip() for part in text.split(",") if part.strip()]
    return items or None


def _normalize_limit(limit):
    if limit is None:
        return None
    if limit <= 0:
        return None
    return limit


def _normalize_capacity_limit(limit):
    if limit is None:
        return None
    if limit <= 0:
        return None
    return limit


def _estimate_bf_seconds(n, scale_samples):
    if scale_samples:
        scale = sum(scale_samples) / len(scale_samples)
        return scale * (2.0 ** n)
    return None


def _estimate_eta_seconds(durations, remaining):
    if remaining <= 0:
        return 0.0
    if not durations:
        return None
    window = durations[-min(5, len(durations)) :]
    avg = sum(window) / len(window)
    return avg * remaining


def _format_eta(eta_seconds):
    if eta_seconds is None:
        return "n/a"
    return f"{eta_seconds:.1f}s"


def build_edge_case_instances():
    instances = []
    for name, weights, values, cap, desc in EDGE_CASES:
        instances.append(
            Instance(
                name=f"edge/{name}",
                weights=weights,
                values=values,
                capacity=cap,
                source="edge",
                meta={"desc": desc},
            )
        )
    return instances


def run_shared_benchmarks(bf_max_seconds=BF_MAX_SECONDS_DEFAULT, allow_bf=True):
    results = []
    total = len(SHARED_SIZES)
    start_time = time.time()
    bf_scale_samples = []
    durations = []
    for i, n in enumerate(SHARED_SIZES):
        if i > 0:
            remaining = total - i
            eta = _estimate_eta_seconds(durations, remaining)
            print(f"  [Shared] Starting n={n:<3} ({i+1}/{total}) | ETA: {_format_eta(eta)}")
        item_start = time.time()
        w, v, cap = generate_test_case(n)

        bf_val = None
        bf_time = None
        if allow_bf:
            estimate = _estimate_bf_seconds(n, bf_scale_samples)
            if estimate is None or estimate <= bf_max_seconds:
                bf_val, bf_time = time_algorithm(knapsack_brute_force, w, v, cap)
                bf_scale_samples.append(bf_time / (2.0 ** n))
            else:
                print(f"  [Shared] Skipping brute force at n={n} (ETA > {bf_max_seconds}s)")

        dp_val, dp_time = time_algorithm(knapsack_dp, w, v, cap)
        gr_val, gr_time = time_algorithm(knapsack_greedy, w, v, cap)

        durations.append(time.time() - item_start)
        remaining = total - (i + 1)
        eta = _estimate_eta_seconds(durations, remaining)
        print(f"  [Shared] Completed n={n:<3} ({i+1}/{total}) | ETA: {_format_eta(eta)}")

        results.append({
            'n': n,
            'capacity': cap,
            'bf_time': bf_time,
            'dp_time': dp_time,
            'gr_time': gr_time,
            'bf_val': bf_val,
            'dp_val': dp_val,
            'gr_val': gr_val,
            'gr_optimal': gr_val == dp_val,
            'gr_ratio': gr_val / dp_val if dp_val > 0 else 1.0,
        })
    return results


def run_large_benchmarks(bf_max_seconds=BF_MAX_SECONDS_DEFAULT, allow_bf=True):
    results = []
    total = len(LARGE_SIZES)
    start_time = time.time()
    durations = []
    bf_scale_samples = []
    for i, n in enumerate(LARGE_SIZES):
        if i > 0:
            remaining = total - i
            eta = _estimate_eta_seconds(durations, remaining)
            print(f"  [Large]  Starting n={n:<4} ({i+1}/{total}) | ETA: {_format_eta(eta)}")
        item_start = time.time()
        w, v, cap = generate_test_case(n)

        bf_val = None
        bf_time = None
        if allow_bf:
            estimate = _estimate_bf_seconds(n, bf_scale_samples)
            if estimate is None:
                print(f"  [Large]  Skipping brute force at n={n} (no BF calibration yet)")
            elif estimate > bf_max_seconds:
                print(f"  [Large]  Skipping brute force at n={n} (ETA > {bf_max_seconds}s)")
            else:
                bf_val, bf_time = time_algorithm(knapsack_brute_force, w, v, cap)
                bf_scale_samples.append(bf_time / (2.0 ** n))

        dp_val, dp_time = time_algorithm(knapsack_dp, w, v, cap)
        gr_val, gr_time = time_algorithm(knapsack_greedy, w, v, cap)

        durations.append(time.time() - item_start)
        remaining = total - (i + 1)
        eta = _estimate_eta_seconds(durations, remaining)
        print(f"  [Large]  Completed n={n:<4} ({i+1}/{total}) | ETA: {_format_eta(eta)}")

        results.append({
            'n': n,
            'capacity': cap,
            'bf_time': bf_time,
            'dp_time': dp_time,
            'gr_time': gr_time,
            'bf_val': bf_val,
            'dp_val': dp_val,
            'gr_val': gr_val,
            'gr_ratio': gr_val / dp_val if dp_val > 0 else 1.0,
        })
    return results


def _to_dataset_row(result, name, source_label):
    return {
        'source': source_label,
        'name': name,
        'n': result.get('n'),
        'capacity': result.get('capacity'),
        'bf_time': result.get('bf_time'),
        'dp_time': result.get('dp_time'),
        'gr_time': result.get('gr_time'),
        'bf_val': result.get('bf_val'),
        'dp_val': result.get('dp_val'),
        'gr_val': result.get('gr_val'),
        'gr_ratio': result.get('gr_ratio'),
    }


def run_dataset_benchmarks(
    instances,
    bf_max_seconds=BF_MAX_SECONDS_DEFAULT,
    allow_bf=True,
    dp_max_capacity=DP_MAX_CAPACITY_DEFAULT,
):
    if not instances:
        return []

    instances = sorted(instances, key=lambda inst: (len(inst.weights), inst.name))
    total = len(instances)
    start_time = time.time()
    bf_scale_samples = []
    durations = []
    results = []

    for i, inst in enumerate(instances):
        if i > 0:
            remaining = total - i
            eta = _estimate_eta_seconds(durations, remaining)
            print(f"  [Data] Starting {inst.name} ({i+1}/{total}) | ETA: {_format_eta(eta)}")
        item_start = time.time()
        n = len(inst.weights)
        bf_val = None
        bf_time = None
        if allow_bf:
            estimate = _estimate_bf_seconds(n, bf_scale_samples)
            if estimate is None or estimate <= bf_max_seconds:
                bf_val, bf_time = time_algorithm(knapsack_brute_force, inst.weights, inst.values, inst.capacity)
                bf_scale_samples.append(bf_time / (2.0 ** n))
            else:
                print(f"  [Data] Skipping brute force at n={n} for {inst.name} (ETA > {bf_max_seconds}s)")

        dp_val = None
        dp_time = None
        if dp_max_capacity is None or inst.capacity <= dp_max_capacity:
            dp_val, dp_time = time_algorithm(knapsack_dp, inst.weights, inst.values, inst.capacity)
        else:
            print(
                f"  [Data] Skipping DP at cap={inst.capacity} for {inst.name} "
                f"(cap > {dp_max_capacity})"
            )
        gr_val, gr_time = time_algorithm(knapsack_greedy, inst.weights, inst.values, inst.capacity)

        durations.append(time.time() - item_start)
        remaining = total - (i + 1)
        eta = _estimate_eta_seconds(durations, remaining)
        print(f"  [Data] Completed {inst.name} ({i+1}/{total}) | ETA: {_format_eta(eta)}")

        ratio = None
        if dp_val is not None and dp_val > 0:
            ratio = gr_val / dp_val

        results.append({
            'name': inst.name,
            'n': n,
            'capacity': inst.capacity,
            'bf_time': bf_time,
            'bf_val': bf_val,
            'dp_time': dp_time,
            'dp_val': dp_val,
            'gr_time': gr_time,
            'gr_val': gr_val,
            'gr_ratio': ratio,
        })

    return results


def run_edge_case_benchmarks(bf_max_seconds=BF_MAX_SECONDS_DEFAULT, allow_bf=True, dp_max_capacity=DP_MAX_CAPACITY_DEFAULT):
    instances = build_edge_case_instances()
    print("Running edge-case benchmarks (tiny n / tiny capacity)...")
    results = run_dataset_benchmarks(
        instances,
        bf_max_seconds=bf_max_seconds,
        allow_bf=allow_bf,
        dp_max_capacity=dp_max_capacity,
    )
    print_dataset_table(results, include_bruteforce=allow_bf)
    return results


def build_parser():
    parser = argparse.ArgumentParser(description="0/1 Knapsack benchmark runner")
    parser.add_argument("--source", choices=["synthetic", "kplib", "jooken", "pisinger", "all"], default="synthetic")
    parser.add_argument("--bf-max-seconds", type=float, default=BF_MAX_SECONDS_DEFAULT)
    parser.add_argument("--dp-max-capacity", type=int, default=DP_MAX_CAPACITY_DEFAULT)
    parser.add_argument("--no-bf", action="store_true")
    parser.add_argument("--output-csv", default=None)

    parser.add_argument("--kplib-root", default="kplib-master")
    parser.add_argument("--kplib-categories", default="00Uncorrelated,01WeaklyCorrelated,02StronglyCorrelated")
    parser.add_argument("--kplib-sizes", default="50,100,200")
    parser.add_argument("--kplib-ratios", default="R01000")
    parser.add_argument("--kplib-seeds", default="0,1,2")
    parser.add_argument("--kplib-limit", type=int, default=30)

    parser.add_argument("--jooken-root", default="knapsackProblemInstances")
    parser.add_argument("--jooken-names-file", default="preliminaryExperiment100Names.txt")
    parser.add_argument("--jooken-use-generator", action="store_true")
    parser.add_argument("--jooken-n", type=int, default=100)
    parser.add_argument("--jooken-capacity", type=int, default=1000)
    parser.add_argument("--jooken-classes", type=int, default=2)
    parser.add_argument("--jooken-fraction", type=float, default=0.5)
    parser.add_argument("--jooken-eps", type=float, default=0.01)
    parser.add_argument("--jooken-small", type=int, default=20)
    parser.add_argument("--jooken-seed", type=int, default=0)
    parser.add_argument("--jooken-count", type=int, default=5)

    parser.add_argument("--pisinger-bin", default="./gen2")
    parser.add_argument("--pisinger-n", type=int, default=100)
    parser.add_argument("--pisinger-r", type=int, default=1000)
    parser.add_argument("--pisinger-type", type=int, default=1)
    parser.add_argument("--pisinger-series", type=int, default=1000)
    parser.add_argument("--pisinger-count", type=int, default=5)

    return parser


def main():
    args = build_parser().parse_args()
    allow_bf = not args.no_bf
    output_csv = args.output_csv
    dp_max_capacity = _normalize_capacity_limit(args.dp_max_capacity)

    print_theory_table()

    if args.source == "synthetic":
        edge_results = run_edge_case_benchmarks(
            bf_max_seconds=args.bf_max_seconds,
            allow_bf=allow_bf,
            dp_max_capacity=dp_max_capacity,
        )
        print("Running shared benchmarks (Brute Force + DP + Greedy)...")
        shared = run_shared_benchmarks(bf_max_seconds=args.bf_max_seconds, allow_bf=allow_bf)
        print_shared_table(shared)

        print("Running large-input benchmarks...")
        large = run_large_benchmarks(bf_max_seconds=args.bf_max_seconds, allow_bf=allow_bf)
        print_large_table(large)

        print_summary(shared, large)

        if output_csv:
            synthetic_rows = []
            synthetic_rows.extend(
                _to_dataset_row(r, f"synthetic/shared_n{r['n']}", "synthetic-shared")
                for r in shared
            )
            synthetic_rows.extend(
                _to_dataset_row(r, f"synthetic/large_n{r['n']}", "synthetic-large")
                for r in large
            )
            synthetic_rows.extend(
                _to_dataset_row(r, r['name'], "synthetic-edge")
                for r in edge_results
            )
            write_dataset_csv(output_csv, synthetic_rows, append=True)
        return

    if args.source in ("kplib", "all"):
        categories = _parse_str_list(args.kplib_categories)
        sizes = _parse_int_list(args.kplib_sizes)
        ratios = _parse_str_list(args.kplib_ratios)
        seeds = _parse_int_list(args.kplib_seeds)
        limit = _normalize_limit(args.kplib_limit)
        instances = load_kplib_instances(
            args.kplib_root,
            categories=categories,
            sizes=sizes,
            ratios=ratios,
            seeds=seeds,
            limit=limit,
        )
        if not instances:
            print("No kplib instances found. Check --kplib-root or dataset paths.")
            if args.source == "kplib":
                return
        else:
            print(f"Running dataset benchmarks from kplib ({len(instances)} instances)...")
            results = run_dataset_benchmarks(
                instances,
                bf_max_seconds=args.bf_max_seconds,
                allow_bf=allow_bf,
                dp_max_capacity=dp_max_capacity,
            )
            print_dataset_table(results, include_bruteforce=allow_bf)
            if output_csv:
                write_dataset_csv(output_csv, results, source_label="kplib", append=False)
        if args.source == "kplib":
            return

    if args.source in ("jooken", "all"):
        names_path = None
        if args.jooken_names_file:
            candidate = Path(args.jooken_root) / args.jooken_names_file
            if candidate.is_file():
                names_path = candidate
        instances = []
        if not args.jooken_use_generator:
            limit = _normalize_limit(args.jooken_count)
            instances = load_jooken_instances(args.jooken_root, names_file=names_path, limit=limit)
        if not instances:
            for i in range(args.jooken_count):
                instances.append(
                    generate_jooken_instance(
                        n=args.jooken_n,
                        capacity=args.jooken_capacity,
                        classes=args.jooken_classes,
                        fraction=args.jooken_fraction,
                        eps=args.jooken_eps,
                        small=args.jooken_small,
                        seed=args.jooken_seed + i,
                    )
                )
        source_name = "Jooken dataset" if not args.jooken_use_generator else "Jooken generator"
        print(f"Running dataset benchmarks from {source_name} ({len(instances)} instances)...")
        results = run_dataset_benchmarks(
            instances,
            bf_max_seconds=args.bf_max_seconds,
            allow_bf=allow_bf,
            dp_max_capacity=dp_max_capacity,
        )
        print_dataset_table(results, include_bruteforce=allow_bf)
        if output_csv:
            append = args.source == "all"
            write_dataset_csv(output_csv, results, source_label="jooken", append=append)
        return

    if args.source == "pisinger":
        instances = []
        try:
            for i in range(args.pisinger_count):
                instances.append(
                    generate_pisinger_gen2(
                        args.pisinger_bin,
                        n=args.pisinger_n,
                        r=args.pisinger_r,
                        instance_type=args.pisinger_type,
                        instance_idx=i,
                        series=args.pisinger_series,
                    )
                )
        except FileNotFoundError as exc:
            print(str(exc))
            print("Compile gen2.c to a ./gen2 binary or pass --pisinger-bin.")
            return
        print(f"Running dataset benchmarks from Pisinger gen2 ({len(instances)} instances)...")
        results = run_dataset_benchmarks(instances, bf_max_seconds=args.bf_max_seconds, allow_bf=allow_bf)
        print_dataset_table(results, include_bruteforce=allow_bf)
        return


if __name__ == '__main__':
    main()
