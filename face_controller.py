class HeadCursorController:
    """Move the virtual cursor from the detected face position."""

    NOSE_TIP_INDEX = 1

    def __init__(self, viewer):
        self.viewer = viewer

    def handle_landmarks(self, faces):
        """Use the nose tip of the first detected face as the head pointer."""
        if not faces:
            return

        face = faces[0]
        self.viewer.move_cursor_from_face(face)
