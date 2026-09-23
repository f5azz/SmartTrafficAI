from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO("yolo11n.pt")

video_path = "videos/traffic.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video")
    exit()


# ==========================================
# TRAFFIC APPROACH ZONES
# ==========================================

zones = {

    "NORTH": np.array([
        [430, 0],
        [680, 0],
        [680, 280],
        [450, 280]
    ], np.int32),

    "SOUTH": np.array([
        [480, 400],
        [720, 400],
        [720, 652],
        [480, 652]
    ], np.int32),

    "WEST": np.array([
        [0, 300],
        [520, 300],
        [520, 500],
        [0, 500]
    ], np.int32),

    "EAST": np.array([
        [680, 150],
        [1156, 150],
        [1156, 420],
        [680, 420]
    ], np.int32)
}


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

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False
    )


    # ==========================================
    # DRAW ZONES
    # ==========================================

    for name, polygon in zones.items():

        cv2.polylines(
            frame,
            [polygon],
            True,
            (0, 255, 255),
            3
        )

        # Find label position
        x = int(np.min(polygon[:, 0]))
        y = int(np.min(polygon[:, 1])) + 30

        cv2.putText(
            frame,
            name,
            (x + 10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )


    # ==========================================
    # COUNTS
    # ==========================================

    zone_counts = {
        "NORTH": 0,
        "SOUTH": 0,
        "EAST": 0,
        "WEST": 0
    }


    if results[0].boxes.id is not None:

        boxes = results[0].boxes

        track_ids = boxes.id.int().cpu().tolist()
        classes = boxes.cls.int().cpu().tolist()
        xyxy = boxes.xyxy.cpu().numpy()


        for track_id, class_id, box in zip(
            track_ids,
            classes,
            xyxy
        ):

            if class_id not in vehicle_classes:
                continue


            x1, y1, x2, y2 = box


            # ==================================
            # BOTTOM CENTER POINT
            # ==================================

            point_x = int((x1 + x2) / 2)
            point_y = int(y2)

            point = (point_x, point_y)


            # Draw tracking point

            cv2.circle(
                frame,
                point,
                5,
                (0, 0, 255),
                -1
            )


            # ==================================
            # FIND ZONE
            # ==================================

            for zone_name, polygon in zones.items():

                inside = cv2.pointPolygonTest(
                    polygon,
                    point,
                    False
                )


                if inside >= 0:

                    zone_counts[zone_name] += 1

                    cv2.putText(
                        frame,
                        f"ID {track_id}",
                        (point_x, point_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        2
                    )

                    break


    # ==========================================
    # DISPLAY COUNTS
    # ==========================================

    y = 40

    total = 0

    for zone, count in zone_counts.items():

        total += count

        cv2.putText(
            frame,
            f"{zone}: {count}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        y += 35


    cv2.putText(
        frame,
        f"TOTAL: {total}",
        (20, y + 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 255),
        2
    )


    cv2.imshow(
        "Smart Traffic AI - Zone Tracking",
        frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()