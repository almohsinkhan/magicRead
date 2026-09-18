class HeadCursorController:
    """Move the virtual cursor from relative head movement."""

    NOSE_TIP_INDEX = 1
    CURSOR_SPEED = 4.0
    DEAD_ZONE = 0.0015
    LANDMARK_SMOOTHING = 0.35

    def __init__(self, viewer):
        self.viewer = viewer
        self.smoothed_x = None
        self.smoothed_y = None
        self.last_x = None
        self.last_y = None

    def handle_landmarks(self, faces):
        """Use the nose tip of the first detected face as the head pointer."""
        if not faces:
            self.reset()
            return

        nose_tip = faces[0][self.NOSE_TIP_INDEX]
        self.smoothed_x = self.smooth(self.smoothed_x, nose_tip.x)
        self.smoothed_y = self.smooth(self.smoothed_y, nose_tip.y)

        if self.last_x is None or self.last_y is None:
            self.last_x = self.smoothed_x
            self.last_y = self.smoothed_y
            return

        movement_x = self.smoothed_x - self.last_x
        movement_y = self.smoothed_y - self.last_y
        self.last_x = self.smoothed_x
        self.last_y = self.smoothed_y

        if abs(movement_x) < self.DEAD_ZONE:
            movement_x = 0
        if abs(movement_y) < self.DEAD_ZONE:
            movement_y = 0
        if movement_x == 0 and movement_y == 0:
            return

        self.viewer.move_cursor_by(
            movement_x * self.CURSOR_SPEED,
            movement_y * self.CURSOR_SPEED,
        )

    def smooth(self, previous, current):
        if previous is None:
            return current
        return previous + (current - previous) * self.LANDMARK_SMOOTHING

    def reset(self):
        """Recalibrate when the face leaves the camera frame."""
        self.smoothed_x = None
        self.smoothed_y = None
        self.last_x = None
        self.last_y = None
