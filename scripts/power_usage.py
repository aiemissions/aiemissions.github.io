from diffusers import DiffusionPipeline
import threading
import torch
pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe.to("cuda")

# if using torch < 2.0
# pipe.enable_xformers_memory_efficient_attention()

prompt = "An astronaut riding a green horse"

import time
import pynvml

pynvml.nvmlInit()

def get_gpu_power_usage(interval=1, duration=60):
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
        while time.time() - start_time < duration:
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                try:
                    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert milliwatts to watts
                    print(f"GPU {i} Power Usage: {power_usage} Watts")
                except pynvml.NVMLError as e:
                    print(f"Failed to get power usage for GPU {i}: {str(e)}")
            time.sleep(interval)
    finally:
        # Shutdown NVML
        pynvml.nvmlShutdown()

def generate():
    start = time.time()
    images = pipe(prompt=prompt).images[0]
    end = time.time()
    print(end-start)
    images.save("image.png")

thread_one = threading.Thread(target=get_gpu_power_usage)
thread_two = threading.Thread(target=generate)
thread_one.start()
thread_two.start()