import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
import time
import joblib
import importlib

model_payload = joblib.load("gesture_phase_model.pkl")

print("Model features:", len(model_payload["feature_cols"]))
print("\nFeature columns:")
for i, col in enumerate(model_payload["feature_cols"], 1):
    print(i, col)

from guidance_data.assalamualaikum_guidance import PHASE_INSTRUCTIONS

# Dynamic gesture selection
AVAILABLE_GESTURES = {
    1: "assalamualaikum",
    2: "apa_khabar"
}

print("Select Gesture to Practice:")
for key, val in AVAILABLE_GESTURES.items():
    print(f"{key} = {val}")

gesture_choice = int(input("Choice: "))
SELECTED_GESTURE = AVAILABLE_GESTURES.get(
    gesture_choice,
    "assalamualaikum"
)

# Dynamic File Paths
reference_path = f"reference_data/{SELECTED_GESTURE}_landmarks.csv"

guidance_module = importlib.import_module(
    f"guidance_data.{SELECTED_GESTURE}_guidance"
)

PHASE_INSTRUCTIONS = guidance_module.PHASE_INSTRUCTIONS

# Camera selection
print("0 = DroidCam")
print("1 = Laptop Webcam")
print("2 = Logitech Webcam")

camera_choice = int(input("Choose camera: "))
cap = cv2.VideoCapture(camera_choice)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print(f"Error: Unable to open camera index {camera_choice}.")
    exit(1)

SIMILARITY_THRESHOLD = 0.80
HOLD_DURATION_REQUIRED = 2.0  # Hold position for 2 seconds instead of raw frame counts
REFERENCE_FRAME_DELAY = 0.25

# Dynamic movement settings
DYNAMIC_THRESHOLD = 0.72

# Maximum acceptable angle difference in degrees
MOVEMENT_ANGLE_TOLERANCE = 25.0

# Acceptable distance difference as a percentage
MOVEMENT_DISTANCE_TOLERANCE = 0.30

# Minimum movement before we start judging direction
MIN_MOVEMENT_DISTANCE = 0.015

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Load reference data
reference = pd.read_csv(reference_path)
phase_numbers = sorted(reference["phase"].unique())
total_phases = len(phase_numbers)

# =========================================================
# 6. LOAD REFERENCE CSV
# =========================================================

reference = pd.read_csv(
    reference_path
)

print(
    f"\nLoaded reference file: "
    f"{reference_path}"
)

print(
    f"Number of reference frames: "
    f"{len(reference)}"
)


# =========================================================
# CHECK WHICH HANDS ARE USED BY THIS GESTURE
# =========================================================

GESTURE_HANDS = {
    "assalamualaikum": "right",
    "apa_khabar": "both"
}

HAND_MODE = GESTURE_HANDS.get(
    SELECTED_GESTURE,
    "both"
)

print(f"Gesture hand mode: {HAND_MODE}")


# =========================================================
# CHECK REQUIRED LANDMARK COLUMNS
# =========================================================

required_columns = []

if HAND_MODE in ("left", "both"):
    required_columns.extend([
        "left_x_0",
        "left_y_0",
        "left_z_0"
    ])

if HAND_MODE in ("right", "both"):
    required_columns.extend([
        "right_x_0",
        "right_y_0",
        "right_z_0"
    ])


missing_columns = [
    col
    for col in required_columns
    if col not in reference.columns
]


if missing_columns:

    print(
        "\nERROR: Reference CSV is missing "
        "required hand columns."
    )

    print("Gesture:", SELECTED_GESTURE)
    print("Hand mode:", HAND_MODE)

    print("Missing columns:")

    for col in missing_columns:
        print(f"  - {col}")

    cap.release()
    hands.close()
    exit(1)

missing_columns = [
    col
    for col in required_columns
    if col not in reference.columns
]

