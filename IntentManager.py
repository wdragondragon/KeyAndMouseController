import random
import threading
import time

from controller.KeyMouseController import KeyMouseController

intention = None


class IntentManager:
    """
        意图管理器，负责推送移动意图
    """

    def __init__(self, key_mouse_controller: KeyMouseController, move_step=(1, 1), move_frequency=1000,
                 move_step_max=None, move_optimization=True):
        self.intention = None
        self.change_coordinates_num = 0
        self.key_mouse_controller = key_mouse_controller
        self.intention_lock = threading.Lock()
        self.sleep_time = 1 / move_frequency
        self.move_step = move_step
        self.move_step_max = move_step_max
        self.move_optimization = move_optimization
        if move_step_max is None:
            self.move_step_max = self.move_step
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
        """`
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
        while self.run_sign:
            if self.intention is not None:
                (x, y) = self.intention
                while x != 0 or y != 0:
                    self.intention_lock.acquire()
                    try:
                        (x, y) = self.intention
                        move_step, move_step_y = self.random_move(x, y)
                        move_up = min(move_step, abs(x)) * (1 if x > 0 else -1)
                        move_down = min(move_step_y, abs(y)) * (1 if y > 0 else -1)
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

    def random_move(self, x, y):
        """
            随机移动方法
        :param x:
        :param y:
        :return:
        """
        move_step_temp, move_step_y_temp = self.move_step
        move_step_temp_max, move_step_y_temp_max = self.move_step_max

        move_step, move_step_y = (random.randint(move_step_temp, move_step_temp_max),
                                  random.randint(move_step_y_temp, move_step_y_temp_max))
        if self.move_optimization and x > 0 and y > 0:
            x_moving_ratio = x / y
            if x_moving_ratio <= 0.5:
                random_number = random.random()
                if x_moving_ratio < random_number:
                    move_step = 1
                else:
                    move_step = 0
            elif x_moving_ratio >= 2:
                y_moving_ratio = y / x
                random_number = random.random()
                if y_moving_ratio > random_number:
                    move_step_y = 1
                else:
                    move_step_y = 0
        return move_step, move_step_y

    def testMouseRate(self):
        """
            测试鼠标性能
        :return:
        """
        i = 0
        x = 1
        start = time.time()
        while int((time.time() - start) * 1000) < 1000:
            self.key_mouse_controller.move_rp(x, x)
            i += 1
            x = -x
        print(f"鼠标性能为{i}/s")
