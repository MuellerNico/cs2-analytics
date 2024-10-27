from demoparser2 import DemoParser
import pandas as pd
import os
import matplotlib.pyplot as plt

def get_demo_files(folder):
    files = [f for f in os.listdir(folder) if f.endswith(".dem")]
    return [os.path.join(folder, f) for f in files]

def get_utility_stats(demos):
    stats = pd.DataFrame()
    for demo in demos:
        print(f"Parsing {demo}")
        parser = DemoParser(demo)
        df = parser.parse_grenades()
        df = df.drop_duplicates(subset="entity_id") 
        df = df[["name", "grenade_type"]]
        stats = pd.concat([stats, df], ignore_index=True)
    return stats

def main():
    folder = "demos/"
    demos = get_demo_files(folder)
    stats = get_utility_stats(demos)   
    # turn grenade_type categories into their own columns and count
    stats = pd.get_dummies(stats, columns=["grenade_type"])
    stats = stats.groupby("name").sum()
    stats["molly"] = stats["grenade_type_molotov"] + stats["grenade_type_incendiary_grenade"]
    stats = stats.rename(columns={'grenade_type_he_grenade': 'HE', 'grenade_type_smoke': 'smoke', 'grenade_type_flashbang': 'flash'})
    stats = stats[["HE", "smoke", "flash", "molly"]]
    stats["total"] = stats.sum(axis=1)
    stats = stats.sort_values(by="total", ascending=False)
    print("======== Utility Usage ========")
    print(stats)

if __name__ == "__main__":
    main()