if missing_columns:

    print(
        "\nERROR: This CSV does not "
        "contain the new two-hand columns."
    )

    print(
        "Missing columns:"
    )

    for col in missing_columns:
        print(
            f"  - {col}"
        )

    print(
        "\nPlease regenerate the CSV "
        "using the updated "
        "dynamic_phase_marker.py."
    )

    cap.release()
    hands.close()
    exit(1)


phase_numbers = sorted(
    reference["phase"]
    .dropna()
    .unique()
)

total_phases = len(
    phase_numbers
)


# =========================================================
# 7. NORMALIZATION
# =========================================================

def normalize_landmarks(
    landmarks
):

    landmarks = np.array(
        landmarks,
        dtype=np.float32
    ).reshape(
        21,
        3
    )

    wrist = (
        landmarks[0]
        .copy()
    )

    normalized = (
        landmarks - wrist
    )

    distances = np.linalg.norm(
        normalized,
        axis=1
    )

    scale = np.max(
        distances
    )

    if scale < 1e-6:

        return normalized

    return (
        normalized / scale
    )


# =========================================================
# 8. EXTRACT LEFT/RIGHT REFERENCE HANDS
# =========================================================

reference_frames = []


for _, row in reference.iterrows():

    left_landmarks = []

    right_landmarks = []


    # -----------------------------------------------------
    # LEFT HAND
    # -----------------------------------------------------

    left_landmarks = []

    if HAND_MODE in ("left", "both"):

        for landmark_id in range(21):

            left_landmarks.append([
                row[f"left_x_{landmark_id}"],
                row[f"left_y_{landmark_id}"],
                row[f"left_z_{landmark_id}"]
            ])


    # -----------------------------------------------------
    # RIGHT HAND
    # -----------------------------------------------------

    right_landmarks = []

    if HAND_MODE in ("right", "both"):

        for landmark_id in range(21):

            right_landmarks.append([
                row[f"right_x_{landmark_id}"],
                row[f"right_y_{landmark_id}"],
                row[f"right_z_{landmark_id}"]
            ])


    # -----------------------------------------------------
    # Handle missing hands
    # -----------------------------------------------------

    left_array = np.array(
        left_landmarks,
        dtype=np.float32
    )

    right_array = np.array(
        right_landmarks,
        dtype=np.float32
    )


    left_valid = (
        HAND_MODE in ("left", "both")
        and len(left_landmarks) == 21
        and not np.isnan(
            np.array(left_landmarks)
        ).all()
    )


    right_valid = (
        HAND_MODE in ("right", "both")
        and len(right_landmarks) == 21
        and not np.isnan(
            np.array(right_landmarks)
        ).all()
    )


    if left_valid:

        left_normalized = (
            normalize_landmarks(
                left_landmarks
            )
        )

    else:

        left_normalized = None


    if right_valid:

        right_normalized = (
            normalize_landmarks(
                right_landmarks
            )
        )

    else:

        right_normalized = None


    # -----------------------------------------------------
    # Movement path values
    # -----------------------------------------------------

    left_path = np.array([

        row.get(
            "left_dx_path",
            0.0
        ),

        row.get(
            "left_dy_path",
            0.0
        ),

        row.get(
            "left_dz_path",
            0.0
        )

    ], dtype=np.float32)


    right_path = np.array([

        row.get(
            "right_dx_path",
            0.0
        ),

        row.get(
            "right_dy_path",
            0.0
        ),

        row.get(
            "right_dz_path",
            0.0
        )

    ], dtype=np.float32)


    reference_frames.append({

        "frame":
            int(row["frame"]),

        "phase":
            int(row["phase"]),

        "left_landmarks":
            left_normalized,

        "right_landmarks":
            right_normalized,

        "left_path":
            left_path,

        "right_path":
            right_path
    })


# =========================================================
# 9. GROUP REFERENCE FRAMES BY PHASE
# =========================================================

phase_frames = {

    phase: [
        item
        for item in reference_frames
        if item["phase"] == phase
    ]

    for phase in phase_numbers
}


# =========================================================
# 10. DRAW REFERENCE HAND
# =========================================================

