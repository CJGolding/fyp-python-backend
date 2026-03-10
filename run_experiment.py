import csv
import os
import random
from concurrent.futures import ProcessPoolExecutor
from itertools import count
from time import perf_counter
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import HuberRegressor

from backend import UnrestrictedGameManager, Player

CURRENT_ID = count()
SEEDS = (5, 10, 15, 20, 25)
SIM_TYPES = ["brute_force", "approximate"]
NUM_PLAYERS = 1000

SCATTER_COLOURS = [
    {"plot": "#1f77b4", "line": "#08306b"},
    {"plot": "#d62728", "line": "#67000d"},
    {"plot": "#2ca02c", "line": "#00441b"},
]

LINE_COLOURS = [
    "#1f77b4",
    "#ff7f0e",
]


def _safe_filename(name):
    """Helper function to ensure the file name only contains alphanumeric characters."""
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_-")
    s = name.lower()
    s = s.replace(" ", "_").replace("(", "").replace(")", "")
    return "".join(ch for ch in s if ch in allowed)


def _ensure_output_dir(path):
    """Helper function to ensure the output directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def _run_seed(seed, sim_type):
    """Helper function to run the experiment for a given seed."""
    approximate = sim_type == "approximate"
    random.seed(seed)

    gm = UnrestrictedGameManager(
        is_recording=False, q_norm=2, p_norm=2, fairness_weight=1, approximate=approximate
    )

    players = [
        Player(i, abs(int(round(random.gauss(1500, 200)))))
        for i in range(NUM_PLAYERS)
    ]

    insertion_times = []
    deletion_times = []
    query_times = []
    best_games = []

    for player in players:
        start = perf_counter()
        gm._insert_player(player)
        insertion_times.append(perf_counter() - start)

        start = perf_counter()
        gm._query_best_game()
        query_times.append(perf_counter() - start)

        best_game = gm._query_best_game().imbalance if gm._query_best_game() else None
        best_games.append(best_game)

    for player in players:
        start = perf_counter()
        gm._remove_player(player)
        deletion_times.append(perf_counter() - start)

        best_game = gm._query_best_game().imbalance if gm._query_best_game() else None
        best_games.append(best_game)

    return insertion_times, deletion_times, query_times, best_games


def _export_scatter_graph(data, fit_model, name, colour, output_dir):
    """Helper function to export scatter plots, including a regressed line of best fit."""
    _ensure_output_dir(output_dir)

    n = len(data)
    x = np.arange(n).reshape(-1, 1)
    plt.figure(figsize=(6, 4))

    if fit_model == "O(log n)":
        x_log = np.log(np.arange(n) + 1).reshape(-1, 1)
        model = HuberRegressor().fit(x_log, data)
        fit = model.predict(x_log)
    else:
        ones = np.ones((n, 1))
        model = HuberRegressor(fit_intercept=False).fit(ones, data)
        fit = model.predict(ones)

    plt.scatter(x, data, s=18, alpha=0.7,
                color=colour["plot"], label=f"Raw {name} Time")
    plt.plot(x, fit, linestyle="--", linewidth=2,
             color=colour["line"], label=f"{fit_model} Fit")

    plt.title(f"{name} Time vs Number of Players")
    plt.xlabel("Number of Players")
    plt.ylabel(f"Time (Seconds)")
    plt.legend()
    plt.tight_layout()

    file_base = _safe_filename(name)
    file_path = os.path.join(output_dir, f"{file_base}_complexity.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

    print(f"Saved: {file_path}")
    return file_base


def _export_line_graph(series_list, labels, line_colours, output_dir, name="Mean Imbalance Over Time (by sim type)"):
    """Helper function to export line graphs, primarily for the imbalance of a game."""
    _ensure_output_dir(output_dir)
    plt.figure(figsize=(8, 5))

    max_len = max((len(s) for s in series_list), default=0)

    for i, series in enumerate(series_list):
        x = np.arange(len(series))
        y = np.array([np.nan if v is None else v for v in series], dtype=float)
        plt.plot(x, y, label=f"{labels[i]}", linewidth=1.8,
                 color=line_colours[i % len(line_colours)])

    all_vals = np.array([v for series in series_list for v in series if v is not None], dtype=float)
    if all_vals.size > 0:
        min_val = float(np.nanmin(all_vals))
        plt.axhline(min_val, linestyle="--", linewidth=2, color="black", label=f"Min ({min_val:.4g})")

    plt.title(name)
    plt.xlabel("Time (Steps, Log Scale)")
    if max_len > 1:
        plt.xscale("log")
    plt.ylabel("Imbalance (f)")
    plt.legend()
    plt.tight_layout()

    file_base = _safe_filename(name)
    file_path = os.path.join(output_dir, f"{file_base}.png")
    plt.savefig(file_path, dpi=300)
    plt.close()
    print(f"Saved: {file_path}")
    return file_base


def _export_csv(data, file_base, seeds, output_dir):
    """Helper function to export csv files containing the raw data that the graphs are based on."""
    _ensure_output_dir(output_dir)

    num_rows = len(data[0]) if data else 0
    num_seeds = len(data)

    csv_path = os.path.join(output_dir, f"{file_base}_raw.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)

        header = ["num_step"] + [f"seed_{s}" for s in seeds]
        writer.writerow(header)

        for row_idx in range(num_rows):
            row = [row_idx + 1]
            for seed_idx in range(num_seeds):
                col = data[seed_idx]
                val = col[row_idx] if row_idx < len(col) else ""
                row.append(val)
            writer.writerow(row)

    print(f"Saved: {csv_path}")


def _export_mean_csv(mean_series_map, file_base, output_dir):
    """Helper function to export csv files """
    _ensure_output_dir(output_dir)
    labels = list(mean_series_map.keys())
    series_list = [list(np.array(mean_series_map[k], dtype=float)) for k in labels]
    max_len = max((len(s) for s in series_list), default=0)

    csv_path = os.path.join(output_dir, f"{file_base}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["num_step"] + labels
        writer.writerow(header)

        for row_idx in range(max_len):
            row = [row_idx + 1]
            for series in series_list:
                val = series[row_idx] if row_idx < len(series) else ""
                if val is None or (isinstance(val, float) and np.isnan(val)):
                    row.append("")
                else:
                    row.append(val)
            writer.writerow(row)

    print(f"Saved: {csv_path}")


def run():
    """
    Orchestrating function to run an experiment to validate key matchmaking operations. The experiment consists of the following steps:
    1. Repeatedly insert 1000 players generated with a random normal distribution on a fixed seed, recording the time taken to insert.
    2. Query the top of the heap after each insertion, recording the best game imbalance and the time taken to query.
    3. Repeatedly remove the 1000 players in a fixed order, recording the time taken to remove.
    4. Query the top of the heap after each remove, recording the best game imbalance.
    These steps are repeated across 5 fixed seeds executed in parallel, and across both brute-force and greedy simulation types.
    To run this experiment, type `make requirements-all` followed by `make run-experiment`.
    The results of the experiment can be found in this repository under `output_approximate`, `output_brute_force` and `output_mean_imbalance`.
    """
    imbalances_mean_by_sim = {}

    for sim_type in SIM_TYPES:
        output_dir = f"output_{sim_type}"
        _ensure_output_dir(output_dir)

        sim_type_args = [sim_type] * len(SEEDS)
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(_run_seed, SEEDS, sim_type_args))

        raw_insertion = [r[0] for r in results]
        raw_deletion = [r[1] for r in results]
        raw_query = [r[2] for r in results]
        raw_imbalance = [r[3] for r in results]

        avg_insertion = np.mean(raw_insertion, axis=0)
        avg_deletion = np.mean(raw_deletion, axis=0)[::-1]
        avg_query = np.mean(raw_query, axis=0)

        raw_imbalance_arr = np.array([[np.nan if v is None else v for v in series] for series in raw_imbalance], dtype=float)
        mean_imbalance = np.nanmean(raw_imbalance_arr, axis=0) if raw_imbalance_arr.size else np.array([])

        imbalances_mean_by_sim[sim_type] = mean_imbalance

        insert_file_base = _export_scatter_graph(avg_insertion, "O(log n)", "Insertion", SCATTER_COLOURS[0], output_dir)
        delete_file_base = _export_scatter_graph(avg_deletion, "O(log n)", "Deletion (Reversed)", SCATTER_COLOURS[1], output_dir)
        query_file_base = _export_scatter_graph(avg_query, "O(1)", "Query", SCATTER_COLOURS[2], output_dir)

        _export_csv(raw_insertion, insert_file_base, SEEDS, output_dir)
        _export_csv(raw_deletion, delete_file_base, SEEDS, output_dir)
        _export_csv(raw_query, query_file_base, SEEDS, output_dir)

        _export_csv(raw_imbalance, "imbalance", SEEDS, output_dir)


    output_dir = "output_mean_imbalance"
    _ensure_output_dir(output_dir)

    series_list = [imbalances_mean_by_sim.get(sim, np.array([])) for sim in SIM_TYPES]
    colours = LINE_COLOURS

    _export_line_graph(series_list, SIM_TYPES, colours, output_dir)
    _export_mean_csv(imbalances_mean_by_sim, "raw_mean_imbalance", output_dir)


if __name__ == "__main__":
    run()