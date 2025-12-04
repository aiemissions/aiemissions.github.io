import json

def process_requests(requests_file_path, carbon_file_path, output_file_path):
    """
    Reads 'requests_none.txt' and updates the last element if the second element is 'California'.
    
    :param requests_file_path: Path to the requests_none.txt file
    :param carbon_file_path:   Path to the carbon_intensity.json file
    :param output_file_path:   Path where the updated requests will be written
    """
    # 1. Load carbon_intensity.json
    with open(carbon_file_path, 'r') as f:
        carbon_data = json.load(f)
    
    # We expect `carbon_data` to be a list of records, each having a structure like:
    # {
    #     "time": "2024-07-01 10:07:04", 
    #     "data": { "US-CAL-CISO": 166, ...}
    # }
    #
    # We want to filter or index these by hour on date 09/27. 
    # In real usage, you'd parse the "time" field to identify the date and hour.
    # For demonstration, let's assume you *only* have data for 09/27, and each "time" 
    # is something like "2024-09-27 05:48:00". We'll parse out the hour.

    # Create a dict mapping hour -> carbon intensity for US-CAL-CISO
    # e.g., hour_map[5] = 166
    hour_map = {}
    for entry in carbon_data:
        # Parse the "time" string
        # Example: "time": "2024-09-27 05:48:00"
        # We'll extract the date portion and hour portion so we can match "09/27" and the hour
        time_str = entry["time"]
        
        # Split date/time. Example: "2024-09-27 05:48:00"
        date_str, time_part = time_str.split()
        # date_str might be "2024-09-27"
        # time_part might be "05:48:00"
        
        # We only care about records from "09-27" (month-day). Let's do a simple check:
        # This is an example check, you can refine it depending on how your data is structured:
        if "09-27" in date_str:
            hour_str = time_part.split(':')[0]  # "05" 
            hour_int = int(hour_str)
            
            # Save the US-CAL-CISO value using the hour as the key
            ciso_value = entry["data"].get("US-CAL-CISO")
            # Only store if we actually have that key
            if ciso_value is not None:
                # If multiple records for the same hour exist, 
                # you can decide which to pick (e.g., the first, average, last, etc.).
                # Here, we’ll just store the last encountered one.
                hour_map[hour_int] = ciso_value
    
    # 2. Read the requests_none.txt, transform lines
    transformed_lines = []
    
    with open(requests_file_path, 'r') as rf:
        for line in rf:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            # Parse the line as a Python list
            # Each line is something like: 
            # ['placeholder', 'California', 49060, 'default prompt', [416, 'US']]
            # Safest approach is to use literal_eval:
            from ast import literal_eval
            row = literal_eval(line)
            
            # If second element is 'California', do the special logic
            if row[1] == "California":
                # row[2] is the 3rd element (the integer we want to floor-divide by 3600)
                hour_val = row[2] // 3600

                # Look up hour_val in hour_map to get the carbon intensity
                ciso_intensity = hour_map.get(hour_val)
                # If found, replace last element with [value, 'US-CAL-CISO']
                if ciso_intensity is not None:
                    row[-1] = [ciso_intensity, "US-CAL-CISO"]
                # If not found, you can decide how to handle 
                # (e.g., do nothing, set a default, or log an error).
            
            # Convert back to string for writing
            transformed_lines.append(str(row))
    
    # 3. Write out transformed lines
    with open(output_file_path, 'w') as wf:
        for tline in transformed_lines:
            wf.write(tline + '\n')

if __name__ == "__main__":
    # Example usage:
    process_requests(
        requests_file_path="requests_none.txt",
        carbon_file_path="carbon_intensity.json",
        output_file_path="requests_none_updated.txt"
    )
