# 🔌 Hardware Assembly & Wiring Guide

This document outlines the physical hardware schematics required to deploy the Edge AI Leukemia Diagnostic pipeline on a Raspberry Pi using a CMOS Microfluidic Biochip and a 16-bit SPI Analog-to-Digital Converter (ADC).

## 🛠️ Required Components
1. **Edge SBC:** Raspberry Pi 4 Model B (2GB+ RAM recommended)
2. **ADC Module:** 16-bit High-Speed SPI ADC (e.g., ADS8320 or equivalent standard SPI ADC)
3. **Sensor:** CMOS Microfluidic Biochip (Microarray)
4. **Jumper Wires:** Standard Female-to-Female dupont cables

---

## 1. Raspberry Pi to ADC Wiring (Digital SPI Bus)
The ADC communicates with the Raspberry Pi via the high-speed SPI bus. This allows the Pi to rapidly read the 54,630 digitized voltage features.

Ensure your Raspberry Pi is powered off before making these connections.

| ADC Pin | Raspberry Pi 4 Pin (Physical) | GPIO Name | Function |
| :--- | :--- | :--- | :--- |
| **VDD / VCC** | Pin 1 | `3.3V Power` | Provides 3.3V logic power to the ADC |
| **GND** | Pin 6 | `Ground` | Common ground reference |
| **SCLK / CLK** | Pin 23 | `GPIO 11 (SCLK)` | SPI Serial Clock (Synchronizes data) |
| **DOUT / MISO**| Pin 21 | `GPIO 9 (MISO)` | Master In Slave Out (Data from ADC to Pi) |
| **DIN / MOSI** | Pin 19 | `GPIO 10 (MOSI)` | Master Out Slave In (Commands to ADC) |
| **CS / CE0** | Pin 24 | `GPIO 8 (CE0)` | Chip Select (Activates the ADC) |



---

## 2. CMOS Biochip to ADC Wiring (Analog Signals)
The biochip outputs raw analog voltages based on the electrochemical impedance of the hybridized RNA. 

1. **V_OUT (Biochip)** ➔ **A0 / Analog In (ADC):** Connect the primary analog output channel of the biochip to the first analog input channel of the ADC.
2. **GND (Biochip)** ➔ **GND (ADC / Pi):** Ensure the biochip shares a common ground with the ADC and Raspberry Pi to prevent floating voltage readings.

---

## 3. SBC System Configuration
By default, the SPI bus is disabled on standard Raspberry Pi OS installations. You must enable it at the hardware level before running `app.py`.

1. Open the Raspberry Pi terminal.
2. Run the configuration tool:
   ```bash
   sudo raspi-config
3. Navigate to Interface Options ➔ SPI.

4. Select Yes to enable the SPI interface.

5. Reboot the Raspberry Pi:
    ```bash
    sudo reboot