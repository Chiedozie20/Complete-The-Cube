from ursina import *
import copy
import sys
import time
import random
import numpy as np
import json
import datetime
import cv2 as cv
from PIL import Image
from rubiks_database import CubeDB

# VARIABLES
#############################################################
app = Ursina()
s = Sky()
window.size = (800, 800)
window.borderless = False
window.fullscreen = False
window.position = (50, 50)
EditorCamera()  # adds camera controls to ursina scene
Text.size = 0.02
Text.default_resolution = 1080 * Text.size
options_txt = Text(background=True, x=-0.8, y=0.4,
                   text="Reset: 1   Save: 2   Solve next level: 3   Scramble: 4   Solve all: 5   Load cube: 6   Input cube: 7")
state_txt = Text(visible=False, background=True, x=0.3, y=0.4, text="next step = solve white cross")
timer_txt = Text(size=0.04, origin=(0, -7), background=True, text="0:00", center=True)

tip_txt = Text(x=-0.8, y=-0.4,
               text="HOLD 'Z' to run through chosen solution: TAP SPACEBAR to begin and end solve timer:   PRESS ESCAPE FOR MENU",
               color=color.red)

# Test saved cube
saved = [(0, 180, -90), (0, 0, -90), (-90, -90, -90), (0, 180, -90), (0, 0, 90), (90, 0, -90), (0, 90, -90),
         (-90, 0, 0), (0, 0, 0), (0, 0, -90), (0, 0, -90), (0, 0, -90), (0, -180, 90), (0, -180, -90), (0, -180, 0),
         (-90, 0, 90), (0, -180, -90), (0, -90, -180), (0, 90, 0), (90, 0, 0), (90, 0, 0), (-90, 0, -90), (0, 0, 90),
         (0, 90, 180), (90, -90, 90), (0, -90, -90), (90, 0, 180)]

# Test saved solution and scramble
example = ['F', 'U', 'D', 'Bi', 'D', 'Di', 'U', 'D', 'L', 'Ui', 'D', 'D', 'F', 'Ri', 'Fi', 'D', 'D', 'Bi', 'D', 'D',
           'Li', 'Ui', 'L', 'Ri', 'U', 'U', 'R', 'Ui', 'Bi', 'U', 'B', 'U', 'L', 'Ui', 'Li', 'U', 'U', 'R', 'Ui', 'Ri',
           'Ui', 'Fi', 'U', 'F', 'L', 'Fi', 'Li', 'F', 'Li', 'Ui', 'L', 'L', 'Fi', 'Li', 'F', 'Li', 'Ui', 'L', 'R',
           'Bi', 'Ri', 'B', 'Ri', 'Ui', 'R', 'U', 'L', 'Fi', 'Li', 'F', 'Li', 'Ui', 'L', 'Bi', 'R', 'B', 'Ri', 'B', 'U',
           'Bi', 'U', 'U', 'F', 'U', 'R', 'Ui', 'Ri', 'Fi', 'U', 'Ri', 'F', 'R', 'Bi', 'Ri', 'Fi', 'R', 'B', 'U', 'U',
           'Ri', 'Ui', 'R', 'U', 'Di', 'R', 'R', 'U', 'Ri', 'U', 'R', 'Ui', 'R', 'Ui', 'R', 'R', 'D', 'U', 'U']

# dictionary of information of different turns format of dictionary is axis, layer, rotation
rot_dict = {'u': ['y', 1, 90], 'd': ['y', -1, -90], 'l': ['x', -1, -90], 'r': ['x', 1, 90], 'f': ['z', -1, 90],
            'b': ['z', 1, -90]}

# variables for input function
inst3D = None
instDB = None
movelist = []
t = 0
prev = 0
current = 0
vector = [2, 3]
counter = 0
running = False
menu_up = False
menu_instance = None
hint_count = 0

timer = 0.0
timer_on = False
# build in ursina function, it is called every time a key is pressed
hint_count = 0


def hints():
    # create instance of solver class
    instSolve = Solver()
    # put 3d cube pos into solver.cube by running through the list of moves that the 3d cube has done
    instSolve.runthrough(inst3D.movelist3D)
    # display the current completion stage of the 3d cube
    solvestate = instSolve.check_state()
    state_txt.text = solvestate[0]  # current solved state
    state_txt.visible = True  # lets user see current state


hint_button = Button(text="Hints", text_color=color.red, text_scale=2, origin=(7, 0), color=color.blue,
    highlight_color=color.azure, pressed_color=color.green, scale=0.1, on_click=hints

)


def secs_to_mins(secs):
    mins = secs / 60
    secs = round((mins - int(mins)) * 60)
    if secs < 10:
        secs = "0" + str(secs)

    mins_txt = f"{int(mins)}:{secs}"
    return mins_txt


def update():
    global timer
    time_elapsed = int(time.time() - timer)
    formatted_time = secs_to_mins(time_elapsed)
    if timer_txt.text != formatted_time and timer_on:
        timer_txt.text = formatted_time


def input(key):
    global t, prev, current, vector, counter, running, menu_up, menu_instance, example, timer, timer_on

    if key == "space":
        if timer_on:
            timer_on = False
            time_elapsed = int(time.time() - timer)
            timer_txt.color = color.white
            print(("do you wish to save your time score? y/n"))
            answer = sys.stdin.readline()[:1].lower()
            if answer == "y":
                if not instDB.logged_in:
                    print("you must log in first")
                    instDB.log_in()
                instDB.add_score(
                    [instDB.username, str(datetime.datetime.now())[:16], secs_to_mins(time_elapsed), time_elapsed])
                print("score added")
            else:
                pass
            timer_txt.text = "0:00"
        elif not timer_on:
            timer_on = True
            timer = time.time()
            timer_txt.color = color.red
    if key == "j":
        print(LVector3f(camera.world_position))
        print(LVector3f(camera.world_rotation))
        print((mouse.position.x * 10, mouse.position.y * 10, mouse.position.z * 10), "\n")
    if key == "1":
        inst3D.reset()
    # save the cube
    if key == "2":
        inst3D.save()

    # solve layer
    if key == "3":
        # create instance of solver class
        instSolve = Solver()
        # put 3d cube pos into solver.cube by running through the list of moves that the 3d cube has done
        instSolve.runthrough(inst3D.movelist3D)
        # display the current completion stage of the 3d cube
        solvestate = instSolve.check_state()
        state_txt.text = solvestate[0]  # current solved state
        state_txt.visible = True  # lets user see current state
        # saves moves to solve next step
        nextstep = solvestate[1].replace(" ", "")  # next step function string is created
        instSolve.show = True  # appends moves to solve list but doesnt perform them or add them to move list
        if nextstep != "Solved":  # cannot solve already solved cube
            exec(f"instSolve.{nextstep}()")  # perform next step
        else:
            return
        instSolve.show = False  # next step didn't change instsolve.cube
        example = instSolve.solvelist  # list of moves to solve cube
        example = Optimiser(example).flatten(example)
        print(example)
        counter = 0
    # scramble
    if key == "9":
        inst3D.build_cube()
    if held_keys["4"] and not time.time() - t < 0.3:
        inst3D.rotator(random.choice(list(rot_dict.keys())) + random.choice(["", "i"]), speed=0.2)
        t = time.time()
    # solve all
    if key == "5":
        instSolve = Solver()  # create instance of solver class
        instSolve.runthrough(inst3D.movelist3D)  # put 3d cube pos into solver.cube
        instSolve.display_cube()
        instSolve.show = True
        instSolve.solveCube()
        instSolve.show = False
        example = instSolve.solvelist  # list of moves to solve cube
        example = Optimiser(example).flatten(example)
        print("3d inputs this")
        instSolve.printCube()
        print(example)
    # load cube
    if key == "6":
        # inst3D.delete_all()
        inst3D.load()
    # open menu
    if key == "7":
        if hint_count == 0:
            # create instance of solver class
            instSolve = Solver()
            # put 3d cube pos into solver.cube by running through the list of moves that the 3d cube has done
            instSolve.runthrough(inst3D.movelist3D)
            # display the current completion stage of the 3d cube
            solvestate = instSolve.check_state()
            state_txt.text = solvestate[0]  # current solved state
            state_txt.visible = True  # lets user see current state
        elif hint_count == 1:
            pass
    if key == "8":
        input_cube()

    if key == "escape":
        if not menu_up:
            menu_instance = MainMenu()
            menu_instance.display_menu(menu_instance.main_menu)
            menu_up = True
        else:
            menu_instance = None
            menu_up = False

    # mouse input
    if key == "left mouse down":
        current = 1
    else:
        current = 0
    if prev == 0 and current == 1:
        vector[0] = LVector3f(mouse.position).x, LVector3f(mouse.position).y
        prev = 1
    if prev == 1 and current == 0:
        vector[1] = LVector3f(mouse.position).x, LVector3f(mouse.position).y
        prev = 0
        if not time.time() - t < 0.5:
            inst3D.gradient(vector[0], vector[1])
            t = time.time()
    # run sequence
    if held_keys["z"]:
        running = True

        if counter == len(example):
            running = False
            inst3D.USD = False

        if not time.time() - t < 0.3 and running:
            inst3D.rotator(example[counter], speed=0.1)
            t = time.time()
            counter += 1

    # time keeper, prevents spam
    elif time.time() - t < 0.6 or key not in rot_dict:  # doesnt allow user to spam buttons
        return

    # does rotation of key press
    else:
        t = time.time()
        inst3D.rotator(inst3D.adjustment(inst3D.get_front_face())[key.upper()])


def input_cube():
    print("in")
    global inst3D
    instCV = CubeCV()
    instCV.webcam()
    print("out")
    if instCV.check_legitimacy():
        inst3D = Cube3D(cube=instCV.cube)
        inst3D.build_cube(instCV.cube_to_rotations())
        inst3D.initCube()
        app.run()
    else:
        print("Capture failed, try in different lighting")


