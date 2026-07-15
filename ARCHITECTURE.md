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
* **Local Components:** Entire stack operates at local level.

## 4. Hardware Economics: The "Bare Silicon" Advantage
A critical design decision in this architecture was bypassing commercial biotechnology monopolies to achieve a true edge-native solution. 

Commercial diagnostic hardware currently operates on a closed-ecosystem model. For example, proprietary CMOS sequencing kits like the Ion Torrent 550 cost upwards of ₹4,56,713, and standard microarray chips like the Affymetrix U133 Plus 2.0 cost up to ₹71,000 per unit. These prices are artificially inflated to subsidize closed-source medical software and heavy sequencing rigs.

Our architecture disrupts this by using a bare-metal approach:

* **Open Hardware Interfacing:** Instead of relying on closed sequencers, we interface directly with mass-produced, unbranded CMOS microfluidic sensors. Based on [Stanford University's "Lab-on-a-Chip" manufacturing breakthroughs](https://indianexpress.com/article/technology/science/scientists-develop-lab-on-a-chip-that-costs-less-than-a-rupee-4512241/), leveraging standard foundry lithography and inkjet deposition brings the raw silicon cost down to sub-₹100 (and often as low as ₹1 at scale).

* **Direct SPI Readout:** By tapping the micro-voltages directly through a 16-bit ADC into the Raspberry Pi's `spidev` bus, we completely bypass the need for proprietary reader hardware. All signal processing and ElasticNet inference happens natively on the open-source Linux SBC.

## 5. Technical Report & Benchmarks
To prove the viability of executing this on an edge SBC, we benchmarked the system strictly on CPU-bound hardware without dedicated NPUs or GPUs.

* **Model & Runtime:** `scikit-learn`'s `SGDClassifier` (configured with `loss="log_loss"` for probability outputs and an `elasticnet` penalty) running on a local Python 3 Flask server.
* **Optimization Technique:** The $L_1$ component of the ElasticNet penalty naturally acts as a feature selector, aggressively shrinking irrelevant microarray feature weights to exactly zero, effectively creating a highly sparse, quantized memory footprint.
* **Model Size:** The final exported `.joblib` artifact is highly compressed for edge deployment.
* **Inference Latency:** < 2.5 milliseconds per sample.
* **Hardware Utilization:** 100% CPU. 

## 6. Evaluation & Clinical Limitations
* **Accuracy & Validation:** The model was trained and validated using a stratified 80/20 train-test split on the 1,890 samples from the NCBI GEO dataset. 
* **Custom Clinical Weighting:** To minimize fatal false negatives, the Master Model applies a custom 3:1 penalty ratio for cancerous profiles (ALL, AML, CLL, CML) versus healthy profiles. This intentionally biases the model to prioritize catching cancer over confirming health.
* **Baseline Comparison:** `SGDClassifier` with ElasticNet was chosen over Deep Neural Networks because it prevents severe overfitting in the high-dimensional ($p \gg n$) genomic space while keeping latency under 2ms.
* **Known Failure Cases:** 1. *Hardware Degradation:* Physical wear on the CMOS biochip or SPI ADC interference can introduce voltage noise, skewing the 1D input array.
  2. *Sample Contamination:* Impure blood samples will generate out-of-distribution impedance values.
  3. *Triage Fallback:* To mitigate the above, the system enforces a strict **>50% confidence threshold**. Any inference below this probability distribution is automatically rejected and flagged as "INCONCLUSIVE" for human review.


## 7. Privacy, Safety & Data Handling
* **Data Storage:** The system operates entirely in volatile memory (RAM). Patient impedance data is read via the SPI bus, scaled, inferred, and immediately discarded. 
* **Permissions:** The web dashboard is hosted locally on `0.0.0.0`, meaning it is only accessible to devices (e.g., clinic iPads) on the exact same physical Wi-Fi network. 
* **Compliance:** Because zero data is transmitted over the public internet, the architecture is intrinsically HIPAA-compliant.

## 8. Attribution & Open Source Acknowledgements
This project stands on the shoulders of the open-source and open-science communities:
* **Dataset:** [NCBI GEO GSE13159](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE13159) provided the raw microarray matrix.
* **Machine Learning:** The `scikit-learn` foundation for the ElasticNet implementation.
* **Hardware I/O:** The `spidev` Linux library for direct SPI bus communication.
* **Hardware Inspiration:** [Stanford University's research](https://indianexpress.com/article/technology/science/scientists-develop-lab-on-a-chip-that-costs-less-than-a-rupee-4512241/) on ultra-low-cost inkjet-printed microfluidics.
