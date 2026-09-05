import cv2
import mediapipe as mp
import csv
import os
import time

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
print("0 = Laptop Webcam")
print("1 = DroidCam")
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
        0,   # wrist
        4,   # thumb tip
        5,   # index base
        8,   # index tip
        9,   # middle base
        12,  # middle tip
        13,  # ring base
        16,  # ring tip
        17,  # pinky base
        20   # pinky tip
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

def is_finger_extended(landmarks, tip, base):
    """Returns True if the finger is extended."""

    tip_y = landmarks[tip * 2 + 1]
    base_y = landmarks[base * 2 + 1]

    return abs(tip_y - base_y) > 1.0

def is_finger_folded(landmarks, tip, base):
    """Returns True if the finger is folded."""

    return not is_finger_extended(
        landmarks,
        tip,
        base
    )

def is_thumb_beside_fingers(landmarks):

    thumb_tip_x = landmarks[4 * 2]
    index_base_x = landmarks[5 * 2]

    return abs(
        thumb_tip_x - index_base_x
    ) < 0.35 # threshold < 0.8

def generate_rule_feedback(gesture_label, landmarks):
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

    if gesture_label == "A":

        if not is_finger_folded(
            landmarks,
            8,
            5
        ):
            feedback.append(
                "Fold your index finger."
            )

        if not is_finger_folded(
            landmarks,
            12,
            9
        ):
            feedback.append(
                "Fold your middle finger."
            )

        if not is_finger_folded(
            landmarks,
            16,
            13
        ):
            feedback.append(
                "Fold your ring finger."
            )

        if not is_finger_folded(
            landmarks,
            20,
            17
        ):
            feedback.append(
                "Fold your little finger."
            )

        if not is_thumb_beside_fingers(landmarks):
            feedback.append(
                "Keep your thumb beside your fingers."
            )
    
    # if gesture_label == "A":
        # For A, fingers should be closed

        # if index_tip_y < -1.2 or middle_tip_y < -1.2 or ring_tip_y < -1.2 or pinky_tip_y < -1.2:
        #     feedback.append("Close your fingers more.")
        #     fingers_ok = False
        # if (
        # index_open > 1.0 or
        # middle_open > 1.0 or
        # ring_open > 1.0 or
        # pinky_open > 1.0
        # ):
        #     feedback.append(
        #         "Close your fingers."
        #     )

        # if thumb_distance > 0.8: #thumb too far outward
        #     feedback.append("Keep your thumb closer beside your fingers.")
        # thumb_ok = False

    elif gesture_label == "B":
        # For B, fingers should be straight and together
        if index_tip_y > -0.5 or middle_tip_y > -0.5:
            feedback.append("Straighten your fingers upward.")

        feedback.append("Place your thumb across your palm.")

    # if gesture_label == "B":

        # if not is_finger_extended(landmarks, 8, 5):
        #     feedback.append(
        #         "Straighten your index finger."
        #     )

        # if not is_finger_extended(landmarks, 12, 9):
        #     feedback.append(
        #         "Straighten your middle finger."
        #     )

        # if not is_finger_extended(landmarks, 16, 13):
        #     feedback.append(
        #         "Straighten your ring finger."
        #     )

        # if not is_finger_extended(landmarks, 20, 17):
        #     feedback.append(
        #         "Straighten your little finger."
        #     )

    elif gesture_label == "C":
        # For C, fingers should be curved
        if index_tip_y < -0.5 or middle_tip_y < -0.5 or ring_tip_y < -0.5 or pinky_tip_y < -0.5:
            feedback.append("Curve your fingers to form a 'C' shape.")

        feedback.append("Keep your thumb opposite to the fingers.")

    return feedback


def find_best_reference(current_landmarks, reference_list):
    """Compare current gesture with all references and return the best match."""
    best_accuracy = -1
    best_box = (0, 0, 0, 0)
    best_landmarks = []

    for reference in reference_list:
        # Load reference box
        xmin_ref = int(reference[-4])
        ymin_ref = int(reference[-3])
        xmax_ref = int(reference[-2])
        ymax_ref = int(reference[-1])

        # Remove box data
        reference_landmarks = reference[:-4]

        accuracy = calculate_accuracy(current_landmarks, reference_landmarks)

        # Keep BEST match
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_box = (xmin_ref, ymin_ref, xmax_ref, ymax_ref)
            best_landmarks = reference_landmarks

    return best_accuracy, best_box, best_landmarks

