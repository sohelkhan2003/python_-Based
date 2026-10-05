import cv2
import torch
from ultralytics import YOLO
from speech_engine import speak

# Device selection
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")

# Load YOLO model
model = YOLO("yolov10n.pt", verbose=False)
model.overrides['verbose'] = False
model.to(device)

def detector(frame):
    results = model(frame)
    r = results[0]
    output_frame = frame.copy()
    detected_names = []

    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        name = model.names[cls_id]
        detected_names.append(name)

        # Draw bounding boxes
        cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(output_frame, f"{name} {conf:.2f}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return output_frame, detected_names


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Webcam not found!")
        return

    print("[INFO] Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        output, names = detector(frame)

        # Speak continuously for every detected object
        if names:
            for obj_name in names:
                speak(f"{obj_name} detected")

        cv2.imshow("Detected Objects", output)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] Force stopped by user.")
    except Exception as e:
        print(f"[ERROR] {e}")
 