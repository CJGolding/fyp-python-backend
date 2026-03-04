import numpy as np
import random, os, csv
import matplotlib.pyplot as plt
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor
from sklearn.linear_model import HuberRegressor
from itertools import count

from backend import UnrestrictedGameManager, Player


CURRENT_ID = count()
SEEDS = (5, 10, 15, 20, 25)
COLOURS = [
    {"plot": "#1f77b4", "line": "#08306b"},
    {"plot": "#d62728", "line": "#67000d"},
    {"plot": "#2ca02c", "line": "#00441b"}
]
OUTPUT_DIR = "./output"
NUM_PLAYERS = 1000


def _run_seed(seed):
    random.seed(seed)
    gm = UnrestrictedGameManager(is_recording=False, team_size=3)

    players = [
        Player(i, abs(int(round(random.gauss(1500, 200)))))
        for i in range(NUM_PLAYERS)
    ]

    insertion_times = []
    deletion_times = []
    query_times = []

    for player in players:
        start = perf_counter()
        gm._insert_player(player)
        insertion_times.append(perf_counter() - start)

        start = perf_counter()
        gm._query_best_game()
        query_times.append(perf_counter() - start)

    for player in players:
        start = perf_counter()
        gm._remove_player(player)
        deletion_times.append(perf_counter() - start)

    return insertion_times, deletion_times, query_times


def _export_graph(data, fit_model, name, colour):
    n = len(data)
    x = np.arange(n).reshape(-1, 1)

    if fit_model == 'O(log n)':
        x_log = np.log(np.arange(n) + 1).reshape(-1, 1)
        model = HuberRegressor().fit(x_log, data)
        fit = model.predict(x_log)
    else:
        ones = np.ones((n, 1))
        model = HuberRegressor(fit_intercept=False).fit(ones, data)
        fit = model.predict(ones)

    plt.figure(figsize=(6, 4))
    plt.scatter(x, data, s=18, alpha=0.7,
                color=colour["plot"], label=f"Raw {name} Time")
    plt.plot(x, fit, linestyle="--", linewidth=2,
             color=colour["line"], label=f"{fit_model} Fit")
    plt.title(f"{name} Time vs Number of Players")
    plt.xlabel("Number of Players")
    plt.ylabel("Time (seconds)")
    plt.ylim(bottom=0)
    plt.legend()
    plt.tight_layout()
    file_name = f"{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}_{NUM_PLAYERS}"
    plt.savefig(f"{OUTPUT_DIR}/{file_name}_complexity.png", dpi=300)
    plt.close()
    print(f"Saved: {file_name}_complexity.png")
    return file_name

def _export_csv(data, file_name):
    num_players = len(data[0])
    num_seeds = len(data)

    with open(f"{OUTPUT_DIR}/{file_name}_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)

        header = ["num_players"] + [f"seed_{i}" for i in range(num_seeds)]
        writer.writerow(header)

        for player_idx in range(num_players):
            row = [player_idx + 1] + [data[seed_idx][player_idx] for seed_idx in range(num_seeds)]
            writer.writerow(row)

    print(f"Saved: {file_name}_raw.csv")


def run():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(_run_seed, SEEDS))

    raw_insertion = [r[0] for r in results]
    raw_deletion = [r[1] for r in results]
    raw_query = [r[2] for r in results]

    avg_insertion = np.mean(raw_insertion, axis=0)
    avg_deletion = np.mean(raw_deletion, axis=0)[::-1]  # reversed
    avg_query = np.mean(raw_query, axis=0)

    insert_file_name = _export_graph(avg_insertion, "O(log n)", "Insertion", COLOURS[0])
    delete_file_name = _export_graph(avg_deletion, "O(log n)", "Deletion (Reversed)", COLOURS[1])
    query_file_name = _export_graph(avg_query, "O(1)", "Query", COLOURS[2])

    _export_csv(raw_insertion, insert_file_name)
    _export_csv(raw_deletion, delete_file_name)
    _export_csv(raw_query, query_file_name)


if __name__ == "__main__":
    run()