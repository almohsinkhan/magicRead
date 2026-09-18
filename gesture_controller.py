import math

from gestures import detect_gesture


class GestureController:
    """Turn deliberate hand movement into PDF navigation."""

    POSITION_SMOOTHING = 0.45
    ZOOM_STABLE_FRAMES = 3
    ZOOM_DEAD_ZONE = 0.002
    ZOOM_SPEED = 6.0
    SCROLL_DEAD_ZONE = 0.002
    SCROLL_SPEED = 300
    VICTORY_STABLE_FRAMES = 2
    PAGE_SWIPE_DISTANCE = 0.07
    PAGE_COOLDOWN_FRAMES = 12

    def __init__(self, viewer):
        self.viewer = viewer
        self.two_hand_frames = 0
        self.smoothed_zoom_distance = None
        self.last_zoom_distance = None

        self.smoothed_pinch_y = None
        self.last_pinch_y = None
        self.scroll_remainder = 0.0

        self.victory_frames = 0
        self.smoothed_swipe_x = None
        self.last_swipe_x = None
        self.swipe_distance = 0.0
        self.page_cooldown = 0

    def handle_landmarks(self, hands):
        """Handle the hands detected in one camera frame."""
        if len(hands) == 2:
            self.handle_two_hands(hands)
        elif len(hands) == 1:
            self.handle_one_hand(hands[0])
        else:
            self.reset_all()

    def handle_two_hands(self, hands):
        """Zoom continuously as the distance between two hands changes."""
        self.two_hand_frames += 1
        self.reset_one_hand_motion()

        hand1, hand2 = hands
        p1, p2 = hand1[8], hand2[8]
        distance = math.hypot(p1.x - p2.x, p1.y - p2.y)
        self.smoothed_zoom_distance = self.smooth(
            self.smoothed_zoom_distance,
            distance,
        )

        if self.two_hand_frames < self.ZOOM_STABLE_FRAMES:
            self.last_zoom_distance = self.smoothed_zoom_distance
            return

        change = self.smoothed_zoom_distance - self.last_zoom_distance
        self.last_zoom_distance = self.smoothed_zoom_distance

        if abs(change) >= self.ZOOM_DEAD_ZONE:
            self.viewer.zoom_by(change * self.ZOOM_SPEED)

    def handle_one_hand(self, hand):
        """Use 🤏 movement to scroll and ✌️ movement to change page."""
        self.reset_two_hand_motion()

        gesture = detect_gesture(hand)
        self.handle_scroll(gesture, hand)
        self.handle_page_swipe(gesture, hand)

    def handle_scroll(self, gesture, hand):
        """Scroll proportionally to vertical movement while pinching."""
        if gesture != "PINCH":
            self.smoothed_pinch_y = None
            self.last_pinch_y = None
            self.scroll_remainder = 0.0
            return

        self.smoothed_pinch_y = self.smooth(
            self.smoothed_pinch_y,
            hand[8].y,
        )

        if self.last_pinch_y is not None:
            movement = self.smoothed_pinch_y - self.last_pinch_y
            if abs(movement) >= self.SCROLL_DEAD_ZONE:
                self.scroll_remainder += movement * self.SCROLL_SPEED
                amount = math.trunc(self.scroll_remainder)
                if amount:
                    self.viewer.scroll(amount)
                    self.scroll_remainder -= amount

        self.last_pinch_y = self.smoothed_pinch_y

    def handle_page_swipe(self, gesture, hand):
        """Change pages after a short, deliberate ✌️ swipe."""
        if gesture != "VICTORY":
            self.victory_frames = 0
            self.smoothed_swipe_x = None
            self.last_swipe_x = None
            self.swipe_distance = 0.0
            return

        self.victory_frames += 1
        self.smoothed_swipe_x = self.smooth(
            self.smoothed_swipe_x,
            hand[8].x,
        )

        if self.last_swipe_x is not None:
            self.swipe_distance += self.smoothed_swipe_x - self.last_swipe_x
        self.last_swipe_x = self.smoothed_swipe_x

        if self.victory_frames < self.VICTORY_STABLE_FRAMES:
            return

        if self.page_cooldown > 0:
            self.page_cooldown -= 1
            self.swipe_distance = 0.0
            return

        if self.swipe_distance > self.PAGE_SWIPE_DISTANCE:
            self.viewer.next_page()
            self.reset_page_swipe()
        elif self.swipe_distance < -self.PAGE_SWIPE_DISTANCE:
            self.viewer.previous_page()
            self.reset_page_swipe()

    def reset_page_swipe(self):
        self.swipe_distance = 0.0
        self.page_cooldown = self.PAGE_COOLDOWN_FRAMES

    def reset_two_hand_motion(self):
        self.two_hand_frames = 0
        self.smoothed_zoom_distance = None
        self.last_zoom_distance = None

    def reset_one_hand_motion(self):
        self.smoothed_pinch_y = None
        self.last_pinch_y = None
        self.scroll_remainder = 0.0
        self.victory_frames = 0
        self.smoothed_swipe_x = None
        self.last_swipe_x = None
        self.swipe_distance = 0.0

    def reset_all(self):
        self.reset_two_hand_motion()
        self.reset_one_hand_motion()

    def smooth(self, previous, current):
        if previous is None:
            return current
        return previous + (current - previous) * self.POSITION_SMOOTHING
