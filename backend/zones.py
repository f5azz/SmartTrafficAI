import cv2
import numpy as np

# Video
video_path = "videos/traffic.mp4"

cap = cv2.VideoCapture(video_path)

# Approximate traffic approach zones
zones = {
    "NORTH": np.array([
        [450, 0],
        [620, 0],
        [650, 210],
        [520, 230]
    ], np.int32),

    "SOUTH": np.array([
        [540, 450],
        [690, 450],
        [700, 652],
        [560, 652]
    ], np.int32),

    "WEST": np.array([
        [0, 350],
        [430, 350],
        [450, 460],
        [0, 460]
    ], np.int32),

    "EAST": np.array([
        [720, 180],
        [1156, 180],
        [1156, 370],
        [720, 350]
    ], np.int32)
}

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Draw each zone
    for name, polygon in zones.items():

        cv2.polylines(
            frame,
            [polygon],
            True,
            (0, 255, 255),
            3
        )

        # Label position
        x, y = polygon[0]

        cv2.putText(
            frame,
            name,
            (x + 10, y + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

    cv2.imshow(
        "Traffic Zones",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()