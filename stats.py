from demoparser2 import DemoParser
import pandas as pd
import os
import matplotlib.pyplot as plt

def get_demo_files(folder):
    files = [f for f in os.listdir(folder) if f.endswith(".dem")]
    return [os.path.join(folder, f) for f in files]

def get_player_stats(demos):
    stats = pd.DataFrame()
    for demo in demos:
        print(f"Parsing {demo}")
        parser = DemoParser(demo)
        max_tick = parser.parse_event("round_end")["tick"].max()
        df = parser.parse_ticks(["kills_total", "deaths_total"], ticks=[max_tick])
        df = df[["name", "kills_total", "deaths_total"]]
        stats = pd.concat([stats, df], ignore_index=True)
    return stats

def calculate_kd(stats):
    stats = stats.groupby("name").sum()
    stats["kd"] = stats["kills_total"] / stats["deaths_total"]
    return stats.sort_values(by="kills_total", ascending=False)

def main():
    folder = "demos/"
    demos = get_demo_files(folder)
    stats = get_player_stats(demos)
    stats = calculate_kd(stats)
    print("======== Scoreboard ========")
    print(stats)

if __name__ == "__main__":
    main()
