# 🔥 Secure IoT Fire Detection System

**Course:** Embedded Systems & IoT Security  
**Platform:** Raspberry Pi | **Language:** Python 

## 📜 Project Overview
This project is about a **real-time fire detection system** on a Raspberry Pi using AI. It connects the domains of **Embedded Engineering** and **IoT Security**.

## 🏗 Architecture (Single Responsibility)
The system is modularized into five core components:

* **`FrameProvider`**: abstraction for PiCamera or video input.
* **`ImageProcessor`**: Pre-processing and input sanitization.
* **`InferenceEngine`**: Wrapper for the ML model.
* **`FireMonitor`**: Main orchestrator controlling the logic loop.
* **`AlertNotifier`**: Handles MQTT communication.

## 🛡 IoT Security: Adversarial Attacks
This project demonstrates vulnerabilities in IoT AI based solutions and implements defenses.

1.  **The Attack:** We demonstrate that an **Adversarial Patch** placed in the camera frame can blind the model (Evasion Attack).
2.  **The Defense:** The deployed model is hardened using **Adversarial Training** to resist these attacks.
