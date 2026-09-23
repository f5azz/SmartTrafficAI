# Smart Traffic AI

A smart traffic management system that combines AI-based vehicle detection, adaptive signal control, and a Flutter dashboard for monitoring traffic conditions in real time.

## Project Overview

This project simulates an intelligent traffic intersection using:

- YOLO-based vehicle detection
- SUMO traffic simulation
- FastAPI backend for live traffic status
- Flutter frontend dashboard for monitoring and control
- Firebase for authentication and dashboard data storage

## Features

- Real-time traffic monitoring dashboard
- Adaptive traffic light decision making based on vehicle density and queue length
- Pedestrian-aware crossing logic
- AI vehicle detection using YOLO
- Firebase authentication and dashboard persistence
- Dark/light mode toggle in the dashboard

## Tech Stack

### Frontend
- Flutter
- Dart
- Firebase Authentication
- Firestore

### Backend
- Python
- FastAPI
- Ultralytics YOLO
- OpenCV
- SUMO Traffic Simulation

## Folder Structure

```bash
SmartTrafficAI/
├── backend/
│   ├── api.py
│   ├── detect.py
│   ├── requirements.txt
│   ├── sumo_service.py
│   ├── traffic_controller.py
│   ├── tracker.py
│   ├── vehicle_counter.py
│   ├── yolo_service.py
│   ├── zone_tracker.py
│   ├── zones.py
│   └── sumo/
│       ├── network/
│       ├── routes/
│       └── simulation/
├── frontend/
│   ├── lib/
│   ├── android/
│   ├── ios/
│   ├── pubspec.yaml
│   └── firebase.json
├── README.md
└── .gitignore
```

## Prerequisites

### Backend
- Python 3.10+
- pip
- SUMO installed and configured

### Frontend
- Flutter SDK
- Firebase project configured

## Backend Setup

1. Open a terminal in the backend folder.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the API:

```bash
uvicorn api:app --reload
```

## Frontend Setup

1. Open a terminal in the frontend folder.
2. Install Flutter dependencies:

```bash
flutter pub get
```

3. Run the app:

```bash
flutter run -d chrome
```

## Firebase Setup

1. Create a Firebase project.
2. Enable Firebase Authentication.
3. Enable Firestore Database.
4. Add the Firebase config to the Flutter app.
5. Ensure the project id matches the app configuration in `frontend/lib/firebase_options.dart`.

## Demo Flow

1. Start the backend server.
2. Start the frontend dashboard.
3. Open the dashboard and let the traffic system run.
4. Monitor traffic density, signal decisions, and detection results.
5. Dashboard snapshots are stored in Firebase Firestore.

## Important Notes

- The YOLO model uses a pretrained `yolo11n.pt` model.
- Traffic flow is simulated using SUMO rather than real-world city traffic.
- This project is intended as an AI-driven smart traffic prototype and demonstration system.

## License

This project is for educational and demonstration purposes.

## Project Status

Prototype / research demo

## Authors

Smart Traffic AI Project