class Cube3D():
    def __init__(self, cube=[]):
        self.cube = cube
        self.center = Entity()  # sets center as the center of rotation
        self.movelist3D = []
        self.runfront = "F"
        self.col_to_face_dict = {"G": "F", "B": "B", "O": "L", "R": "R", "U": "Y", "D": "D"}
        self.USD = False

    # this function creates the cube entities and puts them in a list
    def initCube(self):
        if len(self.cube) == 0:
            for x in (-1, 0, 1):  # these nested for loops create 27 cubie entities
                for y in (-1, 0, 1):
                    for z in (-1, 0, 1):
                        pos = (x, y, z)
                        self.cube.append(
                            Entity(model='cube_model.obj', texture='cube_texture.png', position=pos, rotation=(0, 0, 0),
                                   scale=0.5))  # entity defines and creates the 27 cubes,

    # deletes all cube entities
    def reset(self):
        self.delete_all()
        self.initCube()
        self.movelist3D = []

    def delete_all(self):
        if len(self.cube) > 0:
            for i in reversed(self.cube):
                destroy(i)
            self.cube.clear()

    # attaches cubies on a face to the center
    def parent_child_relation(self, axis, layer):
        # parent relates to the middle of a face and the children are the 8 outer cubies
        for c in self.cube:
            c.position, c.rotation = round(c.world_position, 1), c.world_rotation
            c.parent = scene

        self.center.rotation = 0

        for c in self.cube:

            if eval(f'c.position.{axis}') == layer:
                c.parent = self.center

    def get_front_face(self):
        camera_position = LVector3f(camera.world_position)  # xyz position of where camera is
        center_location = {"U": (0, 1, 0), "D": (0, -1, 0), "L": (-1, 0, 0), "R": (1, 0, 0), "F": (0, 0, -1),
                           "B": (0, 0, 1)}  # location of each og the center cubies
        distance_dict = {}
        for key, value in center_location.items():  # calculates distance between centers and camera
            distance = sqrt((value[0] - camera_position[0]) ** 2 + (value[1] - camera_position[1]) ** 2 + (
                    value[2] - camera_position[2]) ** 2)
            distance_dict[round(distance, 2)] = key

        front_face = distance_dict[min(distance_dict)]
        return front_face  # returns nearest face as string

    def adjustment(self, front_face):
        # sets which corresponding face you must turn depending on which face is at the front
        adjustment_dict = {"F": "F", "R": "R", "B": "B", "L": "L", "U": "U", "D": "D"}
        if front_face == "F":
            adjustment_dict = {"F": "F", "R": "R", "B": "B", "L": "L", "U": "U", "D": "D"}
        elif front_face == "R":
            adjustment_dict = {"F": "R", "R": "B", "B": "L", "L": "F", "U": "U", "D": "D"}
        elif front_face == "L":
            adjustment_dict = {"F": "L", "R": "F", "B": "R", "L": "B", "U": "U", "D": "D"}
        elif front_face == "B":
            adjustment_dict = {"F": "B", "R": "L", "B": "F", "L": "R", "U": "U", "D": "D"}
        elif front_face == "U":
            adjustment_dict = {"F": "U", "R": "R", "B": "D", "L": "L", "U": "B", "D": "F"}
        elif front_face == "D":
            adjustment_dict = {"F": "D", "R": "R", "B": "U", "L": "L", "U": "F", "D": "B"}
        return adjustment_dict

    # sets which corresponding face you must turn depending on if the cube is upside down
    def upside_down(self, move):
        adjustment_dict = {"F": "F", "R": "L", "B": "B", "L": "R", "U": "D", "D": "U"}
        adjusted_move = adjustment_dict[move[0]]
        return adjusted_move

    # performs move based on mouse movement
    def gradient(self, start, end):
        x1, y1 = start
        x2, y2 = end
        if sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < 0.05:
            return
        try:  # if the gradient becomes infinite put it s 100
            grad = (y2 - y1) / (x2 - x1)
        except ZeroDivisionError:
            grad = 100
        front_face = self.get_front_face()
        adjustment_dict = self.adjustment(front_face)
        if abs(grad) > 1:  # if vertical drag
            if x1 > 0 and x2 > 0:  # if drag occurs on right side of cube
                if y1 < y2:  # if drag is from bottom to top
                    self.rotator(adjustment_dict["R"])
                else:
                    self.rotator(adjustment_dict["R"] + "i")
            elif x1 < 0 and x2:  # if drag occurs on left side of cube
                if y1 < y2:
                    self.rotator(adjustment_dict["L"] + "i")
                else:
                    self.rotator(adjustment_dict["L"])
        elif abs(grad) < 1:  # if horizontal drag
            if y1 > 0 and y2 > 0:  # if drag occurs on top side of cube
                if x1 < x2:  # if drag is from right to left
                    self.rotator(adjustment_dict["U"] + "i")
                else:
                    self.rotator(adjustment_dict["U"])

            elif y1 < 0 and y2 < 0:
                if x1 < x2:
                    self.rotator(adjustment_dict["D"])
                else:
                    self.rotator(adjustment_dict["D"] + "i")

    def get_up_face(self, front):
        # call this when down or up is at the front.
        # find the closest of these to the camera position and apply the previously defined adjusts to it

        possible_degrees = [-180, -90, 0, 90, 180]

        # when looking at bot yellow,
        # up = green = -90,0,0
        # up = red = -90,-90,0
        # up = blue = -90,0,-180
        # up = orange = -90,-90,-180

        # when looking at top white,
        # up = green = 90,0,0
        # up = red = 90,-90,180
        # up = blue = 90,-180,180
        # up = orange = 90,90,0
        pass  # find vector to get to each cubeie, the greatest gradient will be the top cubie

    # rotates side of cube
    def rotator(self, key, speed=0.4):
        key = key.upper()
        # if a turn move:
        if key[0] == "Y":
            # new color of front = key[-1]
            self.runfront = self.col_to_face_dict[key[-1]]
            return
        if key[0] == "Z":
            # turn cube upside down if a z move is done
            if self.USD:
                self.USD = False
            else:
                self.USD = True
            return
        if held_keys["z"]:
            if self.USD:  # if cube is upside down, adjust the move accordingly
                if len(key) == 1:  # if clockwise rotation
                    key = self.upside_down(key)
                else:  # if anticlockwise rotation
                    key = self.upside_down(key) + key[-1]
            if running:
                if len(key) == 1:
                    key = self.adjustment(self.runfront)[key[0]]
                else:
                    key = self.adjustment(self.runfront)[key[0]] + key[-1]

        key = key.lower()
        axis, layer, rotation = rot_dict[key[0]]  # e.g 'x', 1, 90
        self.parent_child_relation(axis, layer)
        # if shift is helpd, perform the inverse move
        shift = held_keys["shift"]
        if shift:
            self.movelist3D.append(key.upper() + "i")
        elif len(key) == 1:
            self.movelist3D.append(key.upper())
        else:
            self.movelist3D.append(key[0].upper() + "i")

        if shift or key[-1] == "i":
            rotation = -rotation
        eval(f'self.center.animate_rotation_{axis} ({rotation}, duration = {speed})')

    # loads saved cube
    def load(self):
        global instDB, inst3D

        cubie_rotations, move_history = instDB.load_cube()
        if cubie_rotations == 0:
            return
        cubie_rotations = json.loads(cubie_rotations)
        inst3D.movelist3D = json.loads(move_history)
        self.build_cube(cubie_rotations)
        print("Cube loaded")

    def build_cube(self, cubie_rotations=saved):

        self.delete_all()
        # inst3D.cube.clear()
        inst3D.cube = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    pos = (x, y, z)
                    inst3D.cube.append(Entity(model='cube_model.obj', texture='cube_texture.png', position=pos,
                                              rotation=cubie_rotations.pop(), scale=0.5))

    # saves position of cubes
    def save(self):
        global saved
        while 1:

            if not instDB.logged_in:
                print("you must log in first to save a cube")
                instDB.log_in()

            rotations = []
            for i in reversed(range(27)):
                d = self.cube[i]
                i, j, k = d.rotation.x, d.rotation.y, d.rotation.z
                rotations.append((int(i), int(j), int(k)))
            saved = rotations
            savename = input2("Enter save name:")
            instDB.add_cube([instDB.username, savename, str(datetime.datetime.now())[:16], json.dumps(saved),
                             json.dumps(inst3D.movelist3D)])
            print(f"'{savename}' saved")
            break
            """else:
                print("you must log in first to save a cube")
                if not instDB.log_in():
                    print("not saved")
                    return"""


