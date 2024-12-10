import mediapipe as mp
import cv2 as cv
from mediapipe.tasks import python
# import difflib

class GestureRecognizer:
    def __init__(self, model_path='gesture_recognizer.task', words_file='words.txt'):
        self.model_path = model_path
        self.possibilities = self.load_word_list(words_file)
        self.center = [(0, 0) for _ in range(21)]
        self.score = 0
        self.category = "not detected"
        self.letters = ""
        self.last = 0
        self.start_time = cv.getTickCount()

        # Setup MediaPipe Gesture Recognizer
        self.BaseOptions = mp.tasks.BaseOptions
        self.GestureRecognizer = mp.tasks.vision.GestureRecognizer
        self.GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        self.GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
        self.VisionRunningMode = mp.tasks.vision.RunningMode

        # Initialize the recognizer
        self.recognizer = self.initialize_gesture_recognizer()

        # Initialize the camera
        self.cam = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.frame_width = int(self.cam.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cam.get(cv.CAP_PROP_FRAME_HEIGHT))

    def display_hand(self):
        cv.imshow("image", self.image)
        cv.waitKey(1)

    def load_word_list(self, words_file):
        with open(words_file, 'r') as file:
            return [line.strip() for line in file.readlines()]

    def initialize_gesture_recognizer(self):
        def print_result(result: self.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
            if (result.hand_landmarks.__sizeof__() == 40):
                self.center = [(0, 0) for _ in range(21)]
                self.score = 0
                self.category = "not detected"
            for landmark in result.hand_landmarks:
                for i in range(0, 21):
                    self.center[i] = (int(self.frame_width * landmark[i].x), int(self.frame_height * landmark[i].y))
            for gesture in result.gestures:
                self.score = gesture[0].score
                self.category = gesture[0].category_name

        options = self.GestureRecognizerOptions(
            base_options=self.BaseOptions(model_asset_path=self.model_path),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=print_result
        )
        return self.GestureRecognizer.create_from_options(options)

    def process_frame(self, frame):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        frame_timestamp_ms = int((cv.getTickCount() - self.start_time) * 1000 / cv.getTickFrequency())
        self.recognizer.recognize_async(mp_image, frame_timestamp_ms)

        radius = 2
        color = (239, 3, 7)
        color2 = (100, 2, 5)
        color3 = (251, 182, 151)
        thickness = 2
        thickness2 = -1

        # Draw landmarks and gestures on frame
        for i in range(0, 21):
            cv.circle(frame, self.center[i], radius, color, thickness)
            if (i < 4 or (i >= 5 and i < 8) or (i >= 9 and i < 12) or (i >= 13 and i < 16) or (i >= 17 and i < 20)):
                cv.line(frame, self.center[i], self.center[i+1], color2, thickness)
            if(i > 1 and i < 17 and i % 4 == 1):
                cv.line(frame, self.center[i], self.center[i + 4], color2, thickness)
        cv.line(frame, self.center[0], self.center[5], color2, thickness)
        cv.line(frame, self.center[0], self.center[17], color2, thickness)

        # Display category and score
        position = (200, 450)
        font = cv.FONT_HERSHEY_TRIPLEX
        font_scale = 0.8
        font_color = (0, 0, 0)
        line_type = cv.LINE_AA
        if (self.category == "none"):
            self.category = "backspace"
        cv.putText(frame, self.category, position, font, font_scale, font_color, thickness, line_type)

        cv.rectangle(frame, (400, 432), (600, 455), color3, thickness2)
        position2 = (406, 448)
        font2 = cv.FONT_HERSHEY_TRIPLEX
        font_scale2 = 0.5
        font_color2 = (0, 0, 0)
        procentaj = int(self.score * 100)
        procentaj2 = int(400 + 200 * procentaj / 100)
        cv.rectangle(frame, (400, 432), (procentaj2, 455), color, thickness2)

        string = "%"
        position3 = (428, 448)
        text = str(procentaj)
        cv.putText(frame, text, position2, font2, font_scale2, font_color2, thickness, line_type)
        cv.putText(frame, string, position3, font2, font_scale2, font_color2, thickness, line_type)

        return frame

    def recognize_gesture(self):
        while True:
            ret, frame = self.cam.read()

            if ret:
                frame = self.process_frame(frame)
                cv.imshow('Camera', frame)

            if self.category == "" or self.category == "not detected" or self.category == "none":
                self.last = cv.getTickCount()
                self.score = 0
            if self.category != "" and self.category != "not detected" and self.category != "none" and cv.getTickCount() - self.last >= 2000000000:
                self.letters += self.category
                print(self.letters)
                self.last = cv.getTickCount()

            # Press 'q' to exit the loop
            if cv.waitKey(1) == ord('q'):
                break

        # self.evaluate_gesture()

    # def evaluate_gesture(self):
    #     self.letters = self.letters.lower()
    #     if self.letters not in self.possibilities:
    #         result = difflib.get_close_matches(self.letters, self.possibilities)
    #         print(result)

    def cleanup(self):
        self.cam.release()
        cv.destroyAllWindows()


# Usage example:
if __name__ == "__main__":
    game = GestureRecognizer()
    game.recognize_gesture()
    game.cleanup()
