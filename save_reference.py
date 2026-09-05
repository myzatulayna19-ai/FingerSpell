try:
    import cv2
except ImportError:
    print("Error: OpenCV is not installed. Install it with 'pip install opencv-python'.")
    exit(1)

try:
    import mediapipe as mp
except ImportError:
    print("Error: mediapipe is not installed. Install it with 'pip install mediapipe'.")
    exit(1)

import csv
import os
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands

# Drawing utility
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.7,
    #min_tracking_confidence=0.7
)

# Open camera selection
#print("0 = Laptop Webcam")
#print("1 = DroidCam")
#print("2 = Logitech Webcam")

#camera_choice = int(input("Choose camera: "))
#cap = cv2.VideoCapture(camera_choice)

#if not cap.isOpened():
    #print(f"Error: Unable to open camera index {camera_choice}.")
    #exit(1)

# Ask gesture label
gesture_label = input("Enter gesture label: ").strip().upper()

reference_number = input(
                    "Enter reference number: "
                ).strip()

# Define paths
reference_image_path = (f"reference_gestures/reference_images/{gesture_label}.png")

# CSV output folder
output_folder = (f"reference_gestures/{gesture_label}")

# CSV output path
output_csv_path = (f"{output_folder}/ref{reference_number}.csv")


# Check if reference image exists
if not os.path.exists(reference_image_path):
    print("\nError:")
    print(f"Reference image not found:\n"
          f"{reference_image_path}") 
    #print("\nPlease ensure the reference image is available.")
    #print("reference_gestures/"
        #"reference_images/"
        #f"{gesture_label}.png")
    
    hands.close()
    exit(1)

# Load reference image
reference_png = cv2.imread(reference_image_path, cv2.IMREAD_UNCHANGED)

if reference_png is None:
    print(f"Error: Could not load image:\n"
          f"{reference_image_path}")
    hands.close()
    exit(1)

print(f"Reference image loaded:"
      f"{reference_image_path}")

# Transparent background handling
# Handle png alpha channel if present
if len(reference_png.shape) == 3 and reference_png.shape[2] == 4:

    # Separate BGR and alpha
    bgr_image = reference_png[:, :, :3]
    alpha_channel = reference_png[:, :, 3]

    # Create a white background
    #white_background = (255 * __import__("numpy").ones_like(bgr_image))
    background = np.ones_like(bgr_image) * 255

    # Create black background
    #black_background = (
        #__import__("numpy").zeros_like(bgr_image)
    #)

    alpha_float = (alpha_channel[:, :, None] / 255.0)

    # Blend with white background
    bgr_image = (
        bgr_image * alpha_float
        + background * (1 - alpha_float)
    ).astype(np.uint8)

    # Convert transparent areas to white
    #alpha_float = alpha_channel[:, :, None] / 255.0
    #bgr_image = (bgr_image * alpha_float + white_background * (1 - alpha_float)).astype("uint8")

else:
    bgr_image = reference_png.copy()

# Prepare image for MediaPipe

# Enlarge image for detection
scale_factor = 2.5

# Get original image size
original_h, original_w = bgr_image.shape[:2]

# Enlarge image before MediaPipe detection
#scale_factor = 2.5
new_w = int(original_w * scale_factor)
new_h = int(original_h * scale_factor)

detection_image = cv2.resize(
    bgr_image,
    (new_w, new_h),
    interpolation=cv2.INTER_CUBIC
)

# Convert to RGB
rgb_image = cv2.cvtColor(
    detection_image, 
    cv2.COLOR_BGR2RGB
)

# Detect hand
results = hands.process(rgb_image)

landmark_points = []

# If MediaPipe detects hand
if results.multi_hand_landmarks:
    print(
        "\nMediaPipe successfully detected "
        "the hand!"
    )

    detected_hand =(
        results.multi_hand_landmarks[0]
    )

    # Convert normalized MediaPipe coordinates back to orignal PNG coordinates
    for lm in detected_hand.landmark:
        x = lm.x * new_w
        y = lm.y * new_h

        # Convert back to original image size
        x = x / scale_factor
        y = y / scale_factor
        landmark_points.append((x, y))

