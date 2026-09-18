import math


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def detect_gesture(hand):
    # Thumb tip ↔ index tip
    pinch_distance = distance(hand[4], hand[8])

    if pinch_distance < 0.03:
        return "PINCH"

    # Finger states
    index = hand[8].y < hand[6].y
    middle = hand[12].y < hand[10].y
    ring = hand[16].y < hand[14].y
    pinky = hand[20].y < hand[18].y

    if index and middle and ring and pinky:
        return "OPEN_PALM"

    # Index and middle fingers extended: ✌️
    if index and middle and not ring and not pinky:
        return "VICTORY"

    if index and not middle and not ring and not pinky:
        return "POINT"

    if not index and not middle and not ring and not pinky:
        return "FIST"

    return "UNKNOWN"
