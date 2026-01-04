# Greener Pixels: Reducing Carbon Emissions in AI Image Generation

This repository contains all the scripts, datasets, and analysis for the research project **"Greener Pixels"**, which investigates how to reduce carbon emissions during the inference stage of AI image generation. The study evaluates the environmental impact of popular text-to-image models and explores practical strategies—such as spatial and temporal shifting—to minimize emissions without compromising image quality.

---

## Overview

AI image generation models are being used to create **over 34 million images per day**, resulting in significant carbon emissions. While most prior studies focus on emissions from training, this research focuses on the **inference stage**, which can contribute up to **90% of total emissions** over a model's lifecycle.

We analyze the energy usage of five open-source models across two GPU types (NVIDIA A100 and H100) and propose two key mitigation strategies:
- **Spatial Shifting**: Relocating computation to low-carbon regions.
- **Temporal Shifting**: Running jobs during cleaner energy hours.

---

## Related Work Summary

- **Training vs. Inference**: While model training has been widely studied, inference-related emissions are under-examined despite their larger cumulative footprint.
- **Shifting Techniques**: Existing studies suggest the promise of spatial/temporal shifting but lack real-world quantitative analysis.
- **Carbon Intensity Data**: Electricity Maps provide region- and time-specific carbon intensity data, enabling precise emission tracking.

---

## Methodology

1. **Data Collection**
   - Carbon intensity data was gathered for **228 global regions**.
   - AI model performance was benchmarked using **10 prompts across 5 models** and 2 GPU types.

2. **Energy Measurement**
   - Scripts using `pyNVML` recorded energy consumption during image generation.
   - Image quality was scored on a 1–5 rubric using standardized prompts.

3. **Spatial Shifting Simulation**
   - Simulated **34 million image requests** per day based on regional interest in generative AI.
   - Requests were routed to either (a) the lowest carbon regions globally or (b) the lowest within the same continent.

4. **Temporal Shifting Simulation**
   - Carbon intensity patterns were analyzed over 24-hour cycles.
   - Workloads were shifted to midday hours when solar energy is most available.

---

## Key Findings

### Model & Hardware Impact
- **DreamShaper** used **95% less energy** than the largest model, while maintaining excellent image quality.
- Upgrading from **A100 to H100 GPUs** reduced energy usage by **up to 18%**.

### Spatial Shifting
- **Global spatial shifting** reduced emissions by **97%**, routing tasks to low-carbon regions like Sweden.
- **Regional shifting** achieved a **39% reduction** while maintaining feasibility under data sovereignty laws.

### Temporal Shifting
- In regions like California and Texas, **shifting to midday hours** cut emissions by **up to 77%**.
- Effectiveness varied by location; New York showed minimal benefit due to a flat carbon intensity curve.
- 
---

## Recommendations

To reduce the carbon footprint of AI image generation:
1. **Use smaller, energy-efficient models** (e.g., DreamShaper).
2. **Deploy on efficient GPUs**, like the H100.
3. **Place servers in low-carbon regions**, such as Sweden or France.
4. **Schedule workloads during clean energy hours**, especially in solar-rich regions like California.
