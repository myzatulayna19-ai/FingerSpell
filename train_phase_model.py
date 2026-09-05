import pandas as pd
import numpy as np
import joblib
import glob
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# =========================================================
# 1. FIND ALL REFERENCE CSV FILES
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_files = glob.glob(
    os.path.join(BASE_DIR, "reference_data", "*_landmarks.csv")
)

if not csv_files:

    print(
        "Error: No landmark CSV files found "
        "in 'reference_data/'."
    )

    exit()


print(
    f"Found {len(csv_files)} gesture file(s)."
)


# =========================================================
# 2. LOAD ALL GESTURE DATA
# =========================================================

all_dfs = []


for file in csv_files:

    print(
        f"\nLoading: {file}"
    )


    df = pd.read_csv(
        file
    )


    # -----------------------------------------------------
    # Gesture name from filename
    # -----------------------------------------------------

    gesture_name = (

        os.path.basename(file)

        .replace(
            "_landmarks.csv",
            ""
        )
    )


    df["gesture"] = (
        gesture_name
    )


    # -----------------------------------------------------
    # Create target label
    #
    # Example:
    # assalamualaikum_1
    # assalamualaikum_2
    # apa_khabar_1
    # apa_khabar_2
    # -----------------------------------------------------

    df["gesture_phase"] = (

        df["gesture"].astype(str)

        + "_"

        + df["phase"].astype(str)
    )


    all_dfs.append(
        df
    )


# =========================================================
# 3. COMBINE ALL GESTURES
# =========================================================

full_df = pd.concat(
    all_dfs,
    ignore_index=True
)


print(
    "\nGestures loaded:"
)

print(
    full_df[
        "gesture"
    ].unique().tolist()
)


print(
    "\nPhase labels:"
)

print(
    full_df[
        "gesture_phase"
    ].unique().tolist()
)


# =========================================================
# 4. CHECK TWO-HAND DATA
# =========================================================

left_columns = [

    f"left_x_{i}"

    for i in range(21)
]

right_columns = [

    f"right_x_{i}"

    for i in range(21)
]


missing_left = [

    col

    for col in left_columns

    if col not in full_df.columns
]


missing_right = [

    col

    for col in right_columns

    if col not in full_df.columns
]


if missing_left:

    print(
        "\nWARNING:"
    )

    print(
        "Left-hand landmark columns "
        "are missing."
    )

    print(
        missing_left
    )


if missing_right:

    print(
        "\nWARNING:"
    )

    print(
        "Right-hand landmark columns "
        "are missing."
    )

    print(
        missing_right
    )


if not missing_left and not missing_right:

    print(
        "\n✓ Two-hand landmark data detected."
    )


# =========================================================
# 5. DEFINE FEATURE COLUMNS
# =========================================================

exclude_cols = [

    # Metadata
    "frame",
    "phase",
    "gesture",
    "gesture_phase",

    # Old/internal columns
    "_raw_landmarks",
    "_left_raw_landmarks",
    "_right_raw_landmarks"
]


feature_cols = [

    col

    for col in full_df.columns

    if col not in exclude_cols
]

print("\nALL FEATURES:")
for col in feature_cols:
    print(col)

print("\nTOTAL FEATURES:", len(feature_cols))


# =========================================================
# 6. REMOVE NON-NUMERIC COLUMNS
# =========================================================

numeric_feature_cols = []


for col in feature_cols:

    if pd.api.types.is_numeric_dtype(
        full_df[col]
    ):

        numeric_feature_cols.append(
            col
        )


feature_cols = (
    numeric_feature_cols
)


# =========================================================
# 7. PRINT FEATURE INFORMATION
# =========================================================

print(
    "\n======================================"
)

print(
    "FEATURE INFORMATION"
)

print(
    "======================================"
)

print(
    f"Number of features: "
    f"{len(feature_cols)}"
)


print(
    "\nFeature columns:"
)

for idx, col in enumerate(
    feature_cols,
    start=1
):

    print(
        f"{idx}. {col}"
    )


# =========================================================
# 8. PREPARE X AND Y
# =========================================================

X = full_df[
    feature_cols
].copy()
X = X.fillna(0)


y = full_df[
    "gesture_phase"
].copy()


# =========================================================
# 9. HANDLE MISSING VALUES
# =========================================================

print(
    "\nChecking missing values..."
)


missing_count = (
    X.isna()
    .sum()
    .sum()
)


print(
    f"Total missing feature values: "
    f"{missing_count}"
)


if missing_count > 0:

    print(
        "Filling missing values with 0."
    )

    X = X.fillna(
        0
    )


# Convert to numpy

X = X.values

y = y.values


# =========================================================
# 10. CHECK CLASS COUNTS
# =========================================================

print(
    "\n======================================"
)

print(
    "CLASS DISTRIBUTION"
)

print(
    "======================================"
)


unique_classes, counts = (
    np.unique(
        y,
        return_counts=True
    )
)


for class_name, count in zip(
    unique_classes,
    counts
):

    print(
        f"{class_name}: "
        f"{count} samples"
    )


# =========================================================
# 11. CHECK WHETHER STRATIFIED SPLIT IS SAFE
# =========================================================

minimum_class_count = (
    np.min(counts)
)


if minimum_class_count < 2:

    print(
        "\nERROR:"
    )

    print(
        "At least 2 samples are required "
        "for every gesture phase."
    )

    print(
        "Record more reference frames "
        "for the affected phase."
    )

    exit()


# =========================================================
# 12. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = (

    train_test_split(

        X,

        y,

        test_size=0.2,

        random_state=42,

        stratify=y
    )
)


print(
    "\nTraining samples:",
    len(X_train)
)

print(
    "Testing samples:",
    len(X_test)
)


# =========================================================
# 13. TRAIN RANDOM FOREST
# =========================================================

print(
    "\n======================================"
)

print(
    "TRAINING TWO-HAND AI MODEL"
)

print(
    "======================================"
)


model = RandomForestClassifier(

    n_estimators=200,

    random_state=42,

    class_weight="balanced",

    n_jobs=-1
)


model.fit(
    X_train,
    y_train
)


print(
    "\nTraining complete!"
)


# =========================================================
# 14. EVALUATE MODEL
# =========================================================

y_pred = (
    model.predict(
        X_test
    )
)


accuracy = (
    accuracy_score(
        y_test,
        y_pred
    )
)


print(
    "\n======================================"
)

print(
    "MODEL RESULTS"
)

print(
    "======================================"
)


print(
    f"Accuracy: "
    f"{accuracy * 100:.2f}%"
)


print(
    "\nClassification Report:"
)


print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# =========================================================
# 15. FEATURE IMPORTANCE
# =========================================================

print(
    "\n======================================"
)

print(
    "TOP IMPORTANT FEATURES"
)

print(
    "======================================"
)


feature_importance = (

    pd.DataFrame({

        "feature":
            feature_cols,

        "importance":
            model.feature_importances_

    })

    .sort_values(
        "importance",
        ascending=False
    )
)


print(
    feature_importance.head(20)
)


# =========================================================
# 16. SAVE MODEL
# =========================================================

model_payload = {

    "model":
        model,

    "feature_cols":
        feature_cols
}


joblib.dump(

    model_payload,

    "gesture_phase_model.pkl"
)


print(
    "\n======================================"
)

print(
    "MODEL SAVED"
)

print(
    "======================================"
)


print(
    "Saved to:"
)

print(
    "gesture_phase_model.pkl"
)


print(
    f"Total features saved: "
    f"{len(feature_cols)}"
)


print(
    "\nTraining finished successfully!"
)