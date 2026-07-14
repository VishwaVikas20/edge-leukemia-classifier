from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)

print("--- SBC Medical Edge Engine Booting ---")
model = joblib.load('leukemia_master_model.joblib')
scaler = joblib.load('leukemia_scaler.joblib')
class_names = ['Healthy', 'ALL', 'AML', 'CLL', 'CML']

# --- HARDWARE SPI INITIALIZATION ---
NUM_FEATURES = 54630
V_REF = 3.3  

try:
    import spidev # <-- Moved inside the try block!
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 5000000 
    spi.mode = 0b01
    print("✅ Hardware SPI Bus Locked. Awaiting ADC signals.")
except ImportError:
    print("CRITICAL HARDWARE FAILURE: 'spidev' module not found.")
    print("This script must be run on a Linux SBC (e.g., Raspberry Pi) with SPI enabled.")
    exit(1)
except Exception as e:
    print(f"CRITICAL HARDWARE FAILURE: SPI Bus not detected. ({e})")
    print("Ensure CMOS Biochip and ADC are physically wired to SBC GPIO.")
    exit(1)

def read_cmos_biochip():
    """Reads 54,630 analog voltages via SPI from the hardware."""
    raw_voltages = np.zeros(NUM_FEATURES, dtype=np.float32)
    spi.xfer2([0x01]) 
    
    chunk_size = 4096
    bytes_read = []
    total_bytes_needed = NUM_FEATURES * 2
    
    while len(bytes_read) < total_bytes_needed:
        fetch_size = min(chunk_size, total_bytes_needed - len(bytes_read))
        bytes_read.extend(spi.readbytes(fetch_size))
        
    for i in range(NUM_FEATURES):
        high_byte = bytes_read[i * 2]
        low_byte = bytes_read[(i * 2) + 1]
        digital_val = (high_byte << 8) | low_byte
        raw_voltages[i] = (digital_val / 65535.0) * V_REF
        
    return raw_voltages.reshape(1, -1)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        start_time = time.time()
        
        # Read the real blood sample via SPI
        raw_patient_data = read_cmos_biochip()
        
        scaled_data = scaler.transform(raw_patient_data)
        
        probabilities = model.predict_proba(scaled_data)[0]
        predicted_class = model.predict(scaled_data)[0]
        inference_time = (time.time() - start_time) * 1000

        max_confidence = np.max(probabilities) * 100
        
        if max_confidence < 50.0:
            diagnosis = "INCONCLUSIVE - CLINICAL OVERRIDE"
        else:
            diagnosis = class_names[predicted_class]

        response = {
            'diagnosis': diagnosis,
            'confidence': f"{max_confidence:.2f}%",
            'time_ms': f"{inference_time:.2f} ms",
            'all_probs': {class_names[i]: f"{probabilities[i]*100:.1f}%" for i in range(5)}
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)