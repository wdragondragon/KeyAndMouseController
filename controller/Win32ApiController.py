from ctypes import windll
from controller.KeyMouseController import KeyMouseController

MOUSE_EVEN_TF_LEFT_DOWN = 0x2
MOUSE_EVEN_TF_LEFT_UP = 0x4
MOUSE_EVEN_TF_MIDDLE_DOWN = 0x20
MOUSE_EVEN_TF_MIDDLE_UP = 0x40
MOUSE_EVEN_TF_RIGHT_DOWN = 0x8
MOUSE_EVEN_TF_RIGHT_UP = 0x10
MOUSE_EVEN_TF_MOVE = 0x1


class Win32ApiControllerKey(KeyMouseController):

    def __init__(self, mouse_mover_param):
        super().__init__(mouse_mover_param)
        self.user32 = windll.user32

    def move_rp(self, x: int, y: int):
        self.user32.mouse_event(MOUSE_EVEN_TF_MOVE, x, y)

    def move(self, x, y):
        self.move_rp(x, y)

    def left_click(self):
        self.user32.mouse_event(MOUSE_EVEN_TF_LEFT_DOWN, 0, 0, 0, 0)
        self.user32.mouse_event(MOUSE_EVEN_TF_LEFT_UP, 0, 0, 0, 0)

    def left_down(self):
        self.user32.mouse_event(MOUSE_EVEN_TF_LEFT_DOWN, 0, 0, 0, 0)

    def left_up(self):
        self.user32.mouse_event(MOUSE_EVEN_TF_LEFT_UP, 0, 0, 0, 0)

    def right_down(self):
        self.user32.mouse_event(MOUSE_EVEN_TF_RIGHT_DOWN, 0, 0, 0, 0)

    def right_up(self):
        self.user32.mouse_event(MOUSE_EVEN_TF_RIGHT_UP, 0, 0, 0, 0)
