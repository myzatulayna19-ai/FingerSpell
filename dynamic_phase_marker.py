import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AVAILABLE_GESTURES = {
    1: {"name": "assalamualaikum", "hand": "right"},
    2: {"name": "apa_khabar", "hand": "both"}
}

print("Select Gesture to Practice:")

for key, val in AVAILABLE_GESTURES.items():
    print(f"{key} = {val}")

gesture_choice = int(input("Choice: "))

SELECTED_GESTURE = AVAILABLE_GESTURES.get(
    gesture_choice,
    {"name": "assalamualaikum"}
)["name"]

SELECTED_HAND_MODE = AVAILABLE_GESTURES.get(
    gesture_choice,
    {"hand": "both"}
)["hand"]

print(f"Hand mode: {SELECTED_HAND_MODE}")

# Settings
video_path = os.path.join(
    BASE_DIR,
    "videos",
    f"{SELECTED_GESTURE}.mp4"
)

output_path = os.path.join(
    BASE_DIR,
    "reference_data",
    f"{SELECTED_GESTURE}_landmarks.csv"
)

REWIND_FRAMES = 5

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Video setup
cap = cv2.VideoCapture(video_path)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print(f"Error: Could not open video: {video_path}")
    exit()

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30.0

# Playback Speed multiplier settings
speed_multiplier = 1.0  # Default 1.0x

# Storage
data = {}
phases = []
active_start_frame = None

paused = False
current_frame_img = None
frame_number = 0

# =========================================================
# 7. Extract Features for One Hand
# =========================================================

def extract_hand_features(
    landmarks_array,
    prev_landmarks_array=None
):
    """
    Extract:

    - raw landmarks
    - normalized landmarks
    - wrist velocity
    - palm orientation
    """

    curr = np.array(
        landmarks_array,
        dtype=np.float32
    ).reshape(21, 3)


    # -----------------------------------------------------
    # Normalize landmarks relative to wrist
    # -----------------------------------------------------

    wrist = curr[0].copy()

    normalized = curr - wrist

    scale = np.max(
        np.linalg.norm(
            normalized,
            axis=1
        )
    )

    if scale > 1e-6:
        normalized = normalized / scale


    # -----------------------------------------------------
    # Wrist velocity
    # -----------------------------------------------------

    if prev_landmarks_array is not None:

        prev = np.array(
            prev_landmarks_array,
            dtype=np.float32
        ).reshape(21, 3)

        velocity = (
            curr[0] - prev[0]
        ).tolist()

    else:

        velocity = [
            0.0,
            0.0,
            0.0
        ]


    # -----------------------------------------------------
    # Palm orientation
    # -----------------------------------------------------

    v1 = curr[5] - curr[0]

    v2 = curr[17] - curr[0]

    palm_normal = np.cross(
        v1,
        v2
    )

    norm_val = np.linalg.norm(
        palm_normal
    )

    if norm_val > 1e-6:

        palm_normal = (
            palm_normal / norm_val
        )

    else:

        palm_normal = np.array([
            0.0,
            0.0,
            0.0
        ])


    return (
        curr,
        normalized,
        velocity,
        palm_normal.tolist()
    )


# =========================================================
# 8. Main Video Loop
# =========================================================

