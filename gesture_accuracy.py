import cv2
import mediapipe as mp
import csv
import os
import time
import math
import numpy as np

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils


# Get target gesture
gesture_label = input("Enter target gesture : ")

reference_folder = f"reference_gestures/{gesture_label}"

reference_png = cv2.imread(
    f"reference_gestures/reference_images/{gesture_label}.png",
    cv2.IMREAD_UNCHANGED
)

# Load reference csv files
reference_list = []

if not os.path.exists(reference_folder):
    print(f"Error: Reference folder '{reference_folder}' does not exist.")
    exit(1)

for filename in os.listdir(reference_folder):
    filepath = os.path.join(reference_folder, filename)

    with open(filepath, newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            reference_list.append(list(map(float, row)))

if len(reference_list) == 0:
    print(f"Error: No reference data found in '{reference_folder}'.")
    exit(1)


# Camera selection
print("0 = DroidCam")
print("1 = Laptop Webcam")
print("2 = Logitech Webcam")

camera_choice = int(input("Choose camera: "))
cap = cv2.VideoCapture(camera_choice)

if not cap.isOpened():
    print(f"Error: Unable to open camera index {camera_choice}.")
    exit(1)


# Helper functions
def extract_landmarks(hand_landmarks):
    """Normalize landmarks so accuracy depends on hand shape, not screen position."""
    wrist = hand_landmarks.landmark[0]

    # Use middle finger MCP joint as reference for normalization
    middle_mcp = hand_landmarks.landmark[9]

    scale = ((middle_mcp.x - wrist.x) ** 2 + (middle_mcp.y - wrist.y) ** 2) ** 0.5

    if scale == 0:
        scale = 1  # Prevent division by zero
    
    landmark_data = []

    for lm in hand_landmarks.landmark:
        landmark_data.append((lm.x - wrist.x) / scale if scale != 0 else 0)
        landmark_data.append((lm.y - wrist.y) / scale if scale != 0 else 0)

    return landmark_data

def get_hand_box(hand_landmarks, img_width, img_height):
    """Get rectangle boundary around the detected hand."""
    x_list = []
    y_list = []

    for lm in hand_landmarks.landmark:
        x_list.append(int(lm.x * img_width))
        y_list.append(int(lm.y * img_height))

    xmin = min(x_list)
    xmax = max(x_list)
    ymin = min(y_list)
    ymax = max(y_list)

    return xmin, ymin, xmax, ymax

def calculate_accuracy(current_landmarks, reference_landmarks):
    """Compare only major finger shape points, not every joint."""
    
    # Important landmark indexes only
    important_points = [
        # Wrist
        0,

        # Thumb
        2, 3, 4,

        # Index
        5, 6, 7, 8,
        
        # Middle
        9, 10, 11, 12,
        
        # Ring
        13, 14, 15, 16,
        
        # Pinky
        17, 18, 19, 20,
    ]
    
    total_distance = 0

    for point in important_points:
        x_index = point * 2
        y_index = point * 2 + 1

        dx = abs(current_landmarks[x_index] - reference_landmarks[x_index])
        dy = abs(current_landmarks[y_index] - reference_landmarks[y_index])
        distance = dx + dy

        # More relaxed tolerance
        if distance < 0.25:
            distance = 0

        total_distance += distance

    # More forgiving accuracy calculation
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

    return not is_finger_extended(
        landmarks,
        tip,
        base
    )

def is_finger_straight(landmarks, mcp, pip, dip, tip):

    # Get points
    mcp_x = landmarks[mcp * 2]
    mcp_y = landmarks[mcp * 2 + 1]

    pip_x = landmarks[pip * 2]
    pip_y = landmarks[pip * 2 + 1]

    dip_x = landmarks[dip * 2]
    dip_y = landmarks[dip * 2 + 1]

    tip_x = landmarks[tip * 2]
    tip_y = landmarks[tip * 2 + 1]

    # Calculate angle at PIP
    v1 = (
        mcp_x - pip_x,
        mcp_y - pip_y
    )

    v2 = (
        dip_x - pip_x,
        dip_y - pip_y
    )

    dot = v1[0] * v2[0] + v1[1] * v2[1]

    mag1 = (v1[0] ** 2 + v1[1] ** 2) ** 0.5
    mag2 = (v2[0] ** 2 + v2[1] ** 2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return False

    cos_angle = dot / (mag1 * mag2)

    cos_angle = max(-1, min(1, cos_angle))

    angle = math.degrees(math.acos(cos_angle))

    return angle > 150

def is_thumb_folded(landmarks):

    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]

    index_base_x = landmarks[5 * 2]
    index_base_y = landmarks[5 * 2 + 1]

    distance = (
        (thumb_tip_x - index_base_x) ** 2 +
        (thumb_tip_y - index_base_y) ** 2
    ) ** 0.5

    return distance < 0.3 #or 1.0

def is_thumb_beside_fingers(landmarks):

    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]

    index_base_x = landmarks[5 * 2]
    index_base_y = landmarks[5 * 2 + 1]

    distance = (
        (thumb_tip_x - index_base_x) ** 2 +
        (thumb_tip_y - index_base_y) ** 2
    ) ** 0.5

    return distance < 0.45 #smaller = 0.30, lower = 0.45

