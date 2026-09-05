import cv2
import csv
import os
import math
import mediapipe as mp
import numpy as np

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

REFERENCE_FOLDER = "reference_gestures"

def load_references():
    """Load reference CSV files for all gesture folders inside reference_gestures."""
    reference_dict = {}

    if not os.path.exists(REFERENCE_FOLDER):
        print(f"Error: Reference folder '{REFERENCE_FOLDER}' does not exist.")
        return reference_dict

    for gesture_label in os.listdir(REFERENCE_FOLDER):
        gesture_folder = os.path.join(REFERENCE_FOLDER, gesture_label)

        if not os.path.isdir(gesture_folder):
            continue

        gesture_list = []
        for filename in os.listdir(gesture_folder):
            if not filename.endswith(".csv"):
                continue
            filepath = os.path.join(gesture_folder, filename)

            with open(filepath, newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    gesture_list.append(list(map(float, row)))

        if gesture_list:
            reference_dict[gesture_label.upper()] = gesture_list

    return reference_dict

reference_dict = load_references()


def extract_landmarks(hand_landmarks):
    """Normalize landmarks so accuracy depends on hand shape, not screen position."""
    wrist = hand_landmarks.landmark[0]
    middle_mcp = hand_landmarks.landmark[9]

    scale = ((middle_mcp.x - wrist.x) ** 2 + (middle_mcp.y - wrist.y) ** 2) ** 0.5
    if scale == 0:
        scale = 1

    landmark_data = []
    for lm in hand_landmarks.landmark:
        landmark_data.append((lm.x - wrist.x) / scale if scale != 0 else 0)
        landmark_data.append((lm.y - wrist.y) / scale if scale != 0 else 0)

    return landmark_data


def calculate_accuracy(current_landmarks, reference_landmarks):
    """Compare only major finger shape points, not every joint."""
    important_points = [
        0, 2, 3, 4, 5, 6, 7, 8, 
        9, 10, 11, 12, 13, 14, 15, 16, 
        17, 18, 19, 20
    ]
    
    total_distance = 0

    for point in important_points:
        x_index = point * 2
        y_index = point * 2 + 1

        dx = abs(current_landmarks[x_index] - reference_landmarks[x_index])
        dy = abs(current_landmarks[y_index] - reference_landmarks[y_index])
        distance = dx + dy

        if distance < 0.25:
            distance = 0

        total_distance += distance

    accuracy = max(0, 100 - int(total_distance * 15))
    return accuracy


def calculate_angle(a, b, c):
    """Calculate angle ABC (in degrees) given three points."""
    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )
    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle
    return abs(angle)


def get_point(landmarks, index):
    """Get (x, y) coordinates of a landmark."""
    return (landmarks[index * 2], landmarks[index * 2 + 1])


def is_finger_extended(landmarks, tip, base):
    """Returns True if the finger is extended."""
    tip_y = landmarks[tip * 2 + 1]
    base_y = landmarks[base * 2 + 1]
    return abs(tip_y - base_y) > 0.5


def is_finger_folded(landmarks, tip, base):
    """Returns True if the finger is folded."""
    return not is_finger_extended(landmarks, tip, base)


def is_finger_straight(landmarks, mcp, pip, dip, tip):
    mcp_x, mcp_y = landmarks[mcp * 2], landmarks[mcp * 2 + 1]
    pip_x, pip_y = landmarks[pip * 2], landmarks[pip * 2 + 1]
    dip_x, dip_y = landmarks[dip * 2], landmarks[dip * 2 + 1]

    v1 = (mcp_x - pip_x, mcp_y - pip_y)
    v2 = (dip_x - pip_x, dip_y - pip_y)

    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = (v1[0] ** 2 + v1[1] ** 2) ** 0.5
    mag2 = (v2[0] ** 2 + v2[1] ** 2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return False

    cos_angle = max(-1, min(1, dot / (mag1 * mag2)))
    angle = math.degrees(math.acos(cos_angle))
    return angle > 150


def is_thumb_folded(landmarks):
    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]
    index_base_x = landmarks[5 * 2]
    index_base_y = landmarks[5 * 2 + 1]

    distance = ((thumb_tip_x - index_base_x) ** 2 + (thumb_tip_y - index_base_y) ** 2) ** 0.5
    return distance < 0.3


def is_thumb_beside_fingers(landmarks):
    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]
    index_base_x = landmarks[5 * 2]
    index_base_y = landmarks[5 * 2 + 1]

    distance = ((thumb_tip_x - index_base_x) ** 2 + (thumb_tip_y - index_base_y) ** 2) ** 0.5
    return distance < 0.45


