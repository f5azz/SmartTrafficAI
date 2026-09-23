from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

video_path = "videos/traffic.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video")
    exit()

vehicle_classes = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Track vehicles
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False
    )

    annotated_frame = results[0].plot()

    vehicle_count = 0

    if results[0].boxes.id is not None:

        track_ids = results[0].boxes.id.int().cpu().tolist()
        classes = results[0].boxes.cls.int().cpu().tolist()

        for track_id, class_id in zip(track_ids, classes):

            if class_id in vehicle_classes:

                vehicle_count += 1

                print(
                    f"Vehicle ID: {track_id} | "
                    f"Type: {vehicle_classes[class_id]}"
                )

    cv2.putText(
        annotated_frame,
        f"Vehicles in frame: {vehicle_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "Smart Traffic AI - Tracking",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()