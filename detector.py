#run: python -m pip install mediapipe
#run: !wget -q https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task
#run: sudo apt-get install python3-opencv
import mediapipe as mp
import cv2 as cv
from mediapipe.tasks import python
import difflib

# print(cv.__version__) # project written in 4.10.0
# def setup_detector():
BaseOptions = mp.tasks.BaseOptions
# https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python#configuration_options list of options
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

model_path = 'gesture_recognizer.task'# change path as needed (input? detection?)
with open('wordle/words.txt', 'r') as file:
    possibilities = [line.strip() for line in file.readlines()]

center = [(0, 0) for _ in range(21)]
score = 0
category = "not detected"

# Create a gesture recognizer instance with the live stream mode:
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global center
    global score
    global category
    if (result.hand_landmarks.__sizeof__() == 40):
        center = [(0, 0) for _ in range(21)]
        score = 0
        category = "not detected"
    for landmark in result.hand_landmarks:
        for i in range(0, 21):
            center[i] = (int(frame_width * landmark[i].x), int(frame_height * landmark[i].y))
    for gesture in result.gestures:
        score = gesture[0].score
        category = gesture[0].category_name

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)
recognizer = GestureRecognizer.create_from_options(options)

cam = cv.VideoCapture(0, cv.CAP_DSHOW)
start_time = cv.getTickCount()
last = start_time

# Get the default frame width and height
frame_width = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))

letters = ""
while True:
    ret, frame = cam.read()

    # Write the frame to the output file
    if (ret):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        frame_timestamp_ms = int((cv.getTickCount() - start_time) * 1000 / cv.getTickFrequency())
        recognizer.recognize_async(mp_image, frame_timestamp_ms)
        radius = 2
        color = (239, 3, 7)
        color2 = (100, 2, 5)
        color3 = (251, 182, 151)
        thickness = 2
        thickness2 = -1
        for i in range(0, 21):
            cv.circle(frame, center[i], radius, color, thickness)
            if (i < 4 or (i >= 5 and i < 8) or (i >= 9 and i < 12) or (i >= 13 and i < 16) or (i >= 17 and i < 20)):
                cv.line(frame, center[i], center[i+1], color2, thickness)
            if(i > 1 and i < 17 and i % 4 == 1):
                cv.line(frame, center[i], center[i + 4], color2, thickness)
        cv.line(frame, center[0], center[5], color2, thickness)
        cv.line(frame, center[0], center[17], color2, thickness)
        position = (200, 450)
        font = cv.FONT_HERSHEY_TRIPLEX
        font_scale = 0.8
        font_color = (0, 0, 0)
        line_type = cv.LINE_AA
        cv.putText(frame, category, position, font, font_scale, font_color, thickness, line_type)
        cv.rectangle(frame, (400, 432), (600, 455), color3, thickness2)
        position2 = (406, 448)
        font2 = cv.FONT_HERSHEY_TRIPLEX
        font_scale2 = 0.5
        font_color2 = (0, 0, 0)
        procentaj = int(score * 100)
        procentaj2 = int(400 + 200 * procentaj / 100)
        cv.rectangle(frame, (400, 432), (procentaj2, 455), color, thickness2)

        string = "%"
        position3 = (428, 448)
        text = str(procentaj)
        cv.putText(frame, text, position2, font2, font_scale2, font_color2, thickness, line_type)
        cv.putText(frame, string, position3, font2, font_scale2, font_color2, thickness, line_type)

        # Display the captured frame
        cv.imshow('Camera', frame)

    if (category == "" or category == "not detected" or category == "none"):
        last = cv.getTickCount()
        score = 0
    if (category != "" and category != "not detected" and category != "none" and cv.getTickCount() - last >= 2000000000):
        letters += category
        print(letters)
        last = cv.getTickCount()
    
    # Press 'q' to exit the loop
    if cv.waitKey(1) == ord('q'):
        break

letters = letters.lower()
if letters not in possibilities:
    result = difflib.get_close_matches(letters, possibilities)
    print(result)

cam.release()
cv.destroyAllWindows()

# TODO List:
# 1. Capture live video feed from the webcam using OpenCV.
# 2. Convert the OpenCV frame to a MediaPipe Image object.
# 3. Send the image to the Gesture Recognizer for gesture recognition.
# 4. Display the recognized gesture on the frame.
# 5. Display the frame with the recognized gesture in a window.
# 6. Repeat steps 1-5 for every frame captured from the webcam.

# 7. Implement a gesture recognition model using MediaPipe’s Gesture Recognizer.
# 8. Teach the model the new required gestures.
# 9. Test the model with the new gestures.

# 10. Implement an API to get today's wordle solution.
# 11. Implement a simple wordle game.

# 12. Implement graphic interface to show the letters corresponding to the gestures.
# 13. Implement graphic interface for the wordle game.

# 14. Implement a typo-correcting model.
# 15. Do... something???

# 16. Implement video gesture recognition.
# 17. Implement image gesture recognition.