def is_thumb_across_fingers(landmarks):

    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]

    index_base_x = landmarks[5 * 2]
    index_base_y = landmarks[5 * 2 + 1]

    distance = (
        (thumb_tip_x - index_base_x) ** 2 +
        (thumb_tip_y - index_base_y) ** 2
    ) ** 0.5

    return distance < 0.65 #can adjust

def is_thumb_curved(landmarks):
    # Thumb:
    # 2 = MCP
    # 3 = IP
    # 4 = Tip

    thumb_mcp_x = landmarks[2 * 2]
    thumb_mcp_y = landmarks[2 * 2 + 1]

    thumb_ip_x = landmarks[3 * 2]
    thumb_ip_y = landmarks[3 * 2 + 1]

    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]

    # Distance from MCP to TIP
    mcp_tip_distance = (
        (thumb_tip_x - thumb_mcp_x) ** 2 +
        (thumb_tip_y - thumb_mcp_y) ** 2
    ) ** 0.5

    # Distance from MCP to IP
    mcp_ip_distance = (
        (thumb_ip_x - thumb_mcp_x) ** 2 +
        (thumb_ip_y - thumb_mcp_y) ** 2
    ) ** 0.5

    return (
        mcp_tip_distance
        < mcp_ip_distance * 2.0
    )

def is_thumb_extended(landmarks):

    thumb_mcp_x = landmarks[2 * 2]
    thumb_mcp_y = landmarks[2 * 2 + 1]

    thumb_ip_x = landmarks[3 * 2]
    thumb_ip_y = landmarks[3 * 2 + 1]

    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]

    # Check whether thumb is relatively straight
    v1 = (
        thumb_mcp_x - thumb_ip_x,
        thumb_mcp_y - thumb_ip_y
    )

    v2 = (
        thumb_tip_x - thumb_ip_x,
        thumb_tip_y - thumb_ip_y
    )

    dot = v1[0] * v2[0] + v1[1] * v2[1]

    mag1 = (v1[0] ** 2 + v1[1] ** 2) ** 0.5
    mag2 = (v2[0] ** 2 + v2[1] ** 2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return False

    cos_angle = dot / (mag1 * mag2)
    cos_angle = max(-1, min(1, cos_angle))

    angle = math.degrees(math.acos(cos_angle))

    return angle > 150

def is_thumb_touching_index(landmarks):

    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]

    index_tip_x = landmarks[8 * 2]
    index_tip_y = landmarks[8 * 2 + 1]

    distance = (
        (thumb_tip_x - index_tip_x) ** 2 +
        (thumb_tip_y - index_tip_y) ** 2
    ) ** 0.5

    return distance < 0.35

def is_finger_curved(landmarks, mcp, pip, dip, tip):

    mcp_point = get_point(landmarks, mcp)
    pip_point = get_point(landmarks, pip)
    dip_point = get_point(landmarks, dip)
    tip_point = get_point(landmarks, tip)

    pip_angle = calculate_angle(mcp_point, pip_point, dip_point)
    dip_angle = calculate_angle(pip_point, dip_point, tip_point)

    # Debug: print the angles
    print(
        f"Finger {tip}: "
        f"PIP = {pip_angle:.1f}, "
        f"DIP = {dip_angle:.1f}"
    )

    # Lower angle = more bent
    return pip_angle < 175 and dip_angle < 175

