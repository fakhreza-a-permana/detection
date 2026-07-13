import cv2
import torch
import torch.nn as nn

from PIL import Image
from ultralytics import YOLO
from torchvision import models, transforms


class ActivityRecognizer:

    CLASSES = [
        "lecturing",
        "listening",
        "realtime_writing",
        "usingcomputer"
    ]

    def __init__(
        self,
        yolo_model,
        activity_model_path,
        device=None
    ):

        self.device = device or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        print(f"[Recognizer] Device : {self.device}")

        # Load YOLO

        self.detector = YOLO(yolo_model)

        # Model

        self.activity_model = models.resnet18(weights=None)

        self.activity_model.fc = nn.Linear(
            self.activity_model.fc.in_features,
            len(self.CLASSES)
        )

        checkpoint = torch.load(
            activity_model_path,
            map_location=self.device
        )

        if (
            isinstance(checkpoint, dict)
            and "model_state_dict" in checkpoint
        ):
            self.activity_model.load_state_dict(
                checkpoint["model_state_dict"]
            )
        else:
            self.activity_model.load_state_dict(checkpoint)

        self.activity_model.to(self.device)

        self.activity_model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        print("[Recognizer] Ready")
    
    def detect(self, frame):

        annotated = frame.copy()
        detections = []

        results = self.detector(
            frame,
            classes=[0],
            verbose=False
        )

        person_id = 1

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            conf_det = float(box.conf[0])

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame.shape[1], x2)
            y2 = min(frame.shape[0], y2)
            
            if x2 <= x1 or y2 <= y1:
                continue
            crop = frame[y1:y2, x1:x2]
            
            if crop.size == 0:
                continue
            
            crop = cv2.cvtColor(
                crop,
                cv2.COLOR_BGR2RGB
            )
            
            crop = Image.fromarray(crop)
            tensor = self.transform(crop)
            tensor = tensor.unsqueeze(0)
            tensor = tensor.to(self.device)
            with torch.no_grad():
                output = self.activity_model(tensor)
                prob = torch.softmax(
                    output,
                    dim=1
                )
                score, pred = torch.max(
                    prob,
                    dim=1
                )
            activity = self.CLASSES[pred.item()]

            conf_act = float(score.item())

            label = (
                f"{activity} "
                f"{conf_act:.2f}"
            )

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )
            cv2.putText( annotated,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            detections.append({
                "person": person_id,
                "activity": activity,
                "activity_confidence": conf_act,
                "detection_confidence": conf_det,
                "bbox": [
                    x1,
                    y1,
                    x2,
                    y2
                ]
            })
            person_id += 1

        return {
            "frame": annotated,
            "detections": detections,
            "person_count": len(detections)
        }