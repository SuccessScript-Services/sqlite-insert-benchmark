import csv
import matplotlib.pyplot as plt

COLORS = {"autocommit": "C0", "transaction": "C1", "executemany": "C2"}


def load(path="benchmark_results.csv"):
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key in ("count", "repeats", "seconds", "commits", "rows_per_second"):
            row[key] = float(row[key])
    return rows


def draw(axis, rows, ykey):
    for method in ("autocommit", "transaction", "executemany"):
        chosen = sorted((row for row in rows if row["method"] == method), key=lambda row: row["count"])
        axis.plot(
            [row["count"] for row in chosen],
            [row[ykey] for row in chosen],
            marker="o",
            color=COLORS[method],
            label=method,
        )
    axis.set_yscale("log")
    axis.set_xlabel("rows inserted")
    axis.legend()


def save(figure, path):
    figure.tight_layout()
    figure.savefig(path, dpi=140)
    plt.close(figure)
    print("saved", path)


def main():
    rows = load()
    figure, axis = plt.subplots(figsize=(8, 4.5))
    draw(axis, rows, "seconds")
    axis.set_ylabel("seconds (log scale)")
    axis.set_title("SQLite insert time by write strategy")
    save(figure, "insert_time.png")

    figure, axis = plt.subplots(figsize=(8, 4.5))
    draw(axis, rows, "commits")
    axis.set_ylabel("commit units (log scale)")
    axis.set_title("How many commit boundaries each strategy uses")
    save(figure, "commit_count.png")

    figure, axis = plt.subplots(figsize=(8, 4.5))
    draw(axis, rows, "rows_per_second")
    axis.set_ylabel("rows per second (log scale)")
    axis.set_title("Insert throughput as the table grows")
    save(figure, "throughput.png")


if __name__ == "__main__":
    main()