def finger_difference(
    current,
    reference,
    points
):
    total = 0

    for point in points:

        x = point * 2
        y = point * 2 + 1

        dx = abs(
            current[x] -
            reference[x]
        )

        dy = abs(
            current[y] -
            reference[y]
        )

        total += dx + dy

    return total

def check_rules(gesture_label, landmarks, reference_landmarks=None):
    """Check if the gesture follows basic rules for each gesture."""
    
    rules_ok = True

    if gesture_label == "A":
        rules_ok = (
            is_finger_folded(landmarks, 8, 5) and
            is_finger_folded(landmarks, 12, 9) and
            is_finger_folded(landmarks, 16, 13) and
            is_finger_folded(landmarks, 20, 17) and
            is_thumb_beside_fingers(landmarks)
        )

    elif gesture_label == "B":
        rules_ok = (
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
        rules_ok = (
            is_finger_extended(landmarks, 8, 5) and
            is_finger_folded(landmarks, 12, 9) and
            is_finger_folded(landmarks, 16, 13) and
            is_finger_folded(landmarks, 20, 17) and
            is_thumb_folded(landmarks)
        )

    elif gesture_label == "E":
        rules_ok = (
            is_finger_folded(landmarks, 8, 5) and
            is_finger_folded(landmarks, 12, 9) and
            is_finger_folded(landmarks, 16, 13) and
            is_finger_folded(landmarks, 20, 17) and
            is_thumb_folded(landmarks)  
        )

    elif gesture_label  == "F":
        rules_ok = (
            is_thumb_touching_index(landmarks) and
            is_finger_extended(landmarks, 12, 9) and
            is_finger_extended(landmarks, 16, 13) and
            is_finger_extended(landmarks, 20, 17)
        )

    elif gesture_label == "G":
        rules_ok = (
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

    thumb_ok = True
    fingers_ok = True
    
    # Thumb
    thumb_tip_x = landmarks[4 * 2]
    thumb_tip_y = landmarks[4 * 2 + 1]

    # Index finger
    index_base_x = landmarks[5 * 2]
    index_base_y = landmarks[5 * 2 + 1]
    index_tip_x = landmarks[8 * 2]
    index_tip_y = landmarks[8 * 2 + 1]

    # Middle finger
    middle_base_y = landmarks[9 * 2 + 1]
    middle_tip_y = landmarks[12 * 2 + 1]

    # Ring finger
    ring_base_y = landmarks[13 * 2 + 1]
    ring_tip_y = landmarks[16 * 2 + 1]

    # Pinky
    pinky_base_y = landmarks[17 * 2 + 1]
    pinky_tip_y = landmarks[20 * 2 + 1]

    # Distance from fingertip to finger base
    index_open = abs(index_tip_y - index_base_y)
    middle_open = abs(middle_tip_y - middle_base_y)
    ring_open = abs(ring_tip_y - ring_base_y)
    pinky_open = abs(pinky_tip_y - pinky_base_y)

    # Thumb distance from index base
    thumb_distance = abs(thumb_tip_x - index_base_x)

    rules_ok = True

    if gesture_label == "A":

        if not is_finger_folded(landmarks, 8, 5):
            feedback.append(
                "Fold your index finger."
            )

        if not is_finger_folded(landmarks, 12, 9):
            feedback.append(
                "Fold your middle finger."
            )

        if not is_finger_folded(landmarks, 16, 13):
            feedback.append(
                "Fold your ring finger."
            )

        if not is_finger_folded(landmarks, 20, 17):
            feedback.append(
                "Fold your little finger."
            )

        if not is_thumb_beside_fingers(landmarks):
            feedback.append(
                "Keep your thumb beside your fingers."
            )

    elif gesture_label == "B":

        if not is_finger_extended(landmarks, 8, 5):
            feedback.append(
                "Straighten your index finger."
            )

        if not is_finger_extended(landmarks, 12, 9):
           feedback.append(
               "Straighten your middle finger."
            )

        if not is_finger_extended(landmarks, 16, 13):
            feedback.append(
                "Straighten your ring finger."
            )

        if not is_finger_extended(landmarks, 20, 17):
            feedback.append(
                "Straighten your little finger."
            )

        if not is_thumb_folded(landmarks):
            feedback.append(
                "Fold your thumb across your palm."
            )

    elif gesture_label == "C":

        index_diff = finger_difference(
            landmarks,
            best_landmarks,
            [5,6,7,8]
        )

        middle_diff = finger_difference(
            landmarks,
            best_landmarks,
            [9,10,11,12]
        )

        ring_diff = finger_difference(
            landmarks,
            best_landmarks,
            [13,14,15,16]
        )

        little_diff = finger_difference(
            landmarks,
            best_landmarks,
            [17,18,19,20]
        )

        thumb_diff = finger_difference(
            landmarks,
            best_landmarks,
            [2,3,4]
        )

        THRESHOLD = 0.25
        
        if (
            index_diff > THRESHOLD or
            middle_diff > THRESHOLD or
            ring_diff > THRESHOLD or
            little_diff > THRESHOLD
        ):
            feedback.append(
                "Curve your fingers to form a C shape."
            )
        
        if thumb_diff > THRESHOLD:
            feedback.append(
                "Curve your thumb to form a C shape."
            )

    elif gesture_label == "D":

        if not is_finger_extended(landmarks, 8, 5):
            feedback.append(
                "Straighten your index finger."
            )

        if not is_finger_folded(landmarks, 12, 9):
            feedback.append(
                "Fold your middle finger."
            )

        if not is_finger_folded(landmarks, 16, 13):
            feedback.append(
                "Fold your ring finger."
            )

        if not is_finger_folded(landmarks, 20, 17):
            feedback.append(
                "Fold your little finger."
            )

        if not is_thumb_folded(landmarks):
            feedback.append(
                "Fold your thumb."
            )

    elif gesture_label == "E":
        if not is_finger_folded(landmarks, 8, 5):
            feedback.append(
                "Curl your index finger."
            )

        if not is_finger_folded(landmarks, 12, 9):
            feedback.append(
                "Curl your middle finger."
            )

        if not is_finger_folded(landmarks, 16, 13):
            feedback.append(
                "Curl your ring finger."
            )

        if not is_finger_folded(landmarks, 20, 17):
            feedback.append(
                "Curl your little finger."
            )

        if not is_thumb_folded(landmarks):
            feedback.append(
                "Fold your thumb toward your palm."
            )

    elif gesture_label == "F":

        if not is_thumb_touching_index(landmarks):
            feedback.append(
                "Touch your thumb to your index finger."
            )

        if not is_finger_extended(landmarks, 12, 9):
            feedback.append(
                "Straighten your middle finger."
            )

        if not is_finger_extended(landmarks, 16, 13):
            feedback.append(
                "Straighten your ring finger."
            )

        if not is_finger_extended(landmarks, 20, 17):
            feedback.append(
                "Straighten your little finger."
            )

    elif gesture_label == "G":

        if not is_finger_straight(landmarks, 5, 6, 7, 8):
            feedback.append(
                "Straighten your index finger."
            )

        if not is_thumb_extended(landmarks):
            feedback.append(
                "Straighten and extend your thumb."
            )

        if not is_finger_folded(landmarks, 12, 9):
            feedback.append(
                "Fold your middle finger."
            )

        if not is_finger_folded(landmarks, 16, 13):
            feedback.append(
                "Fold your ring finger."
            )

        if not is_finger_folded(landmarks, 20, 17):
            feedback.append(
                "Fold your little finger."
            )      

    return feedback

def find_best_reference(current_landmarks, reference_list):
    """Compare current gesture with all references and return the best match."""
    best_accuracy = -1
    best_landmarks = []

    #print(type(reference_list))
    #print(len(reference_list))
    #print(reference_list[:3])

    for reference in reference_list:
        # New reference CSV contains ONLY 42 normalized landmark values
        reference_landmarks = reference

        #print(type(reference_landmarks))
        #print(reference_landmarks)

        # Safety check
        if len(reference_landmarks) != 42:
            print(
                "Warning: Reference CSV "
                f"contains {len(reference_landmarks)} values."
            )
            print(
                "Expected exactly 42 values."
            )
            continue

        # Compare camera landmarks with saved reference landmarks
        accuracy = calculate_accuracy(current_landmarks, reference_landmarks)

        # Keep BEST matching reference
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_landmarks = (reference_landmarks.copy())

    return (best_accuracy, best_landmarks)

def show_reference_image(img, reference_png):
    """Display transparent PNG guide."""
    if reference_png is None:
        return
    
    guide = cv2.resize(
        reference_png,
        (250, 250)
    )

    h,w = guide.shape[:2]

    x_offset = 20
    y_offset = 140

    # PNG with transparency
    if guide.shape[2] == 4:
        alpha = (guide[:, :, 3] / 255.0) * 0.3

        for c in range(3):
            img[y_offset:y_offset+h, x_offset:x_offset+w, c] = (
                alpha * guide[:, :, c] +
                (1 - alpha) * img[y_offset:y_offset+h, x_offset:x_offset+w, c]
            )
    else:
        opacity = 0.3
        img[y_offset:y_offset+h, x_offset:x_offset+w] = (
            opacity * guide +
            (1 - opacity) * img[y_offset:y_offset+h, x_offset:x_offset+w]
        )

def draw_dotted_line(img, pt1, pt2, color, thickness=2, gap=10):
    """Draw dotted line between two points."""
    x1, y1 = pt1
    x2, y2 = pt2

    distance = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)

    for i in range(0, distance, gap):
        t = i / distance
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)

        cv2.circle(
            img,
            (x, y),
            thickness,
            color, 
            -1
        )

