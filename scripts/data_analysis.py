import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


def get_data_by_date(file_path, target_date, include_zones=None, exclude_zones=None):
    """
    Reads a JSON file and retrieves all data with timestamps on the specified date.

    :param file_path: Path to the JSON file
    :param target_date: The target date in 'YYYY-MM-DD' format (e.g., '2024-07-05')
    :param include_zones: List of zones to include in the data (optional)
    :param exclude_zones: List of zones to exclude from the data (optional)
    :return: List of entries with timestamps on the specified date
    """
    # Load the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Convert the target date to a datetime object
    target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    # Filter data for timestamps on the target date
    filtered_data = [entry for entry in data if datetime.strptime(entry['time'], '%Y-%m-%d %H:%M:%S').date() == target_date]
    
    # Filter the data based on include_zones or exclude_zones
    for entry in filtered_data:
        if include_zones:
            entry['data'] = {zone: value for zone, value in entry['data'].items() if zone in include_zones}
        elif exclude_zones:
            entry['data'] = {zone: value for zone, value in entry['data'].items() if zone not in exclude_zones}
    
    return filtered_data

def plot_carbon_intensity(data, zones_to_plot=None):
    """
    Plots the carbon intensity data for the specified zones.

    :param data: List of entries with timestamps and carbon intensity data
    :param zones_to_plot: List of zones to specifically plot
    """
    # Extract timestamps and carbon intensity data
    timestamps = [datetime.strptime(entry['time'], '%Y-%m-%d %H:%M:%S') for entry in data]
    intensity_values = {}
    
    for entry in data:
        for region, value in entry['data'].items():
            if region not in intensity_values:
                intensity_values[region] = []
            intensity_values[region].append(value)
    
    # Determine the complete and incomplete zones
    complete_zones = {region: values for region, values in intensity_values.items() if len(values) == len(timestamps)}
    incomplete_zones = {region: values for region, values in intensity_values.items() if len(values) != len(timestamps)}
    
    # Print incomplete zones
    print("Incomplete Zones:")
    for region in incomplete_zones:
        print(region)
    
    # Filter zones to plot if specified
    if zones_to_plot:
        complete_zones = {region: values for region, values in complete_zones.items() if region in zones_to_plot}
    
    # Plot the data
    plt.figure(figsize=(14, 7))
    
    for region, values in complete_zones.items():
        plt.plot(timestamps, values, label=region)
    
    plt.xlabel('Time')
    plt.ylabel('Carbon Intensity')
    plt.title('Carbon Intensity Over Time')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def analyze_standard_deviation(data):
    """
    Analyzes the standard deviation in the carbon intensity data for all complete zones.

    :param data: List of entries with timestamps and carbon intensity data
    :return: Dictionary of zones with their respective standard deviations
    """
    # Extract timestamps and carbon intensity data
    timestamps = [datetime.strptime(entry['time'], '%Y-%m-%d %H:%M:%S') for entry in data]
    intensity_values = {}
    
    for entry in data:
        for region, value in entry['data'].items():
            if region not in intensity_values:
                intensity_values[region] = []
            intensity_values[region].append(value)
    
    # Determine the complete and incomplete zones
    complete_zones = {region: values for region, values in intensity_values.items() if len(values) == len(timestamps)}
    
    # Calculate standard deviation for each complete zone
    std_devs = {region: np.std(values) for region, values in complete_zones.items()}
    
    return std_devs

def plot_standard_deviation(std_devs, threshold=0):
    """
    Plots the standard deviation in carbon intensity data for complete zones that have standard deviations above a certain threshold.

    :param std_devs: Dictionary of zones with their respective standard deviations
    :param threshold: Minimum standard deviation to include in the plot
    """
    # Filter standard deviations by threshold
    filtered_std_devs = {region: std for region, std in std_devs.items() if std > threshold}
    
    # Sort the standard deviations from high to low for filtered data
    sorted_filtered_std_devs = dict(sorted(filtered_std_devs.items(), key=lambda item: item[1], reverse=True))
    
    regions = list(sorted_filtered_std_devs.keys())
    std_values = list(sorted_filtered_std_devs.values())
    
    # Plot the data
    plt.figure(figsize=(14, 7))
    plt.bar(regions, std_values, color='skyblue')
    plt.xlabel('Zones')
    plt.ylabel('Standard Deviation')
    plt.title('Standard Deviation in Carbon Intensity Data for Complete Zones')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
    
    # Print the results in text form (ranked high to low)
    print("Standard Deviation in Carbon Intensity Data for Complete Zones (Ranked High to Low):")
    sorted_std_devs = dict(sorted(std_devs.items(), key=lambda item: item[1], reverse=True))
    for region, std in sorted_std_devs.items():
        print(f"{region}: {std}")

