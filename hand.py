import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize MediaPipe Hand object and drawing utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Get screen size for mapping hand coordinates
screen_width, screen_height = pyautogui.size()

# Capture video from the webcam with reduced resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Previous position for smoothing cursor movement
prev_x, prev_y = 0, 0
smooth_factor = 0.5  # Adjust for smoothing effect (0 to 1)

# Cursor lock state
cursor_locked = False
app_closing = False  # Flag to prevent repeated closing

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for natural mirror view
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame and detect hands
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]  # Assuming only one hand detected
        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]  # Use index finger tip
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

        # Map the hand coordinates to screen coordinates
        screen_x = int(index_finger_tip.x * screen_width)
        screen_y = int(index_finger_tip.y * screen_height)

        # Smooth the cursor movement
        smooth_x = int(prev_x + (screen_x - prev_x) * smooth_factor)
        smooth_y = int(prev_y + (screen_y - prev_y) * smooth_factor)

        # Move the mouse cursor if not locked
        if not cursor_locked:
            pyautogui.moveTo(smooth_x, smooth_y)
            prev_x, prev_y = smooth_x, smooth_y

        # Draw a circle on the index finger tip
        cv2.circle(frame, (int(index_finger_tip.x * 640), int(index_finger_tip.y * 480)), 10, (0, 255, 255), -1)

        # Calculate the distance between index finger tip and thumb for click detection
        distance = np.linalg.norm(np.array([screen_x, screen_y]) - np.array([thumb_tip.x * screen_width, thumb_tip.y * screen_height]))

        # Right-click if index finger tip and thumb are close
        if distance < 50:
            pyautogui.click(button='right')  # Right-click action

        # Implement closing app with right-click gesture (thumb and index together)
        if thumb_tip.y < index_finger_tip.y:  # Thumb above index finger tip
            if not app_closing:  # Only close if not already closing
                app_closing = True
                break  # Exit the app if gesture detected
        else:
            app_closing = False  # Reset the flag if gesture is not detected

        # Count extended fingers
        extended_fingers = 0

        # Check each finger's state
        for i in range(5):  # Check all fingers
            finger_tip = hand_landmarks.landmark[i * 4 + 2]  # Get the tip of the finger
            finger_mcp = hand_landmarks.landmark[i * 4]  # Get the base of the finger

            if finger_tip.y < finger_mcp.y:  # Check if the finger is extended
                extended_fingers += 1

        # Lock cursor if three fingers are extended
        if extended_fingers >= 3:
            cursor_locked = True  # Lock cursor movement
            print("Cursor locked")
        else:
            cursor_locked = False  # Unlock cursor movement

    # Show the webcam feed with hand tracking
    cv2.imshow('Virtual Mouse', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
