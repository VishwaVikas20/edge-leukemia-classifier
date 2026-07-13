from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)

print("Loading Edge AI Pipeline...")
model = joblib.load('leukemia_master_model.joblib')
scaler = joblib.load('leukemia_scaler.joblib')
class_names = ['Healthy', 'ALL', 'AML', 'CLL', 'CML']
print("Pipeline Ready.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if the user uploaded a physical CSV file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            df = pd.read_csv(file)
            if 'Target' in df.columns:
                df = df.drop(columns=['Target'])
                
            raw_patient_data = df.iloc[0].values.reshape(1, -1)
            
        # Otherwise, fall back to the selected preset profile
        else:
            data = request.json
            patient_id = data.get('patient_id', '1')
            
            seeds = {'1': 42, '2': 99, '3': 123}
            np.random.seed(seeds.get(patient_id, 42))
            raw_patient_data = np.random.randn(1, 54630) * 2.0
            
        # Execute the On-Device Pipeline
        start_time = time.time()
        scaled_data = scaler.transform(raw_patient_data)
        
        probabilities = model.predict_proba(scaled_data)[0]
        predicted_class = model.predict(scaled_data)[0]
        inference_time = (time.time() - start_time) * 1000

        response = {
            'diagnosis': class_names[predicted_class],
            'confidence': f"{np.max(probabilities) * 100:.2f}%",
            'time_ms': f"{inference_time:.2f} ms",
            'all_probs': {class_names[i]: f"{probabilities[i]*100:.1f}%" for i in range(5)}
        }
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)