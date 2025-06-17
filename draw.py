import json
import random
import pandas as pd
from datetime import datetime
from pathlib import Path
import re

# === Define input paths ===
startlist_dir = Path("start_list")  # Folder containing startlists (JSON files)
prediction_file = Path("pronostiek.csv")  # File containing player predictions
output_dir = Path("draws") # Directory to save output
output_dir.mkdir(parents=True, exist_ok=True)  

# === Step 1: Find the most recent startlist file ===
def extract_datetime_from_filename(path): # based on the following file name structure: 'startlist_2025-06-14_16-45.json'
    match = re.search(r"startlist_(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})\.json", path.name)
    if match:
        date_str = match.group(1)
        time_str = f"{match.group(2)}:{match.group(3)}"
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return datetime.min

startlist_files = list(startlist_dir.glob("startlist_*.json"))
if not startlist_files:
    raise FileNotFoundError("No startlist files found in 'start_list/' folder.")

latest_startlist_path = max(startlist_files, key=extract_datetime_from_filename)
startlist_filename = latest_startlist_path.name

# === Step 2: Load and filter startlist ===
with open(latest_startlist_path, "r") as f:
    startlist_data = json.load(f)

startlist_date = datetime.strptime(startlist_data["timestamp"], "%Y-%m-%dT%H:%M:%S.%f").date().isoformat()
active_riders = [
    {"name": r["name"], "team": r["team"]}
    for r in startlist_data["riders"]
    if r["status"] == "ACTIVE"
]

# === Step 3: Filter active riders ===
active_riders = [
    {"number": rider["number"],"name": rider["name"], "team": rider["team"]}
    for rider in startlist_data["riders"]
    if rider["status"] == "ACTIVE"
]

# === Step 3: Load player list ===
df = pd.read_csv(prediction_file)
players = [name.strip() for name in df['Naam:'].dropna().unique()]

# === Step 4: Random draw ===
if len(active_riders) < len(players) * 3:
    raise ValueError("Not enough riders for 3 per player.")

random.shuffle(active_riders)
assignments = [
    {
        "player": player,
        "riders": active_riders[i*3:(i+1)*3]
    }
    for i, player in enumerate(players)
]

# === Step 5: Generate output ===
draw_timestamp = datetime.now().isoformat(timespec="seconds")
output = {
    "draw_timestamp": draw_timestamp,
    "startlist_filename": startlist_filename,
    "startlist_date": startlist_date,
    "race": startlist_data.get("race"),
    "assignments": assignments
}

# === Step 6: Save ===
output_filename = f"draw_{draw_timestamp.replace(':', '-').replace('T', '_')}.json"
with open(output_dir / output_filename, "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Draw complete: {output_filename}")
