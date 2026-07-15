# Edge AI Leukemia Classifier

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Theme: On-Device AI](https://img.shields.io/badge/OSDHack_2026-On--Device_AI-success)](#)



## What We Built
We built an offline-first, hardware-integrated clinical pipeline that bridges the gap between biological microarrays and physical edge computing. It compresses a heavy 54,630-feature genomic dataset into an ultra-lightweight ElasticNet model capable of running entirely offline on a Raspberry Pi Edge SBC in expected under 2 milliseconds(for inference).

A patient's processed blood sample is applied to a CMOS biochip, where hybridized RNA alters the chip's electrical impedance. These micro-voltage changes are digitized by a 16-bit SPI ADC and transmitted directly to a Raspberry Pi. The Pi then executes an ultra-lightweight, 54,630-feature ElasticNet inference entirely offline in under 2 milliseconds, serving the final diagnostic results directly to the doctor via a locally hosted web dashboard.

## 🚨 Why It Matters
A traditional Comprehensive Leukemia Diagnostic Panel (using Flow Cytometry, PCR, or Next-Generation Sequencing) in India currently costs patients anywhere from ₹10,000 to ₹33,000 and takes days to process at a centralized lab.

On the other hand, thanks to recent manufacturing breakthroughs, a mass-produced disposable CMOS microfluidic biochip cartridge can cost as little as ₹50 to ₹100 to produce. Since the Raspberry Pi is a reusable device doing all the computation locally, the software cost per test drops to ₹0. resulting in the total cost estimated around ₹500.

While this architecture is not intended to completely replace comprehensive laboratory panels, it serves as a highly affordable, instant screening tool. It allows clinics to initiate testing immediately at the very first sign of symptoms, drastically accelerating the triage process for high-risk patients before committing them to expensive, centralized lab tests.

## ⚙️ How It Works
1. **Physical Hardware:** A CMOS Biochip reads physical blood impedance (hybridized RNA).
2. **Signal Digitization:** A 16-bit High-Speed SPI ADC digitizes the analog voltages.
3. **Edge Inference:** The Raspberry Pi (SBC) reads the 54,630 features natively via the `spidev` bus.
4. **Clinical Guardrails:** A compressed ElasticNet model executes on-device. If model confidence is below 50%, a built-in safety logic rejects the prediction and defaults to "INCONCLUSIVE" to mandate human pathologist review.

## 🧠 How It Uses On Device AI
* **Zero Cloud Dependency:** 100% of the data extraction, preprocessing, and model inference happens locally on the edge device.
* **Hardware Integrated:** It is not just a local web app; it uses the `spidev` library to read live electrical signals straight from the Raspberry Pi's GPIO pins.
* **Local Serving:** It serves a local clinical dashboard on `0.0.0.0` for Phones/Tablets/Desktops/Laptops connected to the same local WiFi network as rasberry pi, bypassing the broader internet completely.

## 🗂️ Repository Architecture
This project is cleanly separated into three distinct environments:

```text
📦 edge-leukemia-classifier
 ┣ 📂 EdgeDeviceDeployment      # Physical SBC hardware logic (spidev)
 ┃ ┣ 📜 app.py                  # Main edge inference script
 ┃ ┣ 📜 HARDWARE_WIRING.md      # SPI pinout schematics
 ┃ ┣ 📜 requirements.txt
 ┃ ┗ 📂 templates               # Local clinical web UI
 ┣ 📂 ModelMaking               # Data science & training sandbox
 ┃ ┣ 📜 main.ipynb              # ElasticNet compression pipeline
 ┃ ┗ 📜 requirements.txt        
 ┣ 📂 Simulation_App            # Interactive hackathon pitch UI
 ┃ ┣ 📜 app.py
 ┃ ┣ 📜 requirements.txt
 ┃ ┗ 📂 templates
 ┣ 📜 .gitignore
 ┣ 📜 LICENSE                   # MIT Open Source License
 ┗ 📜 README.md


## 🚀 How Others Can Run or Try It (Setup & Usage)

### 1. Running the Hardware Simulation (No Hardware Required)
If you do not have a physical CMOS biochip and ADC wired to your machine, you can test the AI and visualize the hardware data flow using our interactive simulation dashboard:
1. Clone this repository and navigate to: `cd Simulation_App`
2. Install the lightweight requirements: `pip install -r requirements.txt`
3. Run the app : `python app.py`
4. Open `http://127.0.0.1:5000` in your browser.
5. Click **Initiate Test** to watch the simulated hardware data-flow.

### 2. Physical Edge Deployment (Raspberry Pi / SBC)
To deploy the true offline architecture on a clinical edge device:
1. Flash a Raspberry Pi 4 with standard Raspberry Pi OS and enable the SPI bus (`sudo raspi-config`).
2. Wire the ADC to the Pi's GPIO (Pins 19, 21, 23, 24). *See `EdgeDeviceDeployment/HARDWARE_WIRING.md` for schematics and circuits.*
3. Navigate to: `cd EdgeDeviceDeployment`
4. Install hardware requirements: `pip install -r requirements.txt`
5. Run the local hardware server: `python app.py`

---

## 🎥 Demo Video
Pending

## 📸 Screenshots
<img width="2916" height="1746" alt="Image 15-07-26 at 1 15 PM" src="https://github.com/user-attachments/assets/c325bb97-31ac-439d-92aa-9f726be74deb" />


<img width="2916" height="1774" alt="Image 15-07-26 at 1 16 PM" src="https://github.com/user-attachments/assets/e0d33715-e227-410c-af84-ecae9fbd5f39" />


<img width="2916" height="1774" alt="Image 15-07-26 at 1 17 PM" src="https://github.com/user-attachments/assets/ffab81ca-9daf-43f8-8f3e-943b1cb30a79" />

If not used in the Edge device with Linux in it 
<img width="1172" height="400" alt="Image 15-07-26 at 1 29 PM" src="https://github.com/user-attachments/assets/c0a85d83-b0ce-4175-9b8d-0eadf8e7e415" />


---
## 📜 License & Open Source
This project is fully open-source and OSI-compliant under the **MIT License**. See the `LICENSE` file in the repository root for details.

*(Note: Due to GitHub's file size limits, the raw 1.7GB NCBI GEO dataset is excluded from `/ModelMaking`. Download `GSE13159` directly from NCBI to retrain the model from scratch.)*

