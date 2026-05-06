from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import subprocess
import tempfile


@dataclass
class Instance:
    name: str
    weights: list[int]
    values: list[int]
    capacity: int
    source: str
    meta: dict


def _read_nonempty_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def parse_kplib_kp(path: Path) -> Instance:
    lines = _read_nonempty_lines(path)
    if len(lines) < 3:
        raise ValueError(f"Invalid kplib file: {path}")
    n = int(lines[0])
    capacity = int(lines[1])
    items = lines[2:2 + n]
    values: list[int] = []
    weights: list[int] = []
    for row in items:
        parts = row.split()
        if len(parts) != 2:
            raise ValueError(f"Invalid kplib row: {row}")
        p, w = int(parts[0]), int(parts[1])
        values.append(p)
        weights.append(w)
    return Instance(
        name=str(path),
        weights=weights,
        values=values,
        capacity=capacity,
        source="kplib",
        meta={"path": str(path), "n": n},
    )


def parse_test_in(path: Path) -> Instance:
    lines = _read_nonempty_lines(path)
    if len(lines) < 3:
        raise ValueError(f"Invalid test.in file: {path}")
    n = int(lines[0])
    item_lines = lines[1:1 + n]
    capacity = int(lines[1 + n])
    values: list[int] = []
    weights: list[int] = []
    for row in item_lines:
        parts = row.split()
        if len(parts) < 3:
            raise ValueError(f"Invalid test.in row: {row}")
        p, w = int(parts[1]), int(parts[2])
        values.append(p)
        weights.append(w)
    return Instance(
        name=str(path),
        weights=weights,
        values=values,
        capacity=capacity,
        source="test.in",
        meta={"path": str(path), "n": n},
    )


def parse_instance(path: Path) -> Instance:
    lines = _read_nonempty_lines(path)
    if len(lines) < 3:
        raise ValueError(f"Invalid instance file: {path}")
    first_item = lines[1].split()
    if len(first_item) == 2:
        return parse_kplib_kp(path)
    if len(first_item) >= 3:
        return parse_test_in(path)
    raise ValueError(f"Unrecognized instance format: {path}")


def load_kplib_instances(
    root: str | Path,
    categories: list[str] | None = None,
    sizes: list[int] | None = None,
    ratios: list[str] | None = None,
    seeds: list[int] | None = None,
    limit: int | None = None,
) -> list[Instance]:
    root_path = Path(root)
    if not root_path.exists():
        return []

    if categories is None:
        categories = sorted([p.name for p in root_path.iterdir() if p.is_dir()])

    instances: list[Instance] = []
    for category in categories:
        cat_path = root_path / category
        if not cat_path.is_dir():
            continue

        if sizes is None:
            size_dirs = sorted([p for p in cat_path.iterdir() if p.is_dir()])
        else:
            size_dirs = [cat_path / f"n{size:05d}" for size in sizes]

        for size_dir in size_dirs:
            if not size_dir.is_dir():
                continue
            if ratios is None:
                ratio_dirs = sorted([p for p in size_dir.iterdir() if p.is_dir()])
            else:
                ratio_dirs = [size_dir / ratio for ratio in ratios]

            for ratio_dir in ratio_dirs:
                if not ratio_dir.is_dir():
                    continue
                if seeds is None:
                    seed_files = sorted(ratio_dir.glob("s*.kp"))
                else:
                    seed_files = [ratio_dir / f"s{seed:03d}.kp" for seed in seeds]

                for seed_file in seed_files:
                    if not seed_file.is_file():
                        continue
                    inst = parse_kplib_kp(seed_file)
                    inst.name = f"kplib/{category}/{size_dir.name}/{ratio_dir.name}/{seed_file.name}"
                    inst.meta.update({"category": category, "ratio": ratio_dir.name})
                    instances.append(inst)
                    if limit is not None and len(instances) >= limit:
                        return instances
    return instances


def load_jooken_instances(
    root: str | Path,
    names_file: str | Path | None = None,
    limit: int | None = None,
) -> list[Instance]:
    root_path = Path(root)
    if not root_path.exists():
        return []

    problem_root = root_path / "problemInstances"
    if not problem_root.exists():
        return []

    instances: list[Instance] = []
    if names_file is not None:
        names_path = Path(names_file)
        names = _read_nonempty_lines(names_path)
        for name in names:
            test_path = problem_root / name / "test.in"
            if not test_path.is_file():
                continue
            inst = parse_test_in(test_path)
            inst.name = f"jooken/{name}"
            inst.source = "jooken"
            instances.append(inst)
            if limit is not None and len(instances) >= limit:
                return instances
        return instances

    for test_path in sorted(problem_root.glob("*/test.in")):
        inst = parse_test_in(test_path)
        inst.name = f"jooken/{test_path.parent.name}"
        inst.source = "jooken"
        instances.append(inst)
        if limit is not None and len(instances) >= limit:
            return instances
    return instances


def generate_jooken_instance(
    n: int,
    capacity: int,
    classes: int,
    fraction: float,
    eps: float,
    small: int,
    seed: int = 0,
) -> Instance:
    if classes < 2:
        raise ValueError("classes must be >= 2")

    rng = random.Random(seed)
    classes = classes - 1
    amount_small = int(n * fraction)
    per_class = (n - amount_small) // classes

    values: list[int] = []
    weights: list[int] = []
    denom = 2.0
    idx = 0

    for _ in range(classes):
        for _ in range(per_class):
            num1 = rng.randint(1, small)
            num2 = rng.randint(1, small)
            value = int((1.0 / denom + eps) * capacity + num1)
            weight = int((1.0 / denom + eps) * capacity + num2)
            values.append(value)
            weights.append(weight)
            idx += 1
        denom *= 2.0

    while idx < n:
        num1 = rng.randint(1, small)
        num2 = rng.randint(1, small)
        values.append(num1)
        weights.append(num2)
        idx += 1

    return Instance(
        name=f"jooken-gen/n{n}_c{capacity}_g{classes+1}_f{fraction}_eps{eps}_s{small}_seed{seed}",
        weights=weights,
        values=values,
        capacity=capacity,
        source="jooken-generator",
        meta={
            "n": n,
            "capacity": capacity,
            "classes": classes + 1,
            "fraction": fraction,
            "eps": eps,
            "small": small,
            "seed": seed,
        },
    )


def generate_pisinger_gen2(
    gen2_path: str | Path,
    n: int,
    r: int,
    instance_type: int,
    instance_idx: int,
    series: int,
) -> Instance:
    gen2_path = Path(gen2_path)
    if not gen2_path.exists():
        raise FileNotFoundError(f"gen2 not found at {gen2_path}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        cmd = [
            str(gen2_path),
            str(n),
            str(r),
            str(instance_type),
            str(instance_idx),
            str(series),
        ]
        subprocess.run(cmd, cwd=tmp_path, check=True, capture_output=True, text=True)
        test_path = tmp_path / "test.in"
        inst = parse_test_in(test_path)
        inst.name = f"pisinger-gen2/n{n}_r{r}_t{instance_type}_i{instance_idx}_S{series}"
        inst.source = "pisinger-gen2"
        inst.meta.update({"r": r, "type": instance_type, "series": series})
        return inst