def reference_to_screen(
    landmarks,
    center_x,
    center_y,
    scale
):

    points = []

    if landmarks is None:

        return points


    for landmark in landmarks:

        x = landmark[0]

        y = landmark[1]

        screen_x = int(
            center_x
            + x * scale
        )

        screen_y = int(
            center_y
            + y * scale
        )

        points.append(
            (
                screen_x,
                screen_y
            )
        )

    return points


def draw_reference_hand(
    frame,
    landmarks,
    center_x,
    center_y,
    scale,
    label
):

    if landmarks is None:

        return


    points = reference_to_screen(
        landmarks,
        center_x,
        center_y,
        scale
    )


    # -----------------------------------------------------
    # Draw connections
    # -----------------------------------------------------

    for connection in (
        mp_hands.HAND_CONNECTIONS
    ):

        start_point = (
            points[
                connection[0]
            ]
        )

        end_point = (
            points[
                connection[1]
            ]
        )

        cv2.line(

            frame,

            start_point,

            end_point,

            (255, 255, 255),

            2
        )


    # -----------------------------------------------------
    # Draw landmarks
    # -----------------------------------------------------

    for point in points:

        cv2.circle(

            frame,

            point,

            5,

            (255, 255, 255),

            -1
        )


    # -----------------------------------------------------
    # Label
    # -----------------------------------------------------

    cv2.putText(

        frame,

        label,

        (
            center_x - 80,
            center_y - 130
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (255, 255, 255),

        2
    )


# =========================================================
# 11. HAND MATCHING
# =========================================================

def calculate_hand_similarity(
    current_landmarks,
    reference_landmarks
):

    if (
        current_landmarks is None
        or reference_landmarks is None
    ):

        return None


    difference = np.linalg.norm(

        current_landmarks
        - reference_landmarks,

        axis=1
    )


    mean_difference = (
        np.mean(difference)
    )


    similarity = max(

        0.0,

        1.0 - mean_difference
    )


    return similarity

def generate_position_correction(
    current_landmarks,
    reference_landmarks,
    hand_name
):
    """
    Compare the user's wrist position with the reference
    and generate a simple correction message.
    """

    if (
        current_landmarks is None
        or reference_landmarks is None
    ):
        return None

    # Wrist = landmark 0
    current_wrist = current_landmarks[0]
    reference_wrist = reference_landmarks[0]

    # Difference between user and reference
    dx = current_wrist[0] - reference_wrist[0]
    dy = current_wrist[1] - reference_wrist[1]

    corrections = []

    # How sensitive the correction should be
    POSITION_TOLERANCE = 0.12

    # -----------------------------------------------------
    # Horizontal position
    # -----------------------------------------------------

    if dx > POSITION_TOLERANCE:
        corrections.append(
            f"Move your {hand_name} hand left"
        )

    elif dx < -POSITION_TOLERANCE:
        corrections.append(
            f"Move your {hand_name} hand right"
        )

    # -----------------------------------------------------
    # Vertical position
    # -----------------------------------------------------

    if dy > POSITION_TOLERANCE:
        corrections.append(
            f"Move your {hand_name} hand up"
        )

    elif dy < -POSITION_TOLERANCE:
        corrections.append(
            f"Move your {hand_name} hand down"
        )

    if corrections:
        return " | ".join(corrections)

    return None


# =========================================================
# 12. TWO-HAND MOVEMENT EVALUATION
# =========================================================

def evaluate_two_hand_movement(
    current_left,
    current_right,
    phase_reference
):

    best_score = 0.0

    best_left_score = 0.0

    best_right_score = 0.0

    best_reference_item = None

    for ref_item in phase_reference:

        left_score = (
            calculate_hand_similarity(
                current_left,
                ref_item[
                    "left_landmarks"
                ]
            )
        )


        right_score = (
            calculate_hand_similarity(
                current_right,
                ref_item[
                    "right_landmarks"
                ]
            )
        )


        # -------------------------------------------------
        # Determine how many hands reference requires
        # -------------------------------------------------

        reference_uses_left = (
            ref_item[
                "left_landmarks"
            ] is not None
        )

        reference_uses_right = (
            ref_item[
                "right_landmarks"
            ] is not None
        )


        # -------------------------------------------------
        # Both hands required
        # -------------------------------------------------

        if (
            reference_uses_left
            and reference_uses_right
        ):

            if (
                left_score is None
                or right_score is None
            ):

                continue


            combined_score = (
                left_score
                * 0.5
                +
                right_score
                * 0.5
            )


        # -------------------------------------------------
        # Left hand only
        # -------------------------------------------------

        elif reference_uses_left:

            if left_score is None:

                continue

            combined_score = (
                left_score
            )


        # -------------------------------------------------
        # Right hand only
        # -------------------------------------------------

        elif reference_uses_right:

            if right_score is None:

                continue

            combined_score = (
                right_score
            )


        else:

            continue


        if combined_score > best_score:

            best_score = (
                combined_score
            )

            best_reference_item = ref_item

            best_left_score = (
                left_score
                if left_score is not None
                else 0.0
            )

            best_right_score = (
                right_score
                if right_score is not None
                else 0.0
            )


    # =====================================================
    # Determine correctness
    # =====================================================

    is_correct = (
        best_score
        >= SIMILARITY_THRESHOLD
    )


    # =====================================================
    # Feedback
    # =====================================================

    feedback = []

    # Generate position correction
    if best_reference_item is not None:
        
        if (
            reference_uses_left
            and current_left is not None
            and best_reference_item["left_landmarks"] is not None
        ):

            left_correction = generate_position_correction(
                current_left,
                best_reference_item["left_landmarks"],
                "LEFT"
            )

            if left_correction:
                feedback.append(left_correction)


        if (
            reference_uses_right
            and current_right is not None
            and best_reference_item["right_landmarks"] is not None
        ):

            right_correction = generate_position_correction(
                current_right,
                best_reference_item["right_landmarks"],
                "RIGHT"
            )

            if right_correction:
                feedback.append(right_correction)
    
    # If position is correct but gesture is not
    if is_correct:

        if reference_uses_left and reference_uses_right:
            feedback_text = "Both hands look good!"

        elif reference_uses_right:
            feedback_text = "Right hand looks good!"

        elif reference_uses_left:
            feedback_text = "Left hand looks good!"

        else:
            feedback_text = "Gesture looks good!"

    elif feedback:

        feedback_text = " | ".join(feedback)

    else:

        feedback_text = "Keep following the movement"

    return (
        best_score,
        is_correct,
        feedback_text,
        best_left_score,
        best_right_score
    )


# =========================================================
# 13. GUIDANCE STATE
# =========================================================

current_phase_index = 0

gesture_completed = False

current_similarity = 0.0

phase_transition = False

transition_start_time = 0

reference_frame_index = 0

# reference_frame_timer = (
#     time.time()
# )

reference_frame_timer = None

reference_demo = True

practice_started = False

hold_start_time = None

feedback_msg = ""

# Wait for camera to appear before starting reference
camera_ready_time = None
CAMERA_START_DELAY = 2.0


# =========================================================
# 14. LIVE CAMERA LOOP
# =========================================================

while cap.isOpened():

    success, frame = (
        cap.read()
    )


    if not success:

        print(
            "Could not read from camera."
        )

        break

    # -----------------------------------------------------
    # Camera ready timer
    # -----------------------------------------------------

    if camera_ready_time is None:
        camera_ready_time = time.time()
        reference_frame_timer = time.time()


    # -----------------------------------------------------
    # Mirror camera
    # -----------------------------------------------------

    # frame = cv2.flip(
    #     frame,
    #     1
    # )


    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    result = hands.process(
        rgb
    )


    current_phase = (
        phase_numbers[
            current_phase_index
        ]
    )


    # =====================================================
    # REFERENCE DEMO
    # =====================================================

    if (
        not gesture_completed
        and not phase_transition
        and reference_demo
        and camera_ready_time is not None
        and time.time() - camera_ready_time >= CAMERA_START_DELAY
    ):

        current_phase_frames = (
            phase_frames[
                current_phase
            ]
        )

        # =====================================================
        # CAMERA START DELAY
        # =====================================================

        if (
            camera_ready_time is not None
            and time.time() - camera_ready_time < CAMERA_START_DELAY
        ):

            remaining = CAMERA_START_DELAY - (
                time.time() - camera_ready_time
            )

            cv2.putText(
                frame,
                "Camera ready...",
                (30, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Starting in {remaining:.1f}s",
                (30, 190),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )


        if current_phase_frames:

            reference_frame_index = min(

                reference_frame_index,

                len(
                    current_phase_frames
                ) - 1
            )


            reference_item = (
                current_phase_frames[
                    reference_frame_index
                ]
            )


            # -------------------------------------------------
            # Draw LEFT reference
            # -------------------------------------------------

            draw_reference_hand(

                frame,

                reference_item[
                    "left_landmarks"
                ],

                center_x=180,

                center_y=390,

                scale=220,

                label="LEFT"
            )


            # -------------------------------------------------
            # Draw RIGHT reference
            # -------------------------------------------------

            draw_reference_hand(

                frame,

                reference_item[
                    "right_landmarks"
                ],

                center_x=500,

                center_y=390,

                scale=220,

                label="RIGHT"
            )


            if (
                time.time()
                - reference_frame_timer
                >= REFERENCE_FRAME_DELAY
            ):

                reference_frame_index += 2

                reference_frame_timer = (
                    time.time()
                )


                if (
                    reference_frame_index
                    >= len(
                        current_phase_frames
                    )
                ):

                    reference_frame_index = (

                        len(
                            current_phase_frames
                        ) - 1
                    )

                    reference_demo = False

                    practice_started = True

                    hold_start_time = None

                    current_similarity = 0.0


    # =====================================================
    # USER HAND DETECTION
    # =====================================================

    detected_hands = {

        "Left": None,

        "Right": None
    }


    if result.multi_hand_landmarks:

        for idx, hand_landmarks in enumerate(

            result.multi_hand_landmarks

        ):

            handedness = (

                result
                .multi_handedness[idx]
                .classification[0]
                .label
            )


            current_landmarks = [

                [
                    lm.x,
                    lm.y,
                    lm.z
                ]

                for lm
                in hand_landmarks.landmark
            ]


            current_normalized = (
                normalize_landmarks(
                    current_landmarks
                )
            )


            detected_hands[
                handedness
            ] = current_normalized


            # Draw user's hands

            mp_draw.draw_landmarks(

                frame,

                hand_landmarks,

                mp_hands.HAND_CONNECTIONS
            )


    # =====================================================
    # USER EVALUATION
    # =====================================================

    if (

        not gesture_completed

        and not reference_demo

        and practice_started

    ):

        current_phase_reference = (
            phase_frames[
                current_phase
            ]
        )


        current_left = (
            detected_hands[
                "Left"
            ]
        )


        current_right = (
            detected_hands[
                "Right"
            ]
        )


        # -------------------------------------------------
        # Evaluate ALL phases as movement phases
        # -------------------------------------------------

        (
            confidence,
            is_correct,
            feedback_msg,
            left_score,
            right_score
        ) = evaluate_two_hand_movement(

            current_left,

            current_right,

            current_phase_reference
        )


        current_similarity = (
            confidence
        )


        # -------------------------------------------------
        # Timer
        # -------------------------------------------------

        if is_correct:

            if hold_start_time is None:

                hold_start_time = (
                    time.time()
                )

        else:

            hold_start_time = None


    # =====================================================
    # NO HAND DETECTED
    # =====================================================

    if (
        not result.multi_hand_landmarks
        and not reference_demo
    ):

        current_similarity = 0.0

        hold_start_time = None

        feedback_msg = (
            "Hands not detected"
        )


    # =====================================================
    # HOLD TIMER
    # =====================================================

    hold_elapsed = (

        time.time()
        - hold_start_time

        if hold_start_time

        else 0.0
    )


    # =====================================================
    # PHASE COMPLETION
    # =====================================================

    if (

        not gesture_completed

        and not phase_transition

        and hold_elapsed
        >= HOLD_DURATION_REQUIRED

    ):

        hold_start_time = None


        if (
            current_phase_index
            < total_phases - 1
        ):

            phase_transition = True

            transition_start_time = (
                time.time()
            )

        else:

            gesture_completed = True


    # =====================================================
    # PHASE TRANSITION
    # =====================================================

    if phase_transition:

        if (

            time.time()
            - transition_start_time
            >= 2.0

        ):

            current_phase_index += 1


            # Reset reference demo

            reference_frame_index = 0

            reference_frame_timer = (
                time.time()
            )

            reference_demo = True

            practice_started = False

            phase_transition = False


    # =====================================================
    # UI
    # =====================================================

    if gesture_completed:

        cv2.putText(

            frame,

            "GESTURE COMPLETED!",

            (30, 50),

            cv2.FONT_HERSHEY_SIMPLEX,

            1.0,

            (0, 255, 0),

            3
        )


    elif phase_transition:

        next_phase = (
            phase_numbers[
                min(
                    current_phase_index + 1,
                    total_phases - 1
                )
            ]
        )


        cv2.putText(

            frame,

            f"Phase {current_phase} Completed!",

            (30, 50),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.9,

            (255, 255, 255),

            2
        )


        cv2.putText(

            frame,

            f"Get ready for Phase {next_phase}...",

            (30, 100),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2
        )


    else:

        instruction = (
            PHASE_INSTRUCTIONS.get(
                current_phase,
                "Follow the reference movement."
            )
        )


        cv2.putText(

            frame,

            (
                f"Phase "
                f"{current_phase} / "
                f"{total_phases}"
            ),

            (30, 45),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.9,

            (255, 255, 255),

            2
        )


        cv2.putText(

            frame,

            instruction,

            (30, 115),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2
        )


        # -------------------------------------------------
        # Demo / practice
        # -------------------------------------------------

        if reference_demo:

            cv2.putText(

                frame,

                "Watch the reference...",

                (30, 150),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255, 255, 255),

                2
            )

        else:

            cv2.putText(

                frame,

                "Your turn!",

                (30, 150),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (0, 255, 0),

                2
            )


            # -------------------------------------------------
            # Match percentage
            # -------------------------------------------------

            cv2.putText(

                frame,

                (
                    f"Match: "
                    f"{current_similarity * 100:.1f}%"
                ),

                (30, 80),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255, 255, 255),

                2
            )


            # -------------------------------------------------
            # Feedback
            # -------------------------------------------------

            if feedback_msg:

                feedback_color = (

                    (0, 255, 0)

                    if hold_start_time

                    else

                    (0, 0, 255)
                )


                cv2.putText(

                    frame,

                    feedback_msg,

                    (30, 240),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.7,

                    feedback_color,

                    2
                )


            # -------------------------------------------------
            # Hold progress
            # -------------------------------------------------

            if (

                current_similarity
                >= SIMILARITY_THRESHOLD

                and hold_start_time

            ):

                cv2.putText(

                    frame,

                    "Good! Hold your movement...",

                    (30, 280),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.7,

                    (0, 255, 0),

                    2
                )


                hold_progress = min(

                    hold_elapsed
                    / HOLD_DURATION_REQUIRED,

                    1.0
                )


                cv2.putText(

                    frame,

                    (
                        f"Hold: "
                        f"{hold_progress * 100:.0f}%"
                    ),

                    (30, 320),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    (0, 255, 0),

                    2
                )


    # =====================================================
    # SHOW
    # =====================================================

    cv2.imshow(

        "FingerSpell - Two Hand Dynamic Guidance",

        frame
    )


    if (
        cv2.waitKey(1)
        & 0xFF
        == ord("q")
    ):

        break


# =========================================================
# CLEANUP
# =========================================================

cap.release()

cv2.destroyAllWindows()

hands.close()