def draw_dotted_hand_landmarks(img, hand_landmarks, color=(255, 255, 255)):
    """Draw dotted skeleton for reference hand."""
    h, w, = img.shape[:2]

    points = []

    for lm in hand_landmarks.landmark:
        x = int(lm.x * w)
        y = int(lm.y * h)
        points.append((x, y))
    
    for connection in mp_hands.HAND_CONNECTIONS:
        start = connection[0]
        end = connection[1]

        draw_dotted_line(
            img,
            points[start],
            points[end],
            color,
            thickness=2,
            gap=8
        )

    for point in points:
        cv2.circle(img, point, 4, (255, 0, 0), -1)
        
def draw_skeleton_on_reference(reference_png, reference_landmarks):
    """Draw saved reference landmarks directly onto the reference PNG."""
    """No MediaPipe detection is performed here."""
    
    if reference_png is None:
        print("Warning: Reference PNG not found.")
        return None
    
    if not reference_landmarks:
        print(
            "Warning: No reference landmarks."
        )
        return reference_png

    # Resize for consistency
    # reference_png = cv2.imread(reference_png)

    # Keep original aspect ratio
    target_height = 250

    original_h, original_w = (reference_png.shape[:2])

    scale_display = (target_height / original_h)
    target_width = int(original_w * scale_display)

    guide =cv2.resize(
        reference_png,
        (
            target_width,
            target_height
        ),
        interpolation=cv2.INTER_AREA
    )

    # Handle alpha channel
    if (
        len(guide.shape) == 3
        and guide.shape[2] == 4
    ):
        bgr_guide = (guide[:, :, :3].copy())

    else:
        bgr_guide = guide.copy()

    # Get reference normalization scale
    # Landmark 0 = wrist
    wrist_x = reference_landmarks[0]
    wrist_y = reference_landmarks[1]

    # Landmark 9 = middle MCP
    middle_mcp_x = reference_landmarks[18]
    middle_mcp_y = reference_landmarks[19]

    # Convert normalized landmarks back to image corrdinates
    points = []

    for i in range(21):
        x_normalized = (reference_landmarks[i * 2])
        y_normalized = (reference_landmarks[i * 2 + 1])

    # Convert normalized coordinates back to coordinates relative to wrist
    x_relative = (
        x_normalized * ((middle_mcp_x - wrist_x) ** 2 + (middle_mcp_y - wrist_y) ** 2) ** 0.5
    )

    y_relative = (
        y_normalized * ((middle_mcp_x - wrist_x) ** 2 + (middle_mcp_y - wrist_y) ** 2) ** 0.5
    )


