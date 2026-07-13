from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        try:
            # 1. Read the uploaded CSV
            df = pd.read_csv(filepath)
            
            # Drop the 'Target' column if it exists in the uploaded mock file
            if 'Target' in df.columns:
                df = df.drop(columns=['Target'])
                
            # Grab the first row to simulate reading one patient's biochip
            raw_patient_data = df.iloc[0].values.reshape(1, -1)
            
            # 2. Run the pipeline
            start_time = time.time()
            scaled_data = scaler.transform(raw_patient_data)
            
            # Predict
            probabilities = model.predict_proba(scaled_data)[0]
            predicted_class = model.predict(scaled_data)[0]
            inference_time = (time.time() - start_time) * 1000

            # 3. Format the response
            response = {
                'diagnosis': class_names[predicted_class],
                'confidence': f"{np.max(probabilities) * 100:.2f}%",
                'time_ms': f"{inference_time:.2f} ms",
                'all_probs': {class_names[i]: f"{probabilities[i]*100:.1f}%" for i in range(5)}
            }
            
            # Clean up the file
            os.remove(filepath)
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)