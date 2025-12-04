import json

import matplotlib.pyplot as plt
import numpy as np  # Import numpy for calculating the mean

def plot_zones_boxplot(file_path, zones):
    # Load the JSON data from the file
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    
    # Initialize a dictionary to hold values for each zone
    zone_values = {zone: [] for zone in zones}
    
    # Extract the values for the specified zones
    for entry in json_data:
        if "07-08" in entry.get("time", ''):
            data = entry.get("data", {})
            for zone in zones:
                if zone in data:
                    zone_values[zone].append(data[zone])
    
    # Filter out zones with no data
    zone_values = {zone: values for zone, values in zone_values.items() if values}
    if not zone_values:
        print(f"No data found for the selected zones: {zones}")
        return

    colors = ['b', 'b', 'lightblue', 'magenta', 'lightyellow', 'lightgreen', 'pink', '#e42c32', 'orange', 'tan']

    # Plot the box plots for the extracted values
    plt.figure(figsize=(10, 6))
    boxplot = plt.boxplot(
        zone_values.values(),
        patch_artist=True,
        #labels=["Singapore","Japan","India","Malaysia","Philippines"]
        #labels=["California","Texas","New York","Australia","New Zealand"]
        labels=["Sweden","France","Great Britain","Germany","Italy"]
    )
    #for patch, color in zip(boxplot['boxes'], colors):
    #    patch.set_facecolor('blue')

    plt.ylabel('Carbon Intensity (gCO2eq/kWh)')
    plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.minorticks_on()
    plt.title('Carbon Intensity Values of Various Regions in Europe', loc='left')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # Calculate the overall mean across all zones
    all_values = [value for values in zone_values.values() for value in values]
    overall_mean = np.mean(all_values)
    
    # Add a horizontal line for the overall mean
    plt.axhline(overall_mean, color='red', linestyle='--', label=f'Overall Mean ({overall_mean:.2f})')
    plt.legend()
    
    plt.show()
    print(zone_values)

# Example usage:
#plot_zones_boxplot('carbon_intensity.json', ['US-CAL-CISO','US-TEX-ERCO',"US-NY-NYIS","AU","NZ"])
plot_zones_boxplot('carbon_intensity.json', ['SE',"FR","GB","DE","IT"])