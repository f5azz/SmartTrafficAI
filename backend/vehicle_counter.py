from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

video_path = "videos/traffic.mp4"
cap = cv2.VideoCapture(video_path)

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

    results = model(frame, verbose=False)

    counts = {
        "car": 0,
        "motorcycle": 0,
        "bus": 0,
        "truck": 0
    }

    for box in results[0].boxes:
        class_id = int(box.cls[0])

        if class_id in vehicle_classes:
            vehicle_type = vehicle_classes[class_id]
            counts[vehicle_type] += 1

    total = sum(counts.values())

    annotated_frame = results[0].plot()

    cv2.putText(
        annotated_frame,
        f"Vehicles: {total}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    y = 80

    for vehicle_type, count in counts.items():
        cv2.putText(
            annotated_frame,
            f"{vehicle_type}: {count}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        y += 30

    cv2.imshow("Smart Traffic AI", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()