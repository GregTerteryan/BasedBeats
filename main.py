import threading
import pygame
import pyautogui
import os

import pygame.time

"""
5 different types of notes:
Type 0: Is a None, functions as a pause between one note and the next
Type 1: Singular circular note that is cleared with a KEYDOWN event
Type 2: Semicircle with a rectangle attached to it, cleared with a KEYDOWN event
Type 3: Rectangle that is cleared when its y value is >= 775 and its key is held down
Type 4: Rectangle with a semicircle attached to it, cleared with a KEYUP event
Type 5: Negative note. -100 points on hit.
"""

current_directory = os.path.realpath(os.path.dirname(__file__))
width = pyautogui.size().width
height = pyautogui.size().height
#width = 1280
#height = 720

pygame.init()

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
fullscreen = True
running = True
autoclicker = False

hitMarker_path = os.path.join(current_directory, "images", "hit_marker.png")
hitMarker = pygame.transform.scale(pygame.image.load(hitMarker_path), (100 * width/1280, 250 * height/720))
hitMarkerTwo = pygame.transform.scale(pygame.image.load(hitMarker_path), (100 * width/1280, 250 * height/720))
hitMarkerThree = pygame.transform.scale(pygame.image.load(hitMarker_path), (100 * width/1280, 250 * height/720))
hitMarkerFour = pygame.transform.scale(pygame.image.load(hitMarker_path), (100 * width/1280, 250 * height/720))
font = pygame.font.Font(None, int(50 * (width/1280)))
music_path = None
bpm = 60

column1 = []
column2 = []
column3 = []
column4 = []
controls = [pygame.K_q, pygame.K_w, pygame.K_o, pygame.K_p]
key_delay = 0
hit_sounds = True
colors = [[255, 0, 0], [0, 255, 0], [255, 255, 0], [0, 0, 255]]


def loadMap(folder):
    global bpm
    global music_path
    global column1
    global column2
    global column3
    global column4
    maps_path = os.path.join(current_directory, "maps", folder, folder + ".txt")
    music_path = os.path.join(current_directory, "maps", folder, folder + ".wav")

    # Open the file and read lines
    with open(maps_path, 'r') as file:
        # Read the first line and store the BPM value
        bpm = int(file.readline().strip())

        # Iterate through each line in the file
        for line in file:
            # Convert the line to a list of integers
            if len(line) >= 4:
                # Convert the line to a list of integers
                numbers = [int(digit) for digit in line.strip()]

                # Distribute the numbers to respective columns
                column1.append(numbers[0])
                column2.append(numbers[1])
                column3.append(numbers[2])
                column4.append(numbers[3])
            else:
                pass

def get_map_folders():
    maps_folder = os.path.join(current_directory, "maps")
    map_folders = []

    for folder in os.listdir(maps_folder):
        folder_path = os.path.join(maps_folder, folder)
        if os.path.isdir(folder_path):
            txt_file = os.path.join(folder_path, f"{folder}.txt")
            wav_file = os.path.join(folder_path, f"{folder}.wav")
            if os.path.exists(txt_file) and os.path.exists(wav_file):
                map_folders.append(folder)

    return map_folders


def load_controls():
    global controls
    controls_path = os.path.join(current_directory, "settings", "controls.txt")

    alt_chars = {
        "~": "BACKQUOTE",
        "`": "BACKQUOTE",
        "!": "1",
        "@": "2",
        "#": "3",
        "$": "4",
        "%": "5",
        "^": "6",
        "&": "7",
        "*": "8",
        "(": "9",
        ")": "0",
        "_": "MINUS",
        "-": "MINUS",
        "+": "EQUALS",
        "=": "EQUALS",
        "Q": "q",
        "W": "w",
        "E": "e",
        "R": "r",
        "T": "t",
        "Y": "y",
        "U": "u",
        "I": "i",
        "O": "o",
        "P": "p",
        "{": "LEFTBRACKET",
        "[": "LEFTBRACKET",
        "}": "RIGHTBRACKET",
        "]": "RIGHTBRACKET",
        "|": "BACKSLASH",
        "\\": "BACKSLASH",
        "A": "a",
        "S": "s",
        "D": "d",
        "F": "f",
        "G": "g",
        "H": "h",
        "J": "j",
        "K": "k",
        "L": "l",
        ":": "SEMICOLON",
        ";": "SEMICOLON",
        "\"": "QUOTE",
        "\'": "QUOTE",
        "Z": "z",
        "X": "x",
        "C": "c",
        "V": "v",
        "B": "b",
        "N": "n",
        "M": "m",
        "<": "COMMA",
        ",": "COMMA",
        ">": "PERIOD",
        ".": "PERIOD",
        "?": "SLASH",
        "/": "SLASH",
        " ": "SPACE",
    }
    try:
        with open(controls_path, "r") as file:
            content = file.read().strip("\n")
        for num in range(4):
            if alt_chars.__contains__(content[num]):
                controls[num] = getattr(pygame, "K_" + alt_chars[content[num]])
            elif 31 < ord(content[num]) < 127:
                controls[num] = getattr(pygame, "K_" + content[num])
    except FileNotFoundError:
        open(controls_path, "x")
        save_controls()


def save_controls():
    global controls
    controls_path = os.path.join(current_directory, "settings", "controls.txt")
    with open(controls_path, "w") as file:
        line = "" + chr(controls[0]) + chr(controls[1]) + chr(controls[2]) + chr(controls[3])
        file.write(line)


def load_delay():
    global key_delay
    global hit_sounds
    delay_path = os.path.join(current_directory, "settings", "audio.txt")
    try:
        with open(delay_path, "r") as file:
            key_delay = int(file.readline().strip("\n"))
            if type(key_delay) is not int:
                key_delay = 0
                save_delay()
            line = file.readline().strip("\n")
            hit_sounds = False if line == "False" else True
            if type(hit_sounds) is not bool:
                hit_sounds = True
                save_delay()
    except FileNotFoundError:
        open(delay_path, "x")
        save_delay()


def save_delay():
    global key_delay
    global hit_sounds
    delay_path = os.path.join(current_directory, "settings", "audio.txt")
    with open(delay_path, "w") as file:
        file.write(str(key_delay) + "\n")
        file.write(str(hit_sounds))