# Main program loop
# accuracy_history = []

# best_score_display = 0

# Capture and hold logic
hold_start_time = None
capture_buffer = []
final_accuracy = None
final_status = "Waiting"
final_feedback = []
capture_done = False
best_box = (0, 0, 0, 0)

HOLD_DURATION = 10  # seconds

while True:
    success, img = cap.read()

    if not success or img is None:
        print("Warning: Failed to read frame from camera.")
        continue

    # Optional mirror mode
    # img = cv2.flip(img, 1)

    h, w, c = img.shape

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            # Draw live hand skeleton
            mp_draw.draw_landmarks(
                img,
                handLms,
                mp_hands.HAND_CONNECTIONS
            )

            # Extract current hand data
            current_landmarks = extract_landmarks(handLms)
            xmin, ymin, xmax, ymax = get_hand_box(handLms, w, h)

            cv2.rectangle(
                img,
                (xmin, ymin),
                (xmax, ymax),
                (255, 0, 0),
                2
            )

            if not capture_done:
                capture_buffer.append(current_landmarks)

                if len(capture_buffer) > 30:
                    capture_buffer.pop(0)

                if hold_start_time is None:
                    hold_start_time = time.time()
                    
                elapsed = time.time() - hold_start_time
                remaining = max(0, int(HOLD_DURATION - elapsed))

                cv2.putText(
                    img,
                    f"Hold steady for {remaining}s",
                    (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

                if elapsed >= HOLD_DURATION and len(capture_buffer) > 0:
                    averaged_landmarks = []

                    for i in range(len(capture_buffer[0])):
                        avg_value = sum(frame[i] for frame in capture_buffer) / len(capture_buffer)
                        averaged_landmarks.append(avg_value)

                    best_accuracy, best_landmarks = find_best_reference(
                        averaged_landmarks,
                        reference_list
                    )

                    final_accuracy = best_accuracy

                    rules_ok = check_rules(
                        gesture_label,
                        averaged_landmarks,
                        best_landmarks
                    )

                    final_accuracy = max(0, final_accuracy)

                    if gesture_label == "C":
                        correct_threshold = 55
                    else:
                        correct_threshold = 90

                    #if final_accuracy >= 90 and rules_ok:
                        #final_feedback = ["Great! Your gesture is accurate."]
                        #final_status = "Correct"
                        #status_color = (0, 255, 0)

                    if final_accuracy >= correct_threshold and rules_ok:
                        final_feedback = ["Great! Your gesture is accurate."]
                        final_status = "Correct"
                        status_color = (0, 255, 0)

                    elif final_accuracy >= 75:
                        final_feedback = generate_rule_feedback(
                            gesture_label,
                            averaged_landmarks,
                            best_landmarks
                        )

                        final_status = "Almost There"
                        status_color = (0, 255, 255)

                    else:
                        final_feedback = generate_rule_feedback(
                            gesture_label,
                            averaged_landmarks,
                            best_landmarks
                        )

                        final_status = "Try Again"
                        status_color = (0, 0, 255)

                    capture_done = True

    # Display status
    cv2.putText(
        img,
        "Reference Gesture",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        img,
        f"Target: {gesture_label}",
        (10, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    if capture_done:
        #xmin_ref, ymin_ref, xmax_ref, ymax_ref = best_box

        cv2.putText(
            img,
            f"Final Accuracy: {final_accuracy}%",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            img,
            f"Status: {final_status}",
            (10, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        y = 180
        for feedback in final_feedback:

        # if len(final_feedback) > 0:
            cv2.putText(
                img,
                "- " + feedback,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            y += 30

        cv2.putText(
            img,
            "Press R to retry | Q/ESC to quit",
            (10, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

    else:
        cv2.putText(
            img,
            "Accuracy: Calculating...",
            (10, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )


    # Show PNG reference image
    show_reference_image(img, reference_png)

    cv2.imshow("Gesture Accuracy System", img)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        # Reset for retry
        hold_start_time = None
        capture_buffer = []
        final_accuracy = None
        final_status = "Waiting"
        final_feedback = []
        capture_done = False
        best_box = (0, 0, 0, 0)

    if key in [ord('q'), 27]:  # 27 is the ESC key
        break


# Cleanup                    
cap.release()
cv2.destroyAllWindows()