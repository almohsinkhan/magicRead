import math

from gestures import detect_gesture


class GestureController:
    """Translate hand landmarks into PDF controls."""

    def __init__(self, viewer):
        self.viewer = viewer
        self.last_zoom_distance = None
        self.last_click_gesture = None
        self.last_y = None
        self.last_x = None
        self.two_hand_frames = 0
        self.zoom_cooldown = 0
        self.page_cooldown = 0

    def handle_landmarks(self, hands):
        """Handle the hands detected in one camera frame."""
        if len(hands) == 2:
            self.handle_two_hands(hands)
        elif len(hands) == 1:
            self.handle_one_hand(hands[0])
        else:
            self.reset_no_hands()

    def handle_two_hands(self, hands):
        """Zoom when two stable hands move apart or together."""
        self.two_hand_frames += 1

        if self.two_hand_frames >= 5:
            hand1, hand2 = hands
            p1, p2 = hand1[8], hand2[8]
            distance = math.hypot(p1.x - p2.x, p1.y - p2.y)

            if self.last_zoom_distance is not None and self.zoom_cooldown == 0:
                change = distance - self.last_zoom_distance

                if change > 0.015:
                    self.viewer.zoom_in()
                    self.zoom_cooldown = 8
                elif change < -0.015:
                    self.viewer.zoom_out()
                    self.zoom_cooldown = 8

            self.last_zoom_distance = distance

        self.last_y = None
        self.last_x = None

        if self.zoom_cooldown > 0:
            self.zoom_cooldown -= 1

    def handle_one_hand(self, hand):
        """Handle highlighting, scrolling, and page-change gestures."""
        self.two_hand_frames = 0
        self.last_zoom_distance = None

        gesture = detect_gesture(hand)
        self.handle_click(gesture)
        self.handle_scroll(gesture, hand)
        self.handle_page_swipe(gesture, hand)

    def handle_click(self, gesture):
        if gesture == "FIST":
            if self.last_click_gesture != "FIST":
                self.viewer.get_word_at_cursor()
            self.last_click_gesture = "FIST"
        else:
            self.last_click_gesture = None

    def handle_scroll(self, gesture, hand):
        if gesture == "PINCH":
            y = hand[8].y

            if self.last_y is not None:
                movement = y - self.last_y

                if movement < -0.01:
                    self.viewer.scroll(-3)
                elif movement > 0.01:
                    self.viewer.scroll(3)

            self.last_y = y
        else:
            self.last_y = None

    def handle_page_swipe(self, gesture, hand):
        """Change page when a ✌️ hand moves left or right."""
        if gesture == "VICTORY":
            x = hand[8].x

            if self.last_x is not None and self.page_cooldown == 0:
                movement = x - self.last_x

                if movement > 0.1:
                    self.viewer.next_page()
                    self.page_cooldown = 30
                    self.last_x = None
                elif movement < -0.15:
                    self.viewer.previous_page()
                    self.page_cooldown = 30
                    self.last_x = None

            if self.page_cooldown > 0:
                self.page_cooldown -= 1

            if self.last_x is None:
                self.last_x = x
        else:
            self.last_x = None

    def reset_no_hands(self):
        """Reset transient gesture state after hands leave the frame."""
        self.two_hand_frames = 0
        self.last_x = None
        self.last_y = None
        self.last_zoom_distance = None
