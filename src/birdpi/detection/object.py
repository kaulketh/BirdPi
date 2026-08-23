"""
ONNX based object detection for BirdPi.
"""

from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

from birdpi.models import CapturedImage, DetectedObject


class ObjectDetector:
    """
    Detect birds in captured images using a YOLO ONNX model.
    """

    BIRD_CLASS_ID = 14

    def __init__(
            self,
            model_path: Path,
            confidence_threshold: float = 0.25,
            iou_threshold: float = 0.45,
            input_size: int = 640,
    ) -> None:
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.input_size = input_size

        self._session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )

        self._input_name = self._session.get_inputs()[0].name

    @staticmethod
    def _xywh_to_xyxy(
            box: np.ndarray,
    ) -> np.ndarray:
        cx, cy, width, height = box

        return np.array(
            [
                cx - width / 2,
                cy - height / 2,
                cx + width / 2,
                cy + height / 2,
            ],
            dtype=np.float32,
        )

    @staticmethod
    def _iou(
            box_a: np.ndarray,
            box_b: np.ndarray,
    ) -> float:
        x1 = max(box_a[0], box_b[0])
        y1 = max(box_a[1], box_b[1])
        x2 = min(box_a[2], box_b[2])
        y2 = min(box_a[3], box_b[3])

        intersection_width = max(0.0, x2 - x1)
        intersection_height = max(0.0, y2 - y1)

        intersection = (
                intersection_width
                * intersection_height
        )

        area_a = (
                (box_a[2] - box_a[0])
                * (box_a[3] - box_a[1])
        )

        area_b = (
                (box_b[2] - box_b[0])
                * (box_b[3] - box_b[1])
        )

        union = area_a + area_b - intersection

        if union <= 0:
            return 0.0

        return float(intersection / union)

    def _letterbox(
            self,
            image: Image.Image,
    ) -> tuple[Image.Image, float, int, int]:
        original_width, original_height = image.size

        scale = min(
            self.input_size / original_width,
            self.input_size / original_height,
        )

        new_width = round(original_width * scale)
        new_height = round(original_height * scale)

        resized = image.resize(
            (new_width, new_height),
            Image.Resampling.BILINEAR,
        )

        pad_x = (self.input_size - new_width) // 2
        pad_y = (self.input_size - new_height) // 2

        canvas = Image.new(
            "RGB",
            (self.input_size, self.input_size),
            (114, 114, 114),
        )

        canvas.paste(
            resized,
            (pad_x, pad_y),
        )

        return canvas, scale, pad_x, pad_y

    def _prepare_image(
            self,
            image: CapturedImage,
    ) -> tuple[np.ndarray, float, int, int]:
        with Image.open(image.path) as source:
            source = source.convert("RGB")

            prepared, scale, pad_x, pad_y = self._letterbox(
                source,
            )

            array = np.asarray(
                prepared,
                dtype=np.float32,
            )

        array /= 255.0
        array = np.transpose(array, (2, 0, 1))
        array = np.expand_dims(array, axis=0)

        return array, scale, pad_x, pad_y

    def _non_max_suppression(
            self,
            candidates: list[tuple[float, np.ndarray]],
    ) -> list[tuple[float, np.ndarray]]:
        candidates = sorted(
            candidates,
            key=lambda item: item[0],
            reverse=True,
        )

        selected = []

        while candidates:
            best = candidates.pop(0)
            selected.append(best)

            best_box = self._xywh_to_xyxy(
                best[1],
            )

            remaining = []

            for candidate in candidates:
                candidate_box = self._xywh_to_xyxy(
                    candidate[1],
                )

                if self._iou(
                        best_box,
                        candidate_box,
                ) < self.iou_threshold:
                    remaining.append(candidate)

            candidates = remaining

        return selected

    @staticmethod
    def _scale_box_to_original(
            box: np.ndarray,
            scale: float,
            pad_x: int,
            pad_y: int,
    ) -> np.ndarray:
        cx, cy, width, height = box

        return np.array(
            [
                (cx - pad_x) / scale,
                (cy - pad_y) / scale,
                width / scale,
                height / scale,
            ],
            dtype=np.float32,
        )

    def detect(
            self,
            image: CapturedImage,
    ) -> list[DetectedObject]:
        """
        Detect birds in a captured image.
        """

        input_array, scale, pad_x, pad_y = (
            self._prepare_image(image)
        )

        output = self._session.run(
            None,
            {
                self._input_name: input_array,
            },
        )[0]

        predictions = output[0].T
        
        candidates = []

        for prediction in predictions:
            box = prediction[:4]
            class_scores = prediction[4:]

            confidence = float(
                class_scores[self.BIRD_CLASS_ID]
            )

            if confidence >= self.confidence_threshold:
                candidates.append(
                    (confidence, box)
                )

        detections = self._non_max_suppression(
            candidates,
        )

        objects = []

        for confidence, box in detections:
            scaled_box = self._scale_box_to_original(
                box,
                scale,
                pad_x,
                pad_y,
            )

            x1, y1, x2, y2 = self._xywh_to_xyxy(
                scaled_box,
            )

            objects.append(
                DetectedObject(
                    label="bird",
                    confidence=confidence,
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                )
            )

        return objects
