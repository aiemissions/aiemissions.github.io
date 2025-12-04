import json
from datetime import datetime
from collections import defaultdict

with open('carbon_intensity.json') as f:
    records = json.load(f)

# Create a dictionary to store running totals and counts
hourly_stats = defaultdict(lambda: defaultdict(lambda: {"sum": 0, "count": 0}))

for rec in records:
    # Parse the timestamp and extract the hour (as a zero-padded string)
    dt = datetime.strptime(rec["time"], "%Y-%m-%d %H:%M:%S")
    hour = dt.strftime("%H")
    for zone, value in rec["data"].items():
        hourly_stats[hour][zone]["sum"] += value
        hourly_stats[hour][zone]["count"] += 1

# Compute averages
averages = {}
for hour, zones in hourly_stats.items():
    averages[hour] = {}
    for zone, stats in zones.items():
        averages[hour][zone] = stats["sum"] / stats["count"]

# Write to a new JSON file
with open('hourly_average.json', 'w') as out:
    json.dump(averages, out, indent=4)