class Optimiser:
    def __init__(self, start_lst, moves=None):
        self.start_lst = start_lst
        self.string = moves
        # start_list = ["R", "U", "R2", "R3", "D2", "U1"]
        # self.start_lst = self.make_list("F F F D R R' R", prime_val="'")
        self.flattened = self.flatten(self.start_lst)
        self.annihilated = self.annihilate(self.flattened.copy())
        self.rle = self.run_length_encode(self.annihilated)
        self.checked = self.check_letters(self.rle)

    def check_letters(self, input_lst):
        output_lst = []
        # loop through the letters in the input list
        for letter in input_lst:
            number = letter[-1]
            # if there is a  number on the end of the move (the move is repeated)
            if number.isnumeric():
                letters, number = letter[:-1], int(number)
                # if there are 3 of a move on a run, replace it with 1 of the inverse move
                if number == 3:
                    if "i" in letters:
                        letters = letters.replace("i", "")
                    else:
                        letters += "i"
                    output_lst.append(letters)
                # if there are 2 moves on a run, always display it with the basic move (rather than the inverse) because
                # they are the same
                elif number == 2:
                    output_lst.append(letters.replace("i", "") + "2")
                # otherwise, just add the move to the list as it was
                else:
                    output_lst.append(letters + str(number))
            # otherwise, add the move with no number attached
            else:
                output_lst.append(letter)

        return output_lst

    def run_length_encode(self, input_lst):
        counter = 1
        letter = ""
        output = []
        # loops through the moves in the list
        for new_letter in input_lst:
            # if the new letter is the same as the old letter, add 1 to the counter for that letter
            if new_letter == letter:
                counter += 1
            else:
                # if the new letter is not the first letter, add the old letter and its counter to the list
                if letter != "":
                    # use %4 because doing 4 of the same move on a run goes all the way round the cube
                    counter = counter % 4
                    # if the counter is not 0, add the letter to the list
                    if counter > 0:
                        # only add the number to the move if it is more than 1
                        num = str(counter) if counter > 1 else ""
                        output.append(letter + num)
                letter = new_letter
                counter = 1
        # add the final letter and its number to the list, in the same way as it was done in the loop
        counter = counter % 4
        if counter > 0:
            num = str(counter) if counter > 1 else ""
            output.append(letter + num)

        return output

    def flatten(self, input_lst):
        output_lst = []
        # loop through the items in the input list
        for item in input_lst:
            # get the number corresponding to how many of the moves are done on a run
            number = item[-1]
            # if the 'number' is a letter, there is no number so there must be only one of the move done
            if number.isnumeric() and item[0] != "Z":
                # get the move that is being done and append it to the list 'number' times
                move = item[:-1]
                for _ in range(int(number)):
                    output_lst.append(move)
            else:
                output_lst.append(item)

        return output_lst

    def annihilate(self, input_lst):
        index = 0
        letter = ""
        letters_changed = True
        # loop round until there have been no changes (similar to bubble sort lol)
        while letters_changed:
            # loop through the list with a variable counter so that you can remove items and change the counter back to
            # where the new items are.
            letters_changed = False
            while index < len(input_lst):
                new_letter = input_lst[index]
                remove_val = False
                # check for move then inverse
                if new_letter == letter + "i" or new_letter + "i" == letter:
                    remove_val = True

                # remove the letter and the letter before and move the counter back to the old letter
                if remove_val:
                    del input_lst[index]
                    del input_lst[index - 1]
                    index -= 2
                    letters_changed = True
                    letter = ""
                # increment the counter
                else:
                    index += 1
                    letter = new_letter

        return input_lst


class MenuButton(Button):

    def __init__(self, text=None, **kwargs):
        super().__init__(text, scale=(.25, .075), highlight_color=color.azure, **kwargs)

        for key, value in kwargs.items():
            setattr(self, key, value)


class MainMenu:

    def __init__(self):
        self.button_spacing = .075 * 1.25
        self.menu_parent = Entity(parent=camera.ui, y=.15)

        self.no_menu = Entity(parent=self.menu_parent)
        self.main_menu = Entity(parent=self.menu_parent)
        self.load_menu = Entity(parent=self.menu_parent)
        self.options_menu = Entity(parent=self.menu_parent)

        self.style_menu = Entity(parent=self.menu_parent)
        self.control_menu = Entity(parent=self.menu_parent)
        state_handler = Animator(
            {'main_menu': self.main_menu, 'load_menu': self.load_menu, 'options_menu': self.options_menu,
             'no_menu': self.no_menu, 'style_menu': self.style_menu, 'control_menu': self.control_menu})

        self.main_menu.buttons = [MenuButton('resume', on_click=Func(setattr, state_handler, 'state', 'no_menu')),
                                  # MenuButton('reset', on_click=Func(inst3D.reset)),
                                  MenuButton('scoreboard', on_click=Func(CubeDB().display_scores)),
                                  MenuButton('save game', on_click=Func(inst3D.save)),
                                  MenuButton('load game', on_click=Func(inst3D.load)),
                                  MenuButton('log in', on_click=Func(instDB.log_in)),
                                  MenuButton('options', on_click=Func(setattr, state_handler, 'state', 'options_menu')),
                                  MenuButton('quit', on_click=Sequence(Wait(.01), Func(sys.exit)))]

        self.options_menu.buttons = [

            MenuButton(parent=self.options_menu, text="style", y=-1 * self.button_spacing,
                       on_click=Func(setattr, state_handler, 'state', 'style_menu')),
            MenuButton(parent=self.options_menu, text="controls", y=-2 * self.button_spacing,
                       on_click=Func(setattr, state_handler, 'state', 'control_menu')),
            # MenuButton(parent=self.options_menu, text="", y=-3 * self.button_spacing),
            MenuButton(parent=self.options_menu, text='back', y=(-5 * self.button_spacing),
                       on_click=Func(setattr, state_handler, 'state', 'main_menu'))]

        self.style_menu.buttons = [MenuButton(parent=self.style_menu, text="pastel", y=-1 * self.button_spacing),
                                   MenuButton(parent=self.style_menu, text="original", y=-2 * self.button_spacing),
                                   MenuButton(parent=self.style_menu, text="colour blind", y=-3 * self.button_spacing),
                                   MenuButton(parent=self.style_menu, text='back', y=(-5 * self.button_spacing),
                                              on_click=Func(setattr, state_handler, 'state', 'options_menu'))]

        self.control_menu.buttons = [MenuButton(parent=self.control_menu, text="RL UD FB", y=-1 * self.button_spacing),
                                     MenuButton(parent=self.control_menu, text="DA WS QE", y=-2 * self.button_spacing),
                                     MenuButton(parent=self.control_menu, text='back', y=(-5 * self.button_spacing),
                                                on_click=Func(setattr, state_handler, 'state', 'options_menu'))]

    def display_menu(self, menu):
        for count, entity in enumerate(menu.buttons):
            entity.parent = menu
            entity.y = -count * self.button_spacing


