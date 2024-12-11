# Wordle Game with Gesture Recognition

This project is an advanced Wordle game implementation, combining gesture recognition for input via a camera feed and a graphical user interface (GUI) for interaction. The game is built using Python and integrates multiple libraries such as `pygame`, `mediapipe`, and `opencv`.

## Features

- **Main Menu**:
  - Start a Wordle game.
  - Input text with a virtual keyboard.
  - Quit the application.
- **Gesture Recognition**:
  - Detect hand gestures to input letters into the game.
- **Dynamic Word Suggestions**:
  - Provides suggestions for similar words when an invalid word is entered.
- **Animations**:
  - Includes tile and alphabet animations for an engaging experience.
- **Word Sourcing**:
  - Words are fetched from a local `words.txt` file or an API.

## How to Play Wordle

1. **Objective**:
   - Guess the hidden 5-letter word within six attempts.

2. **Gameplay**:
   - Enter a 5-letter word guess using gestures or the keyboard.
   - After submitting a guess, the tiles will change color:
     - **Green**: Letter is correct and in the correct position.
     - **Yellow**: Letter is correct but in the wrong position.
     - **Gray**: Letter is not in the word.

3. **Hints**:
   - Use the dynamic word suggestions for help if you enter an invalid word.

4. **Win Condition**:
   - Successfully guess the hidden word within the allowed attempts.

5. **Lose Condition**:
   - Fail to guess the word in six attempts.

6. **Word Solutions**:
   - The first solution is the daily solution fetched from the New York Times API. All subsequent solutions are picked randomly from a comprehensive list of 5-letter English words.

### **Automatic Key Inputs**  
During gameplay, you don't need to hit the Enter or Backspace keys manually. Enter will be automatically triggered 20 seconds after typing the last letter if Backspace hasn't been pressed. Similarly, Backspace will automatically activate a few seconds after entering an invalid word. 

### **Simple Writing Mode**  
For demonstration purposes, there's also a simple writing mode. The writing mode uses a different model that implements space to allow for easier input of text.

Enjoy the animations and visual feedback as you play!

## Usage

1. Run the script:

   ```bash
   python main.py
   ```

2. Navigate the main menu using the arrow keys and select an option by pressing `Enter`.

3. During gameplay:
   - Use hand gestures (via the camera) to input letters and to hit Backspace. Enter is automatic. 
   - Using the keyboard for additional controls is possible, but not mandatory:
     - `Backspace` to delete a letter.
     - `Enter` to submit a word.

4. Sign list:
    - Hovering over the letters will display the corresponding sign.

5. Enjoy animations and feedback during the game.

## File Structure

- `main.py`: The entry point of the application.
- `detector.py`: Implements gesture recognition logic using MediaPipe.
- `settings.py`: Handles configuration and game settings.
- `sprites.py`: Manages animations and graphical elements.
- `gesture_recognizer.task`: Model for hand gesture recognition.
- `words.txt`: A list of valid words for the game.

## Libraries Used

- **Pygame**: For creating the GUI and managing animations.
- **OpenCV**: For camera input and frame processing.
- **Mediapipe**: For gesture recognition using hand tracking.
- **Requests**: For fetching Wordle words from the New York Times API.
- **Difflib**: For suggesting correct words based on similarity to the entered word.

## Acknowledgments

This project is inspired by the popular Wordle game and integrates modern technologies for an innovative interaction method using gesture recognition.

## Future Improvements

- Expand the gesture vocabulary for additional controls.
- Add support for multi-language word lists.
- Optimize animations and performance for better responsiveness.

## Notes

While the NYT API fetches a unique solution daily, it is outdated and does not correspond to the actual solution on the current New York Times website.
While we've implemented space in the writing mode, please note that other punctuation marks have not yet been included in the system.
The writing mode model is less accurate than the game's gesture recognition model and might have a higher error rate in detecting letters.