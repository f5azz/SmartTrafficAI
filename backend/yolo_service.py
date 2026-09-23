from ultralytics import YOLO
import cv2
import os
import threading
import time


MODEL_PATH = "yolo11n.pt"
VIDEO_PATH = os.path.join("videos", "traffic.mp4")

VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


class YOLOService:

    def __init__(self):
        print("Loading YOLO model...")

        self.model = YOLO(MODEL_PATH)

        self.running = False
        self.thread = None

        self.lock = threading.Lock()

        self.data = {
            "status": "READY",
            "vehicles": 0,
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0,
            "density": "LOW",
            "fps": 0,
        }

    def calculate_density(self, vehicles):

        if vehicles <= 5:
            return "LOW"

        if vehicles <= 10:
            return "MEDIUM"

        return "HIGH"

    def process_video(self):

        cap = cv2.VideoCapture(VIDEO_PATH)

        if not cap.isOpened():

            with self.lock:
                self.data["status"] = "VIDEO ERROR"

            print("❌ Could not open:", VIDEO_PATH)

            return

        print("✅ YOLO camera feed started.")

        previous_time = time.time()

        while self.running:

            ret, frame = cap.read()

            if not ret:

                # Restart video when it reaches the end.
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

                continue

            results = self.model(
                frame,
                verbose=False
            )

            counts = {
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
            }

            for box in results[0].boxes:

                class_id = int(box.cls[0])

                if class_id in VEHICLE_CLASSES:

                    vehicle_type = VEHICLE_CLASSES[class_id]

                    counts[vehicle_type] += 1

            total = sum(counts.values())

            current_time = time.time()

            elapsed = current_time - previous_time

            fps = 1 / elapsed if elapsed > 0 else 0

            previous_time = current_time

            with self.lock:

                self.data = {
                    "status": "ACTIVE",
                    "vehicles": total,
                    "car": counts["car"],
                    "motorcycle": counts["motorcycle"],
                    "bus": counts["bus"],
                    "truck": counts["truck"],
                    "density": self.calculate_density(total),
                    "fps": round(fps, 1),
                }

            # Small delay so the laptop isn't unnecessarily overloaded.
            time.sleep(0.01)

        cap.release()

        print("YOLO camera feed stopped.")

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self.process_video,
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.running = False

        if self.thread:

            self.thread.join(timeout=2)

    def get_status(self):

        with self.lock:
            return dict(self.data)


yolo_service = YOLOService()