def load_colors():
    global colors
    colors_path = os.path.join(current_directory, "settings", "colors.txt")
    try:
        with open(colors_path, "r") as file:
            for i in range(len(colors)):
                line = file.readline().strip("\n")
                for j in range(len(colors[i])):
                    if line.find(",") >= 0:
                        colors[i][j] = int(line[0: line.find(",")])
                        line = line[line.find(",") + 1:len(line)]
                    else:
                        colors[i][j] = int(line)
    except FileNotFoundError:
        open(colors_path, "x")
        save_colors()


def save_colors():
    global colors
    colors_path = os.path.join(current_directory, "settings", "colors.txt")
    with open(colors_path, "w") as file:
        for i in range(len(colors)):
            for j in range(len(colors[i])):
                if j != len(colors[i])-1:
                    file.write(str(colors[i][j]) + ",")
                else:
                    file.write(str(colors[i][j]))
            file.write("\n")


def animate(folder, x, y, w, h, delay):
    global screen
    global width
    global height
    frames = []
    c = 0
    while (True):
        frame_path = os.path.join(current_directory, "images", "animations", folder, f"frame_{c}.png")
        if os.path.exists(frame_path):
            frames.append(frame_path)
        else:
            break
        c += 1
    c -= 1
    if c >= 0:
        for num in range(c):
            screen.blit(pygame.transform.scale(pygame.image.load(frames[num]), (w * width/1280, h * height/720)), (x, y))
            pygame.display.update()
            pygame.time.wait(delay)

def get_frame(folder, w, h, frame):
    global screen
    global width
    global height
    frames = []
    c = 0
    while (True):
        frame_path = os.path.join(current_directory, "images", "animations", folder, f"frame_{c}.png")
        if os.path.exists(frame_path):
            frames.append(frame_path)
        else:
            break
        c += 1
    c -= 1
    if frame > c or frame < 0:
        return -1
    return pygame.transform.scale(pygame.image.load(frames[frame]), (w * width/1280, h * height/720))


in_colors = False


