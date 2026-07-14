import joblib
import pandas as pd
import time
import warnings

# Suppress scikit-learn version warnings for cleaner terminal output
warnings.filterwarnings("ignore", category=UserWarning)

print("--- SBC Edge Diagnostic Engine Initializing ---")
print("Loading pipeline from local flash storage...")
start_load = time.time()

# 1. Load the exported pipeline artifacts
model = joblib.load('leukemia_master_model.joblib')
scaler = joblib.load('leukemia_scaler.joblib')
mask = joblib.load('leukemia_gene_mask.joblib')

print(f"Pipeline loaded in {time.time() - start_load:.2f} seconds.")

# 2. Load a real patient for the demo (Simulating a hardware sensor read)
print("\nReading raw patient microarray data...")
df = pd.read_csv("Leukemia_5Class_Dataset.csv")
X_raw = df.drop(columns=["Target"])
y_true = df["Target"]

# Let's pick Patient #42 as our test subject
patient_id = 42
raw_patient_data = X_raw.iloc[patient_id].values.reshape(1, -1)
true_diagnosis = y_true.iloc[patient_id]

# 3. The Edge Inference Execution
print("Executing On-Device Inference...")
start_inference = time.time()

# Step A: Scale the raw data using the pre-fitted standard scaler
scaled_data = scaler.transform(raw_patient_data)

# Step B: Apply the gene mask to filter down to our target panel
filtered_data = scaled_data[:, mask]

# Step C: Predict probabilities
probabilities = model.predict_proba(filtered_data)[0]
predicted_class = model.predict(filtered_data)[0]

inference_time = (time.time() - start_inference) * 1000

# 4. Display Final Diagnostics
class_names = ['Healthy', 'ALL', 'AML', 'CLL', 'CML']

print(f"\n--- DIAGNOSTIC RESULTS (Patient #{patient_id}) ---")
print(f"True Clinical Condition : {class_names[true_diagnosis]}")
print(f"Edge Device Diagnosis   : {class_names[predicted_class]}")

print("\nConfidence Scores:")
for name, prob in zip(class_names, probabilities):
    print(f"  {name:<7}: {prob * 100:>6.2f}%")

print(f"\n⏱️ Total Edge Inference Time: {inference_time:.2f} ms")