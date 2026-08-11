# SENTIENT SCOUT: An Embodied Mission Agent for Adaptive Field Intelligence

## 📌 Overview

Sentient Scout is an Edge-AI powered ground vehicle designed for biometric
target verification, real-time visual servoing, adaptive tracking, and
remote monitoring.

The system combines an NVIDIA Jetson Orin Nano as the Edge-AI host processor
with an ESP32 slave controller for low-level PID and motor execution.

The project integrates computer vision, facial recognition, PID control,
pan-tilt servo actuation, rover control, and remote communication into an
autonomous cyber-physical system.

---

## 🎯 Aim

To develop "Sentient Scout," an Edge-AI powered ground vehicle capable of
biometric target verification, real-time visual servoing via a 360° pan-tilt
mechanism, distance maintenance, and remote tactical deployment via a secure
messaging interface for advanced sentry operations.

---

## ✨ Key Features

- Edge-AI based target detection
- Real-time facial recognition
- 128-dimensional facial embeddings
- Biometric target verification
- Real-time visual servoing
- 2-DOF pan-tilt mechanism
- PID-based tracking control
- Adaptive target following
- Flask-based live video monitoring
- Telegram-based alerts
- Jetson Orin Nano + ESP32 architecture
- JSON serial communication
- Local edge processing without cloud dependency

---

## 🧠 System Architecture

The system consists of a local edge layer and a remote communication layer.

### Local Layer

- 4WD UGV rover
- Camera module
- NVIDIA Jetson Orin Nano
- ESP32 controller
- Pan-tilt servo mechanism
- Rover chassis and motors

### Remote Layer

- Wi-Fi communication
- Flask web server
- Live processed video feed
- Telegram Bot API
- Remote target data and command interface

---

## 🔄 Working Principle

```text
Operator
    │
    ├── Telegram
    │
    ▼
Target Data / Activation Command
    │
    ▼
NVIDIA Jetson Orin Nano
    │
    ▼
Camera Frame Capture
    │
    ▼
Person / Face Detection
    │
    ▼
128-D Facial Embedding
    │
    ▼
Target Comparison
    │
    ├── No Match ──► Continue Scanning
    │
    └── Match
          │
          ▼
      Target Tracking
          │
          ├── PID Control
          │
          ├── Pan-Tilt Control
          │
          ├── Rover Movement
          │
          ├── Telegram Alert
          │
          └── Flask Live Dashboard

⚙️ Hardware
NVIDIA Jetson Orin Nano
ESP32
Camera Module
2-DOF High-Torque TTL Serial Bus Servos
4WD UGV Rover Chassis
Closed-Loop Encoder Motors
3S Lithium Battery UPS System
Wi-Fi Module
💻 Software
Python 3
OpenCV
YOLOv8-nano / HOG Descriptor
face_recognition
dlib
Custom PID Controller
Flask
Telegram Bot API
JSON Serial Communication
🔍 Biometric Verification

The system generates a 128-dimensional facial embedding for the detected
face and compares it with the stored target biometric data using facial
similarity comparison.

If the detected face matches the target, the system activates the tracking
protocol.

🎥 Visual Servoing

Once the target is verified, the system calculates the visual error between
the target's position and the center of the camera frame.

The pan-tilt mechanism is controlled using PID control to continuously keep
the target centered in the camera view.

🎛️ PID Control

The project uses separate PID parameters for pan and tilt control.

Pan
P = 0.012
I = 0.0
D = 0.005
Tilt
P = 0.012
I = 0.001
D = 0.008

Servo limits:

PAN:  -90° to +90°
TILT: -90° to +90°
📡 Remote Monitoring

The project uses two remote communication mechanisms:

Flask Dashboard

The Flask server provides a live processed video stream containing
bounding boxes and identity labels.

Telegram

Telegram is used to:

Receive target information
Activate the tracking mode
Send target detection alerts
Send captured images
Provide remote monitoring
🔌 Jetson–ESP32 Communication

The NVIDIA Jetson Orin Nano performs the main Edge-AI processing while the
ESP32 handles low-level hardware control.

JSON serial communication is used between the Jetson and ESP32.

🧪 Algorithm
Initialize the rover, Jetson Orin Nano, camera, and ESP32.
Receive target biometric data and activation command.
Capture live video frames.
Detect human presence.
Extract facial embeddings.
Compare the detected face with the target data.
If there is no match, continue scanning.
If a match is found, activate tracking.
Send an alert and captured image to the operator.
Control the pan-tilt mechanism using PID.
Command the rover to maintain the desired distance.
Stream the processed video through the Flask dashboard.
Continue until a stop command is received.
📊 Results

The project demonstrated:

Autonomous target detection
Facial recognition
Adaptive target tracking
Pan-tilt visual servoing
Rover movement
Telegram alert delivery
Live Flask video monitoring
Edge-based AI processing

The prototype successfully integrated perception, biometric verification,
physical tracking, and remote communication into an embodied AI rover


📁 Repository Structure
sentient-scout-edge-ai-rover/
│
├── README.md
├── .gitignore
│
├── docs/
│   └── project-report.pdf
│
├── src/
├── core/
├── hardware/
├── config/
├── web/
│
└── assets/

The source-code folders will be populated as the project implementation
is reconstructed from the project documentation.

📄 Documentation

The complete project report is available in:

docs/project-report.pdf
⚠️ Security

Private credentials, API tokens, and biometric target images should not be
uploaded to a public repository.

Use environment variables or local configuration files for sensitive
information.

👨‍💻 Author

A. Moulieswaran

Electronics and Communication Engineering