class handler:
    def __init__(self, cube=None):
        if cube is None:
            cube = [[['W', 'W', 'W'],  # upper 0
                     ['W', 'W', 'W'], ['W', 'W', 'W']],

                    [['G', 'G', 'G'],  # front 1
                     ['G', 'G', 'G'], ['G', 'G', 'G']],

                    [['R', 'R', 'R'],  # right 2
                     ['R', 'R', 'R'], ['R', 'R', 'R']],

                    [['O', 'O', 'O'],  # left 3
                     ['O', 'O', 'O'], ['O', 'O', 'O']],

                    [['Y', 'Y', 'Y'],  # down 4
                     ['Y', 'Y', 'Y'], ['Y', 'Y', 'Y']],

                    [['B', 'B', 'B'],  # back 5
                     ['B', 'B', 'B'], ['B', 'B', 'B']]

                    ]
        self.show = False
        self.solvelist = []
        self.movelist = []
        # cube[face][row][column]
        self.completed_cube = [[['W', 'W', 'W'],  # upper 0
                                ['W', 'W', 'W'], ['W', 'W', 'W']],

                               [['G', 'G', 'G'],  # front 1
                                ['G', 'G', 'G'], ['G', 'G', 'G']],

                               [['R', 'R', 'R'],  # right 2
                                ['R', 'R', 'R'], ['R', 'R', 'R']],

                               [['O', 'O', 'O'],  # left 3
                                ['O', 'O', 'O'], ['O', 'O', 'O']],

                               [['Y', 'Y', 'Y'],  # down 4
                                ['Y', 'Y', 'Y'], ['Y', 'Y', 'Y']],

                               [['B', 'B', 'B'],  # back 5
                                ['B', 'B', 'B'], ['B', 'B', 'B']]

                               ]
        self.cube = cube
        self.d = 'Y'
        self.u = 'W'
        self.f = 'G'
        self.b = 'B'
        self.r = 'R'
        self.l = 'O'

        self.uf = {'u': self.cube[0][2][1], 'd': '', 'f': self.cube[1][0][1], 'b': '', 'r': '', 'l': ''}
        self.ur = {'u': self.cube[0][1][2], 'd': '', 'f': '', 'b': '', 'r': self.cube[2][0][1], 'l': ''}
        self.ub = {'u': self.cube[0][0][1], 'd': '', 'f': '', 'b': self.cube[5][0][1], 'r': '', 'l': ''}
        self.ul = {'u': self.cube[0][1][0], 'd': '', 'f': '', 'b': '', 'r': '', 'l': self.cube[3][0][1]}
        self.df = {'u': '', 'd': self.cube[4][0][1], 'f': self.cube[1][2][1], 'b': '', 'r': '', 'l': ''}
        self.dr = {'u': '', 'd': self.cube[4][1][2], 'f': '', 'b': '', 'r': self.cube[2][2][1], 'l': ''}
        self.db = {'u': '', 'd': self.cube[4][2][1], 'f': '', 'b': self.cube[5][2][1], 'r': '', 'l': ''}
        self.dl = {'u': '', 'd': self.cube[4][1][0], 'f': '', 'b': '', 'r': '', 'l': self.cube[3][2][1]}
        self.fr = {'u': '', 'd': '', 'f': self.cube[1][1][2], 'b': '', 'r': self.cube[2][1][0], 'l': ''}
        self.fl = {'u': '', 'd': '', 'f': self.cube[1][1][0], 'b': '', 'r': '', 'l': self.cube[3][1][2]}
        self.br = {'u': '', 'd': '', 'f': '', 'b': self.cube[5][1][0], 'r': self.cube[2][1][2], 'l': ''}
        self.bl = {'u': '', 'd': '', 'f': '', 'b': self.cube[5][1][2], 'r': '', 'l': self.cube[3][1][0]}

        self.ufr = {'u': self.cube[0][2][2], 'd': '', 'f': self.cube[1][0][2], 'b': '', 'r': self.cube[2][0][0],
                    'l': ''}
        self.ufl = {'u': self.cube[0][2][0], 'd': '', 'f': self.cube[1][0][0], 'b': '', 'r': '',
                    'l': self.cube[3][0][2]}
        self.ubr = {'u': self.cube[0][0][2], 'd': '', 'f': '', 'b': self.cube[5][0][0], 'r': self.cube[2][0][2],
                    'l': ''}
        self.ubl = {'u': self.cube[0][0][0], 'd': '', 'f': '', 'b': self.cube[5][0][2], 'r': '',
                    'l': self.cube[3][0][0]}
        self.dfr = {'u': '', 'd': self.cube[4][0][2], 'f': self.cube[1][2][2], 'b': '', 'r': self.cube[2][2][0],
                    'l': ''}
        self.dfl = {'u': '', 'd': self.cube[4][0][0], 'f': self.cube[1][2][0], 'b': '', 'r': '',
                    'l': self.cube[3][2][2]}
        self.dbr = {'u': '', 'd': self.cube[4][2][2], 'f': '', 'b': self.cube[5][2][0], 'r': self.cube[2][2][2],
                    'l': ''}
        self.dbl = {'u': '', 'd': self.cube[4][2][0], 'f': '', 'b': self.cube[5][2][2], 'r': '',
                    'l': self.cube[3][2][0]}

        self.movedict = {"U": self.U(), "Ui": self.Ui(), "D": self.D(), "Di": self.Di(), "R": self.R(), "Ri": self.Ri(),
                         "L": self.L(), "Li": self.Li(), "F": self.F(), "Fi": self.Fi(), "B": self.B(), "Bi": self.Bi()}

    # updates cubies
    def update_cubies(self):
        self.uf = {'u': self.cube[0][2][1], 'd': '', 'f': self.cube[1][0][1], 'b': '', 'r': '', 'l': ''}
        self.ur = {'u': self.cube[0][1][2], 'd': '', 'f': '', 'b': '', 'r': self.cube[2][0][1], 'l': ''}
        self.ub = {'u': self.cube[0][0][1], 'd': '', 'f': '', 'b': self.cube[5][0][1], 'r': '', 'l': ''}
        self.ul = {'u': self.cube[0][1][0], 'd': '', 'f': '', 'b': '', 'r': '', 'l': self.cube[3][0][1]}
        self.df = {'u': '', 'd': self.cube[4][0][1], 'f': self.cube[1][2][1], 'b': '', 'r': '', 'l': ''}
        self.dr = {'u': '', 'd': self.cube[4][1][2], 'f': '', 'b': '', 'r': self.cube[2][2][1], 'l': ''}
        self.db = {'u': '', 'd': self.cube[4][2][1], 'f': '', 'b': self.cube[5][2][1], 'r': '', 'l': ''}
        self.dl = {'u': '', 'd': self.cube[4][1][0], 'f': '', 'b': '', 'r': '', 'l': self.cube[3][2][1]}
        self.fr = {'u': '', 'd': '', 'f': self.cube[1][1][2], 'b': '', 'r': self.cube[2][1][0], 'l': ''}
        self.fl = {'u': '', 'd': '', 'f': self.cube[1][1][0], 'b': '', 'r': '', 'l': self.cube[3][1][2]}
        self.br = {'u': '', 'd': '', 'f': '', 'b': self.cube[5][1][0], 'r': self.cube[2][1][2], 'l': ''}
        self.bl = {'u': '', 'd': '', 'f': '', 'b': self.cube[5][1][2], 'r': '', 'l': self.cube[3][1][0]}

        self.ufr = {'u': self.cube[0][2][2], 'd': '', 'f': self.cube[1][0][2], 'b': '', 'r': self.cube[2][0][0],
                    'l': ''}
        self.ufl = {'u': self.cube[0][2][0], 'd': '', 'f': self.cube[1][0][0], 'b': '', 'r': '',
                    'l': self.cube[3][0][2]}
        self.ubr = {'u': self.cube[0][0][2], 'd': '', 'f': '', 'b': self.cube[5][0][0], 'r': self.cube[2][0][2],
                    'l': ''}
        self.ubl = {'u': self.cube[0][0][0], 'd': '', 'f': '', 'b': self.cube[5][0][2], 'r': '',
                    'l': self.cube[3][0][0]}
        self.dfr = {'u': '', 'd': self.cube[4][0][2], 'f': self.cube[1][2][2], 'b': '', 'r': self.cube[2][2][0],
                    'l': ''}
        self.dfl = {'u': '', 'd': self.cube[4][0][0], 'f': self.cube[1][2][0], 'b': '', 'r': '',
                    'l': self.cube[3][2][2]}
        self.dbr = {'u': '', 'd': self.cube[4][2][2], 'f': '', 'b': self.cube[5][2][0], 'r': self.cube[2][2][2],
                    'l': ''}
        self.dbl = {'u': '', 'd': self.cube[4][2][0], 'f': '', 'b': self.cube[5][2][2], 'r': '',
                    'l': self.cube[3][2][0]}

    def scramble(self):
        for _ in range(20):
            self.convertmoves(random.choice(list(self.movedict.keys())))

    # displays cube in nice format
    def printCube(self):
        self.update_cubies()
        print("\n\t" + self.ubl['u'] + self.ub['u'] + self.ubr['u'] + "\n\t" + self.ul['u'] + self.u + self.ur[
            'u'] + "\n\t" + self.ufl['u'] + self.uf['u'] + self.ufr['u'] + "\n" + \
 \
              self.ubl['l'] + self.ul['l'] + self.ufl['l'] + " " + self.ufl['f'] + self.uf['f'] + self.ufr['f'] + " " +
              self.ufr['r'] + self.ur['r'] + self.ubr['r'] + " " + self.ubr['b'] + self.ub['b'] + self.ubl['b'] + "\n" + \
              self.bl['l'] + self.l + self.fl['l'] + " " + self.fl['f'] + self.f + self.fr['f'] + " " + self.fr[
                  'r'] + self.r + self.br['r'] + " " + self.br['b'] + self.b + self.bl['b'] + " " + "\n" + self.dbl[
                  'l'] + self.dl['l'] + self.dfl['l'] + " " + self.dfl['f'] + self.df['f'] + self.dfr['f'] + " " +
              self.dfr['r'] + self.dr['r'] + self.dbr['r'] + " " + self.dbr['b'] + self.db['b'] + self.dbl[
                  'b'] + "\n\t" + \
 \
              self.dfl['d'] + self.df['d'] + self.dfr['d'] + "\n\t" + self.dl['d'] + self.d + self.dr['d'] + "\n\t" +
              self.dbl['d'] + self.db['d'] + self.dbr['d'] + "\n")

        print("=====================================")

    # displays cube in nice format
    def display_cube(self):
        for i in self.cube:
            print()
            for j in i:
                print(j)
        print("=====================================")

    # runs through sequence
    def runthrough(self, sequence):
        self.cube = copy.deepcopy(self.completed_cube)
        for move in sequence:
            self.convertmoves(move)

    # Finds put the rotation of each cubie in a list
    def cube_to_rotations(self):
        rotations = []
        order_list = ["dfl", "dl", "dbl", "fl", "l", "bl", "ufl", "ul", "ubl", "df", "d", "db", "f", "center", "b",
                      "uf", "u", "ub", "dfr", "dr", "dbr", "fr", "r", "br", "ufr", "ur", "ubr"]
        possible_dicts = [# (X,Y,Z)
            # (R,U,F)
            # W TOP
            ({'u': 'W', 'd': 'Y', 'f': 'G', 'b': 'B', 'r': 'R', 'l': 'O'}, (0, 0, 0)),
            ({'u': 'W', 'd': 'Y', 'f': 'R', 'b': 'O', 'r': 'B', 'l': 'G'}, (0, 90, 0)),
            ({'u': 'W', 'd': 'Y', 'f': 'B', 'b': 'G', 'r': 'O', 'l': 'R'}, (0, 180, 0)),
            ({'u': 'W', 'd': 'Y', 'f': 'O', 'b': 'R', 'r': 'G', 'l': 'B'}, (0, -90, 0)), # Y TOP
            ({'u': 'Y', 'd': 'W', 'f': 'G', 'b': 'B', 'r': 'O', 'l': 'R'}, (0, 0, 180)),
            ({'u': 'Y', 'd': 'W', 'f': 'O', 'b': 'R', 'r': 'B', 'l': 'G'}, (0, 90, 180)),
            ({'u': 'Y', 'd': 'W', 'f': 'B', 'b': 'G', 'r': 'R', 'l': 'O'}, (0, 180, 180)),
            ({'u': 'Y', 'd': 'W', 'f': 'R', 'b': 'O', 'r': 'G', 'l': 'B'}, (0, -90, 180)), # R TOP
            ({'u': 'R', 'd': 'O', 'f': 'G', 'b': 'B', 'r': 'Y', 'l': 'W'}, (0, 0, -90)),
            ({'u': 'R', 'd': 'O', 'f': 'Y', 'b': 'W', 'r': 'B', 'l': 'G'}, (0, 90, -90)),
            ({'u': 'R', 'd': 'O', 'f': 'B', 'b': 'G', 'r': 'W', 'l': 'Y'}, (0, 180, -90)),
            ({'u': 'R', 'd': 'O', 'f': 'W', 'b': 'Y', 'r': 'G', 'l': 'B'}, (0, -90, -90)), # O TOP
            ({'u': 'O', 'd': 'R', 'f': 'G', 'b': 'B', 'r': 'W', 'l': 'Y'}, (0, 0, 90)),
            ({'u': 'O', 'd': 'R', 'f': 'W', 'b': 'Y', 'r': 'B', 'l': 'G'}, (0, 90, 90)),
            ({'u': 'O', 'd': 'R', 'f': 'B', 'b': 'G', 'r': 'Y', 'l': 'W'}, (0, 180, 90)),
            ({'u': 'O', 'd': 'R', 'f': 'Y', 'b': 'W', 'r': 'G', 'l': 'B'}, (0, -90, 90)), # G TOP
            ({'u': 'G', 'd': 'B', 'f': 'Y', 'b': 'W', 'r': 'R', 'l': 'O'}, (90, 0, 0)),
            ({'u': 'G', 'd': 'B', 'f': 'R', 'b': 'O', 'r': 'W', 'l': 'Y'}, (90, 0, 90)),
            ({'u': 'G', 'd': 'B', 'f': 'W', 'b': 'Y', 'r': 'O', 'l': 'R'}, (90, 0, 180)),
            ({'u': 'G', 'd': 'B', 'f': 'O', 'b': 'R', 'r': 'Y', 'l': 'W'}, (90, 0, -90)), # B TOP
            ({'u': 'B', 'd': 'G', 'f': 'W', 'b': 'Y', 'r': 'R', 'l': 'O'}, (-90, 0, 0)),
            ({'u': 'B', 'd': 'G', 'f': 'R', 'b': 'O', 'r': 'Y', 'l': 'W'}, (-90, 0, -90)),
            ({'u': 'B', 'd': 'G', 'f': 'Y', 'b': 'W', 'r': 'O', 'l': 'R'}, (-90, 0, 180)),
            ({'u': 'B', 'd': 'G', 'f': 'O', 'b': 'R', 'r': 'W', 'l': 'Y'}, (-90, 0, 90))]

        self.update_cubies()
        for cubie in order_list:
            for key, rot in possible_dicts:
                if len(cubie) == 3:
                    # if cube is a corner and matches this case, append the rotation value
                    if eval(f"self.{cubie}['{cubie[0]}'] == {key}['{cubie[0]}'] and "
                            f"self.{cubie}['{cubie[1]}'] == {key}['{cubie[1]}'] and "
                            f"self.{cubie}['{cubie[2]}'] == {key}['{cubie[2]}']"):
                        rotations.append(rot)

                elif len(cubie) == 2:
                    # if cube is an edge and matches this case, append the rotation value
                    if eval(f"self.{cubie}['{cubie[0]}'] == {key}['{cubie[0]}'] and "
                            f"self.{cubie}['{cubie[1]}'] == {key}['{cubie[1]}']"):
                        rotations.append(rot)
                elif len(cubie) == 1 or cubie == "center":
                    rotations.append((0, 0, 0))
                    break
        # self.printCube()
        # self.display_cube()

        rotations.reverse()
        return rotations

    # Given a string, performs calls the rotation function
    def convertmoves(self, move):
        self.movelist.append(move)

        if self.show:  # if we are just creating a solve sequence without change ing the actual cube, we use this to append the move to a list without changeing anythong real
            self.solvelist.append(move)  # return
        if move == "Y":
            self.Y()
        elif move == "Yi":
            self.Yi()
        elif move == "Z2":
            self.Z2()
        elif move == "U2":
            self.U2()
        elif move == "D2":
            self.D2()
        elif move == "R2":
            self.R2()
        elif move == "L2":
            self.L2()
        elif move == "F2":
            self.F2()
        elif move == "B2":
            self.B2()
        elif move == "U":
            self.U()
        elif move == "Ui":
            self.Ui()
        elif move == "D":
            self.D()
        elif move == "Di":
            self.Di()
        elif move == "R":
            self.R()
        elif move == "Ri":
            self.Ri()
        elif move == "L":
            self.L()
        elif move == "Li":
            self.Li()  #
        elif move == "F":
            self.F()
        elif move == "Fi":
            self.Fi()
        elif move == "B":
            self.B()
        elif move == "Bi":
            self.Bi()
        else:
            pass
        self.update_cubies()

        if move in ["Y", "Yi"]:
            try:
                self.solvelist[-1] = self.solvelist[-1] + self.f
            except IndexError:
                pass

    def rotate(self, side, clockwise=True):
        face = self.cube[side]

        if not clockwise:
            face[0][0], face[0][1], face[0][2], face[1][0], face[1][2], face[2][0], face[2][1], face[2][2] = face[0][2], \
                                                                                                             face[1][2], \
                                                                                                             face[2][2], \
                                                                                                             face[0][1], \
                                                                                                             face[2][1], \
                                                                                                             face[0][0], \
                                                                                                             face[1][0], \
                                                                                                             face[2][0]

            self.cube[0][0][0], self.cube[0][0][1], self.cube[0][0][2], self.cube[0][1][0], self.cube[0][1][2], \
            self.cube[0][2][0], self.cube[0][2][1], self.cube[0][2][2] = self.cube[0][0][2], self.cube[0][1][2], \
                                                                         self.cube[0][2][2], self.cube[0][0][1], \
                                                                         self.cube[0][2][1], self.cube[0][0][0], \
                                                                         self.cube[0][1][0], self.cube[0][2][0]


        else:
            face[0][2], face[1][2], face[2][2], face[0][1], face[2][1], face[0][0], face[1][0], face[2][0] = face[0][0], \
                                                                                                             face[0][1], \
                                                                                                             face[0][2], \
                                                                                                             face[1][0], \
                                                                                                             face[1][2], \
                                                                                                             face[2][0], \
                                                                                                             face[2][1], \
                                                                                                             face[2][2]

    def U(self):
        temp = copy.deepcopy(self.cube)
        self.rotate(0, True)
        self.cube[1][0], self.cube[2][0], self.cube[5][0], self.cube[3][0] = temp[2][0], temp[5][0], temp[3][0], \
                                                                             temp[1][0]

    def Ui(self):
        temp = copy.deepcopy(self.cube)
        self.rotate(0, False)
        self.cube[2][0], self.cube[5][0], self.cube[3][0], self.cube[1][0] = temp[1][0], temp[2][0], temp[5][0], \
                                                                             temp[3][0]

    def D(self):
        temp = copy.deepcopy(self.cube)
        self.cube[1][2], self.cube[2][2], self.cube[5][2], self.cube[3][2] = temp[3][2], temp[1][2], temp[2][2], \
                                                                             temp[5][2]
        self.rotate(4)

    def Di(self):
        temp = copy.deepcopy(self.cube)
        self.cube[3][2], self.cube[1][2], self.cube[2][2], self.cube[5][2] = temp[1][2], temp[2][2], temp[5][2], \
                                                                             temp[3][2]
        self.rotate(4, False)

    def R(self):
        temp = copy.deepcopy(self.cube)
        self.rotate(2, True)
        self.cube[0][0][2], self.cube[0][1][2], self.cube[0][2][2] = temp[1][0][2], temp[1][1][2], temp[1][2][2]
        self.cube[1][0][2], self.cube[1][1][2], self.cube[1][2][2] = temp[4][0][2], temp[4][1][2], temp[4][2][2]
        self.cube[4][0][2], self.cube[4][1][2], self.cube[4][2][2] = temp[5][2][0], temp[5][1][0], temp[5][0][0]
        self.cube[5][0][0], self.cube[5][1][0], self.cube[5][2][0] = temp[0][2][2], temp[0][1][2], temp[0][0][2]

    def Ri(self):
        temp = copy.deepcopy(self.cube)
        self.cube[1][0][2], self.cube[1][1][2], self.cube[1][2][2] = temp[0][0][2], temp[0][1][2], temp[0][2][2]
        self.cube[4][0][2], self.cube[4][1][2], self.cube[4][2][2] = temp[1][0][2], temp[1][1][2], temp[1][2][2]
        self.cube[5][2][0], self.cube[5][1][0], self.cube[5][0][0] = temp[4][0][2], temp[4][1][2], temp[4][2][2]
        self.cube[0][2][2], self.cube[0][1][2], self.cube[0][0][2] = temp[5][0][0], temp[5][1][0], temp[5][2][0]

        self.rotate(2, False)

    def L(self):
        temp = copy.deepcopy(self.cube)
        self.rotate(3)
        self.cube[1][0][0], self.cube[1][1][0], self.cube[1][2][0] = temp[0][0][0], temp[0][1][0], temp[0][2][0]
        self.cube[4][0][0], self.cube[4][1][0], self.cube[4][2][0] = temp[1][0][0], temp[1][1][0], temp[1][2][0]
        self.cube[5][0][2], self.cube[5][1][2], self.cube[5][2][2] = temp[4][2][0], temp[4][1][0], temp[4][0][0]
        self.cube[0][0][0], self.cube[0][1][0], self.cube[0][2][0] = temp[5][2][2], temp[5][1][2], temp[5][0][2]

    def Li(self):
        temp = copy.deepcopy(self.cube)
        self.cube[0][0][0], self.cube[0][1][0], self.cube[0][2][0] = temp[1][0][0], temp[1][1][0], temp[1][2][0]
        self.cube[1][0][0], self.cube[1][1][0], self.cube[1][2][0] = temp[4][0][0], temp[4][1][0], temp[4][2][0]
        self.cube[4][2][0], self.cube[4][1][0], self.cube[4][0][0] = temp[5][0][2], temp[5][1][2], temp[5][2][2]
        self.cube[5][2][2], self.cube[5][1][2], self.cube[5][0][2] = temp[0][0][0], temp[0][1][0], temp[0][2][0]

        self.rotate(3, False)

    def F(self):
        temp = copy.deepcopy(self.cube)
        self.cube[3][0][2], self.cube[3][1][2], self.cube[3][2][2] = temp[4][0]
        self.cube[0][2] = [temp[3][2][2], temp[3][1][2], temp[3][0][2]]
        self.cube[2][0][0], self.cube[2][1][0], self.cube[2][2][0] = temp[0][2]
        self.cube[4][0] = [temp[2][2][0], temp[2][1][0], temp[2][0][0]]

        self.rotate(1, True)

    def Fi(self):
        temp = copy.deepcopy(self.cube)
        self.cube[4][0] = [temp[3][0][2], temp[3][1][2], temp[3][2][2]]
        self.cube[3][2][2], self.cube[3][1][2], self.cube[3][0][2] = temp[0][2]
        self.cube[0][2] = [temp[2][0][0], temp[2][1][0], temp[2][2][0]]
        self.cube[2][2][0], self.cube[2][1][0], self.cube[2][0][0] = temp[4][0]

        self.rotate(1, False)

    def B(self):
        temp = copy.deepcopy(self.cube)
        self.cube[2][2][2], self.cube[2][1][2], self.cube[2][0][2] = temp[4][2]
        self.cube[0][0] = [temp[2][0][2], temp[2][1][2], temp[2][2][2]]
        self.cube[3][2][0], self.cube[3][1][0], self.cube[3][0][0] = temp[0][0]
        self.cube[4][2] = [temp[3][0][0], temp[3][1][0], temp[3][2][0]]

        self.rotate(5, True)

    def Bi(self):
        temp = copy.deepcopy(self.cube)
        self.cube[4][2] = [temp[2][2][2], temp[2][1][2], temp[2][0][2]]
        self.cube[2][0][2], self.cube[2][1][2], self.cube[2][2][2] = temp[0][0]
        self.cube[0][0] = [temp[3][2][0], temp[3][1][0], temp[3][0][0]]
        self.cube[3][0][0], self.cube[3][1][0], self.cube[3][2][0] = temp[4][2]

        self.rotate(5, False)

    def U2(self):
        self.U()
        self.U()

    def D2(self):
        self.D()
        self.D()

    def R2(self):
        self.R()
        self.R()

    def L2(self):
        self.L()
        self.L()

    def F2(self):
        self.F()
        self.F()

    def B2(self):
        self.B()
        self.B()

    def Y(self):
        self.cube[1], self.cube[2], self.cube[5], self.cube[3] = self.cube[2], self.cube[5], self.cube[3], self.cube[1]
        self.rotate(0)
        self.rotate(4, False)
        self.f, self.r, self.b, self.l = self.r, self.b, self.l, self.f

    def Yi(self):
        self.cube[2], self.cube[5], self.cube[3], self.cube[1] = self.cube[1], self.cube[2], self.cube[5], self.cube[3]
        self.rotate(0, False)
        self.rotate(4)
        self.r, self.b, self.l, self.f = self.f, self.r, self.b, self.l

    def Z2(self):
        self.cube[0], self.cube[4], self.cube[2], self.cube[3] = self.cube[4], self.cube[0], self.cube[3], self.cube[2]
        self.u, self.d, self.r, self.l = self.d, self.u, self.l, self.r
        self.update_cubies()
        for i in range(len(self.cube)):
            self.rotate(i)
            self.rotate(i)


