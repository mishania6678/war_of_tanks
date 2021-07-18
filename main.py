import tkinter as tk
import tkinter.font

from PIL import Image, ImageTk
from threading import Thread
from time import sleep
from random import choice
from copy import deepcopy
from math import sqrt

from typing import List, Tuple


class Sample(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.frame = None
        self.activate_frame(PregameProcess)

    def activate_frame(self, frame_class):
        """Creates a new frame and destroys an old one"""
        new_frame = frame_class(self)
        if self.frame is not None:
            self.frame.destroy()
        self.frame = new_frame
        self.frame.pack()


class PregameProcess(tk.Frame, object):
    def __init__(self, master: tkinter.Frame):
        tk.Frame.__init__(self, master)

        self.field = None
        self.draw_field()

        self.player_occupied_cords = [([], []) for _ in range(10)]
        self.android_occupied_cords = [([], []) for _ in range(10)]

        self.player_tank_img = Image.open('D:/Миша программирование/Python/Curses/gb_curse/main_curse/extra_tasks/'
                                          'war_of_tanks/other_files/player_tank.png')
        self.player_tank_img = self.player_tank_img.resize((35, 35))
        self.player_tank_img = ImageTk.PhotoImage(self.player_tank_img)

        self.android_tank_img = Image.open('D:/Миша программирование/Python/Curses/gb_curse/main_curse/extra_tasks/'
                                           'war_of_tanks/other_files/android_tank.png')
        self.android_tank_img = self.android_tank_img.resize((35, 35))
        self.android_tank_img = ImageTk.PhotoImage(self.android_tank_img)

        self.menu = None
        self.place_tanks = False
        self.placed_player_tanks = 0
        self.create_tanks_menu()

        self.master.bind('<Button-1>', self.__left_mouse_button_clicked)

    def draw_field(self):
        """Draws a game field"""

        def draw_part_of_field(x: int, y: int, outline: str):
            for i in range(600):
                square_size = 18
                self.field.create_rectangle(x, y, x + square_size, y + square_size, outline=outline)
                x += square_size
                if x > 667:
                    x = 0
                    y += square_size

        self.field = tk.Canvas(self, width=540, height=697, bg='white')
        self.field.pack()

        draw_part_of_field(0, 35, '#65B2E1')
        draw_part_of_field(0, 375, '#65B2E1')

        line_size, crd_x = 15, 2
        for _ in range(30):
            self.field.create_line(crd_x, 350, crd_x + line_size, 350, fill='#65B2E1')
            crd_x += line_size + 6

        font = tk.font.Font(family='Gabriola', size=20, weight='bold')
        self.field.create_text(250, 18, text='Player field', font=font, fill='#4FB0E1')
        self.field.create_text(250, 680, text='Computer field', font=font, fill='#4FB0E1')

    def create_tanks_menu(self):
        """Creates a menu in the upper left corner, where player need to click on the "start placing tanks" command
        to be able to place the tanks on his field or stop this process"""

        def place_tanks():
            self.place_tanks = True

        def delete_tanks():
            self.place_tanks = False

        self.menu = tk.Menu(self)
        self.master.config(menu=self.menu)

        commands_list = tk.Menu(self.menu, tearoff=0)
        commands_list.add_command(label='Place tanks', command=place_tanks)
        commands_list.add_command(label='Delete tanks', command=delete_tanks)
        self.menu.add_cascade(label=f'Menu', menu=commands_list)

    def place_player_tanks(self, x: int, y: int):
        """Let player place 10 tanks on his field if "start placing tanks" command was clicked"""

        def inform_about_error():
            font = tk.font.Font(family='Gabriola', size=12, weight='bold')
            err_text1 = self.field.create_text(100, 8, text='You want to place a tank', font=font, fill='#4FB0E1')
            err_text2 = self.field.create_text(100, 23, text='too close to another', font=font, fill='#4FB0E1')
            sleep(2)
            self.field.delete(err_text1, err_text2)

        if self.place_tanks:
            if 19 <= x <= 521 and 51 <= y <= 305:
                if self.check_cords(self.player_occupied_cords, x, y):
                    self.placed_player_tanks += 1
                    if self.placed_player_tanks >= 10:
                        self.master.unbind('<Button-1>')
                        self.menu.destroy()
                        self.place_android_tanks()
                    self.add_occupied_cords(self.player_occupied_cords, x, y)
                    self.field.create_image(x, y, image=self.player_tank_img)
                else:
                    Thread(target=inform_about_error).start()

    def place_android_tanks(self):
        """Randomly place android tanks on its field"""

        def create_cords() -> Tuple[int, int]:
            xcord, ycord = choice(android_xcords), choice(android_ycords)
            if not self.check_cords(self.android_occupied_cords, xcord, ycord): return create_cords()
            return xcord, ycord

        android_xcords, android_ycords = [i for i in range(19, 522)], [i for i in range(392, 646)]
        for i in range(10):
            x, y = create_cords()
            self.field.create_image(x, y, image=self.android_tank_img)
            self.add_occupied_cords(self.android_occupied_cords, x, y, placed_tanks=i + 1)

        GameProcess(self)

    def check_cords(self, occupied_cords: List[Tuple[List[int]]], x: int, y: int) -> bool:
        """Check if x, y are in occupied_cords variable"""
        cords_copy = self.add_occupied_cords(occupied_cords, x, y, copy=True)
        for cord in cords_copy:
            if x in cord[0] and y in cord[1]:
                return 0
        return 1

    def add_occupied_cords(self, occupied_cords: List[Tuple[List[int]]], x: int, y: int,
                           placed_tanks=None, copy=False) -> [None, bool]:
        """If copy=False, adds tanks_coordinates to an occupied coordinates,
        else returns a copy of occupied_cords variable"""
        if not copy:
            if placed_tanks is None: placed_tanks = self.placed_player_tanks
            occupied_cords[placed_tanks - 1][0].extend(i for i in range(x - 40, x + 41))
            occupied_cords[placed_tanks - 1][1].extend(i for i in range(y - 40, y + 41))
        else:
            cords_copy = deepcopy(occupied_cords)
            return cords_copy

    def __left_mouse_button_clicked(self, event: tkinter.Event):
        """This method is bound to mouse left button clicked event and calls a "place_player_tanks" method"""
        self.place_player_tanks(event.x, event.y)


class GameProcess(object):
    def __init__(self, obj: PregameProcess):
        self.object = obj

        self.destroyed_player_tanks, self.destroyed_android_tanks = 0, 0
        self.player_occupied_cannonball_cords = []

        self.object.master.bind('<Button-1>', self.__left_mouse_button_clicked)

    def player_turn(self, x: int, y: int):
        """Realises player turn"""
        if 9 <= x <= 531 and 31 <= y <= 315:
            oval_size = 10
            x1, y1, x2, y2 = 540 - x, 697 - y, 540 - x + oval_size, 697 - y + oval_size
            self.object.field.create_oval(x1, y1, x2, y2, fill='blue')
            if self.detect_hit(self.object.android_occupied_cords, (x2 + x1) / 2, (y2 + y1) / 2, oval_size // 2):
                self.object.field.create_oval(x1, y1, x2, y2, fill='red')
                self.destroyed_android_tanks += 1
                if self.destroyed_android_tanks == 10:
                    self.announce_winner('player')
            else:
                self.object.master.unbind('<Button-1>')
                self.android_turn()

    def android_turn(self):
        """Randomly generates coordinate of cannonball and shoot there"""

        def create_cords() -> Tuple[int, int]:
            xcord, ycord = choice(android_xcords), choice(android_ycords)
            if not self.check_cannonball_cords(self.player_occupied_cannonball_cords, xcord, ycord, oval_size):
                return create_cords()
            return xcord, ycord

        android_xcords, android_ycords = [i for i in range(19, 522)], [i for i in range(392, 646)]
        oval_size = 10
        x, y = create_cords()
        x1, y1, x2, y2 = 540 - x, 697 - y, 540 - x + oval_size, 697 - y + oval_size
        self.object.field.create_oval(x1, y1, x2, y2, fill='blue')
        self.player_occupied_cannonball_cords.append((x + oval_size // 2, y + oval_size // 2, oval_size // 2))
        if self.detect_hit(self.object.player_occupied_cords, (x2 + x1) / 2, (y2 + y1) / 2, oval_size // 2):
            self.object.field.create_oval(x1, y1, x2, y2, fill='red')
            self.object.master.bind('<Button-1>', self.__left_mouse_button_clicked)
            self.destroyed_player_tanks += 1
            if self.destroyed_player_tanks == 10:
                self.announce_winner('android')
        else:
            self.object.master.bind('<Button-1>', self.__left_mouse_button_clicked)

    @staticmethod
    def detect_hit(occupied_cords: List[Tuple[List[int]]], xcenter, ycenter, r) -> bool:
        """Detects if cannonball shot tank"""

        def check_intersection(point):
            return (point[0] - xcenter) ** 2 + (point[1] - ycenter) ** 2 == r ** 2

        for tank_cords in occupied_cords:
            for xcord in tank_cords[0][25: 55]:
                for ycord in tank_cords[1][25: 55]:
                    if check_intersection((xcord, ycord)) or check_intersection((xcord, ycord)):
                        occupied_cords.remove(tank_cords)
                        return 1
        return 0

    @staticmethod
    def check_cannonball_cords(occupied_cords: List[Tuple[int]], x: int, y: int, r: int) -> bool:
        """Check if current cannonball is not intersected with other on field"""

        def check_intersection():
            return sqrt(abs(x - cord[0]) ** 2 + abs(y - cord[1]) ** 2) > r + cord[2]

        for cord in occupied_cords:
            if not check_intersection():
                return 0
        return 1

    def announce_winner(self, winner):
        """Announces the winner"""
        font = tk.font.Font(family='Gabriola', size=60, weight='bold')
        self.object.field.create_text(250, 340, text=f'{winner.title()} won!', font=font, fill='#4FB0E1')

    def __left_mouse_button_clicked(self, event: tkinter.Event):
        """This method is bound to mouse left button clicked event and calls a "player_move" method"""
        self.player_turn(event.x, event.y)


if __name__ == '__main__':
    root = Sample()
    root.geometry('540x697')
    root.title('War of tanks')
    root.mainloop()
