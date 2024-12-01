FROM python:3.8-slim

WORKDIR /app
COPY . /app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir opencv-python
RUN pip install --no-cache-dir mediapipe
RUN wget -q https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task -O /app/gesture_recognizer.task
CMD ["python", "main.py"]

# docker build -t sign-language-detector .
# docker run -it --rm sign-language-detector
