#include <Arduino.h>
#include <math.h>
#include "esp32_weights.h" 

// Array to hold our simulated patient data
float patient_data[NUM_GENES];

void setup() {
  Serial.begin(115200);
  delay(1000); // Give the serial monitor a second to connect
  
  Serial.println("--- Edge Leukemia Diagnostic Engine Initializing ---");
  Serial.print("Loading model parameters from Flash Memory... Genes: ");
  Serial.println(NUM_GENES);

  // 1. Simulate Patient Data (Standard Scaled)
  // In a real device, this comes from an ADC sensor. 
  // Here, we generate random scaled values between -2.0 and 2.0
  for(int i = 0; i < NUM_GENES; i++) {
    patient_data[i] = random(-200, 200) / 100.0f; 
  }

  // 2. Compute the Logits (Dot Product)
  float logits[NUM_CLASSES];
  float exp_sum = 0.0f;

  long start_time = millis(); // Let's track how fast the ESP32 calculates this!

  for(int c = 0; c < NUM_CLASSES; c++) {
    logits[c] = INTERCEPTS[c];
    
    for(int g = 0; g < NUM_GENES; g++) {
      // CRITICAL: We must use pgm_read_float to pull weights from Flash Memory
      float weight = pgm_read_float(&WEIGHTS[c][g]);
      logits[c] += weight * patient_data[g];
    }
    
    // Softmax preparation: Calculate e^(logit)
    logits[c] = exp(logits[c]);
    exp_sum += logits[c];
  }

  long end_time = millis();

  // 3. Output Final Probabilities
  Serial.println("\n--- DIAGNOSTIC RESULTS ---");
  const char* class_names[] = {"Healthy", "ALL", "AML", "CLL", "CML"};
  
  for(int c = 0; c < NUM_CLASSES; c++) {
    float probability = (logits[c] / exp_sum) * 100.0f;
    Serial.print(class_names[c]);
    Serial.print(": ");
    Serial.print(probability, 2);
    Serial.println("%");
  }

  Serial.print("\nInference Execution Time: ");
  Serial.print(end_time - start_time);
  Serial.println(" milliseconds");
}

void loop() {
  // Edge devices usually run once per button press, so we leave this empty.
}