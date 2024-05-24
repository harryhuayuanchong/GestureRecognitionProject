import cv2
import mediapipe as mp
import socket

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5052)

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
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    lmList = [
                        (int(landmark.x * w), int(landmark.y * h), int(landmark.z * w))
                        for landmark in hand_landmarks.landmark
                    ]
                    
                    # testing_data.extend(lmList)
                    
                    # to json()
                    for lm in lmList:
                        data.extend([lm[0], h - lm[1], lm[2]])
                    
                sock.sendto(str.encode(str(data)), server_address)
                
            print(results.multi_handedness)
            
            image = cv2.resize(image, (0,0), None, 0.5, 0.5)

            cv2.imshow('Hand Gesture Recognition', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
