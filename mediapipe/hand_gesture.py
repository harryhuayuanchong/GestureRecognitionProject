import cv2
import mediapipe as mp
import socket

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5052)

def count_fingers(hand_landmarks, hand_label):
    # Define the landmarks for the finger tips and the base of each finger
    tips = [4, 8, 12, 16, 20]  # Indexes for the tips of each finger
    base = [2, 5, 9, 13, 17]   # Indexes for the base of each finger

    fingers = []
    
    # Thumb: check if it's extended
    if hand_label == "Left":
        if hand_landmarks.landmark[tips[0]].x > hand_landmarks.landmark[base[0]].x:
            fingers.append(1)
        else:
            fingers.append(0)
    else:
        if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[base[0]].x:
            fingers.append(1)
        else:
            fingers.append(0)
    
    # Other fingers: check if they are extended
    for tip, b in zip(tips[1:], base[1:]):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[b].y:
            fingers.append(1)
        else:
            fingers.append(0)
    
    # Calculate the number of extended fingers
    count = sum(fingers)
    return count

def main():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
        
    else:
        print("Camera opened successfully")
    
    with mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            data = []

            if results.multi_hand_landmarks:
                h, w, _ = image.shape
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Get the hand label
                    hand_label = handedness.classification[0].label

                    # Count extended fingers
                    fingers_count = count_fingers(hand_landmarks, hand_label)

                    # Append the hand data
                    lmList = [
                        (int(landmark.x * w), int(landmark.y * h), int(landmark.z * w))
                        for landmark in hand_landmarks.landmark
                    ]
                    
                    # to json()
                    for lm in lmList:
                        data.extend([lm[0], h - lm[1], lm[2]])

                    # Append the fingers count to the data
                    data.append(fingers_count)
                    
                sock.sendto(str.encode(str(data)), server_address)
                
            print(data)
            
            image = cv2.resize(image, (0,0), None, 0.5, 0.5)

            cv2.imshow('Hand Gesture Recognition', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
