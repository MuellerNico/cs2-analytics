from demoparser2 import DemoParser
import pandas as pd
import os

def get_demo_files(folder):
    files = [f for f in os.listdir(folder) if f.endswith(".dem")]
    return [os.path.join(folder, f) for f in files]

def extract_features(parser, ticks):
    rounds_df = parser.parse_event("round_end", other=["round_win_status"])
    wanted_fields = ["health", "is_alive", "team_num", "current_equip_value", "team_rounds_total", 
                     "is_bomb_planted", "team_name", "total_rounds_played"]
    df = parser.parse_ticks(wanted_fields, ticks=ticks)
    teams = df["team_num"].unique()
    assert len(teams) == 2
    features = []
    for tick in ticks:
        subdf = df[df["tick"] == tick]
        subdf_t1 = subdf[subdf["team_num"] == teams[0]]
        subdf_t2 = subdf[subdf["team_num"] == teams[1]]
        tick_features = {
            "round_number" : subdf["total_rounds_played"].values[0],
            "tick" : tick,
            "rounds_won_t1" : subdf_t1["team_rounds_total"].values[0],
            "rounds_won_t2" : subdf_t2["team_rounds_total"].values[0],
            "players_alive_t1" : subdf_t1["is_alive"].sum(),
            "players_alive_t2" : subdf_t2["is_alive"].sum(),
            "average_health_t1" : subdf_t1["health"].mean(),
            "average_health_t2" : subdf_t2["health"].mean(),
            "equipment_value_t1" : subdf_t1["current_equip_value"].sum(),  
            "equipment_value_t2" : subdf_t2["current_equip_value"].sum(),
            "bomb_planted" : subdf_t1["is_bomb_planted"].values[0].astype(int)
        }
        # Get round winner from round_end event
        tick_features["winner"] = rounds_df.loc[tick_features["round_number"]]["round_win_status"] - 2
        features.append(tick_features)
    return pd.DataFrame(features)

# get equidistant sample snapshots from demo
def training_data_from_demo(demo, num_samples):
    print(f"Extracting features from {demo}...")
    parser = DemoParser(demo)
    min_tick = parser.parse_event("round_start")["tick"].min()
    max_tick = parser.parse_event("round_end")["tick"].max()
    ticks = [t for t in range(1, max_tick, max_tick // num_samples)]
    return extract_features(parser, ticks)

# collect training data from all demos in folder and write to csv
def main():
    folder = "demos/"
    samples_per_demo = 100
    all_data = pd.concat(
        training_data_from_demo(demo, samples_per_demo) 
        for demo in get_demo_files(folder)
    )
    all_data.to_csv("training_data.csv", index=False)

if __name__ == "__main__":
    main()
