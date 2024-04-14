import threading
import time

from controller.KeyMouseController import KeyMouseController

intention = None


class IntentManager:
    """
        意图管理器，负责推送移动意图
    """

    def __init__(self, key_mouse_controller: KeyMouseController, move_step=(1, 1), move_frequency=1000):
        self.intention = None
        self.change_coordinates_num = 0
        self.key_mouse_controller = key_mouse_controller
        self.intention_lock = threading.Lock()
        self.sleep_time = 1 / move_frequency
        self.move_step = move_step
        self.run_sign = True

    def set_intention(self, x, y):
        """
            设置移动意图
        :param x:
        :param y:
        """
        self.intention_lock.acquire()
        try:
            self.intention = (x, y)
            self.change_coordinates_num += 1
        finally:
            # 释放锁
            self.intention_lock.release()

    def start(self):
        """
            开始读取移动意图并移动
        """
        self.run_sign = True
        intent_manager_thread = threading.Thread(target=self.run)
        intent_manager_thread.start()

    def run(self):
        """
            开始读取移动意图并移动
        """
        sleep_time = 0.01
        move_step_temp, move_step_y_temp = self.move_step
        while self.run_sign:
            if self.intention is not None:
                (x, y) = self.intention
                while x != 0 or y != 0:
                    self.intention_lock.acquire()
                    try:
                        (x, y) = self.intention
                        move_up = min(move_step_temp, abs(x)) * (1 if x > 0 else -1)
                        move_down = min(move_step_y_temp, abs(y)) * (1 if y > 0 else -1)
                        if x == 0:
                            move_up = 0
                        elif y == 0:
                            move_down = 0
                        x -= move_up
                        y -= move_down
                        self.intention = (x, y)
                    finally:
                        self.intention_lock.release()
                    self.key_mouse_controller.move_rp(int(move_up), int(move_down))
                self.intention = None
                sleep_time = self.sleep_time
            time.sleep(sleep_time)
            self.change_coordinates_num = 0

    def stop(self):
        """
            停止移动意图
        """
        while self.intention is not None:
            time.sleep(0.1)
        self.run_sign = False
