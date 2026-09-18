import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class CameraController:
    """Read webcam frames and provide detected hand and face landmarks."""

    def __init__(
        self,
        root,
        on_hand_landmarks,
        on_face_landmarks,
        hand_model_path="hand_landmarker.task",
        face_model_path="face_landmarker.task",
    ):
        self.root = root
        self.on_hand_landmarks = on_hand_landmarks
        self.on_face_landmarks = on_face_landmarks
        self.cap = cv2.VideoCapture(0)
        self.timestamp = 0
        self.is_running = False

        self.detector = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=python.BaseOptions(model_asset_path=hand_model_path),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=2,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        )
        self.face_detector = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=python.BaseOptions(model_asset_path=face_model_path),
                running_mode=vision.RunningMode.VIDEO,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        )

    def start(self):
        """Start processing webcam frames."""
        self.is_running = True
        self.update()

    def update(self):
        """Process one frame, then schedule the next frame."""
        if not self.is_running:
            return

        success, frame = self.cap.read()

        if success:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            self.timestamp += 1
            hand_result = self.detector.detect_for_video(image, self.timestamp)
            face_result = self.face_detector.detect_for_video(image, self.timestamp)

            self.on_hand_landmarks(hand_result.hand_landmarks)
            self.on_face_landmarks(face_result.face_landmarks)

        self.root.after(10, self.update)

    def close(self):
        """Release webcam and MediaPipe resources."""
        self.is_running = False
        self.cap.release()
        self.detector.close()
        self.face_detector.close()
