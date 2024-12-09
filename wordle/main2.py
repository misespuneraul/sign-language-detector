import random
import pygame
from settings import *
from sprites import *
import datetime
import requests
import sys
import os

import mediapipe as mp
import cv2 as cv
from mediapipe.tasks import python
import difflib

import threading
import time
import queue

from detector import GestureRecognizer

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'sign-language-detector')))

# letter_queue = queue.Queue(maxsize=5)

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.options = ["Play Wordle", "Write Something", "Quit"]
        self.font = pygame.font.Font(None, 50)

    def draw(self, selected_option):
        self.screen.fill(BGCOLOUR)
        title_text = self.font.render("Main Menu", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        for i, option in enumerate(self.options):
            color = GREEN if i == selected_option else WHITE
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(WIDTH // 2, 200 + i * 100))
            self.screen.blit(option_text, option_rect)

        pygame.display.flip()

    def run(self):
        selected_option = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        return selected_option

            self.draw(selected_option)
            self.clock.tick(FPS)

def write_something(screen):
    input_text = ""
    font = pygame.font.Font(None, 50)
    clock = pygame.time.Clock()
    writing = True

    while writing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    writing = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        screen.fill(BGCOLOUR)
        prompt_text = font.render("Write something and press Enter:", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(prompt_text, prompt_rect)

        input_surface = font.render(input_text, True, GREEN)
        input_rect = input_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(input_surface, input_rect)

        pygame.display.flip()
        clock.tick(FPS)

    screen.fill(BGCOLOUR)
    result_text = font.render(f"You wrote: {input_text}", True, WHITE)
    result_rect = result_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(result_text, result_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.create_word_list()
        self.use_api_word = True  # Flag to fetch the first word from API
        self.letters_text = UIElement((self.screen.get_width() - (5 * TILESIZE + 4 * GAPSIZE)) // 2, 70, "Not Enough Letters", WHITE)
        self.invalid_word_text = UIElement((self.screen.get_width() - (5 * TILESIZE + 4 * GAPSIZE)) // 2, 70, "Invalid Word", WHITE)
        self.recommendations = []  # List to store recommended words

        self.letter_timer = 0
        self.letter = ""
        self.cap = cv.VideoCapture(0)
        self.recognizer = GestureRecognizer()
    
    def load_camera(self):
        _, self.frame = self.cap.read()

    def get_letter(self):
        self.frame = self.recognizer.process_frame(self.frame)
        self.letter = self.recognizer.letters[0]
        self.recognizer.letters = self.recognizer.letters[1:]

        # In Game.draw
    def draw_suggestions(self):
        if self.recommendations:
            # Position suggestions dynamically to the right of the grid
            margin_x = self.tiles[0][-1].x + TILESIZE + 2 * GAPSIZE  # Right of the grid
            margin_y = self.tiles[0][0].y  # Aligned with the top of the grid

            for i, word in enumerate(self.recommendations):
                y = margin_y + i * 40  # Space between lines
                text_surface = pygame.font.Font(None, 36).render(word.upper(), True, WHITE)
                self.screen.blit(text_surface, (margin_x, y))

    def create_word_list(self):
        with open("words.txt", "r") as file:
            self.words_list = file.read().splitlines()

    def new(self):
        if self.use_api_word:
            # Fetch the word from the API
            date = datetime.date.today()
            url = f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"
            response = requests.get(url).json()
            print(f"Answer (from API): {response['solution']}")
            self.word = response['solution'].upper()
            self.use_api_word = False  # Switch to using word list for subsequent games
        else:
            # Select a word randomly from the list
            self.word = random.choice(self.words_list).upper()
            print(f"Answer (from list): {self.word}")

        self.text = ""
        self.current_row = 0
        self.tiles = []
        self.create_tiles()
        self.flip = True
        self.not_enough_letters = False
        self.invalid_word = False
        self.timer = 0
        self.alphabet = [chr(i) for i in range(65, 91)]  # A-Z
        self.letter_colors = {letter: WHITE for letter in self.alphabet}  # Initially, all letters are white
        self.alph_letter_colors = {letter: WHITE for letter in self.alphabet}
        
        self.cap = cv.VideoCapture(0)
        self.recognizer = GestureRecognizer()


    def create_tiles(self):
        # Calculate margins for centering
        MARGIN_X = (self.screen.get_width() - (5 * TILESIZE + 4 * GAPSIZE)) // 2
        MARGIN_Y = (self.screen.get_height() - (6 * TILESIZE + 5 * GAPSIZE)) // 2

        # If the matrix already exists, just update positions
        if hasattr(self, 'tiles') and self.tiles:
            for row in range(6):
                for col in range(5):
                    self.tiles[row][col].x = (col * (TILESIZE + GAPSIZE)) + MARGIN_X
                    self.tiles[row][col].y = (row * (TILESIZE + GAPSIZE)) + MARGIN_Y
            return

        # Create the initial matrix
        self.tiles = []
        for row in range(6):
            self.tiles.append([])
            for col in range(5):
                x = (col * (TILESIZE + GAPSIZE)) + MARGIN_X
                y = (row * (TILESIZE + GAPSIZE)) + MARGIN_Y
                self.tiles[row].append(Tile(x, y))

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.load_camera()
        self.add_letter()
        # update every X secunde (5 daca s-a aratat acelasi semn)
        
        if self.letter_timer < 300:
            self.letter_timer += 1
        else:
            self.letter_timer = 0
            self.get_letter()
        
        cv.imshow("Frame", self.frame)
        cv.waitKey(1)

    def add_letter(self):
        # Empty all the letters in the current row
        for tile in self.tiles[self.current_row]:
            tile.letter = ""

        # Add the letters typed to the current row
        for i, letter in enumerate(self.text):
            self.tiles[self.current_row][i].letter = letter
            self.tiles[self.current_row][i].create_font()

    def draw_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.draw(self.screen)

    def draw_alphabet(self):
        # Total width needed for a single row
        total_width = 26 * ALPHABET_TILE_SIZE + 25 * ALPHABET_GAPSIZE
        available_width = self.screen.get_width()

        # Check if the alphabet fits in a single row
        if total_width > available_width:
            # Split alphabet into two rows
            letters_per_row = 13
            rows = 2
        else:
            # Single row
            letters_per_row = 26
            rows = 1

        # Position letters based on the number of rows
        for row in range(rows):
            margin_x = (available_width - (letters_per_row * ALPHABET_TILE_SIZE + (letters_per_row - 1) * ALPHABET_GAPSIZE)) // 2
            y = self.tiles[-1][0].y + TILESIZE + (row * (ALPHABET_TILE_SIZE + ALPHABET_GAPSIZE)) + 2 * ALPHABET_GAPSIZE

            for i in range(letters_per_row):
                index = row * letters_per_row + i
                if index >= len(self.alphabet):
                    break

                letter = self.alphabet[index]
                x = margin_x + i * (ALPHABET_TILE_SIZE + ALPHABET_GAPSIZE)

                # Draw each letter
                pygame.draw.rect(self.screen, self.alph_letter_colors[letter], (x, y, ALPHABET_TILE_SIZE, ALPHABET_TILE_SIZE))
                text_surface = pygame.font.Font(None, 36).render(letter, True, BLACK)
                text_rect = text_surface.get_rect(center=(x + ALPHABET_TILE_SIZE // 2, y + ALPHABET_TILE_SIZE // 2))
                self.screen.blit(text_surface, text_rect)

    def draw(self):
        self.screen.fill(BGCOLOUR)
        # Display the "Not Enough Letters" or "Invalid Word" text
        if self.not_enough_letters or self.invalid_word:
            self.timer += 1
            if self.not_enough_letters:
                self.letters_text.fade_in()
            elif self.invalid_word:
                self.invalid_word_text.fade_in()
            if self.timer > 90:
                self.not_enough_letters = False
                self.invalid_word = False
                self.timer = 0
        else:
            if self.not_enough_letters:
                self.letters_text.fade_out()
            elif self.invalid_word:
                self.invalid_word_text.fade_out()
        if self.not_enough_letters:
            self.letters_text.draw(self.screen)
        elif self.invalid_word:
            self.invalid_word_text.draw(self.screen)

        self.draw_tiles()
        self.draw_suggestions()
        self.draw_alphabet()

        pygame.display.flip()

    def row_animation(self):
        # Row shaking animation if not enough letters are input
        start_pos = self.tiles[0][0].x
        amount_move = 4
        move = 3
        screen_copy = self.screen.copy()
        screen_copy.fill(BGCOLOUR)
        for row in self.tiles:
            for tile in row:
                if row != self.tiles[self.current_row]:
                    tile.draw(screen_copy)

        while True:
            while self.tiles[self.current_row][0].x < start_pos + amount_move:
                self.screen.blit(screen_copy, (0, 0))
                for tile in self.tiles[self.current_row]:
                    tile.x += move
                    tile.draw(self.screen)
                self.clock.tick(FPS)
                pygame.display.flip()

            while self.tiles[self.current_row][0].x > start_pos - amount_move:
                self.screen.blit(screen_copy, (0, 0))
                for tile in self.tiles[self.current_row]:
                    tile.x -= move
                    tile.draw(self.screen)
                self.clock.tick(FPS)
                pygame.display.flip()

            amount_move -= 2
            if amount_move < 0:
                break

    def box_animation(self):
        # tile scale animation for every letter inserted
        for tile in self.tiles[self.current_row]:
            if tile.letter == "":
                screen_copy = self.screen.copy()
                for start, end, step in ((0, 6, 1), (0, -6, -1)):
                    for size in range(start, end, 2*step):
                        self.screen.blit(screen_copy, (0, 0))
                        tile.x -= size
                        tile.y -= size
                        tile.width += size * 2
                        tile.height += size * 2
                        surface = pygame.Surface((tile.width, tile.height))
                        surface.fill(BGCOLOUR)
                        self.screen.blit(surface, (tile.x, tile.y))
                        tile.draw(self.screen)
                        pygame.display.flip()
                        self.clock.tick(FPS)
                    self.add_letter()
                break

    def reveal_animation(self, tile, colour):
        # reveal colours animation when user input the whole word
        screen_copy = self.screen.copy()

        while True:
            surface = pygame.Surface((tile.width + 5, tile.height + 5))
            surface.fill(BGCOLOUR)
            screen_copy.blit(surface, (tile.x, tile.y))
            self.screen.blit(screen_copy, (0, 0))
            if self.flip:
                tile.y += 6
                tile.height -= 12
                tile.font_y += 4
                tile.font_height = max(tile.font_height - 8, 0)
            else:
                tile.colour = colour
                tile.y -= 6
                tile.height += 12
                tile.font_y -= 4
                tile.font_height = min(tile.font_height + 8, tile.font_size)
            if tile.font_height == 0:
                self.flip = False

            tile.draw(self.screen)
            pygame.display.update()
            self.clock.tick(FPS)

            if tile.font_height == tile.font_size:
                self.flip = True
                break

    def check_letters(self):
        # Algoritm pentru verificarea literelor
        
        copy_word = [x for x in self.word]
        print(copy_word)
        print(self.text)
        for i, user_letter in enumerate(self.text):
            colour = LIGHTGREY
            for j, letter in enumerate(copy_word):
                print(user_letter,letter)
                if user_letter == letter:
                    colour = YELLOW
                    if i == j:
                        print("DA!")
                        colour = GREEN
                        copy_word[j] = ""
                        break    
                    
                    

            # Schimbă culoarea alfabetului pentru literele găsite
            self.letter_colors[user_letter] = colour

            # Animație de dezvăluire
            self.reveal_animation(self.tiles[self.current_row][i], colour)

        # Schimbă literele care nu apar deloc în cuvânt
        for letter in self.text:
            if letter not in self.word:
                self.letter_colors[letter] = RED
                self.alph_letter_colors[letter] = RED


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                self.create_tiles()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(self.text) == 5:
                        # check all letters
                        if self.text.lower() in self.words_list:
                            self.recommendations = []  # Clear suggestions when valid word is entered
                            self.check_letters()

                            for letter in self.alphabet:
                                if letter not in self.word and letter in self.text and self.letter_colors[letter] == WHITE:
                                    self.letter_colors[letter] = RED

                            if self.text == self.word or self.current_row + 1 == 6:
                                if self.text != self.word:
                                    self.end_screen_text = UIElement(
                                        (self.screen.get_width() - (5 * TILESIZE + 4 * GAPSIZE)) // 2,
                                        self.screen.get_height() - 200, f"THE WORD WAS: {self.word}", WHITE)
                                else:
                                    self.end_screen_text = UIElement(
                                        (self.screen.get_width() - (5 * TILESIZE + 4 * GAPSIZE)) // 2,
                                        self.screen.get_height() - 200, "YOU GUESSED RIGHT", WHITE)

                                self.playing = False
                                self.end_screen()
                                break
                        else:
                            self.invalid_word = True
                            if self.text.lower() not in possibilities:
                                self.recommendations = difflib.get_close_matches(self.text.lower(), possibilities)
                                print(self.recommendations)
                            self.row_animation()

                        if not self.invalid_word:  # Clear the word text and recommendations
                            self.current_row += 1
                            self.text = ""
                            self.recommendations = []  # Clear recommendations after valid submission

                    else:
                        self.not_enough_letters = True
                        self.row_animation()

                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]

                else:
                    # if len(self.text) < 5 and event.unicode.isalpha():
                    #     self.text += event.unicode.upper()
                    #     self.box_animation()
                    if len(self.text) < 5:
                        self.text += self.letter.upper()
                        self.letter = ""
                        self.box_animation()


    def end_screen(self):
        play_again = UIElement((self.screen.get_width() - (5 * TILESIZE + 4 * GAPSIZE)) // 2, self.screen.get_height() - 150, "PRESS ENTER TO PLAY AGAIN", WHITE, 30)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return

            self.screen.fill(BGCOLOUR)
            self.draw_tiles()
            self.end_screen_text.fade_in()
            self.end_screen_text.draw(self.screen)
            play_again.fade_in()
            play_again.draw(self.screen)
            pygame.display.flip()

def game_loop():
    while True:
        choice = menu.run()
        if choice == 0:
            game.new()
            game.run()
        elif choice == 1:
            write_something(game.screen)
        elif choice == 2:
            pygame.quit()
            quit()


with open('words.txt', 'r') as file:
    possibilities = [line.strip() for line in file.readlines()]
game = Game()
menu = MainMenu(game.screen)
detector = GestureRecognizer()

game_loop()
detector.recognize_gesture()


detector.cleanup()
# cam_thread = threading.Thread(target=cam_loop)
# game_thread = threading.Thread(target=game_loop)

# cam_thread.start()
# game_thread.start()

# cam_thread.join()
# game_thread.join()

# cam.release()
# cv.destroyAllWindows()
