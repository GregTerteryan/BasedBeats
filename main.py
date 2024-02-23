import threading
import pygame
import pyautogui
import os

current_directory = os.getcwd()
width = pyautogui.size().width
height = pyautogui.size().height

pygame.init()

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
fullscreen = True
running = True

hitMarker_path = os.path.join(current_directory, "images", "hit_marker.png")
hitMarker = pygame.image.load(hitMarker_path)
hitMarkerTwo = pygame.image.load(hitMarker_path)
hitMarkerThree = pygame.image.load(hitMarker_path)
hitMarkerFour = pygame.image.load(hitMarker_path)

folder = "OdeToJoy"
maps_path = os.path.join(current_directory, "maps", folder, folder + ".txt")
music_path = os.path.join(current_directory, "maps", folder, folder + ".wav")

column1 = []
column2 = []
column3 = []
column4 = []

# Open the file and read lines
with open(maps_path, 'r') as file:
    # Read the first line and store the BPM value
    bpm = int(file.readline().strip())
    print(bpm)

    # Iterate through each line in the file
    for line in file:
        # Convert the line to a list of integers
        numbers = [int(digit) for digit in line.strip()]

        # Distribute the numbers to respective columns
        column1.append(numbers[0])
        column2.append(numbers[1])
        column3.append(numbers[2])
        column4.append(numbers[3])


class Note:
    def __init__(self, x, y, key, color):
        self.x = x
        self.y = y
        self.key = key
        self.color = color
        self.radius = 50

    def fall(self, dist):
        self.y += dist

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x + self.radius, self.y + self.radius), self.radius)


def initialize_notes(columns):
    notes = []
    current_time = pygame.time.get_ticks()

    for row, notes_in_row in enumerate(zip(*columns), start=1):
        for col_num, number in enumerate(notes_in_row, start=1):
            if number == 1:
                color = (255, 0, 0) if col_num == 1 else (0, 255, 0) if col_num == 2 else (
                255, 255, 0) if col_num == 3 else (0, 0, 255)
                key = pygame.K_a if col_num == 1 else pygame.K_s if col_num == 2 else pygame.K_l if col_num == 3 else pygame.K_SEMICOLON

                note = Note(100 * col_num + (20 * (col_num - 1)), 0, key, color)
                notes.append((note, current_time))

            # Increment the current_time only for the next row
            if col_num == len(columns):
                current_time += 30000 / bpm

    return notes


def playMusic():
    pygame.time.wait(2000)
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play()


def main():
    global fullscreen
    global running
    global screen
    global clock
    screen.blit(hitMarker, (100, 700))
    screen.blit(hitMarkerTwo, (220, 700))
    screen.blit(hitMarkerThree, (340, 700))
    screen.blit(hitMarkerFour, (460, 700))

    columns = [column1, column2, column3, column4]
    notes = initialize_notes(columns)
    music = threading.Thread(target=playMusic, args=())
    music.start()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if fullscreen:
                        screen = pygame.display.set_mode([500, 500])
                        fullscreen = False
                    elif not fullscreen:
                        screen = pygame.display.set_mode([width, height])
                        fullscreen = True

                # Check if a key matches any note's key and update accordingly
                for note, _ in notes:
                    if note and event.key == note.key and note.y >= 600:
                        notes.remove((note, _))
                        break  # Break to only remove one note for the pressed key

        screen.fill((255, 255, 255))  # Clear the screen
        screen.blit(hitMarker, (100, 700))
        screen.blit(hitMarkerTwo, (220, 700))
        screen.blit(hitMarkerThree, (340, 700))
        screen.blit(hitMarkerFour, (460, 700))

        current_time = pygame.time.get_ticks()

        for note, note_time in notes:
            if note:
                # Check if the note should be drawn based on the time delay
                if current_time >= note_time:
                    note.fall(5)
                    note.draw(screen)

        pygame.display.flip()
        pygame.display.update()
        clock.tick(60)

        # Remove notes that have fallen off the screen
        notes = [(note, note_time) for note, note_time in notes if note and note.y <= 900]
    music.join()


main()
input("Press enter to end program")