# If MediaPipe fails
else:
    print(
        "\nMediaPipe could not detect the hand automatically."
    )
    print(
        "\nSwitching to MANUAL LANDMARK MODE."
    )
    print(
        "\nYou need to click the 21 hand joints in the correct order."
    )
    print(
        "\nLandmark order: "
    )
    print(
        "0  Wrist"
    )

    print(
        "1  Thumb CMC"
    )
    print(
        "2  Thumb MCP"
    )
    print(
        "3  Thumb IP"
    )
    print(
        "4  Thumb Tip"
    )

    print(
        "5  Index MCP"
    )
    print(
        "6  Index PIP"
    )
    print(
        "7  Index DIP"
    )
    print(
        "8  Index Tip"
    )

    print(
        "9  Middle MCP"
    )
    print(
        "10 Middle PIP"
    )
    print(
        "11 Middle DIP"
    )
    print(
        "12 Middle Tip"
    )

    print(
        "13 Ring MCP"
    )
    print(
        "14 Ring PIP"
    )
    print(
        "15 Ring DIP"
    )
    print(
        "16 Ring Tip"
    )

    print(
        "17 Pinky MCP"
    )
    print(
        "18 Pinky PIP"
    )
    print(
        "19 Pinky DIP"
    )
    print(
        "20 Pinky Tip"
    )

    print(
        "\nClick the points directly on the image."
    )

    print(
        "Press R to reset the current points."
    )

    print(
        "Press Q to cancel."
    )

    # Manual click callback
    manual_points = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(manual_points) < 21:
                manual_points.append((x, y))
                print(f"Point "
                      f"{len(manual_points) - 1}: "
                      f"({x}, {y})")
                
    # Create manual window
    manual_image = bgr_image.copy()
    cv2.namedWindow("Manual Landmark Selection")
    cv2.setMouseCallback("Manual Landmark Selection", mouse_callback)

    # Manual landmark loop
    while True:
        display_image = manual_image.copy()

        # Draw existing points
        for i, point in enumerate(manual_points):
            cv2.circle(display_image, point, 5, (0, 0, 255), -1)
            cv2.putText(
                display_image,
                str(i),
                (   point[0] + 5, 
                    point[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )
        
        # Draw connections
        if len(manual_points) > 1:
            for connection in (
                mp_hands.HAND_CONNECTIONS
            ):
                start = connection[0]
                end = connection[1]

                if (
                    start < len(manual_points)
                    and end < len(manual_points)
                ):
                    cv2.line(
                        display_image,
                        manual_points[start],
                        manual_points[end],
                        (255, 255, 255),
                        2,
                    )

        # Instructions
        cv2.putText(
            display_image,
            f"Point: {len(manual_points)}/21",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            display_image,
            "Click points | R = Reset | S = Save | Q = Quit",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
        )

        cv2.imshow(
            "Manual Landmark Selection",
            display_image
        )

        key = cv2.waitKey(1) & 0xFF

        # Reset
        if key == ord('r'):
            manual_points.clear()
            print("Points reset.")

        # Save
        elif key == ord('s'):
            if len(manual_points) == 21:
                landmark_points = (manual_points.copy())
                print("\nAll 21 landmarks selected!")
                break
            else:
                print(
                    f"\nYou have selected "
                    f"{len(manual_points)} points. "
                )
                print(
                    "You need exactly 21 points."
                )

        # Quit
        elif key in [
            ord('q'), 27  # 'q' or ESC
        ]:
            print(
                "\nCancelled."
            )
            cv2.destroyAllWindows()
            hands.close()
            exit(0)
        
    cv2.destroyWindow(
        "Manual Landmark Selection"
    )       

# Check landmarks
if len(landmark_points) != 21:
    print(
        "\nERROR: Expected 21 landmarks."
    )
    hands.close()
    exit(1)

# Normalize landmarks
# Same method as gesture_accuracy.py

wrist_x, wrist_y = landmark_points[0]
middle_mcp_x, middle_mcp_y = landmark_points[9]

scale = (
    ((middle_mcp_x - wrist_x) ** 2)
    + ((middle_mcp_y - wrist_y) ** 2)
) ** 0.5

if scale == 0:
    scale = 1

landmark_data = []

for x, y in landmark_points:
    normalized_x = (x - wrist_x) / scale
    normalized_y = (y - wrist_y) / scale
    landmark_data.append(normalized_x)
    landmark_data.append(normalized_y)

# Create output folder
os.makedirs(output_folder, exist_ok=True)

# Save csv
with open(
    output_csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(landmark_data)

print(
    "\n================================"
)
print(
    "Reference landmarks saved successfully!"
)
print(
    "================================"
)
print(
    f"Gesture: {gesture_label}"
)
print(
    f"Reference: {reference_number}"
)
print(
    f"Landmarks: {len(landmark_points)}"
)
print(
    f"Saved to: {output_csv_path}"
)

# Show reference with landmarks drawn
preview_image = bgr_image.copy()

# Draw joints
for i, point in enumerate(landmark_points):
    cv2.circle(preview_image,
               (int(point[0]), int(point[1])), 5, (255, 0, 0), -1)

    cv2.putText(
        preview_image,
        str(i),
        (int(point[0]) + 5, int(point[1]) - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        2,
    )

# Draw skeleton
for connection in (mp_hands.HAND_CONNECTIONS
):
    start = connection[0]
    end = connection[1]

    pt1 = (
        int(landmark_points[start][0]),
        int(landmark_points[start][1])
    )
    pt2 = (
        int(landmark_points[end][0]),
        int(landmark_points[end][1])
    )

    cv2.line(preview_image, pt1, pt2, (255, 255, 255), 2)

cv2.imshow(
    "Saved Reference Landmarks",
    preview_image
)

print(
    "\nPress any key to close the preview."
)

cv2.waitKey(0)
cv2.destroyAllWindows()
hands.close()