# CUBE SOLVER
########################################################################################################################

class Solver(handler):
    def __init__(self, cube=handler().completed_cube):
        handler.__init__(self, cube=cube)
        self.srt = lambda piece: sorted(''.join(list(piece.values())))

    # returns whether the the top layer and the middle cubie match color, and whether the top face has a cross on it
    def cross(self, yface):  # yface is face on the y axis, color, so white or yellow
        cross = True
        matched = True
        for face in ["b", "r", "f", "l"]:
            if not eval(f"self.d{face}['{face}'] == self.{face}"):
                matched = False
            if not eval(f"self.d{face}['d'] == '{yface}'"):
                cross = False
        return cross, matched

    # checks the current stage of completion the cube is solved to
    def check_state(self):

        if self.cube == self.completed_cube:
            return ["Solved", "Solved"]

        f2l = True  # first 2 layers
        f1l = True  # first 1  layer
        if not self.cube[0] == self.completed_cube[0]:  # if top face isnt complete, f2l and f1l cannot be true
            f2l = False
            f1l = False
        for row in [0, 1]:
            for face in [1, 2, 3, 5]:
                if not (self.cube[face][row] == self.completed_cube[face][row]):  # row is not solved
                    f2l = False
                    if row == 0:  # if the first row is not solved
                        f1l = False

        cross, matched = self.cross("Y")

        self.convertmoves("Z2")  # turns upside down then back to normal so that we can use the check done function
        cd = self.checkdone()  # true if all corners are in correct position
        self.convertmoves("Z2")
        if matched and cross and f2l and cd:
            return ["Yellow corners Positioned", "orient Yellow Corners"]
        if matched and cross and f2l:
            return ["Yellow edges matched", "position Yellow Corners"]

        if cross and f2l:
            return ["Yellow cross completed", "match Yellow Edges"]

        if f2l:
            return ["Second layer completed", "solve Yellow Cross"]
        self.convertmoves("Z2")  # flip to check for white cross
        cross, matched = self.cross("W")
        self.convertmoves("Z2")
        # print(cross)
        if cross and f1l:
            return ["White corners solved", "solve Second Layer"]

        if cross and matched:
            return ["White cross solved", "solve White Corners"]
        else:
            return ["Cube not at any stage", "solve White Cross"]

        # if self.cube[0] == self.completed_cube[0] and

    # functions solve step of the cube
    def solveWhiteCross(self):
        self.update_cubies()
        sides = ['G', 'R', 'B', 'O']
        for side in sides:
            if self.dr['d'] == 'W' and self.dr['r'] == side:
                self.convertmoves("R")
                self.convertmoves("R")
                self.convertmoves("U")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.db['d'] == 'W' and self.db['b'] == side:
                self.convertmoves("B")
                self.convertmoves("B")
                self.convertmoves("U")
                self.convertmoves("U")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.dl['d'] == 'W' and self.dl['l'] == side:
                self.convertmoves("L")
                self.convertmoves("L")
                self.convertmoves("Ui")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.fr['f'] == 'W' and self.fr['r'] == side:
                self.convertmoves("R")
                self.convertmoves("U")
                self.convertmoves("Ri")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.fl['f'] == 'W' and self.fl['l'] == side:
                self.convertmoves("Li")
                self.convertmoves("Ui")
                self.convertmoves("L")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.br['b'] == 'W' and self.br['r'] == side:
                self.convertmoves("Ri")
                self.convertmoves("U")
                self.convertmoves("R")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.bl['b'] == 'W' and self.bl['l'] == side:
                self.convertmoves("L")
                self.convertmoves("Ui")
                self.convertmoves("Li")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.uf['u'] == 'W' and self.uf['f'] == side:
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.ur['u'] == 'W' and self.ur['r'] == side:
                self.convertmoves("U")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.ul['u'] == 'W' and self.ul['l'] == side:
                self.convertmoves("Ui")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.ub['u'] == 'W' and self.ub['b'] == side:
                self.convertmoves("U")
                self.convertmoves("U")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.dr['d'] == side and self.dr['r'] == 'W':
                self.convertmoves("R")
                self.convertmoves("F")

            elif self.db['d'] == side and self.db['b'] == 'W':
                self.convertmoves("B")
                self.convertmoves("D")
                self.convertmoves("R")
                self.convertmoves("Di")

            elif self.dl['d'] == side and self.dl['l'] == 'W':
                self.convertmoves("Li")
                self.convertmoves("Fi")

            elif self.fr['f'] == side and self.fr['r'] == 'W':
                self.convertmoves("F")

            elif self.fl['f'] == side and self.fl['l'] == 'W':
                self.convertmoves("Fi")

            elif self.br['b'] == side and self.br['r'] == 'W':
                self.convertmoves("B")
                self.convertmoves("U")
                self.convertmoves("U")
                self.convertmoves("Bi")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.bl['b'] == side and self.bl['l'] == 'W':
                self.convertmoves("Bi")
                self.convertmoves("U")
                self.convertmoves("U")
                self.convertmoves("B")
                self.convertmoves("F")
                self.convertmoves("F")

            elif self.uf['u'] == side and self.uf['f'] == 'W':
                self.convertmoves("Ui")
                self.convertmoves("Ri")
                self.convertmoves("F")
                self.convertmoves("R")

            elif self.ur['u'] == side and self.ur['r'] == 'W':
                self.convertmoves("Ri")
                self.convertmoves("F")
                self.convertmoves("R")

            elif self.ul['u'] == side and self.ul['l'] == 'W':
                self.convertmoves("L")
                self.convertmoves("Fi")
                self.convertmoves("Li")

            elif self.ub['u'] == side and self.ub['b'] == 'W':
                self.convertmoves("U")
                self.convertmoves("Ri")
                self.convertmoves("F")
                self.convertmoves("R")

            elif self.df['d'] == side and self.df['f'] == 'W':
                self.convertmoves("Fi")
                self.convertmoves("D")
                self.convertmoves("Ri")
                self.convertmoves("Di")

            self.convertmoves("Y")

        self.convertmoves("F2")
        self.convertmoves("R2")
        self.convertmoves("B2")
        self.convertmoves("L2")

    def solveWhiteCorners(self):
        self.update_cubies()
        white_corners = ["WGR", "WRB", "WBO", "WOG"]
        for corner in white_corners:
            # Moves corner to
            if self.ufl['u'] in corner and self.ufl['f'] in corner and self.ufl['l'] in corner:
                self.convertmoves("L")
                self.convertmoves("D")
                self.convertmoves("Li")
            elif self.ubl['u'] in corner and self.ubl['b'] in corner and self.ubl['l'] in corner:
                self.convertmoves("Li")
                self.convertmoves("D2")
                self.convertmoves("L")
            elif self.ubr['u'] in corner and self.ubr['b'] in corner and self.ubr['r'] in corner:
                self.convertmoves("Bi")
                self.convertmoves("Di")
                self.convertmoves("B")

            elif self.dfl['d'] in corner and self.dfl['f'] in corner and self.dfl['l'] in corner:
                self.convertmoves("D")

            elif self.dbl['d'] in corner and self.dbl['b'] in corner and self.dbl['l'] in corner:
                self.convertmoves("D2")

            elif self.dbr['d'] in corner and self.dbr['b'] in corner and self.dbr['r'] in corner:
                self.convertmoves("Di")

            # corners are now in ufr or dfr positions, time to orient/move them

            if self.dfr['r'] == 'W' and self.dfr['d'] in corner and self.dfr['f'] in corner:
                self.convertmoves("D")
                self.convertmoves("F")
                self.convertmoves("Di")
                self.convertmoves("Fi")

            if self.dfr['f'] == 'W' and self.dfr['d'] in corner and self.dfr['r'] in corner:
                self.convertmoves("Di")
                self.convertmoves("Ri")
                self.convertmoves("D")
                self.convertmoves("R")

            if self.dfr['d'] == 'W' and self.dfr['f'] in corner and self.dfr['r'] in corner:
                self.convertmoves("F")
                self.convertmoves("L")
                self.convertmoves("D2")
                self.convertmoves("Li")
                self.convertmoves("Fi")

            if self.ufr['u'] == 'W' and self.ufr['f'] in corner and self.ufr['r'] in corner:
                pass  # do nothing (:

            if self.ufr['f'] == 'W' and self.ufr['u'] in corner and self.ufr['r'] in corner:
                self.convertmoves("Ri")
                self.convertmoves("Di")
                self.convertmoves("R")
                self.convertmoves("D")
                # now in dfr w at bottom position
                self.convertmoves("F")
                self.convertmoves("L")
                self.convertmoves("D2")
                self.convertmoves("Li")
                self.convertmoves("Fi")

            if self.ufr['r'] == 'W' and self.ufr['u'] in corner and self.ufr['f'] in corner:
                self.convertmoves("Ri")
                self.convertmoves("Di")
                self.convertmoves("R")
                self.convertmoves("D")
                # now in dfr w at right position
                self.convertmoves("D")
                self.convertmoves("F")
                self.convertmoves("Di")
                self.convertmoves("Fi")

            self.convertmoves("Y")

    def solveSecondLayer(self):
        self.update_cubies()
        if self.u == "W":
            self.convertmoves("Z2")  # to see the edges easier, we turn the cube upside down
        edges = ["GO", "OB", "BR", "RG"]
        right_alg = ["U", "R", "Ui", "Ri", "Ui", "Fi", "U", "F"]
        left_alg = ["Ui", "Li", "U", "L", "U", "F", "Ui", "Fi"]

        for edge in edges:
            # if edge is in middle, move it to the top
            if self.fl['f'] in edge and self.fl['l'] in edge:
                while "Y" not in self.uf.values():  # this ensures we are not putting a piece we will need back into the second layer, this saves time
                    self.convertmoves("U")

                for move in left_alg:
                    self.convertmoves(move)

            elif self.bl['b'] in edge and self.bl['l'] in edge:
                self.convertmoves("Yi")
                while "Y" not in self.uf.values():  # this ensures we are not putting a piece we will need back into the second layer, this saves time
                    self.convertmoves("U")

                for move in left_alg:  # takes piece out of place
                    self.convertmoves(move)
                self.convertmoves("Y")  # moves cube back to uf position

            elif self.br['b'] in edge and self.br['r'] in edge:
                self.convertmoves("Y")
                while "Y" not in self.uf.values():  # ensures we're not putting a piece we will need back into the second layer:saves time
                    self.convertmoves("U")
                for move in right_alg:
                    self.convertmoves(move)
                self.convertmoves("Yi")
            # now edge is on top, move it to the front
            if self.ub['u'] in edge and self.ub['b'] in edge:
                self.convertmoves("U2")
            elif self.ur['u'] in edge and self.ur['r'] in edge:
                self.convertmoves("U")
            elif self.ul['u'] in edge and self.ul['l'] in edge:
                self.convertmoves("Ui")

            # if the front of the edge is lined up with the center, perform the algorithm to move it into the right side
            if self.uf['f'] == edge[0] and self.uf['u'] == edge[1]:
                for move in right_alg:
                    self.convertmoves(move)
            # if the front of the edge is NOT lined up with the center,
            # turn the cube and perform algorithm to move it into the left side
            elif self.uf['f'] == edge[1] and self.uf['u'] == edge[0]:
                self.convertmoves("Y")
                self.convertmoves("Ui")
                for move in left_alg:
                    self.convertmoves(move)
                self.convertmoves("Yi")
            if self.fr['f'] != edge[0]:
                while "Y" not in self.uf.values():  # ensures we're not putting a piece we will need back into the second layer:saves time
                    self.convertmoves("U")
                for move in right_alg:
                    self.convertmoves(move)
                self.convertmoves("U2")
                for move in right_alg:
                    self.convertmoves(move)
            if self.fr['f'] == edge[0]:
                pass  # goal reached

            self.convertmoves("Y")

    def solveYellowCross(self):
        if self.u == "W":
            self.convertmoves("Z2")
        self.update_cubies()
        cross_completed = False
        cross_alg = ["F", "R", "U", "Ri", "Ui", "Fi"]
        while not cross_completed:
            # cross completed
            if ((self.ub['u'] == "Y") and (self.ur['u'] == "Y")) and ((self.uf['u'] == "Y") and (self.ul['u'] == "Y")):
                cross_completed = True

            # line - if horizontal line xor vertical line
            elif ((self.ub['u'] == "Y") and (self.uf['u'] == "Y")) ^ ((self.ur['u'] == "Y") and (self.ul['u'] == "Y")):
                if self.ub['u'] == "Y" and self.uf['u'] == "Y":  # if horizontal line, make into vertical line
                    self.convertmoves("U")
                for move in cross_alg:  # perform move on vertical line
                    self.convertmoves(move)

            # dot - if other edges are not yellow
            elif ((self.ub['u'] != "Y") and (self.ur['u'] != "Y")) and (
                    (self.uf['u'] != "Y") and (self.ul['u'] != "Y")):  #
                for move in cross_alg:
                    self.convertmoves(move)
            # L - the last possible case is the L shape
            else:
                while not (self.ub['u'] == "Y" and self.ul['u'] == "Y"):
                    self.convertmoves("U")
                for move in cross_alg:
                    self.convertmoves(move)

    def matchYellowEdges(self):
        if self.u == "W":
            self.convertmoves("Z2")
        self.update_cubies()

        fav_alg = ["R", "U", "Ri", "U", "R", "U2", "Ri", "U"]
        matches = []
        d = False
        # while there are less than two matches, rotate until there are two matches
        while len(matches) < 2:
            if self.ub['b'] == self.b:
                matches.append("ub")
            if self.ur['r'] == self.r:
                matches.append("ur")
            if self.uf['f'] == self.f:
                matches.append("uf")
            if self.ul['l'] == self.l:
                matches.append("ul")
            if len(matches) < 2:
                self.convertmoves("U")
                matches = []

        # all sides are matched
        if len(matches) == 4:
            return
        # 2 sides are opposite

        elif ("ub" in matches and "uf" in matches) or ("ul" in matches and "ur" in matches):
            if "ub" not in matches:
                self.convertmoves("U")
                d = True
            for move in fav_alg:
                self.convertmoves(move)
            if d:  # this just corrects for the U move we did a few lines ago
                self.convertmoves("Ui")
            # match sides again
            new_matches = []


        # if sides are next to each other

        elif len(matches) == 2:
            while not (self.ub['b'] == self.b and self.ur['r'] == self.r):
                self.convertmoves("Y")
            for move in fav_alg:
                self.convertmoves(move)

    def checkdone(self):  # checks if all pieces are in the right position
        match = []
        if self.srt(self.ufr) == sorted([self.u, self.f, self.r]):
            match.append(self.ufr)
        if self.srt(self.ubr) == sorted([self.u, self.b, self.r]):
            match.append(self.ubr)
        if self.srt(self.ubl) == sorted([self.u, self.b, self.l]):
            match.append(self.ubl)
        if self.srt(self.ufl) == sorted([self.u, self.f, self.l]):
            match.append(self.ufl)
        if len(match) == 4:
            return True
        else:
            return False

    def positionYellowCorners(self):
        if self.u == "W":
            self.convertmoves("Z2")
        self.update_cubies()

        corner_alg = ["U", "R", "Ui", "Li", "U", "Ri", "Ui", "L"]
        while not self.checkdone():
            # finds matched corner and performs algorithm on there
            match = []
            if self.srt(self.ufr) == sorted([self.u, self.f, self.r]):
                match.append(self.ufr)
                for move in corner_alg:
                    self.convertmoves(move)
            elif self.srt(self.ubr) == sorted([self.u, self.b, self.r]):
                match.append(self.ubr)
                self.convertmoves("Y")
                for move in corner_alg:
                    self.convertmoves(move)
            elif self.srt(self.ubl) == sorted([self.u, self.b, self.l]):
                match.append(self.ubl)
                self.convertmoves("Y")
                self.convertmoves("Y")
                for move in corner_alg:
                    self.convertmoves(move)
            elif self.srt(self.ufl) == sorted([self.u, self.f, self.l]):
                match.append(self.ufl)
                self.convertmoves("Yi")
                for move in corner_alg:
                    self.convertmoves(move)
            elif len(match) == 0:
                for move in corner_alg:
                    self.convertmoves(move)

    def orientYellowCorners(self):
        if self.u == "W":
            self.convertmoves("Z2")
        self.update_cubies()

        orient_alg = ['Ri', 'Di', 'R', 'D']

        while self.ufr['u'] + self.ubr['u'] + self.ufl['u'] + self.ubl['u'] != "YYYY":
            # if corner isn't oriented
            if self.ufr['u'] != "Y":
                for move in orient_alg:
                    self.convertmoves(move)

            if self.ufr['u'] == "Y":
                self.convertmoves("U")

        while self.uf['f'] != self.f:
            self.convertmoves("U")

    # rotates cube so thar green is the front and white is at the top
    def orientToNeutralPosition(self):
        if self.u == "Y":
            self.convertmoves("Z2")
        while self.f != "G":
            self.convertmoves("Y")

    def solveCube(self):

        self.printCube()
        self.solveWhiteCross()

        self.solveWhiteCorners()

        self.solveSecondLayer()

        self.solveYellowCross()

        self.matchYellowEdges()

        self.positionYellowCorners()

        self.orientYellowCorners()

        self.orientToNeutralPosition()

        self.printCube()


