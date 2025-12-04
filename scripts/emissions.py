import requests
def calc_emissions(power, time, intensity=-1):
    if intensity==-1:
        intensity = requests.get("https://api.electricitymap.org/v3/carbon-intensity/latest?zone=US-CAL-CISO").json()["carbonIntensity"]
    return (power/1000)*(time/3600)*intensity

print(calc_emissions(150, 16.67656))