#run: python -m pip install mediapipe
#run: !wget -q https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task
#run: sudo apt-get install python3-opencv
import mediapipe as mp
import cv2 as cv
import time
import numpy as np
import sys
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# print(cv.__version__) # project written in 4.10.0

BaseOptions = mp.tasks.BaseOptions
# https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python#configuration_options list of options
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

model_path = 'gesture_recognizer.task' # change path as needed (input? detection?)

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode


# Create a gesture recognizer instance with the live stream mode:
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    print('gesture recognition result: {}'.format(result))


options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)
recognizer = GestureRecognizer.create_from_options(options)

# Use OpenCV’s VideoCapture to start capturing from the webcam.
# Create a loop to read the latest frame from the camera using VideoCapture#read()
# Convert the frame received from OpenCV to a MediaPipe’s Image object.

cam = cv.VideoCapture(0, cv.CAP_DSHOW)
start_time = cv.getTickCount()

# Get the default frame width and height
frame_width = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'mp4v')
out = cv.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

while True:
    ret, frame = cam.read()

    # Write the frame to the output file
    if (ret):
      out.write(frame)
      mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
      # frame_timestamp_ms = int(time.perf_counter() * 20)
      frame_timestamp_ms = int((cv.getTickCount() - start_time) * 1000 / cv.getTickFrequency())
      recognizer.recognize_async(mp_image, frame_timestamp_ms)

      # Display the captured frame
      cv.imshow('Camera', frame)

    # Press 'q' to exit the loop
    if cv.waitKey(1) == ord('q'):
        break

# Load the last frame as a numpy array into mediapipe

# The Gesture Recognizer uses the recognize (for images), recognize_for_video (for video)
# and recognize_async (for live) functions to trigger inferences. For gesture recognition,
# this involves preprocessing input data, detecting hands in the image, detecting hand
# landmarks, and recognizing hand gesture from the landmarks.

# Send live image data to perform gesture recognition.
# The results are accessible via the `result_callback` provided in
# the `GestureRecognizerOptions` object.
# The gesture recognizer must be created with the live stream mode.
# recognizer.recognize_async(mp_image, frame_timestamp_ms)
# When running in the video mode or the live stream mode, you must
# also provide the Gesture Recognizer task the timestamp of the input frame.
# When running in the live stream mode, the Gesture Recognizer task doesn’t
# block the current thread but returns immediately. It will invoke its result
# listener with the recognition result every time it has finished processing an
# input frame. If the recognition function is called when the Gesture Recognizer
# task is busy processing another frame, the task will ignore the new input frame.

# Release the capture and writer objects
cam.release()
out.release()
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