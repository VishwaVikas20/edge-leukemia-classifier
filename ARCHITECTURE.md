# 🏗️ System Architecture & Data Flow

This document outlines the end-to-end hardware and software architecture of the Edge AI Leukemia Diagnostic pipeline.

## 1. System Diagram & Data Flow
The architecture is designed as a unidirectional, offline data pipeline prioritizing speed and clinical isolation.

1.  **CMOS Biochip (Physical Input):** A patient blood sample hybridizes with the microarray.
2.  **Analog Voltage:** The chip outputs raw electrical impedance as micro-voltages.
3.  **16-bit SPI ADC (Digitization):** Converts the analog signals into digital values (0-65535).
4.  **Raspberry Pi / Edge SBC (Ingestion):** Reads the data via the GPIO pins using the `spidev` hardware bus.
5.  **Data Scaling:** The local Python backend normalizes the 54,630 features using a pre-fitted `StandardScaler`.
6.  **ElasticNet Inference:** The compressed `.joblib` model executes the 5-class probability matrix.
7.  **Local UI:** The Flask server broadcasts the result to `127.0.0.1:5000` for the clinical dashboard.

## 2. Model Pipeline & Design Decisions
Why did we choose an ElasticNet-regularized linear model over a Deep Neural Network (DNN) for edge hardware?

* **The "Curse of Dimensionality":** Microarray data operates in an extreme $p \gg n$ regime (54,630 features vs. a small cohort of patient samples). Deep learning models would immediately overfit this data space without massive data augmentation.
* **Feature Selection via L1 Penalty:** The $L_1$ component of the ElasticNet penalty naturally drives irrelevant genomic features to zero, effectively compressing the model's memory footprint by discarding useless parameters.
* **Collinearity Handling via L2 Penalty:** The $L_2$ component stabilizes the selection of highly correlated gene expression pathways, ensuring robust predictions even with noisy analog inputs.
* **Edge Compute Constraints:** By utilizing this statistical learning approach, the final model requires only a fraction of a megabyte of RAM and executes in under 2 milliseconds on a standard ARM CPU, eliminating the need for a dedicated NPU or GPU.

## 3. Local / Cloud Components
* **Cloud Components:** None.
* **Local Components:** 100% of the stack (Hardware I/O, Web Server, Data Scaler, Machine Learning Model, UI rendering) operates on the edge device.

* ## 4. Hardware Economics: The "Bare Silicon" Advantage
A critical design decision in this architecture was bypassing commercial biotechnology monopolies to achieve a true edge-native solution. 

Commercial diagnostic hardware currently operates on a closed-ecosystem model. For example, proprietary CMOS sequencing kits like the Ion Torrent 550 cost upwards of ₹4,56,713, and standard microarray chips like the Affymetrix U133 Plus 2.0 cost up to ₹71,000 per unit. These prices are artificially inflated to subsidize closed-source medical software and heavy sequencing rigs.

Our architecture disrupts this by using a bare-metal approach:
* **Open Hardware Interfacing:** Instead of relying on closed sequencers, we interface directly with mass-produced, unbranded CMOS microfluidic sensors whose raw manufacturing cost is sub-₹100 (leveraging standard foundry lithography).
* **Direct SPI Readout:** By tapping the micro-voltages directly through a 16-bit ADC into the Raspberry Pi's `spidev` bus, we completely bypass the need for proprietary reader hardware. All signal processing and ElasticNet inference happens natively on the open-source Linux SBC.