class CubeCV(handler):

    def __init__(self):
        handler.__init__(self)

        self.width = None
        self.height = None

        self.faces = {"red": 2, "blue": 5, "orange": 3, "green": 1, "white": 0, "yellow": 4}
        self.colorvalues = {"red": None, "blue": None, "orange": None, "green": None, "white": None, "yellow": None}

    # Reads  counter file and returns the next number to use for image names
    def img_counter_file(self):
        counter_file = open("image_counter_file.txt", "r+")
        count = int(counter_file.read())

        count += 1
        counter_file.truncate(0)
        counter_file.close()

        counter_file = open("image_counter_file.txt", "w")
        counter_file.write(str(count))
        counter_file.close()

        return count

    # Resizes webcam box size
    def rescale_frame(frame, percent=75):
        width = int(frame.shape[1] * percent / 100)
        height = int(frame.shape[0] * percent / 100)
        dim = (width, height)
        return cv.resize(frame, dim, interpolation=cv.INTER_AREA)

    # Opens webcam and asks users to take picture of cube
    def webcam(self):
        global saved
        cam = cv.VideoCapture(0)
        cv.namedWindow("Cube catcher")
        counter = 0
        order = ["red", "blue", "orange", "green", "white", "yellow"]
        facephotos = []
        lines = ["Hold the cube with the WHITE side facing UP: Position the RED side in the square (space to capture)",
                 "Hold the cube with the WHITE side facing UP: Position the BLUE side in the square",
                 "Hold the cube with the WHITE side facing UP: Position the ORANGE side in the square",
                 "Hold the cube with the WHITE side facing UP: Position the GREEN side in the square",
                 "Hold the cube with the GREEN side facing DOWN: Position the WHITE side in the square",
                 "Hold the cube with the GREEN side facing UP: Position the YELLOW side in the square"]
        img_counter = self.img_counter_file()
        on = True

        try:
            # main loop
            while on:
                ret, img = cam.read()
                # gets dimensions of window
                self.width = int(cam.get(3))
                self.height = int(cam.get(4))

                if not ret:
                    print("capture failed")
                    break
                # draws rectangle on cam
                img = cv.flip(img, 1)
                img = cv.rectangle(img, (180, 100), (460, 380), (0, 200, 0), 5)  # top left, bottom right, thickness
                # start, end, rgb, thickness
                img = cv.line(img, (273, 100), (273, 380), (200, 200, 200), 3)
                img = cv.line(img, (367, 100), (367, 380), (200, 200, 200), 3)
                img = cv.line(img, (180, 193), (460, 193), (200, 200, 200), 3)
                img = cv.line(img, (180, 287), (460, 287), (200, 200, 200), 3)

                img = cv.putText(img, lines[counter], (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.4, (00, 0, 0),
                                 1)  # displays text with instructions
                img = CubeCV.rescale_frame(img, percent=150)  # makes the frame look bigger (:

                cv.imshow("Cube catcher", img)
                # wait key waits until a key is pressed
                k = cv.waitKey(1)
                # closes app
                if cv.getWindowProperty("Cube catcher", cv.WND_PROP_VISIBLE) < 1:
                    on = False
                if k % 256 == 27:  # esc key
                    print("Escape hit, closing the app")
                    on = False
                # takes picture
                elif k % 256 == 32:  # space key
                    #
                    img_name = f"opencv_{order[counter]}{img_counter}.png"
                    facephotos.append(img_name)
                    cv.imwrite(img_name, img)
                    print("side captured")
                    counter += 1
                    if counter == 6:  # if we are on the last image do this
                        # print(facephotos) / remove comment to print files for test material
                        for file, color in zip(facephotos, order):  # puts each photo into the cube array
                            self.face_filler(self.faces[color], color, file)

                        self.rgb_to_color_cube()
                        self.display_cube()
                        # saved = self.cube_to_rotations()
                        on = False

            cam.release()
            cv.DestroyAllWindows()
        except AttributeError:
            pass

    # Turns a cube 3d list of rgb values into a cube of colors
    def rgb_to_color_cube(self):
        for i, face in enumerate(self.cube):
            for j, row in enumerate(face):
                diffdict = {}
                for k, facelet in enumerate(row):
                    for name, rgb in self.colorvalues.items():
                        difference = sqrt(
                            (facelet[0] - rgb[0]) ** 2 + (facelet[1] - rgb[1]) ** 2 + (facelet[2] - rgb[2]) ** 2)
                        diffdict[round(difference, 2)] = name
                    color = diffdict[min(diffdict)]
                    color = self.hue_comparison(color, facelet)
                    self.cube[i][j][k] = color[0].upper()

    # this function takes what i thought to be the color of an rgb value then finds the color with the closest hue and becomes that

    def hue_comparison(self, color_arg, rgb):
        # print(self.colorvalues,"#]##########")
        # print("color and rgb", color_arg,rgb)
        # groups of colors which are similar
        near_groups = [("white", "yellow"), ("green", "blue"), ("red", "orange", "yellow")]
        hue_diffdict = {}
        # loops through all of the groups of similar colors
        for group in (near_groups):
            # if the color is in a similar group
            if color_arg in group:
                # find the hues of the colors in the group and compare which its closest to
                for color_name in group:
                    color_rgb = self.colorvalues[color_name]
                    color_hue = self.rgb_to_hsv(color_rgb)[0]
                    hue_diffdict[abs(color_hue - self.rgb_to_hsv(rgb)[0])] = color_name
        # returns the name of the color with the minimum hue difference

        return hue_diffdict[min(hue_diffdict)]


    # Returns color of the pixel in the coordinate position
    def rgb_to_hsv(self, rgb):  # this function converts rgb values into hsv values
        r, g, b = rgb
        r, g, b = r / 255.0, g / 255.0, b / 255.0  # converts rgb into a value in range 0-1
        mx = max(r, g, b)  # find maximum and minimmum values
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = (df / mx) * 100
        v = mx * 100
        hsv = (h, s, v)
        return hsv

    def pixel_identifier(self, coordinate, filename="opencv_frame0.png"):
        image = Image.open(filename)
        rgbpixel = image.getpixel(coordinate)
        del image
        return rgbpixel

    # Returns average rgb value of a facelet
    def getfaceletcolor(self, coordinate,
                        filename):  # input the center coord of a facelet and it will return its color in hvs
        x, y = coordinate
        x *= 1.5
        y *= 1.5
        k = 5  # k is shift constant
        rgbvals = (self.pixel_identifier(coordinate, filename), self.pixel_identifier((x + k, y), filename),
                   self.pixel_identifier((x - k, y), filename), self.pixel_identifier((x, y + k), filename),
                   self.pixel_identifier((x, y - k), filename))

        avgcol = tuple(np.mean(rgbvals, axis=0))
        return avgcol

    # Inputs rgb values of facelet into the 3D list
    def face_filler(self, face, color, file):
        # this function will take center values of each facelet and run the pixel identifier function on it then get the name of the collor
        x = face

        self.cube[x][0][0] = self.getfaceletcolor((413, 147), filename=file)
        self.cube[x][0][1] = self.getfaceletcolor((320, 147), filename=file)
        self.cube[x][0][2] = self.getfaceletcolor((227, 147), filename=file)

        self.cube[x][1][0] = self.getfaceletcolor((413, 240), filename=file)

        self.cube[x][1][1] = self.colorvalues[color] = self.getfaceletcolor((320, 240), filename=file)  # center

        self.cube[x][1][2] = self.getfaceletcolor((227, 240), filename=file)

        self.cube[x][2][0] = self.getfaceletcolor((413, 333), filename=file)
        self.cube[x][2][1] = self.getfaceletcolor((320, 333), filename=file)
        self.cube[x][2][2] = self.getfaceletcolor((227, 333), filename=file)

    # for debugging
    def test(self):
        order = ["red", "blue", "orange", "green", "white", "yellow"]
        test_sequence = ['opencv_red93.png', 'opencv_blue93.png', 'opencv_orange93.png', 'opencv_green93.png',
                         'opencv_white93.png', 'opencv_yellow93.png']
        for file, color in zip(test_sequence, order):  # puts each photo into the cube array
            self.face_filler(self.faces[color], color, file)

        print(self.colorvalues)
        # print(self.cube)
        self.display_cube()
        self.rgb_to_color_cube()
        self.display_cube()
        print(self.check_legitimacy())

    # checks if inputted cube is possible
    def check_legitimacy(self):
        facelets = []
        for face in self.cube:
            for row in face:
                for facelet in row:
                    facelets.append(facelet)

        for _ in ["W", "Y", "O", "G", "B", "R"]:
            amount = facelets.count(color)
            if amount != 9:
                print("Color error: please edit the cube")
                self.edit_cube()
                return True
            else:
                yn = input2("Is the cube displayed correct? (y/n)")
                if yn.lower() == "y":
                    return True
                else:
                    self.edit_cube()

    def edit_cube(self):
        print("enter edit code ( 510r means, counting from zero; change face 5, row 1, facelet 0 to red")
        while 1:

            edit_code = input2("enter edit code (xxx when complete) :")
            # if the user enters xxx, exit the function
            if "xxx" in edit_code.lower():
                break
            face, row, facelet, color = list(edit_code[:4])
            try:
                self.cube[int(face)][int(row)][int(facelet)] = color.upper()
                self.display_cube()
            except:
                print("invalid code")


# because ursina comes with a built in function called input, the normal python input will not work
# ths function just replaces the normal input() function
def input2(prompt=""):
    print(prompt, end="")
    return sys.stdin.readline()


class Menu(handler):

    def __init__(self):
        pass

    def mainMenu(self):
        global inst3D, saved, instDB
        print("Menu")
        print("___________________________________")
        print("1: 3D Cube ")
        print("2: Input real cube ")
        print("3: Log in")
        print("4: Sign up")
        print("5: Score Board")
        print("6: Exit program")

        answer = sys.stdin.readline()[:1]

        if answer == "1":
            inst3D = Cube3D()
            instDB = CubeDB()
            inst3D.initCube()

            app.run()
            self.menucv()

        if answer == "2":
            instCV = CubeCV()
            instCV.webcam()
            if instCV.check_legitimacy():
                # saved =
                inst3D = Cube3D(cube=instCV.cube)
                inst3D.build_cube(instCV.cube_to_rotations())
                inst3D.initCube()
                app.run()
            else:
                print("Capture failed, try in different lighting")

        elif answer == "3":
            instDB.log_in()
        elif answer == "4":
            instDB.sign_up()
        elif answer == "5":
            CubeDB.display_scores()
        elif answer == "6":
            sys.exit()
        else:
            print("Invalid input")
            self.mainMenu()


# Run program
##################################
run_menu = True
if __name__ == "__main__":
    while 1:
        Menu().mainMenu()


