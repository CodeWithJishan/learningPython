import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Initialize Mediapipe Face Mesh and Drawing Utilities
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Get screen size for mapping eye coordinates
screen_width, screen_height = pyautogui.size()

# Capture video from the webcam
cap = cv2.VideoCapture(0)

# Previous position for smoothing cursor movement
prev_x, prev_y = 0, 0
smooth_factor = 0.5  # Adjust for smoothing effect (0 to 1)

# Cursor lock state
cursor_locked = False

# Duration to close the app when both eyes are closed
close_app_duration = 1  # seconds
last_closed_time = None

def is_eye_closed(eye_landmarks):
    # Calculate distances between specific landmarks for eye openness
    vertical_length = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])  # Vertical distance
    horizontal_length = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])  # Horizontal distance
    return vertical_length / horizontal_length < 0.2  # Adjust threshold as needed

with mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.7) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for natural mirror view
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and detect face landmarks
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get left and right eye landmarks
                left_eye = np.array([(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in range(33, 134)])
                right_eye = np.array([(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in range(362, 463)])

                # Calculate the center of the eyes
                left_eye_center = np.mean(left_eye, axis=0)
                right_eye_center = np.mean(right_eye, axis=0)

                # Find the midpoint between the two eyes
                eye_center_x = int((left_eye_center[0] + right_eye_center[0]) / 2 * screen_width)
                eye_center_y = int((left_eye_center[1] + right_eye_center[1]) / 2 * screen_height)

                # Smooth the cursor movement
                smooth_x = int(prev_x + (eye_center_x - prev_x) * smooth_factor)
                smooth_y = int(prev_y + (eye_center_y - prev_y) * smooth_factor)

                # Move the mouse cursor
                if not cursor_locked:
                    pyautogui.moveTo(smooth_x, smooth_y)
                    prev_x, prev_y = smooth_x, smooth_y

                # Check if the left or right eye is closed
                left_eye_closed = is_eye_closed(left_eye)
                right_eye_closed = is_eye_closed(right_eye)

                # Right-click if left eye is closed and right is open
                if left_eye_closed and not right_eye_closed:
                    pyautogui.click(button='right')  # Right-click action
                    cv2.putText(frame, "Right Click", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Left-click if right eye is closed and left is open (optional)
                if right_eye_closed and not left_eye_closed:
                    pyautogui.click(button='left')  # Left-click action
                    cv2.putText(frame, "Left Click", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                # Check if both eyes are closed
                if left_eye_closed and right_eye_closed:
                    if last_closed_time is None:
                        last_closed_time = time.time()  # Start the timer
                    elif time.time() - last_closed_time >= close_app_duration:
                        print("Closing application...")
                        cap.release()
                        cv2.destroyAllWindows()
                        exit()  # Close the application
                else:
                    last_closed_time = None  # Reset the timer if any eye is open

                # Draw circles on the eye centers for visualization
                cv2.circle(frame, (smooth_x, smooth_y), 10, (0, 255, 255), -1)

        # Show the webcam feed with eye tracking
        cv2.imshow('Eye Tracking Virtual Mouse', frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()
