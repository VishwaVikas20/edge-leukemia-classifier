import joblib
import json
import time
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

print("--- SBC Edge Diagnostic Engine Initializing ---")
print("Loading clinical pipeline from local flash storage...")
start_load = time.time()

# 1. Load the exported pipeline artifacts
model = joblib.load('leukemia_master_model.joblib')
scaler = joblib.load('leukemia_scaler.joblib')
mask = joblib.load('leukemia_gene_mask.joblib')

print(f"Pipeline loaded in {time.time() - start_load:.2f} seconds.")

# 2. Hardware Trigger Wait
input("\n[ SYSTEM READY ] Press ENTER to simulate inserting biochip cartridge...")

print("\nCartridge detected. Scanning 54,630 micro-channels via SPI bus...")
time.sleep(1.5) # Simulating physical hardware read time

# 3. Read the mock sensor buffer
with open("sensor_buffer.json", "r") as f:
    data = json.load(f)
    raw_patient_data = np.array(data["sensor_readings"]).reshape(1, -1)

print("Scan complete. Executing On-Device Inference...")
start_inference = time.time()


# 4. The Edge Inference Execution
scaled_data = scaler.transform(raw_patient_data)

# Pass the full array directly. The model's 0.0 weights will naturally filter it!
probabilities = model.predict_proba(scaled_data)[0]
predicted_class = model.predict(scaled_data)[0]

inference_time = (time.time() - start_inference) * 1000

# 5. Output
class_names = ['Healthy', 'ALL', 'AML', 'CLL', 'CML']

print(f"\n--- DIAGNOSTIC RESULTS ---")
print(f"Edge Device Diagnosis : {class_names[predicted_class]}")

print("\nConfidence Scores:")
for name, prob in zip(class_names, probabilities):
    print(f"  {name:<7}: {prob * 100:>6.2f}%")

print(f"\n⏱️ Total Edge Compute Time: {inference_time:.2f} ms")