from ctypes import *

import win32com.client

from log import LogFactory
from controller.KeyMouseController import KeyMouseController


class WuYaControllerKey(KeyMouseController):
    def __init__(self, mouse_mover_param):
        # 进程内注册插件,模块所在的路径按照实际位置修改
        super().__init__(mouse_mover_param)
        vid_pid = mouse_mover_param["VID/PID"]
        hkm_dll = windll.LoadLibrary("./wy_hkm.dll")
        hkm_dll.DllInstall.argtypes = (c_long, c_longlong)
        if hkm_dll.DllInstall(1, 2) < 0:
            LogFactory.logger().print_log("注册失败!")
        vid = int(vid_pid[:4], 16)
        pid = int(vid_pid[4:], 16)
        try:
            self.wy_hkm = win32com.client.Dispatch("wyp.hkm")
        except Exception as e:
            LogFactory.logger().print_log("创建对象失败!")
            print(e)
        version = self.wy_hkm.GetVersion()
        LogFactory.logger().print_log("无涯键鼠盒子模块版本：" + hex(version))
        dev_id = self.wy_hkm.SearchDevice(vid, pid, 0)
        if dev_id == -1:
            LogFactory.logger().print_log("未找到无涯键鼠盒子")
        if not self.wy_hkm.Open(dev_id, 0):
            LogFactory.logger().print_log("打开无涯键鼠盒子失败")

    def move_rp(self, short_x: int, short_y: int):
        self.wy_hkm.MoveRP(short_x, short_y)

    def move(self, short_x: int, short_y: int):
        self.wy_hkm.MoveR(short_x, short_y)

    def left_click(self):
        self.wy_hkm.LeftClick()