while cap.isOpened():

    if not paused:

        success, frame = cap.read()


        # -------------------------------------------------
        # End of video
        # -------------------------------------------------

        if not success:

            print(
                "Video reached end. "
                "Pausing automatically..."
            )

            paused = True

            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                total_frames - 1
            )

            frame_number = total_frames - 1


        else:

            frame_number = (
                int(
                    cap.get(
                        cv2.CAP_PROP_POS_FRAMES
                    )
                ) - 1
            )


            # -------------------------------------------------
            # MediaPipe
            # -------------------------------------------------

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            result = hands.process(rgb)


            # -------------------------------------------------
            # Prepare frame storage
            # -------------------------------------------------

            row = {
                "frame": frame_number
            }


            # =================================================
            # Detect Hands
            # =================================================

            detected_hands = {
                "Left": None,
                "Right": None
            }


            if result.multi_hand_landmarks:

                for idx, hand_landmarks in enumerate(
                    result.multi_hand_landmarks
                ):

                    # -----------------------------------------
                    # Get MediaPipe handedness
                    # -----------------------------------------

                    handedness = (
                        result.multi_handedness[idx]
                        .classification[0]
                        .label
                    )

                    # Correct mirrored camera handedness
                    if handedness == "Left":
                         handedness = "Right"
                    elif handedness == "Right":
                         handedness = "Left"


                    raw_coords = [
                        [
                            lm.x,
                            lm.y,
                            lm.z
                        ]
                        for lm in hand_landmarks.landmark
                    ]


                    detected_hands[
                        handedness
                    ] = (
                        hand_landmarks,
                        raw_coords
                    )


            # =================================================
            # Process LEFT HAND
            # =================================================

            if detected_hands["Left"] is not None:

                hand_landmarks, raw_coords = (
                    detected_hands["Left"]
                )

                previous_left = None

                if (
                    frame_number - 1
                    in data
                    and data[
                        frame_number - 1
                    ].get(
                        "_left_raw_landmarks"
                    ) is not None
                ):

                    previous_left = data[
                        frame_number - 1
                    ][
                        "_left_raw_landmarks"
                    ]


                (
                    curr_raw,
                    norm_landmarks,
                    velocity,
                    palm_normal
                ) = extract_hand_features(
                    raw_coords,
                    previous_left
                )


                row[
                    "_left_raw_landmarks"
                ] = curr_raw


                # Normalized landmarks

                for lm_id, point in enumerate(
                    norm_landmarks
                ):

                    row[
                        f"left_x_{lm_id}"
                    ] = point[0]

                    row[
                        f"left_y_{lm_id}"
                    ] = point[1]

                    row[
                        f"left_z_{lm_id}"
                    ] = point[2]


                # Velocity

                row[
                    "left_vx_wrist"
                ] = velocity[0]

                row[
                    "left_vy_wrist"
                ] = velocity[1]

                row[
                    "left_vz_wrist"
                ] = velocity[2]


                # Palm normal

                row[
                    "left_nx_palm"
                ] = palm_normal[0]

                row[
                    "left_ny_palm"
                ] = palm_normal[1]

                row[
                    "left_nz_palm"
                ] = palm_normal[2]


                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )


            # =================================================
            # Process RIGHT HAND
            # =================================================

            if detected_hands["Right"] is not None:

                hand_landmarks, raw_coords = (
                    detected_hands["Right"]
                )

                previous_right = None

                if (
                    frame_number - 1
                    in data
                    and data[
                        frame_number - 1
                    ].get(
                        "_right_raw_landmarks"
                    ) is not None
                ):

                    previous_right = data[
                        frame_number - 1
                    ][
                        "_right_raw_landmarks"
                    ]


                (
                    curr_raw,
                    norm_landmarks,
                    velocity,
                    palm_normal
                ) = extract_hand_features(
                    raw_coords,
                    previous_right
                )


                row[
                    "_right_raw_landmarks"
                ] = curr_raw


                # Normalized landmarks

                for lm_id, point in enumerate(
                    norm_landmarks
                ):

                    row[
                        f"right_x_{lm_id}"
                    ] = point[0]

                    row[
                        f"right_y_{lm_id}"
                    ] = point[1]

                    row[
                        f"right_z_{lm_id}"
                    ] = point[2]


                # Velocity

                row[
                    "right_vx_wrist"
                ] = velocity[0]

                row[
                    "right_vy_wrist"
                ] = velocity[1]

                row[
                    "right_vz_wrist"
                ] = velocity[2]


                # Palm normal

                row[
                    "right_nx_palm"
                ] = palm_normal[0]

                row[
                    "right_ny_palm"
                ] = palm_normal[1]

                row[
                    "right_nz_palm"
                ] = palm_normal[2]


                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )


            # -------------------------------------------------
            # Save row
            # -------------------------------------------------

            data[frame_number] = row

            current_frame_img = frame


    # =====================================================
    # Render UI
    # =====================================================

    if current_frame_img is not None:

        display_frame = (
            current_frame_img.copy()
        )


        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        status_state = (
            "PAUSED"
            if paused
            else
            f"PLAYING ({speed_multiplier:.1f}x)"
        )


        cv2.putText(
            display_frame,
            (
                f"Frame: {frame_number}/"
                f"{total_frames} | "
                f"State: [{status_state}]"
            ),
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        # -------------------------------------------------
        # Hand detection status
        # -------------------------------------------------

        left_detected = (
            frame_number in data
            and data[
                frame_number
            ].get(
                "_left_raw_landmarks"
            ) is not None
        )

        right_detected = (
            frame_number in data
            and data[
                frame_number
            ].get(
                "_right_raw_landmarks"
            ) is not None
        )


        hand_status = (
            f"Left: "
            f"{'Detected' if left_detected else 'Missing'} | "
            f"Right: "
            f"{'Detected' if right_detected else 'Missing'}"
        )


        cv2.putText(
            display_frame,
            hand_status,
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


        # -------------------------------------------------
        # Phase status
        # -------------------------------------------------

        status_text = (

            f"Recording Phase "
            f"{len(phases) + 1} "
            f"STARTING at frame "
            f"{active_start_frame}..."

            if active_start_frame is not None

            else

            f"Completed Phases: "
            f"{len(phases)}"
        )


        status_color = (
            (0, 255, 255)
            if active_start_frame is not None
            else
            (0, 255, 0)
        )


        cv2.putText(
            display_frame,
            status_text,
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            status_color,
            2
        )


        # -------------------------------------------------
        # Phase list
        # -------------------------------------------------

        y_offset = 140

        for idx, p in enumerate(
            phases,
            start=1
        ):

            cv2.putText(
                display_frame,
                (
                    f"Phase {idx}: "
                    f"Frames {p['start']} "
                    f"-> {p['end']}"
                ),
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1
            )

            y_offset += 25


        # -------------------------------------------------
        # Controls
        # -------------------------------------------------

        cv2.putText(
            display_frame,
            (
                "P = Start/End | "
                "R = Undo | "
                "SPACE = Pause | "
                "1 = 0.5x | "
                "2 = 1.0x | "
                "3 = 2.0x | "
                "A/D = Rewind/Forward | "
                "Q = Save"
            ),
            (
                20,
                display_frame.shape[0] - 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (255, 255, 255),
            2
        )


        cv2.imshow(
            "Phase Marker - Two Hand Dynamic Movement",
            display_frame
        )


    # =====================================================
    # Playback Timing
    # =====================================================

    base_delay = int(
        1000 / fps
    )

    calculated_delay = int(
        base_delay / speed_multiplier
    )

    wait_time = (
        30
        if paused
        else
        max(
            1,
            calculated_delay
        )
    )


    key = (
        cv2.waitKey(wait_time)
        & 0xFF
    )


    # =====================================================
    # Keyboard Controls
    # =====================================================

    if key == ord("p"):

        if active_start_frame is None:

            active_start_frame = (
                frame_number
            )

            print(
                f"--> Started Phase "
                f"{len(phases) + 1} "
                f"at frame "
                f"{frame_number}"
            )

        else:

            if frame_number > active_start_frame:

                phases.append({
                    "start":
                        active_start_frame,
                    "end":
                        frame_number
                })

                print(
                    f"--> Ended Phase "
                    f"{len(phases)} "
                    f"at frame "
                    f"{frame_number} "
                    f"("
                    f"{frame_number - active_start_frame + 1}"
                    f" frames)"
                )

                active_start_frame = None

            else:

                print(
                    "Error: End frame must "
                    "be after start frame!"
                )


    elif key == ord("r"):

        if active_start_frame is not None:

            print(
                f"Canceled start marker "
                f"at frame "
                f"{active_start_frame}"
            )

            active_start_frame = None

        elif phases:

            removed = phases.pop()

            print(
                f"Removed Phase "
                f"{len(phases) + 1}: "
                f"{removed['start']} "
                f"to "
                f"{removed['end']}"
            )

        else:

            print(
                "No phase markers to remove."
            )


    elif key == ord(" "):

        paused = not paused

        print(
            "Paused"
            if paused
            else
            "Resumed",
            f"at frame {frame_number}"
        )


    elif key == ord("1"):

        speed_multiplier = 0.5

        print(
            "Speed set to 0.5x"
        )


    elif key == ord("2"):

        speed_multiplier = 1.0

        print(
            "Speed set to 1.0x"
        )


    elif key == ord("3"):

        speed_multiplier = 2.0

        print(
            "Speed set to 2.0x"
        )


    elif key == ord("a"):

        new_frame = max(
            0,
            frame_number - REWIND_FRAMES
        )

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            new_frame
        )

        frame_number = new_frame

        if paused:

            success, frame = cap.read()

            if success:

                current_frame_img = frame


    elif key == ord("d"):

        new_frame = min(
            total_frames - 1,
            frame_number + REWIND_FRAMES
        )

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            new_frame
        )

        frame_number = new_frame

        if paused:

            success, frame = cap.read()

            if success:

                current_frame_img = frame


    elif key == ord("q"):

        print(
            "Saving valid phase data "
            "and exiting..."
        )

        break


# =========================================================
# Cleanup
# =========================================================

cap.release()

cv2.destroyAllWindows()

hands.close()


# =========================================================
# Save Logic
# =========================================================

if not data:

    print(
        "No MediaPipe landmarks "
        "were detected."
    )

    exit()


df = pd.DataFrame(
    list(data.values())
)


# =========================================================
# Assign Phase
# =========================================================

def assign_phase(frame_num):

    for phase_idx, p in enumerate(
        phases,
        start=1
    ):

        if (
            p["start"]
            <= frame_num
            <= p["end"]
        ):

            return phase_idx

    return None


df["phase"] = (
    df["frame"]
    .apply(assign_phase)
)


df_filtered = (
    df
    .dropna(
        subset=["phase"]
    )
    .copy()
)


df_filtered["phase"] = (
    df_filtered["phase"]
    .astype(int)
)


# =========================================================
# Compute Movement Path
# For BOTH hands, relative to phase start
# =========================================================

left_dx_path = []
left_dy_path = []
left_dz_path = []

right_dx_path = []
right_dy_path = []
right_dz_path = []


for _, row in df_filtered.iterrows():

    p_num = row["phase"]

    start_frame = (
        phases[p_num - 1]["start"]
    )


    # -----------------------------------------------------
    # Find first valid left/right frame in this phase
    # -----------------------------------------------------

    phase_start_left = None
    phase_start_right = None


    for frame_idx in range(
        start_frame,
        phases[p_num - 1]["end"] + 1
    ):

        if frame_idx not in data:
            continue


        frame_data = data[
            frame_idx
        ]


        if (
            phase_start_left is None
            and frame_data.get(
                "_left_raw_landmarks"
            ) is not None
        ):

            phase_start_left = (
                frame_data[
                    "_left_raw_landmarks"
                ][0]
            )


        if (
            phase_start_right is None
            and frame_data.get(
                "_right_raw_landmarks"
            ) is not None
        ):

            phase_start_right = (
                frame_data[
                    "_right_raw_landmarks"
                ][0]
            )


        if (
            phase_start_left is not None
            and
            phase_start_right is not None
        ):

            break


    # -----------------------------------------------------
    # LEFT HAND PATH
    # -----------------------------------------------------

    current_left = data.get(
        int(row["frame"]),
        {}
    ).get(
        "_left_raw_landmarks"
    )


    if (
        phase_start_left is not None
        and current_left is not None
        and not isinstance(current_left, float)
    ):

        current_left_wrist = (
            current_left[0]
        )

        left_dx_path.append(
            current_left_wrist[0]
            - phase_start_left[0]
        )

        left_dy_path.append(
            current_left_wrist[1]
            - phase_start_left[1]
        )

        left_dz_path.append(
            current_left_wrist[2]
            - phase_start_left[2]
        )

    else:

        left_dx_path.append(0.0)
        left_dy_path.append(0.0)
        left_dz_path.append(0.0)


    # -----------------------------------------------------
    # RIGHT HAND PATH
    # -----------------------------------------------------

    current_right = data.get(
        int(row["frame"]),
        {}
    ).get(
        "_right_raw_landmarks"
    )

    if (
        phase_start_right is not None
        and current_right is not None
    ):

        current_right = np.asarray(
            current_right,
            dtype=np.float32
        )

        if current_right.shape == (21, 3):

            current_right_wrist = current_right[0]

            right_dx_path.append(
                current_right_wrist[0]
                - phase_start_right[0]
            )

            right_dy_path.append(
                current_right_wrist[1]
                - phase_start_right[1]
            )

            right_dz_path.append(
                current_right_wrist[2]
                - phase_start_right[2]
            )

        else:

            right_dx_path.append(0.0)
            right_dy_path.append(0.0)
            right_dz_path.append(0.0)

    else:

        right_dx_path.append(0.0)
        right_dy_path.append(0.0)
        right_dz_path.append(0.0)


# =========================================================
# Add Movement Path Columns
# =========================================================

df_filtered[
    "left_dx_path"
] = left_dx_path

df_filtered[
    "left_dy_path"
] = left_dy_path

df_filtered[
    "left_dz_path"
] = left_dz_path


df_filtered[
    "right_dx_path"
] = right_dx_path

df_filtered[
    "right_dy_path"
] = right_dy_path

df_filtered[
    "right_dz_path"
] = right_dz_path


# =========================================================
# Remove Internal Raw Data
# =========================================================

df_filtered.drop(
    columns=[
        "_left_raw_landmarks",
        "_right_raw_landmarks"
    ],
    inplace=True,
    errors="ignore"
)

# =========================================================
# Ensure All Expected Feature Columns Exist
# =========================================================

required_feature_cols = [
    # LEFT motion
    "left_vx_wrist",
    "left_vy_wrist",
    "left_vz_wrist",
    "left_nx_palm",
    "left_ny_palm",
    "left_nz_palm",

    # LEFT movement path
    "left_dx_path",
    "left_dy_path",
    "left_dz_path",

    # RIGHT motion
    "right_vx_wrist",
    "right_vy_wrist",
    "right_vz_wrist",
    "right_nx_palm",
    "right_ny_palm",
    "right_nz_palm",

    # RIGHT movement path
    "right_dx_path",
    "right_dy_path",
    "right_dz_path"
]

for col in required_feature_cols:
    if col not in df_filtered.columns:
        df_filtered[col] = 0.0

# =========================================================
# Organize Columns
# =========================================================

base_cols = [
    "frame",
    "phase"
]


motion_cols = [

    # LEFT
    "left_vx_wrist",
    "left_vy_wrist",
    "left_vz_wrist",

    "left_nx_palm",
    "left_ny_palm",
    "left_nz_palm",

    "left_dx_path",
    "left_dy_path",
    "left_dz_path",

    # RIGHT
    "right_vx_wrist",
    "right_vy_wrist",
    "right_vz_wrist",

    "right_nx_palm",
    "right_ny_palm",
    "right_nz_palm",

    "right_dx_path",
    "right_dy_path",
    "right_dz_path"
]


lm_cols = [

    col
    for col in df_filtered.columns

    if (
        col not in base_cols
        and col not in motion_cols
    )
]


# Put LEFT landmarks first,
# then RIGHT landmarks

left_lm_cols = [
    col
    for col in lm_cols
    if col.startswith("left_")
]

right_lm_cols = [
    col
    for col in lm_cols
    if col.startswith("right_")
]


final_columns = (
    base_cols
    + motion_cols
    + left_lm_cols
    + right_lm_cols
)


df_filtered = (
    df_filtered[
        final_columns
    ]
)


# =========================================================
# Save CSV
# =========================================================

output_directory = (
    os.path.dirname(
        output_path
    )
)

if output_directory:

    os.makedirs(
        output_directory,
        exist_ok=True
    )

df_filtered.to_csv(
    output_path,
    index=False
)

print("\n========================================")
print("CSV SAVED SUCCESSFULLY")
print("========================================")
print(f"Saved to: {output_path}")
print(f"Full path: {os.path.abspath(output_path)}")
print(f"File exists: {os.path.exists(output_path)}")
print(f"Total saved frames: {len(df_filtered)}")
print(f"Total phases: {df_filtered['phase'].nunique()}")

# =========================================================
# Hand Detection Check
# =========================================================

print("\n=== HAND DETECTION CHECK ===")

left_count = 0
right_count = 0

for frame_data in data.values():

    if frame_data.get("_left_raw_landmarks") is not None:
        left_count += 1

    if frame_data.get("_right_raw_landmarks") is not None:
        right_count += 1

print(
    f"Frames with LEFT hand data: "
    f"{left_count}/{len(data)}"
)

print(
    f"Frames with RIGHT hand data: "
    f"{right_count}/{len(data)}"
)

if left_count == 0:
    print("WARNING: No LEFT hand was detected.")

if right_count == 0:
    print("WARNING: No RIGHT hand was detected.")

print(
    "\nSaved TWO-HAND Dynamic Features CSV to:",
    output_path
)

print(
    "Total saved frames:",
    len(df_filtered)
)

print(
    "Total phases:",
    len(phases)
)