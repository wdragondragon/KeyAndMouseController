from log.LogWindow import LogWindow
from log.Logger import Logger

current_logger = None


def init_logger(mode):
    """
        初始化日志窗口
    :param mode:
    """
    global current_logger
    if mode == 'console':
        current_logger = Logger()
    elif mode == 'windows':
        current_logger = LogWindow()


def logger():
    """
        获取日志窗口
    :return:
    """
    return current_logger
