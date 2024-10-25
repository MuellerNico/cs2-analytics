from demoparser2 import DemoParser
import pandas as pd

filename = "demos/natus-vincere-vs-mouz-m1-inferno.dem"

parser = DemoParser(filename)
tickrate = 64

header = parser.parse_header()
print("Map:", header["map_name"])

# determine teams
df = parser.parse_event("game_end", other=["team_name", "team_clan_name"])

#print(parser.parse_grenades())
#print(parser.parse_player_info())
#for e in parser.list_game_events():
#    print(e) 

round_start = parser.parse_event("round_start")
freeze_end = parser.parse_event("round_freeze_end", other=["game_time"])
round_end = parser.parse_event("round_end", other=["game_time"])
warmup_end = parser.parse_event("warmup_end") # useless (empty)

freeze_time_len = (freeze_end["tick"] - round_start["tick"]) / tickrate
round_time_len = (round_end["tick"] - freeze_end["tick"]) / tickrate
average_round_time = round_time_len.mean()
print("Average round time: {:.2f} seconds".format(average_round_time))
print("Freeze time length: {:.2f} seconds".format(freeze_time_len.median()))
# freezetimes longer than mean are timeouts
timeouts = freeze_time_len[freeze_time_len > freeze_time_len.median()]
print("Number of timeouts:", len(timeouts) - 1) # half time is not a timeout
 
#df = parser.parse_event("round_end", other=["team_rounds_total", "team_score_first_half", "team_score_second_half"])
# last round 
#df = df.iloc[-1]
# print(df)
# rounds_T = df[df["winner"] == "T"]
# rounds_CT = df[df["winner"] == "CT"]
# print(df["ct_team_rounds_total"])
# print(df["t_team_rounds_total"])

max_tick = parser.parse_event("round_end")["tick"].max()
print("max tick:", max_tick)
wanted_fields = ["kills_total", "deaths_total"]
df = parser.parse_ticks(wanted_fields, ticks=[max_tick])
df = df[["name", "kills_total", "deaths_total"]]
df["kd"] = df["kills_total"] / df["deaths_total"]
df = df.sort_values(by="kills_total", ascending=False)
print("======== Scoreboard ========")
print(df)

# last tick info
wanted_fields = ["game_time"]
df = parser.parse_ticks(wanted_fields, ticks=[max_tick])
game_end_time = df["game_time"].values[0]
# first tick info
df = parser.parse_ticks(wanted_fields, ticks=[1])
game_start_time = df["game_time"].values[0]
game_duration = game_end_time - game_start_time
print("Game duration: {:.2f} minutes".format(game_duration / 60))

# death time
#df = parser.parse_event("player_death", other=["game_time", "round_start_time"])
#df["player_died_time"] = df["game_time"] - df["round_start_time"]
#print(df.loc[:, ["attacker_name", "player_died_time"]])


