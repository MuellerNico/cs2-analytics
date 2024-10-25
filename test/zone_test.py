from demoparser2 import DemoParser

filename = "demos/natus-vincere-vs-mouz-m1-inferno.dem"
parser = DemoParser(filename)
df = parser.parse_event("player_death", player=["last_place_name"])

# filter out None from steamid fields
df = df[df["attacker_steamid"].notnull()]
df = df[df["user_steamid"].notnull()]

print(df["attacker_steamid"].unique())
MY_STEAMID = int(df["attacker_steamid"].unique()[0])

df["attacker_steamid"] = df["attacker_steamid"].astype(int)
df["user_steamid"] = df["user_steamid"].astype(int)

my_kills = df[df["attacker_steamid"] == MY_STEAMID]
my_deaths = df[df["user_steamid"] == MY_STEAMID]

# Get a list of all zones
all_unique_zones = my_kills["attacker_last_place_name"].unique().tolist()
all_unique_zones.extend(my_deaths["user_last_place_name"].unique())


for zone in all_unique_zones:
    n_kills = len(my_kills[my_kills["attacker_last_place_name"] == zone])
    n_deaths = len(my_deaths[my_deaths["user_last_place_name"] == zone])

    print(f"{zone}       Kills:{n_kills},       Deaths: {n_deaths}")