def is_thumb_extended(landmarks):
    thumb_mcp_x, thumb_mcp_y = landmarks[2 * 2], landmarks[2 * 2 + 1]
    thumb_ip_x, thumb_ip_y = landmarks[3 * 2], landmarks[3 * 2 + 1]
    thumb_tip_x, thumb_tip_y = landmarks[4 * 2], landmarks[4 * 2 + 1]

    v1 = (thumb_mcp_x - thumb_ip_x, thumb_mcp_y - thumb_ip_y)
    v2 = (thumb_tip_x - thumb_ip_x, thumb_tip_y - thumb_ip_y)

    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = (v1[0] ** 2 + v1[1] ** 2) ** 0.5
    mag2 = (v2[0] ** 2 + v2[1] ** 2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return False

    cos_angle = max(-1, min(1, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cos_angle)) > 150


def is_thumb_touching_index(landmarks):
    thumb_tip_x, thumb_tip_y = landmarks[4 * 2], landmarks[4 * 2 + 1]
    index_tip_x, index_tip_y = landmarks[8 * 2], landmarks[8 * 2 + 1]

    distance = ((thumb_tip_x - index_tip_x) ** 2 + (thumb_tip_y - index_tip_y) ** 2) ** 0.5
    return distance < 0.35


def is_finger_curved(landmarks, mcp, pip, dip, tip):
    pip_angle = calculate_angle(get_point(landmarks, mcp), get_point(landmarks, pip), get_point(landmarks, dip))
    dip_angle = calculate_angle(get_point(landmarks, pip), get_point(landmarks, dip), get_point(landmarks, tip))
    return pip_angle < 175 and dip_angle < 175


def finger_difference(current, reference, points):
    total = 0
    for point in points:
        x, y = point * 2, point * 2 + 1
        total += abs(current[x] - reference[x]) + abs(current[y] - reference[y])
    return total


def check_rules(gesture_label, landmarks, reference_landmarks=None):
    """Check if the gesture follows basic rules for each gesture."""
    if gesture_label == "A":
        return (
            is_finger_folded(landmarks, 8, 5) and
            is_finger_folded(landmarks, 12, 9) and
            is_finger_folded(landmarks, 16, 13) and
            is_finger_folded(landmarks, 20, 17) and
            is_thumb_beside_fingers(landmarks)
        )
    elif gesture_label == "B":
        return (
            is_finger_extended(landmarks, 8, 5) and
            is_finger_extended(landmarks, 12, 9) and
            is_finger_extended(landmarks, 16, 13) and
            is_finger_extended(landmarks, 20, 17) and
            is_thumb_folded(landmarks)
        )
    elif gesture_label == "C":
        return (
            is_finger_curved(landmarks, 5, 6, 7, 8) and
            is_finger_curved(landmarks, 9, 10, 11, 12) and
            is_finger_curved(landmarks, 13, 14, 15, 16) and
            is_finger_curved(landmarks, 17, 18, 19, 20)
        )
    elif gesture_label == "D":
        return (
            is_finger_extended(landmarks, 8, 5) and
            is_finger_folded(landmarks, 12, 9) and
            is_finger_folded(landmarks, 16, 13) and
            is_finger_folded(landmarks, 20, 17) and
            is_thumb_folded(landmarks)
        )
    elif gesture_label == "E":
        return (
            is_finger_folded(landmarks, 8, 5) and
            is_finger_folded(landmarks, 12, 9) and
            is_finger_folded(landmarks, 16, 13) and
            is_finger_folded(landmarks, 20, 17) and
            is_thumb_folded(landmarks)  
        )
    elif gesture_label == "F":
        return (
            is_thumb_touching_index(landmarks) and
            is_finger_extended(landmarks, 12, 9) and
            is_finger_extended(landmarks, 16, 13) and
            is_finger_extended(landmarks, 20, 17)
        )
    elif gesture_label == "G":
        return (
            is_finger_straight(landmarks, 5, 6, 7, 8) and
            is_thumb_extended(landmarks) and
            is_finger_folded(landmarks, 12, 9) and
            is_finger_folded(landmarks, 16, 13) and
            is_finger_folded(landmarks, 20, 17)
        )
    return True


def generate_rule_feedback(gesture_label, landmarks, best_landmarks):
    """Generate basic rule-based feedback for each gesture."""
    feedback = []

    if gesture_label == "A":
        if not is_finger_folded(landmarks, 8, 5): feedback.append("Fold your index finger.")
        if not is_finger_folded(landmarks, 12, 9): feedback.append("Fold your middle finger.")
        if not is_finger_folded(landmarks, 16, 13): feedback.append("Fold your ring finger.")
        if not is_finger_folded(landmarks, 20, 17): feedback.append("Fold your little finger.")
        if not is_thumb_beside_fingers(landmarks): feedback.append("Keep your thumb beside your fingers.")

    elif gesture_label == "B":
        if not is_finger_extended(landmarks, 8, 5): feedback.append("Straighten your index finger.")
        if not is_finger_extended(landmarks, 12, 9): feedback.append("Straighten your middle finger.")
        if not is_finger_extended(landmarks, 16, 13): feedback.append("Straighten your ring finger.")
        if not is_finger_extended(landmarks, 20, 17): feedback.append("Straighten your little finger.")
        if not is_thumb_folded(landmarks): feedback.append("Fold your thumb across your palm.")

    elif gesture_label == "C" and best_landmarks:
        THRESHOLD = 0.25
        if (finger_difference(landmarks, best_landmarks, [5,6,7,8]) > THRESHOLD or
            finger_difference(landmarks, best_landmarks, [9,10,11,12]) > THRESHOLD or
            finger_difference(landmarks, best_landmarks, [13,14,15,16]) > THRESHOLD or
            finger_difference(landmarks, best_landmarks, [17,18,19,20]) > THRESHOLD):
            feedback.append("Curve your fingers to form a C shape.")
        if finger_difference(landmarks, best_landmarks, [2,3,4]) > THRESHOLD:
            feedback.append("Curve your thumb to form a C shape.")

    elif gesture_label == "D":
        if not is_finger_extended(landmarks, 8, 5): feedback.append("Straighten your index finger.")
        if not is_finger_folded(landmarks, 12, 9): feedback.append("Fold your middle finger.")
        if not is_finger_folded(landmarks, 16, 13): feedback.append("Fold your ring finger.")
        if not is_finger_folded(landmarks, 20, 17): feedback.append("Fold your little finger.")
        if not is_thumb_folded(landmarks): feedback.append("Fold your thumb.")

    elif gesture_label == "E":
        if not is_finger_folded(landmarks, 8, 5): feedback.append("Curl your index finger.")
        if not is_finger_folded(landmarks, 12, 9): feedback.append("Curl your middle finger.")
        if not is_finger_folded(landmarks, 16, 13): feedback.append("Curl your ring finger.")
        if not is_finger_folded(landmarks, 20, 17): feedback.append("Curl your little finger.")
        if not is_thumb_folded(landmarks): feedback.append("Fold your thumb toward your palm.")

    elif gesture_label == "F":
        if not is_thumb_touching_index(landmarks): feedback.append("Touch your thumb to your index finger.")
        if not is_finger_extended(landmarks, 12, 9): feedback.append("Straighten your middle finger.")
        if not is_finger_extended(landmarks, 16, 13): feedback.append("Straighten your ring finger.")
        if not is_finger_extended(landmarks, 20, 17): feedback.append("Straighten your little finger.")

    elif gesture_label == "G":
        if not is_finger_straight(landmarks, 5, 6, 7, 8): feedback.append("Straighten your index finger.")
        if not is_thumb_extended(landmarks): feedback.append("Straighten and extend your thumb.")
        if not is_finger_folded(landmarks, 12, 9): feedback.append("Fold your middle finger.")
        if not is_finger_folded(landmarks, 16, 13): feedback.append("Fold your ring finger.")
        if not is_finger_folded(landmarks, 20, 17): feedback.append("Fold your little finger.")

    return feedback


def find_best_reference(current_landmarks, target_gesture):
    """Compare current gesture with target gesture references and return best match."""
    target_key = (target_gesture or "A").strip().upper()
    if target_key not in reference_dict or not reference_dict[target_key]:
        return 0, []

    best_accuracy = -1
    best_landmarks = []

    for reference_landmarks in reference_dict[target_key]:
        if len(reference_landmarks) != 42:
            continue

        accuracy = calculate_accuracy(current_landmarks, reference_landmarks)
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_landmarks = reference_landmarks.copy()

    return best_accuracy, best_landmarks


def recognize_gesture(frame, target_gesture="A"):
    """Flask backend entry point for single-frame recognition."""
    target_key = (target_gesture or "A").strip().upper()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if not results.multi_hand_landmarks:
        return {
            "gesture": target_gesture,
            "accuracy": 0,
            "status": "No Hand",
            "feedback": ["Please show your hand to the camera."]
        }

    hand_landmarks = results.multi_hand_landmarks[0]
    current_landmarks = extract_landmarks(hand_landmarks)

    best_accuracy, best_landmarks = find_best_reference(current_landmarks, target_key)
    final_accuracy = max(0, best_accuracy)

    rules_ok = check_rules(target_key, current_landmarks, best_landmarks)

    correct_threshold = 55 if target_key == "C" else 90

    if final_accuracy >= correct_threshold and rules_ok:
        status = "Correct"
        feedback = ["Great! Your gesture is accurate."]
    elif final_accuracy >= 75:
        status = "Almost There"
        feedback = generate_rule_feedback(target_key, current_landmarks, best_landmarks)
    else:
        status = "Try Again"
        feedback = generate_rule_feedback(target_key, current_landmarks, best_landmarks)

    return {
        "gesture": target_gesture,
        "accuracy": final_accuracy,
        "status": status,
        "feedback": feedback if feedback else ["Adjust your hand position according to the guide."]
    }