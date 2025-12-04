import requests
# import schedule
import time
from datetime import datetime
import json
import os

start = -1

def get_zone_ids():
    url = 'https://api.electricitymap.org/v3/zones'
    response = requests.get(url)
    data = response.json()
    return list(data.keys())

def get_carbon_intensity(zone_id):
    url = f'https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone_id}'
    response = requests.get(url, headers={
        "auth-token": f"your-api-key"
    })
    data = response.json()
    return data.get('carbonIntensity', None)

def get_zone_carbon_intensity_dict():
    zone_ids = get_zone_ids()
    carbon_intensity_dict = {}
    
    for zone_id in zone_ids:
        carbon_intensity = get_carbon_intensity(zone_id)
        if carbon_intensity is not None:
            carbon_intensity_dict[zone_id] = carbon_intensity
    
    return carbon_intensity_dict

def job():
    # Load existing data
    if os.path.exists('carbon_intensity.json'):
        with open('carbon_intensity.json', 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Get new data
    carbon_intensity_dict = get_zone_carbon_intensity_dict()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {"time": current_time, "data": carbon_intensity_dict}

    # Append new data to existing data
    existing_data.append(new_entry)

    # Save updated data back to the file
    with open('carbon_intensity.json', 'w') as f:
        json.dump(existing_data, f, indent=4)

    print(f"Time: {current_time}")
    print(carbon_intensity_dict)

'''
# Schedule the job every hour
schedule.every().hour.do(job)
'''

# Run the scheduler
while True:
    if datetime.now().hour != start:
        start = datetime.now().hour
        job()
    time.sleep(1800)