def calculate_below_50th_percentile_avg(data):
    """
    Calculates the average of all values below the 50th percentile for each region.

    :param data: List of entries with timestamps and carbon intensity data
    :return: Dictionary of regions with their respective averages of values below the 50th percentile
    """
    intensity_values = {}
    
    for entry in data:
        for region, value in entry['data'].items():
            if region not in intensity_values:
                intensity_values[region] = []
            intensity_values[region].append(value)
    
    below_50th_avg = {}
    
    for region, values in intensity_values.items():
        values = np.array(values)
        if np.all(values == values[0]):  # Check if all values are the same
            avg_below_median = "All values are the same"
        else:
            median_value = np.percentile(values, 50)
            below_median_values = values[values < median_value]
            avg_below_median = np.mean(below_median_values) if len(below_median_values) > 0 else "No values below median"
        below_50th_avg[region] = avg_below_median
    
    return below_50th_avg

def plot_below_50th_percentile_avg(below_50th_avg):
    """
    Plots the average of values below the 50th percentile for each region.

    :param below_50th_avg: Dictionary of regions with their respective averages of values below the 50th percentile
    """
    # Filter out regions with non-numeric averages
    numeric_below_50th_avg = {region: avg for region, avg in below_50th_avg.items() if isinstance(avg, (int, float))}
    
    # Sort the averages from high to low
    sorted_below_50th_avg = dict(sorted(numeric_below_50th_avg.items(), key=lambda item: item[1], reverse=True))
    
    regions = list(sorted_below_50th_avg.keys())
    avg_values = list(sorted_below_50th_avg.values())
    
    # Plot the data
    plt.figure(figsize=(14, 7))
    plt.bar(regions, avg_values, color='skyblue')
    plt.xlabel('Zones')
    plt.ylabel('Average Carbon Intensity')
    plt.title('Average Carbon Intensity Below 50th Percentile for Complete Zones')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
    
    # Print the results in text form (ranked high to low)
    print("Average Carbon Intensity Below 50th Percentile for Complete Zones (Ranked High to Low):")
    for region, avg in below_50th_avg.items():
        print(f"{region}: {avg}")

# Example usage
file_path = 'carbon_intensity.json'
target_date = '2024-07-05'
filtered_data = get_data_by_date(file_path, target_date, exclude_zones=["ES-CE",
            "ES-CN-FVLZ",
            "ES-CN-GC",
            "ES-CN-HI",
            "ES-CN-IG",
            "ES-CN-LP",
            "ES-CN-TE",
            "ES-IB-FO",
            "ES-IB-IZ",
            "ES-IB-MA",
            "ES-IB-ME",
            "ES-ML",
            "CY",
            "FO-MI",
            "FO",
            "FO-SI",
            "LT",
            "LV",
            "EE",
            "MK",
            "BA",
            "RS",
            "RE",
            "NI",
            "PF",
            "GP",
            "GT",
            "SI",
            "HN",
            "GF",
            "DO",
            "SK",
            "CR",
            "LU",
            "AW",
            "BO",
            "OM",
            "PE",
            "MQ",
            "PA",
            "BD",
            "MD",
            "AX",
            "GE",
            "IS",
            "XK",
            "US",
            "RU",
            "IN",
            "SE",
            "NO",
            "DK",
            "AU",
            "CA",
            "BR",
            "JP",
            "AU-TAS-KI",
            "AU-TAS-FI",
            "AU-WA-RI",
            "MX-CE",
            "MX-NE",
            "MX-NO",
            "MX-NW",
            "MX-OR",
            "MX-PN",
            "MX-BC",
            "RU-2",
            "RU-AS",
            "BR-N",
            "BR-NE",
            "KW",
            "NO-NO3",
            "NO-NO4",
            "NO-NO5",
            "SE-SE1",
            "SE-SE2",
            "SE-SE4",
            "CA-YT",
            "CA-AB",
            "CA-SK",
            "CA-NB",
            "CA-PE",
            "AU-TAS",
            "AU-NT",
            "AU-SA"])


# Specify the zones to plot
zones_to_plot = ['HK', "ID", "BH"]

# Plot the filtered data for the specified zones
plot_carbon_intensity(filtered_data)


# Analyze standard deviation for the complete zones
std_devs = analyze_standard_deviation(filtered_data)

# Plot the standard deviation
plot_standard_deviation(std_devs, threshold=50)

# Calculate the average of values below the 50th percentile for each region
below_50th_avg = calculate_below_50th_percentile_avg(get_data_by_date(file_path, target_date))

# Plot the average below 50th percentile
plot_below_50th_percentile_avg(below_50th_avg)  