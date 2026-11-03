import csv
import os
import sqlite3
import tempfile
import time

COUNTS = [2_000, 8_000, 20_000]
METHODS = ["autocommit", "transaction", "executemany"]


def rows_for(count):
    return [(index, f"event-{index}") for index in range(count)]


def insert_autocommit(connection, rows):
    connection.isolation_level = None
    for row in rows:
        connection.execute("INSERT INTO events(id, payload) VALUES (?, ?)", row)
    return len(rows)


def insert_transaction(connection, rows):
    connection.execute("BEGIN")
    for row in rows:
        connection.execute("INSERT INTO events(id, payload) VALUES (?, ?)", row)
    connection.execute("COMMIT")
    return 1


def insert_executemany(connection, rows):
    connection.execute("BEGIN")
    connection.executemany("INSERT INTO events(id, payload) VALUES (?, ?)", rows)
    connection.execute("COMMIT")
    return 1


FUNCTIONS = {
    "autocommit": insert_autocommit,
    "transaction": insert_transaction,
    "executemany": insert_executemany,
}


def run(method, count):
    path = tempfile.mktemp(prefix="sqlite-bench-", suffix=".db")
    try:
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, payload TEXT)")
        rows = rows_for(count)
        started = time.perf_counter()
        commits = FUNCTIONS[method](connection, rows)
        seconds = time.perf_counter() - started
        connection.close()
        return seconds, commits
    finally:
        if os.path.exists(path):
            os.remove(path)


def repeats_for(count):
    if count <= 2_000:
        return 3
    if count <= 8_000:
        return 2
    return 1


def main():
    rows = []
    for count in COUNTS:
        repeats = repeats_for(count)
        for method in METHODS:
            total_seconds = 0.0
            commits = 0
            for _ in range(repeats):
                seconds, commits = run(method, count)
                total_seconds += seconds
            seconds = total_seconds / repeats
            rows.append([
                method,
                count,
                repeats,
                round(seconds, 6),
                commits,
                round(count / seconds, 1),
            ])

    with open("benchmark_results.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "method", "count", "repeats", "seconds", "commits", "rows_per_second",
        ])
        writer.writerows(rows)

    print(len(rows), "measurements written")


if __name__ == "__main__":
    main()
