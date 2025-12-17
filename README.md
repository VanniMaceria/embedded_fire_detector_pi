# 🔥 Secure IoT Fire Detection System

**Course:** Embedded Systems & IoT Security  
**Platform:** Raspberry Pi | **Language:** Python | **Method:** TDD

## 📜 Project Overview
This project implements a **real-time fire detection system** on a Raspberry Pi using Edge AI. It connects the domains of **Embedded Engineering** (via strict Test Driven Development) and **IoT Security** (via Adversarial Machine Learning).

## 🏗 Architecture (Single Responsibility)
The system is modularized into five core components:

* **`FrameProvider`**: abstraction for PiCamera or video input.
* **`ImageProcessor`**: Pre-processing and input sanitization.
* **`InferenceEngine`**: Wrapper for the ML model.
* **`FireMonitor`**: Main orchestrator controlling the logic loop.
* **`AlertNotifier`**: Handles HTTP/REST API communication.

## 🛡 IoT Security: Adversarial Attacks
This project demonstrates vulnerabilities in Edge AI and implements defenses.

1.  **The Attack (Physical):** We demonstrate that an **Adversarial Patch** placed in the camera frame can blind the model (Evasion Attack).
2.  **The Defense:** The deployed model is hardened using **Adversarial Training** (retraining with adversarial examples) to resist these attacks.

## 🧪 TDD & Mocking Strategy
Development followed a **Test-First** approach.
* **Hardware Mocking:** `PiCamera` and `RPi.GPIO` are mocked using `unittest.mock` to run tests on non-ARM architecture.
* **Network Mocking:** API calls are mocked to verify logic without server dependency.