def display_menu():
    global autoclicker
    global in_colors
    map_folders = get_map_folders()
    selected_index = 0
    title = pygame.transform.scale(pygame.image.load(os.path.join(current_directory, "images", "title.png")), (696 * width/1280, 122 * height/720))
    map_text = font.render(map_folders[0], True, (0, 0, 0))
    controls_text = font.render("Controls", True, (0, 0, 0))
    delay_text = font.render("Audio Settings", True, (0, 0, 0))
    colors_text = font.render("Note Colors", True, (0, 0, 0))
    quit_text = font.render("Quit Game", True, (0, 0, 0))
    container_l_path = os.path.join(current_directory, "images", "text_container_l.png")
    container_r_path = os.path.join(current_directory, "images", "text_container_r.png")
    container_mid_path = os.path.join(current_directory, "images", "text_container_mid.png")
    map_container = [pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
                      pygame.transform.scale(pygame.image.load(container_mid_path), (map_text.get_width(), 50 * height / 720)),
                      pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))]
    controls_container = [
        pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
        pygame.transform.scale(pygame.image.load(container_mid_path), (controls_text.get_width(), 50 * height / 720)),
        pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))]
    delay_container = [
        pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
        pygame.transform.scale(pygame.image.load(container_mid_path), (delay_text.get_width(), 50 * height / 720)),
        pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))]
    colors_container = [
        pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
        pygame.transform.scale(pygame.image.load(container_mid_path), (colors_text.get_width(), 50 * height / 720)),
        pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))
    ]
    quit_container = [
        pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
        pygame.transform.scale(pygame.image.load(container_mid_path), (quit_text.get_width(), 50 * height / 720)),
        pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))]
    c = 0
    # options = ["Map", "Controls", "Audio Settings", "Note Colors", "Quit"]
    index = 0
    while True:
        bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        if bg == -1:
            c = 0
            bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and index == 0:
                    prev_index = selected_index
                    selected_index = (selected_index - 1) % len(map_folders)
                    prev_text = font.render(map_folders[prev_index], True, (0, 0, 0))
                    map_text = font.render(map_folders[selected_index], True, (0, 0, 0))
                    prev_container = [pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
                                      pygame.transform.scale(pygame.image.load(container_mid_path), (prev_text.get_width(), 50 * height / 720)),
                                      pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))]
                    map_container = [pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
                                      pygame.transform.scale(pygame.image.load(container_mid_path), (map_text.get_width(), 50 * height / 720)),
                                      pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))]
                    slide(prev_text, map_text, "left", 42 * width/1280, 300 * height/720, 50, prev_container, map_container, c, controls_text, controls_container, delay_text, delay_container, colors_text, colors_container, quit_text, quit_container, title)
                elif event.key == pygame.K_RIGHT and index == 0:
                    prev_index = selected_index
                    selected_index = (selected_index - 1) % len(map_folders)
                    prev_text = font.render(map_folders[prev_index], True, (0, 0, 0))
                    map_text = font.render(map_folders[selected_index], True, (0, 0, 0))
                    prev_container = [pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
                                      pygame.transform.scale(pygame.image.load(container_mid_path), (prev_text.get_width(), 50 * height / 720)),
                                      pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))]
                    map_container = [pygame.transform.scale(pygame.image.load(container_l_path), (43 * width / 1280, 50 * height / 720)),
                                      pygame.transform.scale(pygame.image.load(container_mid_path), (map_text.get_width(), 50 * height / 720)),
                                      pygame.transform.scale(pygame.image.load(container_r_path), (43 * width / 1280, 50 * height / 720))]
                    slide(prev_text, map_text, "right", 42 * width / 1280, 300 * height / 720, 50, prev_container, map_container, c, controls_text, controls_container, delay_text, delay_container, colors_text, colors_container, quit_text, quit_container, title)
                elif event.key == pygame.K_RETURN:
                    if index == 0:
                        autoclicker = False
                        return map_folders[selected_index]
                    elif index == 1:
                        controls_menu(c)
                    elif index == 2:
                        delay_menu(c)
                    elif index == 3:
                        in_colors = True
                        colors_menu(c)
                    else:
                        pygame.quit()
                        quit()
                elif event.key == pygame.K_EQUALS and index == 0:
                    autoclicker = True
                    return map_folders[selected_index]
                elif event.key == pygame.K_DOWN:
                    index += 1
                    if index > 4:
                        index = 0
                elif event.key == pygame.K_UP:
                    index -= 1
                    if index < 0:
                        index = 4
        screen.blit(bg, (0, 0))
        c += 1
        if index == 0:
            screen.blit(map_container[0], (0 * width/1280, 292 * height/720))
            screen.blit(map_container[1], (42 * width/1280, 292 * height/720))
            screen.blit(map_container[2], (42 * width/1280 + map_text.get_width(), 292 * height/720))
            screen.blit(map_text, (42 * width/1280, 300 * height/720))
            screen.blit(controls_container[0], (-42 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[1], (0 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[2], (0 * width / 1280 + controls_text.get_width(), 342 * height / 720))
            screen.blit(controls_text, (0 * width / 1280, 350 * height / 720))
            screen.blit(delay_container[0], (-42 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[1], (0 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[2], (0 * width / 1280 + delay_text.get_width(), 392 * height / 720))
            screen.blit(delay_text, (0 * width / 1280, 400 * height / 720))
            screen.blit(colors_container[0], (-42 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[1], (0 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[2], (0 * width / 1280 + colors_text.get_width(), 442 * height / 720))
            screen.blit(colors_text, (0 * width / 1280, 450 * height / 720))
            screen.blit(quit_container[0], (-42 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[1], (0 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[2], (0 * width / 1280 + quit_text.get_width(), 492 * height / 720))
            screen.blit(quit_text, (0 * width / 1280, 500 * height / 720))
        elif index == 1:
            screen.blit(map_container[0], (-42 * width / 1280, 292 * height / 720))
            screen.blit(map_container[1], (0 * width / 1280, 292 * height / 720))
            screen.blit(map_container[2], (0 * width / 1280 + map_text.get_width(), 292 * height / 720))
            screen.blit(map_text, (0 * width / 1280, 300 * height / 720))
            screen.blit(controls_container[0], (0 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[1], (42 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[2], (42 * width / 1280 + controls_text.get_width(), 342 * height / 720))
            screen.blit(controls_text, (42 * width / 1280, 350 * height / 720))
            screen.blit(delay_container[0], (-42 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[1], (0 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[2], (0 * width / 1280 + delay_text.get_width(), 392 * height / 720))
            screen.blit(delay_text, (0 * width / 1280, 400 * height / 720))
            screen.blit(colors_container[0], (-42 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[1], (0 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[2], (0 * width / 1280 + colors_text.get_width(), 442 * height / 720))
            screen.blit(colors_text, (0 * width / 1280, 450 * height / 720))
            screen.blit(quit_container[0], (-42 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[1], (0 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[2], (0 * width / 1280 + quit_text.get_width(), 492 * height / 720))
            screen.blit(quit_text, (0 * width / 1280, 500 * height / 720))
        elif index == 2:
            screen.blit(map_container[0], (-42 * width / 1280, 292 * height / 720))
            screen.blit(map_container[1], (0 * width / 1280, 292 * height / 720))
            screen.blit(map_container[2], (0 * width / 1280 + map_text.get_width(), 292 * height / 720))
            screen.blit(map_text, (0 * width / 1280, 300 * height / 720))
            screen.blit(controls_container[0], (-42 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[1], (0 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[2], (0 * width / 1280 + controls_text.get_width(), 342 * height / 720))
            screen.blit(controls_text, (0 * width / 1280, 350 * height / 720))
            screen.blit(delay_container[0], (0 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[1], (42 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[2], (42 * width / 1280 + delay_text.get_width(), 392 * height / 720))
            screen.blit(delay_text, (42 * width / 1280, 400 * height / 720))
            screen.blit(colors_container[0], (-42 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[1], (0 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[2], (0 * width / 1280 + colors_text.get_width(), 442 * height / 720))
            screen.blit(colors_text, (0 * width / 1280, 450 * height / 720))
            screen.blit(quit_container[0], (-42 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[1], (0 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[2], (0 * width / 1280 + quit_text.get_width(), 492 * height / 720))
            screen.blit(quit_text, (0 * width / 1280, 500 * height / 720))
        elif index == 3:
            screen.blit(map_container[0], (-42 * width / 1280, 292 * height / 720))
            screen.blit(map_container[1], (0 * width / 1280, 292 * height / 720))
            screen.blit(map_container[2], (0 * width / 1280 + map_text.get_width(), 292 * height / 720))
            screen.blit(map_text, (0 * width / 1280, 300 * height / 720))
            screen.blit(controls_container[0], (-42 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[1], (0 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[2], (0 * width / 1280 + controls_text.get_width(), 342 * height / 720))
            screen.blit(controls_text, (0 * width / 1280, 350 * height / 720))
            screen.blit(delay_container[0], (-42 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[1], (0 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[2], (0 * width / 1280 + delay_text.get_width(), 392 * height / 720))
            screen.blit(delay_text, (0 * width / 1280, 400 * height / 720))
            screen.blit(colors_container[0], (0 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[1], (42 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[2], (42 * width / 1280 + colors_text.get_width(), 442 * height / 720))
            screen.blit(colors_text, (42 * width / 1280, 450 * height / 720))
            screen.blit(quit_container[0], (-42 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[1], (0 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[2], (0 * width / 1280 + quit_text.get_width(), 492 * height / 720))
            screen.blit(quit_text, (0 * width / 1280, 500 * height / 720))
        else:
            screen.blit(map_container[0], (-42 * width / 1280, 292 * height / 720))
            screen.blit(map_container[1], (0 * width / 1280, 292 * height / 720))
            screen.blit(map_container[2], (0 * width / 1280 + map_text.get_width(), 292 * height / 720))
            screen.blit(map_text, (0 * width / 1280, 300 * height / 720))
            screen.blit(controls_container[0], (-42 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[1], (0 * width / 1280, 342 * height / 720))
            screen.blit(controls_container[2], (0 * width / 1280 + controls_text.get_width(), 342 * height / 720))
            screen.blit(controls_text, (0 * width / 1280, 350 * height / 720))
            screen.blit(delay_container[0], (-42 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[1], (0 * width / 1280, 392 * height / 720))
            screen.blit(delay_container[2], (0 * width / 1280 + delay_text.get_width(), 392 * height / 720))
            screen.blit(delay_text, (0 * width / 1280, 400 * height / 720))
            screen.blit(colors_container[0], (-42 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[1], (0 * width / 1280, 442 * height / 720))
            screen.blit(colors_container[2], (0 * width / 1280 + colors_text.get_width(), 442 * height / 720))
            screen.blit(colors_text, (0 * width / 1280, 450 * height / 720))
            screen.blit(quit_container[0], (0 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[1], (42 * width / 1280, 492 * height / 720))
            screen.blit(quit_container[2], (42 * width / 1280 + quit_text.get_width(), 492 * height / 720))
            screen.blit(quit_text, (42 * width / 1280, 500 * height / 720))
        screen.blit(title, (0, 50 * height/720))
        pygame.display.flip()
        clock.tick(30)


def slide(text, replacement, direction, x, y, amt, prev_cont, curr_cont, c, controls_text, controls_container, audio_text, audio_container, colors_text, colors_container, quit_text, quit_container, title):
    text_w = text.get_width()
    text_h = text.get_height()
    rep_w = replacement.get_width()
    rep_h = replacement.get_height()
    prev_cont_l_w = prev_cont[0].get_width()
    prev_cont_l_h = prev_cont[0].get_height()
    prev_cont_mid_w = prev_cont[1].get_width()
    prev_cont_mid_h = prev_cont[1].get_height()
    prev_cont_r_w = prev_cont[2].get_width()
    prev_cont_r_h = prev_cont[2].get_height()
    curCont = curr_cont[:]
    curCont_l_w = curr_cont[0].get_width()
    curCont_l_h = curr_cont[0].get_height()
    curCont_mid_w = curr_cont[1].get_width()
    curCont_mid_h = curr_cont[1].get_height()
    curCont_r_w = curr_cont[2].get_width()
    curCont_r_h = curr_cont[2].get_height()
    global screen
    percent = 100
    while percent > 0:
        bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        if bg == -1:
            c = 0
            bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        rep_start = x - (amt * 10)
        percent -= 10
        text = pygame.transform.scale(text, (text_w * (percent/100.0), text_h * (percent/100.0)))
        prev_cont[0] = pygame.transform.scale(prev_cont[0], (prev_cont_l_w * percent/100.0, prev_cont_l_h * percent/100.0))
        prev_cont[1] = pygame.transform.scale(prev_cont[1], ((prev_cont_mid_w * (percent/100.0)), prev_cont_mid_h * (percent/100.0)))
        prev_cont[2] = pygame.transform.scale(prev_cont[2],(prev_cont_r_w * percent / 100.0, prev_cont_r_h * percent / 100.0))
        rep = pygame.transform.scale(replacement, (rep_w * (100 - percent)/100.0, rep_h * (100 - percent)/100.0))
        curCont[0] = pygame.transform.scale(curr_cont[0],(curCont_l_w * (100-percent)/100.0, curCont_l_h * (100-percent)/100.0))
        curCont[1] = pygame.transform.scale(curr_cont[1], ((curCont_mid_w * (100-percent)/100.0), curCont_mid_h * (100-percent)/100.0))
        curCont[2] = pygame.transform.scale(curr_cont[2],(curCont_r_w * (100-percent)/100.0, curCont_r_h * (100-percent)/100.0))
        if direction == "left":
            screen.blit(bg, (0, 0))
            c += 1
            screen.blit(prev_cont[0], (x - (prev_cont[0].get_width()) + amt, y - 8 * width / 1280))
            screen.blit(prev_cont[1], (x + amt, y - 8 * width / 1280))
            screen.blit(prev_cont[2], (x + (prev_cont[1].get_width()) + amt, y - 8 * width/1280))
            screen.blit(curCont[0], (rep_start - (curCont[0].get_width()) + amt, y - 8 * width / 1280))
            screen.blit(curCont[1], (rep_start + amt, y - 8 * width / 1280))
            screen.blit(curCont[2], (rep_start + (curCont[1].get_width()) + amt, y - 8 * width / 1280))
            screen.blit(text, (x + amt, y - 8 * height/720 * (100-percent)/100.0))
            screen.blit(rep, (rep_start + amt, y - 8 * height/720 * percent/100.0))
            x += amt
            rep_start += amt
        elif direction == "right":
            rep_start = x + (amt * 10)
            screen.blit(bg, (0, 0))
            c += 1
            screen.blit(prev_cont[1], (x - amt, y - 8 * width/1280))
            screen.blit(prev_cont[0], (x - (prev_cont[0].get_width()) - amt, y - 8 * width / 1280))
            screen.blit(prev_cont[2], (x + (prev_cont[1].get_width()) - amt, y - 8 * width/1280))
            screen.blit(curCont[0], (rep_start - (curCont[0].get_width()) - amt, y - 8 * width / 1280))
            screen.blit(curCont[1], (rep_start - amt, y - 8 * width/1280))
            screen.blit(curCont[2], (rep_start + (curCont[1].get_width()) - amt, y - 8 * width / 1280))
            screen.blit(text, (x - amt, y - 8 * height/720 * (100-percent)/100.0))
            screen.blit(rep, (rep_start-amt, y - 8 * height/720 * percent/100.0))
            x -= amt
            rep_start -= amt
        screen.blit(controls_container[0], (-42 * width / 1280, 342 * height / 720))
        screen.blit(controls_container[1], (0 * width / 1280, 342 * height / 720))
        screen.blit(controls_container[2], (0 * width / 1280 + controls_text.get_width(), 342 * height / 720))
        screen.blit(controls_text, (0 * width / 1280, 350 * height / 720))
        screen.blit(audio_container[0], (-42 * width / 1280, 392 * height / 720))
        screen.blit(audio_container[1], (0 * width / 1280, 392 * height / 720))
        screen.blit(audio_container[2], (0 * width / 1280 + audio_text.get_width(), 392 * height / 720))
        screen.blit(audio_text, (0 * width / 1280, 400 * height / 720))
        screen.blit(colors_container[0], (-42 * width / 1280, 442 * height / 720))
        screen.blit(colors_container[1], (0 * width / 1280, 442 * height / 720))
        screen.blit(colors_container[2], (0 * width / 1280 + colors_text.get_width(), 442 * height / 720))
        screen.blit(colors_text, (0 * width / 1280, 450 * height / 720))
        screen.blit(quit_container[0], (-42 * width / 1280, 492 * height / 720))
        screen.blit(quit_container[1], (0 * width / 1280, 492 * height / 720))
        screen.blit(quit_container[2], (0 * width / 1280 + quit_text.get_width(), 492 * height / 720))
        screen.blit(quit_text, (0 * width / 1280, 500 * height / 720))
        screen.blit(title, (0, 50 * height / 720))
        pygame.display.flip()
        clock.tick(30)
        # pygame.time.wait(5)


def controls_menu(c):
    menu_screen = pygame.transform.scale(pygame.image.load(os.path.join(current_directory, "images", "controls_menu.png")), (990 * width/1280, 630 * height/720))
    index = 0
    big_font = pygame.font.Font(None, int(75 * (width/1280)))
    while True:
        bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        if bg == -1:
            c = 0
            bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        keys = [big_font.render(chr(controls[0]), True, (75, 75, 75)), big_font.render(chr(controls[1]), True, (75, 75, 75)), big_font.render(chr(controls[2]), True, (75, 75, 75)), big_font.render(chr(controls[3]), True, (75, 75, 75))]
        keys[index] = big_font.render(chr(controls[index]), True, (0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    index += 1
                    if index > 3:
                        index = 0
                elif event.key == pygame.K_LEFT:
                    index -= 1
                    if index < 0:
                        index = 3
                elif event.key == pygame.K_RETURN:
                    keys[index] = big_font.render(chr(controls[index]), True, (255, 255, 255))
                    selected = True
                    while selected:
                        bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
                        if bg == -1:
                            c = 0
                            bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
                        for evt in pygame.event.get():
                            if evt.type == pygame.QUIT:
                                selected = False
                                pygame.quit()
                                quit()
                            elif evt.type == pygame.KEYDOWN:
                                if 32 <= evt.key <= 126 and not controls.__contains__(evt.key):
                                    controls[index] = evt.key
                                    save_controls()
                                    load_controls()
                                    save_controls()
                                    selected = False
                                elif controls.__contains__(evt.key):
                                    selected = False
                        screen.blit(bg, (0, 0))
                        c += 1
                        screen.blit(menu_screen, (145 * width / 1280, 45 * height / 720))
                        for num in range(4):
                            screen.blit(keys[num], ((290 + 200 * num) * width / 1280, 500 * height / 720))
                        pygame.display.flip()
                        clock.tick(60)
                elif event.key == pygame.K_ESCAPE:
                    return
        screen.blit(bg, (0, 0))
        c += 1
        screen.blit(menu_screen, (145 * width/1280, 45 * height/720))
        for num in range(4):
            screen.blit(keys[num], ((290 + 200 * num) * width/1280, 500 * height/720))
        pygame.display.flip()
        clock.tick(100)


def delay_menu(c):
    global key_delay
    global hit_sounds
    menu_screen = pygame.transform.scale(pygame.image.load(os.path.join(current_directory, "images", "delay_menu.png")), (990 * width / 1280, 630 * height / 720))
    check_box = pygame.transform.scale(pygame.image.load(os.path.join(current_directory, "images", "check_box.png")), (66 * width / 1280, 66 * height / 720))
    big_font = pygame.font.Font(None, int(75 * (width / 1280)))

    while True:
        bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        if bg == -1:
            c = 0
            bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_delay()
                    return
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if 305 * height / 720 <= pos[1] <= 414 * height / 720:
                    if 169 * width / 1280 <= pos[0] < 278 * width / 1280:
                        key_delay -= 100
                        if key_delay < -2583:
                            key_delay = -2583
                    elif 278 * width / 1280 <= pos[0] < 387 * width / 1280:
                        key_delay -= 10
                        if key_delay < -2583:
                            key_delay = -2583
                    elif 387 * width / 1280 <= pos[0] < 497 * width / 1280:
                        key_delay -= 1
                        if key_delay < -2583:
                            key_delay = -2583
                    elif 783 * width / 1280 <= pos[0] < 892 * width / 1280:
                        key_delay += 1
                    elif 892 * width / 1280 <= pos[0] < 1001 * width / 1280:
                        key_delay += 10
                    elif 1001 * width / 1280 <= pos[0] < 1110 * width / 1280:
                        key_delay += 100
                if 526 * height/720 <= pos[1] <= 593 * height/720 and 635 * width/1280 <= pos[0] <= 701 * width/1280:
                    hit_sounds = not hit_sounds
        delay_display = big_font.render(str(key_delay), True, (0, 0, 0))
        screen.blit(bg, (0, 0))
        c += 1
        screen.blit(menu_screen, (145 * width / 1280, 45 * height / 720))
        screen.blit(delay_display, ((639 - delay_display.get_width()/3) * width / 1280, (359 - delay_display.get_height()/3) * height / 720))
        if hit_sounds:
            screen.blit(check_box, (635 * width/1280, 526 * height/720))
        pygame.display.flip()
        clock.tick(100)


def colors_menu(c):
    global colors
    global in_colors
    menu_screen = pygame.transform.scale(pygame.image.load(os.path.join(current_directory, "images", "colors_menu.png")), (990 * width / 1280, 630 * height / 720))
    mid_font = pygame.font.Font(None, int(40 * (width / 1280)))
    color_displays = []
    for i in range(len(colors)):
        color_displays.append([])
        for j in range(len(colors[i])):
            color_displays[i].append(mid_font.render(str(colors[i][j]), True, (0, 0, 0)))
    rgb = threading.Thread(target=rgb_display, args=(color_displays,))
    rgb.start()
    while True:
        bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        if bg == -1:
            c = 0
            bg = get_frame(os.path.join(current_directory, "images", "animations", "bg_test"), width, height, c)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_colors = False
                    pygame.time.wait(200)
                    rgb.join()
                    save_colors()
                    return
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                i = 0
                if 223 + 45 <= pos[1]*720/height <= 223 + 52 + 45:
                    i = 0
                elif 303 + 45 <= pos[1]*720/height <= 303 + 52 + 45:
                    i = 1
                elif 386 + 45 <= pos[1]*720/height <= 386 + 52 + 45:
                    i = 2
                elif 467 + 45 <= pos[1]*720/height <= 467 + 52 + 45:
                    i = 3
                if 88 + 145 <= pos[0]*1280/width < 88 + 52 + 145:
                    colors[i][0] -= 10
                    if colors[i][0] < 0:
                        colors[i][0] = 0
                elif 140 + 145 <= pos[0]*1280/width < 140 + 52 + 145:
                    colors[i][0] -= 1
                    if colors[i][0] < 0:
                        colors[i][0] = 0
                elif 272 + 145 <= pos[0]*1280/width < 272 + 52 + 145:
                    colors[i][0] += 1
                    if colors[i][0] > 255:
                        colors[i][0] = 255
                elif 324 + 145 <= pos[0]*1280/width <= 324 + 52 + 145:
                    colors[i][0] += 10
                    if colors[i][0] > 255:
                        colors[i][0] = 255
                elif 386 + 145 <= pos[0]*1280/width < 386 + 52 + 145:
                    colors[i][1] -= 10
                    if colors[i][1] < 0:
                        colors[i][1] = 0
                elif 438 + 145 <= pos[0]*1280/width < 438 + 52 + 145:
                    colors[i][1] -= 1
                    if colors[i][1] < 0:
                        colors[i][1] = 0
                elif 571 + 145 <= pos[0]*1280/width < 571 + 52 + 145:
                    colors[i][1] += 1
                    if colors[i][1] > 255:
                        colors[i][1] = 255
                elif 623 + 145 <= pos[0]*1280/width < 623 + 52 + 145:
                    colors[i][1] += 10
                    if colors[i][1] > 255:
                        colors[i][1] = 255
                elif 685 + 145 <= pos[0]*1280/width < 685 + 52 + 145:
                    colors[i][2] -= 10
                    if colors[i][2] < 0:
                        colors[i][2] = 0
                elif 737 + 145 <= pos[0]*1280/width < 737 + 52 + 145:
                    colors[i][2] -= 1
                    if colors[i][2] < 0:
                        colors[i][2] = 0
                elif 870 + 145 <= pos[0]*1280/width < 870 + 52 + 145:
                    colors[i][2] += 1
                    if colors[i][2] > 255:
                        colors[i][2] = 255
                elif 922 + 145 <= pos[0]*1280/width < 922 + 52 + 145:
                    colors[i][2] += 10
                    if colors[i][2] > 255:
                        colors[i][2] = 255
        screen.blit(bg, (0, 0))
        c += 1
        screen.blit(menu_screen, (145 * width / 1280, 45 * height / 720))
        pygame.draw.circle(screen, colors[0], (195 * width / 1280, 295 * height / 720), 25)
        pygame.draw.circle(screen, colors[1], (195 * width / 1280, 375 * height / 720), 25)
        pygame.draw.circle(screen, colors[2], (195 * width / 1280, 455 * height / 720), 25)
        pygame.draw.circle(screen, colors[3], (195 * width / 1280, 535 * height / 720), 25)
        pygame.display.flip()
        clock.tick(100)


def rgb_display(color_displays):
    clock.tick(100)
    mid_font = pygame.font.Font(None, int(40 * (width / 1280)))
    while in_colors:
        for c in range(len(color_displays)):
            y = 225 + 24 + 45 if c == 0 else 305 + 24 + 45 if c == 1 else 388 + 24 + 45 if c == 2 else 469 + 24 + 45
            for d in range(len(color_displays[c])):
                x = 232 + 145 + d * 300
                color_displays[c][d] = mid_font.render(str(colors[c][d]), True, (0, 0, 0))
                val = color_displays[c][d]
                screen.blit(val, ((x - (val.get_width() / 3)) * width / 1280, (y - val.get_height() / 3) * height / 720))


class Note:
    def __init__(self, x, y, key, color, type):
        self.x = x
        self.y = y
        self.key = key
        self.color = color
        self.radius = 50 * width/1280
        self.type = type

    def fall(self, dist):
        self.y += dist

    def draw(self, screen):
        if self.type is 1:
            val1 = self.color[0]
            val2 = self.color[1]
            val3 = self.color[2]
            val1 -= 100
            val2 -= 100
            val3 -= 100
            if val1 < 0:
                val1 = 0
            if val2 < 0:
                val2 = 0
            if val3 < 0:
                val3 = 0
            pygame.draw.circle(screen, (val1, val2, val3), (self.x + self.radius, self.y + self.radius), self.radius)
            pygame.draw.circle(screen, self.color, (self.x + self.radius, self.y + self.radius), self.radius - (7 * width/1280))
        else:
            pygame.draw.circle(screen, (255, 0, 0), (self.x + self.radius, self.y + self.radius), self.radius)
            pygame.draw.circle(screen, (0, 0, 0), (self.x + self.radius, self.y + self.radius), self.radius - (7 * width / 1280))


class HeldNote:
    def __init__(self, x, y, key, color, type):
        self.x = x
        self.y = y
        self.key = key
        self.color = color
        self.radius = 50 * width/1280
        self.type = type  # 2 for start, 3 for middle, 4 for end

    def draw(self, screen):
        if self.type == 2:
            val1 = self.color[0]
            val2 = self.color[1]
            val3 = self.color[2]
            val1 -= 100
            val2 -= 100
            val3 -= 100
            if val1 < 0:
                val1 = 0
            if val2 < 0:
                val2 = 0
            if val3 < 0:
                val3 = 0
            pygame.draw.circle(screen, (val1, val2, val3), (self.x + self.radius, self.y + self.radius), self.radius)
            pygame.draw.circle(screen, self.color, (self.x + self.radius, self.y + self.radius), self.radius - (7 * width/1280))
            pygame.draw.rect(screen, self.color, (self.x, self.y, 2*self.radius, self.radius))
        elif self.type == 3:
            pygame.draw.rect(screen, self.color, (self.x, self.y + 20 * width/1280, 2*self.radius, self.radius*180/bpm))
        elif self.type == 4:
            val1 = self.color[0]
            val2 = self.color[1]
            val3 = self.color[2]
            val1 -= 100
            val2 -= 100
            val3 -= 100
            if val1 < 0:
                val1 = 0
            if val2 < 0:
                val2 = 0
            if val3 < 0:
                val3 = 0
            pygame.draw.circle(screen, (val1, val2, val3), (self.x + self.radius, self.y + self.radius), self.radius)
            pygame.draw.circle(screen, self.color, (self.x + self.radius, self.y + self.radius), self.radius - (7 * width/1280))
            pygame.draw.rect(screen, self.color, (self.x, self.y + self.radius, 2 * self.radius, self.radius))

    def fall(self, dist):
        self.y += dist


def initialize_notes(columns):
    global colors
    notes = []
    current_time = pygame.time.get_ticks()

    for row, notes_in_row in enumerate(zip(*columns), start=1):
        for col_num, number in enumerate(notes_in_row, start=1):
            if number == 1 or number == 5:
                color = colors[col_num - 1]
                key = controls[col_num - 1]
                note = Note((90 + 200 * col_num) * width/1280, 0, key, color, number)
                notes.append((note, current_time))

            elif number in (2, 3, 4):
                color = colors[col_num-1]
                key = controls[col_num-1]
                held_note = HeldNote((90 + 200 * col_num) * width/1280, 0, key, color, number)
                notes.append((held_note, current_time))

            # Increment the current_time only for the next row
            if col_num == len(columns):
                current_time += 30000/bpm

    return notes


def playMusic():
    pygame.time.wait(2583 + key_delay)
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play()

def play(file, channel):
    pygame.mixer.Channel(channel).play(pygame.mixer.Sound(os.path.join(os.path.realpath(os.path.dirname(__file__)), "sound", "sfx", file + ".wav")))


def main():
    global fullscreen
    global running
    global screen
    global clock
    global autoclicker
    global controls
    global hit_sounds
    load_controls()
    load_delay()
    load_colors()
    loadMap(display_menu())
    start = True
    startText = font.render("Press Space to start.", True, (0, 0, 0))
    while start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                start = False
        screen.fill((255, 255, 255))
        screen.blit(startText, (400, 400))
        pygame.display.flip()
        pygame.display.update()
    acc1 = font.render("", True, (255, 255, 255))
    acc2 = font.render("", True, (255, 255, 255))
    acc3 = font.render("", True, (255, 255, 255))
    acc4 = font.render("", True, (255, 255, 255))
    columns = [column1, column2, column3, column4]
    notes = initialize_notes(columns)
    music = threading.Thread(target=playMusic, args=())
    music.start()
    ws = 0
    nices = 0
    oks = 0
    bruhs = 0
    ls = 0
    misses = 0
    yikess = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
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
                    if note and event.key == note.key and note.y >= 400 * height/720:
                        notes.remove((note, _))
                        if note.key == controls[0]:
                            if note.type == 5:
                                acc1 = font.render("Yikes", True, (230, 0, 0))
                                yikess += 1
                            else:
                                if hit_sounds:
                                    play("hit", 1)
                                if 520 * height/720 <= note.y <= 530 * height/720:
                                    acc1 = font.render("W!", True, (250, 250, 0))
                                    ws += 1
                                elif 500 * height/720 <= note.y <= 550 * height/720:
                                    acc1 = font.render("Nice!", True, (0, 230, 0))
                                    nices += 1
                                elif 475 * height/720 <= note.y <= 575 * height/720:
                                    acc1 = font.render("OK", True, (0, 0, 255))
                                    oks += 1
                                elif 450 * height/720 <= note.y <= 600 * height/720:
                                    acc1 = font.render("Bruh", True, (0, 0, 0))
                                    bruhs += 1
                                else:
                                    acc1 = font.render("L", True, (255, 0, 0))
                                    ls += 1
                        if note.key == controls[1]:
                            if note.type == 5:
                                acc2 = font.render("Yikes", True, (230, 0, 0))
                                yikess += 1
                            else:
                                if hit_sounds:
                                    play("hit", 2)
                                if 520 * height / 720 <= note.y <= 530 * height / 720:
                                    acc2 = font.render("W!", True, (250, 250, 0))
                                    ws += 1
                                elif 500 * height / 720 <= note.y <= 550 * height / 720:
                                    acc2 = font.render("Nice!", True, (0, 230, 0))
                                    nices += 1
                                elif 475 * height / 720 <= note.y <= 575 * height / 720:
                                    acc2 = font.render("OK", True, (0, 0, 255))
                                    oks += 1
                                elif 450 * height / 720 <= note.y <= 600 * height / 720:
                                    acc2 = font.render("Bruh", True, (0, 0, 0))
                                    bruhs += 1
                                else:
                                    acc2 = font.render("L", True, (255, 0, 0))
                                    ls += 1
                        if note.key == controls[2]:
                            if note.type == 5:
                                acc3 = font.render("Yikes", True, (230, 0, 0))
                                yikess += 1
                            else:
                                if hit_sounds:
                                    play("hit", 3)
                                if 520 * height / 720 <= note.y <= 530 * height / 720:
                                    acc3 = font.render("W!", True, (250, 250, 0))
                                    ws += 1
                                elif 500 * height / 720 <= note.y <= 550 * height / 720:
                                    acc3 = font.render("Nice!", True, (0, 230, 0))
                                    nices += 1
                                elif 475 * height / 720 <= note.y <= 575 * height / 720:
                                    acc3 = font.render("OK", True, (0, 0, 255))
                                    oks += 1
                                elif 450 * height / 720 <= note.y <= 600 * height / 720:
                                    acc3 = font.render("Bruh", True, (0, 0, 0))
                                    bruhs += 1
                                else:
                                    acc3 = font.render("L", True, (255, 0, 0))
                                    ls += 1
                        if note.key == controls[3]:
                            if note.type == 5:
                                acc4 = font.render("Yikes", True, (200, 0, 0))
                                yikess += 1
                            else:
                                if hit_sounds:
                                    play("hit", 4)
                                if 520 * height / 720 <= note.y <= 530 * height / 720:
                                    acc4 = font.render("W!", True, (250, 250, 0))
                                    ws += 1
                                elif 500 * height / 720 <= note.y <= 550 * height / 720:
                                    acc4 = font.render("Nice!", True, (0, 230, 0))
                                    nices += 1
                                elif 475 * height / 720 <= note.y <= 575 * height / 720:
                                    acc4 = font.render("OK", True, (0, 0, 255))
                                    oks += 1
                                elif 450 * height / 720 <= note.y <= 600 * height / 720:
                                    acc4 = font.render("Bruh", True, (0, 0, 0))
                                    bruhs += 1
                                else:
                                    acc4 = font.render("L", True, (255, 0, 0))
                                    ls += 1
                        break  # Break to only remove one note for the pressed key
            elif event.type == pygame.KEYUP:
                for note, _ in notes:
                    if note and event.key == note.key and note.y >= 400 * height/720:
                        if note.type == 3:
                            continue
                        if note.type == 4:
                            notes.remove((note, _))
                            if note.key == controls[0]:
                                if hit_sounds:
                                    play("hit", 1)
                                acc1 = font.render("W!", True, (250, 250, 0)) if 520 * height/720 <= note.y <= 530 * height/720 else font.render("Nice!", True, (0, 230, 0)) if 500 * height/720 <= note.y <= 550 * height/720 else font.render("OK", True, (0, 0, 255)) if 475 * height/720 <= note.y <= 575 * height/720 else font.render("Bruh", True, (0, 0, 0)) if 450 * height/720 <= note.y <= 600 * height/720 else font.render("L", True, (255, 0, 0))
                            if note.key == controls[1]:
                                if hit_sounds:
                                    play("hit", 2)
                                acc2 = font.render("W!", True, (250, 250, 0)) if 520 * height/720 <= note.y <= 530 * height/720 else font.render("Nice!", True, (0, 230, 0)) if 500 * height/720 <= note.y <= 550 * height/720 else font.render("OK", True, (0, 0, 255)) if 475 * height/720 <= note.y <= 575 * height/720 else font.render("Bruh", True, (0, 0, 0)) if 450 * height/720 <= note.y <= 600 * height/720 else font.render("L", True, (255, 0, 0))
                            if note.key == controls[2]:
                                if hit_sounds:
                                    play("hit", 3)
                                acc3 = font.render("W!", True, (250, 250, 0)) if 520 * height/720 <= note.y <= 530 * height/720 else font.render("Nice!", True, (0, 230, 0)) if 500 * height/720 <= note.y <= 550 * height/720 else font.render("OK", True, (0, 0, 255)) if 475 * height/720 <= note.y <= 575 * height/720 else font.render("Bruh", True, (0, 0, 0)) if 450 * height/720 <= note.y <= 600 * height/720 else font.render("L", True, (255, 0, 0))
                            if note.key == controls[3]:
                                if hit_sounds:
                                    play("hit", 4)
                                acc4 = font.render("W!", True, (250, 250, 0)) if 520 * height/720 <= note.y <= 530 * height/720 else font.render("Nice!", True, (0, 230,  0)) if 500 * height/720 <= note.y <= 550 * height/720 else font.render("OK", True, (0, 0, 255)) if 475 * height/720 <= note.y <= 575 * height/720 else font.render("Bruh", True, (0, 0, 0)) if 450 * height/720 <= note.y <= 600 * height/720 else font.render("L", True, (255, 0, 0))
                        break

        current_time = pygame.time.get_ticks()

        for note, note_time in notes:
            if note:
                # Check if the note should be drawn based on the time delay
                if current_time >= note_time:
                    if note.y >= 525 * height/720 and autoclicker:
                        if note.type in (1, 2, 4):
                            if hit_sounds:
                                play("hit", 1 if note.key == controls[0] else 2 if note.key == controls[1] else 3 if note.key == controls[2] else 4)
                            notes.remove((note, note_time))

                    if note.type in (3, 5) and note.y >= 525 * height/720:
                        # Clear type 3 and 5 notes at the "W!" spot for simplicity's sake
                        notes.remove((note, note_time))
                    else:
                        note.fall(5 * width/1920)
                        note.draw(screen)

        pygame.display.flip()
        pygame.display.update()
        clock.tick(60)

        # Remove notes that have fallen off the screen
        for note, _ in notes:
            if note.y > height and note.type not in (3, 5):
                misses += 1
                if note.key == controls[0]:
                    acc1 = font.render("Miss", True, (125, 0, 0))
                if note.key == controls[1]:
                    acc2 = font.render("Miss", True, (125, 0, 0))
                if note.key == controls[2]:
                    acc3 = font.render("Miss", True, (125, 0, 0))
                if note.key == controls[3]:
                    acc4 = font.render("Miss", True, (125, 0, 0))
        notes = [(note, note_time) for note, note_time in notes if note and note.y <=  height]

        if len(notes) == 0:
            totalWs = font.render(f"{ws} \"W\"s", True, (0, 0, 0))
            if ws == 1:
                totalWs = font.render("1 \"W\"", True, (0, 0, 0))
            totalNices = font.render(f"{nices} \"Nice\"s", True, (0, 0, 0))
            if nices == 1:
                totalNices = font.render("1 \"Nice\"", True, (0, 0, 0))
            totalOKs = font.render(f"{oks} \"OK\"s", True, (0, 0, 0))
            if oks == 1:
                totalOKs = font.render("1 \"OK\"", True, (0, 0, 0))
            totalBruhs = font.render(f"{bruhs} \"Bruh\"s", True, (0, 0, 0))
            if bruhs == 1:
                totalBruhs = font.render("1 \"Bruh\"", True, (0, 0, 0))
            totalLs = font.render(f"{ls} \"L\"s", True, (0, 0, 0))
            if ls == 1:
                totalLs = font.render("1 \"L\"", True, (0, 0, 0))
            totalYikess = font.render(f"{yikess} \"Yikes\"s", True, (0, 0, 0))
            if yikess == 1:
                totalYikess = font.render("1 \"Yikes\"", True, (0, 0, 0))
            totalMisses = font.render(f"{misses} Misses", True, (0, 0, 0))
            if misses == 1:
                totalMisses = font.render("1 Miss", True, (0, 0, 0))
            maxScore = (ws + nices + oks + bruhs + ls + misses) * 100
            score = ws * 100 + nices * 75 + oks * 50 + bruhs * 25 + misses * -100 + yikess * -100
            scoretext = font.render(f"{score}/{maxScore}", True, (0, 0, 0))
            screen.fill((255, 255, 255))  # Clear the screen
            screen.blit(hitMarker, (290 * width / 1280, 450 * height / 720))
            screen.blit(hitMarkerTwo, (490 * width / 1280, 450 * height / 720))
            screen.blit(hitMarkerThree, (690 * width / 1280, 450 * height / 720))
            screen.blit(hitMarkerFour, (890 * width / 1280, 450 * height / 720))
            screen.blit(totalWs, (800 * width / 1280, 50 * height / 720))
            screen.blit(totalNices, (800 * width / 1280, 100 * height / 720))
            screen.blit(totalOKs, (800 * width / 1280, 150 * height / 720))
            screen.blit(totalBruhs, (800 * width / 1280, 200 * height / 720))
            screen.blit(totalLs, (800 * width / 1280, 250 * height / 720))
            screen.blit(totalYikess, (800 * width / 1280, 300 * height / 720))
            screen.blit(totalMisses, (800 * width/1280, 350 * height/720))
            screen.blit(scoretext, (800 * width/1280, 400 * height/720))

            pygame.display.flip()
            pygame.display.update()
            pygame.time.wait(5000)
            break
        screen.fill((255, 255, 255))  # Clear the screen
        screen.blit(hitMarker, (290 * width / 1280, 450 * height / 720))
        screen.blit(hitMarkerTwo, (490 * width / 1280, 450 * height / 720))
        screen.blit(hitMarkerThree, (690 * width / 1280, 450 * height / 720))
        screen.blit(hitMarkerFour, (890 * width / 1280, 450 * height / 720))

        screen.blit(acc1, (400 * width / 1280, 560 * height / 720))
        screen.blit(acc2, (600 * width / 1280, 560 * height / 720))
        screen.blit(acc3, (800 * width / 1280, 560 * height / 720))
        screen.blit(acc4, (1000 * width / 1280, 560 * height / 720))
    music.join()


while running:
    main()
    column1 = []
    column2 = []
    column3 = []
    column4 = []
