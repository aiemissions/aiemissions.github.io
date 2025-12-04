# Libraries
import os
from diffusers import DiffusionPipeline
import threading
import torch
import requests
import pandas as pd
import time
import pynvml
from datetime import datetime

# Initialization
def initialize_emissions_dataframe():
    # Define the CSV file name
    csv_file = 'emissions.csv'
    
    # Check if the CSV file exists
    if os.path.exists(csv_file):
        # Load the CSV file into a DataFrame
        df = pd.read_csv(csv_file)
    else:
        # Create a new DataFrame with the specified columns
        df = pd.DataFrame(columns=[
            'model', 'emissions', 'carbon intensity', 'zone', 'duration', 
            'time', 'power usage', 'gpu', 'prompt', 'image file'
        ])
        # Save the empty DataFrame to a new CSV file
        df.to_csv(csv_file, index=False)
    
    return df

df = initialize_emissions_dataframe()
numbers = [int(f.split('.')[0]) for f in df['image file'].tolist()]
image_index = (max(numbers) if numbers else 0) + 1

# stage 1
stage_1 = DiffusionPipeline.from_pretrained("DeepFloyd/IF-I-XL-v1.0", variant="fp16", torch_dtype=torch.float16)

# stage 2
stage_2 = DiffusionPipeline.from_pretrained(
    "DeepFloyd/IF-II-L-v1.0", text_encoder=None, variant="fp16", torch_dtype=torch.float16
)

# stage 3
safety_modules = {"feature_extractor": stage_1.feature_extractor, "safety_checker": stage_1.safety_checker, "watermarker": stage_1.watermarker}
stage_3 = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-x4-upscaler", **safety_modules, torch_dtype=torch.float16)
stage_1.to("cuda")
stage_2.to("cuda")
stage_3.to("cuda")
generator = torch.manual_seed(0)

prompts = [
    "A mystical forest with glowing mushrooms, towering ancient trees, and a crystal-clear stream running through it. The sky is filled with vibrant auroras.",
    "A futuristic city with towering skyscrapers made of glass and metal, flying cars zooming by, and a vibrant, bustling marketplace filled with alien creatures.",
    "A bustling medieval marketplace with people in period clothing, merchants selling goods from wooden stalls, and a castle looming in the background.",
    "A colorful, swirling pattern of geometric shapes and lines, with a focus on bright blues, reds, and yellows, evoking a sense of motion and energy.",
    "A detailed, realistic portrait of a young woman with curly hair, wearing a vintage dress, sitting by a window with soft sunlight illuminating her face.",
    "A serene lakeside scene at dawn, with mist rising from the water, a family of ducks swimming by, and a fisherman in a small boat casting his line.",
    "A gritty city street with vibrant graffiti covering the walls, a breakdancer performing in the foreground, and bystanders watching and taking pictures.",
    "A majestic dragon with shimmering scales, large wings, and piercing eyes, perched on a mountain peak with a stormy sky in the background.",
    "A dream-like scene with floating islands, a giant clock melting over a tree branch, and a man in a suit with a fishbowl for a head walking on a checkerboard path.",
    "A dynamic action scene with a superhero in a colorful costume flying through the air, about to clash with a menacing villain, with bold lines and vibrant colors."
]

power_data = []
durations = []  # List to accumulate duration values

stop = False

# Actual emissions calculating
def get_gpu_power_usage(interval=1):
    pynvml.nvmlInit()
    global stop
    """
    Logs the power usage of NVIDIA GPUs every `interval` seconds for a `duration` period.
    
    Args:
    interval (int): Measurement interval in seconds.
    duration (int): Total duration to record power usage in seconds.
    """
    
    # Get number of GPUs
    device_count = pynvml.nvmlDeviceGetCount()
    
    try:
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            print(f"Monitoring GPU {i}: {pynvml.nvmlDeviceGetName(handle)}")

        start_time = time.time()
        while stop == False:
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                try:
                    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert milliwatts to watts
                    print(f"GPU {i} Power Usage: {power_usage} Watts")
                    power_data.append(power_usage)
                except pynvml.NVMLError as e:
                    print(f"Failed to get power usage for GPU {i}: {str(e)}")
            time.sleep(interval)
    finally:
        # Shutdown NVML
        pynvml.nvmlShutdown()

def generate(prompt):
    global duration
    global stop
    start = time.time()
    prompt_embeds, negative_embeds = stage_1.encode_prompt(prompt)
    image = stage_1(prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_embeds, generator=generator, output_type="pt").images
    image = stage_2(
        image=image, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_embeds, generator=generator, output_type="pt"
    ).images
    image = stage_3(prompt=prompt, image=image, generator=generator, noise_level=100).images
    images = image[0]

    end = time.time()
    duration = end - start
    images.save(f"{image_index}.png")
    stop = True

def calc_emissions(power, duration, intensity=-1):
    global df
    coords = requests.get("https://ipinfo.io/json").json()["loc"].split(",")
    response = requests.get("https://api.electricitymap.org/v3/carbon-intensity/latest?lat="+str(coords[0])+"&lon="+str(coords[1])).json()
    
    if intensity == -1:
        intensity = response["carbonIntensity"]
    
    new_row = {
        'model': "idk",
        'emissions': (power / 1000) * (duration / 3600) * intensity,
        'carbon intensity': intensity,
        'zone': response["zone"],
        'duration': duration,
        'time': datetime.now(),
        'power usage': power,
        'gpu': 'gpu_1x_a10',
        'prompt': prompt,
        'image file': f"{image_index}.png"
    }
    
    df = df.append(new_row, ignore_index=True)
    df.to_csv('emissions.csv', index=False)
    
    print("Average Power Usage: " + str(power))
    print("Duration: " + str(duration))
    print("Carbon Intensity: " + str(intensity))
    print("Zone: " + response["zone"])
    print("Time: " + str(new_row['time']))
    print("Image: " + f"{image_index}.png")
    
    return (power / 1000) * (duration / 3600) * intensity

for prompt in prompts:
    stop = False
    thread_one = threading.Thread(target=get_gpu_power_usage)
    thread_two = threading.Thread(target=generate, args=(prompt,))
    thread_one.start()
    thread_two.start()
    thread_one.join()
    thread_two.join()
    
    power_data = [i for i in power_data if i >= max(power_data) * 0.9]
    power = sum(power_data) / len(power_data)
    print(calc_emissions(power, duration))
    
    durations.append(duration)  # Add each duration to the list
    image_index += 1

# Calculate and print the average duration at the end
average_duration = sum(durations) / len(durations)
print("Average Generation Duration:", average_duration)
