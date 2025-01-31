from demoparser2 import DemoParser
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

def get_round_durations_dict(parser):
    round_start = parser.parse_event("round_freeze_end", other=["total_rounds_played", "game_time"])
    round_end = parser.parse_event("round_end", other=["game_time"])
    round_duration = round_end["game_time"] - round_start["game_time"]
    return round_duration.to_dict() # zero indexed rounds

def get_demo_files(folder):
    files = [f for f in os.listdir(folder) if f.endswith(".dem")]
    return [os.path.join(folder, f) for f in files]

# confusing: round_start_time property is equivalent to the game_time of the 
# round_freeze_end event and not the game_time of the round_start event
# calculate kill time as the percentage of the round duration
def get_kill_time_stats(demos):
    stats = pd.DataFrame()
    for demo in demos:
        print(f"Parsing {demo}")
        parser = DemoParser(demo)
        fields = ["game_time", "round_start_time", "total_rounds_played"]
        df = parser.parse_event("player_death", other=fields, player=["team_name"])
        #print(df.columns)
        #print(df[["user_team_name", "attacker_team_name"]])
        round_durations = get_round_durations_dict(parser)
        df["round_duration"] = df["total_rounds_played"].map(round_durations)
        df["kill_time"] = (df["game_time"] - df["round_start_time"]) / df["round_duration"]
        df = df[["attacker_name", "kill_time", "attacker_team_name"]]
        df = df[df["kill_time"] <= 1]
        stats = pd.concat([stats, df], ignore_index=True)
    return stats

def main():
    folder = "demos/"
    demos = get_demo_files(folder)
    stats = get_kill_time_stats(demos)
    
    df = stats.copy()
    plt.figure(figsize=(10, 6))
    for player in df['attacker_name'].unique():
        sns.kdeplot(data=df[df['attacker_name'] == player], x='kill_time', label=player, fill=True, common_norm=False, alpha=0.4)
    plt.title("Density Plot of Kill Time by Player (how late in the round)")
    plt.xlabel("Time")
    plt.ylabel("Density")
    plt.legend(title="Attacker", loc="upper right")
    plt.show()

    # Bee Swarm Plot for goal times by player
    plt.figure(figsize=(10, 6))
    sns.swarmplot(data=df, x='kill_time', y='attacker_name', size=4)
    #sns.violinplot(data=df, x='kill_time', y='attacker_name', inner=None, color='lightgray')
    plt.title("Bee swarm plot of Kill Time by Player (how late in the round)")
    plt.xlabel("Time (normalized to round duration)")
    plt.ylabel("Attacker")
    plt.show()

    # average kill time for each player depending on side (T/CT)
    stats = stats.groupby(["attacker_name", "attacker_team_name"]).median()
    stats = stats.unstack()
    stats["diff"] = stats["kill_time"]["CT"] - stats["kill_time"]["TERRORIST"]
    # sort by diff
    stats = stats.sort_values(by="diff", ascending=False)
    print(stats)

if __name__ == "__main__":
    main()