def show_reference_image(img, reference_png):
    """Display transparent PNG guide."""
    if reference_png is None:
        return
    
    guide = cv2.resize(
        reference_png,
        (300, 300)
    )

    h,w = guide.shape[:2]

    x_offset = 20
    y_offset = 140

    # PNG with transparency
    if guide.shape[2] == 4:
        alpha = (guide[:, :, 3] / 255.0) * 0.5

        for c in range(3):
            img[y_offset:y_offset+h, x_offset:x_offset+w, c] = (
                alpha * guide[:, :, c] +
                (1 - alpha) * img[y_offset:y_offset+h, x_offset:x_offset+w, c]
            )
    else:
        opacity = 0.5
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
        
def draw_skeleton_on_reference(reference_png):
    """Draw MediaPipe skeleton on the reference PNG."""
    if reference_png is None:
        print("Warning: Reference PNG not found for skeleton drawing.")
        return

    # Resize for consistency
    guide = cv2.resize(reference_png, (300, 300))

    # Convert transparent PNG into normal 3-channel BGR image
    if guide.shape[2] == 4:
        bgr_guide = guide[:, :, :3].copy()
    else:
        bgr_guide = guide.copy()

    # Convert to RGB for MediaPipe processing
    guide_rgb = cv2.cvtColor(
        bgr_guide,
        cv2.COLOR_BGR2RGB
    )

    # Process with MediaPipe
    results = hands.process(guide_rgb)

    print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            draw_dotted_hand_landmarks(
                bgr_guide,
                handLms,
                color=(255, 255, 255)
            )

    return bgr_guide

reference_png = draw_skeleton_on_reference(
    reference_png
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

            #capture_buffer.append(current_landmarks)

            # # Find best matching reference
            # best_accuracy, best_box, best_landmarks = find_best_reference(
            #     current_landmarks,
            #     reference_list
            # )

            # xmin_ref, ymin_ref, xmax_ref, ymax_ref = best_box

            # # Smooth accuracy
            # accuracy_history.append(best_accuracy)

            # if len(accuracy_history) > 10:
            #     accuracy_history.pop(0)

            # smooth_accuracy = int(
            #     sum(accuracy_history) / len(accuracy_history)
            # )

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

                    # Penalize each incorrect finger
                    if not is_finger_folded(averaged_landmarks, 8, 5):
                        final_accuracy -= 8

                    if not is_finger_folded(averaged_landmarks, 12, 9):
                        final_accuracy -= 8

                    if not is_finger_folded(averaged_landmarks, 16, 13):
                        final_accuracy -= 8

                    if not is_finger_folded(averaged_landmarks, 20, 17):
                        final_accuracy -= 8

                    if not is_thumb_beside_fingers(averaged_landmarks):
                        final_accuracy -= 10

                    final_accuracy = max(0, final_accuracy)

                    a_rules_ok = (
                        is_finger_folded(averaged_landmarks, 8, 5) and # Index
                        is_finger_folded(averaged_landmarks, 12, 9) and # Middle
                        is_finger_folded(averaged_landmarks, 16, 13) and # Ring
                        is_finger_folded(averaged_landmarks, 20, 17) and # Pinky
                        is_thumb_beside_fingers(averaged_landmarks) # Thumb
                    )

                    if final_accuracy >= 90 and a_rules_ok:
                        final_feedback = ["Great! Your gesture is accurate."]
                        final_status = "Correct"
                        status_color = (0, 255, 0)

                    elif final_accuracy >= 75:
                        final_feedback = generate_rule_feedback(
                            gesture_label,
                            averaged_landmarks
                        )

                        final_status = "Almost There"
                        status_color = (0, 255, 255)

                    else:
                        final_feedback = generate_rule_feedback(
                            gesture_label,
                            averaged_landmarks
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
        xmin_ref, ymin_ref, xmax_ref, ymax_ref = best_box

        cv2.rectangle(
            img,
            (xmin_ref, ymin_ref),
            (xmax_ref, ymax_ref),
            (0, 255, 0),
            2
        )

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